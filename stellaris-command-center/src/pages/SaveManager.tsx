import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '@/api/client';
import type {
  WatcherStatus,
  SaveRecord,
  SaveUploadResponse,
  PlanetSummary,
  FleetSummary,
} from '@/api/types';

export default function SaveManager() {
  const [watcher, setWatcher] = useState<WatcherStatus | null>(null);
  const [history, setHistory] = useState<SaveRecord[]>([]);
  const [uploadResult, setUploadResult] = useState<SaveUploadResponse | null>(null);
  const [dirInput, setDirInput] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const fileRef = useRef<HTMLInputElement>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const [status, hist] = await Promise.all([
        api.getWatcherStatus(),
        api.getSaveHistory(10),
      ]);
      setWatcher(status);
      setHistory(hist);
      if (status.directory) setDirInput(status.directory);
    } catch {
      // 后端未启动时静默处理，UI 会自动显示未连接状态
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const handleStartWatcher = async () => {
    try {
      setError('');
      await api.startWatcher(dirInput);
      await fetchStatus();
    } catch { setError('启动监控失败，请检查目录路径'); }
  };

  const handleStopWatcher = async () => {
    try {
      await api.stopWatcher();
      await fetchStatus();
    } catch { setError('停止监控失败'); }
  };

  const handleUpload = async (file: File) => {
    if (!file.name.endsWith('.sav')) { setError('请选择 .sav 格式的存档文件'); return; }
    setUploading(true);
    setError('');
    try {
      const result = await api.uploadSave(file);
      setUploadResult(result);
      await fetchStatus();
    } catch { setError('上传失败'); }
    finally { setUploading(false); }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  if (loading) {
    return (
      <main className="flex-1 overflow-y-auto p-8 flex items-center justify-center">
        <p className="text-[#4b5563] text-sm animate-pulse">加载中...</p>
      </main>
    );
  }

  return (
    <main className="flex-1 overflow-y-auto p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between mb-1">
        <div>
          <h1 className="font-orbitron text-[22px] font-bold text-[#d4af37] tracking-[3px]"
            style={{ textShadow: '0 0 30px rgba(212,175,55,0.2)' }}>存档管理器</h1>
          <p className="text-xs text-[#4b5563] mt-0.5">
            管理《群星》游戏存档的自动监控与手动上传
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-700/50 rounded-lg px-4 py-2.5 text-xs text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        {/* 存档目录监控 */}
        <section className="bg-[#0d111f] border border-[hsl(222,28%,18%)] rounded-lg p-5">
          <h2 className="font-orbitron text-sm text-[#d4af37] tracking-[2px] mb-4">
            📂 存档目录监控
          </h2>
          <div className="flex items-center gap-2 mb-3">
            <span className={`inline-block w-2.5 h-2.5 rounded-full ${
              watcher?.running ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-gray-600'
            }`} />
            <span className="text-xs text-[#94a3b8] font-mono">
              {watcher?.running ? '● 监控中' : '○ 未启动'}
            </span>
          </div>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={dirInput}
              onChange={(e) => setDirInput(e.target.value)}
              placeholder="存档目录路径..."
              className="flex-1 bg-[#06080f] border border-[hsl(222,28%,18%)] rounded-md px-3 py-2 text-xs text-[#e2e8f0] font-mono focus:outline-none focus:border-[#8b6914]"
            />
            <button
              onClick={handleStartWatcher}
              disabled={watcher?.running}
              className="px-4 py-2 rounded-md text-xs font-mono font-semibold bg-[#1a3a1a] text-green-400 border border-green-700/50 hover:bg-[#1f4a1f] disabled:opacity-40 transition-colors"
            >
              启动
            </button>
            <button
              onClick={handleStopWatcher}
              disabled={!watcher?.running}
              className="px-4 py-2 rounded-md text-xs font-mono font-semibold bg-[#3a1a1a] text-red-400 border border-red-700/50 hover:bg-[#4a1f1f] disabled:opacity-40 transition-colors"
            >
              停止
            </button>
          </div>
          {watcher && (
            <div className="text-[10px] text-[#4b5563] font-mono space-y-0.5">
              {watcher.last_detection && <p>最后检测: {watcher.last_detection}</p>}
              {watcher.last_path && <p className="truncate">{watcher.last_path}</p>}
            </div>
          )}
        </section>

        {/* 手动上传 */}
        <section className="bg-[#0d111f] border border-[hsl(222,28%,18%)] rounded-lg p-5">
          <h2 className="font-orbitron text-sm text-[#d4af37] tracking-[2px] mb-4">
            📤 手动上传存档
          </h2>
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-[hsl(222,28%,25%)] rounded-lg p-6 text-center cursor-pointer hover:border-[#8b6914] transition-colors"
            onClick={() => fileRef.current?.click()}
          >
            {uploading ? (
              <p className="text-xs text-[#94a3b8] animate-pulse">解析中...</p>
            ) : (
              <>
                <p className="text-2xl mb-2">📁</p>
                <p className="text-xs text-[#94a3b8]">拖拽 .sav 文件到此处</p>
                <p className="text-[10px] text-[#4b5563] mt-1">或点击选择文件</p>
              </>
            )}
          </div>
          <input
            ref={fileRef}
            type="file"
            accept=".sav"
            className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUpload(f); }}
          />
          {/* 上传历史 */}
          {history.length > 0 && (
            <div className="mt-4">
              <p className="text-[10px] text-[#4b5563] font-mono mb-2">上传历史</p>
              <div className="space-y-1 max-h-[120px] overflow-y-auto">
                {history.slice(0, 5).map((r) => (
                  <div key={r.id} className="text-[10px] text-[#94a3b8] font-mono flex justify-between">
                    <span className="truncate">{r.save_name}</span>
                    <span className="text-[#4b5563] shrink-0 ml-2">{r.game_date}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </div>

      {/* 解析结果 */}
      {uploadResult && uploadResult.parsed && (
        <>
          <EmpireOverview result={uploadResult} />
          <PlanetTable planets={uploadResult.planets || []} />
          <FleetTable fleets={uploadResult.fleets || []} />
        </>
      )}
      {uploadResult && !uploadResult.parsed && (
        <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-4 text-xs text-red-400">
          解析失败: {uploadResult.error || '未知错误'}
        </div>
      )}
    </main>
  );
}

function EmpireOverview({ result }: { result: SaveUploadResponse }) {
  const e = result.empire;
  const r = result.resources;
  const p = result.planets || [];
  const totalPops = p.reduce((sum, pl) => sum + (pl.population || 0), 0);

  return (
    <section className="bg-[#0d111f] border border-[hsl(222,28%,18%)] rounded-lg p-5">
      <h2 className="font-orbitron text-sm text-[#d4af37] tracking-[2px] mb-4">
        📊 帝国数据概览
      </h2>
      <div className="grid grid-cols-4 gap-3">
        <Stat label="帝国名称" value={String(e.name || '?')} />
        <Stat label="游戏日期" value={String(e.date || '?')} />
        <Stat label="殖民星球" value={String(e.planet_count || p.length)} />
        <Stat label="总人口" value={String(e.population || totalPops)} />
        <Stat label="能量币" value={fmt(e.energy_credits || r.energy_credits)} />
        <Stat label="矿物" value={fmt(e.minerals || r.minerals)} />
        <Stat label="合金" value={fmt(e.alloys || r.alloys)} />
        <Stat label="舰队战力" value={fmt(e.fleet_power)} />
        <Stat label="稳定度" value={e.stability ? `${e.stability}%` : '?'} />
        <Stat label="已研究科技" value={String(e.researched_techs || result.technologies?.length || '?')} />
        <Stat label="舰船数量" value={String(e.total_ships || '?')} />
        <Stat label="战争状态" value={String(e.war_status || '?')} />
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-[#06080f] border border-[hsl(222,28%,12%)] rounded px-3 py-2.5">
      <p className="text-[9px] text-[#4b5563] font-mono mb-0.5">{label}</p>
      <p className="text-sm font-mono font-semibold text-[#e2e8f0]">{value}</p>
    </div>
  );
}

function PlanetTable({ planets }: { planets: PlanetSummary[] }) {
  if (!planets.length) return null;
  return (
    <section className="bg-[#0d111f] border border-[hsl(222,28%,18%)] rounded-lg p-5">
      <h2 className="font-orbitron text-sm text-[#d4af37] tracking-[2px] mb-4">
        🌍 星球一览 ({planets.length})
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-xs font-mono">
          <thead>
            <tr className="text-[#4b5563] border-b border-[hsl(222,28%,12%)]">
              <th className="text-left py-2 px-3">星球名</th>
              <th className="text-left py-2 px-3">类型</th>
              <th className="text-left py-2 px-3">定位</th>
              <th className="text-right py-2 px-3">人口</th>
              <th className="text-right py-2 px-3">稳定度</th>
            </tr>
          </thead>
          <tbody>
            {planets.map((p, i) => (
              <tr key={i} className="border-b border-[hsl(222,28%,6%)] text-[#94a3b8] hover:bg-white/[0.02]">
                <td className="py-2 px-3 text-[#e2e8f0]">{p.name}</td>
                <td className="py-2 px-3">{p.planet_class || '?'}</td>
                <td className="py-2 px-3">{p.designation || '未指定'}</td>
                <td className="py-2 px-3 text-right">{p.population}</td>
                <td className="py-2 px-3 text-right" style={{ color: p.stability >= 70 ? '#22c55e' : p.stability >= 40 ? '#f59e0b' : '#ef4444' }}>
                  {p.stability}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function FleetTable({ fleets }: { fleets: FleetSummary[] }) {
  if (!fleets.length) return null;
  return (
    <section className="bg-[#0d111f] border border-[hsl(222,28%,18%)] rounded-lg p-5">
      <h2 className="font-orbitron text-sm text-[#d4af37] tracking-[2px] mb-4">
        🚀 舰队一览 ({fleets.length})
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-xs font-mono">
          <thead>
            <tr className="text-[#4b5563] border-b border-[hsl(222,28%,12%)]">
              <th className="text-left py-2 px-3">舰队名</th>
              <th className="text-right py-2 px-3">舰船数</th>
              <th className="text-right py-2 px-3">战力</th>
              <th className="text-left py-2 px-3">位置</th>
            </tr>
          </thead>
          <tbody>
            {fleets.map((f, i) => (
              <tr key={i} className="border-b border-[hsl(222,28%,6%)] text-[#94a3b8] hover:bg-white/[0.02]">
                <td className="py-2 px-3 text-[#e2e8f0]">{f.name}</td>
                <td className="py-2 px-3 text-right">{f.ship_count}</td>
                <td className="py-2 px-3 text-right text-[#f59e0b]">{f.fleet_power.toLocaleString()}</td>
                <td className="py-2 px-3 text-[#4b5563]">{f.location || '?'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function fmt(val: unknown): string {
  if (val === null || val === undefined) return '?';
  if (typeof val === 'number') return Number.isInteger(val) ? val.toLocaleString() : val.toFixed(1);
  return String(val);
}
