import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

export const checkConnection = async () => {
  try {
    const res = await api.get('/');
    return res.status === 200;
  } catch {
    return false;
  }
};

export const getStats = async () => {
  try {
    const res = await api.get('/stats');
    return { data: res.data };
  } catch (err) {
    return { error: err.message };
  }
};

export const uploadFiles = async (files) => {
  try {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    const res = await api.post('/video/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return { data: res.data };
  } catch (err) {
    return { error: err.response?.data?.detail || err.message };
  }
};

export const sendChat = async (question, skill, sessionId) => {
  try {
    // API expects form data per main.py Form() inputs in streamlt_app.py
    const formData = new FormData();
    formData.append('question', question);
    formData.append('skill', skill);
    formData.append('session_id', sessionId);
    
    const res = await api.post('/video/chat', formData);
    return { data: res.data };
  } catch (err) {
    return { error: err.response?.data?.detail || err.message };
  }
};

export const clearChat = async (sessionId) => {
  try {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    const res = await api.post('/video/chat/clear', formData);
    return { data: res.data };
  } catch (err) {
    return { error: err.message };
  }
};

export const generateQuiz = async (sessionId, numQuestions = 5) => {
  try {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('num_questions', numQuestions);
    const res = await api.post('/video/chat/generate-quiz', formData);
    return { data: res.data };
  } catch (err) {
    return { error: err.response?.data?.detail || err.message };
  }
};

export const getFileUrl = (filename) => `${API_BASE_URL}/public/quizzes/${filename}`;
