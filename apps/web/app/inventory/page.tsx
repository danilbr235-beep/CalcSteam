'use client';

import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getInventory, patchCodeStatus } from '@/lib/api';
import { useAuthStore } from '@/store/auth';

const statuses = ['new', 'reserved', 'sent', 'redeemed', 'problem', 'archived'];

export default function InventoryPage() {
  const role = useAuthStore((s) => s.role);
  const token = useAuthStore((s) => s.token);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const qc = useQueryClient();

  const q = useQuery({ queryKey: ['inventory'], queryFn: () => getInventory(token) });
  const patch = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => patchCodeStatus(id, status, token),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['inventory'] }),
  });

  const rows = useMemo(() => {
    const data = q.data || [];
    return statusFilter === 'all' ? data : data.filter((r) => r.status === statusFilter);
  }, [q.data, statusFilter]);

  return (
    <main className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Inventory</h1>
        <select className="rounded border px-2 py-1" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">all statuses</option>
          {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="rounded-xl bg-white shadow">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left">
            <tr>
              <th className="p-3">ID</th>
              <th>Masked Code</th>
              <th>Status</th>
              <th>Cost ₽</th>
              <th>Batch</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-t">
                <td className="p-3">{r.id}</td>
                <td>{r.masked_code}</td>
                <td>{r.status}</td>
                <td>{r.purchase_cost_rub}</td>
                <td>{r.batch_id}</td>
                <td>
                  {role === 'viewer' ? (
                    <span className="text-slate-400">read-only</span>
                  ) : (
                    <div className="flex gap-2">
                      <button className="rounded border px-2 py-1" onClick={() => patch.mutate({ id: r.id, status: 'reserved' })}>reserve</button>
                      <button className="rounded border px-2 py-1" onClick={() => patch.mutate({ id: r.id, status: 'problem' })}>problem</button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
