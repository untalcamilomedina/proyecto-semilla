import { OnboardingData } from "@/stores/onboarding";
import { apiPost } from "@/lib/api";

/**
 * Submits the onboarding data to the backend.
 * 
 * @param data OnboardingData collected from the wizard
 */
export async function submitOnboarding(data: OnboardingData): Promise<void> {
  console.log("Submitting Onboarding Data:", data);

  // 1. Create Organization (and Tenant)
  // This endpoint now supports authenticated users without password
  await apiPost('/api/v1/onboarding/start/', {
    org_name: data.organization.name,
    subdomain: data.organization.slug,
    // We can also send plan_id if we add support to backend, 
    // but for now let's just establish the workspace.
  });

  // TODO: Send Plan/Payment info to a separate endpoint or update 'start' to accept it.
  // For v0.12.0 scope, establishing the Tenant is the MVP success criteria.
}
