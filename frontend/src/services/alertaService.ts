import api from './api';

export interface AlertaBackend {
  id: number;
  servidor_id: string;
  mensaje: string;
  leida: boolean;
  tiempo: string;
}

export const getAlertasPendientes = async (): Promise<AlertaBackend[]> => {
  const response = await api.get<AlertaBackend[]>('/alertas/pendientes');
  return response.data;
};

export const marcarAlertaLeida = async (alertaId: number): Promise<void> => {
  await api.patch(`/alertas/${alertaId}/marcar-leida`);
};
