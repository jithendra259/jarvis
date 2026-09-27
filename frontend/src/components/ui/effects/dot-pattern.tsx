import React from 'react';
import { cn } from '@/lib/utils';

interface DotPatternProps {
  id?: string;
  width?: string | number;
  height?: string | number;
  x?: string | number;
  y?: string | number;
  cx?: string | number;
  cy?: string | number;
  cr?: string | number;
  className?: string;
  [key: string]: string | number | undefined;
}
export function DotPattern({
  id: customId,
  width = 24,
  height = 24,
  x = 0,
  y = 0,
  cx = 1,
  cy = 0.5,
  cr = 0.5,
  className,
  ...props
}: DotPatternProps) {
  const patternId = customId || 'portfolio-dot-pattern';

  return (
    <svg
      aria-hidden="true"
      className={cn(
        'pointer-events-none absolute inset-0 h-full w-full fill-slate-500/50 md:fill-slate-500/70',
        className
      )}
      {...props}
    >
      <defs>
        <pattern
          id={patternId}
          width={width}
          height={height}
          patternUnits="userSpaceOnUse"
          patternContentUnits="userSpaceOnUse"
          x={x}
          y={y}
        >
          <circle id="pattern-circle" cx={cx} cy={cy} r={cr} />
        </pattern>
      </defs>
      <rect width="100%" height="100%" strokeWidth={0} fill={`url(#${patternId})`} />
    </svg>
  );
}

export default DotPattern;
