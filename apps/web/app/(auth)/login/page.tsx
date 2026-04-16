'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';

export default function LoginPage() {
  const [email, setEmail] = useState('operator@test.com');
  const [password, setPassword] = useState('operator123');
  const [error, setError] = useState('');
  const setToken = useAuthStore((s) => s.setToken);
  const setRole = useAuthStore((s) => s.setRole);
  const router = useRouter();

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError('');
    const res = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      setError('Invalid credentials');
      return;
    }
    const data = await res.json();
    setToken(data.access_token);
    if (email.includes('admin')) setRole('admin');
    else if (email.includes('viewer')) setRole('viewer');
    else setRole('operator');
    router.push('/orders');
  }

  return (
    <main className="mx-auto mt-24 max-w-md rounded-xl bg-white p-6 shadow">
      <h1 className="mb-4 text-xl font-semibold">CalcSteam Admin Login</h1>
      <form className="space-y-3" onSubmit={submit}>
        <input className="w-full rounded border p-2" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="w-full rounded border p-2" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <div className="text-sm text-red-600">{error}</div>}
        <button className="w-full rounded bg-slate-900 p-2 text-white">Sign In</button>
      </form>
    </main>
  );
}
