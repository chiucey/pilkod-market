// stats.mjs — 纯 JS 统计计算（无第三方依赖）
export function mean(a) { return a.reduce((s, x) => s + x, 0) / a.length; }
export function median(a) {
  const s = [...a].sort((x, y) => x - y);
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}
export function corr(a, b) {
  const n = Math.min(a.length, b.length);
  const ma = mean(a.slice(0, n)), mb = mean(b.slice(0, n));
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) {
    const dx = a[i] - ma, dy = b[i] - mb;
    sxy += dx * dy; sxx += dx * dx; syy += dy * dy;
  }
  return sxx && syy ? sxy / Math.sqrt(sxx * syy) : 0;
}
/** 一元线性回归 y = slope*x + intercept（按序号拟合，与 numpy.polyfit 一致） */
export function linreg(y) {
  const n = y.length;
  const x = Array.from({ length: n }, (_, i) => i);
  const mx = mean(x), my = mean(y);
  let sxy = 0, sxx = 0;
  for (let i = 0; i < n; i++) { sxy += (x[i] - mx) * (y[i] - my); sxx += (x[i] - mx) ** 2; }
  const slope = sxx ? sxy / sxx : 0;
  const intercept = my - slope * mx;
  return { slope, intercept, at: (i) => slope * i + intercept };
}
export const round = (v, n = 4) => Math.round(v * 10 ** n) / 10 ** n;
