import React from 'react';

export default function PacketInput({ onUpload }) {
  const handleFile = async (e) => {
    const file = e.target.files[0];
    const buf = await file.arrayBuffer();
    const bytes = new Uint8Array(buf);
    const packetSize = 1024;
    const packets = [];
    for (let i = 0; i < bytes.length; i += packetSize) {
      packets.push(bytes.slice(i, i + packetSize));
    }
    onUpload(packets);
  };

  return (
    <div>
      <input type="file" onChange={handleFile} />
    </div>
  );
}
