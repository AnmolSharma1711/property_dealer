import axios from 'axios';

// Determine API base URL based on environment
const getApiBaseUrl = () => {
  let url;
  
  // If explicitly set via environment variable (build time)
  if (import.meta.env.VITE_API_URL) {
    url = import.meta.env.VITE_API_URL;
    console.log('Using VITE_API_URL:', url);
  } else if (typeof window !== 'undefined' && window.location.hostname.includes('onrender.com')) {
    // In production on Render static sites
    url = 'https://property-dealer-gf4c.onrender.com/api';
    console.log('Detected Render production, using:', url);
  } else {
    // In development, use localhost
    url = 'http://localhost:8000/api';
    console.log('Development mode, using:', url);
  }
  
  // Ensure the URL includes /api path
  if (!url.endsWith('/api') && !url.includes('/api/')) {
    url = url.endsWith('/') ? url + 'api' : url + '/api';
    console.log('Appended /api suffix, final URL:', url);
  }
  
  return url;
};

const API_BASE_URL = getApiBaseUrl();
console.log('API_BASE_URL final value:', API_BASE_URL);

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
