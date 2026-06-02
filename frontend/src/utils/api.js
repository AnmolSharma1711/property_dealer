import axios from 'axios';

// Determine API base URL based on environment
const getApiBaseUrl = () => {
  // If explicitly set via environment variable (dev)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // In production on Render, infer from current domain
  // If on broker-frontend.onrender.com, backend is on broker-backend.onrender.com
  if (typeof window !== 'undefined' && window.location.hostname.includes('onrender.com')) {
    const domain = window.location.hostname;
    const backendUrl = domain.replace('broker-frontend', 'broker-backend');
    return `https://${backendUrl}/api`;
  }
  
  // In development, use localhost
  return 'http://localhost:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
export { API_BASE_URL };
