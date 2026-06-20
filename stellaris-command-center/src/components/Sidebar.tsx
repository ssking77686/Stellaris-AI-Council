import { NavLink } from 'react-router-dom';

interface NavItem { icon: string; label: string; to: string; badge?: string }

const navSections: { title: string; items: NavItem[] }[] = [
  {
    title: '指挥中心',
    items: [
      { icon: '◈', label: '帝国仪表盘', to: '/' },
      { icon: '💬', label: '大臣对话', to: '/chat' },
      { icon: '📋', label: '审批面板', to: '/approvals' },
      { icon: '📂', label: '存档管理器', to: '/saves' },
    ],
  },
  {
    title: '帝国议会',
    items: [
      { icon: '👑', label: '朝会大厅', to: '/court' },
      { icon: '📜', label: '帝国编年史', to: '/chronicle' },
    ],
  },
  {
    title: '内阁大臣',
    items: [
      { icon: '💰', label: '财政大臣', to: '/chat' },
      { icon: '⚔', label: '军事大臣', to: '/chat' },
      { icon: '🔬', label: '首席科学官', to: '/chat' },
      { icon: '🤝', label: '外交大臣', to: '/chat' },
      { icon: '🏛', label: '内政大臣', to: '/chat' },
      { icon: '🏗', label: '建造与殖民大臣', to: '/chat' },
    ],
  },
];

const linkStyle = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-2.5 py-2.5 px-[18px] mx-2 rounded-lg cursor-pointer text-[13px] transition-all duration-200 relative no-underline ${
    isActive
      ? 'text-[#d4af37] border-l-2 border-[#d4af37] ml-1'
      : 'text-[#94a3b8] hover:bg-white/[0.03] hover:text-[#e2e8f0]'
  }`;

export default function Sidebar() {
  return (
    <nav className="bg-gradient-to-r from-[#0b101e] to-[#0d111f] border-r border-[hsl(222,28%,18%)] py-3 flex flex-col gap-px w-[230px] shrink-0 overflow-y-auto"
      style={{ boxShadow: '2px 0 20px rgba(0,0,0,0.3)' }}>
      {navSections.map((section) => (
        <div key={section.title}>
          <div className="px-[18px] pt-2.5 pb-1 text-[9px] uppercase tracking-[2.5px] text-[#8b6914] font-orbitron">{section.title}</div>
          {section.items.map((item) => (
            <NavLink key={item.label} to={item.to} end={item.to === '/'} className={linkStyle}
              style={({ isActive }) => (isActive ? { background: 'linear-gradient(90deg, rgba(212,175,55,0.12), transparent)', boxShadow: 'inset 0 0 20px rgba(212,175,55,0.05)' } : {})}>
              <span className="text-[17px] w-6 text-center">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </div>
      ))}
    </nav>
  );
}
