---
name: create-form-component
description: Guía para crear formularios validados con react-hook-form, Zod, i18n y componentes Glass.
author: AppNotion Dev Team
version: 1.0.0
---

# Skill: Crear Componente de Formulario

Esta skill estandariza la creación de formularios en el frontend usando `react-hook-form` con validación `Zod`, integración completa con i18n, y componentes del design system Glass.

## Prerrequisitos

- [ ] Dependencias instaladas:
  ```bash
  npm install react-hook-form @hookform/resolvers zod
  ```
- [ ] Namespace i18n definido (ver skill `add-i18n-keys`).
- [ ] Componentes Glass disponibles (`GlassInput`, `GlassButton`).

## Cuándo Usar

- Al crear formularios de entrada de datos (login, signup, settings).
- Formularios de edición (profile, organization).
- Wizards multi-paso (onboarding).
- Modales con inputs (invite member, create role).

## Arquitectura de Formularios

```
Formulario AppNotion
├── Schema Zod (validación)
├── react-hook-form (estado)
├── GlassInput/GlassButton (UI)
├── i18n (labels, placeholders, errores)
└── Accesibilidad (aria-*, focus)
```

---

## Proceso

### Paso 1: Definir Schema de Validación

Crear el schema Zod con mensajes de error como keys i18n.

```typescript
import * as z from "zod";

// Schema con keys de i18n para mensajes
export const createUserSchema = (t: (key: string, values?: Record<string, any>) => string) =>
    z.object({
        email: z
            .string()
            .min(1, t("validation.required"))
            .email(t("validation.invalidEmail")),
        password: z
            .string()
            .min(8, t("validation.minChars", { count: 8 }))
            .max(100, t("validation.maxChars", { count: 100 })),
        confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
        message: t("validation.passwordsMatch"),
        path: ["confirmPassword"],
    });

export type UserFormData = z.infer<ReturnType<typeof createUserSchema>>;
```

### Paso 2: Crear el Componente de Formulario

---

## Templates

### Template A: Formulario Simple

Ideal para: Login, creación de entidades simples.

```tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useTranslations } from "next-intl";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { Label } from "@/components/ui/label";

// Schema factory con i18n
const createSchema = (t: (key: string, values?: Record<string, any>) => string) =>
    z.object({
        name: z
            .string()
            .min(2, t("validation.minChars", { count: 2 }))
            .max(50, t("validation.maxChars", { count: 50 })),
        email: z
            .string()
            .min(1, t("validation.required"))
            .email(t("validation.invalidEmail")),
    });

type FormData = z.infer<ReturnType<typeof createSchema>>;

interface Props {
    onSubmit: (data: FormData) => Promise<void>;
    defaultValues?: Partial<FormData>;
}

export function SimpleForm({ onSubmit, defaultValues }: Props) {
    const t = useTranslations("myFeature");
    const tValidation = useTranslations("validation");

    const schema = createSchema(tValidation);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<FormData>({
        resolver: zodResolver(schema),
        defaultValues,
    });

    return (
        <form
            onSubmit={handleSubmit(onSubmit)}
            className="space-y-6"
            noValidate // Desactivar validación HTML nativa
        >
            {/* Campo: Name */}
            <div className="space-y-2">
                <Label htmlFor="name" className="text-white">
                    {t("form.name")}
                </Label>
                <GlassInput
                    id="name"
                    placeholder={t("form.namePlaceholder")}
                    error={!!errors.name}
                    aria-invalid={errors.name ? "true" : undefined}
                    aria-describedby={errors.name ? "name-error" : undefined}
                    {...register("name")}
                />
                {errors.name && (
                    <p id="name-error" className="text-xs text-red-400" role="alert">
                        {errors.name.message}
                    </p>
                )}
            </div>

            {/* Campo: Email */}
            <div className="space-y-2">
                <Label htmlFor="email" className="text-white">
                    {t("form.email")}
                </Label>
                <GlassInput
                    id="email"
                    type="email"
                    placeholder={t("form.emailPlaceholder")}
                    error={!!errors.email}
                    aria-invalid={errors.email ? "true" : undefined}
                    aria-describedby={errors.email ? "email-error" : undefined}
                    {...register("email")}
                />
                {errors.email && (
                    <p id="email-error" className="text-xs text-red-400" role="alert">
                        {errors.email.message}
                    </p>
                )}
            </div>

            {/* Submit */}
            <GlassButton
                type="submit"
                className="w-full"
                loading={isSubmitting}
                disabled={isSubmitting}
            >
                {isSubmitting ? t("form.submitting") : t("form.submit")}
            </GlassButton>
        </form>
    );
}
```

