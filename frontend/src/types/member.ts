export interface Member {
    id: number;
    user: number; // User PK
    user_email: string;
    role_slug: string;
    role_name: string;
    is_active: boolean;
    joined_at: string;
}

export interface MemberInviteRequest {
    emails: string[];
    role_slug: string;
}
