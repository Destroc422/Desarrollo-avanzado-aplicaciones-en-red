import axios from 'axios';

export const AUTH_UNAUTHORIZED_EVENT = 'cocktail-api:unauthorized';
const configuredApiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const API_BASE_URL = configuredApiUrl.trim().replace(/\/+$/, '').replace(/\/api\/v1$/, '');

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  withCredentials: true,
  headers: { Accept: 'application/json' },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      window.dispatchEvent(new Event(AUTH_UNAUTHORIZED_EVENT));
    }
    return Promise.reject(error);
  },
);

export const getApiErrorMessage = (error, fallback = 'No fue posible comunicarse con el servidor.') => {
  const detail = error?.response?.data?.detail || error?.response?.data?.message;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.message || item.msg).filter(Boolean).join('. ') || fallback;
  }
  return typeof detail === 'string' ? detail : fallback;
};

export default api;
