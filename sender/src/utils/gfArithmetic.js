// GF(2^8) arithmetic with log/exp tables
const EXP = new Uint8Array(512);
const LOG = new Uint8Array(256);
(function initTables() {
  let x = 1;
  for (let i = 0; i < 255; i++) {
    EXP[i] = x;
    LOG[x] = i;
    x ^= x << 1 ^ ((x & 0x80) ? 0x1d : 0);
    x &= 0xff;
  }
  for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
})();
export function add(a, b) { return a ^ b; }
export function mul(a, b) {
  return a && b ? EXP[LOG[a] + LOG[b]] : 0;
}
export function randomVector(k, fieldSize) {
  return Array.from({ length: k }, () => Math.floor(Math.random() * (fieldSize - 1)) + 1);
}
export function encodePacket(packets, g, fieldSize) {
  const len = packets[0].length;
  const result = new Uint8Array(len);
  for (let i = 0; i < g.length; i++) {
    for (let j = 0; j < len; j++) {
      result[j] = add(result[j], mul(g[i], packets[i][j]));
    }
  }
  return Array.from(result);
}
