import { useState, useEffect } from 'react';
import AgentCard from '@/components/AgentCard';
import ResourceGauges from '@/components/ResourceGauges';
import RightPanel from '@/components/RightPanel';
import { api } from '@/api/client';
import type { EmpireState, AgentInfo } from '@/api/types';
import { agents as fallbackAgents, type AgentData } from '@/data/empire';

function buildAgentData(state: EmpireState | null, infos: AgentInfo[]): AgentData[] {
  if (!state) return fallbackAgents;
  const infoMap = new Map(infos.map((i) => [i.id, i]));
  return fallbackAgents.map((a) => {
    const info = infoMap.get(a.id);
    let metrics = a.metrics;
    let analysis = a.analysis;
    let progress = a.progress;

    switch (a.id) {
      case 'finance':
        metrics = [
          { label: '月净收入', value: `+${state.energy_income - state.energy_expense} ⚡ / 月`, valueClass: 'good' },
          { label: '月支出', value: `${state.energy_expense} ⚡ / 月`, valueClass: 'warn' },
          { label: '贸易总额', value: `${state.trade_value} ⚡` },
        ];
        progress = { width: Math.min(95, (state.energy_credits / 3500) * 100), color: 'gold' };
        break;
      case 'military':
        metrics = [
          { label: '舰队总战力', value: `${state.fleet_power.toLocaleString()} ⚔` },
          { label: '海军容量', value: `${state.naval_usage} / ${state.naval_capacity}` },
          { label: '星堡', value: `${state.starbase_count} 座` },
        ];
        progress = { width: (state.naval_usage / state.naval_capacity) * 100, color: 'blue' };
        break;
      case 'science':
        metrics = [
          { label: '物理学', value: `+${state.physics_research} / 月`, valueClass: 'good' },
          { label: '社会学', value: `+${state.society_research} / 月` },
          { label: '工程学', value: `+${state.engineering_research} / 月` },
        ];
        progress = { width: state.tech_progress, color: 'green' };
        break;
      case 'foreign':
        metrics = [
          { label: '联邦地位', value: state.federation_status, valueClass: 'good' },
          { label: '边境局势', value: state.border_tension === '升高' ? '紧张' : '正常', valueClass: 'warn' },
          { label: '间谍网络', value: '3 个活跃' },
        ];
        progress = { width: 45, color: 'purple' };
        break;
      case 'interior':
        metrics = [
          { label: '总人口', value: `${state.population} POP` },
          { label: '稳定度', value: `${state.stability}%`, valueClass: 'good' },
          { label: '帝国规模', value: `${state.empire_sprawl} / ${state.sprawl_cap}` },
        ];
        progress = { width: state.stability, color: 'purple' };
        break;
      case 'construction':
        progress = { width: 50, color: 'gold' };
        break;
    }
    return {
      ...a,
      name: info ? `${a.name.split('·')[0]}· ${info.role_name}` : a.name,
      analysis: a.analysis,  // 保持静态分析文本，后续可改为 API 生成
      metrics,
      progress,
    };
  });
}

export default function Dashboard() {
  const [agents, setAgents] = useState(buildAgentData(null, []));
  const [gameDate, setGameDate] = useState('');
  const [empireName, setEmpireName] = useState('银河帝国');

  useEffect(() => {
    Promise.all([
      api.getEmpireState().catch(() => null),
      api.getAgentList().catch(() => []),
    ]).then(([state, infos]) => {
      if (state) {
        setGameDate(state.game_date);
        setEmpireName(state.name);
        setAgents(buildAgentData(state, infos));
      }
    });
  }, []);

  return (
    <>
      <main className="flex-1 overflow-y-auto p-5 flex flex-col gap-3.5">
        <div className="flex items-center justify-between mb-1">
          <div>
            <h1 className="font-orbitron text-[22px] font-bold text-[#d4af37] tracking-[3px]"
              style={{ textShadow: '0 0 30px rgba(212,175,55,0.2)' }}>帝国仪表盘</h1>
            <p className="text-xs text-[#4b5563] mt-0.5">
              {empireName} · {gameDate || '第 52 年'} · 稳定度 78% · 6 位内阁大臣就任
            </p>
          </div>
          <a href="/court"
            className="flex items-center gap-2 px-7 py-3 rounded-lg font-orbitron text-xs font-semibold tracking-[3px] uppercase text-[#d4af37] border border-[#8b6914] transition-all duration-300 no-underline"
            style={{ background: 'linear-gradient(135deg, rgba(212,175,55,0.12), rgba(212,175,55,0.03))', animation: 'courtGlow 3s infinite' }}>
            👑 召开朝会
          </a>
        </div>
        <ResourceGauges />
        <div className="grid grid-cols-3 gap-3">
          {agents.map((agent) => <AgentCard key={agent.id} agent={agent} />)}
        </div>
      </main>
      <RightPanel />
    </>
  );
}
