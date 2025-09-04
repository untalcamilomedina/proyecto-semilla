-- Extensiones necesarias para Proyecto Semilla
-- Este archivo se ejecuta automáticamente al crear el contenedor PostgreSQL

-- Extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extensión para encriptación (para contraseñas)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Extensión para Row Level Security
-- RLS ya está disponible por defecto en PostgreSQL 15, pero lo habilitamos explícitamente
-- No necesitamos CREATE EXTENSION para RLS, está built-in

-- Verificar que las extensiones se instalaron correctamente
DO $$
BEGIN
    RAISE NOTICE 'Extensiones instaladas correctamente:';
    RAISE NOTICE '- uuid-ossp: %', (SELECT installed_version FROM pg_available_extensions WHERE name = 'uuid-ossp');
    RAISE NOTICE '- pgcrypto: %', (SELECT installed_version FROM pg_available_extensions WHERE name = 'pgcrypto');
END $$;