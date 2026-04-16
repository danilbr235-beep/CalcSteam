'use client';

import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fulfillOrder, getInventory, getOrders, markOrderProblem, reserveOrder } from '@/lib/api';
import { useAuthStore } from '@/store/auth';

export default function OrdersPage() {
  const role = useAuthStore((s) => s.role);
  const token = useAuthStore((s) => s.token);
  const qc = useQueryClient();
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedOrder, setSelectedOrder] = useState<number | null>(null);
  const [selectedCodeId, setSelectedCodeId] = useState<number | null>(null);

  const ordersQ = useQuery({ queryKey: ['orders'], queryFn: () => getOrders(token) });
  const invQ = useQuery({ queryKey: ['inventory'], queryFn: () => getInventory(token) });

  const reserveM = useMutation({
    mutationFn: (args: { orderId: number; codeIds: number[] }) => reserveOrder(args.orderId, args.codeIds, token),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['orders'] }),
  });

  const fulfillM = useMutation({
    mutationFn: (orderId: number) => fulfillOrder(orderId, token),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['orders'] }),
  });

  const problemM = useMutation({
    mutationFn: (orderId: number) => markOrderProblem(orderId, token),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['orders'] }),
  });

  const rows = useMemo(() => {
    const data = ordersQ.data || [];
    return statusFilter === 'all' ? data : data.filter((r) => r.status === statusFilter);
  }, [ordersQ.data, statusFilter]);

  const availableCodes = (invQ.data || []).filter((c) => c.status === 'new');

  return (
    <main className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Orders</h1>
        <select className="rounded border px-2 py-1" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">all statuses</option>
          <option value="new">new</option>
          <option value="reserved">reserved</option>
          <option value="fulfilled">fulfilled</option>
          <option value="problem">problem</option>
          <option value="completed">completed</option>
        </select>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 rounded-xl bg-white shadow">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left">
              <tr>
                <th className="p-3">ID</th><th>External Ref</th><th>Status</th><th>Revenue ₽</th><th>Manual</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="cursor-pointer border-t hover:bg-slate-50" onClick={() => setSelectedOrder(r.id)}>
                  <td className="p-3">{r.id}</td>
                  <td>{r.external_ref}</td>
                  <td>{r.status}</td>
                  <td>{r.expected_revenue_rub}</td>
                  <td>{r.manual_review ? 'yes' : 'no'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <aside className="rounded-xl bg-white p-4 shadow">
          <h2 className="mb-3 font-semibold">Order actions</h2>
          {selectedOrder ? (
            <div className="space-y-3">
              <div className="text-xs text-slate-500">Order #{selectedOrder}</div>
              <select className="w-full rounded border px-2 py-1" value={selectedCodeId ?? ''} onChange={(e) => setSelectedCodeId(Number(e.target.value))}>
                <option value="">select code</option>
                {availableCodes.map((c) => (
                  <option key={c.id} value={c.id}>{c.id} · {c.masked_code}</option>
                ))}
              </select>

              {role === 'viewer' ? (
                <div className="rounded bg-slate-100 p-2 text-xs text-slate-500">viewer cannot reserve/fulfill/problem</div>
              ) : (
                <>
                  <button
                    className="w-full rounded bg-slate-900 px-3 py-2 text-white"
                    disabled={!selectedCodeId || reserveM.isPending}
                    onClick={() => selectedCodeId && reserveM.mutate({ orderId: selectedOrder, codeIds: [selectedCodeId] })}
                  >
                    Reserve
                  </button>
                  <button className="w-full rounded border px-3 py-2" onClick={() => fulfillM.mutate(selectedOrder)}>
                    Fulfill
                  </button>
                  <button className="w-full rounded border border-red-300 px-3 py-2 text-red-700" onClick={() => problemM.mutate(selectedOrder)}>
                    Mark Problem
                  </button>
                </>
              )}
            </div>
          ) : (
            <div className="text-sm text-slate-500">Select order from table</div>
          )}
        </aside>
      </div>
    </main>
  );
}
