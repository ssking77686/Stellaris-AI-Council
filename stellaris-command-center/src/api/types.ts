// 后端 API 返回类型

export interface EmpireState {
  id: number;
  name: string;
  game_date: string;
  energy_credits: number;
  minerals: number;
  food: number;
  consumer_goods: number;
  alloys: number;
  influence: number;
  unity: number;
  energy_income: number;
  energy_expense: number;
  mineral_income: number;
  trade_value: number;
  naval_capacity: number;
  naval_usage: number;
  fleet_power: number;
  starbase_count: number;
  army_count: number;
  physics_research: number;
  society_research: number;
  engineering_research: number;
  current_tech: string;
  tech_progress: number;
  federation_status: string;
  border_tension: string;
  population: number;
  stability: number;
  empire_sprawl: number;
  sprawl_cap: number;
}

export interface AgentInfo {
  id: string;
  role_name: string;
  domain: string;
}

export interface ProposalData {
  id: string;
  agent_id: string;
  title: string;
  description: string;
  cost: string;
  status: string;
  created_at: string;
}

export interface ChatResponse {
  text: string;
  proposals: ProposalData[];
}

export interface TickResponse {
  state: EmpireState;
  event: EmpireEvent | null;
}

export interface EmpireEvent {
  id: number;
  event_type: string;
  title: string;
  description: string;
  agent_id: string;
  created_at: string;
}

export interface ChronicleEntry {
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

// 存档管理
export interface WatcherStatus {
  running: boolean;
  directory: string;
  last_detection: string;
  last_path: string;
}

export interface SaveRecord {
  id: number;
  save_name: string;
  game_date: string;
  empire_name: string;
  parsed_at: string;
}

export interface PlanetSummary {
  name: string;
  planet_class: string;
  designation: string;
  population: number;
  stability: number;
  districts: Record<string, number>;
  buildings: string[];
}

export interface FleetSummary {
  name: string;
  fleet_power: number;
  ship_count: number;
  location: string;
}

export interface SaveDetail {
  id: number;
  save_name: string;
  game_date: string;
  empire_name: string;
  planets: PlanetSummary[];
  fleets: FleetSummary[];
  technologies: string[];
  diplomacy: Record<string, unknown>;
  leaders: Record<string, unknown>[];
  empire: Record<string, unknown>;
  parsed_at: string;
}

export interface SaveUploadResponse {
  meta: Record<string, unknown>;
  empire: Record<string, unknown>;
  resources: Record<string, number>;
  planets: PlanetSummary[];
  fleets: FleetSummary[];
  technologies: string[];
  diplomacy: Record<string, unknown>;
  leaders: Record<string, unknown>[];
  parsed: boolean;
  error: string | null;
}
