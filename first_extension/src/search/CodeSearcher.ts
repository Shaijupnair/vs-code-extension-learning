import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { search } from '@orama/orama';
import { restore } from '@orama/plugin-data-persistence';
// Backend registration is CRITICAL here too
import '@tensorflow/tfjs-backend-cpu';
import * as tf from '@tensorflow/tfjs-core';

export class CodeSearcher {
    private db: any | null = null;
    private dbFilePath: string;

    constructor(context: vscode.ExtensionContext) {
        if (!context.globalStorageUri) {
            throw new Error("Global storage not available");
        }
        const workspaceName = vscode.workspace.name || 'default';
        // MUST match the filename format used in PersistentIndexer.ts
        this.dbFilePath = path.join(context.globalStorageUri.fsPath, `index-${workspaceName}-all-MiniLM-L6-v2.json`);
    }

    async init() {
        // 1. Ensure CPU Backend for Search Vector Generation
        // This prevents "No backend found" if this class is instantiated in a fresh worker/context.
        if (tf.getBackend() !== 'cpu') {
            await tf.setBackend('cpu');
        }
        await tf.ready();

        // 2. Load DB from Disk
        if (!fs.existsSync(this.dbFilePath)) {
            console.warn(`[Searcher] Index not found at ${this.dbFilePath}`);
            return;
        }

        try {
            const dbData = fs.readFileSync(this.dbFilePath, 'utf-8');
            this.db = await restore('json', JSON.parse(dbData));
            console.log('✅ Searcher: Database loaded into memory.');
        } catch (error) {
            console.error('❌ Searcher: Failed to load DB:', error);
        }
    }

    async findRelevantApis(queryText: string): Promise<string> {
        if (!this.db) {
            return ""; // DB not loaded yet
        }

        // 3. Run Hybrid Search (Keyword + Vector)
        const results = await search(this.db, {
            term: queryText,
            limit: 5, // Get top 5 matches
            mode: 'hybrid',
            properties: ['doc', 'signature', 'code', 'packageName'] // Search these fields
        });

        if (results.count === 0) {
            return "";
        }

        // 4. Format for the AI
        return results.hits.map((hit: any) => {
            const doc = hit.document;
            return `
=== EXISTING API MATCH ===
Package: ${doc.packageName}
Signature: ${doc.signature}
Javadoc: ${doc.doc}
Code:
${doc.code}
==========================
`;
        }).join('\n');
    }
}
