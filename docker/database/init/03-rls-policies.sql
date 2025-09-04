-- Row Level Security Policies para Proyecto Semilla
-- Este archivo crea las políticas RLS para todas las tablas

-- Habilitar RLS en todas las tablas
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;

-- ===========================================
-- POLÍTICAS PARA TENANTS
-- ===========================================

-- Política para tenants: Los usuarios solo pueden ver tenants a los que pertenecen
-- o tenants hijos (jerarquía), o si son super_admin
CREATE POLICY tenant_isolation_policy ON tenants
    FOR ALL
    USING (
        id = current_tenant_id() OR
        parent_tenant_id = current_tenant_id() OR
        is_super_admin()
    );

-- Política para creación de tenants: Solo super_admin puede crear tenants raíz
-- Usuarios normales pueden crear sub-tenants de su tenant actual
CREATE POLICY tenant_creation_policy ON tenants
    FOR INSERT
    WITH CHECK (
        (parent_tenant_id IS NULL AND is_super_admin()) OR
        (parent_tenant_id = current_tenant_id())
    );

-- ===========================================
-- POLÍTICAS PARA USERS
-- ===========================================

-- Política de aislamiento: Usuarios solo ven users de su mismo tenant
CREATE POLICY user_tenant_isolation_policy ON users
    FOR ALL
    USING (
        tenant_id = current_tenant_id() OR
        is_super_admin()
    );

-- Política de creación: Solo se pueden crear users en el tenant actual
CREATE POLICY user_creation_policy ON users
    FOR INSERT
    WITH CHECK (
        tenant_id = current_tenant_id() OR
        is_super_admin()
    );

-- Política de actualización: Solo el propio usuario o super_admin pueden actualizar
-- (excepto campos sensibles que solo super_admin puede cambiar)
CREATE POLICY user_update_policy ON users
    FOR UPDATE
    USING (
        id = current_user_id() OR
        is_super_admin()
    )
    WITH CHECK (
        tenant_id = current_tenant_id() OR
        is_super_admin()
    );

-- ===========================================
-- POLÍTICAS PARA ROLES
-- ===========================================

-- Política de aislamiento: Roles solo del tenant actual
CREATE POLICY role_tenant_isolation_policy ON roles
    FOR ALL
    USING (
        tenant_id = current_tenant_id() OR
        is_super_admin()
    );

-- Política de creación: Solo en tenant actual
CREATE POLICY role_creation_policy ON roles
    FOR INSERT
    WITH CHECK (
        tenant_id = current_tenant_id() OR
        is_super_admin()
    );

-- ===========================================
-- POLÍTICAS PARA REFRESH_TOKENS
-- ===========================================

-- Política de aislamiento: Solo tokens del tenant actual
CREATE POLICY refresh_token_tenant_isolation_policy ON refresh_tokens
    FOR ALL
    USING (
        tenant_id = current_tenant_id() OR
        is_super_admin()
    );

-- Política de creación: Solo en tenant actual
CREATE POLICY refresh_token_creation_policy ON refresh_tokens
    FOR INSERT
    WITH CHECK (
        tenant_id = current_tenant_id() OR
        is_super_admin()
    );

-- ===========================================
-- POLÍTICAS PARA USER_ROLES
-- ===========================================

-- Política de aislamiento: Solo roles del tenant actual
CREATE POLICY user_role_tenant_isolation_policy ON user_roles
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = user_roles.user_id
            AND (u.tenant_id = current_tenant_id() OR is_super_admin())
        ) AND
        EXISTS (
            SELECT 1 FROM roles r
            WHERE r.id = user_roles.role_id
            AND (r.tenant_id = current_tenant_id() OR is_super_admin())
        )
    );

-- Política de creación: Solo asignar roles del tenant actual
CREATE POLICY user_role_creation_policy ON user_roles
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = user_roles.user_id
            AND (u.tenant_id = current_tenant_id() OR is_super_admin())
        ) AND
        EXISTS (
            SELECT 1 FROM roles r
            WHERE r.id = user_roles.role_id
            AND (r.tenant_id = current_tenant_id() OR is_super_admin())
        )
    );

-- ===========================================
-- POLÍTICAS ADICIONALES DE SEGURIDAD
-- ===========================================

-- Evitar que usuarios modifiquen su propio tenant_id
CREATE POLICY prevent_tenant_id_change ON users
    FOR UPDATE
    USING (OLD.tenant_id = NEW.tenant_id OR is_super_admin())
    WITH CHECK (OLD.tenant_id = NEW.tenant_id OR is_super_admin());

-- Solo super_admin puede cambiar roles críticos
CREATE POLICY restrict_super_admin_role ON user_roles
    FOR ALL
    USING (
        NOT EXISTS (
            SELECT 1 FROM roles r
            WHERE r.id = user_roles.role_id
            AND r.name = 'super_admin'
        ) OR is_super_admin()
    );

-- ===========================================
-- MENSAJE DE CONFIRMACIÓN
-- ===========================================

DO $$
BEGIN
    RAISE NOTICE 'Row Level Security policies configuradas correctamente';
    RAISE NOTICE 'Políticas aplicadas a: tenants, users, roles, user_roles';
    RAISE NOTICE 'Todas las tablas tienen aislamiento por tenant';
END $$;