"use client";

import { useState, useEffect } from 'react';
import { ChevronDown, Monitor, Layers, Server, LogOut, Clock } from 'lucide-react';
import CpuChart from "../../../components/charts/CpuChart";
import RamChart from "../../../components/charts/RamChart";
import NetworkChart from "../../../components/charts/NetworkChart";
import DiskChart from "../../../components/charts/DiskChart";
import { getServidores } from '@/services/servidorService'; 
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();
  
  const [servidoresReales, setServidoresReales] = useState<any[]>([]);
  const [metricasReales, setMetricasReales] = useState<any[]>([]);
  const [errorBackend, setErrorBackend] = useState('');

  const [resolucion, setResolucion] = useState<'segundos' | 'minutos'>('segundos');
  
  const [rangoTiempo, setRangoTiempo] = useState('1h');

  const opcionesTiempo = [
    { valor: '15m', etiqueta: '15 Min' },
    { valor: '1h', etiqueta: '1 Hora' },
    { valor: '24h', etiqueta: '24 Horas' },
    { valor: '7d', etiqueta: '7 Días' },
  ];

  const filterOptions = [
    { id: 'all', name: 'Toda la Infraestructura', type: 'global', icon: Layers },
    ...servidoresReales.map(srv => ({
      id: srv.id,
      name: srv.nombre,
      type: 'server',
      icon: Server
    }))
  ];

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedView, setSelectedView] = useState(filterOptions[0]);

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const token = localStorage.getItem('token');
        const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
          .replace(/\/$/, '').replace(/\/api$/, '');

        const dataServidores = await getServidores();
        
        const resMetricas = await fetch(`${API_BASE}/api/metricas/?rango=${rangoTiempo}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (resMetricas.ok) {
          const dataMetricas = await resMetricas.json();
          setMetricasReales(dataMetricas);
        }

        setServidoresReales(dataServidores);
        setErrorBackend('');
      } catch (err) {
        setErrorBackend('No se pudo conectar con la API.');
      }
    };

    cargarDatos();

    const intervalo = setInterval(() => {
      cargarDatos();
    }, 5000);

    return () => clearInterval(intervalo);
  }, [rangoTiempo]);

  const vistaActual = filterOptions.find(opt => opt.id === selectedView.id) || filterOptions[0];

  const metricasFiltradas = vistaActual.id === 'all' 
    ? metricasReales 
    : metricasReales.filter(m => m.servidor_id === vistaActual.id);

  const agrupadoPorHora = metricasFiltradas.reduce((acc: any, metrica: any) => {
    const fecha = new Date(metrica.tiempo);
    
    // 🌟 CORRECCIÓN DE ZONA HORARIA: Forzamos la hora local del navegador
    const opcionesFecha: Intl.DateTimeFormatOptions = { 
      hour: '2-digit', 
      minute: '2-digit',
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone 
    };
    if (resolucion === 'segundos') {
      opcionesFecha.second = '2-digit';
    }
    
    const horaFormateada = fecha.toLocaleTimeString([], opcionesFecha);
    
    if (!acc[horaFormateada]) {
      acc[horaFormateada] = { sumaCpu: 0, sumaRam: 0, sumaNetwork: 0, count: 0 };
    }
    acc[horaFormateada].sumaCpu += metrica.cpu_usage_pct;
    acc[horaFormateada].sumaRam += (metrica.ram_usage_mb / 1024); 
    acc[horaFormateada].sumaNetwork += metrica.network_latency_ms;
    acc[horaFormateada].count += 1;
    
    return acc;
  }, {});

  const datosGraficas = Object.keys(agrupadoPorHora).length > 0
    ? Object.keys(agrupadoPorHora).map(hora => {
        const datos = agrupadoPorHora[hora];
        return {
          time: hora,
          cpu: Number((datos.sumaCpu / datos.count).toFixed(1)),
          ram: Number((datos.sumaRam / datos.count).toFixed(2)),
          network: Number((datos.sumaNetwork / datos.count).toFixed(1))
        };
      })
    : [{ time: '00:00', cpu: 0, ram: 0, network: 0 }, { time: '00:01', cpu: 0, ram: 0, network: 0 }]; 

  const cpuActual = datosGraficas[datosGraficas.length - 1]?.cpu || 0;
  const ultimaMetrica = metricasFiltradas[metricasFiltradas.length - 1];

  const datosDisco = ultimaMetrica ? [
    { name: 'Sistema Operativo', value: Number(ultimaMetrica.disk_os_gb || 0) },
    { name: 'Bases de Datos', value: Number(ultimaMetrica.disk_db_gb || 0) },
    { name: 'Archivos de Log', value: Number(ultimaMetrica.disk_logs_gb || 0) },
    { name: 'Espacio Libre', value: Number(ultimaMetrica.disk_free_gb || 100) }
  ] : [];

  return (
    <div className="space-y-6">
      <header className="flex flex-col xl:flex-row xl:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-title">Resumen del Sistema</h1>
          <p className="text-text mt-2">Visión general de la infraestructura monitorizada.</p>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3">
          
          <div className="flex items-center bg-surface border border-border rounded-lg p-1 shadow-sm w-full sm:w-auto">
            <Clock size={16} className="text-light mx-2" />
            {opcionesTiempo.map((opcion) => (
              <button
                key={opcion.valor}
                onClick={() => setRangoTiempo(opcion.valor)}
                className={`px-3 py-2 text-xs font-medium rounded-md transition-all flex-1 sm:flex-none ${
                  rangoTiempo === opcion.valor
                    ? 'bg-body text-main shadow-sm border border-border'
                    : 'text-light hover:text-title hover:bg-body/50'
                }`}
              >
                {opcion.etiqueta}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-auto">
            <button 
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-3 bg-surface border border-border px-4 py-2.5 rounded-lg shadow-sm hover:border-main transition-colors text-title min-w-[250px] justify-between w-full"
            >
              <div className="flex items-center gap-2">
                <vistaActual.icon size={18} className="text-main" />
                <span className="font-medium">{vistaActual.name}</span>
              </div>
              <ChevronDown size={18} className={`text-light transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {isDropdownOpen && (
              <div className="absolute right-0 top-full mt-2 w-full bg-surface border border-border rounded-lg shadow-lg overflow-hidden z-20 max-h-64 overflow-y-auto">
                {filterOptions.map((option) => (
                  <button
                    key={option.id}
                    onClick={() => {
                      setSelectedView(option);
                      setIsDropdownOpen(false);
                    }}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-body
                      ${vistaActual.id === option.id ? 'bg-body text-main font-medium border-l-2 border-main' : 'text-text border-l-2 border-transparent'}
                    `}
                  >
                    <option.icon size={18} className={vistaActual.id === option.id ? 'text-main' : 'text-light'} />
                    {option.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </header>

      {errorBackend && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-500 text-sm p-3 rounded-lg">
          {errorBackend}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm transition-colors duration-200">
          <h3 className="text-light font-medium">{vistaActual.type === 'server' ? 'Procesos Activos' : 'Servidores Registrados'}</h3>
          <p className="text-3xl font-bold text-title mt-2">
            {vistaActual.type === 'global' ? servidoresReales.length : '124'}
          </p>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm transition-colors duration-200">
          <h3 className="text-light font-medium">Alertas Pendientes</h3>
          <p className="text-3xl font-bold text-red-500 mt-2">0</p>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm transition-colors duration-200">
          <h3 className="text-light font-medium">Uso {vistaActual.type === 'global' ? 'Medio ' : ''}CPU</h3>
          <p className="text-3xl font-bold text-main mt-2">{cpuActual}%</p>
        </div>
      </div>

      <div className="bg-surface p-6 rounded-xl border border-border shadow-sm transition-colors duration-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-title font-semibold text-lg">Nodos Conectados (FastAPI + SQLite)</h3>
        </div>
        {servidoresReales.length === 0 ? (
          <p className="text-light text-sm">No hay servidores registrados en la base de datos.</p>
        ) : (
          <ul className="divide-y divide-border">
            {servidoresReales.map((srv: any) => (
              <li key={srv.id} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-body rounded-lg">
                    <Server size={18} className="text-main" />
                  </div>
                  <div>
                    <p className="font-medium text-title">{srv.nombre}</p>
                    <p className="text-xs text-light font-mono">ID: {srv.id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono bg-body text-text px-2 py-1 rounded border border-border">
                    IP: {srv.ip}
                  </span>
                  <span className="flex items-center gap-1 text-xs font-medium text-green-500 bg-green-500/10 px-2 py-1 rounded border border-green-500/20">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                    Online
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="bg-surface p-6 rounded-xl border border-border shadow-sm transition-colors duration-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-4">
          <div className="flex items-center gap-3">
            <h3 className="text-title font-semibold text-lg">Rendimiento de CPU</h3>
            <span className="text-xs font-medium bg-body text-light px-2.5 py-1 rounded-full border border-border">
              {vistaActual.name}
            </span>
          </div>
          
          <div className="flex items-center bg-body p-1 rounded-lg border border-border">
            <button
              onClick={() => setResolucion('segundos')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                resolucion === 'segundos' 
                  ? 'bg-surface text-main shadow-sm border border-border' 
                  : 'text-light hover:text-text'
              }`}
            >
              Exacto (Segs)
            </button>
            <button
              onClick={() => setResolucion('minutos')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                resolucion === 'minutos' 
                  ? 'bg-surface text-main shadow-sm border border-border' 
                  : 'text-light hover:text-text'
              }`}
            >
              Media (Mins)
            </button>
          </div>
        </div>
        
        <CpuChart data={datosGraficas} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm transition-colors duration-200">
          <h3 className="text-title font-semibold text-lg">Distribución de Memoria RAM (GB)</h3>
          <RamChart data={datosGraficas} />
        </div>
        
        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm transition-colors duration-200">
          <h3 className="text-title font-semibold text-lg">Tráfico de Red (ms)</h3>
          <NetworkChart data={datosGraficas} />
        </div>

        <div className="bg-surface p-6 rounded-xl border border-border shadow-sm transition-colors duration-200">
          <h3 className="text-title font-semibold text-lg">Almacenamiento de Disco</h3>
          {datosDisco.length > 0 ? (
            <DiskChart data={datosDisco} />
          ) : (
            <div className="flex h-64 items-center justify-center text-light text-sm">
              Esperando datos del servidor...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}