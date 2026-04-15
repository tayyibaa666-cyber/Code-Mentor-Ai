import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, TerminalSquare, FileText, CheckCircle, XCircle } from 'lucide-react';
import { sendChat, generateQuiz, getFileUrl } from '../services/api';

const ChatInterface = ({ skillLevel, sessionId, messages, setMessages }) => {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showQuizPrompt, setShowQuizPrompt] = useState(false);
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, showQuizPrompt]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input, skill: skillLevel };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);
    setShowQuizPrompt(false);

    const { data, error } = await sendChat(input, skillLevel, sessionId);
    setIsTyping(false);

    if (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: `**Error:** ${error}` }]);
      return;
    }

    const assistantMsg = {
      role: 'assistant',
      content: data.answer || "No response received",
      skill: data.detected_difficulty || data.skill || skillLevel
    };
    
    setMessages(prev => [...prev, assistantMsg]);

    if (data.quiz_prompt) {
      setShowQuizPrompt(true);
    }
  };

  const handleGenerateQuiz = async () => {
    setShowQuizPrompt(false);
    setIsGeneratingQuiz(true);
    
    const { data, error } = await generateQuiz(sessionId, 5);
    setIsGeneratingQuiz(false);

    if (error) {
       setMessages(prev => [...prev, { role: 'assistant', content: `**Quiz Generation Error:** ${error}` }]);
       return;
    }

    // Prepare quiz message
    const quizTitle = data.quiz_title || 'Programming Quiz';
    const numQuestions = data.questions?.length || 0;
    
    const quizMessage = {
       role: 'assistant',
       type: 'quiz',
       content: `📝 I've generated a quiz for you: **${quizTitle}** (${numQuestions} questions). Review your questions below and download the DOCX file!`,
       quizData: data
    };

    setMessages(prev => [...prev, quizMessage]);
  };

  return (
    <main className="main-content">
      <header className="chat-header">
        <TerminalSquare size={28} color="var(--accent-primary)" style={{ marginRight: '1rem' }} />
        <h1 style={{ fontSize: '1.25rem', margin: 0 }}>Code Mentor AI</h1>
      </header>

      <div className="chat-container">
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', marginTop: '20vh', color: 'var(--text-secondary)' }}>
            <h2 style={{ color: 'var(--text-primary)', marginBottom: '1rem', background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', display: 'inline-block' }}>Your Friendly Programming Assistant</h2>
            <p>Ask me anything about coding! I can explain concepts, find bugs, or generate code snippets.</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="avatar">
               {msg.role === 'user' ? 'U' : 'AI'}
            </div>
            <div className="message-card">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
              
              {msg.skill && (
                 <div style={{ fontSize: '0.7rem', opacity: 0.7, marginTop: '0.5rem', textAlign: 'right' }}>
                   Level: {msg.skill}
                 </div>
              )}

              {/* Quiz specific rendering inside message */}
              {msg.type === 'quiz' && msg.quizData && (
                <div className="quiz-block">
                   <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <FileText size={18} color="var(--accent-primary)"/> 
                      {msg.quizData.quiz_title || 'Quiz'}
                   </h3>
                   <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                      {msg.quizData.docx_student_filename && (
                        <a href={getFileUrl(msg.quizData.docx_student_filename)} target="_blank" rel="noreferrer" style={{ textDecoration: 'none' }}>
                            <button className="btn btn-primary" style={{ padding: '0.5rem 1rem' }}>📄 Download Quiz Student Version (DOCX)</button>
                        </a>
                      )}
                      {msg.quizData.docx_answers_filename && (
                        <a href={getFileUrl(msg.quizData.docx_answers_filename)} target="_blank" rel="noreferrer" style={{ textDecoration: 'none' }}>
                            <button className="btn" style={{ padding: '0.5rem 1rem' }}>📄 Download Answer Key (DOCX)</button>
                        </a>
                      )}
                   </div>
                   
                   <details style={{ marginTop: '1rem' }}>
                      <summary style={{ cursor: 'pointer', color: 'var(--text-secondary)' }}>Preview Questions</summary>
                      <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                          {msg.quizData.questions?.map((q, i) => (
                              <div key={i} style={{ background: 'var(--bg-main)', padding: '1rem', borderRadius: '4px' }}>
                                 <strong>Q{i+1}: </strong> {q.question}
                                 <br/><br/>
                                 <span style={{ color: 'var(--success)', fontSize: '0.9rem' }}>Answer: {q.correct_answer}</span>
                              </div>
                          ))}
                      </div>
                   </details>
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
           <div className="message assistant">
             <div className="avatar">AI</div>
             <div className="message-card" style={{ padding: '0.8rem 1.25rem' }}>
                <span style={{ animation: 'pulse 1s infinite' }}>Thinking...</span>
             </div>
           </div>
        )}

        {isGeneratingQuiz && (
            <div className="message assistant">
             <div className="avatar">AI</div>
             <div className="message-card" style={{ padding: '0.8rem 1.25rem' }}>
                <span style={{ animation: 'pulse 1s infinite' }}>Generating quiz...</span>
             </div>
           </div>
        )}

        {showQuizPrompt && (
          <div className="quiz-prompt">
             <div className="avatar" style={{ background: 'var(--warning)', color: '#000' }}>💡</div>
             <div className="message-card" style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid var(--warning)' }}>
                 <p style={{ margin: '0 0 1rem 0' }}>Would you like to take a quick quiz based on our conversation?</p>
                 <div style={{ display: 'flex', gap: '1rem' }}>
                    <button className="btn btn-primary" onClick={handleGenerateQuiz}>
                        <CheckCircle size={16}/> Yes, generate quiz
                    </button>
                    <button className="btn" onClick={() => setShowQuizPrompt(false)}>
                        <XCircle size={16}/> No, skip
                    </button>
                 </div>
             </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-wrapper">
        <form className="chat-input-form" onSubmit={handleSubmit}>
          <input 
            type="text" 
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me a programming question..."
            disabled={isTyping}
          />
          <button type="submit" className="send-btn" disabled={!input.trim() || isTyping}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </main>
  );
};

export default ChatInterface;
