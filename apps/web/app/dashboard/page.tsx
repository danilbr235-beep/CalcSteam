import { SummaryCards } from '@/components/SummaryCards';

export default function DashboardPage() {
  return (
    <main className="space-y-4 p-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <SummaryCards />
      <div className="rounded-xl bg-white p-4 shadow">Charts (Recharts placeholder)</div>
    </main>
  );
}
