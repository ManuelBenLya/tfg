import api from './api';

export const loginAPI = async (email: string, password: string) => {
  const formData = new URLSearchParams();
  // FastAPI espera "username", así que le pasamos el email aquí:
  formData.append('username', email);
  formData.append('password', password);

  // Hacemos el POST al endpoint que tienes en usuarios.py
  const response = await api.post('/usuarios/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  return response.data;
};