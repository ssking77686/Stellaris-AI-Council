import { useState, useEffect } from 'react';
import { api } from '@/api/client';
import type { ProposalData } from '@/api/types';

const agentIcons: Record<string, string> = {
  finance: '💰', military: '⚔', science: '🔬', foreign: '🤝', interior: '🏛', construction: '🏗',
};
const agentNames: Record<string, string> = {
  finance: '财政大臣', military: '军事大臣', science: '首席科学官',
  foreign: '外交大臣', interior: '内政大臣', construction: '建造与殖民大臣',
};

function safeDate(d: string | undefined | null): string {
  try { return d ? new Date(d).toLocaleDateString('zh-CN') : '未知'; }
  catch { return '未知'; }
}

function parseCosts(cost: string): { label: string; amount: number }[] {
  if (!cost) return [];
  try {
    const parsed = JSON.parse(cost);
    if (Array.isArray(parsed)) return parsed;
    return Object.entries(parsed).map(([k, v]) => ({ label: k, amount: Number(v) }));
  } catch {
    return [{ label: '资源', amount: 0 }];
  }
}

export default function ApprovalPanel() {
  const [proposals, setProposals] = useState<ProposalData[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ approved: 0, rejected: 0 });

  const fetchProposals = async () => {
    try {
      const data = await api.getProposals();
      setProposals(data);
    } catch { /* 后端未启动时静默处理 */ }
    setLoading(false);
  };

  useEffect(() => { fetchProposals(); }, []);

  const handleAction = async (id: string, action: 'approve' | 'reject') => {
    try {
      if (action === 'approve') await api.approveProposal(id);
      else await api.rejectProposal(id);
      setStats((s) => action === 'approve' ? { ...s, approved: s.approved + 1 } : { ...s, rejected: s.rejected + 1 });
      setProposals((prev) => prev.filter((p) => p.id !== id));
    } catch { /* 静默处理 */ }
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-orbitron text-[22px] font-bold text-[#d4af37] tracking-[3px]"
            style={{ textShadow: '0 0 30px rgba(212,175,55,0.2)' }}>审批面板</h1>
          <p className="text-xs text-[#4b5563] mt-0.5">
            待审批 {proposals.length} 项 · 已批准 {stats.approved} 项 · 已拒绝 {stats.rejected} 项
          </p>
        </div>
        <button onClick={fetchProposals}
          className="text-[11px] px-3 py-1.5 rounded-lg border border-[hsl(222,28%,18%)] text-[#94a3b8] hover:border-[#8b6914] hover:text-[#d4af37] transition-all">
          刷新
        </button>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center text-[#4b5563] text-sm p-20">正在调阅帝国档案...</div>
      ) : proposals.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-[#4b5563] text-sm p-20">暂无待审批提议</div>
      ) : (
        <div className="grid gap-3">
          {proposals.map((app) => (
            <div key={app.id} className="bg-[#111827] border border-[hsl(222,28%,18%)] rounded-lg p-5 hover:border-[hsl(222,28%,32%)] transition-all">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl border border-white/[0.08] bg-[rgba(212,175,55,0.08)] shrink-0">
                  {agentIcons[app.agent_id] || '📋'}
                </div>
                <div className="flex-1">
                  <div className="text-base font-semibold text-[#d4af37] mb-0.5">{app.title}</div>
                  <div className="text-[11px] text-[#4b5563] mb-3">
                    {agentNames[app.agent_id] || app.agent_id} 提议 · {safeDate(app.created_at)}
                  </div>
                  <p className="text-[13px] text-[#94a3b8] leading-relaxed mb-3">{app.description}</p>
                  {app.cost && (
                    <div className="flex gap-2 mb-4 flex-wrap">
                      {parseCosts(app.cost).map((c, ci) => (
                        <span key={ci} className="text-[11px] font-mono px-3 py-1 bg-black/30 rounded-lg text-[#f59e0b] border border-[hsl(222,28%,18%)]">
                          {c.label} {c.amount}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="flex gap-2">
                    <button onClick={() => handleAction(app.id, 'approve')}
                      className="px-5 py-2 rounded-lg text-[11px] font-orbitron font-semibold tracking-[1px] uppercase bg-gradient-to-r from-[#166534] to-[#22c55e] text-white border border-[#22c55e]/50 hover:shadow-[0_0_15px_rgba(34,197,94,0.3)] transition-all">
                      批准
                    </button>
                    <button onClick={() => handleAction(app.id, 'reject')}
                      className="px-5 py-2 rounded-lg text-[11px] font-orbitron font-semibold tracking-[1px] uppercase bg-transparent border border-[hsl(222,28%,18%)] text-[#94a3b8] hover:border-[#ef4444] hover:text-[#ef4444] transition-all">
                      拒绝
                    </button>
                  </div>
                </div>
                <span className="text-[9px] font-orbitron tracking-[1px] px-2 py-1 bg-[#f59e0b]/10 text-[#f59e0b] border border-[#f59e0b]/30 rounded-lg shrink-0">
                  {app.status === 'pending' ? '待审批' : app.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
