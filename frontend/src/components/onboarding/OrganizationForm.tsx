"use client";

import React, { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { useOnboardingStore } from "@/stores/onboarding";
import { useRouter } from "@/lib/navigation";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

const schema = z.object({
  name: z.string().min(2, "Organization name is required"),
  slug: z.string().min(3, "Slug must be at least 3 characters").regex(/^[a-z0-9-]+$/, "Slug can only contain lowercase letters, numbers, and hyphens"),
});

type FormData = z.infer<typeof schema>;

export default function OrganizationForm() {
  const { organization, updateOrganization, nextStep } = useOnboardingStore();
  const router = useRouter();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: organization,
  });

  const nameValue = watch("name");

  useEffect(() => {
    if (nameValue && !organization.slug) {
      const slug = nameValue
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/(^-|-$)/g, "");
      setValue("slug", slug);
    }
  }, [nameValue, organization.slug, setValue]);

  const onSubmit = (data: FormData) => {
    updateOrganization(data);
    nextStep();
    router.push("/onboarding/plan");
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 animate-in slide-in-from-right-8 duration-500">
      <div className="space-y-2">
        <Label htmlFor="name" className="text-foreground">Organization Name</Label>
        <GlassInput
          id="name"
          placeholder="Acme Corp"
          {...register("name")}
          className={errors.name ? "border-error-border" : ""}
        />
        {errors.name && <p className="text-xs text-error-text">{errors.name.message}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="slug" className="text-foreground">Workspace URL</Label>
        <div className="flex items-center">
          <span className="text-text-secondary text-sm mr-2">acme.dev/</span>
          <GlassInput
            id="slug"
            placeholder="acme-corp"
            {...register("slug")}
            className={cn(errors.slug ? "border-error-border" : "")}
          />
        </div>
        {errors.slug && <p className="text-xs text-error-text">{errors.slug.message}</p>}
        <p className="text-xs text-text-tertiary">This will be your unique address.</p>
      </div>

      <GlassButton type="submit" className="w-full">
        Continue
      </GlassButton>
    </form>
  );
}
