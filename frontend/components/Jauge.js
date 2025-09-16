export default function Jauge({ value = 0 }) {
  // value: 0..1
  const pct = Math.max(0, Math.min(1, value));
  const size = 160, stroke = 14, r = (size - stroke) / 2, cx = size / 2, cy = size / 2;
  const circ = 2 * Math.PI * r, arc = circ * pct;

  return (
    <div className="inline-block">
      <svg width={size} height={size} className="rotate-[-90deg]">
        <circle cx={cx} cy={cy} r={r} stroke="#e5e7eb" strokeWidth={stroke} fill="none" />
        <circle
          cx={cx} cy={cy} r={r}
          stroke="currentColor" strokeWidth={stroke} fill="none"
          strokeDasharray={`${arc} ${circ - arc}`} strokeLinecap="round"
          className={pct >= 0.5 ? "text-green-500" : "text-amber-500"}
        />
      </svg>
      <div className="text-center -mt-10 font-semibold text-xl">{Math.round(pct*100)}%</div>
    </div>
  );
}