### Template B: Formulario con Password

Ideal para: Login, Signup, Change Password.

```tsx
"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useTranslations } from "next-intl";
import { Eye, EyeOff } from "lucide-react";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { Label } from "@/components/ui/label";

const createSchema = (t: (key: string, values?: Record<string, any>) => string) =>
    z
        .object({
            email: z.string().email(t("invalidEmail")),
            password: z.string().min(8, t("minChars", { count: 8 })),
            confirmPassword: z.string(),
        })
        .refine((data) => data.password === data.confirmPassword, {
            message: t("passwordsMatch"),
            path: ["confirmPassword"],
        });

type FormData = z.infer<ReturnType<typeof createSchema>>;

export function SignupForm() {
    const t = useTranslations("auth");
    const tValidation = useTranslations("validation");
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<FormData>({
        resolver: zodResolver(createSchema(tValidation)),
    });

    const onSubmit = async (data: FormData) => {
        // API call
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>
            {/* Email */}
            <div className="space-y-2">
                <Label htmlFor="email">{t("email")}</Label>
                <GlassInput
                    id="email"
                    type="email"
                    placeholder={t("emailPlaceholder")}
                    error={!!errors.email}
                    {...register("email")}
                />
                {errors.email && (
                    <p className="text-xs text-red-400">{errors.email.message}</p>
                )}
            </div>

            {/* Password con toggle */}
            <div className="space-y-2">
                <Label htmlFor="password">{t("password")}</Label>
                <div className="relative">
                    <GlassInput
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder={t("signupPasswordPlaceholder")}
                        error={!!errors.password}
                        className="pr-10"
                        {...register("password")}
                    />
                    <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/60"
                        aria-label={showPassword ? t("hidePassword") : t("showPassword")}
                    >
                        {showPassword ? (
                            <EyeOff className="h-4 w-4" />
                        ) : (
                            <Eye className="h-4 w-4" />
                        )}
                    </button>
                </div>
                {errors.password && (
                    <p className="text-xs text-red-400">{errors.password.message}</p>
                )}
            </div>

            {/* Confirm Password */}
            <div className="space-y-2">
                <Label htmlFor="confirmPassword">{t("confirmPassword")}</Label>
                <div className="relative">
                    <GlassInput
                        id="confirmPassword"
                        type={showConfirm ? "text" : "password"}
                        placeholder={t("confirmPasswordPlaceholder")}
                        error={!!errors.confirmPassword}
                        className="pr-10"
                        {...register("confirmPassword")}
                    />
                    <button
                        type="button"
                        onClick={() => setShowConfirm(!showConfirm)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/60"
                        aria-label={showConfirm ? t("hidePassword") : t("showPassword")}
                    >
                        {showConfirm ? (
                            <EyeOff className="h-4 w-4" />
                        ) : (
                            <Eye className="h-4 w-4" />
                        )}
                    </button>
                </div>
                {errors.confirmPassword && (
                    <p className="text-xs text-red-400">{errors.confirmPassword.message}</p>
                )}
            </div>

            <GlassButton type="submit" className="w-full" loading={isSubmitting}>
                {t("createAccount")}
            </GlassButton>
        </form>
    );
}
```

### Template C: Formulario en Modal

Ideal para: Invite member, Create role, Quick edit.

```tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useTranslations } from "next-intl";
import { GlassModal } from "@/components/ui/glass/GlassModal";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { Label } from "@/components/ui/label";

const createSchema = (t: (key: string) => string) =>
    z.object({
        emails: z.string().min(1, t("required")),
    });

type FormData = z.infer<ReturnType<typeof createSchema>>;

interface Props {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onInvite: (emails: string[]) => Promise<void>;
}

export function InviteMemberModal({ open, onOpenChange, onInvite }: Props) {
    const t = useTranslations("members");
    const tValidation = useTranslations("validation");
    const tCommon = useTranslations("common");

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isSubmitting },
    } = useForm<FormData>({
        resolver: zodResolver(createSchema(tValidation)),
    });

    const onSubmit = async (data: FormData) => {
        const emails = data.emails
            .split(/[\n,]/)
            .map((e) => e.trim())
            .filter(Boolean);

        await onInvite(emails);
        reset();
        onOpenChange(false);
    };

    const handleClose = () => {
        reset();
        onOpenChange(false);
    };

    return (
        <GlassModal
            open={open}
            onOpenChange={handleClose}
            title={t("inviteTitle")}
            description={t("inviteDescription")}
        >
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <div className="space-y-2">
                    <Label htmlFor="emails">{t("emails")}</Label>
                    <textarea
                        id="emails"
                        placeholder={t("emailsPlaceholder")}
                        className="w-full h-32 rounded-xl px-4 py-3 bg-white/5 backdrop-blur-sm border border-white/10 text-white placeholder:text-white/30 resize-none focus:outline-none focus:ring-2 focus:ring-white/20"
                        {...register("emails")}
                    />
                    {errors.emails && (
                        <p className="text-xs text-red-400">{errors.emails.message}</p>
                    )}
                </div>

                <div className="flex gap-3 justify-end">
                    <GlassButton
                        type="button"
                        variant="ghost"
                        onClick={handleClose}
                    >
                        {tCommon("cancel")}
                    </GlassButton>
                    <GlassButton type="submit" loading={isSubmitting}>
                        {t("sendInvitations")}
                    </GlassButton>
                </div>
            </form>
        </GlassModal>
    );
}
```

### Template D: Formulario Wizard (Multi-paso)

Ideal para: Onboarding, Setup wizards.

```tsx
"use client";

import { useForm, FormProvider } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useTranslations } from "next-intl";
import { useState } from "react";

// Schema para todos los pasos
const createFullSchema = (t: (key: string) => string) =>
    z.object({
        // Step 1
        organizationName: z.string().min(2, t("required")),
        // Step 2
        plan: z.enum(["free", "pro", "enterprise"]),
        // Step 3
        inviteEmails: z.string().optional(),
    });

type WizardData = z.infer<ReturnType<typeof createFullSchema>>;

const STEPS = ["organization", "plan", "invite"] as const;

export function OnboardingWizard() {
    const t = useTranslations("onboarding");
    const tValidation = useTranslations("validation");
    const [currentStep, setCurrentStep] = useState(0);

    const methods = useForm<WizardData>({
        resolver: zodResolver(createFullSchema(tValidation)),
        mode: "onChange",
    });

    const nextStep = async () => {
        // Validar solo campos del paso actual
        const fieldsToValidate = getFieldsForStep(currentStep);
        const isValid = await methods.trigger(fieldsToValidate);

        if (isValid && currentStep < STEPS.length - 1) {
            setCurrentStep((s) => s + 1);
        }
    };

    const prevStep = () => {
        if (currentStep > 0) {
            setCurrentStep((s) => s - 1);
        }
    };

    const onSubmit = async (data: WizardData) => {
        // Submit final
        console.log("Final data:", data);
    };

    return (
        <FormProvider {...methods}>
            <form onSubmit={methods.handleSubmit(onSubmit)}>
                {/* Progress indicator */}
                <div className="flex gap-2 mb-8">
                    {STEPS.map((step, index) => (
                        <div
                            key={step}
                            className={`h-1 flex-1 rounded-full ${
                                index <= currentStep ? "bg-white/50" : "bg-white/10"
                            }`}
                        />
                    ))}
                </div>

                {/* Step content */}
                {currentStep === 0 && <Step1Organization />}
                {currentStep === 1 && <Step2Plan />}
                {currentStep === 2 && <Step3Invite />}

                {/* Navigation */}
                <div className="flex gap-3 mt-8">
                    {currentStep > 0 && (
                        <GlassButton type="button" variant="ghost" onClick={prevStep}>
                            {t("back")}
                        </GlassButton>
                    )}
                    {currentStep < STEPS.length - 1 ? (
                        <GlassButton type="button" onClick={nextStep} className="ml-auto">
                            {t("next")}
                        </GlassButton>
                    ) : (
                        <GlassButton type="submit" className="ml-auto">
                            {t("finish")}
                        </GlassButton>
                    )}
                </div>
            </form>
        </FormProvider>
    );
}

function getFieldsForStep(step: number): (keyof WizardData)[] {
    switch (step) {
        case 0:
            return ["organizationName"];
        case 1:
            return ["plan"];
        case 2:
            return ["inviteEmails"];
        default:
            return [];
    }
}
```

