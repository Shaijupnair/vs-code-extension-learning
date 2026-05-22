/**
 * Thin wrapper around the VS Code webview API.
 * acquireVsCodeApi() can only be called once per webview lifetime.
 */

interface VsCodeApi {
  postMessage(message: unknown): void;
  getState(): unknown;
  setState(state: unknown): void;
}

// Cache the API instance — acquireVsCodeApi can only be called once
let api: VsCodeApi | undefined;

export function getVsCodeApi(): VsCodeApi {
  if (!api) {
    // @ts-expect-error — acquireVsCodeApi is injected by VS Code at runtime
    api = acquireVsCodeApi();
  }
  return api!;
}
