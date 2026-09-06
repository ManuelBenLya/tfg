import api from './api';

export const loginAPI = async (email: string, password: string) => {
  // OAuth2 requiere application/x-www-form-urlencoded con campo "username"
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await api.post('/usuarios/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  return response.data;
};

export const getMeAPI = async (token?: string) => {
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
  const response = await api.get('/usuarios/me', { headers });
  return response.data;
};

export const getEmpleados = async () => {
  const response = await api.get('/usuarios/empleados');
  return response.data;
};

export const crearEmpleado = async (data: { email: string; password: string; rol: string }) => {
  const response = await api.post('/usuarios/empleados', data);
  return response.data;
};

export const eliminarEmpleado = async (empleadoId: string) => {
  const response = await api.delete(`/usuarios/empleados/${empleadoId}`);
  return response.data;
};

export const actualizarAjustes = async (data: {
  discord_webhook?: string;
  slack_webhook?: string;
  recibir_alertas_email?: boolean;
}) => {
  const response = await api.put('/usuarios/ajustes', data);
  return response.data;
};