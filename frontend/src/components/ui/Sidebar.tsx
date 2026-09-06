"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
// 🌟 Añadimos el icono Users para la pestaña de Equipo
import { LayoutDashboard, Server, Bell, Settings, LogOut, Users } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

export default function Sidebar() {
  const router = useRouter();
  const [usuario, setUsuario] = useState<any>(null);

  // 🌟 Leemos quién es el usuario al cargar el Sidebar
  useEffect(() => {
    const userGuardado = localStorage.getItem('usuario');
    if (userGuardado) {
      setUsuario(JSON.parse(userGuardado));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario'); // 🌟 Limpiamos también el usuario al salir
    router.push('/login');
  };

  return (
    <aside className="w-64 bg-surface h-screen flex flex-col shrink-0 border-r border-border transition-colors duration-300">
      <div className="h-16 flex items-center justify-center border-b border-border">
        <h1 className="text-xl font-bold tracking-wider text-main">MonitorTFG</h1>
      </div>

      <nav className="flex-1 py-6 px-4 space-y-2">
        <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 text-text hover:bg-body hover:text-title rounded-lg transition-colors">
          <LayoutDashboard size={20} className="text-light group-hover:text-main" />
          <span className="font-medium">Panel Principal</span>
        </Link>
        <Link href="/servers" className="flex items-center gap-3 px-4 py-3 text-text hover:bg-body hover:text-title rounded-lg transition-colors group">
          <Server size={20} className="text-light group-hover:text-main" />
          <span className="font-medium">Servidores</span>
        </Link>
        <Link href="/alerts" className="flex items-center gap-3 px-4 py-3 text-text hover:bg-body hover:text-title rounded-lg transition-colors group">
          <Bell size={20} className="text-light group-hover:text-main" />
          <span className="font-medium">Alertas</span>
        </Link>
        
        {/* 🌟 MAGIA: Este botón solo sale si eres Administrador */}
        {usuario?.rol === 'admin' && (
          <Link href="/equipo" className="flex items-center gap-3 px-4 py-3 text-text hover:bg-body hover:text-title rounded-lg transition-colors group">
            <Users size={20} className="text-light group-hover:text-main" />
            <span className="font-medium">Mi Equipo</span>
          </Link>
        )}

        <Link href="/settings" className="flex items-center gap-3 px-4 py-3 text-text hover:bg-body hover:text-title rounded-lg transition-colors group">
          <Settings size={20} className="text-light group-hover:text-main" />
          <span className="font-medium">Ajustes</span>
        </Link>
      </nav>

      <div className="p-4 border-t border-border flex items-center justify-between">
        <ThemeToggle />
        <button 
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-2 text-red-500 hover:bg-body rounded-lg transition-colors"
        >
          <LogOut size={20} />
          <span className="font-medium text-sm">Salir</span>
        </button>
      </div>
    </aside>
  );
}