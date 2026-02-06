import { StepGuard } from "@/components/onboarding/StepGuard";
import UserProfileForm from "@/components/onboarding/UserProfileForm";
import { WizardLayout } from "@/components/onboarding/WizardLayout";

export default function ProfilePage() {
  return (
    <StepGuard step={1}>
      <WizardLayout 
        title="Let's start with you" 
        description="We need some basic information to set up your account profile."
      >
        <UserProfileForm />
      </WizardLayout>
    </StepGuard>
  );
}
