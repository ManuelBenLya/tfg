import { useState } from 'react';
import { Server, X, Plus, Copy, CheckCircle2, AlertCircle } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ModalNuevoServidorProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function ModalNuevoServidor({ onClose, onSuccess }: ModalNuevoServidorProps) {
  const [formData, setFormData] = useState({ nombre: '', ip_direccion: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  
  // Estado para la pantalla de éxito
  const [tokenGenerado, setTokenGenerado] = useState<string | null>(null);
  const [copiado, setCopiado] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/servidores/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          nombre: formData.nombre,
          ip_direccion: formData.ip_direccion || 'Pendiente de conexión...', 
          estado: 'Offline' 
        })
      });

      if (res.ok) {
        const data = await res.json();
        setTokenGenerado(data.token_auth);
        onSuccess(); // Recarga la tabla de fondo
      } else {
        const errData = await res.json();
        setError(errData.detail || 'Error al registrar el servidor.');
      }
    } catch (err) {
      setError('Error de conexión con el servidor.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const copiarToken = () => {
    if (tokenGenerado) {
      navigator.clipboard.writeText(tokenGenerado);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl w-full max-w-md border border-gray-200 dark:border-slate-700 overflow-hidden">
        
        {/* Cabecera */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between bg-gray-50 dark:bg-slate-800">
          <div className="flex items-center gap-2 text-gray-800 dark:text-white">
            <Server size={20} className="text-blue-500" />
            <h3 className="font-semibold">
              {tokenGenerado ? 'Servidor Registrado' : 'Añadir Nuevo Servidor'}
            </h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* CONTENIDO: Formulario o Pantalla de Éxito */}
        {!tokenGenerado ? (
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Registra un nuevo nodo para monitorizar. El sistema generará un token de acceso único.
            </p>

            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg flex items-center gap-2">
                <AlertCircle size={16} /> {error}
              </div>
            )}

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre del Servidor</label>
                <input 
                  type="text" required placeholder="Ej: SRV-Web-03"
                  className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.nombre}
                  onChange={(e) => setFormData({...formData, nombre: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Dirección IP <span className="text-gray-400 font-normal">(Opcional)</span>
                </label>
                <input 
                  type="text" 
                  placeholder="Se detectará automáticamente al conectar"
                  className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.ip_direccion}
                  onChange={(e) => setFormData({...formData, ip_direccion: e.target.value})}
                />
              </div>
            </div>

            <div className="pt-4 flex justify-end gap-3 border-t border-gray-200 dark:border-slate-700 mt-6">
              <button 
                type="button" onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button 
                type="submit" disabled={isSubmitting}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
              >
                <Plus size={16} />
                {isSubmitting ? 'Registrando...' : 'Registrar Nodo'}
              </button>
            </div>
          </form>
        ) : (
          <div className="p-6 space-y-6 text-center">
            <div className="mx-auto w-12 h-12 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-500 rounded-full flex items-center justify-center">
              <CheckCircle2 size={24} />
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-800 dark:text-white">¡Registro Completado!</h4>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Pega este Token en el archivo de configuración del Agente de escritorio.
              </p>
            </div>

            <div className="bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 p-4 rounded-lg relative group">
              <p className="font-mono text-sm text-gray-800 dark:text-gray-200 break-all pr-8">
                {tokenGenerado}
              </p>
              <button 
                onClick={copiarToken}
                title="Copiar token"
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition-colors"
              >
                {copiado ? <CheckCircle2 size={18} className="text-emerald-500" /> : <Copy size={18} />}
              </button>
            </div>

            <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 rounded-lg text-left flex gap-3">
              <AlertCircle size={20} className="text-amber-600 shrink-0 mt-0.5" />
              <p className="text-xs text-amber-700 dark:text-amber-400">
                <strong>Importante:</strong> Guarda este token. Por motivos de seguridad, no se volverá a mostrar.
              </p>
            </div>

            <button 
              onClick={onClose}
              className="w-full py-2.5 text-sm font-medium text-white bg-gray-800 hover:bg-gray-900 dark:bg-slate-700 dark:hover:bg-slate-600 rounded-lg transition-colors"
            >
              Cerrar y volver al inventario
            </button>
          </div>
        )}
      </div>
    </div>
  );
}