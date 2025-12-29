import { StepGuard } from "@/components/onboarding/StepGuard";
import PlanSelection from "@/components/onboarding/PlanSelection";
import { WizardLayout } from "@/components/onboarding/WizardLayout";

export default function PlanPage() {
  return (
    <StepGuard step={3}>
      <WizardLayout 
        title="Choose your plan" 
        description="Select the plan that fits your needs."
      >
        <PlanSelection />
      </WizardLayout>
    </StepGuard>
  );
}
