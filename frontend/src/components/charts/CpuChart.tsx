"use client";

import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

// Definimos la estructura de los datos que espera recibir la gráfica
interface CpuChartProps {
  data: { time: string; cpu: number }[];
}

export default function CpuChart({ data }: CpuChartProps) {
  const mainColor = "#1083D6"; 

  return (
    <div className="h-72 w-full mt-6">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={mainColor} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={mainColor} stopOpacity={0}/>
            </linearGradient>
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" opacity={0.5} />
          <XAxis dataKey="time" stroke="var(--light-text-color)" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="var(--light-text-color)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}%`} />
          
          <Tooltip 
            contentStyle={{ backgroundColor: 'var(--surface-color)', borderColor: 'var(--border-color)', color: 'var(--text-color)', borderRadius: '8px' }}
            itemStyle={{ color: mainColor, fontWeight: 'bold' }}
          />
          
          <Area type="monotone" dataKey="cpu" name="Uso de CPU" stroke={mainColor} strokeWidth={3} fillOpacity={1} fill="url(#colorCpu)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}