"use client";


import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, Lock, Mail, ArrowRight } from 'lucide-react';
import { loginAPI } from '@/services/authService'; // Ajusta la ruta si es necesario

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('admin@sitem.local');
  const [password, setPassword] = useState('********');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Llamada real al backend de FastAPI
      const data = await loginAPI(email, password);
      
      if (data.access_token) {
        // Guardamos el token real que nos devuelve FastAPI
        // Usamos 'token' como clave (asegúrate de que el interceptor de Axios busque esta misma clave)
        localStorage.setItem('token', data.access_token);
        
        // Redirigimos al dashboard
        router.push('/dashboard');
      }
    } catch (err: any) {
      // Si FastAPI devuelve un 401, caerá aquí
      if (err.response?.status === 401) {
        setError('Credenciales incorrectas. Comprueba tu correo y contraseña.');
      } else {
        setError('Error de conexión con el servidor de autenticación.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-body flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-surface border border-border rounded-2xl shadow-lg p-8 space-y-6">
        
        {/* Cabecera / Logo */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 bg-main/10 text-main rounded-2xl border border-main/20 mb-1">
            <Shield size={32} />
          </div>
          <h1 className="text-2xl font-bold text-title">SITEM Monitoring</h1>
          <p className="text-text text-sm">Introduce tus credenciales para acceder al panel central.</p>
        </div>

        {/* Mensaje de error si lo hay */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-500 text-xs font-medium p-3 rounded-lg text-center">
            {error}
          </div>
        )}

        {/* Formulario de Login */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-light uppercase mb-1.5">Correo Electrónico</label>
            <div className="relative">
              <Mail size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-light" />
              <input 
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-body border border-border rounded-lg pl-10 pr-4 py-2.5 text-title text-sm focus:outline-none focus:border-main transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-light uppercase mb-1.5">Contraseña</label>
            <div className="relative">
              <Lock size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-light" />
              <input 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-body border border-border rounded-lg pl-10 pr-4 py-2.5 text-title text-sm focus:outline-none focus:border-main transition-colors"
              />
            </div>
          </div>

          <button 
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 flex items-center justify-center gap-2 bg-main hover:bg-opacity-90 text-white py-2.5 rounded-lg font-medium transition-all shadow-sm disabled:opacity-50 cursor-pointer"
          >
            {isLoading ? (
              <span>Verificando acceso...</span>
            ) : (
              <>
                <span>Iniciar Sesión</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="text-center pt-2 border-t border-border">
          <p className="text-xs text-light">
            Sistema Centralizado de Monitorización • TFG 2026
          </p>
        </div>

      </div>
    </div>
  );
}