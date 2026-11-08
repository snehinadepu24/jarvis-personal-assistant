import React, { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { HOME } from "@/constants/testIds";
import { ParticlesOrb } from "@/registry/orbe/particles-orb/particles-orb.tsx";
import { VoiceSettings } from "@/components/VoiceSettings";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [orbState, setOrbState] = useState("speaking");

  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log(response.data.message);
    } catch (e) {
      console.error(e, `errored out requesting / api`);
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  const handleOrbClick = () => {
    // Cycle states on click: idle -> listening -> thinking -> speaking -> idle
    const stateCycle = {
      idle: "listening",
      listening: "thinking",
      thinking: "speaking",
      speaking: "idle",
      connecting: "idle",
      error: "idle",
      disabled: "idle",
    };
    setOrbState((prev) => stateCycle[prev] || "idle");
  };

  return (
    // The marker attribute below lets the platform probe detect the stock splash — remove it with this page
    <div data-emergent-splash className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col justify-between p-6">
      <header className="App-header flex flex-col items-center justify-center max-w-xl mx-auto w-full pt-4">
        <a
          data-testid={HOME.emergentLink}
          className="App-link mb-4 opacity-80 hover:opacity-100 transition-opacity"
          href="https://emergent.sh"
          target="_blank"
          rel="noopener noreferrer"
        >
          <img
            src="https://avatars.githubusercontent.com/in/1201222?s=120&u=2686cf91179bbafbc7a71bfbc43004cf9ae1acea&v=4"
            alt="logo"
            className="w-12 h-12 rounded-full ring-2 ring-violet-500/30"
          />
        </a>

        {/* Particles Orb Component */}
        <div
          onClick={handleOrbClick}
          className="cursor-pointer group flex flex-col items-center justify-center my-4 transition-transform hover:scale-105 active:scale-95 select-none"
          title="Click to interact with the Assistant"
        >
          <ParticlesOrb
            state={orbState}
            size={168}
            speed={1}
            colorFrom="#f0abfc"
            colorTo="#818cf8"
          />
          <span className="text-xs font-medium text-zinc-400 mt-2 capitalize tracking-wide flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${orbState === 'listening' ? 'bg-emerald-400 animate-ping' : orbState === 'speaking' ? 'bg-indigo-400 animate-pulse' : orbState === 'thinking' ? 'bg-amber-400 animate-pulse' : 'bg-zinc-500'}`} />
            {orbState} • Click to toggle
          </span>
        </div>

        {/* Voice Control & 'Hey Jarvis' Wake Word Toggle */}
        <VoiceSettings orbState={orbState} setOrbState={setOrbState} />

        <p className="mt-4 text-xs text-zinc-500">
          JARVIS Voice Pipeline: Moonshine STT • Pocket TTS 7M • openWakeWord
        </p>
      </header>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
