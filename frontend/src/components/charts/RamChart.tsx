"use client";

// Si usas recharts, mantén tus importaciones. Suele ser algo así:
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// 1. Añadimos { data }: { data: any[] } para que acepte los datos del padre
export default function RamChart({ data }: { data: any[] }) {
  return (
    <div className="h-64 w-full">
      {/* 2. Le pasamos el data al contenedor de la gráfica */}
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
          <XAxis dataKey="time" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e1e2d', borderColor: '#2b2b40', color: '#fff' }}
            itemStyle={{ color: '#10b981' }} // Un color verdecito para la RAM
          />
          {/* 3. CLAVE: le decimos que dibuje el valor de "ram" */}
          <Area type="monotone" dataKey="ram" stroke="#10b981" fill="#10b981" fillOpacity={0.2} strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}