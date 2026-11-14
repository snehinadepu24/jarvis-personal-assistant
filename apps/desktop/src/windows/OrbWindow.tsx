import React, { useState } from 'react';
import { ParticlesOrb } from '../components/orb/particles-orb';
import { useJarvisStore, setJarvisState } from '../stores/jarvisStore';
import { wsService } from '../services/websocket';
import { Mic, Terminal, Square, Check, X, ShieldAlert, ExternalLink, GripVertical, XCircle, Eye, EyeOff } from 'lucide-react';
import { invoke } from '@tauri-apps/api/core';

// Helper function to convert AudioBuffer to WAV format
const audioBufferToWav = async (audioBuffer: AudioBuffer): Promise<Blob> => {
  const numberOfChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const format = 1; // PCM
  const bitDepth = 16;

  const length = audioBuffer.length * numberOfChannels * 2;
  const buffer = new ArrayBuffer(44 + length);
  const view = new DataView(buffer);

  // Write WAV header
  const writeString = (offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  writeString(0, 'RIFF');
  view.setUint32(4, 36 + length, true);
  writeString(8, 'WAVE');
  writeString(12, 'fmt ');
  view.setUint32(16, 16, true); // fmt chunk size
  view.setUint16(20, format, true);
  view.setUint16(22, numberOfChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * numberOfChannels * bitDepth / 8, true);
  view.setUint16(32, numberOfChannels * bitDepth / 8, true);
  view.setUint16(34, bitDepth, true);
  writeString(36, 'data');
  view.setUint32(40, length, true);

  // Write audio data
  const channels = [];
  for (let i = 0; i < numberOfChannels; i++) {
    channels.push(audioBuffer.getChannelData(i));
  }

  let offset = 44;
  for (let i = 0; i < audioBuffer.length; i++) {
    for (let channel = 0; channel < numberOfChannels; channel++) {
      const sample = Math.max(-1, Math.min(1, channels[channel][i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
      offset += 2;
    }
  }

  return new Blob([buffer], { type: 'audio/wav' });
};

// TTS helper function for speaking responses
const speakTextResponse = async (text: string, voice: string = 'alba'): Promise<void> => {
  try {
    console.log('[TTS] Generating speech for:', text);
    const response = await fetch('http://127.0.0.1:8000/api/tts/speech', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice, format: 'wav' }),
    });
    
    if (!response.ok) {
      console.error('[TTS] Failed to generate speech:', response.statusText);
      return;
    }
    
    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    
    return new Promise((resolve, reject) => {
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        console.log('[TTS] Speech playback completed');
        resolve();
      };
      
      audio.onerror = (err) => {
        console.error('[TTS] Audio playback error:', err);
        URL.revokeObjectURL(audioUrl);
        reject(err);
      };
      
      audio.play().catch(reject);
      console.log('[TTS] Playing speech audio');
    });
  } catch (error) {
    console.error('[TTS] Error in speakText:', error);
  }
};

