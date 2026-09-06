import api from './api';

export const getMetricas = async (rango: string = '1h', servidorId?: string) => {
  const params: Record<string, string> = { rango };
  if (servidorId && servidorId !== 'all') {
    params.servidor_id = servidorId;
  }
  const response = await api.get('/metricas/', { params });
  return response.data;
};