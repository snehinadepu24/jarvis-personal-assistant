import { useState, useEffect } from 'react';
import { wsService } from '../services/websocket';
import { ApprovalRequest, OrbState, TaskProgress, TaskStatus } from '../types/jarvis';

export interface JarvisState {
  orbState: OrbState;
  isConnected: boolean;
  activeTask: TaskStatus | null;
  progress: TaskProgress | null;
  approval: ApprovalRequest | null;
  history: TaskStatus[];
  statusText: string;
}

let globalState: JarvisState = {
  orbState: 'idle',
  isConnected: false,
  activeTask: null,
  progress: null,
  approval: null,
  history: [],
  statusText: 'JARVIS Ready',
};

const listeners = new Set<(state: JarvisState) => void>();

function notify() {
  listeners.forEach((listener) => listener({ ...globalState }));
}

export function setJarvisState(partial: Partial<JarvisState>) {
  globalState = { ...globalState, ...partial };
  notify();
}

// Wire up WebSocket events to global state
wsService.on('connection.open', () => {
  setJarvisState({ isConnected: true, statusText: 'Connected to JARVIS Engine' });
});

wsService.on('connection.close', () => {
  setJarvisState({ isConnected: false, orbState: 'idle', statusText: 'Disconnected (Reconnecting...)' });
});

wsService.on('system.ready', (data) => {
  setJarvisState({ isConnected: true, statusText: 'System Ready' });
});

wsService.on('task.accepted', (data) => {
  const task: TaskStatus = {
    id: data.task_id,
    goal: data.goal,
    status: 'running',
    steps: 0,
    summary: '',
  };
  setJarvisState({
    activeTask: task,
    orbState: 'thinking',
    statusText: `Planning: ${data.goal}`,
  });
});

wsService.on('task.started', (data) => {
  setJarvisState({
    orbState: 'thinking',
    statusText: `Executing: ${data.goal}`,
  });
});

wsService.on('task.progress', (data) => {
  const progress: TaskProgress = {
    step: data.step,
    thought: data.thought || '',
    action: data.action || {},
    expect: data.expect || '',
  };
  setJarvisState({
    progress,
    orbState: 'executing',
    statusText: data.thought ? `Step ${data.step}: ${data.thought}` : `Executing Step ${data.step}`,
  });
});

wsService.on('action.approval_required', (data) => {
  const approval: ApprovalRequest = {
    tier: data.tier,
    nonce: data.nonce,
    summary: data.summary,
    window: data.window,
    element: data.element,
    thought: data.thought,
  };
  setJarvisState({
    approval,
    orbState: 'waiting_approval',
    statusText: `Approval required (Tier ${data.tier})`,
  });
});

wsService.on('task.completed', (data) => {
  const current = globalState.activeTask;
  if (current) {
    current.status = 'completed';
    current.summary = data.summary;
    current.metrics = data.metrics;
    globalState.history.unshift(current);
  }
  setJarvisState({
    activeTask: null,
    progress: null,
    approval: null,
    orbState: 'speaking',
    statusText: data.summary ? `Done: ${data.summary}` : 'Task Completed',
  });
  // Return to idle after speech feedback
  setTimeout(() => {
    if (globalState.orbState === 'speaking') {
      setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' });
    }
  }, 4000);
});

wsService.on('task.failed', (data) => {
  const current = globalState.activeTask;
  if (current) {
    current.status = 'failed';
    current.error = data.error;
    globalState.history.unshift(current);
  }
  setJarvisState({
    activeTask: null,
    progress: null,
    approval: null,
    orbState: 'error',
    statusText: `Task Failed: ${data.error || 'Unknown error'}`,
  });
  setTimeout(() => {
    if (globalState.orbState === 'error') {
      setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' });
    }
  }, 5000);
});

wsService.on('task.cancelled', (data) => {
  setJarvisState({
    activeTask: null,
    progress: null,
    approval: null,
    orbState: 'idle',
    statusText: 'Task Cancelled',
  });
});

export function useJarvisStore(): JarvisState {
  const [state, setState] = useState<JarvisState>(globalState);

  useEffect(() => {
    listeners.add(setState);
    return () => {
      listeners.delete(setState);
    };
  }, []);

  return state;
}

