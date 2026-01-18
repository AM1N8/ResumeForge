import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface SettingsState {
    projectCount: number;
    resumeLanguage: string;
    verbosity: string;
    primaryColor: string;
    updateSettings: (settings: Partial<SettingsState>) => void;
    resetSettings: () => void;
}

export const useSettings = create<SettingsState>()(
    persist(
        (set) => ({
            projectCount: 3,
            resumeLanguage: 'English',
            verbosity: 'Standard',
            primaryColor: 'blue',
            updateSettings: (newSettings) => set((state) => ({ ...state, ...newSettings })),
            resetSettings: () => set({
                projectCount: 3,
                resumeLanguage: 'English',
                verbosity: 'Standard',
                primaryColor: 'blue'
            }),
        }),
        {
            name: 'cvagent-settings',
        }
    )
);
