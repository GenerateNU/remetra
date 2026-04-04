import { create } from 'zustand';

interface UIStore {
  showLogModal: boolean;
  openLogModal: () => void;
  closeLogModal: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  showLogModal: false,
  openLogModal: () => set({ showLogModal: true }),
  closeLogModal: () => set({ showLogModal: false }),
}));
