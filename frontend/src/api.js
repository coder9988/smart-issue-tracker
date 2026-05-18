import axios from "axios";
import { getToken } from "./auth";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? "http://localhost:8000/api/" : "/api/"),
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
