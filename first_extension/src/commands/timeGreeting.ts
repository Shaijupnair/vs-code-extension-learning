import * as vscode from 'vscode';

export function timeGreeting() {
    // Get the different parts of the time
    const now = new Date();
    const currentHour = now.getHours(); // Returns 0-23

    let greetingMessage: string;

    // Logic to determine greeting
    if (currentHour < 12) {
        greetingMessage = 'Good Morning, Avantika!';
    } else {
        greetingMessage = 'Good Evening!';
    }

    vscode.window.showInformationMessage(greetingMessage);
}
