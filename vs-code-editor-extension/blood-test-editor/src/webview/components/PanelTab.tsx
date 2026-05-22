import React from 'react';
import { TestField } from './TestField';
import { getVsCodeApi } from '../hooks/useVsCodeApi';

// Types mirrored from extension types to avoid cross-compilation issues
interface InterpretationRule {
  status: string;
  min: number;
  max: number;
  note?: string;
}

interface UiSpecItem {
  test_name?: string;
  vital_type?: string;
  loinc: string;
  unit: string;
  ui_control: string;
  tooltip: string;
  reference_range?: { min: number; max: number };
  interpretations?: string[];
  interpretation_rules: InterpretationRule[];
}

interface UiSpecPanel {
  panel_id: string;
  panel_name: string;
  description: string;
  items: UiSpecItem[];
}

interface VitalEntry {
  type: string;
  value: string;
  unit: string;
}

interface TestResult {
  testName: string;
  loinc: string;
  result: string;
  unit: string;
  refRange: string;
  interpretation: string;
}

interface PanelData {
  name: string;
  tests: TestResult[];
}

interface FieldError {
  loinc: string;
  fieldName: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

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
  vitals: VitalEntry[];
  panels: PanelData[];
}

interface PanelTabProps {
  panel: UiSpecPanel;
  state: BloodTestState;
  errors: FieldError[];
}

/**
 * Map a UI spec panel_name to the XML panel name.
 * The mapping is needed because XML uses display names like "Complete Blood Count"
 * while the UI spec uses "Hematology (CBC)".
 */
const panelNameToXmlName: Record<string, string> = {
  'Hematology (CBC)': 'Complete Blood Count',
  'Comprehensive Metabolic Panel (CMP)': 'Comprehensive Metabolic Panel',
  'Lipid Profile': 'Lipid Profile',
  'Thyroid & Endocrine': 'Thyroid & Endocrine',
  'Immunology': 'Immunology',
  'Tumor Markers': 'Tumor Markers',
  'Nutrition & Vitamins': 'Nutrition & Vitamins',
  'Coagulation Panel': 'Coagulation Panel',
};

/**
 * Renders all fields for a single panel tab.
 */
export const PanelTab: React.FC<PanelTabProps> = ({ panel, state, errors }) => {
  const vscode = getVsCodeApi();

  const handleVitalChange = (vitalType: string, newValue: string) => {
    vscode.postMessage({
      type: 'editVital',
      vitalType,
      value: newValue,
    });
  };

  const handleTestChange = (panelName: string, testIndex: number, field: string, newValue: string) => {
    vscode.postMessage({
      type: 'editTest',
      panelName,
      testIndex,
      field,
      value: newValue,
    });
  };

  const isVitalsPanel = panel.panel_id === 'GEN-001';

  return (
    <div className="panel-content">
      <div className="panel-description">{panel.description}</div>

      <div className="field-grid">
        {panel.items.map((item, idx) => {
          const name = item.test_name || item.vital_type || 'Unknown';
          const error = errors.find(e => e.loinc === item.loinc);

          let currentValue = '';

          if (isVitalsPanel && item.vital_type) {
            // Find in vitals array
            const vital = state.vitals.find(v => v.type === item.vital_type);
            currentValue = vital?.value || '';

            return (
              <TestField
                key={item.loinc}
                label={name}
                loinc={item.loinc}
                unit={item.unit}
                tooltip={item.tooltip}
                value={currentValue}
                interpretationRules={item.interpretation_rules}
                error={error}
                onValueChange={(val) => handleVitalChange(item.vital_type!, val)}
              />
            );
          } else {
            // Find in lab panels
            const xmlPanelName = panelNameToXmlName[panel.panel_name] || panel.panel_name;
            const panelData = state.panels.find(p => p.name === xmlPanelName);
            const test = panelData?.tests.find(t => t.loinc === item.loinc);
            const testIndex = panelData?.tests.findIndex(t => t.loinc === item.loinc) ?? -1;
            currentValue = test?.result || '';

            return (
              <TestField
                key={item.loinc}
                label={name}
                loinc={item.loinc}
                unit={item.unit}
                tooltip={item.tooltip}
                value={currentValue}
                interpretationRules={item.interpretation_rules}
                error={error}
                onValueChange={(val) => handleTestChange(xmlPanelName, testIndex, 'Result', val)}
              />
            );
          }
        })}
      </div>
    </div>
  );
};
