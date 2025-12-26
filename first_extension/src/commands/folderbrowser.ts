import * as vscode from 'vscode';

/**
 * Command Handler for 'Select Folder'
 * 
 * Logic:
 * 1. Opens a native OS dialog.
 * 2. Restricts selection to usage folders only (no files).
 * 3. Returns the selected path to the user.
 */
export async function selectFolder() {
    // vscode.window.showOpenDialog is the standard API to open file/folder pickers.
    // It returns a Promise that resolves to an array of URIs (or undefined if cancelled).
    const folderUri = await vscode.window.showOpenDialog({
        // Reasoning: We want the users to pick a directory to work with, not individual files.
        canSelectFiles: false,

        // Reasoning: This must be true to allow folder selection.
        canSelectFolders: true,

        // Reasoning: To keep logic simple, we restrict the user to picking just one folder at a time.
        canSelectMany: false,

        // Reasoning: Customizable label for the "Open" button to make the action clear.
        openLabel: 'Select Folder'
    });

    // Check if the user actually picked something (not undefined) and that the array is not empty
    if (folderUri && folderUri.length > 0) {
        // We take the first element [0] because we disabled multiple selection (canSelectMany: false).
        // .fsPath gives us the standard filesystem path (e.g., "c:\Users\Name\Folder")
        const selectedUri = folderUri[0];
        const selectedPath = selectedUri.fsPath;

        // Feedback to the user: We are starting the calculation (since it might take a moment)
        vscode.window.setStatusBarMessage('Calculating folder size...', 3000);

        try {
            // Calculate size recursively
            const sizeInBytes = await getFolderSize(selectedUri);
            const formattedSize = formatBytes(sizeInBytes);

            vscode.window.showInformationMessage(`📂 Folder: ${selectedPath}\n📊 Size: ${formattedSize}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Error calculating size: ${error}`);
        }

    } else {
        // Reasoning: Good UX requires acknowledging "Cancellation" or "No Selection" so the user isn't left wondering.
        vscode.window.showInformationMessage('No folder selected.');
    }
}

/**
 * Recursively calculates the size of a folder and its subfolders.
 * @param uri The URI of the folder to measure.
 * @returns Total size in bytes.
 */
async function getFolderSize(uri: vscode.Uri): Promise<number> {
    let totalSize = 0;

    try {
        // vscode.workspace.fs.readDirectory returns an array of [name, FileType] pairs
        const children = await vscode.workspace.fs.readDirectory(uri);

        for (const [name, type] of children) {
            // Construct the full URI for the child
            const childUri = vscode.Uri.joinPath(uri, name);

            if (type === vscode.FileType.File) {
                // If it's a file, get its metadata to find the size
                const stat = await vscode.workspace.fs.stat(childUri);
                totalSize += stat.size;
            } else if (type === vscode.FileType.Directory) {
                // If it's a directory, RECURSE! (Call this same function again)
                totalSize += await getFolderSize(childUri);
            }
            // We ignore Symlinks or other types to avoid infinite loops or errors
        }
    } catch (e) {
        // If we can't read a specific folder (permissions, etc.), just ignore it
        // console.error(`Failed to read ${uri.fsPath}`);
    }

    return totalSize;
}

/**
 * Helper to convert raw bytes into human-readable strings (KB, MB, GB).
 */
function formatBytes(bytes: number, decimals = 2): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    // Calculate the log base 1024 to find which unit to use
    // Math.floor(Math.log(1024) / Math.log(1024)) = 1 (KB)
    // Math.floor(Math.log(1000000) / Math.log(1024)) = 2 (MB)
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}
