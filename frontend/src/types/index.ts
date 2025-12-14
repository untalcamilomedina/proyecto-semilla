/**
 * API Response Types for Django backend
 */

// Auth
export interface User {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    is_active: boolean;
}

export interface AuthResponse {
    user: User;
    is_authenticated: boolean;
}

// Tenant
export interface Tenant {
    id: number;
    name: string;
    slug: string;
    schema_name: string;
    plan_code: string;
    enabled_modules: string[];
    branding: Record<string, unknown>;
    domain_base: string;
}

// Membership
export interface Role {
    id: number;
    name: string;
    slug: string;
    description: string;
    position: number;
    is_system: boolean;
}

export interface Membership {
    id: number;
    user: User;
    organization: number;
    role: Role;
    role_name: string;
    invited_at: string;
    joined_at: string | null;
}

// Permissions
export interface Permission {
    id: number;
    module: string;
    codename: string;
    name: string;
    description: string;
    is_system: boolean;
}

// Billing
export interface Plan {
    id: number;
    code: string;
    name: string;
    description: string;
    seat_limit: number | null;
    price_cents: number;
    currency: string;
    interval: string;
    trial_days: number;
    is_active: boolean;
    is_public: boolean;
}

export interface Subscription {
    id: number;
    plan: Plan;
    status: "active" | "trialing" | "past_due" | "canceled" | "incomplete";
    quantity: number;
    current_period_start: string;
    current_period_end: string;
    cancel_at_period_end: boolean;
}

export interface Invoice {
    id: number;
    stripe_invoice_id: string;
    status: string;
    amount_paid: string;
    currency: string;
    hosted_invoice_url: string | null;
    invoice_pdf: string | null;
    created_at: string;
}

// Paginated Response
export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

// CSRF
export interface CsrfResponse {
    csrfToken: string;
}

// Error
export interface ValidationError {
    [field: string]: string[];
}

export interface ApiErrorResponse {
    detail?: string;
    non_field_errors?: string[];
    [field: string]: unknown;
}
