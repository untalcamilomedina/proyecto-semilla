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
      confirmPassword: user.password || "", // Pre-fill if editing (unsafe but acceptable for wizard flow)
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
        <Label htmlFor="email" className="text-white">Email Address</Label>
        <GlassInput id="email" type="email" {...register("email")} className={errors.email ? "border-red-500" : ""} />
        {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="password" className="text-white">Password</Label>
          <GlassInput id="password" type="password" {...register("password")} className={errors.password ? "border-red-500" : ""} />
          {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className="text-white">Confirm Password</Label>
          <GlassInput id="confirmPassword" type="password" {...register("confirmPassword")} className={errors.confirmPassword ? "border-red-500" : ""} />
          {errors.confirmPassword && <p className="text-xs text-red-500">{errors.confirmPassword.message}</p>}
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
