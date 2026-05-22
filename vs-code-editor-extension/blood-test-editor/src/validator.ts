import * as vscode from 'vscode';
import type { BloodTestState, UiControlSpec, FieldError, InterpretationRule } from './types';

/**
 * Compute the interpretation status for a numeric value given a set of rules.
 */
export function computeInterpretation(
  value: number,
  rules: InterpretationRule[]
): string {
  for (const rule of rules) {
    if (value >= rule.min && value <= rule.max) {
      return rule.status;
    }
  }
  return 'Out of Range';
}

/**
 * Validate the entire BloodTestState against the UI control spec.
 * Returns an array of FieldError objects.
 */
export function validateState(
  state: BloodTestState,
  uiSpec: UiControlSpec
): FieldError[] {
  const errors: FieldError[] = [];

  for (const panel of uiSpec.panels) {
    for (const item of panel.items) {
      const name = item.test_name || item.vital_type || 'Unknown';
      const rules = item.interpretation_rules;
      if (!rules || rules.length === 0) { continue; }

      // Find the current value
      let rawValue: string | undefined;

      if (item.vital_type) {
        // Look in vitals
        const vital = state.vitals.find(v => v.type === item.vital_type);
        rawValue = vital?.value;
      } else if (item.test_name) {
        // Look in lab panels
        for (const p of state.panels) {
          const test = p.tests.find(t => t.loinc === item.loinc);
          if (test) {
            rawValue = test.result;
            break;
          }
        }
      }

      // Skip validation if no value present
      if (rawValue === undefined || rawValue === '') { continue; }

      const numValue = parseFloat(rawValue);
      if (isNaN(numValue)) {
        errors.push({
          loinc: item.loinc,
          fieldName: name,
          message: `${name}: value "${rawValue}" is not a valid number.`,
          severity: 'error',
        });
        continue;
      }

      // Check if value is within the overall valid range
      const globalMin = Math.min(...rules.map(r => r.min));
      const globalMax = Math.max(...rules.map(r => r.max));

      if (numValue < globalMin || numValue > globalMax) {
        errors.push({
          loinc: item.loinc,
          fieldName: name,
          message: `${name}: value ${numValue} is outside the valid range (${globalMin} – ${globalMax}).`,
          severity: 'error',
        });
        continue;
      }

      // Check for critical interpretations
      const interpretation = computeInterpretation(numValue, rules);
      if (interpretation.toLowerCase().includes('critical')) {
        errors.push({
          loinc: item.loinc,
          fieldName: name,
          message: `${name}: CRITICAL value ${numValue} — ${interpretation}.`,
          severity: 'warning',
        });
      }
    }
  }

  return errors;
}

/**
 * Convert FieldErrors into VS Code Diagnostics for the Problems tab.
 * Maps errors to the line in the XML where the value appears.
 */
export function buildDiagnostics(
  errors: FieldError[],
  xmlText: string
): vscode.Diagnostic[] {
  const diagnostics: vscode.Diagnostic[] = [];
  const lines = xmlText.split(/\r?\n/);

  for (const err of errors) {
    // Try to find the line containing this LOINC code or the result value
    let lineIdx = -1;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes(`<LOINC>${err.loinc}</LOINC>`)) {
        // Find the <Result> line near this LOINC
        for (let j = i; j < Math.min(i + 10, lines.length); j++) {
          if (lines[j].includes('<Result>') || lines[j].includes('<Value>')) {
            lineIdx = j;
            break;
          }
        }
        if (lineIdx === -1) { lineIdx = i; }
        break;
      }
      // For vitals, look by type attribute
      if (lines[i].includes(`type="${err.fieldName}"`) ||
          lines[i].includes(`type="${err.loinc}"`)) {
        for (let j = i; j < Math.min(i + 5, lines.length); j++) {
          if (lines[j].includes('<Value>')) {
            lineIdx = j;
            break;
          }
        }
        if (lineIdx === -1) { lineIdx = i; }
        break;
      }
    }

    if (lineIdx === -1) { lineIdx = 0; } // fallback to first line

    const severity = err.severity === 'error'
      ? vscode.DiagnosticSeverity.Error
      : err.severity === 'warning'
        ? vscode.DiagnosticSeverity.Warning
        : vscode.DiagnosticSeverity.Information;

    const range = new vscode.Range(lineIdx, 0, lineIdx, lines[lineIdx]?.length || 0);
    const diagnostic = new vscode.Diagnostic(range, err.message, severity);
    diagnostic.source = 'Blood Test Editor';
    diagnostics.push(diagnostic);
  }

  return diagnostics;
}
