// Re-export from protocol for backwards compatibility
import { OrbState } from './protocol';
export type { OrbState };

export interface TaskProgress {
  step: number;
  total_steps?: number;
  thought: string;
  action: Record<string, any>;
  expect: string;
}

export interface ApprovalRequest {
  tier: number;
  nonce: string;
  summary: string;
  window: string;
  element?: string;
  thought?: string;
}

export interface TaskStatus {
  id: string;
  goal: string;
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled';
  steps: number;
  summary: string;
  error?: string;
  metrics?: Record<string, any>;
}

export interface SystemCapabilities {
  version: string;
  platform: {
    os: string;
    is_windows_native: boolean;
    python_version: string;
  };
  perception: Record<string, any>;
  execution: Record<string, any>;
  memory_architecture: Record<string, any>;
}

