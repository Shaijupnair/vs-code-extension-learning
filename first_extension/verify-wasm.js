const Module = require('web-tree-sitter');
const path = require('path');
const fs = require('fs');

// Based on debug analysis:
// Module = { Parser: class Parser { static init()... }, Language: class Language... }
const Parser = Module.Parser;
const Language = Module.Language;

// ... configuration ...
const WASM_RELATIVE_PATH = 'resources/wasm/tree-sitter-java.wasm';

async function verify() {
    console.log("🔍 Starting WASM Verification...\n");

    // 1. Resolve the full path
    const wasmPath = path.resolve(__dirname, WASM_RELATIVE_PATH);
    console.log(`Checking path: ${wasmPath}`);

    // ... (file check remains same) ...
    if (!fs.existsSync(wasmPath)) {
        console.error("❌ ERROR: File not found!");
        process.exit(1);
    }
    console.log("✅ File found on disk.");

    // 3. Try to load it
    try {
        await Parser.init(); // Calling static init on the class
        console.log("✅ Core initialized.");

        const lang = await Language.load(wasmPath);
        console.log("✅ WASM loaded successfully into Tree-sitter.");

        const parser = new Parser();
        parser.setLanguage(lang);

        const nodeTypeCount = lang.nodeTypeCount;
        console.log(`✅ Verification Complete! The Java grammar contains ${nodeTypeCount} node types.`);

    } catch (error) {
        console.error("❌ ERROR: File exists but failed to load.");
        console.error("   -> Error details:", error.message);
        process.exit(1);
    }
}

verify();