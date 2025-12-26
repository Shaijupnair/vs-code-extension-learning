import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
// Use require to handle the specific export structure of web-tree-sitter v0.26+
// This avoids mismatch between TS types and actual Runtime CJS exports.
const WebTreeSitter = require('web-tree-sitter');

import { create, insert, remove, Orama } from '@orama/orama';
import { pluginEmbeddings } from '@orama/plugin-embeddings';
import { persist, restore } from '@orama/plugin-data-persistence';
import { env } from '@xenova/transformers';

// Force onnxruntime-web (WASM) backend for VS Code extension environment
// We removed onnxruntime-node to prevent binary mismatch errors.
// This forces Xenova/Transformers to use the pure JS/WASM backend.
env.allowLocalModels = false;
env.useBrowserCache = false; // Optional: helps with reload consistency in dev

// Force TensorFlow.js CPU backend (Orama internal dependency)
// This resolves "No backend found" if Orama attempts to use TFJS internally.
import * as tf from '@tensorflow/tfjs-core';
import '@tensorflow/tfjs-backend-cpu';



export class PersistentIndexer {
    private db: any | null = null;
    private parser: any | null = null; // Typing 'any' to avoid TS conflict with require
    private language: any | null = null;
    private storagePath: string;
    private dbFilePath: string;
    private extensionPath: string;

    constructor(context: vscode.ExtensionContext) {
        if (!context.globalStorageUri) {
            throw new Error("Global storage not available");
        }
        this.storagePath = context.globalStorageUri.fsPath;
        this.extensionPath = context.extensionPath;

        // Ensure storage folder exists
        if (!fs.existsSync(this.storagePath)) {
            fs.mkdirSync(this.storagePath, { recursive: true });
        }

        const workspaceName = vscode.workspace.name || 'default';
        this.dbFilePath = path.join(this.storagePath, `index-${workspaceName}-all-MiniLM-L6-v2.json`);
    }

    /**
     * Initialize the AI Service: Load WASM and DB
     */
    async init() {
        // [Concept: Backend Initialization]
        // TensorFlow.js usually tries WebGL/WebGPU first. In VS Code extension host (Node.js/Electron),
        // we lack those graphics contexts. We explicit set 'cpu' to avoid "No backend found" errors.
        // This is crucial for stability, even if slower than GPU.
        await tf.setBackend('cpu');
        await tf.ready();

        // 1. Initialize WebTreeSitter
        // [Concept: WASM (WebAssembly)]
        // Tree-sitter runs as a WASM binary. We must initialize the runtime (Parser) 
        // and tell it where to find the .wasm file.
        // Based on verification: default export is a Module containing Parser, Language, etc.
        const Parser = WebTreeSitter.Parser || WebTreeSitter;
        const Language = WebTreeSitter.Language || WebTreeSitter.Language; // Fallback
        const Query = WebTreeSitter.Query || WebTreeSitter.Query;


        // Initialize the core library
        // Note: Some versions need locateFile, some don't if wasm is local.
        // We point it to the valid one we found just in case.
        const mainWasm = path.join(this.extensionPath, 'node_modules', 'web-tree-sitter', 'web-tree-sitter.wasm');
        await Parser.init({
            locateFile: () => mainWasm
        });

        // 2. Load Java Grammar
        const javaWasmPath = path.join(this.extensionPath, 'resources', 'wasm', 'tree-sitter-java.wasm');
        if (!fs.existsSync(javaWasmPath)) {
            throw new Error(`WASM grammar not found at: ${javaWasmPath}`);
        }

        const lang = await Language.load(javaWasmPath);
        this.language = lang;
        this.parser = new Parser();
        this.parser.setLanguage(lang);

        console.log('✅ AI Service: Parser Initialized');

        // 3. Load or Create Vector DB
        if (fs.existsSync(this.dbFilePath)) {
            try {
                console.log(this.dbFilePath);
                const dbData = fs.readFileSync(this.dbFilePath, 'utf-8');
                this.db = await restore('json', JSON.parse(dbData));
                console.log('✅ AI Service: Loaded existing index.');
            } catch (e) {
                console.error('❌ AI Service: Failed to restore DB, creating new.', e);
                await this.createNewDb();
            }
        } else {
            await this.createNewDb();
        }
    }

    private async createNewDb() {
        // [Concept: Vector Database Schema]
        // Orama is an edge-search compatible vector DB.
        // We define a schema for the data we want to index (code, signatures, etc.).
        // 'embedding' field of type 'vector[384]' matches the output dimension of the detailed model below.
        this.db = await create({
            schema: {
                id: 'string',
                signature: 'string',
                packageName: 'string',
                code: 'string',
                doc: 'string',
                path: 'string',
                // We use a predefined model for embeddings (runs locally)
                embedding: 'vector[384]',
            },
            plugins: [
                (await pluginEmbeddings({
                    embeddings: {
                        model: 'Xenova/all-MiniLM-L6-v2',
                        verbose: false,
                        properties: ['doc', 'code']
                    } as any,
                })) as any,
            ],
        });
        console.log('✅ AI Service: Created new DB');
    }

