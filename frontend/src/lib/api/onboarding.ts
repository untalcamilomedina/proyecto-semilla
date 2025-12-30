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
    admin_email: data.user.email,
    password: data.user.password,
    confirm_password: data.user.password,
    language: data.language,
    stripe_connected: data.stripe.enabled,
    stripe_public_key: data.stripe.publicKey,
    stripe_secret_key: data.stripe.secretKey,
    stripe_webhook_secret: data.stripe.webhookSecret,
  });

  // TODO: Send Plan/Payment info to a separate endpoint or update 'start' to accept it.
  // For v0.12.0 scope, establishing the Tenant is the MVP success criteria.
}
