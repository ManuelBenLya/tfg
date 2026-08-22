"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Users, Mail, Lock, Shield, Plus, Loader2, CheckCircle2 } from 'lucide-react';

export default function EquipoPage() {
  const router = useRouter();
  const [usuarioActual, setUsuarioActual] = useState<any>(null);
  const [isChecking, setIsChecking] = useState(true);

  // Estados del formulario
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rol, setRol] = useState('usuario');
  
  // Estados de feedback
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // 1. 🔒 PROTECCIÓN DE RUTA (Comprobamos si es admin)
  useEffect(() => {
    const userGuardado = localStorage.getItem('usuario');
    if (userGuardado) {
      const userObj = JSON.parse(userGuardado);
      if (userObj.rol !== 'admin') {
        // Si es un empleado normal, lo echamos al Dashboard
        router.push('/dashboard');
      } else {
        setUsuarioActual(userObj);
      }
    } else {
      router.push('/login');
    }
    setIsChecking(false);
  }, [router]);

  // 2. FUNCIÓN PARA CREAR EMPLEADO
  const handleCrearEmpleado = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const res = await fetch('http://127.0.0.1:8000/api/usuarios/empleados', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: email,
          password: password,
          rol: rol
        })
      });

      const data = await res.json();

      if (res.ok) {
        setSuccess(`¡Éxito! ${data.mensaje}`);
        // Limpiamos el formulario
        setEmail('');
        setPassword('');
        setRol('usuario');
      } else {
        setError(data.detail || "Error al crear el usuario");
      }
    } catch (err) {
      setError("Error de conexión con el servidor");
    } finally {
      setLoading(false);
    }
  };

  if (isChecking) {
    return <div className="p-8 flex justify-center"><Loader2 className="animate-spin text-main" /></div>;
  }

  // Si no hay usuario (porque está redirigiendo), no renderizamos nada
  if (!usuarioActual) return null;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-title">Gestión de Equipo</h1>
        <p className="text-text mt-1">Añade técnicos y administradores a la organización.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* PANEL IZQUIERDO: FORMULARIO */}
        <div className="lg:col-span-1 bg-surface border border-border rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 border-b border-border bg-body/30">
            <h2 className="font-semibold text-title flex items-center gap-2">
              <Plus size={18} className="text-main" />
              Nuevo Empleado
            </h2>
          </div>
          
          <div className="p-6">
            {error && (
              <div className="mb-4 bg-red-500/10 border border-red-500/20 text-red-500 text-sm p-3 rounded-lg">
                {error}
              </div>
            )}
            
            {success && (
              <div className="mb-4 flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-sm p-3 rounded-lg">
                <CheckCircle2 size={18} />
                {success}
              </div>
            )}

            <form onSubmit={handleCrearEmpleado} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-light uppercase mb-1.5">Email del técnico</label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-light" />
                  <input 
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-body border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-title focus:outline-none focus:border-main transition-colors"
                    placeholder="tecnico@empresa.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-light uppercase mb-1.5">Contraseña Temporal</label>
                <div className="relative">
                  <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-light" />
                  <input 
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-body border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-title focus:outline-none focus:border-main transition-colors"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-light uppercase mb-1.5">Nivel de Acceso (Rol)</label>
                <div className="relative">
                  <Shield size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-light" />
                  <select 
                    value={rol}
                    onChange={(e) => setRol(e.target.value)}
                    className="w-full bg-body border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-title focus:outline-none focus:border-main transition-colors appearance-none"
                  >
                    <option value="usuario">Operador / Técnico (Solo lectura)</option>
                    <option value="admin">Administrador (Control Total)</option>
                  </select>
                </div>
              </div>

              <button 
                type="submit"
                disabled={loading}
                className="w-full mt-4 flex items-center justify-center gap-2 bg-main hover:bg-opacity-90 text-white py-2 rounded-lg font-medium transition-all shadow-sm disabled:opacity-50"
              >
                {loading ? <Loader2 size={18} className="animate-spin" /> : 'Registrar Empleado'}
              </button>
            </form>
          </div>
        </div>

        {/* PANEL DERECHO: INFORMACIÓN */}
        <div className="lg:col-span-2">
          <div className="bg-surface border border-border rounded-xl shadow-sm p-8 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
            <div className="p-4 bg-body rounded-full mb-4">
              <Users size={32} className="text-light" />
            </div>
            <h3 className="text-lg font-semibold text-title mb-2">Arquitectura Multi-Inquilino</h3>
            <p className="text-text text-sm max-w-md">
              Los usuarios creados aquí quedarán vinculados exclusivamente a tu organización (<code>ID: {usuarioActual.empresa_id.split('-')[0]}...</code>). <br/><br/>
              Un operador normal solo podrá ver los servidores que tú le asignes explícitamente y no podrá modificar parámetros críticos como los umbrales de alerta.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}