    /**
     * Index all Java files in the current workspace.
     * Non-blocking (async) using VS Code API.
     */
    /**
     * Index all Java files in the current workspace.
     * Non-blocking (async) using VS Code API.
     */
    async indexWorkspace(progress: vscode.Progress<{ message?: string; increment?: number }>, token: vscode.CancellationToken) {
        if (!this.db || !this.parser) {
            console.error('AI Service not initialized!');
            return;
        }

        // Use findFiles for fast, non-blocking search respecting gitignore
        const uris = await vscode.workspace.findFiles('**/*.java', '**/node_modules/**');
        const javaFiles = uris.map(u => u.fsPath);

        await this.processFiles(javaFiles, progress, token);
    }

    async indexFolder(folderPath: string, progress: vscode.Progress<{ message?: string; increment?: number }>, token: vscode.CancellationToken) {
        if (!this.db || !this.parser) {
            console.error('AI Service not initialized!');
            return;
        }

        const javaFiles = this.findAllJavaFiles(folderPath);
        await this.processFiles(javaFiles, progress, token);
    }

    private findAllJavaFiles(dir: string): string[] {
        let results: string[] = [];
        try {
            const list = fs.readdirSync(dir);
            for (const file of list) {
                const filePath = path.join(dir, file);
                const stat = fs.statSync(filePath);
                if (stat && stat.isDirectory()) {
                    if (file !== 'node_modules' && !file.startsWith('.')) {
                        results = results.concat(this.findAllJavaFiles(filePath));
                    }
                } else {
                    if (filePath.endsWith('.java')) {
                        results.push(filePath);
                    }
                }
            }
        } catch (e) {
            console.warn(`Error scanning directory ${dir}:`, e);
        }
        return results;
    }

    private async processFiles(filePaths: string[], progress: vscode.Progress<{ message?: string; increment?: number }>, token: vscode.CancellationToken) {
        const totalFiles = filePaths.length;
        console.log(`Found ${totalFiles} Java files to index.`);
        let processedCount = 0;

        for (const filePath of filePaths) {
            if (token.isCancellationRequested) break;

            const fileName = path.basename(filePath);

            progress.report({
                message: `Indexing ${fileName}...`,
                increment: (1 / totalFiles) * 100
            });

            try {
                await this.parseAndInsert(filePath);
            } catch (e) {
                console.warn(`Failed to parse ${fileName}:`, e);
            }

            processedCount++;
        }

        // Save after indexing
        if (processedCount > 0) {
            progress.report({ message: "Saving index to disk..." });
            const data = await persist(this.db!, 'json');
            fs.writeFileSync(this.dbFilePath, JSON.stringify(data));
            console.log(`✅ Indexing complete. Saved ${processedCount} files.`);
        }
    }

    private async parseAndInsert(filePath: string) {
        const content = fs.readFileSync(filePath, 'utf8');
        const tree = this.parser.parse(content);
        const Query = WebTreeSitter.Query || WebTreeSitter;

        // 1. Extract Package Name
        const packageQuery = new Query(this.language, `
            (package_declaration
                (scoped_identifier) @pkg
            )
        `);
        // Fallback for simple package names "package com;"
        const packageQuerySimple = new Query(this.language, `
            (package_declaration
                (identifier) @pkg
            )
        `);

        let packageName = "";
        let pkgMatches = packageQuery.matches(tree.rootNode);
        if (pkgMatches.length === 0) {
            pkgMatches = packageQuerySimple.matches(tree.rootNode);
        }

        if (pkgMatches.length > 0) {
            packageName = pkgMatches[0].captures[0].node.text;
        }

        // 2. Query for Methods
        const query = new Query(this.language, `
            (method_declaration
                name: (identifier) @name
            ) @method
        `);

        const matches = query.matches(tree.rootNode);

        for (const match of matches) {
            // [Concept: Syntax Tree Traversal]
            // We iterate over 'matches' found by the query. Each match contains 'captures'
            // which map our query labels (@name, @method) to specific syntax nodes.
            const capture = match.captures.find((c: any) => c.name === 'method');
            if (!capture) continue;

            const node = capture.node;
            // Get method signature (roughly first line)
            const signature = node.text.split('{')[0].trim();
            const startLine = node.startPosition.row;

            // Javadoc extraction (Naïve approach: check previous sibling)
            let doc = "";
            const prev = node.previousSibling;
            if (prev && (prev.type === 'block_comment' || prev.type === 'line_comment')) {
                doc = prev.text;
            }

            // [Concept: Unique Identification Strategy]
            // To support re-indexing (idempotency) and ensuring every method is distinct:
            // 1. Uniqueness: `${filePath}::${startLine}` guarantees uniqueness even if method names are identical.
            // 2. Idempotency: We 'Upsert' (Update/Insert). 
            //    We try to `remove` any existing doc with this ID first.
            //    This prevents "DOCUMENT_ALREADY_EXISTS" errors when running indexer multiple times.
            const uniqueId = `${filePath}::${startLine}`;

            // Handle Duplicates: Remove if exists, then Insert (Upsert)
            try {
                await remove(this.db!, uniqueId);
            } catch (e) {
                // Ignore if doesn't exist
            }

            await insert(this.db!, {
                id: uniqueId,
                signature: signature,
                packageName: packageName,
                code: node.text,
                doc: doc,
                path: filePath
            });
        }
    }
}