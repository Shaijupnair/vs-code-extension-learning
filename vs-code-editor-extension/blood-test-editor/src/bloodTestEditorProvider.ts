import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { parseBloodTestXml, buildVitalEdit, buildTestEdit, buildMetaEdit } from './xmlParser';
import { validateState, buildDiagnostics } from './validator';
import type { BloodTestState, UiControlSpec, WebviewMessage, ExtensionMessage, FieldError } from './types';

/**
 * CustomTextEditorProvider for .bmx (Blood Test XML) files.
 * Implements the unidirectional data flow:
 *   Webview → Extension (WorkspaceEdit) → VS Code → Extension (parse+validate) → Webview
 */
export class BloodTestEditorProvider implements vscode.CustomTextEditorProvider {

  public static readonly viewType = 'bloodTestEditor.bmxEditor';

  private readonly diagnosticCollection: vscode.DiagnosticCollection;
  private uiSpec: UiControlSpec | undefined;

  constructor(private readonly context: vscode.ExtensionContext) {
    this.diagnosticCollection = vscode.languages.createDiagnosticCollection('bloodTestEditor');

    // Load the UI control spec
    try {
      const specPath = path.join(context.extensionPath, 'spec', 'ui_control_spec.json');
      console.log('[BloodTestEditor] Loading UI spec from:', specPath);
      console.log('[BloodTestEditor] File exists:', fs.existsSync(specPath));
      const specText = fs.readFileSync(specPath, 'utf-8');
      this.uiSpec = JSON.parse(specText) as UiControlSpec;
      console.log('[BloodTestEditor] UI spec loaded OK. Panels:', this.uiSpec.panels.length);
    } catch (err) {
      console.error('[BloodTestEditor] ERROR loading UI spec:', err);
      this.uiSpec = undefined;
    }
  }

