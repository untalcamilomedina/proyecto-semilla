import { StepGuard } from "@/components/onboarding/StepGuard";
import OrganizationForm from "@/components/onboarding/OrganizationForm";
import { WizardLayout } from "@/components/onboarding/WizardLayout";

export default function OrganizationPage() {
  return (
    <StepGuard step={2}>
      <WizardLayout 
        title="Name your workspace" 
        description="This is where your team will collaborate."
      >
        <OrganizationForm />
      </WizardLayout>
    </StepGuard>
  );
}
