import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

/**
 * [Concept: Higher-Order Function / Factory Pattern]
 * Syntax: `() => async () => { ... }`
 * 1. `searchFileHandler` is a function that takes NO arguments `()`.
 * 2. It RETURNS another function `async () => { ... }`.
 * 3. The returned function is the actual Command Handler executed by VS Code.
 * 
 * Why? This pattern allows us to 'inject' dependencies (like context) in the first call,
 * which are then available to the inner function via Closure.
 */
export const searchFileHandler = () => async () => {

    // 1. Get Input from User (UI Interaction)
    // This is an async operation (returns a Promise) because we wait for the user to type and press Enter.
    const fileName = await vscode.window.showInputBox({
        prompt: "Enter file name to search (e.g., 'notes.txt')",
        placeHolder: "filename.ext"
    });

    if (!fileName) {
        vscode.window.showWarningMessage("Search cancelled.");
        return;
    }

    vscode.window.showInformationMessage(`Starting parallel search for '${fileName}' on C: and D:...`);

    // [Concept: Promise & Parallel Execution]
    // Syntax: `const worker1 = searchDrive(...)` (WITHOUT await)
    // - When you call an `async` function, it IMMEDIATELY returns a Promise object.
    // - The code inside starts running in the background (microtask queue).
    // - By NOT using `await` here, we do NOT pause this function. We let the search begin.
    // - This effectively starts "Task 1" in parallel with whatever comes next.

    // Task 1: Search C Drive

    // Task 1: Search C Drive
    const worker1 = searchDrive('C:/', fileName, 0);

    // Task 2: Search D Drive (Assuming it exists, or simulated)
    const worker2 = searchDrive('D:/', fileName, 0)
        .catch(err => {
            // [Concept: Promise Rejection Handling]
            // If D: doesn't exist, this promise will fail/reject.
            // We catch it here to prevent the whole operation from crashing.
            console.log("D: drive search skipped or failed", err);
            return "D: Drive unavailable";
        });

    // [Concept: Synchronization with Promise.all]
    // Syntax: `await Promise.all([p1, p2, ...])`
    // - Takes an ARRAY of Promises.
    // - Returns a NEW Promise that resolves when ALL items in the array are resolved.
    // - `await` pauses execution HERE until that happens.
    // - `results` will be an ARRAY containing the resolution value of each promise in order.
    try {
        const results = await Promise.all([worker1, worker2]);

        // results matches the order of input promises: [resultFromC, resultFromD]
        const finalMessage = `Search Complete!\nC: ${results[0]}\nD: ${results[1]}`;
        vscode.window.showInformationMessage(finalMessage);

    } catch (error) {
        vscode.window.showErrorMessage("An error occurred during search: " + error);
    }
};

/**
 * Searches for a file in a given directory recursively.
 * Returns a Promise that resolves with a status message.
 * 
 * [Concept: Async Function Definition]
 * Syntax: `async function name(...): Promise<Type> { ... }`
 * - `async` keyword ensures the function ALWAYS returns a Promise.
 * - `Promise<string>`: TypeScript annotation saying this promise will eventually yield a string.
 */
async function searchDrive(rootPath: string, targetFile: string, depth: number): Promise<string> {
    // [Concept: Manual Promise Construction]
    // Syntax: `new Promise<T>((resolve, reject) => { ... })`
    // - Used when wrapping callback-based APIs (like fs.readdir) into Promises.
    // - `resolve(value)`: Call this to successfully finish the promise.
    // - `reject(error)`: Call this to fail the promise.
    return new Promise<string>((resolve, reject) => {

        // Limit depth to prevent infinite loops or hanging the PC for this demo
        if (depth > 3) {
            resolve("Depth limit reached (Demo)");
            return;
        }

        // Check if drive/folder exists
        if (!fs.existsSync(rootPath)) {
            reject(new Error(`Path ${rootPath} does not exist`));
            return;
        }

        // [Concept: Callbacks (Legacy Pattern)]
        // Syntax: `fs.readdir(path, options, (err, data) => { ... })`
        // - This is NOT a promise. It takes a function (callback) as the last argument.
        // - Node.js "Error-First Callback" style: first arg `err` is null if successful.
        fs.readdir(rootPath, { withFileTypes: true }, async (err, entries) => {
            if (err) {
                // If permission denied or other error, we just resolve with "Skipped" 
                // to keep the flow going, or we could reject.
                resolve("Access Denied/Skipped");
                return;
            }

            let foundPaths: string[] = [];
            const subFolderPromises: Promise<string>[] = [];

            for (const entry of entries) {
                const fullPath = path.join(rootPath, entry.name);

                if (entry.isFile()) {
                    if (entry.name.toLowerCase() === targetFile.toLowerCase()) {
                        foundPaths.push(fullPath);
                        // Notify immediately when found (as requested)
                        vscode.window.showInformationMessage(`FOUND: ${fullPath}`);
                    }
                } else if (entry.isDirectory()) {
                    // [Concept: Recursive Promises]
                    // We start a search in the subfolder. This adds another "thread" of work.
                    // We don't await immediately, we collect promises.
                    subFolderPromises.push(searchDrive(fullPath, targetFile, depth + 1));
                }
            }

            // Wait for all subfolders to finish searching
            await Promise.all(subFolderPromises);

            if (foundPaths.length > 0) {
                resolve(`Found ${foundPaths.length} matches.`);
            } else {
                resolve("No matches found.");
            }
        });
    });
}
