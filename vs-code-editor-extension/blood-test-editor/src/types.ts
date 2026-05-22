// Shared types between extension host and webview

/** A single vital sign entry parsed from XML */
export interface VitalEntry {
  type: string;
  value: string;
  unit: string;
}

/** Patient profile parsed from XML */
export interface PatientProfile {
  patientId: string;
  fullName: string;
  dob: string;
  gender: string;
  bloodType: string;
}

/** A single lab test result parsed from XML */
export interface TestResult {
  testName: string;
  loinc: string;
  result: string;
  unit: string;
  refRange: string;
  interpretation: string;
}

/** A lab panel (group of tests) parsed from XML */
export interface PanelData {
  name: string;
  tests: TestResult[];
}

/** Complete parsed state of a .bmx file */
export interface BloodTestState {
  reportId: string;
  generatedDate: string;
  laboratoryName: string;
  patient: PatientProfile;
  vitals: VitalEntry[];
  panels: PanelData[];
}

/** Interpretation rule from ui_control_spec.json */
export interface InterpretationRule {
  status: string;
  min: number;
  max: number;
  note?: string;
}

/** A single item (test or vital) from ui_control_spec.json */
export interface UiSpecItem {
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

/** A panel from ui_control_spec.json */
export interface UiSpecPanel {
  panel_id: string;
  panel_name: string;
  description: string;
  items: UiSpecItem[];
}

/** The full ui_control_spec.json structure */
export interface UiControlSpec {
  panels: UiSpecPanel[];
}

/** A validation error for a specific field */
export interface FieldError {
  loinc: string;
  fieldName: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

// ---- Message protocol between extension and webview ----

/** Messages sent FROM the webview TO the extension */
export type WebviewMessage =
  | { type: 'ready' }
  | { type: 'edit'; xpath: string; value: string }
  | { type: 'editVital'; vitalType: string; value: string }
  | { type: 'editTest'; panelName: string; testIndex: number; field: string; value: string }
  | { type: 'editMeta'; field: string; value: string };

/** Messages sent FROM the extension TO the webview */
export type ExtensionMessage =
  | { type: 'update'; state: BloodTestState; errors: FieldError[]; uiSpec: UiControlSpec }
  | { type: 'init'; state: BloodTestState; errors: FieldError[]; uiSpec: UiControlSpec };
