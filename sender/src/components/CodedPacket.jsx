import React from 'react';

export default function CodedPacket({ packet }) {
  return (
    <div className="border p-2 rounded">
      <div>Coefficients: [{packet.coeffs.join(', ')}]</div>
      <div>Data (hex): {packet.data.slice(0,8).map(b=>b.toString(16).padStart(2,'0')).join(' ')}...</div>
    </div>
  );
}
