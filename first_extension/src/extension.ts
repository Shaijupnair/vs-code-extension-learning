import * as vscode from 'vscode';
import { helloWorld } from './commands/helloWorld';
import { timeGreeting } from './commands/timeGreeting';
import { addTask, showRandomTask, showHighPriorityTasks, setupWordCount } from './commands/todo';
import { selectFolder } from './commands/folderbrowser';
import { searchFileHandler } from './commands/searchFile';
import { registerChatParticipant } from './chat/Agent';
import { askOpenAICommand } from './commands/AskCommand';

export function activate(context: vscode.ExtensionContext) {
    console.log('Congratulations, your extension "first-extension" is now active!');

    // Initialize the Debounced Word Count feature
    setupWordCount(context);

    // Register all commands
    context.subscriptions.push(
        vscode.commands.registerCommand('first-extension.helloWorld', helloWorld)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('first-extension.timeGreeting', timeGreeting)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('first-extension.addTask', addTask)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('first-extension.showRandomTask', showRandomTask)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('first-extension.showHighPriority', showHighPriorityTasks)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('first-extension.selectFolder', selectFolder)
    );

    // Register AI Indexing Command
    context.subscriptions.push(
        vscode.commands.registerCommand('first-extension.indexSource', require('./commands/IndexSource').indexSourceHandler(context))
    );

    // Register Promise Demo Command
    context.subscriptions.push(
        vscode.commands.registerCommand('first-extension.searchFile', searchFileHandler())
    );

    // --- PHASE 2: Chat Participant ---
    console.log('Activating Legacy API Agent...');
    registerChatParticipant(context);

    // --- PHASE 3: OpenAI Agent ---
    context.subscriptions.push(
        vscode.commands.registerCommand('agent.askOpenAI', () => {
            askOpenAICommand(context);
        })
    );

}

export function deactivate() { }