---

## Keys i18n Requeridas

Agregar al namespace de validación (`validation`):

```json
{
  "validation": {
    "required": "This field is required",
    "minChars": "Minimum {count} characters",
    "maxChars": "Maximum {count} characters",
    "invalidEmail": "Invalid email address",
    "passwordsMatch": "Passwords don't match",
    "invalidUrl": "Invalid URL",
    "invalidPhone": "Invalid phone number"
  }
}
```

```json
{
  "validation": {
    "required": "Este campo es obligatorio",
    "minChars": "Mínimo {count} caracteres",
    "maxChars": "Máximo {count} caracteres",
    "invalidEmail": "Correo electrónico inválido",
    "passwordsMatch": "Las contraseñas no coinciden",
    "invalidUrl": "URL inválida",
    "invalidPhone": "Número de teléfono inválido"
  }
}
```

---

## Accesibilidad en Formularios

### Requisitos WCAG

| Elemento | Implementación |
|----------|----------------|
| Labels | Siempre usar `<Label htmlFor="id">` |
| Errores | `aria-invalid`, `aria-describedby`, `role="alert"` |
| Required | `aria-required="true"` si es obligatorio |
| Loading | `aria-busy="true"` en botón submit |

### Patrón de Error Accesible

```tsx
<div className="space-y-2">
    <Label htmlFor="email">
        {t("email")}
        <span className="text-red-400 ml-1" aria-hidden="true">*</span>
    </Label>
    <GlassInput
        id="email"
        type="email"
        aria-required="true"
        aria-invalid={errors.email ? "true" : undefined}
        aria-describedby={errors.email ? "email-error" : "email-hint"}
        {...register("email")}
    />
    <p id="email-hint" className="text-xs text-white/40">
        {t("emailHint")}
    </p>
    {errors.email && (
        <p id="email-error" className="text-xs text-red-400" role="alert">
            {errors.email.message}
        </p>
    )}
</div>
```

---

## Checklist de Verificación

### Estructura
- [ ] Schema Zod definido con factory function para i18n
- [ ] `useForm` con `zodResolver`
- [ ] `noValidate` en el form tag
- [ ] Manejo de `isSubmitting` state

### i18n
- [ ] Labels traducidos
- [ ] Placeholders traducidos
- [ ] Mensajes de error traducidos
- [ ] Hints/descriptions traducidos

### Accesibilidad
- [ ] Todos los inputs tienen `id` y `<Label htmlFor>`
- [ ] Errores tienen `role="alert"` y `aria-describedby`
- [ ] Campos inválidos tienen `aria-invalid="true"`
- [ ] Botón submit tiene estado loading accesible

### UX
- [ ] Validación en blur o change (no solo submit)
- [ ] Loading state visual en submit
- [ ] Reset del form después de éxito (si aplica)
- [ ] Focus al primer error

---

## Errores Comunes

### Error: Mensajes de validación no traducidos

**Causa:** Usar strings directos en Zod schema.

**Solución:** Usar factory function que recibe `t`:
```tsx
const createSchema = (t: Function) => z.object({
    name: z.string().min(2, t("minChars", { count: 2 }))
});
```

### Error: Form no resetea después de submit

**Causa:** No llamar `reset()` después de submit exitoso.

**Solución:**
```tsx
const onSubmit = async (data) => {
    await api.submit(data);
    reset(); // Limpiar form
};
```

### Error: Validación corre en cada keystroke

**Causa:** `mode: "onChange"` sin necesidad.

**Solución:** Usar `mode: "onBlur"` o `mode: "onSubmit"` según UX deseada.

---

## Referencias

- [React Hook Form Docs](https://react-hook-form.com/)
- [Zod Documentation](https://zod.dev/)
- [Skill add-i18n-keys](../add-i18n-keys/SKILL.md)
- [Skill create-design-component](../create-design-component/SKILL.md)

---

*Última actualización: 2025-02-04*
