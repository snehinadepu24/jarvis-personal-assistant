import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Mic, MicOff, Radio, Volume2, Sparkles } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export const VoiceSettings = ({ orbState, setOrbState }) => {
  const [wakewordEnabled, setWakewordEnabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [voiceError, setVoiceError] = useState('');
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const [voiceConfig, setVoiceConfig] = useState({
    stt_model: 'moonshine-small-streaming',
    tts_model: 'pocket-tts-7m-int8',
    tts_voice: 'alba',
    hotkey: '<ctrl_r>+<space>',
  });

  // Fetch initial config from backend
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await axios.get(`${BACKEND_URL}/api/voice/config`);
        if (res.data) {
          setWakewordEnabled(Boolean(res.data.wakeword_enabled));
          setVoiceConfig(res.data);
        }
      } catch (e) {
        // Fallback for standalone/offline preview
        console.debug('Voice config API offline, running in local preview mode:', e.message);
      }
    };
    fetchConfig();
  }, []);

  useEffect(() => {
    const handleHotkey = (event) => {
      if (event.ctrlKey && event.code === 'Space') {
        event.preventDefault();
        if (recording) {
          stopRecording();
        } else {
          void startRecording();
        }
      }
    };
    window.addEventListener('keydown', handleHotkey);
    return () => window.removeEventListener('keydown', handleHotkey);
  }, [recording]);

  const encodeWav = async (blob) => {
    const audioContext = new AudioContext();
    try {
      const decoded = await audioContext.decodeAudioData(await blob.arrayBuffer());
      const channel = decoded.getChannelData(0);
      const buffer = new ArrayBuffer(44 + channel.length * 2);
      const view = new DataView(buffer);
      const writeString = (offset, value) => {
        for (let i = 0; i < value.length; i += 1) {
          view.setUint8(offset + i, value.charCodeAt(i));
        }
      };
      writeString(0, 'RIFF');
      view.setUint32(4, 36 + channel.length * 2, true);
      writeString(8, 'WAVE');
      writeString(12, 'fmt ');
      view.setUint32(16, 16, true);
      view.setUint16(20, 1, true);
      view.setUint16(22, 1, true);
      view.setUint32(24, decoded.sampleRate, true);
      view.setUint32(28, decoded.sampleRate * 2, true);
      view.setUint16(32, 2, true);
      view.setUint16(34, 16, true);
      writeString(36, 'data');
      view.setUint32(40, channel.length * 2, true);
      for (let i = 0; i < channel.length; i += 1) {
        const sample = Math.max(-1, Math.min(1, channel[i]));
        view.setInt16(44 + i * 2, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
      }
      return new Blob([buffer], { type: 'audio/wav' });
    } finally {
      await audioContext.close();
    }
  };

  const startRecording = async () => {
    if (recording) return;
    setVoiceError('');
    setTranscript('');
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      setVoiceError('Microphone recording is not supported by this browser.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        setRecording(false);
        setOrbState('thinking');
        try {
          const wav = await encodeWav(new Blob(chunksRef.current, { type: recorder.mimeType }));
          const form = new FormData();
          form.append('file', wav, 'voice.wav');
          const result = await axios.post(`${BACKEND_URL}/api/stt/transcribe`, form);
          const text = result.data?.text?.trim() || '';
          setTranscript(text || 'I could not hear that clearly.');
          const assistant = text
            ? await axios.post(`${BACKEND_URL}/api/assistant/respond`, { text })
            : { data: { text: 'I could not hear that clearly. Please try again.' } };
          const responseText = assistant.data.text;
          setTranscript(text || responseText);
          const speech = await axios.post(
            `${BACKEND_URL}/api/tts/speech`,
            { text: responseText, voice: voiceConfig.tts_voice || 'alba', format: 'wav' },
            { responseType: 'blob' },
          );
          const audio = new Audio(URL.createObjectURL(speech.data));
          audio.onended = () => {
            URL.revokeObjectURL(audio.src);
            setOrbState('idle');
          };
          setOrbState('speaking');
          await audio.play();
        } catch (error) {
          console.error('Voice request failed:', error);
          setVoiceError('Voice request failed. Check that the backend is running.');
          setOrbState('error');
        }
      };
      recorder.start();
      mediaRecorderRef.current = recorder;
      setRecording(true);
      setOrbState('listening');
    } catch (error) {
      console.error('Microphone access failed:', error);
      setVoiceError('Microphone access was denied or unavailable.');
      setOrbState('error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }
  };

  const handleToggleWakeWord = async (checked) => {
    setLoading(true);
    setWakewordEnabled(checked);
    try {
      await axios.post(`${BACKEND_URL}/api/voice/config`, {
        wakeword_enabled: checked,
      });
    } catch (e) {
      console.debug('Could not sync wake word state to backend:', e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto my-4 p-5 rounded-2xl bg-zinc-900/80 border border-zinc-800 backdrop-blur-md shadow-2xl text-zinc-100 transition-all duration-300">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800/80">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-violet-600/20 text-violet-400">
            <Radio className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-100">Voice Control & Wake Word</h3>
            <p className="text-xs text-zinc-400">Hands-free detection & local neural speech</p>
          </div>
        </div>
        <Badge variant={wakewordEnabled ? "default" : "secondary"} className={`text-xs px-2.5 py-0.5 font-medium transition-colors ${wakewordEnabled ? "bg-emerald-600/30 text-emerald-300 border-emerald-500/30" : "bg-zinc-800 text-zinc-400"}`}>
          {wakewordEnabled ? "Always Listening" : "Push-to-Talk"}
        </Badge>
      </div>

      {/* Main Wake Word Toggle */}
      <div className="my-4 flex items-center justify-between p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800/60 hover:border-zinc-700/60 transition-colors">
        <div className="flex items-start gap-3">
          <div className={`mt-0.5 p-1.5 rounded-lg ${wakewordEnabled ? "bg-emerald-500/20 text-emerald-400" : "bg-zinc-800 text-zinc-400"}`}>
            {wakewordEnabled ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
          </div>
          <div>
            <label htmlFor="wakeword-switch" className="text-sm font-medium text-zinc-200 cursor-pointer">
              "Hey Jarvis" Wake Word
            </label>
            <p className="text-xs text-zinc-400 mt-0.5">
              {wakewordEnabled
                ? "Wake word mode is enabled"
                : `Push-to-talk active (${voiceConfig.hotkey || "Right Ctrl + Space"})`}
            </p>
          </div>
        </div>
        <Switch
          id="wakeword-switch"
          checked={wakewordEnabled}
          onCheckedChange={handleToggleWakeWord}
          disabled={loading}
          aria-label="Toggle 'Hey Jarvis' Wake Word"
        />
      </div>

      {/* Pipeline Specs Pills */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="p-2.5 rounded-lg bg-zinc-950/40 border border-zinc-800/40 flex items-center gap-2 text-zinc-300">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
          <div className="truncate">
            <span className="text-zinc-500 block text-[10px] uppercase font-bold tracking-wider">STT Engine</span>
            <span className="font-mono text-zinc-200">Moonshine 123M</span>
          </div>
        </div>
        <div className="p-2.5 rounded-lg bg-zinc-950/40 border border-zinc-800/40 flex items-center gap-2 text-zinc-300">
          <Volume2 className="w-3.5 h-3.5 text-pink-400 shrink-0" />
          <div className="truncate">
            <span className="text-zinc-500 block text-[10px] uppercase font-bold tracking-wider">TTS Engine</span>
            <span className="font-mono text-zinc-200">Pocket TTS 7M INT8</span>
          </div>
        </div>
      </div>

      {/* Interactive Test Button */}
      <div className="mt-4 pt-3 border-t border-zinc-800/60 flex items-center justify-between">
        <span className="text-xs text-zinc-400">
          Orb Status: <span className="font-semibold text-violet-300 capitalize">{orbState || 'idle'}</span>
        </span>
        <button
          onClick={recording ? stopRecording : startRecording}
          type="button"
          className="text-xs px-3 py-1.5 rounded-lg bg-violet-600/30 hover:bg-violet-600/50 text-violet-200 border border-violet-500/30 font-medium transition-all active:scale-95"
        >
          {recording ? 'Stop speaking' : 'Start speaking'}
        </button>
      </div>
      {transcript && <p className="mt-3 text-xs text-zinc-300">Heard: {transcript}</p>}
      {voiceError && <p className="mt-2 text-xs text-red-300">{voiceError}</p>}
    </div>
  );
};

export default VoiceSettings;
