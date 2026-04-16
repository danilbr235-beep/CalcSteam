const cls: Record<string, string> = {
  ok: 'bg-emerald-100 text-emerald-700',
  low_margin: 'bg-amber-100 text-amber-700',
  loss: 'bg-red-100 text-red-700',
  no_combo: 'bg-red-100 text-red-700',
  stale_rate: 'bg-orange-100 text-orange-700',
  low_stock: 'bg-yellow-100 text-yellow-700',
  manual_review: 'bg-indigo-100 text-indigo-700',
};

export function StatusBadge({ status }: { status: string }) {
  return <span className={`rounded px-2 py-1 text-xs ${cls[status] || cls.ok}`}>{status}</span>;
}
