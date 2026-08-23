import { useState } from 'react';
import { Settings, X, Save } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UmbralesProps {
  servidorId: string;
  nombreServidor: string;
  umbralesActuales: {
    cpu: number;
    ram: number;
    disco: number;
    red: number;
  };
  onClose: () => void;
  onUpdateSuccess: () => void;
}

export default function ModalUmbrales({ servidorId, nombreServidor, umbralesActuales, onClose, onUpdateSuccess }: UmbralesProps) {
  const [formData, setFormData] = useState(umbralesActuales);
  const [isSaving, setIsSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    try {
      const res = await fetch(`${API_BASE}/api/servidores/${servidorId}/umbrales`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          // 'Authorization': `Bearer ${localStorage.getItem('token')}` // Si usas JWT
        },
        body: JSON.stringify({
          umbral_cpu: formData.cpu,
          umbral_ram: formData.ram,
          umbral_disco: formData.disco,
          umbral_red: formData.red
        })
      });

      if (res.ok) {
        onUpdateSuccess(); // Para recargar la lista de servidores en el componente padre
        onClose(); // Cerramos el modal
      } else {
        console.error("Error al guardar los umbrales");
      }
    } catch (error) {
      console.error("Fallo de conexión", error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl w-full max-w-md border border-gray-200 dark:border-slate-700 overflow-hidden">
        
        {/* Cabecera */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between bg-gray-50 dark:bg-slate-800">
          <div className="flex items-center gap-2 text-gray-800 dark:text-white">
            <Settings size={20} className="text-blue-500" />
            <h3 className="font-semibold">Configurar Umbrales</h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Ajusta los límites de alerta para <span className="font-semibold text-gray-700 dark:text-gray-200">{nombreServidor}</span>.
          </p>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">CPU (%)</label>
              <input 
                type="number" max="100" min="1" step="0.1" required
                className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                value={formData.cpu}
                onChange={(e) => setFormData({...formData, cpu: parseFloat(e.target.value)})}
              />
            </div>
            
            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">RAM (MB)</label>
              <input 
                type="number" min="1" required
                className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                value={formData.ram}
                onChange={(e) => setFormData({...formData, ram: parseFloat(e.target.value)})}
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">Disco (%)</label>
              <input 
                type="number" max="100" min="1" step="0.1" required
                className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                value={formData.disco}
                onChange={(e) => setFormData({...formData, disco: parseFloat(e.target.value)})}
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">Red - Latencia (ms)</label>
              <input 
                type="number" min="1" required
                className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                value={formData.red}
                onChange={(e) => setFormData({...formData, red: parseFloat(e.target.value)})}
              />
            </div>
          </div>

          <div className="pt-4 flex justify-end gap-3 border-t border-gray-200 dark:border-slate-700 mt-6">
            <button 
              type="button" 
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
            >
              <Save size={16} />
              {isSaving ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}