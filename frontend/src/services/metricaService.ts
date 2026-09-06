import api from './api';

export const getMetricas = async () => {
  // Hacemos un GET al endpoint de FastAPI que devuelve las métricas
  const response = await api.get('/metricas/');
  return response.data;
};