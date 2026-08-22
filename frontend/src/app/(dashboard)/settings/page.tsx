"use client";

import { useState, useEffect } from 'react';
import { Save, Bell, User, Key, Mail, MessageSquare, Download, Terminal, Monitor } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    emailNotifications: true,
    emailAddress: 'Cargando...', // Se llenará desde la API
    discordWebhook: '',
    slackWebhook: '',
    rol: 'Cargando...'
  });

  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  // 🌟 FORMATEADOR DE URL A PRUEBA DE BALAS
  // Quita las barras sobrantes y el /api final si existiera, asegurando una ruta limpia.
  const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
    .replace(/\/$/, '')
    .replace(/\/api$/, '');

  // 1. CARGAR LOS DATOS AL ABRIR LA PÁGINA
  useEffect(() => {
    const cargarAjustes = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;

        const res = await fetch(`${API_BASE}/api/usuarios/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.ok) {
          const data = await res.json();
          setSettings(prev => ({
            ...prev,
            emailAddress: data.email,
            rol: data.rol === 'admin' ? 'Administrador' : data.rol === 'superadmin' ? 'Super Admin' : 'Usuario',
            discordWebhook: data.discord_webhook || '',
            slackWebhook: data.slack_webhook || '',
          }));
        }
      } catch (error) {
        console.error("Error al cargar ajustes:", error);
      } finally {
        setLoading(false);
      }
    };

    cargarAjustes();
  }, [API_BASE]);

  const handleChange = (field: string, value: any) => {
    setSettings(prev => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  // 2. GUARDAR LOS DATOS EN LA BASE DE DATOS
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      
      const res = await fetch(`${API_BASE}/api/usuarios/ajustes`, {
        method: 'PUT',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          discord_webhook: settings.discordWebhook,
          slack_webhook: settings.slackWebhook,
          recibir_alertas_email: settings.emailNotifications
        })
      });

      if (res.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      } else {
        alert("Error al guardar en la base de datos.");
      }
    } catch (error) {
      console.error("Error al guardar:", error);
      alert("Error de conexión con el servidor.");
    }
  };

  if (loading) {
    return <div className="p-8 text-light text-sm animate-pulse">Cargando configuración...</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl pb-10">
      {/* Cabecera */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-title">Ajustes de la Plataforma</h1>
          <p className="text-text mt-1">Configuración de usuario, y canales de alerta.</p>
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
                value={settings.emailAddress}
                className="w-full bg-body/50 border border-border rounded-lg px-3.5 py-2 text-light text-sm font-mono cursor-not-allowed"
              />
              <p className="text-[10px] text-light mt-1">El email no se puede cambiar por motivos de seguridad.</p>
            </div>
            <div>
              <label className="block text-xs font-medium text-light uppercase mb-1.5">Rol en el Sistema</label>
              <div className="w-full bg-body border border-border rounded-lg px-3.5 py-2 text-title text-sm flex items-center gap-2">
                <Key size={14} className="text-amber-500" />
                <span className="font-medium text-amber-500">{settings.rol}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 2. CANALES DE NOTIFICACIÓN EXTERNA */}
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm space-y-5">
          <div className="flex items-center gap-3 pb-3 border-b border-border">
            <span className="p-2 bg-body rounded-lg text-main"><Bell size={20} /></span>
            <div>
              <h2 className="text-lg font-semibold text-title">Integraciones y Alertas</h2>
              <p className="text-xs text-light">Dónde quieres recibir los avisos cuando un servidor falle.</p>
            </div>
          </div>

          <div className="space-y-6">
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
            </div>

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

        {/* 3. DESCARGA DEL AGENTE */}
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm space-y-5">
          <div className="flex items-center gap-3 pb-3 border-b border-border">
            <span className="p-2 bg-body rounded-lg text-main"><Download size={20} /></span>
            <div>
              <h2 className="text-lg font-semibold text-title">Despliegue del Agente</h2>
              <p className="text-xs text-light">Descarga los ejecutables para instalar en tus servidores objetivo.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a 
              href="/agente-linux" 
              download="agente-linux"
              className="flex items-center gap-4 bg-body hover:bg-border/50 border border-border rounded-lg p-4 transition-colors group cursor-pointer"
            >
              <div className="p-2.5 bg-surface rounded-md text-light group-hover:text-main transition-colors border border-border">
                <Terminal size={24} />
              </div>
              <div className="text-left">
                <p className="text-sm font-semibold text-title">Linux (Debian/Mint)</p>
                <p className="text-[11px] text-light mt-0.5">Binario ejecutable sin dependencias</p>
              </div>
            </a>

            <a 
              href="/agente.exe" 
              download="agente.exe"
              className="flex items-center gap-4 bg-body hover:bg-border/50 border border-border rounded-lg p-4 transition-colors group cursor-pointer"
            >
              <div className="p-2.5 bg-surface rounded-md text-light group-hover:text-main transition-colors border border-border">
                <Monitor size={24} />
              </div>
              <div className="text-left">
                <p className="text-sm font-semibold text-title">Windows</p>
                <p className="text-[11px] text-light mt-0.5">Archivo .exe (Bandeja del sistema)</p>
              </div>
            </a>
          </div>
        </div>

      </form>
    </div>
  );
}