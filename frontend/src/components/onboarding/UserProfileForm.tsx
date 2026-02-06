"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { useOnboardingStore } from "@/stores/onboarding";
import { useRouter } from "@/lib/navigation";
import { Label } from "@/components/ui/label";

const schema = z.object({
  firstName: z.string().min(2, "First name is required"),
  lastName: z.string().min(2, "Last name is required"),
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  confirmPassword: z.string().min(8, "Confirm Password is required"),
  role: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
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
    defaultValues: {
      ...user,
      confirmPassword: user.password || "",
    },
  });

  const onSubmit = (data: FormData) => {
    updateUser({
      firstName: data.firstName,
      lastName: data.lastName,
      email: data.email,
      password: data.password,
      role: data.role
    });
    nextStep();
    router.push("/onboarding/organization");
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 animate-in slide-in-from-right-8 duration-500">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="firstName" className="text-foreground">First Name</Label>
          <GlassInput id="firstName" {...register("firstName")} className={errors.firstName ? "border-error-border" : ""} />
          {errors.firstName && <p className="text-xs text-error-text">{errors.firstName.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="lastName" className="text-foreground">Last Name</Label>
          <GlassInput id="lastName" {...register("lastName")} className={errors.lastName ? "border-error-border" : ""} />
          {errors.lastName && <p className="text-xs text-error-text">{errors.lastName.message}</p>}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="email" className="text-foreground">Email Address</Label>
        <GlassInput id="email" type="email" {...register("email")} className={errors.email ? "border-error-border" : ""} />
        {errors.email && <p className="text-xs text-error-text">{errors.email.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="password" className="text-foreground">Password</Label>
          <GlassInput id="password" type="password" {...register("password")} className={errors.password ? "border-error-border" : ""} />
          {errors.password && <p className="text-xs text-error-text">{errors.password.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className="text-foreground">Confirm Password</Label>
          <GlassInput id="confirmPassword" type="password" {...register("confirmPassword")} className={errors.confirmPassword ? "border-error-border" : ""} />
          {errors.confirmPassword && <p className="text-xs text-error-text">{errors.confirmPassword.message}</p>}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="role" className="text-foreground">Role</Label>
        <GlassInput id="role" {...register("role")} disabled className="opacity-50" />
        <p className="text-xs text-text-tertiary">You are creating this workspace, so you are the Owner.</p>
      </div>

      <GlassButton type="submit" className="w-full">
        Continue
      </GlassButton>
    </form>
  );
}
