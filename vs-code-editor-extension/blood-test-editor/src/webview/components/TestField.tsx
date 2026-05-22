import React, { useCallback, useRef } from 'react';
import { Tooltip } from './Tooltip';

// Types inlined to avoid cross-compilation issues with the extension types
interface InterpretationRule {
  status: string;
  min: number;
  max: number;
  note?: string;
}

interface FieldError {
  loinc: string;
  fieldName: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

interface TestFieldProps {
  label: string;
  loinc: string;
  unit: string;
  tooltip: string;
  value: string;
  interpretationRules: InterpretationRule[];
  error?: FieldError;
  onValueChange: (newValue: string) => void;
}

/**
 * Compute interpretation status from a numeric value.
 */
function getInterpretation(value: string, rules: InterpretationRule[]): { status: string; cssClass: string } {
  const num = parseFloat(value);
  if (isNaN(num) || !rules || rules.length === 0) {
    return { status: '', cssClass: 'status-unknown' };
  }

  for (const rule of rules) {
    if (num >= rule.min && num <= rule.max) {
      const status = rule.status;
      let cssClass = 'status-unknown';

      const lower = status.toLowerCase();
      if (lower.includes('critical')) {
        cssClass = 'status-critical';
      } else if (lower.includes('high') || lower.includes('risk')) {
        cssClass = 'status-high';
      } else if (lower.includes('low') || lower.includes('deficien') || lower.includes('insufficient')) {
        cssClass = 'status-low';
      } else if (lower.includes('normal') || lower.includes('sufficient') || lower.includes('recorded')) {
        cssClass = 'status-normal';
      } else if (lower.includes('optimal') || lower.includes('therapeutic')) {
        cssClass = 'status-optimal';
      }

      return { status, cssClass };
    }
  }

  return { status: 'Out of Range', cssClass: 'status-critical' };
}

/**
 * A single test/vital field card: label + input + interpretation badge.
 */
export const TestField: React.FC<TestFieldProps> = ({
  label,
  loinc,
  unit,
  tooltip,
  value,
  interpretationRules,
  error,
  onValueChange,
}) => {
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;

    // Debounce to avoid flooding the extension with edits
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    debounceRef.current = setTimeout(() => {
      onValueChange(newValue);
    }, 300);
  }, [onValueChange]);

  const { status, cssClass } = getInterpretation(value, interpretationRules);
  const hasError = !!error;

  return (
    <div className={`test-field ${hasError ? 'has-error' : ''}`} data-loinc={loinc}>
      <div className="field-header">
        <span className="field-label">{label}</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span className="field-unit">{unit}</span>
          <Tooltip text={tooltip} />
        </div>
      </div>

      <div className="field-input-row">
        <input
          type="text"
          defaultValue={value}
          onChange={handleChange}
          className={hasError ? 'error' : ''}
          placeholder="Enter value..."
          id={`field-${loinc}`}
        />
        {status && (
          <span className={`interpretation-badge ${cssClass}`}>
            {status}
          </span>
        )}
      </div>

      {hasError && (
        <div className="field-error-msg">{error.message}</div>
      )}
    </div>
  );
};
