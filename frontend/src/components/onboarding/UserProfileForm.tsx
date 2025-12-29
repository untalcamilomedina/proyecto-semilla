"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { useOnboardingStore } from "@/stores/onboarding";
import { useRouter } from "next/navigation";
import { Label } from "@/components/ui/label";

const schema = z.object({
  firstName: z.string().min(2, "First name is required"),
  lastName: z.string().min(2, "Last name is required"),
  role: z.string(),
});

type FormData = z.infer<typeof schema>;

export default function UserProfileForm() {
  const { user, updateUser, nextStep } = useOnboardingStore();
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: user,
  });

  const onSubmit = (data: FormData) => {
    updateUser(data);
    nextStep();
    router.push("/onboarding/organization");
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 animate-in slide-in-from-right-8 duration-500">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="firstName" className="text-white">First Name</Label>
          <GlassInput id="firstName" {...register("firstName")} className={errors.firstName ? "border-red-500" : ""} />
          {errors.firstName && <p className="text-xs text-red-500">{errors.firstName.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="lastName" className="text-white">Last Name</Label>
          <GlassInput id="lastName" {...register("lastName")} className={errors.lastName ? "border-red-500" : ""} />
          {errors.lastName && <p className="text-xs text-red-500">{errors.lastName.message}</p>}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="role" className="text-white">Role</Label>
        <GlassInput id="role" {...register("role")} disabled className="opacity-50" />
        <p className="text-xs text-white/40">You are creating this workspace, so you are the Owner.</p>
      </div>

      <GlassButton type="submit" className="w-full">
        Continue
      </GlassButton>
    </form>
  );
}
