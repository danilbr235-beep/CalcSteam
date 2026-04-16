import { StatusBadge } from '@/components/StatusBadge';

const rows = [
  { c: 'EUR', n: 20, p: 1590, combo: 'SGD20+MYR5', status: 'ok' },
  { c: 'USD', n: 50, p: 3690, combo: 'SGD50', status: 'low_margin' },
  { c: 'KZT', n: 5000, p: 920, combo: 'MYR10', status: 'manual_review' },
];

export default function PricingPage() {
  return (
    <main className="p-6">
      <h1 className="mb-4 text-2xl font-bold">Pricing Matrix</h1>
      <table className="w-full overflow-hidden rounded-xl bg-white shadow">
        <thead className="bg-slate-50 text-left text-sm">
          <tr><th className="p-3">Currency</th><th>Nominal</th><th>Recommended ₽</th><th>Combo</th><th>Status</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={`${r.c}-${r.n}`} className="border-t">
              <td className="p-3">{r.c}</td><td>{r.n}</td><td>{r.p}</td><td>{r.combo}</td><td><StatusBadge status={r.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
