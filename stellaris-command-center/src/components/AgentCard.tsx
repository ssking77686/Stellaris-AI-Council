import type { AgentData } from '@/data/empire';

const progressColors: Record<string, string> = {
  gold: 'from-[#8b6914] to-[#f0d060]',
  blue: 'from-[#1e4a80] to-[#60a5fa]',
  green: 'from-[#166534] to-[#22c55e]',
  red: 'from-[#7f1d1d] to-[#ef4444]',
  purple: 'from-[#4c1d95] to-[#8b5cf6]',
};

const statusColor: Record<string, string> = {
  good: 'bg-[#22c55e] shadow-[0_0_8px_rgba(34,197,94,0.6)]',
  warn: 'bg-[#f59e0b] shadow-[0_0_8px_rgba(245,158,11,0.6)]',
  bad: 'bg-[#ef4444] shadow-[0_0_8px_rgba(239,68,68,0.6)]',
};

const valueColor: Record<string, string> = {
  good: 'text-[#22c55e]',
  warn: 'text-[#f59e0b]',
  bad: 'text-[#ef4444]',
};

export default function AgentCard({ agent }: { agent: AgentData }) {
  return (
    <div className="bg-[#111827] border border-[hsl(222,28%,18%)] rounded-lg p-4 transition-all duration-300 relative overflow-hidden group hover:border-[hsl(222,28%,32%)] hover:bg-[#151d30] hover:-translate-y-px"
      style={{ boxShadow: 'none' }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 0 30px rgba(59,130,246,0.06), 0 4px 20px rgba(0,0,0,0.3)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      {/* Top shimmer line */}
      <div className="absolute top-0 left-0 right-0 h-px"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent)' }} />

      {/* Header */}
      <div className="flex items-center gap-2.5 mb-2.5 pb-2.5 border-b border-[hsl(222,28%,18%)]/50">
        <div className="w-[38px] h-[38px] rounded-lg flex items-center justify-center text-[19px] border border-white/[0.08]"
          style={{ background: agent.iconBg, borderColor: agent.iconBorder }}>
          {agent.icon}
        </div>
        <div className="flex-1">
          <div className="font-orbitron text-[11px] font-semibold text-[#e2e8f0] tracking-[1px]">{agent.role}</div>
          <div className="text-[10px] text-[#4b5563] mt-px">{agent.name}</div>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={`w-[7px] h-[7px] rounded-full inline-block ${statusColor[agent.statusType]}`} />
          <span className="text-[10px] text-[#94a3b8]">{agent.status}</span>
        </div>
      </div>

      {/* Metrics */}
      <div className="flex flex-col gap-1.5">
        {agent.metrics.map((m) => (
          <div key={m.label} className="flex items-center justify-between text-xs">
            <span className="text-[#94a3b8]">{m.label}</span>
            <span className={`font-mono font-semibold text-[13px] ${m.valueClass ? valueColor[m.valueClass] : ''}`}>
              {m.value}
            </span>
          </div>
        ))}
      </div>

      {/* Progress bar */}
      <div className="h-[3px] bg-[hsl(222,28%,18%)]/50 rounded-lg mt-2 overflow-hidden">
        <div
          className={`h-full rounded-lg bg-gradient-to-r ${progressColors[agent.progress.color]} relative`}
          style={{ width: `${agent.progress.width}%` }}
        >
          <div className="absolute right-0 top-0 bottom-0 w-5 bg-gradient-to-l from-white/30 to-transparent" />
        </div>
      </div>

      {/* Analysis box */}
      <div className="mt-2.5 pt-2.5 border-t border-[hsl(222,28%,18%)]/30">
        <div className="text-[8px] text-[#8b6914] font-orbitron tracking-[2px] uppercase mb-1 not-italic">📋 近期分析</div>
        <div className="pl-2.5 border-l-2 border-[#8b6914] rounded-r-sm">
          <p className="text-[11px] text-[#94a3b8] leading-relaxed italic">{agent.analysis}</p>
        </div>
      </div>
    </div>
  );
}
