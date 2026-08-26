"use client";

import Link from 'next/link';
import { 
  Activity, 
  ShieldCheck, 
  Cpu, 
  BellRing, 
  ChevronRight, 
  Mail, 
  ArrowRight, 
  Server, 
  Terminal, 
  SlidersHorizontal 
} from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0b0f19] text-slate-300 font-sans selection:bg-indigo-500 selection:text-white">
      {/* 1. HEADER / NAVIGATION */}
      <nav className="border-b border-slate-800 bg-[#0b0f19]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="p-2 bg-indigo-500/10 text-indigo-400 rounded-lg border border-indigo-500/20">
              <Activity size={20} className="animate-pulse" />
            </span>
            <span className="text-xl font-bold text-white tracking-tight">SITEM</span>
            <span className="text-xs font-mono bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
              SaaS B2B
            </span>
          </div>

          <div className="flex items-center gap-4">
            <Link 
              href="/login" 
              className="text-sm font-medium text-slate-400 hover:text-white transition-colors"
            >
              Acceso Empresa
            </Link>
            <Link 
              href="/login" 
              className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-all shadow-md shadow-indigo-600/10 cursor-pointer"
            >
              <span>Panel de Control</span>
              <ChevronRight size={16} />
            </Link>
          </div>
        </div>
      </nav>

      {/* 2. HERO SECTION */}
      <section className="relative overflow-hidden pt-20 pb-24 px-6 border-b border-slate-900 bg-gradient-to-b from-[#0b0f19] via-[#0d1425] to-[#0b0f19]">
        {/* Decorative background glows */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-500/5 blur-[120px] rounded-full pointer-events-none"></div>
        <div className="absolute top-1/3 left-1/4 w-[300px] h-[300px] bg-sky-500/5 blur-[100px] rounded-full pointer-events-none"></div>

        <div className="max-w-4xl mx-auto text-center space-y-6 relative z-10">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-500/10 text-indigo-400 rounded-full text-xs font-semibold border border-indigo-500/20 tracking-wide uppercase">
            <ShieldCheck size={14} /> Exclusivo para Clientes Corporativos
          </span>
          
          <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-none">
            Monitorización de Infraestructura <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              en Tiempo Real
            </span>
          </h1>
          
          <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto font-light leading-relaxed">
            SITEM es una plataforma SaaS B2B blindada para la monitorización de servidores, 
            análisis de métricas de hardware y envío inteligente de alertas críticas.
          </p>

          <div className="pt-6 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link 
              href="/login" 
              className="w-full sm:w-auto flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-6 py-3.5 rounded-xl transition-all shadow-lg shadow-indigo-600/25 cursor-pointer text-sm"
            >
              <span>Acceder al Panel Corporativo</span>
              <ArrowRight size={18} />
            </Link>
            <a 
              href="#contacto" 
              className="w-full sm:w-auto flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-slate-300 font-medium px-6 py-3.5 rounded-xl border border-slate-800 hover:border-slate-700 transition-all text-sm cursor-pointer"
            >
              <span>Solicitar Alta de Empresa</span>
            </a>
          </div>
        </div>
      </section>

      {/* 3. PRODUCT ORIENTATION (B2B NOTICE) */}
      <section className="py-16 px-6 max-w-7xl mx-auto">
        <div className="bg-[#121a2e]/50 border border-indigo-500/10 rounded-2xl p-8 sm:p-10 flex flex-col md:flex-row items-center justify-between gap-8 backdrop-blur-sm">
          <div className="space-y-4 max-w-2xl text-left">
            <h2 className="text-2xl font-bold text-white">Plataforma Exclusiva B2B</h2>
            <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
              El registro público de usuarios está deshabilitado. SITEM opera bajo un modelo de 
              **aislamiento Multi-tenant**. Cada empresa cuenta con un entorno aislado donde se almacenan sus métricas, 
              servidores y configuraciones de alertas de forma totalmente segura.
            </p>
            <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
              Si tu empresa ya ha sido dada de alta por la administración central de SITEM, puedes acceder 
              utilizando las credenciales proporcionadas.
            </p>
          </div>
          <div className="w-full md:w-auto flex flex-col gap-3 min-w-[200px]">
            <Link 
              href="/login" 
              className="w-full text-center bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 font-medium px-5 py-3 rounded-xl border border-indigo-500/20 transition-all text-sm cursor-pointer"
            >
              Iniciar Sesión
            </Link>
          </div>
        </div>
      </section>

      {/* 4. HOW IT WORKS */}
      <section className="py-20 px-6 bg-[#0a0d16] border-t border-slate-900">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center space-y-3">
            <h2 className="text-3xl font-bold text-white">¿Cómo Funciona SITEM?</h2>
            <p className="text-slate-400 max-w-xl mx-auto text-sm sm:text-base">
              Flujo integrado desde la recolección física en tus máquinas hasta el panel de administración.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="bg-[#121a2e]/30 border border-slate-800/60 p-8 rounded-2xl text-left space-y-4 relative">
              <span className="absolute -top-4 left-6 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">1</span>
              <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl inline-block border border-indigo-500/20">
                <Terminal size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">1. Instalación del Agente</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Descarga el agente ejecutable ligero para Windows o Linux en tus máquinas de destino. 
                El daemon se ejecuta en segundo plano recopilando métricas de hardware de forma automática.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-[#121a2e]/30 border border-slate-800/60 p-8 rounded-2xl text-left space-y-4 relative">
              <span className="absolute -top-4 left-6 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">2</span>
              <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl inline-block border border-indigo-500/20">
                <Server size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">2. Conexión Segura</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                El agente se vincula a tu cuenta mediante un Token de seguridad SHA-256 único y seguro. Las métricas se 
                envían encriptadas al backend centralizado del sistema mediante peticiones HTTPS seguras.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-[#121a2e]/30 border border-slate-800/60 p-8 rounded-2xl text-left space-y-4 relative">
              <span className="absolute -top-4 left-6 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">3</span>
              <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl inline-block border border-indigo-500/20">
                <BellRing size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">3. Notificación y Control</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Si alguna métrica supera tus umbrales estáticos personalizados, se registran alertas inmediatas 
                y se te notifica al instante por canales de Slack, Discord o Correo electrónico.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. MAIN FEATURES GRID */}
      <section className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-bold text-white">Características Principales</h2>
          <p className="text-slate-400 max-w-xl mx-auto text-sm sm:text-base">
            Todo lo necesario para mantener tu infraestructura monitorizada y segura en un único portal.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-6 bg-[#121a2e]/25 border border-slate-800/80 rounded-xl text-left space-y-3">
            <span className="text-indigo-400"><ShieldCheck size={28} /></span>
            <h4 className="text-base font-bold text-white">Seguridad Multi-Tenant</h4>
            <p className="text-xs text-slate-400 leading-relaxed">Aislamiento lógico a nivel de base de datos para que los datos de tu empresa permanezcan estrictamente inaccesibles.</p>
          </div>

          <div className="p-6 bg-[#121a2e]/25 border border-slate-800/80 rounded-xl text-left space-y-3">
            <span className="text-indigo-400"><SlidersHorizontal size={28} /></span>
            <h4 className="text-base font-bold text-white">Umbrales Dinámicos</h4>
            <p className="text-xs text-slate-400 leading-relaxed">Establece límites de alarma para CPU, Memoria RAM, uso de disco y latencia de red de forma granular para cada servidor.</p>
          </div>

          <div className="p-6 bg-[#121a2e]/25 border border-slate-800/80 rounded-xl text-left space-y-3">
            <span className="text-indigo-400"><BellRing size={28} /></span>
            <h4 className="text-base font-bold text-white">Alertas Multi-Canal</h4>
            <p className="text-xs text-slate-400 leading-relaxed">Integración nativa con Webhooks de Discord, Slack y servidores de correo electrónico para notificar incidencias al instante.</p>
          </div>

          <div className="p-6 bg-[#121a2e]/25 border border-slate-800/80 rounded-xl text-left space-y-3">
            <span className="text-indigo-400"><Cpu size={28} /></span>
            <h4 className="text-base font-bold text-white">Control Granular</h4>
            <p className="text-xs text-slate-400 leading-relaxed">Roles diferenciados para administradores (gestión total de empresa y accesos) y técnicos (supervisión asignada de máquinas).</p>
          </div>
        </div>
      </section>

      {/* 6. CONTACT SECTION */}
      <section id="contacto" className="py-20 px-6 bg-[#0a0d16] border-t border-slate-900">
        <div className="max-w-3xl mx-auto bg-gradient-to-br from-[#121a2e]/80 to-[#0e1424]/80 border border-slate-800 p-8 sm:p-12 rounded-3xl text-center space-y-8 relative overflow-hidden backdrop-blur-md">
          {/* Decorative radial blur */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-600/5 blur-[80px] rounded-full pointer-events-none"></div>
          
          <div className="space-y-3 relative z-10">
            <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-2xl inline-block border border-indigo-500/20 mb-2">
              <Mail size={24} />
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">¿Quieres usar SITEM en tu empresa?</h2>
            <p className="text-slate-400 text-sm sm:text-base max-w-lg mx-auto font-light leading-relaxed">
              Solicita el alta de tu empresa en nuestra base de datos. Nos pondremos en contacto contigo para asignarte una cuenta de Administrador raíz.
            </p>
          </div>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-4 relative z-10 max-w-md mx-auto">
            <a 
              href="mailto:soporte@sitem.com" 
              className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-6 py-3.5 rounded-xl transition-all shadow-md text-sm cursor-pointer flex items-center justify-center gap-2"
            >
              <Mail size={16} />
              <span>Contactar con Soporte</span>
            </a>
            <div className="text-xs text-slate-500 font-mono">
              O escríbenos directamente a: <br className="sm:hidden" />
              <span className="text-indigo-400 font-semibold">soporte@sitem.com</span>
            </div>
          </div>
        </div>
      </section>

      {/* 7. FOOTER */}
      <footer className="py-12 border-t border-slate-900 bg-[#0b0f19] text-center text-xs text-slate-500 px-6">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} SITEM - Sistema de Monitorización de Infraestructuras. Todos los derechos reservados.</p>
          <div className="flex gap-4">
            <Link href="/login" className="hover:text-slate-300 transition-colors">Acceso de Clientes</Link>
            <span>•</span>
            <a href="#contacto" className="hover:text-slate-300 transition-colors">Solicitar Demo</a>
          </div>
        </div>
      </footer>
    </main>
  );
}