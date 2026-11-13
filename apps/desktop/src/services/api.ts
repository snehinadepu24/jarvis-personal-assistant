import { API_BASE_URL } from '../types/protocol';

const API_BASE = API_BASE_URL;

export async function fetchCapabilities() {
  const res = await fetch(`${API_BASE}/capabilities`);
  return res.json();
}

export async function submitTaskHttp(goal: string, plannerMode: string = 'auto') {
  const res = await fetch(`${API_BASE}/task/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal, planner_mode: plannerMode }),
  });
  return res.json();
}

export async function fetchTaskStatus(taskId: string) {
  const res = await fetch(`${API_BASE}/task/status/${taskId}`);
  return res.json();
}

export async function cancelTaskHttp(taskId: string) {
  const res = await fetch(`${API_BASE}/task/cancel/${taskId}`, { method: 'POST' });
  return res.json();
}

export async function synthesizeSpeechHttp(text: string, voice: string = 'alba'): Promise<Blob> {
  const res = await fetch(`${API_BASE}/tts/speech`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, voice }),
  });
  return res.blob();
}

export async function transcribeAudioHttp(audioBlob: Blob): Promise<{ text: string }> {
  const formData = new FormData();
  formData.append('file', audioBlob, 'recording.wav');
  const res = await fetch(`${API_BASE}/stt/transcribe`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

