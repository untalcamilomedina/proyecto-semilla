import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface OnboardingData {
  user: {
    firstName: string;
    lastName: string;
    role: string;
  };
  organization: {
    name: string;
    slug: string;
  };
  planId: string | null;
  billingPeriod: 'monthly' | 'yearly';
}

interface OnboardingState extends OnboardingData {
  step: number;
  isLoading: boolean;
  
  // Actions
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  updateUser: (data: Partial<OnboardingData['user']>) => void;
  updateOrganization: (data: Partial<OnboardingData['organization']>) => void;
  setPlan: (planId: string, period: 'monthly' | 'yearly') => void;
  reset: () => void;
}

const INITIAL_STATE: OnboardingData = {
  user: {
    firstName: '',
    lastName: '',
    role: 'owner',
  },
  organization: {
    name: '',
    slug: '',
  },
  planId: null,
  billingPeriod: 'monthly',
};

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set) => ({
      ...INITIAL_STATE,
      step: 1,
      isLoading: false,

      setStep: (step) => set({ step }),
      
      nextStep: () => set((state) => ({ step: state.step + 1 })),
      
      prevStep: () => set((state) => ({ step: Math.max(1, state.step - 1) })),

      updateUser: (userData) => 
        set((state) => ({ 
          user: { ...state.user, ...userData } 
        })),

      updateOrganization: (orgData) => 
        set((state) => ({ 
          organization: { ...state.organization, ...orgData } 
        })),

      setPlan: (planId, billingPeriod) => 
        set({ planId, billingPeriod }),

      reset: () => set({ ...INITIAL_STATE, step: 1 }),
    }),
    {
      name: 'onboarding-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ 
        user: state.user,
        organization: state.organization,
        planId: state.planId,
        billingPeriod: state.billingPeriod,
        step: state.step
      }),
    }
  )
);
