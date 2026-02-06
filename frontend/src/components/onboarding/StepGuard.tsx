"use client";

import { useOnboardingStore } from "@/stores/onboarding";
import { useRouter } from "@/lib/navigation";
import { useEffect } from "react";

interface StepGuardProps {
  children: React.ReactNode;
  step: number;
}

export function StepGuard({ children, step }: StepGuardProps) {
  const { step: currentStep, isLoading } = useOnboardingStore();
  const router = useRouter();

  useEffect(() => {
    // If backend is loading, wait
    if (isLoading) return;

    // If trying to access a future step
    if (step > currentStep) {
      // Redirect to the max allowed step
      const routes = [
        "/onboarding/profile",
        "/onboarding/organization",
        "/onboarding/plan",
        "/onboarding/payment",
        "/onboarding/review",
      ];
      // Safety check for index
      const targetIndex = Math.min(currentStep - 1, routes.length - 1);
      router.push(routes[targetIndex]);
    }
  }, [step, currentStep, isLoading, router]);

  if (isLoading || step > currentStep) {
    return null; // Don't render protected content while redirecting
  }

  return <>{children}</>;
}
