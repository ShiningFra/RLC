import React from 'react';

export default function Controls({ onSend, disabled }) {
  return (
    <button onClick={onSend} disabled={disabled} className="mt-2 px-4 py-2 rounded shadow">
      Send Coded Packet
    </button>
  );
}
