import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach token from localStorage (if present) to Authorization header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    if (token) {
      config.headers = config.headers || {};
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Hotels API
export const hotelService = {
  getAllHotels: async () => {
    const response = await api.get('/hotels');
    return response.data;
  },
  getHotelById: async (id) => {
    const response = await api.get(`/hotels/${id}`);
    return response.data;
  },
};

// Reviews API
export const reviewService = {
  createReview: async (reviewData) => {
    const response = await api.post('/reviews', reviewData);
    return response.data;
  },
};

// Sentiment Analysis API
export const sentimentService = {
  analyzeSentiment: async (text) => {
    const response = await api.post('/analyze', { text });
    return response.data;
  },
};

// Summarization API
export const summarizationService = {
  summarizeReviews: async (hotelId, options = {}) => {
    const requestData = {
      hotel_id: hotelId,
      max_length: options.maxLength || 100,
      min_length: options.minLength || 20,
    };
    const response = await api.post('/summarize', requestData);
    return response.data;
  },
};

// Auth API (full)
export const authService = {
  register: async (username, password, email) => {
    const response = await api.post('/register', { username, password, email });
    return response.data;
  },

  login: async (username, password) => {
    const response = await api.post('/login', { username, password });
    if (response?.data?.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      // try to fetch /me to stash username if backend provides it
      try {
        const me = await api.get('/me');
        if (me?.data?.username) {
          localStorage.setItem('username', me.data.username);
        }
      } catch (err) {
        // ignore if /me fails for any reason
        console.warn('Could not fetch /me after login', err);
      }
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
  },

  getToken: () => localStorage.getItem('access_token'),
  getUsername: () => localStorage.getItem('username') || null,

  me: async () => {
    const response = await api.get('/me');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/me', profileData);
    return response.data;
  },

  requestPasswordReset: async (usernameOrEmail) => {
    const response = await api.post('/request-password-reset', { username_or_email: usernameOrEmail });
    return response.data;
  },

  resetPassword: async (token, newPassword) => {
    const response = await api.post('/reset-password', { token, new_password: newPassword });
    return response.data;
  },

  verifyEmail: async (token) => {
    const response = await api.get('/verify-email', { params: { token } });
    return response.data;
  },
};

export default api;