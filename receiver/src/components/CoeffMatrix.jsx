import React from 'react';

export default function CoeffMatrix({ matrix }) {
  return (
    <div className="border p-2 rounded">
      <div className="font-semibold">Coefficient Matrix:</div>
      {matrix.map((row, i) => (
        <div key={i}>[{row.join(', ')}]</div>
      ))}
    </div>
  );
}
