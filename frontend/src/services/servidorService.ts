import api from './api';

export interface Servidor {
  id: string;
  nombre: string;
  ip_direccion: string;
  estado: string;
  empresa_id: number;
  token_auth?: string;
  umbral_cpu?: number;
  umbral_ram?: number;
  umbral_disco?: number;
  umbral_red?: number;
  usuarios_con_acceso?: any[];
}

export interface UmbralesPayload {
  umbral_cpu: number;
  umbral_ram: number;
  umbral_disco: number;
  umbral_red: number;
}

export const getServidores = async (): Promise<Servidor[]> => {
  const response = await api.get<Servidor[]>('/servidores/');
  return response.data;
};

export const crearServidor = async (data: { nombre: string; ip_direccion: string; estado?: string }) => {
  const response = await api.post('/servidores/', data);
  return response.data;
};

export const actualizarUmbrales = async (servidorId: string, umbrales: UmbralesPayload) => {
  const response = await api.patch(`/servidores/${servidorId}/umbrales`, umbrales);
  return response.data;
};

export const asignarUsuariosServidor = async (servidorId: string, usuariosIds: string[]) => {
  const response = await api.put(`/servidores/${servidorId}/asignar-usuarios`, {
    usuario_ids: usuariosIds,
  });
  return response.data;
};

export const eliminarServidor = async (servidorId: string) => {
  const response = await api.delete(`/servidores/${servidorId}`);
  return response.data;
};

export const renombrarServidor = async (servidorId: string, nombre: string) => {
  const response = await api.put(`/servidores/${servidorId}`, { nombre });
  return response.data;
};

export const descargarReportePdf = async (servidorId: string): Promise<Blob> => {
  const response = await api.get(`/servidores/${servidorId}/reporte-pdf`, {
    responseType: 'blob',
  });
  return response.data;
};