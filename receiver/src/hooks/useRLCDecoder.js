import { useState, useCallback } from 'react';
import { gaussJordanSolve } from '../utils/matrixSolver';

export function useRLCDecoder(k, fieldSize) {
  const [coeffMatrix, setCoeffMatrix] = useState([]);
  const [dataMatrix, setDataMatrix] = useState([]);
  const [decoded, setDecoded] = useState(null);

  const receiveCoded = useCallback(({ coeffs, data }) => {
    setCoeffMatrix(prev => [...prev, coeffs]);
    setDataMatrix(prev => [...prev, data]);
  }, []);

  const tryDecode = useCallback(() => {
    if (coeffMatrix.length < k) return false;
    const sol = gaussJordanSolve(coeffMatrix, dataMatrix, fieldSize);
    if (sol) setDecoded(sol);
    return !!sol;
  }, [coeffMatrix, dataMatrix]);

  return { coeffMatrix, dataMatrix, decoded, receiveCoded, tryDecode };
}
