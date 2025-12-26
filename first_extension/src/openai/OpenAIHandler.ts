import OpenAI from 'openai';
import { CodeSearcher } from '../search/CodeSearcher';
import * as vscode from 'vscode';

export class OpenAIHandler {
    private openai: OpenAI;
    private searcher: CodeSearcher;

    constructor(apiKey: string, context: vscode.ExtensionContext) {
        // Initialize OpenAI with the user's key
        this.openai = new OpenAI({
            apiKey: apiKey,
            // In VS Code extension, we occasionally need to dangeroulsyAllowBrowser 
            // if we were in webview, but here we are in Node process, so standard init is fine.
        });

        // Reuse your existing Searcher logic from Phase 2
        this.searcher = new CodeSearcher(context);
        this.searcher.init(); // Fire and forget load
    }

    async generateAnswer(userQuery: string): Promise<string> {
        // 1. Search Local Vector DB
        const context = await this.searcher.findRelevantApis(userQuery);

        // 2. Build the System Prompt
        // This instructs the AI to act as a legacy code expert
        const systemPrompt = `
            You are a Senior Developer with deep knowledge of this codebase.
            
            TASK: Answer the user's technical question.
            
            CRITICAL INSTRUCTIONS:
            1. Use the provided "EXISTING API MATCHES" to solve the problem.
            2. If a utility method exists in the matches, provide a code snippet calling it.
            3. Do NOT write new implementation logic if a reusable API exists.
            4. Format your response in clean Markdown.
            
            EXISTING API MATCHES (Retrieved from Index):
            ${context || "No relevant internal APIs found. Answer based on general Java knowledge."}
        `;

        // 3. Call OpenAI
        try {
            const completion = await this.openai.chat.completions.create({
                messages: [
                    { role: "system", content: systemPrompt },
                    { role: "user", content: userQuery }
                ],
                model: "gpt-4o", // Default to highly capable model.
            });

            return completion.choices[0].message.content || "No response generated.";
        } catch (error: any) {
            console.error(error);
            return `❌ **OpenAI API Error:** ${error.message}`;
        }
    }
}
