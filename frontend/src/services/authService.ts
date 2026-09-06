import api from './api';

// 1. Obtener el Token (Tu código original, intacto)
export const loginAPI = async (email: string, password: string) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await api.post('/usuarios/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  return response.data; // Devuelve { access_token: "...", token_type: "bearer" }
};

// 2. NUEVO: Obtener los datos del perfil (Incluyendo el ROL y EMPRESA_ID)
export const getMeAPI = async (token: string) => {
  const response = await api.get('/usuarios/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  return response.data; // Devuelve { id: "...", email: "...", rol: "admin", empresa_id: "..." }
};