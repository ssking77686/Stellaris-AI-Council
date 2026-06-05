export interface ResourceData {
  id: string;
  name: string;
  icon: string;
  value: number;
  delta: number;
  iconClass: string;
}

export interface AgentMetrics {
  label: string;
  value: string;
  valueClass?: 'good' | 'warn' | 'bad';
}

export interface ProgressBar {
  width: number;
  color: 'gold' | 'blue' | 'green' | 'red' | 'purple';
}

export interface AgentData {
  id: string;
  role: string;
  name: string;
  icon: string;
  status: string;
  statusType: 'good' | 'warn' | 'bad';
  metrics: AgentMetrics[];
  progress: ProgressBar;
  analysis: string;
  iconBg: string;
  iconBorder: string;
}

export interface EventItem {
  time: string;
  tag: '提议' | '报告' | '预警' | '协商';
  text: string;
}

export interface ApprovalItem {
  id: string;
  icon: string;
  title: string;
  agent: string;
  detail: string;
  costs: { label: string; amount: number }[];
}

export const resources: ResourceData[] = [
  { id: 'energy', name: '能量币', icon: '⚡', value: 2847, delta: 24, iconClass: 'border-yellow-600/30 bg-yellow-500/10' },
  { id: 'mineral', name: '矿物', icon: '⛏', value: 1203, delta: 18, iconClass: 'border-orange-600/30 bg-orange-500/10' },
  { id: 'food', name: '食物', icon: '🌾', value: 456, delta: 8, iconClass: 'border-green-600/30 bg-green-500/10' },
  { id: 'goods', name: '消费品', icon: '📦', value: 312, delta: -3, iconClass: 'border-purple-600/30 bg-purple-500/10' },
  { id: 'alloy', name: '合金', icon: '⚙', value: 89, delta: 5, iconClass: 'border-slate-500/30 bg-slate-500/10' },
  { id: 'influence', name: '影响力', icon: '★', value: 340, delta: 3, iconClass: 'border-amber-500/30 bg-amber-500/10' },
  { id: 'unity', name: '凝聚力', icon: '✦', value: 1050, delta: 12, iconClass: 'border-sky-500/30 bg-sky-500/10' },
];

