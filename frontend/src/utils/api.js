import axios from 'axios';

// Determine API base URL based on environment
const getApiBaseUrl = () => {
  // If explicitly set via environment variable (build time or Render env vars)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // In production on Render, detect the correct backend from frontend domain
  if (typeof window !== 'undefined' && window.location.hostname.includes('onrender.com')) {
    // Map known frontend domains to their backend domains
    const domain = window.location.hostname;
    
    // Handle property-dealer pattern (property-dealer-xxxxx.onrender.com)
    if (domain.includes('property-dealer-1')) {
      return 'https://property-dealer-gf4c.onrender.com/api';
    }
    
    // Fallback: try replacing digits pattern (property-dealer-xxxxx → property-dealer-yyyyy)
    // This is a generic fallback for other naming patterns
    return `https://property-dealer-gf4c.onrender.com/api`;
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
