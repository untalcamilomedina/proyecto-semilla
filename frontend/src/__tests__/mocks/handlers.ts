import { http, HttpResponse } from "msw";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export const handlers = [
    // Auth
    http.get(`${API}/api/v1/auth/me/`, () => {
        return HttpResponse.json({
            id: 1,
            username: "testuser",
            email: "test@blockflow.app",
            first_name: "Test",
            last_name: "User",
        });
    }),

    // Tenant
    http.get(`${API}/api/v1/tenant/`, () => {
        return HttpResponse.json({
            id: 1,
            name: "Test Org",
            slug: "test-org",
            plan_code: "pro",
            enabled_modules: ["diagrams", "members"],
        });
    }),

    // Dashboard
    http.get(`${API}/api/v1/dashboard/`, () => {
        return HttpResponse.json({
            stats: {
                total_members: 5,
                active_members: 3,
                pending_invites: 2,
                mrr: 99,
            },
            recent_activity: [],
            modules_status: {},
        });
    }),

    // Members
    http.get(`${API}/api/v1/memberships/`, () => {
        return HttpResponse.json([
            {
                id: 1,
                user: { email: "admin@test.com", first_name: "Admin", last_name: "User" },
                role: { name: "Admin", slug: "admin" },
                is_active: true,
                created_at: "2026-01-01T00:00:00Z",
            },
            {
                id: 2,
                user: { email: "dev@test.com", first_name: "Dev", last_name: "User" },
                role: { name: "Developer", slug: "developer" },
                is_active: true,
                created_at: "2026-01-15T00:00:00Z",
            },
        ]);
    }),

    // Diagrams
    http.get(`${API}/api/v1/diagrams/`, () => {
        return HttpResponse.json({
            count: 1,
            next: null,
            previous: null,
            results: [
                {
                    id: "d1",
                    name: "Test Diagram",
                    type: "erd",
                    description: "A test diagram",
                    entities_count: 3,
                    updated_at: "2026-02-01T00:00:00Z",
                },
            ],
        });
    }),

    http.delete(`${API}/api/v1/diagrams/:id/`, () => {
        return new HttpResponse(null, { status: 204 });
    }),

    // API Keys
    http.get(`${API}/api/v1/ai/keys/`, () => {
        return HttpResponse.json([
            {
                id: "k1",
                name: "My Gemini Key",
                prefix: "AIza***",
                service: "gemini",
                created_at: "2026-02-01T00:00:00Z",
            },
        ]);
    }),

    http.post(`${API}/api/v1/ai/keys/`, () => {
        return HttpResponse.json({
            id: "k2",
            name: "New Key",
            prefix: "sk-***",
            service: "openai",
            created_at: "2026-02-05T00:00:00Z",
        });
    }),

    http.delete(`${API}/api/v1/ai/keys/:id/`, () => {
        return new HttpResponse(null, { status: 204 });
    }),

    // Activity Logs
    http.get(`${API}/api/v1/activity-logs/`, () => {
        return HttpResponse.json({
            count: 1,
            next: null,
            previous: null,
            results: [
                {
                    id: 1,
                    actor: { email: "admin@test.com" },
                    action: "CREATE",
                    target: "Diagram: Test",
                    created_at: "2026-02-01T10:00:00Z",
                },
            ],
        });
    }),

    // CSRF
    http.get(`${API}/api/v1/csrf/`, () => {
        return HttpResponse.json({ csrfToken: "test-csrf-token" });
    }),
];
