import { StepGuard } from "@/components/onboarding/StepGuard";
import ReviewConfirm from "@/components/onboarding/ReviewConfirm";
import { WizardLayout } from "@/components/onboarding/WizardLayout";

export default function ReviewPage() {
  return (
    <StepGuard step={5}>
      <WizardLayout 
        title="Review & Confirm" 
        description="We're almost there! Review your details below."
      >
        <ReviewConfirm />
      </WizardLayout>
    </StepGuard>
  );
}
