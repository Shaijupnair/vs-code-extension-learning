import * as vscode from 'vscode';
import { CodeSearcher } from '../search/CodeSearcher';

export function registerChatParticipant(context: vscode.ExtensionContext) {

    // 1. Initialize Searcher (Background Load)
    const searcher = new CodeSearcher(context);
    searcher.init().catch(err => console.error("Failed to init searcher:", err));

    // 2. Define the Chat Handler
    const handler: vscode.ChatRequestHandler = async (
        request: vscode.ChatRequest,
        chatContext: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ) => {

        // A. Indicate we are working
        stream.progress('Searching internal knowledge base...');

        // B. Search Local DB
        const relevantContext = await searcher.findRelevantApis(request.prompt);

        if (!relevantContext) {
            stream.markdown('ℹ️ **No relevant legacy APIs found in the index.**\n\n');
            stream.markdown('Run the `DevDash: Index Source Folder` command if you haven\'t yet.\n\n');
            stream.markdown('Proceeding with general AI response...\n\n');
        } else {
            stream.markdown('🔎 **I found existing APIs that might help:**\n\n');
            // Optional: Show a collapsed detail view
            // Note: In real app, you might construct a real URI to show the code file
            // stream.reference(...) 
        }

        // C. Construct System Prompt
        // This instructs Copilot to prioritize your APIs.
        const systemPrompt = `
            You are an expert developer for this specific project.
            
            GOAL: Answer the user's request. 
            CRITICAL RULE: If the "Context" below contains reusable Java APIs, you MUST use them in your solution. 
            Do not write new helper functions if one already exists in the Context.
            
            CONTEXT (Retrieved from Project Knowledge Base):
            ${relevantContext || "No specific internal APIs found."}
        `;

        // D. Send to VS Code Language Model (Copilot GPT-4)
        try {
            // Select GPT-4 or similar high-reasoning model
            const [model] = await vscode.lm.selectChatModels({ family: 'gpt-4' });

            if (!model) {
                // Fallback to any model if gpt-4 specific one not found (e.g. 'copilot-chat')
                // But better to warn user.
                stream.markdown("❌ **Error:** GitHub Copilot (GPT-4) model not accessible. Please ensure you have GitHub Copilot Chat installed.");
                return;
            }

            const messages = [
                vscode.LanguageModelChatMessage.User(systemPrompt),
                vscode.LanguageModelChatMessage.User(request.prompt)
            ];

            const chatResponse = await model.sendRequest(messages, {}, token);

            // E. Stream the AI's answer chunk by chunk
            for await (const fragment of chatResponse.text) {
                stream.markdown(fragment);
            }

        } catch (err) {
            stream.markdown(`\n\n❌ **Error communicating with AI:** ${err}`);
        }
    };

    // 3. Register the Participant
    const participant = vscode.chat.createChatParticipant('legacy.apiHelper', handler);
    // 'library' icon looks like code books
    participant.iconPath = new vscode.ThemeIcon('library');

    context.subscriptions.push(participant);
}
