import React, { useState, useEffect } from 'react';
import { PanelTab } from './components/PanelTab';
import { getVsCodeApi } from './hooks/useVsCodeApi';
import './styles/editor.css';

// Types mirrored to avoid cross-compilation
interface BloodTestState {
  reportId: string;
  generatedDate: string;
  laboratoryName: string;
  patient: {
    patientId: string;
    fullName: string;
    dob: string;
    gender: string;
    bloodType: string;
  };
  vitals: { type: string; value: string; unit: string }[];
  panels: { name: string; tests: { testName: string; loinc: string; result: string; unit: string; refRange: string; interpretation: string }[] }[];
}

interface FieldError {
  loinc: string;
  fieldName: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

interface UiSpecPanel {
  panel_id: string;
  panel_name: string;
  description: string;
  items: {
    test_name?: string;
    vital_type?: string;
    loinc: string;
    unit: string;
    ui_control: string;
    tooltip: string;
    reference_range?: { min: number; max: number };
    interpretations?: string[];
    interpretation_rules: { status: string; min: number; max: number; note?: string }[];
  }[];
}

interface UiControlSpec {
  panels: UiSpecPanel[];
}

interface ExtensionMessage {
  type: 'update' | 'init';
  state: BloodTestState;
  errors: FieldError[];
  uiSpec: UiControlSpec;
}

console.log('[Webview] App.tsx module loaded');

/**
 * Main Blood Test Editor application.
 */
const App: React.FC = () => {
  const [state, setState] = useState<BloodTestState | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [uiSpec, setUiSpec] = useState<UiControlSpec | null>(null);
  const [activeTabIndex, setActiveTabIndex] = useState(0);
  const [debugInfo, setDebugInfo] = useState<string>('Waiting for data from extension...');

  console.log('[Webview] App render. state:', !!state, 'uiSpec:', !!uiSpec);

  useEffect(() => {
    console.log('[Webview] useEffect: Setting up message listener');

    const handleMessage = (event: MessageEvent) => {
      const msg = event.data;
      console.log('[Webview] Received message, type:', msg?.type);
      console.log('[Webview] Message has state:', !!msg?.state, 'uiSpec:', !!msg?.uiSpec);
      
      if (msg && (msg.type === 'init' || msg.type === 'update')) {
        console.log('[Webview] Setting state. Vitals:', msg.state?.vitals?.length, 'Panels:', msg.state?.panels?.length);
        console.log('[Webview] UI spec panels:', msg.uiSpec?.panels?.length);
        setState(msg.state);
        setErrors(msg.errors || []);
        if (msg.uiSpec) {
          setUiSpec(msg.uiSpec);
        }
        setDebugInfo(`Data received! State: ${JSON.stringify(msg.state?.reportId)}, Panels: ${msg.uiSpec?.panels?.length || 'none'}`);
      } else {
        console.log('[Webview] Unknown message:', JSON.stringify(msg).substring(0, 200));
      }
    };

    // Set up the listener FIRST
    window.addEventListener('message', handleMessage);
    console.log('[Webview] Message listener registered');

    // THEN signal readiness
    try {
      const vscode = getVsCodeApi();
      console.log('[Webview] Got VS Code API, sending ready...');
      vscode.postMessage({ type: 'ready' });
      console.log('[Webview] Ready message sent');
    } catch (err) {
      console.error('[Webview] Error sending ready message:', err);
      setDebugInfo(`Error: ${err}`);
    }

    return () => {
      console.log('[Webview] Cleaning up message listener');
      window.removeEventListener('message', handleMessage);
    };
  }, []);

  if (!state || !uiSpec) {
    return (
      <div className="loading">
        <div>Loading Blood Test Editor...</div>
        <div style={{ fontSize: '11px', marginTop: '8px', color: '#888' }}>{debugInfo}</div>
        <div style={{ fontSize: '10px', marginTop: '16px', color: '#666' }}>
          If this persists, check:<br/>
          1. Debug Console (main VS Code) for extension logs<br/>
          2. Developer Tools (Ctrl+Shift+I in this window) → Console for webview logs
        </div>
      </div>
    );
  }

  const panels = uiSpec.panels;
  const activePanel = panels[activeTabIndex];

  return (
    <div>
      {/* Header */}
      <div className="editor-header">
        <span className="report-id">{state.reportId || 'New Report'}</span>
        <span className="patient-name">{state.patient.fullName || '—'}</span>
        <span className="meta-item">DOB: {state.patient.dob || '—'}</span>
        <span className="meta-item">Gender: {state.patient.gender || '—'}</span>
        <span className="meta-item">Blood Type: {state.patient.bloodType || '—'}</span>
        <span className="meta-item">Lab: {state.laboratoryName || '—'}</span>
      </div>

      {/* Tab Bar */}
      <div className="tab-bar" role="tablist">
        {panels.map((panel, idx) => (
          <button
            key={panel.panel_id}
            role="tab"
            className={idx === activeTabIndex ? 'active' : ''}
            onClick={() => setActiveTabIndex(idx)}
            aria-selected={idx === activeTabIndex}
          >
            {panel.panel_name}
          </button>
        ))}
      </div>

      {/* Active Panel Content */}
      {activePanel && (
        <PanelTab
          panel={activePanel}
          state={state}
          errors={errors}
        />
      )}
    </div>
  );
};

export default App;
