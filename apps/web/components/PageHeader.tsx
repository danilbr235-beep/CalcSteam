'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/auth';

const items = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/pricing', label: 'Pricing' },
  { href: '/inventory', label: 'Inventory' },
  { href: '/orders', label: 'Orders' },
  { href: '/settings', label: 'Settings' },
  { href: '/reports', label: 'Reports' },
];

export function PageHeader() {
  const pathname = usePathname();
  const role = useAuthStore((s) => s.role);
  const setRole = useAuthStore((s) => s.setRole);

  return (
    <header className="border-b bg-white px-6 py-3">
      <div className="mb-2 flex items-center justify-between">
        <div className="font-bold">CalcSteam Admin</div>
        <div className="flex items-center gap-2 text-sm">
          <span className="text-slate-500">Role</span>
          <select className="rounded border px-2 py-1" value={role} onChange={(e) => setRole(e.target.value as any)}>
            <option value="admin">admin</option>
            <option value="operator">operator</option>
            <option value="viewer">viewer</option>
          </select>
        </div>
      </div>
      <nav className="flex gap-3 text-sm">
        {items.map((i) => (
          <Link key={i.href} href={i.href} className={pathname === i.href ? 'font-semibold text-slate-900' : 'text-slate-500'}>
            {i.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
