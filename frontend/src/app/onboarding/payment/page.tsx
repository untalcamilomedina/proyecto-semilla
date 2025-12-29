import { StepGuard } from "@/components/onboarding/StepGuard";
import PaymentSetup from "@/components/onboarding/PaymentSetup";
import { WizardLayout } from "@/components/onboarding/WizardLayout";

export default function PaymentPage() {
  return (
    <StepGuard step={4}>
      <WizardLayout 
        title="Payment Method" 
        description="Securely add your payment details."
      >
        <PaymentSetup />
      </WizardLayout>
    </StepGuard>
  );
}
