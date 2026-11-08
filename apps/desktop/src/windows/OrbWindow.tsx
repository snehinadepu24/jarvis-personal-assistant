import React, { useState } from 'react';
import { ParticlesOrb } from '../components/orb/particles-orb';
import { useJarvisStore, setJarvisState } from '../stores/jarvisStore';
import { wsService } from '../services/websocket';
import { Mic, Terminal, Square, Check, X, ShieldAlert, ExternalLink } from 'lucide-react';

export const OrbWindow: React.FC = () => {
  const { orbState, isConnected, statusText, activeTask, progress, approval } = useJarvisStore();
  const [showInput, setShowInput] = useState(false);
  const [inputGoal, setInputGoal] = useState('');

  const handleOrbClick = () => {
    if (approval) {
      return;
    }
    if (activeTask) {
      wsService.cancelTask(activeTask.id);
      return;
    }
    setShowInput(!showInput);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputGoal.trim()) return;
    wsService.submitTask(inputGoal.trim());
    setInputGoal('');
    setShowInput(false);
  };

  const handleApprove = () => {
    if (approval && activeTask) {
      wsService.respondApproval(activeTask.id, approval.nonce, true);
    }
  };

  const handleDeny = () => {
    if (approval && activeTask) {
      wsService.respondApproval(activeTask.id, approval.nonce, false, 'User denied');
    }
  };

  const orbColorMap = {
    idle: { from: '#a855f7', to: '#6366f1' },
    listening: { from: '#10b981', to: '#06b6d4' },
    thinking: { from: '#f59e0b', to: '#ec4899' },
    executing: { from: '#3b82f6', to: '#8b5cf6' },
    speaking: { from: '#818cf8', to: '#f472b6' },
    error: { from: '#ef4444', to: '#f97316' },
    waiting_approval: { from: '#eab308', to: '#dc2626' },
  };

  const colors = orbColorMap[orbState] || orbColorMap.idle;

  return (
    <div
      data-tauri-drag-region
      className="w-full h-full flex flex-col items-center justify-center p-3 select-none bg-transparent overflow-hidden"
    >
      {/* Approval Banner if waiting */}
      {approval && (
        <div className="absolute top-2 w-[92%] bg-amber-950/90 border border-amber-500/50 rounded-xl p-2.5 shadow-2xl backdrop-blur-md text-amber-200 z-50 animate-bounce">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-400">
            <ShieldAlert size={14} /> Tier {approval.tier} Confirmation
          </div>
          <p className="text-[11px] text-zinc-300 mt-1 line-clamp-2">{approval.summary}</p>
          <div className="flex items-center justify-end gap-2 mt-2">
            <button
              onClick={handleDeny}
              className="px-2.5 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded text-xs flex items-center gap-1 cursor-pointer transition-colors"
            >
              <X size={12} /> Deny
            </button>
            <button
              onClick={handleApprove}
              className="px-2.5 py-1 bg-amber-500 hover:bg-amber-400 text-zinc-950 font-medium rounded text-xs flex items-center gap-1 cursor-pointer transition-colors"
            >
              <Check size={12} /> Approve ({approval.nonce})
            </button>
          </div>
        </div>
      )}

      {/* Floating Particles Orb */}
      <div
        onClick={handleOrbClick}
        className="cursor-pointer group flex flex-col items-center justify-center transition-transform hover:scale-105 active:scale-95"
        title={activeTask ? 'Click to stop active task' : 'Click to prompt JARVIS'}
      >
        <ParticlesOrb
          state={orbState as any}
          size={160}
          speed={1.1}
          colorFrom={colors.from}
          colorTo={colors.to}
        />
      </div>

      {/* Dynamic Status Capsule */}
      <div className="mt-1 px-3 py-1 bg-zinc-900/80 border border-zinc-800/80 rounded-full shadow-lg backdrop-blur-md flex items-center gap-2 max-w-[220px]">
        <span
          className={`w-2 h-2 rounded-full ${
            orbState === 'listening'
              ? 'bg-emerald-400 animate-ping'
              : orbState === 'executing'
              ? 'bg-blue-400 animate-pulse'
              : orbState === 'thinking'
              ? 'bg-amber-400 animate-pulse'
              : orbState === 'error'
              ? 'bg-red-500'
              : isConnected
              ? 'bg-purple-500'
              : 'bg-zinc-600'
          }`}
        />
        <span className="text-[11px] font-medium text-zinc-300 truncate">{statusText}</span>
      </div>

      {/* Inline Quick Task Input */}
      {showInput && !activeTask && (
        <form
          onSubmit={handleSubmit}
          className="absolute bottom-3 w-[90%] flex items-center gap-1.5 bg-zinc-900/95 border border-zinc-700/80 rounded-xl p-1.5 shadow-2xl backdrop-blur-xl z-40 animate-in fade-in zoom-in-95 duration-150"
        >
          <input
            type="text"
            value={inputGoal}
            onChange={(e) => setInputGoal(e.target.value)}
            placeholder="Type a task (e.g. Open Notepad...)"
            autoFocus
            className="flex-1 bg-transparent px-2 py-1 text-xs text-zinc-100 placeholder-zinc-500 outline-none"
          />
          <button
            type="submit"
            className="p-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs cursor-pointer transition-colors"
          >
            Run
          </button>
        </form>
      )}
    </div>
  );
};

