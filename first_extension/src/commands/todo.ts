import * as vscode from 'vscode';

// Interface defining the structure of a To-Do item
interface TodoItem {
    description: string;
    priority: string;
}

// GLOBAL VARIABLE (Array of Objects)
// Changed from string[] to TodoItem[] to store multiple properties per task
let todoList: TodoItem[] = [];

export async function addTask() {
    // Prompt the user for input
    const result = await vscode.window.showInputBox({
        placeHolder: 'e.g., "Fix login bug; High"',
        prompt: 'Add a task. Optional: Add "; Priority" at the end.'
    });

    // Check if input is valid
    if (result && result.trim().length > 0) {
        // Parse the input strings
        // "Fix login bug; High" -> ["Fix login bug", " High"]
        const parts = result.split(';');

        // Part 0 is always the description
        const description = parts[0].trim();

        // Part 1 is the priority (if it exists), otherwise default to "Normal"
        // We checking if parts[1] exists and is not empty
        let priority = 'Normal';
        if (parts.length > 1 && parts[1].trim().length > 0) {
            priority = parts[1].trim();
        }

        // Create the new object
        const newTask: TodoItem = {
            description: description,
            priority: priority
        };

        // Add to our list
        todoList.push(newTask);

        vscode.window.showInformationMessage(`Task added: "${description}" (Priority: ${priority})`);
    } else {
        vscode.window.showErrorMessage('No task entered!');
    }
}

export function showRandomTask() {
    // Check if list is empty
    if (todoList.length === 0) {
        vscode.window.showInformationMessage('Your To-Do list is empty! Add some tasks first.');
        return;
    }

    // Pick a random index
    const randomIndex = Math.floor(Math.random() * todoList.length);
    const randomTask = todoList[randomIndex];

    // Display the task with its priority
    // Using an icon/emoji for the priority makes it look nicer
    vscode.window.showInformationMessage(`🎲 [${randomTask.priority}] ${randomTask.description}`);
}

export function showHighPriorityTasks() {
    // 1. Filter the list using the .filter() array method
    // This creates a NEW array containing ONLY the items where priority is 'High'
    // case-sensitive check: 'High' must match exactly
    const highPriorityTasks = todoList.filter((task) => {
        return task.priority.trim() === 'High';
    });

    // 2. Check if we found any
    if (highPriorityTasks.length === 0) {
        vscode.window.showInformationMessage('No High priority tasks found! Good job!');
        return;
    }

    // 3. Format the output
    // We map each object to a string "• Task Name"
    const taskNames = highPriorityTasks.map(task => `• ${task.description}`);

    // Join them with newlines to make a single list
    const message = `🔥 High Priority Tasks:\n${taskNames.join('\n')}`;

    // 4. Show the list in a modal dialog (modal: true forces the user to close it)
    vscode.window.showInformationMessage(message, { modal: true });
}

// =================================================================================
// DEBOUNCED WORD COUNT FEATURE
// =================================================================================

/**
 * Higher-Order Function: Debounce
 * 
 * Concept:
 * A Higher-Order function is a function that takes another function as input 
 * or returns a function as output.
 * 
 * Logic:
 * 1. Takes a function (`func`) and a delay (`wait`).
 * 2. Returns a NEW function that manages a timer.
 * 3. Closure: The returned function has access to `timeout` even after `debounce` finishes.
 */
function debounce(func: Function, wait: number) {
    let timeout: NodeJS.Timeout | undefined;

    return function (...args: any[]) {
        // If a timer is already running (user is typing fast), cancel it!
        if (timeout) {
            clearTimeout(timeout);
        }

        // Start a new timer
        // The original function (`func`) will ONLY run if this timer completes
        // without being cleared by a new keystroke.
        timeout = setTimeout(() => {
            func(...args);
        }, wait);
    };
}

// Status Bar Item reference
let wordCountStatusBar: vscode.StatusBarItem;

// The actual logic to count words
function updateWordCount() {
    // Get the active text editor
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        if (wordCountStatusBar) wordCountStatusBar.hide();
        return;
    }

    // Get the text from the document
    const doc = editor.document;
    const text = doc.getText();

    // Count words (split by whitespace)
    const wordCount = text.split(/\s+/).filter(word => word.length > 0).length;

    // Update the status bar
    if (wordCountStatusBar) {
        wordCountStatusBar.text = `$(pencil) ${wordCount} Words`;
        wordCountStatusBar.show();
    }
}

/**
 * Sets up the word count feature.
 * Should be called from extension.ts activate().
 */
export function setupWordCount(context: vscode.ExtensionContext) {
    // Create the status bar item (Alignment: Left, Priority: 100)
    wordCountStatusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    context.subscriptions.push(wordCountStatusBar);

    // Create the DEBOUNCED version of our function
    // We wrap `updateWordCount` so it only runs after 300ms of silence
    const debouncedUpdate = debounce(updateWordCount, 300);

    // Listen to keystrokes (document changes)
    // Every time the user types, `debouncedUpdate` is called.
    // But thanks to logic above, `updateWordCount` only runs when they STOP typing.
    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument(debouncedUpdate)
    );

    // Also update when changing files
    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(updateWordCount)
    );

    // Run once on start
    updateWordCount();
}
