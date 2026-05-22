import { XMLParser, XMLBuilder } from 'fast-xml-parser';
import type { BloodTestState, PatientProfile, VitalEntry, PanelData, TestResult } from './types';

const parserOptions = {
  ignoreAttributes: false,
  attributeNamePrefix: '@_',
  allowBooleanAttributes: true,
  parseTagValue: false, // keep values as strings
  trimValues: true,
};

const builderOptions = {
  ignoreAttributes: false,
  attributeNamePrefix: '@_',
  format: true,
  indentBy: '    ',
  suppressEmptyNode: false,
};

/**
 * Parse a .bmx XML string into a structured BloodTestState object.
 */
export function parseBloodTestXml(xmlText: string): BloodTestState {
  const parser = new XMLParser(parserOptions);
  const doc = parser.parse(xmlText);
  const root = doc.BloodTestReport || {};

  // Parse patient profile
  const pp = root.PatientProfile || {};
  const patient: PatientProfile = {
    patientId: pp.PatientID || '',
    fullName: pp.FullName || '',
    dob: pp.DOB || '',
    gender: pp.Gender || '',
    bloodType: pp.BloodType || '',
  };

  // Parse vital signs
  const vitals: VitalEntry[] = [];
  const vitalSigns = root.VitalSigns;
  if (vitalSigns && vitalSigns.Vital) {
    const vitalArr = Array.isArray(vitalSigns.Vital) ? vitalSigns.Vital : [vitalSigns.Vital];
    for (const v of vitalArr) {
      vitals.push({
        type: v['@_type'] || '',
        value: v.Value || '',
        unit: v.Unit || '',
      });
    }
  }

  // Parse lab result panels
  const panels: PanelData[] = [];
  const labResults = root.LabResults;
  if (labResults && labResults.Panel) {
    const panelArr = Array.isArray(labResults.Panel) ? labResults.Panel : [labResults.Panel];
    for (const p of panelArr) {
      const tests: TestResult[] = [];
      if (p.Test) {
        const testArr = Array.isArray(p.Test) ? p.Test : [p.Test];
        for (const t of testArr) {
          tests.push({
            testName: t.TestName || '',
            loinc: t.LOINC || '',
            result: t.Result || '',
            unit: t.Unit || '',
            refRange: t.RefRange || '',
            interpretation: t.Interpretation || '',
          });
        }
      }
      panels.push({
        name: p['@_name'] || '',
        tests,
      });
    }
  }

  return {
    reportId: root.ReportID || '',
    generatedDate: root.GeneratedDate || '',
    laboratoryName: root.LaboratoryName || '',
    patient,
    vitals,
    panels,
  };
}

/**
 * Find the line number (0-indexed) containing a specific text pattern in the XML.
 */
export function findLineIndex(xmlText: string, pattern: string): number {
  const lines = xmlText.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(pattern)) {
      return i;
    }
  }
  return -1;
}

/**
 * Build a text edit to update a Vital's <Value> in the XML.
 * Returns { lineIndex, oldLine, newLine } or null if not found.
 */
export function buildVitalEdit(
  xmlText: string,
  vitalType: string,
  newValue: string
): { lineIndex: number; oldLine: string; newLine: string } | null {
  const lines = xmlText.split(/\r?\n/);

  // Find the <Vital type="..."> line
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(`type="${vitalType}"`)) {
      // The <Value> should be on the next line (or within a few lines)
      for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
        const match = lines[j].match(/^(\s*<Value>)([^<]*)(<\/Value>\s*)$/);
        if (match) {
          return {
            lineIndex: j,
            oldLine: lines[j],
            newLine: `${match[1]}${newValue}${match[3]}`,
          };
        }
      }
    }
  }
  return null;
}

/**
 * Build a text edit to update a Test field (Result, Interpretation, etc.) in the XML.
 * We locate the test by finding the panel name and the test index within it.
 */
export function buildTestEdit(
  xmlText: string,
  panelName: string,
  testIndex: number,
  field: string,
  newValue: string
): { lineIndex: number; oldLine: string; newLine: string } | null {
  const lines = xmlText.split(/\r?\n/);
  
  // Find the panel
  let panelLine = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(`name="${panelName}"`) || lines[i].includes(`name="${panelName.replace(/&/g, '&amp;')}"`)) {
      panelLine = i;
      break;
    }
  }
  if (panelLine === -1) { return null; }

  // Find the Nth <Test> within this panel
  let testCount = -1;
  let testStartLine = -1;
  for (let i = panelLine + 1; i < lines.length; i++) {
    if (lines[i].includes('</Panel>')) { break; }
    if (lines[i].trim() === '<Test>') {
      testCount++;
      if (testCount === testIndex) {
        testStartLine = i;
        break;
      }
    }
  }
  if (testStartLine === -1) { return null; }

  // Find the <Field> line within this test
  const tag = field; // e.g. 'Result', 'Interpretation'
  for (let i = testStartLine + 1; i < Math.min(testStartLine + 15, lines.length); i++) {
    const regex = new RegExp(`^(\\s*<${tag}>)([^<]*)(<\\/${tag}>\\s*)$`);
    const match = lines[i].match(regex);
    if (match) {
      return {
        lineIndex: i,
        oldLine: lines[i],
        newLine: `${match[1]}${newValue}${match[3]}`,
      };
    }
  }
  return null;
}

/**
 * Build a text edit to update a top-level metadata field (ReportID, LaboratoryName, etc.).
 */
export function buildMetaEdit(
  xmlText: string,
  field: string,
  newValue: string
): { lineIndex: number; oldLine: string; newLine: string } | null {
  const lines = xmlText.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const regex = new RegExp(`^(\\s*<${field}>)([^<]*)(<\\/${field}>\\s*)$`);
    const match = lines[i].match(regex);
    if (match) {
      return {
        lineIndex: i,
        oldLine: lines[i],
        newLine: `${match[1]}${newValue}${match[3]}`,
      };
    }
  }
  return null;
}

/**
 * Serialize a BloodTestState back to XML. Used as fallback for full-document rebuild.
 */
export function serializeToXml(state: BloodTestState): string {
  const doc = {
    '?xml': { '@_version': '1.0', '@_encoding': 'UTF-8' },
    BloodTestReport: {
      ReportID: state.reportId,
      GeneratedDate: state.generatedDate,
      LaboratoryName: state.laboratoryName,
      PatientProfile: {
        PatientID: state.patient.patientId,
        FullName: state.patient.fullName,
        DOB: state.patient.dob,
        Gender: state.patient.gender,
        BloodType: state.patient.bloodType,
      },
      VitalSigns: {
        Vital: state.vitals.map(v => ({
          '@_type': v.type,
          Value: v.value,
          Unit: v.unit,
        })),
      },
      LabResults: {
        Panel: state.panels.map(p => ({
          '@_name': p.name,
          Test: p.tests.map(t => ({
            TestName: t.testName,
            LOINC: t.loinc,
            Result: t.result,
            Unit: t.unit,
            RefRange: t.refRange,
            Interpretation: t.interpretation,
          })),
        })),
      },
    },
  };
  const builder = new XMLBuilder(builderOptions);
  return builder.build(doc);
}
