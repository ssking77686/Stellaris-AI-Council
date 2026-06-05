import { useState, useEffect } from 'react';
import { api } from '@/api/client';
import type { EmpireState } from '@/api/types';
import { resources as fallbackResources } from '@/data/empire';

function mapResources(state: EmpireState | null) {
  const source = fallbackResources;
  if (!state) return source;
  const map: Record<string, number> = {
    energy: state.energy_credits, mineral: state.minerals, food: state.food,
    goods: state.consumer_goods, alloy: state.alloys, influence: state.influence, unity: state.unity,
  };
  return source.map((r) => ({ ...r, value: map[r.id] ?? r.value }));
}

export default function TopBar() {
  const [empire, setEmpire] = useState<EmpireState | null>(null);
  useEffect(() => { api.getEmpireState().then(setEmpire).catch(() => {}); }, []);
  const resData = mapResources(empire);

  return (
    <header className="bg-gradient-to-b from-[#0f1729] to-[#0c1424] border-b border-[hsl(222,28%,18%)] flex items-center px-4 h-[72px] relative gap-0 shrink-0"
      style={{ boxShadow: '0 1px 0 rgba(30,45,74,0.3), 0 4px 20px rgba(0,0,0,0.5)' }}>
      <div className="absolute bottom-0 left-0 right-0 h-px"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(212,175,55,0.3), transparent)' }} />

      <span className="font-orbitron text-[13px] font-bold text-[#d4af37] tracking-[3px] whitespace-nowrap px-4 py-1.5 border border-[#8b6914] rounded-lg mr-3 shrink-0"
        style={{ background: 'linear-gradient(135deg, rgba(212,175,55,0.08), transparent)', textShadow: '0 0 20px rgba(212,175,55,0.3)' }}>
        ✦ {empire?.name || '银河帝国'}
      </span>

      <div className="flex flex-1 overflow-x-auto gap-0">
        {resData.map((res) => (
          <div key={res.id}
            className="flex items-center gap-2 px-3 py-2 cursor-pointer shrink-0 border-r border-[hsl(222,28%,18%)]/40 hover:bg-white/[0.03] transition-all duration-200 relative"
            style={{ boxShadow: 'none' }}
            onMouseEnter={(e) => (e.currentTarget.style.boxShadow = 'inset 0 2px 0 #8b6914')}
            onMouseLeave={(e) => (e.currentTarget.style.boxShadow = 'none')}
          >
            <span className={`w-[26px] h-[26px] rounded-lg flex items-center justify-center text-[15px] border ${res.iconClass}`}>
              {res.icon}
            </span>
            <div className="flex flex-col">
              <span className="text-[9px] text-[#4b5563] uppercase tracking-[1px] font-orbitron">{res.name}</span>
              <div className="flex items-baseline gap-1">
                <span className="font-mono text-sm font-bold text-white">{res.value.toLocaleString()}</span>
                <span className={`font-mono text-[10px] ${res.delta >= 0 ? 'text-[#22c55e]' : 'text-[#ef4444]'}`}>
                  {res.delta >= 0 ? '+' : ''}{res.delta}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <span className="font-orbitron text-[11px] text-[#94a3b8] tracking-[2px] whitespace-nowrap px-3 py-2 border-l border-[hsl(222,28%,18%)] bg-black/20 rounded-lg ml-2 shrink-0">
        {empire?.game_date || '2252.06.05'}
      </span>

      {/* Quick actions */}
      <div className="flex gap-1.5 ml-2 shrink-0">
        <button className="w-[34px] h-[34px] rounded-lg bg-black/30 border border-[hsl(222,28%,18%)] text-[#94a3b8] flex items-center justify-center text-[15px] hover:border-[#8b6914] hover:text-[#d4af37] transition-all duration-300 relative">
          👑
        </button>
        <button className="w-[34px] h-[34px] rounded-lg bg-black/30 border border-[hsl(222,28%,18%)] text-[#94a3b8] flex items-center justify-center text-[15px] hover:border-[#8b6914] hover:text-[#d4af37] transition-all duration-300 relative">
          🔔
          <span className="absolute top-1 right-1 w-[7px] h-[7px] rounded-full bg-[#ef4444] animate-pulse"
            style={{ boxShadow: '0 0 0 0 rgba(239,68,68,0.6)' }} />
        </button>
        <button className="w-[34px] h-[34px] rounded-lg bg-black/30 border border-[hsl(222,28%,18%)] text-[#94a3b8] flex items-center justify-center text-[15px] hover:border-[#8b6914] hover:text-[#d4af37] transition-all duration-300">
          ⚙
        </button>
      </div>
    </header>
  );
}
