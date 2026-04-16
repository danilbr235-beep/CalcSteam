import { CodeItem, OrderRow } from './types';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function authHeaders(token?: string): HeadersInit {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function getInventory(token?: string): Promise<CodeItem[]> {
  const res = await fetch(`${API}/inventory/codes`, { headers: authHeaders(token), cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to load inventory');
  return res.json();
}

export async function patchCodeStatus(id: number, status: string, token?: string) {
  const res = await fetch(`${API}/inventory/codes/${id}/status`, {
    method: 'PATCH',
    headers: authHeaders(token),
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error('Failed to patch status');
  return res.json();
}

export async function getOrders(token?: string): Promise<OrderRow[]> {
  const res = await fetch(`${API}/orders`, { headers: authHeaders(token), cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to load orders');
  return res.json();
}

export async function reserveOrder(orderId: number, codeIds: number[], token?: string) {
  const res = await fetch(`${API}/orders/${orderId}/reserve`, {
    method: 'POST',
    headers: { ...authHeaders(token), 'X-Idempotency-Key': `web-${orderId}-${Date.now()}` },
    body: JSON.stringify({ code_ids: codeIds }),
  });
  if (!res.ok) throw new Error('Reserve failed');
  return res.json();
}

export async function fulfillOrder(orderId: number, token?: string) {
  const res = await fetch(`${API}/orders/${orderId}/fulfill`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Fulfill failed');
  return res.json();
}

export async function markOrderProblem(orderId: number, token?: string) {
  const res = await fetch(`${API}/orders/${orderId}/problem`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Mark problem failed');
  return res.json();
}
