import { useState, useEffect } from 'react';
import { api } from '@/api/client';
import type { ConfigData } from '@/api/types';

const MODELS = [
  { value: 'deepseek-chat', label: 'DeepSeek Chat (V3)' },
  { value: 'deepseek-reasoner', label: 'DeepSeek Reasoner (R1)' },
];

export default function Settings() {
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [baseUrl, setBaseUrl] = useState('https://api.deepseek.com');
  const [model, setModel] = useState('deepseek-chat');
  const [showKey, setShowKey] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ status: string; message: string } | null>(null);
  const [saveMsg, setSaveMsg] = useState('');

  useEffect(() => {
    api.getConfig().then((c) => {
      setConfig(c);
      setBaseUrl(c.base_url);
      setModel(c.model);
    }).catch(() => {});
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg('');
    try {
      await api.updateConfig({ api_key: apiKey, base_url: baseUrl, model });
      setApiKey('');
      setSaveMsg('配置已保存');
      const updated = await api.getConfig();
      setConfig(updated);
    } catch {
      setSaveMsg('保存失败，请检查后端是否运行');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      // 如果用户输入了新 Key，先临时保存再测试
      if (apiKey) {
        await api.updateConfig({ api_key: apiKey, base_url: baseUrl, model });
      }
      const result = await api.testConnection();
      setTestResult(result);
      const updated = await api.getConfig();
      setConfig(updated);
    } catch {
      setTestResult({ status: 'error', message: '无法连接到后端服务' });
    } finally {
      setTesting(false);
    }
  };

  return (
    <main className="flex-1 overflow-y-auto p-8 flex flex-col items-center">
      <div className="w-full max-w-[520px] space-y-6">
        {/* 标题 */}
        <div className="mb-2">
          <h1 className="font-orbitron text-[22px] font-bold text-[#d4af37] tracking-[3px]"
            style={{ textShadow: '0 0 30px rgba(212,175,55,0.2)' }}>系统设置</h1>
          <p className="text-xs text-[#4b5563] mt-1">配置 DeepSeek API 连接参数</p>
        </div>

        {/* API Key */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-[#94a3b8] uppercase tracking-[1px]">API Key</label>
          <div className="relative">
            <input
              type={showKey ? 'text' : 'password'}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={config?.api_key_masked || '输入你的 DeepSeek API Key'}
              className="w-full bg-[#0d1117] border border-[hsl(222,28%,18%)] rounded-lg px-4 py-2.5 text-sm text-[#e2e8f0] placeholder:text-[#4b5563] focus:outline-none focus:border-[#8b6914] focus:ring-1 focus:ring-[#8b6914]/30 transition-all font-mono"
            />
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#4b5563] hover:text-[#94a3b8] text-xs transition-colors"
            >
              {showKey ? '隐藏' : '显示'}
            </button>
          </div>
          {config?.api_key_masked && !apiKey && (
            <p className="text-[10px] text-[#4b5563]">当前: {config.api_key_masked}</p>
          )}
        </div>

        {/* Base URL */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-[#94a3b8] uppercase tracking-[1px]">API Base URL</label>
          <input
            type="text"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            className="w-full bg-[#0d1117] border border-[hsl(222,28%,18%)] rounded-lg px-4 py-2.5 text-sm text-[#e2e8f0] focus:outline-none focus:border-[#8b6914] focus:ring-1 focus:ring-[#8b6914]/30 transition-all font-mono"
          />
        </div>

        {/* Model */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-[#94a3b8] uppercase tracking-[1px]">模型</label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full bg-[#0d1117] border border-[hsl(222,28%,18%)] rounded-lg px-4 py-2.5 text-sm text-[#e2e8f0] focus:outline-none focus:border-[#8b6914] focus:ring-1 focus:ring-[#8b6914]/30 transition-all cursor-pointer"
          >
            {MODELS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>

        {/* 按钮区 */}
        <div className="flex gap-3 pt-2">
          <button
            onClick={handleTest}
            disabled={testing}
            className="flex-1 py-2.5 rounded-lg text-sm font-semibold border transition-all duration-300 disabled:opacity-50"
            style={{
              borderColor: 'hsl(222,28%,18%)',
              color: '#94a3b8',
              background: testing ? 'transparent' : 'linear-gradient(135deg, rgba(148,163,184,0.08), rgba(148,163,184,0.02))',
            }}
          >
            {testing ? '测试中...' : '🔍 测试连接'}
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !apiKey}
            className="flex-1 py-2.5 rounded-lg text-sm font-bold transition-all duration-300 disabled:opacity-50"
            style={{
              background: apiKey
                ? 'linear-gradient(135deg, rgba(212,175,55,0.18), rgba(212,175,55,0.06))'
                : 'transparent',
              border: apiKey ? '1px solid #8b6914' : '1px solid hsl(222,28%,18%)',
              color: apiKey ? '#d4af37' : '#4b5563',
              boxShadow: apiKey ? '0 0 20px rgba(212,175,55,0.08)' : 'none',
            }}
          >
            {saving ? '保存中...' : '💾 保存配置'}
          </button>
        </div>

        {/* 测试结果 */}
        {testResult && (
          <div className={`p-4 rounded-lg border text-sm ${
            testResult.status === 'ok'
              ? 'border-[#22c55e]/30 bg-[#22c55e]/5 text-[#22c55e]'
              : 'border-[#ef4444]/30 bg-[#ef4444]/5 text-[#ef4444]'
          }`}>
            <p className="font-semibold text-xs uppercase tracking-[1px] mb-1">
              {testResult.status === 'ok' ? '✓ 连接成功' : '✗ 连接失败'}
            </p>
            <p className="text-xs opacity-80">{testResult.message}</p>
          </div>
        )}

        {/* 保存提示 */}
        {saveMsg && (
          <div className="p-3 rounded-lg border border-[#22c55e]/30 bg-[#22c55e]/5 text-[#22c55e] text-xs text-center">
            {saveMsg}
          </div>
        )}
      </div>
    </main>
  );
}
