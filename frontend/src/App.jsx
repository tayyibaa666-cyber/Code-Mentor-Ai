import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import { checkConnection } from './services/api';

function App() {
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [isConnected, setIsConnected] = useState(true);
  const [skillLevel, setSkillLevel] = useState('all');
  const [messages, setMessages] = useState([]);
  
  useEffect(() => {
    const initCheck = async () => {
      const ok = await checkConnection();
      setIsConnected(ok);
    };
    initCheck();
  }, []);

  if (!isConnected) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#ef4444' }}>
        <h2>⚠️ Cannot connect to API</h2>
        <p>Please make sure the FastAPI server is running at http://localhost:8000</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Sidebar 
        skillLevel={skillLevel} 
        setSkillLevel={setSkillLevel}
        sessionId={sessionId}
        setMessages={setMessages}
      />
      <ChatInterface 
        skillLevel={skillLevel}
        sessionId={sessionId}
        messages={messages}
        setMessages={setMessages}
      />
    </div>
  );
}

export default App;
