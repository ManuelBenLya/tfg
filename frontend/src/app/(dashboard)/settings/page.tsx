"use client";

import { useState } from 'react';
import { Save, Bell, User, Monitor, Key, Mail, MessageSquare } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    // Preferencias
    refreshInterval: '5',
    theme: 'dark',
    // Notificaciones
    emailNotifications: true,
    emailAddress: 'admin@mitfg.es',
    discordWebhook: '',
    slackWebhook: '',
  });

  const [saved, setSaved] = useState(false);

  const handleChange = (field: string, value: any) => {
    setSettings(prev => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    // Aquí en el futuro harías un fetch() a tu API para guardar estos datos
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl pb-10">
      {/* Cabecera */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-title">Ajustes de la Plataforma</h1>
          <p className="text-text mt-1">Configuración de usuario, interfaz y canales de alerta.</p>
        </div>

        <button 
          onClick={handleSave}
          className="flex items-center justify-center gap-2 bg-main hover:bg-opacity-90 text-white px-5 py-2.5 rounded-lg font-medium transition-all shadow-sm"
        >
          <Save size={18} />
          <span>Guardar Cambios</span>
        </button>
      </header>

      {saved && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 px-4 py-3 rounded-xl text-sm font-medium flex items-center gap-2">
          <span>✓ Configuración guardada correctamente en el sistema.</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        
        {/* 1. PERFIL DE USUARIO */}
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm space-y-5">
          <div className="flex items-center gap-3 pb-3 border-b border-border">
            <span className="p-2 bg-body rounded-lg text-main"><User size={20} /></span>
            <div>
              <h2 className="text-lg font-semibold text-title">Perfil de Cuenta</h2>
              <p className="text-xs text-light">Información personal y nivel de acceso.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-medium text-light uppercase mb-1.5">Correo Electrónico</label>
              <input 
                type="email"
                disabled
                value="admin@sistema.local"
                className="w-full bg-body/50 border border-border rounded-lg px-3.5 py-2 text-light text-sm font-mono cursor-not-allowed"
              />
              <p className="text-[10px] text-light mt-1">El email no se puede cambiar por motivos de seguridad.</p>
            </div>
            <div>
              <label className="block text-xs font-medium text-light uppercase mb-1.5">Rol en el Sistema</label>
              <div className="w-full bg-body border border-border rounded-lg px-3.5 py-2 text-title text-sm flex items-center gap-2">
                <Key size={14} className="text-amber-500" />
                <span className="font-medium text-amber-500">Administrador</span>
              </div>
            </div>
          </div>
        </div>

        {/* 2. PREFERENCIAS DE INTERFAZ */}
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm space-y-5">
          <div className="flex items-center gap-3 pb-3 border-b border-border">
            <span className="p-2 bg-body rounded-lg text-main"><Monitor size={20} /></span>
            <div>
              <h2 className="text-lg font-semibold text-title">Preferencias de Interfaz</h2>
              <p className="text-xs text-light">Comportamiento del panel de control de Next.js.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-medium text-light uppercase mb-1.5">Refresco del Dashboard</label>
              <select
                value={settings.refreshInterval}
                onChange={(e) => handleChange('refreshInterval', e.target.value)}
                className="w-full bg-body border border-border rounded-lg px-3.5 py-2 text-title text-sm focus:outline-none focus:border-main"
              >
                <option value="5">Cada 5 segundos (Tiempo Real)</option>
                <option value="15">Cada 15 segundos</option>
                <option value="30">Cada 30 segundos</option>
                <option value="60">Cada 1 minuto (Ahorro de recursos)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-xs font-medium text-light uppercase mb-1.5">Tema Visual</label>
              <select
                value={settings.theme}
                onChange={(e) => handleChange('theme', e.target.value)}
                className="w-full bg-body border border-border rounded-lg px-3.5 py-2 text-title text-sm focus:outline-none focus:border-main"
              >
                <option value="dark">Modo Oscuro (Recomendado)</option>
                <option value="light">Modo Claro</option>
                <option value="system">Seguir preferencias del sistema</option>
              </select>
            </div>
          </div>
        </div>

        {/* 3. CANALES DE NOTIFICACIÓN EXTERNA */}
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm space-y-5">
          <div className="flex items-center gap-3 pb-3 border-b border-border">
            <span className="p-2 bg-body rounded-lg text-main"><Bell size={20} /></span>
            <div>
              <h2 className="text-lg font-semibold text-title">Integraciones y Alertas</h2>
              <p className="text-xs text-light">Dónde quieres recibir los avisos cuando un servidor falle.</p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Correo Electrónico */}
            <div className="p-4 bg-body border border-border rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-start gap-3">
                <Mail className="text-light mt-0.5" size={20} />
                <div>
                  <p className="text-title font-medium text-sm">Notificaciones por Correo</p>
                  <p className="text-xs text-light mt-0.5">Recibe un resumen cuando ocurra una caída del sistema.</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  className="sr-only peer"
                  checked={settings.emailNotifications}
                  onChange={(e) => handleChange('emailNotifications', e.target.checked)}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-main"></div>
              </label>
            </div>

            {/* Discord */}
            <div>
              <label className="flex items-center gap-2 text-xs font-medium text-light uppercase mb-1.5">
                <MessageSquare size={14} /> Webhook de Discord
              </label>
              <input 
                type="text"
                placeholder="https://discord.com/api/webhooks/..."
                value={settings.discordWebhook}
                onChange={(e) => handleChange('discordWebhook', e.target.value)}
                className="w-full bg-body border border-border rounded-lg px-3.5 py-2.5 text-title text-sm focus:outline-none focus:border-main font-mono placeholder:text-gray-500"
              />
              <p className="text-[11px] text-light mt-1.5">El sistema enviará un mensaje automatizado al canal configurado en este webhook.</p>
            </div>

            {/* Slack */}
            <div>
              <label className="flex items-center gap-2 text-xs font-medium text-light uppercase mb-1.5">
                <MessageSquare size={14} /> Webhook de Slack
              </label>
              <input 
                type="text"
                placeholder="https://hooks.slack.com/services/..."
                value={settings.slackWebhook}
                onChange={(e) => handleChange('slackWebhook', e.target.value)}
                className="w-full bg-body border border-border rounded-lg px-3.5 py-2.5 text-title text-sm focus:outline-none focus:border-main font-mono placeholder:text-gray-500"
              />
            </div>
          </div>
        </div>

      </form>
    </div>
  );
}