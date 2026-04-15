import React, { useState, useEffect } from 'react';
import { UploadCloud, File, RefreshCw, Trash2, Settings } from 'lucide-react';
import { getStats, uploadFiles, clearChat } from '../services/api';

const Sidebar = ({ skillLevel, setSkillLevel, sessionId, setMessages }) => {
  const [stats, setStats] = useState({ total_documents: 0, vector_dimension: 0 });
  const [uploadedFilesList, setUploadedFilesList] = useState([]);
  const [isUploading, setIsUploading] = useState(false);

  const fetchStats = async () => {
    const { data } = await getStats();
    if (data && !data.error) {
      setStats({
        total_documents: data.total_documents || 0,
        vector_dimension: data.vector_dimension || 0
      });
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    setIsUploading(true);
    const { data, error } = await uploadFiles(files);
    setIsUploading(false);

    if (error) {
      alert(`Error uploading: ${error}`);
    } else {
      setUploadedFilesList(prev => [...new Set([...prev, ...files.map(f => f.name)])]);
      fetchStats();
      // Reset input
      e.target.value = null;
    }
  };

  const handleClearChat = async () => {
    if (window.confirm("Are you sure you want to clear the chat history?")) {
      const { error } = await clearChat(sessionId);
      if (!error) {
        setMessages([]);
      }
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <Settings size={24} color="var(--accent-primary)" />
        <span>Settings</span>
      </div>

      <div className="sidebar-section">
        <label className="section-title">Skill Level</label>
        <select 
          className="select-input" 
          value={skillLevel} 
          onChange={(e) => setSkillLevel(e.target.value)}
        >
          <option value="all">All</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      <hr style={{ borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <div className="sidebar-section">
        <label className="section-title">Upload Files</label>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          Upload JSON, CSV, PDF, or TXT
        </p>
        <label className="file-upload-zone">
          <input 
            type="file" 
            multiple 
            accept=".json,.csv,.pdf,.txt" 
            style={{ display: 'none' }} 
            onChange={handleFileUpload}
          />
          <UploadCloud size={32} style={{ marginBottom: '0.5rem', color: 'var(--accent-primary)' }} />
          <div>{isUploading ? 'Uploading...' : 'Click to browse files'}</div>
        </label>
      </div>

      {uploadedFilesList.length > 0 && (
        <div className="sidebar-section">
          <label className="section-title">Uploaded Files</label>
          {uploadedFilesList.map((fname, i) => (
             <div key={i} className="uploaded-file" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-main)', padding: '0.5rem', borderRadius: '4px', fontSize: '0.85rem' }}>
                <File size={16} color="var(--accent-secondary)" />
               <span style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace:'nowrap'}}>{fname}</span>
             </div>
          ))}
        </div>
      )}

      <hr style={{ borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <div className="sidebar-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <label className="section-title">Statistics</label>
          <button className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem' }} onClick={fetchStats}>
            <RefreshCw size={14} />
          </button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '0.5rem' }}>
          <div style={{ background: 'var(--bg-main)', padding: '1rem', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.total_documents}</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>DOCUMENTS</div>
          </div>
          <div style={{ background: 'var(--bg-main)', padding: '1rem', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.vector_dimension}</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>DIMENSION</div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 'auto' }}>
        <button className="btn btn-danger" onClick={handleClearChat}>
          <Trash2 size={18} /> Clear Chat History
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
