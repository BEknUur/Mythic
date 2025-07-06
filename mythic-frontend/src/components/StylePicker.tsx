import React from 'react';

interface Style {
  value: string;
  label: string;
}

export const STYLES: Style[] = [
  { value: 'romantic', label: 'Романтический' },
  { value: 'fantasy', label: 'Фантастика' },
  { value: 'humor', label: 'Юмор' },
  // можно добавить свои стили
];

export function StylePicker({ value, onChange }: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <select
      className="border rounded p-2 w-full"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    >
      {STYLES.map((s) => (
        <option key={s.value} value={s.value}>
          {s.label}
        </option>
      ))}
    </select>
  );
} 