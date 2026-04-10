import React, { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { ShoppingBag, Users, Wallet, MapPin } from 'lucide-react';

// Твои данные подключения
const SUPABASE_URL = "https://nxavfiprlksneqwbmhfl.supabase.co";
const SUPABASE_KEY = "sb_publishable_4Av4JQLr4D8mUG8Ktw8fiA_5U1ZVdXx";
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

function App() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  async function fetchOrders() {
    const { data, error } = await supabase.from('orders').select('*').gt('total_sum', 50000);
    if (error) console.log('error', error);
    else setOrders(data);
    setLoading(false);
  }

  const totalSum = orders.reduce((sum, order) => sum + (order.total_sum || 0), 0);
  const avgOrder = orders.length > 0 ? (totalSum / orders.length).toFixed(0) : 0;

  // Данные для графика по городам
  const chartData = Object.values(orders.reduce((acc, order) => {
    acc[order.city] = acc[order.city] || { name: order.city, total: 0 };
    acc[order.city].total += order.total_sum;
    return acc;
  }, {}));

  if (loading) return <div className="flex h-screen items-center justify-center">Загрузка...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">GBC Analytics Dashboard</h1>
        <p className="text-gray-500">Данные синхронизированы из RetailCRM в Supabase</p>
      </header>

      {/* Карточки с метриками */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard icon={<ShoppingBag />} label="Всего заказов" value={orders.length} color="bg-blue-500" />
        <StatCard icon={<Wallet />} label="Выручка" value={`${totalSum.toLocaleString()} ₸`} color="bg-green-500" />
        <StatCard icon={<Users />} label="Средний чек" value={`${avgOrder} ₸`} color="bg-purple-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* График */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <MapPin size={20}/> Продажи по городам
          </h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="total" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Таблица */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <h2 className="text-xl font-semibold mb-4">Последние заказы</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b text-gray-400 text-sm">
                  <th className="pb-3 font-medium">Имя</th>
                  <th className="pb-3 font-medium">Город</th>
                  <th className="pb-3 font-medium text-right">Сумма</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {orders.slice(0, 10).map((order) => (
                  <tr key={order.id} className="text-sm text-gray-700">
                    <td className="py-3">{order.first_name} {order.last_name}</td>
                    <td className="py-3">{order.city}</td>
                    <td className="py-3 text-right font-semibold">{order.total_sum} ₸</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
      <div className={`${color} p-3 rounded-lg text-white`}>{icon}</div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
    </div>
  );
}

export default App;
