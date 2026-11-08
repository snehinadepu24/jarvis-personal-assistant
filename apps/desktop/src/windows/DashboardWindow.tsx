import React, { useState, useEffect } from 'react';
import { useJarvisStore } from '../stores/jarvisStore';
import { wsService } from '../services/websocket';
import { fetchCapabilities } from '../services/api';
import {
  Play,
  Square,
  Activity,
  History,
  Cpu,
  Shield,
  Layers,
  Sparkles,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowRight,
  Terminal,
} from 'lucide-react';

export const DashboardWindow: React.FC = () => {
  const { isConnected, activeTask, progress, history, statusText } = useJarvisStore();
  const [goalInput, setGoalInput] = useState('');
  const [capabilities, setCapabilities] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'monitor' | 'history' | 'capabilities'>('monitor');

  useEffect(() => {
    fetchCapabilities().then(setCapabilities).catch(console.warn);
  }, []);

  const handleRunGoal = (goalToRun?: string) => {
    const target = goalToRun || goalInput;
    if (!target.trim()) return;
    wsService.submitTask(target.trim());
    setGoalInput('');
  };

  const quickTasks = [
    'Open Notepad and write Hello from JARVIS.',
    'Inspect active foreground window accessibility controls.',
    'Toggle Windows Bluetooth setting.',
    'Check system audio volume and mute status.',
  ];

  return (
    <div className="w-full h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans select-none">
      {/* Top Header */}
      <header className="px-6 py-4 border-b border-zinc-800/80 bg-zinc-900/40 flex items-center justify-between backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center font-bold text-white shadow-lg shadow-purple-500/20">
            J
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-wide text-zinc-100">JARVIS Desktop Monitor</h1>
            <p className="text-[11px] text-zinc-400">Autonomous UIA Desktop Assistant & Engine</p>
          </div>
        </div>

        {/* Status Pill & Navigation Tabs */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1 bg-zinc-900 border border-zinc-800 rounded-full text-xs">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-red-500 animate-pulse'}`} />
            <span className="text-zinc-300">{isConnected ? 'Engine Online' : 'Connecting...'}</span>
          </div>

          <div className="flex bg-zinc-900 border border-zinc-800 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => setActiveTab('monitor')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'monitor' ? 'bg-purple-600 text-white font-medium' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Monitor
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'history' ? 'bg-purple-600 text-white font-medium' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              History
            </button>
            <button
              onClick={() => setActiveTab('capabilities')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'capabilities' ? 'bg-purple-600 text-white font-medium' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Capabilities
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
        {activeTab === 'monitor' && (
          <>
            {/* Task Input Section */}
            <section className="bg-zinc-900/60 border border-zinc-800/80 rounded-2xl p-4 shadow-xl backdrop-blur-md">
              <label className="block text-xs font-medium text-zinc-400 mb-2">
                Submit Autonomous Desktop Task
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={goalInput}
                  onChange={(e) => setGoalInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleRunGoal()}
                  placeholder="e.g. Open Notepad and write Hello from JARVIS."
                  className="flex-1 bg-zinc-950/80 border border-zinc-800 rounded-xl px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-purple-500/80 transition-colors"
                />
                {activeTask ? (
                  <button
                    onClick={() => wsService.cancelTask(activeTask.id)}
                    className="px-5 py-2.5 bg-red-600 hover:bg-red-500 text-white font-medium rounded-xl text-sm flex items-center gap-2 transition-colors cursor-pointer shadow-lg shadow-red-600/20"
                  >
                    <Square size={14} fill="currentColor" /> Cancel
                  </button>
                ) : (
                  <button
                    onClick={() => handleRunGoal()}
                    className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-medium rounded-xl text-sm flex items-center gap-2 transition-colors cursor-pointer shadow-lg shadow-purple-600/20"
                  >
                    <Play size={14} fill="currentColor" /> Execute
                  </button>
                )}
              </div>

              {/* Quick Prompt Badges */}
              <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-zinc-800/60">
                <span className="text-[11px] font-medium text-zinc-500 flex items-center gap-1">
                  <Sparkles size={12} /> Suggested:
                </span>
                {quickTasks.map((t, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleRunGoal(t)}
                    className="px-2.5 py-1 bg-zinc-800/70 hover:bg-zinc-700/80 border border-zinc-700/50 rounded-lg text-xs text-zinc-300 transition-colors cursor-pointer truncate max-w-[280px]"
                  >
                    {t}
                  </button>
                ))}
              </div>
            </section>

            {/* Active Task Live Monitor */}
            {activeTask ? (
              <section className="flex-1 bg-zinc-900/60 border border-purple-500/30 rounded-2xl p-5 shadow-2xl flex flex-col gap-4">
                <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
                  <div className="flex items-center gap-2">
                    <Activity className="text-purple-400 animate-pulse" size={18} />
                    <h2 className="text-sm font-semibold text-zinc-200">Task in Progress</h2>
                    <span className="text-xs text-zinc-500 font-mono">[{activeTask.id}]</span>
                  </div>
                  <span className="px-2.5 py-0.5 bg-purple-950/80 border border-purple-500/40 text-purple-300 rounded-full text-xs font-medium">
                    Step {progress?.step || 0}
                  </span>
                </div>

                <div className="bg-zinc-950/90 border border-zinc-800/80 rounded-xl p-4 flex flex-col gap-3 font-mono">
                  <div>
                    <span className="text-xs text-zinc-500 block uppercase tracking-wider font-sans mb-1">Goal</span>
                    <p className="text-sm text-zinc-100 font-sans">{activeTask.goal}</p>
                  </div>

                  {progress && (
                    <>
                      <div className="pt-2 border-t border-zinc-900">
                        <span className="text-xs text-purple-400 block uppercase tracking-wider font-sans mb-1">
                          Planner Thought
                        </span>
                        <p className="text-xs text-zinc-300 bg-purple-950/20 border-l-2 border-purple-500 p-2 rounded-r">
                          {progress.thought || '(Synthesizing action...)'}
                        </p>
                      </div>

                      <div className="pt-2 border-t border-zinc-900">
                        <span className="text-xs text-blue-400 block uppercase tracking-wider font-sans mb-1">
                          Dispatched Action
                        </span>
                        <pre className="text-[11px] text-zinc-400 bg-zinc-900/80 p-2 rounded overflow-x-auto">
                          {JSON.stringify(progress.action, null, 2)}
                        </pre>
                      </div>

                      {progress.expect && (
                        <div className="pt-2 border-t border-zinc-900">
                          <span className="text-xs text-emerald-400 block uppercase tracking-wider font-sans mb-1">
                            Expected Outcome
                          </span>
                          <p className="text-xs text-zinc-300">{progress.expect}</p>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </section>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-zinc-800/80 rounded-2xl p-8 text-center text-zinc-500">
                <Terminal size={36} className="mb-3 text-zinc-600" />
                <h3 className="text-sm font-medium text-zinc-400">Idle / Ready for Instructions</h3>
                <p className="text-xs text-zinc-600 mt-1 max-w-sm">
                  Enter a desktop task above or click the floating Orb to execute actions via UI Automation and direct connectors.
                </p>
              </div>
            )}
          </>
        )}

        {activeTab === 'history' && (
          <section className="flex flex-col gap-3">
            <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Completed Executions</h2>
            {history.length === 0 ? (
              <p className="text-xs text-zinc-600 italic">No tasks executed in this session yet.</p>
            ) : (
              history.map((h, i) => (
                <div key={i} className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-4 flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    {h.status === 'completed' ? (
                      <CheckCircle2 className="text-emerald-400 mt-0.5" size={16} />
                    ) : (
                      <XCircle className="text-red-400 mt-0.5" size={16} />
                    )}
                    <div>
                      <h4 className="text-sm font-medium text-zinc-200">{h.goal}</h4>
                      {h.summary && <p className="text-xs text-zinc-400 mt-1">{h.summary}</p>}
                      {h.error && <p className="text-xs text-red-400 mt-1">{h.error}</p>}
                    </div>
                  </div>
                  <span className="text-xs text-zinc-500 font-mono">Steps: {h.steps}</span>
                </div>
              ))
            )}
          </section>
        )}

        {activeTab === 'capabilities' && capabilities && (
          <section className="flex flex-col gap-4">
            <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Engine Architecture & Capabilities</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-4">
                <h3 className="text-xs font-medium text-purple-400 flex items-center gap-2 mb-2">
                  <Layers size={14} /> Perception Hierarchy
                </h3>
                <ul className="text-xs text-zinc-400 space-y-1.5">
                  {capabilities.perception?.available_routes?.map((r: any) => (
                    <li key={r.route} className="flex items-center justify-between">
                      <span>Route {r.route}: {r.name}</span>
                      <span className="text-[11px] text-zinc-500">{r.description}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-4">
                <h3 className="text-xs font-medium text-indigo-400 flex items-center gap-2 mb-2">
                  <Cpu size={14} /> Unified 5-Tier Memory
                </h3>
                <ul className="text-xs text-zinc-400 space-y-1.5">
                  {capabilities.memory_architecture?.tiers?.map((t: any) => (
                    <li key={t.tier} className="flex items-center justify-between">
                      <span>Tier {t.tier}: {t.name}</span>
                      <span className="text-[11px] text-zinc-500">{t.description}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
};

