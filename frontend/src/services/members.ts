import { apiGet, apiPost, apiPatch, apiDelete } from "@/lib/api";
import { Member, MemberInviteRequest } from "@/types/member";

const ENDPOINT = "/api/v1/memberships/";

export const memberService = {
    getAll: async () => {
        return apiGet<Member[]>(ENDPOINT);
    },

    invite: async (data: MemberInviteRequest) => {
        return apiPost(`${ENDPOINT}invite/`, data);
    },

    updateRole: async (id: number, role_slug: string) => {
        return apiPatch(`${ENDPOINT}${id}/`, { role_slug });
    },

    delete: async (id: number) => {
        return apiDelete(`${ENDPOINT}${id}/`);
    },
};
