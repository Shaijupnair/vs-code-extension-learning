import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { OpenAIHandler } from '../openai/OpenAIHandler';

export async function askOpenAICommand(context: vscode.ExtensionContext) {

    // 1. Get API Key (Best practice: Store in Settings, but prompting for now is easier)
    // We check configuration first
    let apiKey = vscode.workspace.getConfiguration('legacyAgent').get<string>('openaiApiKey');

    // [File Check]
    const keyFilePath = path.join(context.extensionPath, 'resources', 'openai_key.txt');
    if (fs.existsSync(keyFilePath)) {
        try {
            const fileContent = fs.readFileSync(keyFilePath, 'utf-8').trim();
            // Basic validation to avoid using the placeholder
            if (fileContent && !fileContent.startsWith("PASTE_YOUR") && fileContent.length > 10) {
                console.log(`Using API Key from file: ${keyFilePath}`);
                apiKey = fileContent;
            }
        } catch (e) {
            console.warn("Failed to read key file", e);
        }
    }

    if (!apiKey) {
        apiKey = await vscode.window.showInputBox({
            prompt: "Enter your OpenAI API Key",
            password: true,
            ignoreFocusOut: true,
            placeHolder: "sk-..."
        });

        if (apiKey) {
            // Save it for next time globally
            await vscode.workspace.getConfiguration('legacyAgent').update('openaiApiKey', apiKey, vscode.ConfigurationTarget.Global);
        } else {
            return; // User cancelled
        }
    }

    // 2. Get User Query
    const query = await vscode.window.showInputBox({
        placeHolder: "E.g., How do I parse an XML file using our utilities?",
        prompt: "Ask the Legacy Code Agent (OpenAI)"
    });

    if (!query) return;

    // 3. Show Progress while thinking
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "Agent: Consulting Legacy Index...",
        cancellable: false
    }, async (progress) => {

        progress.report({ message: "Connecting to OpenAI..." });

        const handler = new OpenAIHandler(apiKey!, context);
        const answer = await handler.generateAnswer(query);

        // 4. Show Result in a Webview Panel (The "Rich Popup")
        const panel = vscode.window.createWebviewPanel(
            'legacyAgentResult',
            'Agent Answer',
            vscode.ViewColumn.Beside, // Opens in split view
            { enableScripts: true }
        );

        panel.webview.html = getWebviewContent(query, answer);
    });
}

// Helper: Generate clean HTML for the answer
function getWebviewContent(query: string, markdownAnswer: string): string {
    // Basic styling to match VS Code theme
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'unsafe-inline';">
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; color: var(--vscode-editor-foreground); background-color: var(--vscode-editor-background); }
            h1, h2, h3 { border-bottom: 1px solid var(--vscode-descriptionForeground); padding-bottom: 5px; }
            code { background-color: var(--vscode-textBlockQuote-background); padding: 2px 4px; border-radius: 3px; font-family: var(--vscode-editor-font-family); }
            pre { background-color: var(--vscode-textBlockQuote-background); padding: 10px; border-radius: 5px; overflow-x: auto; }
            pre code { background-color: transparent; padding: 0; }
            .query { font-style: italic; color: var(--vscode-descriptionForeground); margin-bottom: 20px; border-left: 3px solid var(--vscode-textLink-foreground); padding-left: 10px; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    </head>
    <body>
        <div class="query">Q: ${query}</div>
        <div id="content">Loading...</div>
        <script>
            // Render the Markdown sent from the extension
            const rawMarkdown = ${JSON.stringify(markdownAnswer)};
            try {
                document.getElementById('content').innerHTML = marked.parse(rawMarkdown);
            } catch (e) {
                document.getElementById('content').innerText = "Error parsing markdown: " + e;
            }
        </script>
    </body>
    </html>
    `;
}
