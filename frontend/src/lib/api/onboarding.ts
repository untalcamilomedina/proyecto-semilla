import { OnboardingData } from "@/stores/onboarding";

/**
 * Submits the onboarding data to the backend.
 * Currently uses a simulated delay as the backend endpoint requires adjustments.
 * 
 * @param data OnboardingData collected from the wizard
 */
export async function submitOnboarding(data: OnboardingData): Promise<void> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 2000));

  console.log("Submitting Onboarding Data:", data);

  // TODO: Connect to real endpoint once Backend Auth flow is aligned.
  // The Backend 'start' endpoint currently expects { admin_email, password } 
  // which implies it handles Signup + Tenant Creation together.
  // Since we are in a post-signup flow, we might need a new endpoint or 
  // default to current user context.

  // Example of what the real call might look like:
  /*
  const response = await fetch('/api/v1/onboarding/start/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      org_name: data.organization.name,
      subdomain: data.organization.slug,
      // ... missing auth fields
    }),
  });
  if (!response.ok) throw new Error('Failed to create workspace');
  */
  
  return Promise.resolve();
}
