import { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';
import { api } from '@/api/client';
import type { AgentInfo, ProposalData } from '@/api/types';
import { agents as fallbackAgents } from '@/data/empire';

interface Msg { role: 'agent' | 'user' | 'proposal'; text: string; proposals?: ProposalData[] }

const ministerMeta: Record<string, { title: string; icon: string }> = {
  finance: { title: '财政大臣', icon: '💰' },
  military: { title: '军事大臣', icon: '⚔' },
  science: { title: '首席科学官', icon: '🔬' },
  foreign: { title: '外交大臣', icon: '🤝' },
  interior: { title: '内政大臣', icon: '🏛' },
  construction: { title: '建造与殖民大臣', icon: '🏗' },
};

export default function AgentChat() {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [active, setActive] = useState('finance');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Record<string, Msg[]>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getAgentList().then(setAgents).catch(() => {
      setAgents(fallbackAgents.map((a) => ({ id: a.id, role_name: a.role, domain: a.name })));
    });
  }, []);

  const currentMsgs = messages[active] || [];
  const info = agents.find((a) => a.id === active);
  const meta = ministerMeta[active] || { title: active, icon: '🤖' };

  const handleSend = useCallback(async () => {
    if (!input.trim() || loading) return;
    const text = input.trim();
    setInput('');
    setMessages((prev) => ({
      ...prev,
      [active]: [...(prev[active] || []), { role: 'user', text }],
    }));
    setLoading(true);
    try {
      const res = await api.chat(active, text);
      setMessages((prev) => ({
        ...prev,
        [active]: [
          ...(prev[active] || []),
          { role: 'agent', text: res.text, proposals: res.proposals },
        ],
      }));
    } catch {
      setMessages((prev) => ({
        ...prev,
        [active]: [...(prev[active] || []), { role: 'agent', text: '（通信故障，无法联系大臣）' }],
      }));
    } finally {
      setLoading(false);
    }
  }, [input, loading, active]);

  return (
    <div className="flex gap-3 h-full">
      {/* Minister list */}
      <div className="w-[240px] shrink-0 bg-[#111827] border border-[hsl(222,28%,18%)] rounded-lg overflow-y-auto">
        <div className="font-orbitron text-[9px] text-[#8b6914] uppercase tracking-[2px] p-3 pb-2 border-b border-[hsl(222,28%,18%)]/50">内阁大臣</div>
        {agents.map((a) => {
          const m = ministerMeta[a.id] || { title: a.role_name, icon: '🤖' };
          return (
            <div key={a.id}
              className={`flex items-center gap-2.5 p-3 cursor-pointer transition-all duration-200 border-l-2 text-sm
                ${active === a.id ? 'border-l-[#d4af37] text-[#d4af37] bg-[rgba(212,175,55,0.08)]' : 'border-l-transparent text-[#94a3b8] hover:bg-white/[0.02]'}`}
              onClick={() => setActive(a.id)}>
              <span className="text-lg">{m.icon}</span>
              <div><div className="text-[13px] font-semibold">{m.title}</div><div className="text-[10px] text-[#4b5563]">{a.domain}</div></div>
            </div>
          );
        })}
        {agents.length === 0 && (
          <div className="p-3 text-[11px] text-[#4b5563]">正在连接帝国网络...</div>
        )}
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col bg-[#111827] border border-[hsl(222,28%,18%)] rounded-lg">
        <div className="p-3 border-b border-[hsl(222,28%,18%)]/50 flex items-center gap-3">
          <span className="text-2xl">{meta.icon}</span>
          <div>
            <div className="font-orbitron text-sm font-semibold text-[#d4af37] tracking-[1px]">{meta.title}</div>
            <div className="text-[10px] text-[#4b5563]">{info?.domain || '加载中...'}</div>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
          {currentMsgs.map((msg, i) => (
            <div key={i}>
              <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[70%] p-3 rounded-lg text-sm leading-relaxed
                  ${msg.role === 'user'
                    ? 'bg-[#1e3a5f] text-[#e2e8f0] rounded-br-none'
                    : 'bg-[#1a1f2e] text-[#94a3b8] rounded-bl-none border-l-2 border-l-[#d4af37] markdown-body'}`}>
                  {msg.role === 'agent' ? <ReactMarkdown rehypePlugins={[rehypeSanitize]}>{msg.text}</ReactMarkdown> : msg.text}
                </div>
              </div>
              {msg.proposals && msg.proposals.length > 0 && (
                <div className="mt-2 ml-2 space-y-1.5">
                  {msg.proposals.map((p, pi) => (
                    <div key={pi} className="bg-[#0d111f] border border-[#8b6914] rounded-lg p-3 text-xs">
                      <span className="text-[#f59e0b] font-orbitron text-[10px] tracking-[1px]">📋 提议</span>
                      <div className="text-[#d4af37] font-semibold mt-0.5">{p.title}</div>
                      <div className="text-[#94a3b8] mt-0.5">{p.description}</div>
                      {p.cost && <div className="text-[#f59e0b] font-mono mt-1">消耗: {p.cost}</div>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-[#1a1f2e] text-[#d4af37] text-xs px-4 py-2 rounded-lg rounded-bl-none border-l-2 border-l-[#d4af37] animate-pulse">
                大臣正在拟旨...
              </div>
            </div>
          )}
        </div>
        <div className="p-3 border-t border-[hsl(222,28%,18%)]/50 flex gap-2">
          <input value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={info ? `向${meta.title}发送指令...` : '选择一位大臣开始对话'}
            className="flex-1 bg-[#0d111f] border border-[hsl(222,28%,18%)] rounded-lg px-3 py-2 text-sm text-[#e2e8f0] placeholder:text-[#4b5563] outline-none focus:border-[hsl(222,28%,32%)]" />
          <button onClick={handleSend} disabled={loading}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-[#7a6400] to-[#c8a020] text-black font-orbitron text-[11px] font-semibold tracking-[1px] uppercase border border-[#d4af37] hover:shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all disabled:opacity-50">
            发送
          </button>
        </div>
      </div>
    </div>
  );
}
