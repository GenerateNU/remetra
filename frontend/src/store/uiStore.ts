import { create } from 'zustand';
import { ModalStep } from '../types/logs';

interface UIStore {
  showLogModal: boolean;
  initialLogType: ModalStep;
  initialLogTimestamp: Date; // a fresh Date on every open, so the forms reset to it
  openLogModal: (logType?: ModalStep, timestamp?: Date) => void;
  closeLogModal: () => void;
  logVersion: number;
  notifyLogCreated: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  showLogModal: false,
  initialLogType: 'select_type',
  initialLogTimestamp: new Date(),
  openLogModal: (logType = 'select_type', timestamp) =>
    set({ showLogModal: true, initialLogType: logType, initialLogTimestamp: timestamp ?? new Date() }),
  closeLogModal: () => set({ showLogModal: false }),
  logVersion: 0,
  notifyLogCreated: () => set((s) => ({ logVersion: s.logVersion + 1 })),
}));
