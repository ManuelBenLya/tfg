"use client";

import { useState, useEffect } from 'react';
import { Server, Plus, Search, CheckCircle2, AlertTriangle, XCircle, Settings, Loader2, Users, FileText, Pencil, Trash2 } from 'lucide-react';
import ModalUmbrales from '@/components/ui/ModalUmbrales'; 
import ModalNuevoServidor from '@/components/ui/ModalNuevoServidor'; 
import ModalAsignarUsuarios from '@/components/ui/ModalAsignarUsuarios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ServersPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [servers, setServers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [servidorEditando, setServidorEditando] = useState<any | null>(null);
  const [mostrarModalNuevo, setMostrarModalNuevo] = useState(false); 
  
  const [usuario, setUsuario] = useState<any>(null);
  const [servidorAsignando, setServidorAsignando] = useState<any | null>(null);

  const fetchServidores = async () => {
    try {
      const token = localStorage.getItem('token'); 
      const res = await fetch(`${API_BASE}/api/servidores/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        setServers(data);
      } else {
        setServers([]);
      }
    } catch (error) {
      console.error("Error al conectar con el backend:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async (servidorId: string, nombreServidor: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/servidores/${servidorId}/reporte-pdf`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!res.ok) throw new Error("Error al descargar el PDF");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Reporte_${nombreServidor}.pdf`; 
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert("Hubo un problema al generar el reporte PDF.");
    }
  };

  // 🌟 NUEVO: BORRAR SERVIDOR
  const handleEliminarServidor = async (servidorId: string, nombre: string) => {
    if (!window.confirm(`¿Estás seguro de que quieres eliminar "${nombre}"? Esta acción borrará todas sus métricas y no se puede deshacer.`)) {
      return;
    }
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/servidores/${servidorId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (res.ok) {
        fetchServidores();
      } else {
        alert("Error al eliminar el servidor.");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  // 🌟 NUEVO: RENOMBRAR SERVIDOR
  const handleRenombrarServidor = async (servidorId: string, nombreActual: string) => {
    const nuevoNombre = window.prompt("Introduce el nuevo nombre para el servidor:", nombreActual);
    if (!nuevoNombre || nuevoNombre === nombreActual) return;

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/servidores/${servidorId}`, {
        method: 'PUT',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nombre: nuevoNombre })
      });
      
      if (res.ok) {
        fetchServidores();
      } else {
        alert("Error al renombrar el servidor.");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  useEffect(() => {
    fetchServidores();
    const userGuardado = localStorage.getItem('usuario');
    if (userGuardado) {
      setUsuario(JSON.parse(userGuardado));
    }
  }, []);

  const filteredServers = servers.filter(srv => 
    srv.nombre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    srv.ip_direccion?.includes(searchTerm) ||
    srv.estado?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 relative">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-title">Inventario de Servidores</h1>
          <p className="text-text mt-1">Gestión, estado y configuración de los nodos de la infraestructura.</p>
        </div>

        {usuario?.rol === 'admin' && (
          <button 
            onClick={() => setMostrarModalNuevo(true)}
            className="flex items-center justify-center gap-2 bg-main hover:bg-opacity-90 text-white px-4 py-2.5 rounded-lg font-medium transition-all shadow-sm"
          >
            <Plus size={18} />
            <span>Añadir Servidor</span>
          </button>
        )}
      </header>

      <div className="bg-surface p-4 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-96">
          <Search size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-light" />
          <input 
            type="text"
            placeholder="Buscar por nombre, IP o estado..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-body border border-border rounded-lg pl-10 pr-4 py-2 text-title text-sm focus:outline-none focus:border-main transition-colors"
          />
        </div>

        <div className="flex items-center gap-3 text-xs text-light">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Online ({servers.filter(s => s.estado === 'Online').length})</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-red-500"></span> Offline ({servers.filter(s => s.estado === 'Offline').length})</span>
        </div>
      </div>

      <div className="bg-surface rounded-xl border border-border shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-body/50 text-light text-xs uppercase tracking-wider">
                <th className="py-3.5 px-6 font-semibold">Servidor / Nodo</th>
                <th className="py-3.5 px-6 font-semibold">Dirección IP</th>
                <th className="py-3.5 px-6 font-semibold">Estado</th>
                <th className="py-3.5 px-6 font-semibold">Token (Auth)</th> 
                <th className="py-3.5 px-6 font-semibold text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border text-sm">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-light">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <Loader2 size={24} className="animate-spin text-main" />
                      <p>Cargando inventario de servidores...</p>
                    </div>
                  </td>
                </tr>
              ) : filteredServers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-light">
                    No se encontraron servidores que coincidan con la búsqueda.
                  </td>
                </tr>
              ) : (
                filteredServers.map((srv) => (
                  <tr key={srv.id} className="hover:bg-body/30 transition-colors">
                    <td className="py-4 px-6 font-medium text-title flex items-center gap-3">
                      <div className="p-2 bg-body rounded-lg border border-border text-main">
                        <Server size={18} />
                      </div>
                      <div>
                        <p>{srv.nombre}</p>
                        <span className="text-xs text-light font-normal font-mono">{srv.id.slice(0, 13)}...</span>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-text font-mono text-xs">{srv.ip_direccion}</td>
                    <td className="py-4 px-6">
                      {srv.estado?.toLowerCase() === 'online' ? (
                        <span className="inline-flex items-center gap-1.5 text-emerald-500 bg-emerald-500/10 px-2.5 py-1 rounded-full text-xs font-medium">
                          <CheckCircle2 size={14} /> Online
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 text-red-500 bg-red-500/10 px-2.5 py-1 rounded-full text-xs font-medium">
                          <XCircle size={14} /> Offline
                        </span>
                      )}
                    </td>
                    <td className="py-4 px-6 font-mono text-xs text-light">
                      <span className="bg-body border border-border px-2 py-1 rounded">
                        {srv.token_auth ? `${srv.token_auth.slice(0, 8)}***` : 'N/A'}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-right">
                    <div className="flex items-center justify-end gap-2">
                      
                      <button 
                        onClick={() => handleDownloadPDF(srv.id, srv.nombre)}
                        title="Descargar Reporte PDF"
                        className="inline-flex items-center justify-center p-2 text-light hover:text-emerald-500 hover:bg-body border border-transparent hover:border-border rounded-lg transition-colors shadow-sm"
                      >
                        <FileText size={18} />
                      </button>

                      {usuario?.rol === 'admin' ? (
                        <>
                          <button 
                            onClick={() => handleRenombrarServidor(srv.id, srv.nombre)}
                            title="Renombrar Servidor"
                            className="inline-flex items-center justify-center p-2 text-light hover:text-title hover:bg-body border border-transparent hover:border-border rounded-lg transition-colors shadow-sm"
                          >
                            <Pencil size={18} />
                          </button>

                          <button 
                            onClick={() => setServidorAsignando(srv)}
                            title="Asignar Usuarios"
                            className="inline-flex items-center justify-center p-2 text-light hover:text-blue-500 hover:bg-body border border-transparent hover:border-border rounded-lg transition-colors shadow-sm"
                          >
                            <Users size={18} />
                          </button>

                          <button 
                            onClick={() => setServidorEditando(srv)}
                            title="Configurar Umbrales"
                            className="inline-flex items-center justify-center p-2 text-light hover:text-main hover:bg-body border border-transparent hover:border-border rounded-lg transition-colors shadow-sm"
                          >
                            <Settings size={18} />
                          </button>

                          <div className="w-px h-5 bg-border mx-1"></div>

                          <button 
                            onClick={() => handleEliminarServidor(srv.id, srv.nombre)}
                            title="Eliminar Servidor"
                            className="inline-flex items-center justify-center p-2 text-light hover:text-red-500 hover:bg-body border border-transparent hover:border-border rounded-lg transition-colors shadow-sm"
                          >
                            <Trash2 size={18} />
                          </button>
                        </>
                      ) : (
                        <span className="text-xs text-light italic bg-body px-2 py-1 rounded">
                          Solo lectura
                        </span>
                      )}
                    </div>
                  </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {servidorEditando && (
        <ModalUmbrales 
          servidorId={servidorEditando.id}
          nombreServidor={servidorEditando.nombre}
          umbralesActuales={{
            cpu: servidorEditando.umbral_cpu || 90.0,
            ram: servidorEditando.umbral_ram || 16000.0,
            disco: servidorEditando.umbral_disco || 90.0,
            red: servidorEditando.umbral_red || 500.0
          }}
          onClose={() => setServidorEditando(null)}
          onUpdateSuccess={fetchServidores}
        />
      )}

      {mostrarModalNuevo && (
        <ModalNuevoServidor 
          onClose={() => setMostrarModalNuevo(false)}
          onSuccess={fetchServidores}
        />
      )}

      {servidorAsignando && (
        <ModalAsignarUsuarios
          servidorId={servidorAsignando.id}
          nombreServidor={servidorAsignando.nombre}
          usuariosConAcceso={servidorAsignando.usuarios_con_acceso}
          onClose={() => setServidorAsignando(null)}
        />
      )}
    </div>
  );
}