export const OrbWindow: React.FC = () => {
  const { orbState, isConnected, statusText, activeTask, progress, approval, backgroundMode } = useJarvisStore();
  const [showInput, setShowInput] = useState(false);
  const [inputGoal, setInputGoal] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  const handleOrbClick = () => {
    if (approval) {
      return;
    }
    if (activeTask) {
      wsService.cancelTask(activeTask.id);
      return;
    }
    // Clicking orb now starts voice input instead of text input
    toggleVoiceInput();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputGoal.trim()) return;
    wsService.submitTask(inputGoal.trim(), 'auto', 'state_machine', backgroundMode);
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

  const handleClose = async () => {
    try {
      await invoke('close_orb');
    } catch (error) {
      console.error('Failed to close orb:', error);
    }
  };

  const startVoiceInput = async () => {
    try {
      console.log('[Voice] Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('[Voice] Microphone access granted');
      
      const recorder = new MediaRecorder(stream);
      const audioChunks: Blob[] = [];

      // Add audio level visualization
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      let animationId: number;
      
      // Visualize audio levels
      const updateAudioLevel = () => {
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        const normalizedLevel = Math.min(average / 128, 1); // 0 to 1
        
        // Update orb based on audio level
        if (normalizedLevel > 0.1) {
          console.log('[Voice] Audio level:', normalizedLevel.toFixed(2));
          setJarvisState({ 
            orbState: 'listening', 
            statusText: `🎤 ${Math.round(normalizedLevel * 100)}%` 
          });
        }
        
        animationId = requestAnimationFrame(updateAudioLevel);
      };
      updateAudioLevel();

      recorder.ondataavailable = (event) => {
        console.log('[Voice] Audio data available:', event.data.size, 'bytes');
        audioChunks.push(event.data);
      };

      recorder.onstop = async () => {
        cancelAnimationFrame(animationId);
        audioContext.close();
        
        console.log('[Voice] Recording stopped. Total chunks:', audioChunks.length);
        
        if (audioChunks.length === 0) {
          console.error('[Voice] No audio data captured!');
          setJarvisState({ orbState: 'error', statusText: 'No audio captured' });
          setTimeout(() => setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' }), 2000);
          stream.getTracks().forEach(track => track.stop());
          setIsListening(false);
          return;
        }
        
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        console.log('[Voice] Audio blob size:', audioBlob.size, 'bytes');
        console.log('[Voice] Audio blob type:', audioBlob.type);
        
        if (audioBlob.size < 1000) {
          console.warn('[Voice] Audio too short (<1KB), likely silence');
          setJarvisState({ orbState: 'error', statusText: 'Recording too short' });
          setTimeout(() => setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' }), 2000);
          stream.getTracks().forEach(track => track.stop());
          setIsListening(false);
          return;
        }
        
        setJarvisState({ orbState: 'thinking', statusText: 'Processing...' });
        
        try {
          // Convert WebM to WAV using Web Audio API
          console.log('[Voice] Converting audio to WAV...');
          const arrayBuffer = await audioBlob.arrayBuffer();
          const newAudioContext = new AudioContext();
          const audioBuffer = await newAudioContext.decodeAudioData(arrayBuffer);
          
          console.log('[Voice] Audio duration:', audioBuffer.duration.toFixed(2), 'seconds');
          console.log('[Voice] Sample rate:', audioBuffer.sampleRate, 'Hz');
          console.log('[Voice] Channels:', audioBuffer.numberOfChannels);
          
          if (audioBuffer.duration < 0.5) {
            console.warn('[Voice] Audio duration too short (<0.5s)');
            setJarvisState({ orbState: 'error', statusText: 'Speak longer' });
            setTimeout(() => setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' }), 2000);
            stream.getTracks().forEach(track => track.stop());
            setIsListening(false);
            return;
          }
          
          // Convert to WAV format
          const wavBlob = await audioBufferToWav(audioBuffer);
          console.log('[Voice] WAV blob size:', wavBlob.size, 'bytes');
          console.log('[Voice] WAV blob type:', wavBlob.type);
          
          const formData = new FormData();
          formData.append('file', wavBlob, 'recording.wav');

          console.log('[Voice] Sending to STT endpoint: http://127.0.0.1:8000/api/stt/transcribe');
          console.log('[Voice] FormData contents:', {
            fileName: 'recording.wav',
            fileSize: wavBlob.size,
            fileType: wavBlob.type
          });
          
          const response = await fetch('http://127.0.0.1:8000/api/stt/transcribe', {
            method: 'POST',
            body: formData,
          });
          
          console.log('[Voice] STT response status:', response.status);
          console.log('[Voice] STT response headers:', Object.fromEntries(response.headers.entries()));
          
          if (response.ok) {
            const result = await response.json();
            console.log('[Voice] STT result:', JSON.stringify(result, null, 2));
            
            if (result.text && result.text.trim()) {
              console.log('[Voice] ✅ Transcription successful:', result.text);
              const userText = result.text.trim();
              
              // Simple intent classification: check if it's a task or conversational query
              const isTask = /^(open|launch|start|close|type|write|create|delete|search|find|go to|navigate|click|press|run|execute)/i.test(userText);
              
              if (isTask) {
                // Execute as a task
                console.log('[Voice] Detected TASK intent, submitting to task engine');
                wsService.submitTask(userText, 'auto', 'state_machine', backgroundMode);
                setJarvisState({ orbState: 'thinking', statusText: `Executing: ${userText}` });
              } else {
                // Conversational response via assistant API
                console.log('[Voice] Detected CONVERSATIONAL intent, calling assistant API');
                setJarvisState({ orbState: 'thinking', statusText: 'Thinking...' });
                
                try {
                  const assistantResponse = await fetch('http://127.0.0.1:8000/api/assistant/respond', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: userText }),
                  });
                  
                  if (assistantResponse.ok) {
                    const assistantResult = await assistantResponse.json();
                    console.log('[Assistant] Response:', assistantResult.text);
                    setJarvisState({ orbState: 'speaking', statusText: assistantResult.text });
                    
                    // Generate and play TTS for the response
                    await speakTextResponse(assistantResult.text);
                    
                    // Return to idle after speaking
                    setTimeout(() => {
                      setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' });
                    }, 1000);
                  } else {
                    console.error('[Assistant] API error:', assistantResponse.status);
                    setJarvisState({ orbState: 'error', statusText: 'Assistant unavailable' });
                    setTimeout(() => setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' }), 2000);
                  }
                } catch (error) {
                  console.error('[Assistant] Request failed:', error);
                  setJarvisState({ orbState: 'error', statusText: 'Assistant error' });
                  setTimeout(() => setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' }), 2000);
                }
              }
            } else {
              console.warn('[Voice] ⚠️ No text transcribed. Full result:', result);
              setJarvisState({ orbState: 'error', statusText: 'No speech detected' });
              setTimeout(() => setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' }), 2000);
            }
          } else {
            const errorText = await response.text();
            console.error('[Voice] ❌ STT error response:', response.status, errorText);
            setJarvisState({ orbState: 'error', statusText: 'Voice recognition failed' });
            setTimeout(() => setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' }), 2000);
          }
        } catch (error) {
          console.error('[Voice] ❌ Processing failed:', error);
          setJarvisState({ orbState: 'error', statusText: 'Audio processing failed' });
          setTimeout(() => setJarvisState({ orbState: 'idle', statusText: 'JARVIS Ready' }), 2000);
        } finally {
          stream.getTracks().forEach(track => track.stop());
          setIsListening(false);
        }
      };

      recorder.start(100); // Request data every 100ms
      setMediaRecorder(recorder);
      setIsListening(true);
      setJarvisState({ orbState: 'listening', statusText: 'Listening...' });
      console.log('[Voice] Recording started with 100ms timeslice');
    } catch (error) {
      console.error('Microphone access failed:', error);
      alert('Microphone access denied. Please enable microphone permissions.');
    }
  };

  const stopVoiceInput = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
  };

  const toggleVoiceInput = () => {
    if (isListening) {
      stopVoiceInput();
    } else {
      startVoiceInput();
    }
  };

  const toggleBackgroundMode = () => {
    setJarvisState({ backgroundMode: !backgroundMode });
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
      className="w-full h-full flex flex-col items-center justify-center p-3 select-none bg-transparent overflow-hidden relative"
    >
      {/* Draggable background overlay - covers entire window except interactive elements */}
      <div 
        data-tauri-drag-region
        className="absolute inset-0 z-0"
        style={{ cursor: 'move' }}
      />

      {/* Top Control Bar - Background Toggle, Close Button */}
      <div 
        className="absolute top-2 left-2 right-2 flex items-center justify-end z-50 p-2"
      >
        <div className="flex items-center gap-1.5">
          {/* Microphone Button */}
          <button
            onClick={toggleVoiceInput}
            disabled={activeTask !== null}
            className={`p-1.5 border backdrop-blur-md rounded-lg transition-all cursor-pointer ${
              isListening
                ? 'bg-red-600/90 border-red-500/50 text-white animate-pulse'
                : activeTask
                ? 'bg-zinc-900/50 border-zinc-700/50 text-zinc-600 cursor-not-allowed'
                : 'bg-zinc-900/80 hover:bg-emerald-600/80 border-zinc-700/50 hover:border-emerald-500/50 text-zinc-400 hover:text-white'
            }`}
            title={isListening ? 'Recording... Click to stop' : activeTask ? 'Finish current task first' : 'Click to speak (or click orb)'}
          >
            <Mic size={14} />
          </button>

          {/* Background Mode Toggle */}
          <button
            onClick={toggleBackgroundMode}
            className={`p-1.5 border backdrop-blur-md rounded-lg transition-all cursor-pointer ${
              backgroundMode
                ? 'bg-purple-600/90 border-purple-500/50 text-white'
                : 'bg-zinc-900/80 hover:bg-zinc-800/80 border-zinc-700/50 text-zinc-400'
            }`}
            title={backgroundMode ? 'Background mode ON - tasks run hidden' : 'Background mode OFF - tasks shown'}
          >
            {backgroundMode ? <EyeOff size={14} /> : <Eye size={14} />}
          </button>

          {/* Close Button */}
          <button
            onClick={handleClose}
            className="p-1.5 bg-zinc-900/80 hover:bg-red-600/80 border border-zinc-700/50 hover:border-red-500/50 rounded-lg backdrop-blur-md transition-all cursor-pointer"
            title="Close orb window"
          >
            <XCircle size={14} className="text-zinc-400 hover:text-white" />
          </button>
        </div>
      </div>

      {/* Approval Banner if waiting */}
      {approval && (
        <div className="absolute top-14 w-[92%] bg-amber-950/90 border border-amber-500/50 rounded-xl p-2.5 shadow-2xl backdrop-blur-md text-amber-200 z-50 animate-bounce">
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

      {/* Floating Particles Orb - Now activates voice on click */}
      <div
        onClick={handleOrbClick}
        className="cursor-pointer group flex flex-col items-center justify-center transition-transform hover:scale-105 active:scale-95 z-10 relative"
        title={
          approval 
            ? 'Approval required - respond above' 
            : activeTask 
            ? 'Click to cancel task' 
            : isListening
            ? 'Recording... Click to stop'
            : 'Click to speak your command'
        }
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
      <div className="mt-1 px-3 py-1 bg-zinc-900/80 border border-zinc-800/80 rounded-full shadow-lg backdrop-blur-md flex items-center gap-2 max-w-[220px] relative z-10">
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

      {/* Background Mode Indicator */}
      {backgroundMode && (
        <div className="mt-1 px-2 py-0.5 bg-purple-600/20 border border-purple-500/30 rounded-full backdrop-blur-md relative z-10">
          <span className="text-[10px] font-medium text-purple-300">Background Mode</span>
        </div>
      )}

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
