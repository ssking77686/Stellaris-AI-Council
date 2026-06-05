import { useState, useEffect } from 'react';
import { api } from '@/api/client';
import type { EmpireEvent, ProposalData } from '@/api/types';

const tagStyles: Record<string, string> = {
  '提议': 'bg-[#3b82f6]/15 text-[#60a5fa] border border-[#3b82f6]/30',
  '报告': 'bg-[#22c55e]/15 text-[#22c55e] border border-[#22c55e]/30',
  '预警': 'bg-[#ef4444]/15 text-[#ef4444] border border-[#ef4444]/30',
  '协商': 'bg-[#8b5cf6]/15 text-[#8b5cf6] border border-[#8b5cf6]/30',
  'proposal': 'bg-[#3b82f6]/15 text-[#60a5fa] border border-[#3b82f6]/30',
  'report': 'bg-[#22c55e]/15 text-[#22c55e] border border-[#22c55e]/30',
  'alert': 'bg-[#ef4444]/15 text-[#ef4444] border border-[#ef4444]/30',
  'coordination': 'bg-[#8b5cf6]/15 text-[#8b5cf6] border border-[#8b5cf6]/30',
  'random': 'bg-[#f59e0b]/15 text-[#f59e0b] border border-[#f59e0b]/30',
};

const eventTypeTag: Record<string, string> = {
  proposal: '提议', report: '报告', alert: '预警', coordination: '协商', random: '事件',
};

function formatTime(d: string) {
  try { return new Date(d).toLocaleString('zh-CN', { hour12: false }); }
  catch { return d; }
}

const agentIcons: Record<string, string> = {
  finance: '💰', military: '⚔', science: '🔬', foreign: '🤝', interior: '🏛', construction: '🏗',
};

export default function RightPanel() {
  const [events, setEvents] = useState<EmpireEvent[]>([]);
  const [approvals, setApprovals] = useState<ProposalData[]>([]);

  useEffect(() => {
    api.getEvents().then(setEvents).catch(() => {});
    api.getProposals('pending').then(setApprovals).catch(() => {});
  }, []);

  const handleApproval = async (id: string, action: 'approve' | 'reject') => {
    try {
      if (action === 'approve') await api.approveProposal(id);
      else await api.rejectProposal(id);
      setApprovals((prev) => prev.filter((a) => a.id !== id));
    } catch { /* 静默处理 */ }
  };

  return (
    <aside className="bg-gradient-to-l from-[#0b101e] to-[#0d111f] border-l border-[hsl(222,28%,18%)] p-3.5 flex flex-col gap-3 w-[340px] shrink-0 overflow-y-auto"
      style={{ boxShadow: '-2px 0 20px rgba(0,0,0,0.3)' }}>

      {/* Events */}
      <div>
        <div className="font-orbitron text-[9px] text-[#8b6914] uppercase tracking-[2.5px] pb-1.5 mb-0.5 border-b border-[hsl(222,28%,18%)]/40">
          📡 帝国动态
        </div>
        <div className="flex flex-col gap-1.5 mt-2">
          {events.map((ev) => {
            const tag = eventTypeTag[ev.event_type] || ev.event_type;
            return (
              <div key={ev.id}
                className="p-2.5 bg-[#0d111f]/60 border border-transparent border-l-2 border-l-[hsl(222,28%,18%)] rounded-lg text-[11px] cursor-pointer transition-all duration-200 hover:border-[hsl(222,28%,32%)] hover:border-l-[#3b82f6] hover:bg-[#111827]/80">
                <div className="font-mono text-[9px] text-[#4b5563] mb-0.5">{formatTime(ev.created_at)}</div>
                <span className={`inline-block text-[8px] px-1.5 py-0.5 rounded-lg mr-1 font-orbitron tracking-[1px] font-semibold ${tagStyles[ev.event_type] || tagStyles['random']}`}>
                  {tag}
                </span>
                <span className="text-[#94a3b8] leading-relaxed">{ev.title}</span>
              </div>
            );
          })}
          {events.length === 0 && (
            <div className="text-[10px] text-[#4b5563] p-2">暂无动态记录</div>
          )}
        </div>
      </div>

      {/* Approvals */}
      <div>
        <div className="font-orbitron text-[9px] text-[#8b6914] uppercase tracking-[2.5px] pb-1.5 mb-0.5 border-b border-[hsl(222,28%,18%)]/40">
          🗓 待审批
        </div>
        <div className="flex flex-col gap-2.5 mt-2">
          {approvals.map((app) => (
            <div key={app.id}
              className="p-3.5 bg-[#0d111f]/80 border border-[#8b6914] rounded-lg relative transition-all duration-300 hover:border-[#d4af37]"
              style={{ boxShadow: 'none' }}
              onMouseEnter={(e) => { e.currentTarget.style.boxShadow = '0 0 20px rgba(212,175,55,0.1)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.boxShadow = 'none'; }}
            >
              <span className="absolute -top-2.5 right-3 w-6 h-6 bg-[#111827] border border-[#8b6914] rounded-full flex items-center justify-center text-xs">
                {agentIcons[app.agent_id] || '📋'}
              </span>
              <div className="text-[13px] font-semibold text-[#d4af37] mb-1">{app.title}</div>
              <div className="text-[10px] text-[#4b5563] mb-1.5">{app.agent_id}</div>
              <div className="text-[11px] text-[#94a3b8] leading-relaxed mb-2.5">{app.description}</div>
              <div className="flex gap-1.5">
                <button onClick={() => handleApproval(app.id, 'approve')}
                  className="px-3.5 py-1.5 rounded-lg text-[10px] font-orbitron font-semibold tracking-[1px] uppercase bg-gradient-to-r from-[#7a6400] to-[#c8a020] text-black border border-[#d4af37] hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] transition-all">
                  批准
                </button>
                <button onClick={() => handleApproval(app.id, 'reject')}
                  className="px-3.5 py-1.5 rounded-lg text-[10px] font-orbitron font-semibold tracking-[1px] uppercase bg-transparent border border-[hsl(222,28%,18%)] text-[#94a3b8] hover:border-[#94a3b8] hover:text-white transition-all">
                  拒绝
                </button>
              </div>
            </div>
          ))}
          {approvals.length === 0 && (
            <div className="text-[10px] text-[#4b5563] p-2">暂无待审批提议</div>
          )}
        </div>
      </div>
    </aside>
  );
}
