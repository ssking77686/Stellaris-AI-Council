import { useState, useEffect } from 'react';
import { events as fallbackEvents, approvals as fallbackApprovals } from '@/data/empire';

interface ChronicleEntry {
  type: string;
  subtype: string;
  title: string;
  description: string;
  agent_id: string;
  time: string;
  status?: string;
  cost?: string;
  session_id?: string;
}

const typeIcons: Record<string, string> = {
  event: '📡', proposal: '📋', coordination: '🤝', court: '👑',
};
const typeLabels: Record<string, string> = {
  event: '事件', proposal: '提议', coordination: '协商', court: '朝会',
};
const subtypeColors: Record<string, string> = {
  report: 'border-l-[#22c55e]', alert: 'border-l-[#ef4444]', proposal: 'border-l-[#3b82f6]',
  coordination: 'border-l-[#8b5cf6]', random: 'border-l-[#f59e0b]',
  approved: 'border-l-[#22c55e]', rejected: 'border-l-[#ef4444]', pending: 'border-l-[#f59e0b]',
  resolved: 'border-l-[#22c55e]', failed: 'border-l-[#ef4444]',
  closed: 'border-l-[#22c55e]', opening: 'border-l-[#d4af37]',
  reporting: 'border-l-[#3b82f6]', discussing: 'border-l-[#8b5cf6]', closing: 'border-l-[#22c55e]',
};
const agentIcons: Record<string, string> = {
  system: '👑', finance: '💰', military: '⚔', science: '🔬',
  foreign: '🤝', interior: '🏛', construction: '🏗',
};

function formatDate(d: string) {
  try { return new Date(d).toLocaleDateString('zh-CN'); }
  catch { return d?.slice(0, 10) || '未知'; }
}

function TimelineEntry({ entry }: { entry: ChronicleEntry }) {
  const borderColor = subtypeColors[entry.subtype] || 'border-l-[hsl(222,28%,32%)]';
  return (
    <div className={`flex gap-4 p-4 bg-[#111827] border border-[hsl(222,28%,18%)] rounded-lg border-l-2 ${borderColor} hover:border-[hsl(222,28%,32%)] transition-all`}>
      <div className="flex flex-col items-center gap-1 shrink-0">
        <span className="text-xl">{typeIcons[entry.type] || '📌'}</span>
        <span className="text-[8px] text-[#4b5563] font-orbitron tracking-[1px]">{typeLabels[entry.type]}</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-semibold text-[#d4af37]">{entry.title}</span>
          {entry.status && (
            <span className={`text-[8px] px-1.5 py-0.5 rounded-lg border font-orbitron tracking-[1px]
              ${entry.status === 'approved' || entry.status === 'resolved' ? 'text-[#22c55e] border-[#22c55e]/30 bg-[#22c55e]/10' :
                entry.status === 'rejected' || entry.status === 'failed' ? 'text-[#ef4444] border-[#ef4444]/30 bg-[#ef4444]/10' :
                'text-[#f59e0b] border-[#f59e0b]/30 bg-[#f59e0b]/10'}`}>
              {entry.status}
            </span>
          )}
        </div>
        <p className="text-[12px] text-[#94a3b8] leading-relaxed mb-1.5">{entry.description}</p>
        <div className="flex items-center gap-2 text-[10px] text-[#4b5563]">
          {entry.agent_id && entry.agent_id !== 'system' && (
            <span>{agentIcons[entry.agent_id] || '🤖'} {entry.agent_id}</span>
          )}
          <span className="font-mono">{formatDate(entry.time)}</span>
        </div>
      </div>
    </div>
  );
}

export default function Chronicle() {
  const [entries, setEntries] = useState<ChronicleEntry[]>([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  const tagSubtype: Record<string, string> = {
    '提议': 'proposal', '报告': 'report', '预警': 'alert', '协商': 'coordination',
  };

  useEffect(() => {
    fetch('http://localhost:8001/api/chronicle/?limit=60').then(r => r.json())
      .then(setEntries).catch(() => {
        const evEntries: ChronicleEntry[] = fallbackEvents.map((e) => ({
          type: tagSubtype[e.tag] === 'report' || tagSubtype[e.tag] === 'alert' ? 'event' : tagSubtype[e.tag],
          subtype: tagSubtype[e.tag] || 'random',
          title: e.text,
          description: '',
          agent_id: '',
          time: e.time,
        }));
        const apEntries: ChronicleEntry[] = fallbackApprovals.map((a) => ({
          type: 'proposal',
          subtype: 'pending',
          title: a.title,
          description: a.detail,
          agent_id: '',
          time: new Date().toISOString(),
          status: 'pending',
          cost: JSON.stringify(a.costs),
        }));
        setEntries([...evEntries, ...apEntries]);
      }).finally(() => setLoading(false));
  }, []);

  const types = ['all', 'event', 'proposal', 'coordination', 'court'];
  const filtered = filter === 'all' ? entries : entries.filter((e) => e.type === filter);

  // Group by date
  const grouped: Record<string, ChronicleEntry[]> = {};
  for (const e of filtered) {
    const date = formatDate(e.time);
    if (!grouped[date]) grouped[date] = [];
    grouped[date].push(e);
  }

  return (
    <div className="flex flex-col gap-3 h-full">
      <div>
        <h1 className="font-orbitron text-[22px] font-bold text-[#d4af37] tracking-[3px]"
          style={{ textShadow: '0 0 30px rgba(212,175,55,0.2)' }}>帝国编年史</h1>
        <p className="text-xs text-[#4b5563] mt-0.5">{entries.length} 条历史记录</p>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1.5">
        {types.map((t) => (
          <button key={t} onClick={() => setFilter(t)}
            className={`px-4 py-1.5 rounded-lg text-[11px] font-orbitron tracking-[1px] transition-all border
              ${filter === t ? 'text-[#d4af37] border-[#8b6914] bg-[rgba(212,175,55,0.08)]' : 'text-[#4b5563] border-transparent hover:text-[#94a3b8]'}`}>
            {t === 'all' ? '全部' : typeLabels[t] || t}
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center text-[#4b5563] text-sm p-20">正在查阅帝国档案...</div>
        ) : filtered.length === 0 ? (
          <div className="flex items-center justify-center text-[#4b5563] text-sm p-20">暂无记录</div>
        ) : (
          <div className="space-y-6">
            {Object.entries(grouped).map(([date, items]) => (
              <div key={date}>
                <div className="sticky top-0 z-10 flex items-center gap-3 mb-3 py-1.5">
                  <span className="font-orbitron text-xs text-[#8b6914] tracking-[2px]">{date}</span>
                  <div className="flex-1 h-px bg-[hsl(222,28%,18%)]" />
                </div>
                <div className="space-y-2">
                  {items.map((entry, i) => (
                    <TimelineEntry key={`${date}-${i}`} entry={entry} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
