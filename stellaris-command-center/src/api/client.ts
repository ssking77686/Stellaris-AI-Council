const BASE = 'http://localhost:8001';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  // 帝国
  getEmpireState: () => request<import('./types').EmpireState>('/api/empire/state'),
  tickEmpire: (days = 1) =>
    request<import('./types').TickResponse>(`/api/empire/tick?days=${days}`, { method: 'POST' }),

  // Agent
  getAgentList: () => request<import('./types').AgentInfo[]>('/api/agents/list'),
  chat: (agentId: string, message: string) =>
    request<import('./types').ChatResponse>('/api/agents/chat', {
      method: 'POST',
      body: JSON.stringify({ agent_id: agentId, message }),
    }),

  // 审批
  getProposals: (status = 'pending') =>
    request<import('./types').ProposalData[]>(`/api/proposals/?status=${status}`),
  approveProposal: (id: string) =>
    request<{ status: string }>(`/api/proposals/${id}/approve`, { method: 'POST' }),
  rejectProposal: (id: string) =>
    request<{ status: string }>(`/api/proposals/${id}/reject`, { method: 'POST' }),

  // 事件
  getEvents: (limit = 20) =>
    request<import('./types').EmpireEvent[]>(`/api/events/?limit=${limit}`),

  // 编年史
  getChronicle: (limit = 60) =>
    request<import('./types').EmpireEvent[]>(`/api/chronicle/?limit=${limit}`),

  // 存档管理
  getWatcherStatus: () =>
    request<import('./types').WatcherStatus>('/api/save/watcher/status'),
  startWatcher: (directory: string) =>
    request<{ status: string }>('/api/save/watcher/start', {
      method: 'POST',
      body: JSON.stringify({ directory }),
    }),
  stopWatcher: () =>
    request<{ status: string }>('/api/save/watcher/stop', { method: 'POST' }),
  uploadSave: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch(`${BASE}/api/save/upload`, { method: 'POST', body: formData }).then(
      (r) => r.json() as Promise<import('./types').SaveUploadResponse>,
    );
  },
  getSaveHistory: (limit = 10) =>
    request<import('./types').SaveRecord[]>(`/api/save/history?limit=${limit}`),
  getSaveDetail: (id: number) =>
    request<import('./types').SaveDetail>(`/api/save/${id}/detail`),
};
