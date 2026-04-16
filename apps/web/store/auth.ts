'use client';

import { create } from 'zustand';
import { UserRole } from '@/lib/types';

interface AuthState {
  role: UserRole;
  token: string;
  setRole: (r: UserRole) => void;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  role: 'operator',
  token: '',
  setRole: (role) => set({ role }),
  setToken: (token) => set({ token }),
}));
