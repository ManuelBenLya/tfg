import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

// Definimos la interfaz de lo que esperamos recibir
interface DiskData {
  name: string;
  value: number;
}

export default function DiskChart({ data }: { data: DiskData[] }) {
  // Colores: Azul (SO), Verde (BD), Naranja (Logs), Violeta (Otros), Gris oscuro (Libre)
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#3f3f46'];

  return (
    <div className="h-64 w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={5}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: any) => [`${value} GB`, 'Espacio']}
            contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#f4f4f5' }}
            itemStyle={{ color: '#f4f4f5' }}
          />
          <Legend verticalAlign="bottom" height={36} iconType="circle" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}