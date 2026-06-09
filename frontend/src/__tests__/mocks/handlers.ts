import { http, HttpResponse } from "msw";


export const handlers = [
    // Auth
    http.get(`/api/v1/auth/me/`, () => {
        return HttpResponse.json({
            id: 1,
            username: "testuser",
            email: "test@example.com",
            first_name: "Test",
            last_name: "User",
        });
    }),

    // Tenant
    http.get(`/api/v1/tenant/`, () => {
        return HttpResponse.json({
            id: 1,
            name: "Test Org",
            slug: "test-org",
            plan_code: "pro",
            enabled_modules: ["cms", "members"],
        });
    }),

    // Dashboard
    http.get(`/api/v1/dashboard/`, () => {
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
    http.get(`/api/v1/memberships/`, () => {
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

    // Roles (recurso paginado de ejemplo para los tests de hooks)
    http.get(`/api/v1/roles/`, () => {
        return HttpResponse.json({
            count: 1,
            next: null,
            previous: null,
            results: [
                {
                    id: "r1",
                    name: "Test Role",
                    slug: "test-role",
                    description: "A test role",
                    position: 1,
                    permissions: [],
                },
            ],
        });
    }),

    http.delete(`/api/v1/roles/:id/`, () => {
        return new HttpResponse(null, { status: 204 });
    }),

    // API Keys
    http.get(`/api/v1/api-keys/`, () => {
        return HttpResponse.json([
            {
                id: "k1",
                name: "CI Key",
                prefix: "ak_test",
                scopes: [],
                created_at: "2026-02-01T00:00:00Z",
            },
        ]);
    }),

    http.post(`/api/v1/api-keys/`, () => {
        return HttpResponse.json({
            id: "k2",
            name: "New Key",
            prefix: "ak_new",
            scopes: [],
            created_at: "2026-02-05T00:00:00Z",
        });
    }),

    http.delete(`/api/v1/api-keys/:id/`, () => {
        return new HttpResponse(null, { status: 204 });
    }),

    // Activity Logs
    http.get(`/api/v1/activity-logs/`, () => {
        return HttpResponse.json({
            count: 1,
            next: null,
            previous: null,
            results: [
                {
                    id: 1,
                    actor: { email: "admin@test.com" },
                    action: "CREATE",
                    target: "Role: Test",
                    created_at: "2026-02-01T10:00:00Z",
                },
            ],
        });
    }),

    // CSRF
    http.get(`/api/v1/csrf/`, () => {
        return HttpResponse.json({ csrfToken: "test-csrf-token" });
    }),
];
