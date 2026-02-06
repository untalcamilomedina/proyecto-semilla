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
    is_superuser?: boolean;
    is_staff?: boolean;
    avatar_url?: string;
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

// Enterprise
export interface ActivityLog {
    id: number;
    actor: User;
    action: string;
    target: string;
    description: string;
    ip_address: string;
    user_agent: string;
    created_at: string;
    context: Record<string, unknown>;
}

export interface ApiKey {
    id: number;
    name: string;
    key?: string; // Only on creation
    prefix: string;
    created_at: string;
    last_used_at: string | null;
    revoked_at: string | null;
    scopes: string[];
}

export interface ApiKeyCreate {
    name: string;
    scopes?: string[];
}

// Diagrams
export interface Diagram {
    id: string; // UUID
    title: string;
    description?: string;
    spec?: Record<string, any>; // Canonical JSON
    project: number;
    entities_count?: number; // Annotated field
    updated_at: string;
    created_at: string;
}
