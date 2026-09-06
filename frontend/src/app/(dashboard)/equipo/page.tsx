"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Users, Mail, Lock, Shield, Plus, Loader2, CheckCircle2, Trash2 } from 'lucide-react';

import { getEmpleados, crearEmpleado, eliminarEmpleado } from '@/services/authService';

export default function EquipoPage() {
  const router = useRouter();
  const [usuarioActual, setUsuarioActual] = useState<any>(null);
  const [isChecking, setIsChecking] = useState(true);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rol, setRol] = useState('usuario');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [empleados, setEmpleados] = useState<any[]>([]);
  const [loadingEmpleados, setLoadingEmpleados] = useState(true);

  useEffect(() => {
    const userGuardado = localStorage.getItem('usuario');
    if (userGuardado) {
      const userObj = JSON.parse(userGuardado);
      if (userObj.rol !== 'admin') {
        router.push('/dashboard');
      } else {
        setUsuarioActual(userObj);
      }
    } else {
      router.push('/login');
    }
    setIsChecking(false);
  }, [router]);

  useEffect(() => {
    if (usuarioActual) {
      cargarEmpleados();
    }
  }, [usuarioActual]);

  const cargarEmpleados = async () => {
    setLoadingEmpleados(true);
    try {
      const data = await getEmpleados();
      setEmpleados(data);
    } catch (err) {
      console.error("Error al cargar empleados", err);
    } finally {
      setLoadingEmpleados(false);
    }
  };

  const handleCrearEmpleado = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const data = await crearEmpleado({ email, password, rol });
      setSuccess(`¡Éxito! ${data.mensaje || 'Empleado creado'}`);
      setEmail('');
      setPassword('');
      setRol('usuario');
      cargarEmpleados(); 
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Error al crear el usuario";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleEliminarEmpleado = async (empleadoId: string, emailEmpleado: string) => {
    const confirmado = window.confirm(`¿Seguro que quieres revocar el acceso a ${emailEmpleado}?`);
    if (!confirmado) return;

    try {
      await eliminarEmpleado(empleadoId);
      cargarEmpleados();
      alert("Empleado eliminado con éxito.");
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Error al eliminar el empleado";
      alert(msg);
    }
  };
  if (isChecking) {
    return <div className="p-8 flex justify-center"><Loader2 className="animate-spin text-main" /></div>;
  }

  if (!usuarioActual) return null;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-title">Gestión de Equipo</h1>
        <p className="text-text mt-1">Añade o elimina técnicos de la organización.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* PANEL IZQUIERDO: FORMULARIO */}
        <div className="lg:col-span-1 bg-surface border border-border rounded-xl shadow-sm self-start">
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

        {/* PANEL DERECHO: LISTA DE EQUIPO */}
        <div className="lg:col-span-2">
          <div className="bg-surface border border-border rounded-xl shadow-sm overflow-hidden">
            <div className="p-4 border-b border-border bg-body/30 flex items-center justify-between">
              <h2 className="font-semibold text-title flex items-center gap-2">
                <Users size={18} className="text-main" />
                Directorio de la Organización
              </h2>
            </div>
            
            <div className="p-0 overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-border bg-body/50 text-light text-xs uppercase tracking-wider">
                    <th className="py-3 px-6 font-semibold">Usuario</th>
                    <th className="py-3 px-6 font-semibold">Rol</th>
                    <th className="py-3 px-6 font-semibold text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border text-sm">
                  {loadingEmpleados ? (
                    <tr>
                      <td colSpan={3} className="py-8 text-center"><Loader2 className="animate-spin text-main mx-auto" /></td>
                    </tr>
                  ) : empleados.length === 0 ? (
                    <tr>
                      <td colSpan={3} className="py-8 text-center text-light">No hay más usuarios en la organización.</td>
                    </tr>
                  ) : (
                    empleados.map((emp) => (
                      <tr key={emp.id} className="hover:bg-body/30 transition-colors">
                        <td className="py-3 px-6 font-medium text-title">{emp.email}</td>
                        <td className="py-3 px-6">
                          {emp.rol === 'admin' ? (
                            <span className="text-xs bg-amber-500/10 text-amber-500 px-2 py-1 rounded font-medium border border-amber-500/20">Administrador</span>
                          ) : (
                            <span className="text-xs bg-blue-500/10 text-blue-500 px-2 py-1 rounded font-medium border border-blue-500/20">Técnico</span>
                          )}
                        </td>
                        <td className="py-3 px-6 text-right">
                          <button
                            onClick={() => handleEliminarEmpleado(emp.id, emp.email)}
                            disabled={emp.id === usuarioActual.id} 
                            title={emp.id === usuarioActual.id ? "No puedes borrarte a ti mismo" : "Eliminar empleado"}
                            className="inline-flex p-2 text-light hover:text-red-500 hover:bg-body rounded-lg transition-colors disabled:opacity-30 disabled:hover:text-light disabled:hover:bg-transparent cursor-pointer disabled:cursor-not-allowed"
                          >
                            <Trash2 size={16} />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}