  public async resolveCustomTextEditor(
    document: vscode.TextDocument,
    webviewPanel: vscode.WebviewPanel,
    _token: vscode.CancellationToken
  ): Promise<void> {

    console.log('[BloodTestEditor] resolveCustomTextEditor called for:', document.uri.toString());
    console.log('[BloodTestEditor] Document length:', document.getText().length, 'chars');

    if (!this.uiSpec) {
      console.error('[BloodTestEditor] UI spec not loaded — cannot render editor');
      webviewPanel.webview.html = '<html><body><h2>Error: UI spec not found</h2><p>Check the Debug Console for details.</p></body></html>';
      return;
    }

    // Configure the webview
    webviewPanel.webview.options = {
      enableScripts: true,
      localResourceRoots: [
        vscode.Uri.file(path.join(this.context.extensionPath, 'dist')),
      ],
    };

    // Set the HTML content
    const html = this.getHtmlForWebview(webviewPanel.webview);
    console.log('[BloodTestEditor] Setting webview HTML, length:', html.length);
    webviewPanel.webview.html = html;

    // Capture uiSpec for closures
    const uiSpec = this.uiSpec;

    // Helper to send state to the webview
    const updateWebview = (msgType: 'init' | 'update') => {
      const xmlText = document.getText();
      console.log(`[BloodTestEditor] updateWebview('${msgType}') — XML length: ${xmlText.length}`);
      let state: BloodTestState;
      try {
        state = parseBloodTestXml(xmlText);
        console.log('[BloodTestEditor] Parsed state OK — vitals:', state.vitals.length, 'panels:', state.panels.length);
      } catch (err) {
        console.error('[BloodTestEditor] XML parse error:', err);
        state = {
          reportId: '', generatedDate: '', laboratoryName: '',
          patient: { patientId: '', fullName: '', dob: '', gender: '', bloodType: '' },
          vitals: [], panels: [],
        };
      }

      const errors: FieldError[] = validateState(state, uiSpec);
      console.log('[BloodTestEditor] Validation errors:', errors.length);

      // Update diagnostics in the Problems tab
      const diagnostics = buildDiagnostics(errors, xmlText);
      this.diagnosticCollection.set(document.uri, diagnostics);

      const message: ExtensionMessage = {
        type: msgType,
        state,
        errors,
        uiSpec: uiSpec,
      };
      console.log('[BloodTestEditor] Posting message to webview, type:', msgType);
      webviewPanel.webview.postMessage(message);
    };

    // Listen for messages from the webview
    webviewPanel.webview.onDidReceiveMessage(
      async (message: WebviewMessage) => {
        console.log('[BloodTestEditor] Received message from webview:', JSON.stringify(message).substring(0, 200));
        switch (message.type) {
          case 'ready':
            console.log('[BloodTestEditor] Webview is ready, sending init...');
            updateWebview('init');
            return;

          case 'editVital': {
            const xmlText = document.getText();
            const editInfo = buildVitalEdit(xmlText, message.vitalType, message.value);
            if (editInfo) {
              const edit = new vscode.WorkspaceEdit();
              const line = document.lineAt(editInfo.lineIndex);
              edit.replace(document.uri, line.range, editInfo.newLine);
              await vscode.workspace.applyEdit(edit);
            }
            return;
          }

          case 'editTest': {
            const xmlText = document.getText();
            const editInfo = buildTestEdit(
              xmlText, message.panelName, message.testIndex, message.field, message.value
            );
            if (editInfo) {
              const edit = new vscode.WorkspaceEdit();
              const line = document.lineAt(editInfo.lineIndex);
              edit.replace(document.uri, line.range, editInfo.newLine);
              await vscode.workspace.applyEdit(edit);
            }
            return;
          }

          case 'editMeta': {
            const xmlText = document.getText();
            const editInfo = buildMetaEdit(xmlText, message.field, message.value);
            if (editInfo) {
              const edit = new vscode.WorkspaceEdit();
              const line = document.lineAt(editInfo.lineIndex);
              edit.replace(document.uri, line.range, editInfo.newLine);
              await vscode.workspace.applyEdit(edit);
            }
            return;
          }
        }
      },
      undefined,
      this.context.subscriptions
    );

    // Listen for document changes (from WorkspaceEdit, undo/redo, or external edits)
    const changeDocSub = vscode.workspace.onDidChangeTextDocument(e => {
      if (e.document.uri.toString() === document.uri.toString() && e.contentChanges.length > 0) {
        updateWebview('update');
      }
    });

    // Clean up when the editor is closed
    webviewPanel.onDidDispose(() => {
      changeDocSub.dispose();
      this.diagnosticCollection.delete(document.uri);
    });

    // Send initial state immediately (safety net in case 'ready' message is missed)
    console.log('[BloodTestEditor] Sending initial state to webview...');
    updateWebview('init');
  }

  /**
   * Generate the secure HTML for the webview.
   */
  private getHtmlForWebview(webview: vscode.Webview): string {
    const scriptPath = path.join(this.context.extensionPath, 'dist', 'webview.js');
    console.log('[BloodTestEditor] Script file exists:', fs.existsSync(scriptPath));
    
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.file(scriptPath)
    );
    console.log('[BloodTestEditor] Script URI:', scriptUri.toString());

    const nonce = getNonce();

    return /* html */ `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Security-Policy" 
              content="default-src 'none'; 
                       style-src ${webview.cspSource} 'unsafe-inline'; 
                       font-src ${webview.cspSource}; 
                       img-src ${webview.cspSource}; 
                       script-src 'nonce-${nonce}' ${webview.cspSource};">
        <title>Blood Test Editor</title>
      </head>
      <body>
        <div id="root"><p>React is loading...</p></div>
        <script nonce="${nonce}">
          window.onerror = function(msg, url, line, col, error) {
            var el = document.getElementById('root');
            if (el) {
              el.innerHTML = '<pre style="color:red;padding:16px;white-space:pre-wrap;">SCRIPT ERROR:\\n' + msg + '\\nURL: ' + url + '\\nLine: ' + line + '\\n' + (error && error.stack ? error.stack : '') + '</pre>';
            }
            return false;
          };
          console.log('[Webview] Error handler installed');
        </script>
        <script nonce="${nonce}" src="${scriptUri}"></script>
      </body>
      </html>
    `;
  }

  public dispose(): void {
    this.diagnosticCollection.dispose();
  }
}

function getNonce(): string {
  let text = '';
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}
