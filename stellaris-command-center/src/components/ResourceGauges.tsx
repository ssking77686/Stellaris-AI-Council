import { useState, useEffect } from 'react';
import { api } from '@/api/client';
import type { EmpireState } from '@/api/types';

interface GaugeDef {
  key: string; label: string; icon: string; max: number; color: string;
}

const gauges: GaugeDef[] = [
  { key: 'energy_credits', label: '能量币', icon: '⚡', max: 4000, color: '#facc15' },
  { key: 'minerals', label: '矿物', icon: '⛏', max: 2000, color: '#f97316' },
  { key: 'food', label: '食物', icon: '🌾', max: 800, color: '#22c55e' },
  { key: 'consumer_goods', label: '消费品', icon: '📦', max: 600, color: '#a78bfa' },
  { key: 'alloys', label: '合金', icon: '⚙', max: 300, color: '#94a3b8' },
  { key: 'influence', label: '影响力', icon: '★', max: 500, color: '#fbbf24' },
  { key: 'unity', label: '凝聚力', icon: '✦', max: 2000, color: '#38bdf8' },
];

function RingGauge({ value, max, color, icon, label }: { value: number; max: number; color: string; icon: string; label: string }) {
  const pct = Math.min(value / max, 1);
  const angle = pct * 2 * Math.PI;
  const r = 22; const cx = 28; const cy = 28; const stroke = 4;
  const x2 = cx + r * Math.sin(angle);
  const y2 = cy - r * Math.cos(angle);
  const large = pct > 0.5 ? 1 : 0;

  return (
    <div className="flex flex-col items-center gap-1" title={`${label}: ${value.toLocaleString()} / ${max}`}>
      <svg width="56" height="56" className="drop-shadow-lg">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="hsl(222 28% 18%)" strokeWidth={stroke} />
        <path
          d={`M ${cx} ${cy - r} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`}
          fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 4px ${color}40)` }}
        />
        <text x={cx} y={cy + 1} textAnchor="middle" dominantBaseline="middle"
          fill="#e2e8f0" fontSize="9" fontFamily="monospace" fontWeight="bold">{icon}</text>
      </svg>
      <span className="text-[9px] text-[#4b5563] font-mono">{label}</span>
      <span className="text-[11px] font-mono font-bold text-white">{value.toLocaleString()}</span>
    </div>
  );
}

export default function ResourceGauges() {
  const [state, setState] = useState<EmpireState | null>(null);

  useEffect(() => { api.getEmpireState().then(setState).catch(() => {}); }, []);

  if (!state) return null;

  return (
    <div className="flex justify-center gap-4 py-3 px-4 bg-[#111827] border border-[hsl(222,28%,18%)] rounded-lg">
      {gauges.map((g) => (
        <RingGauge key={g.key} value={Number((state as any)[g.key]) || 0} max={g.max} color={g.color} icon={g.icon} label={g.label} />
      ))}
    </div>
  );
}
