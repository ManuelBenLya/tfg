import api from './api';

export const getServidores = async () => {
  // Como ya tenemos el interceptor, no hace falta pasarle el token aquí
  const response = await api.get('/servidores/');
  return response.data;
};