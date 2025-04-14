import React, { useEffect } from 'react';
import CoeffMatrix from './components/CoeffMatrix';
import CodedPacket from './components/CodedPacket';
import { useWebSocket } from './hooks/useWebSocket';
import { useRLCDecoder } from './hooks/useRLCDecoder';

function App() {
  const { coeffMatrix, dataMatrix, decoded, receiveCoded, tryDecode } = useRLCDecoder(4, 256);
  const { send } = useWebSocket((pkt) => {
    receiveCoded(pkt);
  });

  useEffect(() => {
    if (tryDecode()) send('ack');
  }, [coeffMatrix, dataMatrix]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">RLC Receiver</h1>
      <CoeffMatrix matrix={coeffMatrix} />
      <div className="mt-4 space-y-2">
        {dataMatrix.map((d, i) => <CodedPacket key={i} packet={{ coeffs: coeffMatrix[i], data: d }} />)}
      </div>
      {decoded && <div className="mt-4 p-2 border rounded">Decoded packets count: {decoded.length}</div>}
    </div>
  );
}

export default App;
