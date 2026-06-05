import { useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Starfield from '@/components/Starfield';
import TopBar from '@/components/TopBar';
import Sidebar from '@/components/Sidebar';
import Dashboard from '@/pages/Dashboard';
import AgentChat from '@/pages/AgentChat';
import ApprovalPanel from '@/pages/ApprovalPanel';
import CourtHall from '@/pages/CourtHall';
import Chronicle from '@/pages/Chronicle';
import SaveManager from '@/pages/SaveManager';
import { useWebSocket } from '@/api/useWebSocket';

interface Toast { id: number; type: string; text: string }

let toastId = 0;
const typeLabel: Record<string, string> = {
  empire_tick: '⏳', periodic_report: '📊', coordination: '🤝', new_proposal: '📋',
  save_updated: '💾',
};

function AppLayout({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((type: string, text: string) => {
    const id = ++toastId;
    setToasts((prev) => [...prev.slice(-4), { id, type, text }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 5000);
  }, []);

  useWebSocket((msg) => {
    switch (msg.type) {
      case 'empire_tick':
        addToast('empire_tick', `时间推进 · ${msg.data.state.game_date}`);
        break;
      case 'periodic_report':
        const alerts = msg.data.alerts?.length
          ? `预警: ${msg.data.alerts.join(', ')}`
          : '帝国运转正常';
        addToast('periodic_report', `帝国报告 · ${msg.data.date} · ${alerts}`);
        break;
      case 'coordination':
        addToast('coordination', `协商完成: ${msg.data.from} ↔ ${msg.data.to}`);
        break;
      case 'save_updated':
        const d = msg.data;
        const alertText = d.alerts?.length ? ` · 预警: ${d.alerts.join(', ')}` : '';
        addToast('save_updated',
          `存档已更新 · ${d.game_date} · ${d.empire_name} · ${d.summary?.planets || 0}星球 · ${d.summary?.fleet_power || 0}战力${alertText}`);
        break;
    }
  });

  return (
    <div className="h-screen flex flex-col bg-[#06080f] text-[#e2e8f0]">
      <Starfield />
      <div className="scanlines" />
      <TopBar />
      <div className="flex flex-1 overflow-hidden relative z-[1]">
        <Sidebar />
        {children}
      </div>

      {/* Toast notifications */}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
        {toasts.map((t) => (
          <div key={t.id}
            className="bg-[#111827] border border-[#8b6914] rounded-lg px-4 py-2.5 text-xs text-[#94a3b8] shadow-lg pointer-events-auto animate-[slideIn_0.3s_ease-out]"
            style={{ boxShadow: '0 0 20px rgba(212,175,55,0.1)' }}>
            <span className="mr-2">{typeLabel[t.type] || '📡'}</span>
            {t.text}
          </div>
        ))}
      </div>

      <style>{`
        @keyframes courtGlow {
          0%, 100% { box-shadow: 0 0 5px rgba(212,175,55,0.1); }
          50% { box-shadow: 0 0 25px rgba(212,175,55,0.2); }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(20px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout><Dashboard /></AppLayout>} />
        <Route path="/chat" element={<AppLayout><AgentChat /></AppLayout>} />
        <Route path="/approvals" element={<AppLayout><ApprovalPanel /></AppLayout>} />
        <Route path="/court" element={<AppLayout><CourtHall /></AppLayout>} />
        <Route path="/chronicle" element={<AppLayout><Chronicle /></AppLayout>} />
        <Route path="/saves" element={<AppLayout><SaveManager /></AppLayout>} />
      </Routes>
    </BrowserRouter>
  );
}
