import { useState, useCallback } from 'react';
import { randomVector, encodePacket } from '../utils/gfArithmetic';

export function useRLCEncoder(packets, fieldSize) {
  const [sentPackets, setSentPackets] = useState([]);

  const generateCoded = useCallback(() => {
    const k = packets.length;
    const g = randomVector(k, fieldSize);
    const C = encodePacket(packets, g, fieldSize);
    const coded = { coeffs: g, data: C };
    setSentPackets(prev => [...prev, coded]);
    return coded;
  }, [packets, fieldSize]);

  return { sentPackets, generateCoded };
}
