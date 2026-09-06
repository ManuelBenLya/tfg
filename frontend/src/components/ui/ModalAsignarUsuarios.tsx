"use client";

import { useState, useEffect } from 'react';
import { X, Users, Loader2, Check } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ModalAsignarUsuariosProps {
  servidorId: string;
  nombreServidor: string;
  usuariosConAcceso?: any[];
  onClose: () => void;
}

export default function ModalAsignarUsuarios({ servidorId, nombreServidor, usuariosConAcceso, onClose }: ModalAsignarUsuariosProps) {
  const [empleados, setEmpleados] = useState<any[]>([]);
  const [seleccionados, setSeleccionados] = useState<string[]>(
    usuariosConAcceso ? usuariosConAcceso.map((u: any) => u.id) : []
  );
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchDatos = async () => {
      try {
        const token = localStorage.getItem('token');
        
        // 1. Obtenemos TODOS los empleados de la empresa
        const resEmpleados = await fetch(`${API_BASE}/api/usuarios/empleados`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const dataEmpleados = await resEmpleados.json();
        // Filtramos para excluir administradores (ya que tienen acceso global por defecto)
        const filtrados = dataEmpleados.filter((emp: any) => emp.rol !== 'admin' && emp.rol !== 'superadmin');
        setEmpleados(filtrados);

        // (Opcional pero recomendado para UX: Aquí podrías hacer un fetch para saber 
        // cuáles estaban ya marcados previamente, para rellenar el array 'seleccionados')
        // Por simplicidad, aquí partimos de 0 marcados o puedes pre-marcar a los admins.

      } catch (error) {
        console.error("Error al cargar empleados", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDatos();
  }, [servidorId]);

  const toggleUsuario = (id: string) => {
    setSeleccionados(prev => 
      prev.includes(id) ? prev.filter(uid => uid !== id) : [...prev, id]
    );
  };

  const handleGuardar = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/servidores/${servidorId}/asignar-usuarios`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ usuario_ids: seleccionados })
      });

      if (res.ok) {
        onClose(); // Cerramos el modal con éxito
      }
    } catch (error) {
      console.error("Error al guardar", error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface w-full max-w-md rounded-2xl shadow-xl border border-border overflow-hidden">
        
        <div className="flex justify-between items-center p-5 border-b border-border bg-body/50">
          <div>
            <h2 className="text-lg font-bold text-title flex items-center gap-2">
              <Users size={20} className="text-main" />
              Asignar Accesos
            </h2>
            <p className="text-xs text-light mt-1">Servidor: <span className="font-mono text-text">{nombreServidor}</span></p>
          </div>
          <button onClick={onClose} className="text-light hover:text-red-500 transition-colors">
            <X size={24} />
          </button>
        </div>

        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {loading ? (
            <div className="flex justify-center py-8"><Loader2 className="animate-spin text-main" /></div>
          ) : (
            <div className="space-y-3">
              {empleados.map(emp => (
                <label 
                  key={emp.id} 
                  className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition-all ${
                    seleccionados.includes(emp.id) ? 'border-main bg-main/5' : 'border-border hover:border-light bg-body/30'
                  }`}
                >
                  <div>
                    <p className="font-medium text-title text-sm">{emp.email}</p>
                    <p className="text-xs text-light uppercase tracking-wider mt-0.5">{emp.rol}</p>
                  </div>
                  <div className={`w-5 h-5 rounded flex items-center justify-center border ${
                    seleccionados.includes(emp.id) ? 'bg-main border-main text-white' : 'border-light/50 text-transparent'
                  }`}>
                    <Check size={14} />
                  </div>
                  <input 
                    type="checkbox" 
                    className="hidden" 
                    checked={seleccionados.includes(emp.id)}
                    onChange={() => toggleUsuario(emp.id)}
                  />
                </label>
              ))}
            </div>
          )}
        </div>

        <div className="p-5 border-t border-border bg-body/50 flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 text-sm font-medium text-text hover:text-title">
            Cancelar
          </button>
          <button 
            onClick={handleGuardar}
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2 bg-main text-white rounded-lg font-medium shadow-sm hover:bg-opacity-90 disabled:opacity-50"
          >
            {saving ? <Loader2 size={16} className="animate-spin" /> : 'Guardar Accesos'}
          </button>
        </div>
      </div>
    </div>
  );
}