import React from 'react';

interface TooltipProps {
  text: string;
}

/**
 * A small "?" icon that reveals a tooltip on hover.
 */
export const Tooltip: React.FC<TooltipProps> = ({ text }) => {
  if (!text) { return null; }

  return (
    <span className="tooltip-icon" aria-label={text}>
      ?
      <span className="tooltip-text">{text}</span>
    </span>
  );
};
