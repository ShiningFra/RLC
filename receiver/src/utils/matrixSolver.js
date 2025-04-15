import { add, mul } from './gfArithmetic';

export function gaussJordanSolve(A, B, fieldSize) {
  const n = A.length, k = A[0].length;
  const M = A.map(row => row.slice());
  const D = B.map(row => row.slice());

  let rank = 0;
  for (let col = 0; col < k && rank < n; col++) {
    let pivot = rank;
    while (pivot < n && M[pivot][col] === 0) pivot++;
    if (pivot === n) continue;
    [M[rank], M[pivot]] = [M[pivot], M[rank]];
    [D[rank], D[pivot]] = [D[pivot], D[rank]];
    const inv = invElt(M[rank][col]);
    for (let c = col; c < k; c++) M[rank][c] = mul(M[rank][c], inv);
    for (let j = 0; j < D[rank].length; j++) D[rank][j] = mul(D[rank][j], inv);
    for (let i = 0; i < n; i++) {
      if (i !== rank && M[i][col]) {
        const factor = M[i][col];
        for (let c = col; c < k; c++) M[i][c] = add(M[i][c], mul(factor, M[rank][c]));
        for (let j = 0; j < D[i].length; j++) D[i][j] = add(D[i][j], mul(factor, D[rank][j]));
      }
    }
    rank++;
  }
  if (rank < k) return null;
  return D;
}

function invElt(a) {
  const { LOG, EXP } = require('./gfArithmetic');
  return EXP[255 - LOG[a]];
}
