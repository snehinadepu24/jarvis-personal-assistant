import { ApprovalRequest, OrbState, TaskProgress, TaskStatus } from '../types/jarvis';

export type EventCallback = (data: any) => void;

class JarvisWebSocketService {
  private ws: WebSocket | null = null;
  private url: string = 'ws://127.0.0.1:8000/api/ws';
  private listeners: Map<string, Set<EventCallback>> = new Map();
  private isConnecting: boolean = false;
  private reconnectTimer: any = null;

  constructor() {
    this.connect();
  }

  public connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }
    this.isConnecting = true;
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.isConnecting = false;
        console.log('[JARVIS WS] Connected to Python Engine backend.');
        this.emit('connection.open', { connected: true });
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const evType = payload.event;
          const data = payload.data || {};
          this.emit(evType, data);
        } catch (e) {
          console.error('[JARVIS WS] Parse error:', e);
        }
      };

      this.ws.onclose = () => {
        this.isConnecting = false;
        this.emit('connection.close', { connected: false });
        this.scheduleReconnect();
      };

      this.ws.onerror = (err) => {
        console.warn('[JARVIS WS] Connection error:', err);
        this.ws?.close();
      };
    } catch (e) {
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, 2000);
  }

  public on(event: string, callback: EventCallback): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  public emit(event: string, data: any): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach((cb) => {
        try {
          cb(data);
        } catch (err) {
          console.error(`[JARVIS WS] Error in listener for ${event}:`, err);
        }
      });
    }
  }

  public sendCommand(command: string, data: Record<string, any> = {}): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const payload = JSON.stringify({ command, data });
      this.ws.send(payload);
    } else {
      console.warn('[JARVIS WS] Cannot send command, WebSocket is not open:', command);
    }
  }

  public submitTask(goal: string, plannerMode: string = 'auto', engine: string = 'state_machine'): void {
    this.sendCommand('task.submit', { goal, planner_mode: plannerMode, engine });
  }

  public cancelTask(taskId?: string): void {
    this.sendCommand('task.cancel', { task_id: taskId });
  }

  public respondApproval(taskId: string, nonce: string, approved: boolean, reason: string = ''): void {
    this.sendCommand('approval.respond', {
      task_id: taskId,
      nonce,
      approved,
      reason,
    });
  }
}

export const wsService = new JarvisWebSocketService();

