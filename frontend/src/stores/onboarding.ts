import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface OnboardingData {
  user: {
    firstName: string;
    lastName: string;
    email: string;
    password?: string;
    role: string;
  };
  organization: {
    name: string;
    slug: string;
  };
  language: 'es' | 'en';
  stripe: {
    enabled: boolean;
    publicKey: string;
    secretKey: string;
    webhookSecret: string;
  };
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
  setLanguage: (lang: 'es' | 'en') => void;
  setStripe: (data: Partial<OnboardingData['stripe']>) => void;
  reset: () => void;
}

const INITIAL_STATE: OnboardingData = {
  user: {
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    role: 'owner',
  },
  organization: {
    name: '',
    slug: '',
  },
  language: 'es',
  stripe: {
    enabled: false,
    publicKey: '',
    secretKey: '',
    webhookSecret: '',
  },
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

      setLanguage: (language) => set({ language }),

      setStripe: (stripeData) => 
        set((state) => ({ 
          stripe: { ...state.stripe, ...stripeData } 
        })),

      reset: () => set({ ...INITIAL_STATE, step: 1 }),
    }),
    {
      name: 'onboarding-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // SECURITY: Never persist secrets to localStorage
        user: state.user
          ? { firstName: state.user.firstName, lastName: state.user.lastName, email: state.user.email, role: state.user.role }
          : state.user,
        organization: state.organization,
        language: state.language,
        stripe: state.stripe
          ? { enabled: state.stripe.enabled, publicKey: state.stripe.publicKey }
          : state.stripe,
        step: state.step,
      }),
    }
  )
);
