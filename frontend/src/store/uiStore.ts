import { create } from 'zustand';

interface UIStore {
  showLogModal: boolean;
  openLogModal: () => void;
  closeLogModal: () => void;
  logVersion: number;
  notifyLogCreated: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  showLogModal: false,
  openLogModal: () => set({ showLogModal: true }),
  closeLogModal: () => set({ showLogModal: false }),
  logVersion: 0,
  notifyLogCreated: () => set((s) => ({ logVersion: s.logVersion + 1 })),
}));
