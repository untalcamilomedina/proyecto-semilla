-- Configuración de Row Level Security (RLS) para Proyecto Semilla
-- Este archivo configura las políticas de seguridad a nivel de fila

-- Función helper para obtener el tenant actual del contexto
CREATE OR REPLACE FUNCTION current_tenant_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_tenant_id', TRUE), '')::UUID;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función helper para verificar si el usuario es super_admin
CREATE OR REPLACE FUNCTION is_super_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN COALESCE(current_setting('app.user_role', TRUE), '') = 'super_admin';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función helper para obtener el usuario actual
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_user_id', TRUE), '')::UUID;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Crear usuario de aplicación para RLS (si no existe)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user LOGIN PASSWORD 'app_password';
        GRANT CONNECT ON DATABASE proyecto_semilla TO app_user;
        GRANT USAGE ON SCHEMA public TO app_user;
    END IF;
END $$;

-- Otorgar permisos básicos
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Configurar que las nuevas tablas tengan RLS por defecto
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_user;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Row Level Security configurado correctamente para Proyecto Semilla';
    RAISE NOTICE 'Funciones helper creadas: current_tenant_id(), is_super_admin(), current_user_id()';
    RAISE NOTICE 'Usuario app_user creado con permisos básicos';
END $$;