import { create } from 'zustand';
import { ModalStep } from '../types/logs';

interface UIStore {
  showLogModal: boolean;
  initialLogType: ModalStep;
  openLogModal: (logType?: ModalStep) => void;
  closeLogModal: () => void;
  logVersion: number;
  notifyLogCreated: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  showLogModal: false,
  initialLogType: 'select_type',
  openLogModal: (logType = 'select_type') => set({ showLogModal: true, initialLogType: logType }),
  closeLogModal: () => set({ showLogModal: false }),
  logVersion: 0,
  notifyLogCreated: () => set((s) => ({ logVersion: s.logVersion + 1 })),
}));
