import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '@/api/useWebSocket';

interface Speech { session_id: string; stage: string; agent_id: string; speaker: string; text: string; time: string; }
interface CourtData { id: string; status: string; transcript: Speech[]; created_at: string; }

const STAGES = [
  { key: 'opening', label: '开幕', icon: '👑' },
  { key: 'reporting', label: '汇报', icon: '📊' },
  { key: 'discussing', label: '讨论', icon: '🗣' },
  { key: 'closing', label: '闭幕', icon: '📜' },
];
const stageIndex = (s: string) => STAGES.findIndex((x) => x.key === s);

const agentIcons: Record<string, string> = {
  system: '👑', finance: '💰', military: '⚔', science: '🔬',
  foreign: '🤝', interior: '🏛', construction: '🏗',
};

function stageBadge(stage: string) {
  const label: Record<string, string> = { opening: '开幕', reporting: '汇报', discussing: '讨论', closing: '闭幕', closed: '已结束' };
  const colors: Record<string, string> = {
    opening: 'bg-[#d4af37]/15 text-[#d4af37] border-[#d4af37]/30',
    reporting: 'bg-[#3b82f6]/15 text-[#60a5fa] border-[#3b82f6]/30',
    discussing: 'bg-[#8b5cf6]/15 text-[#8b5cf6] border-[#8b5cf6]/30',
    closing: 'bg-[#22c55e]/15 text-[#22c55e] border-[#22c55e]/30',
    closed: 'bg-[#4b5563]/15 text-[#94a3b8] border-[#4b5563]/30',
  };
  return <span className={`text-[8px] px-1.5 py-0.5 rounded-lg font-orbitron tracking-[1px] border ${colors[stage] || colors.closed}`}>{label[stage] || stage}</span>;
}

export default function CourtHall() {
  const [session, setSession] = useState<CourtData | null>(null);
  const [speeches, setSpeeches] = useState<Speech[]>([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<CourtData[]>([]);

  useEffect(() => {
    fetch('http://localhost:8001/api/court/current').then(r => r.json()).then((d) => {
      if (d.session) { setSession(d.session); setSpeeches(d.session.transcript || []); }
      else {
        fetch('http://localhost:8001/api/court/history?limit=5').then(r => r.json()).then(setHistory).catch(() => {});
      }
    }).catch(() => {});
  }, []);

  useWebSocket(useCallback((msg) => {
    if (msg.type === 'court_speech') {
      setSpeeches((prev) => prev.some((s) => s.time === msg.data.time) ? prev : [...prev, msg.data]);
      setSession((prev) => prev ? { ...prev, status: msg.data.stage } : prev);
    }
    if (msg.type === 'court_closed') {
      setSession((prev) => prev ? { ...prev, status: 'closed' } : prev);
    }
  }, []));

  const startCourt = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8001/api/court/start', { method: 'POST' });
      const data = await res.json();
      setSession({ id: data.session_id, status: 'opening', transcript: [], created_at: new Date().toISOString() });
      setSpeeches([]);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const currentStageIdx = stageIndex(session?.status || 'closed');

  return (
    <div className="flex flex-col gap-3 h-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-orbitron text-[22px] font-bold text-[#d4af37] tracking-[3px]"
            style={{ textShadow: '0 0 30px rgba(212,175,55,0.2)' }}>朝会大厅</h1>
          <p className="text-xs text-[#4b5563] mt-0.5">
            {session ? `进行中 · ${speeches.length} 条发言 · ${STAGES[currentStageIdx]?.label || '准备中'}` : `${history.length} 场历史朝会`}
          </p>
        </div>
        <button onClick={startCourt} disabled={loading || !!session}
          className="flex items-center gap-2 px-7 py-3 rounded-lg font-orbitron text-xs font-semibold tracking-[3px] uppercase text-[#d4af37] border border-[#8b6914] transition-all duration-300 disabled:opacity-30 disabled:cursor-not-allowed"
          style={{ background: 'linear-gradient(135deg, rgba(212,175,55,0.12), rgba(212,175,55,0.03))', animation: session ? 'none' : 'courtGlow 3s infinite' }}>
          👑 {session ? '朝会进行中' : '召开朝会'}
        </button>
      </div>

      {/* Stage progress */}
      <div className="flex gap-1 bg-[#111827] border border-[hsl(222,28%,18%)] rounded-lg p-1.5">
        {STAGES.map((s, i) => (
          <div key={s.key} className={`flex items-center gap-1.5 flex-1 text-center py-2.5 rounded-lg text-[10px] font-orbitron tracking-[1px] transition-all duration-500 justify-center
            ${i <= currentStageIdx ? 'text-[#d4af37] bg-[rgba(212,175,55,0.1)]' : 'text-[#4b5563]'}`}>
            <span>{s.icon}</span> {s.label}
          </div>
        ))}
      </div>

      {/* Transcript */}
      <div className="flex-1 overflow-y-auto bg-[#111827] border border-[hsl(222,28%,18%)] rounded-lg p-4 flex flex-col gap-3">
        {session && speeches.length === 0 && (
          <div className="flex-1 flex items-center justify-center text-[#4b5563] text-sm animate-pulse">
            等待大臣入朝...
          </div>
        )}

        {speeches.map((sp, i) => (
          <div key={i} className={`flex ${sp.agent_id === 'system' ? 'justify-center' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3.5 rounded-lg text-sm leading-relaxed
              ${sp.agent_id === 'system'
                ? 'bg-[rgba(212,175,55,0.06)] border border-[#8b6914] text-center text-[#d4af37]'
                : 'bg-[#1a1f2e] text-[#94a3b8] border-l-2 border-l-[#d4af37]'}`}>
              <div className="flex items-center gap-2 mb-1.5">
                <span>{agentIcons[sp.agent_id] || '🤖'}</span>
                <span className="font-orbitron text-[10px] text-[#d4af37] tracking-[1px]">{sp.speaker}</span>
                {stageBadge(sp.stage)}
                <span className="text-[9px] text-[#4b5563] font-mono ml-auto">
                  {new Date(sp.time).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </div>
              <div className="markdown-body whitespace-pre-wrap">{sp.text}</div>
            </div>
          </div>
        ))}

        {!session && history.length > 0 && (
          <div className="space-y-2">
            <div className="text-xs text-[#8b6914] font-orbitron tracking-[2px] mb-2">📜 历史朝会</div>
            {history.map((h) => (
              <div key={h.id} className="p-3 bg-[#0d111f] border border-[hsl(222,28%,18%)] rounded-lg cursor-pointer hover:border-[#8b6914] transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[#d4af37] font-semibold">
                    朝会 · {new Date(h.created_at).toLocaleDateString('zh-CN')}
                  </span>
                  <span className="text-[10px] text-[#4b5563]">{h.transcript.length} 条发言</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {!session && history.length === 0 && (
          <div className="flex-1 flex items-center justify-center text-[#4b5563] text-sm">
            暂无朝会记录，点击上方按钮召开朝会
          </div>
        )}
      </div>

      <style>{`
        @keyframes courtGlow {
          0%, 100% { box-shadow: 0 0 5px rgba(212,175,55,0.1); }
          50% { box-shadow: 0 0 25px rgba(212,175,55,0.2); }
        }
      `}</style>
    </div>
  );
}