export const agents: AgentData[] = [
  {
    id: 'finance',
    role: '帝国经济',
    name: '财政大臣 · 瓦伦·喀山',
    icon: '💰',
    status: '盈余',
    statusType: 'good',
    metrics: [
      { label: '月净收入', value: '+24 ⚡ / 月', valueClass: 'good' },
      { label: '月支出', value: '48 ⚡ / 月', valueClass: 'warn' },
      { label: '贸易总额', value: '156 ⚡' },
    ],
    progress: { width: 72, color: 'gold' },
    analysis: '贸易收入占比过高（62%），建议在第3星区增设能量枢纽以分散收入来源。消费品出现-3赤字需关注。',
    iconBg: 'rgba(212,175,55,0.1)',
    iconBorder: 'rgba(212,175,55,0.2)',
  },
  {
    id: 'military',
    role: '军事实力',
    name: '军事大臣 · 塔罗斯·阿基里斯',
    icon: '⚔',
    status: '备战',
    statusType: 'good',
    metrics: [
      { label: '舰队总战力', value: '3,200 ⚔' },
      { label: '海军容量', value: '28 / 40' },
      { label: '星堡', value: '4 座（3 升级中）' },
    ],
    progress: { width: 64, color: 'blue' },
    analysis: '邻国"泽恩共同体"舰队在边境集结，建议在边境星系建造第5座星堡。海军容量尚余12单位，可扩充第4舰队。',
    iconBg: 'rgba(239,68,68,0.1)',
    iconBorder: 'rgba(239,68,68,0.2)',
  },
  {
    id: 'science',
    role: '科研进展',
    name: '首席科学官 · 莉亚·诺瓦',
    icon: '🔬',
    status: '突破中',
    statusType: 'good',
    metrics: [
      { label: '物理学', value: '+96 / 月', valueClass: 'good' },
      { label: '社会学', value: '+88 / 月' },
      { label: '工程学', value: '+102 / 月' },
    ],
    progress: { width: 58, color: 'green' },
    analysis: '先进激光武器预计6个月后研发完成，建议同步储备稀有水晶资源。社会学方向可考虑解锁"殖民狂热"传统加速扩张。',
    iconBg: 'rgba(6,182,212,0.1)',
    iconBorder: 'rgba(6,182,212,0.2)',
  },
  {
    id: 'foreign',
    role: '外交态势',
    name: '外交大臣 · 塞拉斯·艾瑞斯',
    icon: '🤝',
    status: '关注',
    statusType: 'warn',
    metrics: [
      { label: '联邦地位', value: '理事会成员', valueClass: 'good' },
      { label: '周边关系', value: '2 国态度冷淡', valueClass: 'warn' },
      { label: '间谍网络', value: '3 个活跃' },
    ],
    progress: { width: 45, color: 'purple' },
    analysis: '泽恩共同体对我方边境星系的探测行为需要外交途径交涉。建议向理事会提议通过贸易制裁决议。',
    iconBg: 'rgba(139,92,246,0.1)',
    iconBorder: 'rgba(139,92,246,0.2)',
  },
  {
    id: 'interior',
    role: '内政与人口',
    name: '内政大臣 · 艾琳·沃斯',
    icon: '🏛',
    status: '稳定',
    statusType: 'good',
    metrics: [
      { label: '总人口', value: '48 POP' },
      { label: '稳定度', value: '78%', valueClass: 'good' },
      { label: '帝国规模', value: '62 / 80' },
    ],
    progress: { width: 78, color: 'purple' },
    analysis: '军国主义派系支持率上升（目前34%），可考虑满足其扩张诉求以提高影响力收入。母星失业率3%，需新增岗位。',
    iconBg: 'rgba(100,160,220,0.1)',
    iconBorder: 'rgba(100,160,220,0.2)',
  },
  {
    id: 'construction',
    role: '建造与殖民',
    name: '建造与殖民大臣 · 马库斯·石锤',
    icon: '🏗',
    status: '扩展中',
    statusType: 'good',
    metrics: [
      { label: '已殖民星球', value: '4 颗' },
      { label: '在建项目', value: '3 个' },
      { label: '可殖民星系', value: '2 个待评估' },
    ],
    progress: { width: 50, color: 'gold' },
    analysis: '天津四星系第2行星宜居度72%，建议派遣殖民船。母星第3区划空置，可建造合金铸造厂。边境矿区防御薄弱需配合军事大臣部署。',
    iconBg: 'rgba(245,158,11,0.1)',
    iconBorder: 'rgba(245,158,11,0.2)',
  },
];

export const events: EventItem[] = [
  { time: '2252.06.05 09:30', tag: '提议', text: '财政大臣：建造半人马座α采矿站（矿物+8/月）' },
  { time: '2252.06.05 08:00', tag: '协商', text: '建造大臣向军事大臣请求边境矿区防御部署' },
  { time: '2252.06.04 14:15', tag: '报告', text: '军事大臣：舰队演习完成，第二舰队战力1,200' },
  { time: '2252.06.03 16:00', tag: '预警', text: '外交大臣：泽恩共同体舰队出现在我方边境' },
  { time: '2252.06.01 12:00', tag: '报告', text: '首席科学官：物理学突破，解锁先进激光武器分支' },
  { time: '2252.05.28 10:20', tag: '提议', text: '建造大臣：天津四星系殖民计划（宜居度72%）' },
];

export const approvals: ApprovalItem[] = [
  {
    id: '1',
    icon: '🪐',
    title: '半人马座α采矿站',
    agent: '财政大臣 · 瓦伦·喀山 提议',
    detail: '该星系矿物产量丰富，建成后预计月收入+8矿物，可缓解当前合金冶炼的原料压力。',
    costs: [{ label: '⛏ 矿物', amount: 100 }, { label: '⚡ 能量币', amount: 50 }],
  },
  {
    id: '2',
    icon: '🛡',
    title: '边境星堡（第5座）',
    agent: '军事大臣 · 塔罗斯·阿基里斯 提议',
    detail: '针对泽恩共同体的边境活动，建议在边境星系增建星堡以增强防御威慑。',
    costs: [{ label: '⚙ 合金', amount: 200 }, { label: '★ 影响力', amount: 50 }],
  },
  {
    id: '3',
    icon: '🚀',
    title: '天津四星系殖民计划',
    agent: '建造与殖民大臣 · 马库斯·石锤 提议',
    detail: '天津四第2行星宜居度72%，拥有丰富的矿物和能源资源，建议派遣殖民船。',
    costs: [{ label: '⛏ 矿物', amount: 200 }, { label: '🌾 食物', amount: 100 }, { label: '⚡ 能量币', amount: 200 }],
  },
];
