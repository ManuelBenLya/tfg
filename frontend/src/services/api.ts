import axios from 'axios';

// Creamos la instancia base apuntando a tu FastAPI
const api = axios.create({
  baseURL: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api`, 
});

// Este "interceptor" se ejecuta antes de cada petición
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token'); // La misma clave que usaste en el login
    if (token) {
      // Si hay token, lo metemos en la cabecera de seguridad
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export default api;