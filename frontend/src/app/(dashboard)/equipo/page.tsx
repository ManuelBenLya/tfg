"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Users, Mail, Lock, Shield, Plus, Loader2, CheckCircle2, Trash2 } from 'lucide-react';

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

  // 🌟 FORMATEADOR DE URL INTELIGENTE
  const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
    .replace(/\/$/, '')
    .replace(/\/api$/, '');

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

  // 🌟 SE EJECUTA CUANDO usuarioActual ESTÁ LISTO
  useEffect(() => {
    if (usuarioActual) {
      cargarEmpleados();
    }
  }, [usuarioActual]);

  const cargarEmpleados = async () => {
    setLoadingEmpleados(true);
    try {
      const token = localStorage.getItem('token');
      // 🌟 USAMOS API_BASE
      const res = await fetch(`${API_BASE}/api/usuarios/empleados`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setEmpleados(data);
      }
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
      const token = localStorage.getItem('token');
      // 🌟 USAMOS API_BASE
      const res = await fetch(`${API_BASE}/api/usuarios/empleados`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ email, password, rol })
      });

      const data = await res.json();

      if (res.ok) {
        setSuccess(`¡Éxito! ${data.mensaje}`);
        setEmail('');
        setPassword('');
        setRol('usuario');
        cargarEmpleados(); 
      } else {
        setError(data.detail || "Error al crear el usuario");
      }
    } catch (err) {
      setError("Error de conexión con el servidor");
    } finally {
      setLoading(false);
    }
  };

 const handleEliminarEmpleado = async (empleadoId: string, emailEmpleado: string) => {
    // CHIVATO 1: ¿Llega a ejecutarse el click?
    console.log("1. Botón pulsado. Intentando borrar a:", emailEmpleado, "con ID:", empleadoId);

    const confirmado = window.confirm(`¿Seguro que quieres revocar el acceso a ${emailEmpleado}?`);
    
    // CHIVATO 2: ¿Qué ha respondido la ventana de confirmación?
    console.log("2. Respuesta de la confirmación:", confirmado);

    if (!confirmado) {
      console.log("3. Operación cancelada por el usuario.");
      return;
    }

    try {
      const token = localStorage.getItem('token');
      // CHIVATO 3: Verificamos la URL exacta a la que estamos llamando
      const urlDestino = `${API_BASE}/api/usuarios/empleados/${empleadoId}`;
      console.log("4. Disparando FETCH hacia:", urlDestino);

      const res = await fetch(urlDestino, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      // CHIVATO 4: ¿Qué código HTTP nos devuelve FastAPI? (200, 404, 422, 500...)
      console.log("5. El backend ha respondido con STATUS:", res.status);

      if (res.ok) {
        console.log("6. ¡Éxito! Recargando la lista...");
        cargarEmpleados();
        alert("Empleado eliminado con éxito.");
      } else {
        const errData = await res.json();
        console.error("7. El backend ha devuelto un error:", errData);
        alert(errData.detail || "Error al eliminar el empleado");
      }
    } catch (err) {
      console.error("8. Error crítico de red (¿CORS o backend apagado?):", err);
      alert("Error de conexión al intentar borrar el empleado.");
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