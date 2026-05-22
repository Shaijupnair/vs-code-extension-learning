To get the best results from **AntiGravity**, your prompt needs to be highly structured, 

---

## The Optimized AntiGravity Prompt

### **Role & Context**
"You are a Senior VS Code Extension Architect specializing in Custom Editor API implementations. I need you to scaffold a high-performance Custom Editor extension for **AntiGravity** that handles `.bmx` files (XML-based) using a dynamic, schema-driven React UI."

### **1. Architecture & Data Flow (Strict Constraint)**
"To ensure 'Single Source of Truth' and native Undo/Redo support, you **must** implement this exact unidirectional data flow:
1.  **Webview:** UI Control change triggers a message to the Extension.
2.  **Extension:** Receives message, calculates the XML diff, and applies a `vscode.WorkspaceEdit` to the underlying `TextDocument`.
3.  **VS Code:** Handles the native undo/redo stack and triggers `onDidChangeTextDocument`.
4.  **Extension:** Parses the updated XML, runs the validation logic, and pushes the new state + error array back to the Webview.
5.  **Webview:** Re-renders the React components based on the incoming state."



### **2. Technical Stack**
* **Frontend:** React (running in a Webview) using the **Webview UI Toolkit for VS Code** for a native look and feel.
* **State Management:** Reactive props/state driven by the extension's messages.
* **Validation:** Asynchronous validation that populates the VS Code **Problems** tab (`vscode.DiagnosticCollection`) to prevent UI blocking.

### **3. File Dependencies & Knowledge Base**
"Refer to the following local paths to build the logic:
* **Data File (.bmx):** XML format. Example: `E:\Learn_Vs_Code_Extension\vs-code-editor-extension\blood-test-editor\spec\bspec.xml`.
* **Schema:** `E:\Learn_Vs_Code_Extension\vs-code-editor-extension\blood-test-editor\spec\bspec_schema.xsd`.
* **UI Specification:** `E:\Learn_Vs_Code_Extension\vs-code-editor-extension\blood-test-editor\spec\ui_control_spec.json`.
    * *Note:* This JSON defines tabs (panels), control types, labels, tooltips, and valid ranges."

### **4. Component Requirements**
"For each item defined in the `ui_control_spec.json`, generate:
* A **Tab** for each panel in the `ui_control_spec.json`.
* Within each **Tab**create UI components listed in within that panel.
* A **Label** and its corresponding **UI Control** (Input, Dropdown, etc.).
* A **Tooltip** for help text.
* An **Interpretation Label** that updates dynamically based on the current value.
* **Validation Logic:** Silently validate against the 'Valid Range' in the JSON. Errors must appear in the VS Code Problems tab and highlight the relevant field in the Webview."

### **5. Action Items**
"Please generate:
0. Create detailed plan to implement the editor ask for clarification if needed.
1.  The `CustomEditorProvider` registration logic in `extension.ts`.
2.  The React-based Webview source code, including a dynamic component factory that maps `ui_control_spec.json` types to UI Toolkit components.
3.  The message-passing bridge that implements the `WorkspaceEdit` logic for XML manipulation.
4.  The Diagnostic provider for the validation layer."
5. Update the dependencies in `package.json` to include the required packages.
6. Run npm install to install the dependencies 

---



