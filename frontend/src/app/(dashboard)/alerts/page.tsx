"use client";

import { useState, useEffect } from 'react';
import { AlertTriangle, Bell, CheckCircle, Clock, Server, XCircle } from 'lucide-react';

interface AlertaBackend {
  id: number;
  servidor_id: string;
  mensaje: string;
  leida: boolean;
  tiempo: string;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertaBackend[]>([]);
  const [filter, setFilter] = useState<'all' | 'active' | 'resolved'>('all');
  const [loading, setLoading] = useState(true);

  // 🌟 URL base inteligente para evitar problemas de CORS o IP local
  const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
    .replace(/\/$/, '')
    .replace(/\/api$/, '');

  const fetchAlertas = async () => {
    try {
      const token = localStorage.getItem('token'); // 🔑 Obtenemos el token de seguridad
      const res = await fetch(`${API_BASE}/api/alertas/pendientes`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}` // 🛡️ Enviamos el token al backend blindado
        }
      });
      
      if (res.ok) {
        const data: AlertaBackend[] = await res.json();
        setAlerts(data);
      } else {
        console.error("Error al obtener alertas:", res.status);
      }
    } catch (error) {
      console.error("Error al conectar con el backend de alertas:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlertas();
    const interval = setInterval(fetchAlertas, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleResolve = async (id: number) => {
    try {
      const token = localStorage.getItem('token'); // 🔑 Obtenemos el token
      const res = await fetch(`${API_BASE}/api/alertas/${id}/marcar-leida`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}` // 🛡️ Autorizamos la petición de cambio
        },
      });
      
      if (res.ok) {
        setAlerts(prev => prev.map(alt => alt.id === id ? { ...alt, leida: true } : alt));
      } else {
        console.error("Error al marcar como leída:", res.status);
      }
    } catch (error) {
      console.error("Error al marcar la alerta como leída:", error);
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'active') return !alert.leida;
    if (filter === 'resolved') return alert.leida;
    return true;
  });

  const criticasActivas = alerts.filter(a => !a.leida).length;
  const resueltasTotal = alerts.filter(a => a.leida).length;

  return (
    <div className="space-y-6">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-title">Centro de Alertas</h1>
          <p className="text-text mt-1">Monitoreo de incidencias detectadas por el sistema de umbrales estáticos.</p>
        </div>

        <div className="flex items-center gap-2 bg-surface border border-border p-1 rounded-lg">
          <button 
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${filter === 'all' ? 'bg-main text-white' : 'text-text hover:text-title'}`}
          >
            Todas
          </button>
          <button 
            onClick={() => setFilter('active')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${filter === 'active' ? 'bg-main text-white' : 'text-text hover:text-title'}`}
          >
            Activas
          </button>
          <button 
            onClick={() => setFilter('resolved')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${filter === 'resolved' ? 'bg-main text-white' : 'text-text hover:text-title'}`}
          >
            Resueltas
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-light font-medium text-sm">Alertas Activas</h3>
            <span className="p-2 bg-red-500/10 text-red-500 rounded-lg"><XCircle size={18} /></span>
          </div>
          <p className="text-3xl font-bold text-red-500 mt-2">{criticasActivas}</p>
        </div>

        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-light font-medium text-sm">Motor de Detección</h3>
            <span className="p-2 bg-blue-500/10 text-main rounded-lg"><Bell size={18} /></span>
          </div>
          <p className="text-xl font-bold text-title mt-2">Umbrales Dinámicos</p>
        </div>

        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-light font-medium text-sm">Gestionadas / Leídas</h3>
            <span className="p-2 bg-emerald-500/10 text-emerald-500 rounded-lg"><CheckCircle size={18} /></span>
          </div>
          <p className="text-3xl font-bold text-emerald-500 mt-2">{resueltasTotal}</p>
        </div>
      </div>

      <div className="bg-surface rounded-xl border border-border shadow-sm overflow-hidden divide-y divide-border">
        {loading ? (
          <div className="p-12 text-center text-light">Cargando alertas del sistema...</div>
        ) : filteredAlerts.length === 0 ? (
          <div className="p-12 text-center text-light">
            No hay alertas que coincidan con este filtro. ¡El sistema está estable!
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div key={alert.id} className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-body/30 transition-colors">
              <div className="flex items-start gap-4">
                <div className="mt-1">
                  {!alert.leida ? (
                    <span className="p-2.5 bg-red-500/10 text-red-500 rounded-xl inline-block border border-red-500/20"><AlertTriangle size={20} /></span>
                  ) : (
                    <span className="p-2.5 bg-emerald-500/10 text-emerald-500 rounded-xl inline-block border border-emerald-500/20"><CheckCircle size={20} /></span>
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono bg-body border border-border px-2 py-0.5 rounded text-light">ALT-{alert.id}</span>
                    <span className="text-xs font-medium text-main flex items-center gap-1"><Server size={12} /> {alert.servidor_id.slice(0, 8)}...</span>
                    <span className="text-xs text-light flex items-center gap-1"><Clock size={12} /> {new Date(alert.tiempo).toLocaleTimeString()}</span>
                  </div>
                  <p className="text-title font-medium mt-1.5">{alert.mensaje}</p>
                </div>
              </div>

              <div className="flex items-center gap-3 self-end md:self-center">
                {!alert.leida ? (
                  <button 
                    onClick={() => handleResolve(alert.id)}
                    className="bg-body hover:bg-border text-title border border-border px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors shadow-sm cursor-pointer"
                  >
                    Marcar como Resuelta
                  </button>
                ) : (
                  <span className="inline-flex items-center gap-1.5 text-emerald-500 bg-emerald-500/10 px-3 py-1.5 rounded-lg text-xs font-medium">
                    <CheckCircle size={14} /> Resuelta
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}