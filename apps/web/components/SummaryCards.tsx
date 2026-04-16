export function SummaryCards() {
  const cards = [
    { label: 'Avg Margin', value: '12.8%' },
    { label: 'Profit Today', value: '₽ 23 100' },
    { label: 'Low Stock', value: '7' },
    { label: 'Risky Items', value: '3' },
  ];
  return (
    <div className="grid grid-cols-4 gap-4">
      {cards.map((c) => (
        <div key={c.label} className="rounded-xl bg-white p-4 shadow">
          <div className="text-xs text-slate-500">{c.label}</div>
          <div className="text-xl font-semibold">{c.value}</div>
        </div>
      ))}
    </div>
  );
}
