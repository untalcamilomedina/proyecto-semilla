from __future__ import annotations

# Re-export por compatibilidad: la implementación canónica vive en common.api.permissions
from common.api.permissions import IsTenantMember, PolicyPermission

__all__ = ["IsTenantMember", "PolicyPermission"]
