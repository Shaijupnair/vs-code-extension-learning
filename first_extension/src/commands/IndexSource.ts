import * as vscode from 'vscode';
import { PersistentIndexer } from '../indexer/PersistantIndexer';

// ----------------------------------------------------------------------------------
// This function exports a "Factory Pattern" or "Curried Function".
// 
// Concept: Higher-Order Function
// Instead of just being a function that runs, this is a function that *returns* 
// another function.
// 
// Why?
// We need the `vscode.ExtensionContext` to initialize our dependencies (like PersistentIndexer),
// but the actual command registry in VS Code expects a function that takes no arguments (or specific args).
// By passing `context` first, we "bake it in" to the returned function so it's available when needed.
// 
// JS CONCEPT DEEP DIVE: "The Double Arrow"
// export const indexSourceHandler = (context) => async () => { ... }
//
// 1. The "Double Arrow" Pattern (Currying / Higher-Order Function)
//    In simple terms, this is a function that returns another function.
//    Think of it like a Factory. You give the factory a `context` (toolbelt), 
//    and it creates a specific worker function for you that is ready to work.
//
// 2. The Concept of "Closure" (The Magic)
//    - The Problem: The inner function (the worker) runs later (when user clicks).
//      But it needs `context` which is only available NOW.
//    - The Solution: JavaScript functions "remember" variables from when they were created.
//    - Result: Even though `indexSourceHandler` finishes immediately, the inner function 
//      keeps `context` in its "backpack" (Closure) forever.
//
// 3. Visual Breakdown
//    `const indexSourceHandler` -> Name of the factory
//    `= (context)`             -> Argument for the factory
//    `=>`                      -> "Returns..."
//    `async ()`                -> ...an async function taking zero args
//    `=> { ... }`              -> The body of the worker function
// ----------------------------------------------------------------------------------
export const indexSourceHandler = (context: vscode.ExtensionContext) => async () => {

    // ------------------------------------------------------------------------------
    // TS Concept: Promises & Async/Await
    // VS Code APIs for UI (like dialogs) are asynchronous. They don't block the computer.
    // We use `await` to pause this function until the user actually picks a folder.
    // ------------------------------------------------------------------------------
    const folderUri = await vscode.window.showOpenDialog({
        canSelectFiles: false,      // User can't pick files
        canSelectFolders: true,     // User MUST pick a folder
        canSelectMany: false,       // User can only pick one
        openLabel: 'Select Folder to Index'
    });

    // Guard Clause:
    // If the user cancelled the dialog, folderUri will be undefined or empty.
    if (!folderUri || folderUri.length === 0) {
        return;
    }

    // ------------------------------------------------------------------------------
    // VS Code Concept: URIs vs Paths
    // VS Code uses `Uri` objects to handle files because they could be remote (SSH, WSL, Web).
    // `fsPath` gives us the OS-specific string path (e.g., "C:\Users\Name\...") 
    // which our node.js `fs` module needs.
    // ------------------------------------------------------------------------------
    const selectedFolder = folderUri[0].fsPath;

    // Initialize our service class with the context we received earlier.
    const indexer = new PersistentIndexer(context);

    // ------------------------------------------------------------------------------
    // VS Code Concept: Progress Notifications
    // `withProgress` shows a small notification window that tracks our long-running task.
    // It's "Thenable" (Promise-like), so we await it to ensure we don't finish too early.
    // ------------------------------------------------------------------------------
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification, // Show at bottom right
        title: "AI Indexing Source",
        cancellable: true // Adds a "Cancel" button for the user
    }, async (progress, token) => {
        // --------------------------------------------------------------------------
        // Concept: Error Handling
        // Always wrap async/heavy operations in try/catch blocks.
        // If something breaks (network, file permissions), we catch it smoothly 
        // instead of crashing the extension.
        // --------------------------------------------------------------------------
        try {
            progress.report({ message: "Initializing..." });

            // Perform the heavy lifting
            await indexer.init();

            // Pass the progress object down so the indexer can update the UI too!
            await indexer.indexFolder(selectedFolder, progress, token);

            vscode.window.showInformationMessage(`Successfully indexed: ${selectedFolder}`);

        } catch (err: any) {
            // TS Concept: `any` type
            // In a catch block, TS doesn't know what `err` is (it could be anything).
            // We cast to `any` here to safely access `.message`. 
            // In stricter code, we might check `if (err instanceof Error)`.
            vscode.window.showErrorMessage(`Indexing failed: ${err.message}`);
            console.error(err);
        }
    });
};
