import React, { useState } from 'react';
import PacketInput from './components/PacketInput';
import CodedPacket from './components/CodedPacket';
import Controls from './components/Controls';
import { useWebSocket } from './hooks/useWebSocket';
import { useRLCEncoder } from './hooks/useRLCEncoder';

function App() {
  const [packets, setPackets] = useState([]);
  const { sentPackets, generateCoded } = useRLCEncoder(packets, 256);
  const { send } = useWebSocket((msg) => console.log('ACK received', msg));

  const handleUpload = (data) => setPackets(data);
  const sendNext = () => {
    const coded = generateCoded();
    send('send_packet', coded);
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">RLC Sender</h1>
      <PacketInput onUpload={handleUpload} />
      <Controls onSend={sendNext} disabled={!packets.length} />
      <div className="mt-4 space-y-2">
        {sentPackets.map((p, i) => <CodedPacket key={i} packet={p} />)}
      </div>
    </div>
  );
}

export default App;
