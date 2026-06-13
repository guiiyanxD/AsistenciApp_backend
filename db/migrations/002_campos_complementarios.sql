-- =========================================================
-- Campos complementarios por rol + tabla administrador
-- =========================================================

-- Docente: título académico, departamento y teléfono
ALTER TABLE docente
    ADD COLUMN titulo       VARCHAR(60)  NOT NULL DEFAULT '',
    ADD COLUMN departamento VARCHAR(120) NOT NULL DEFAULT '',
    ADD COLUMN telefono     VARCHAR(20);

-- Estudiante: código institucional, carrera y semestre
ALTER TABLE estudiante
    ADD COLUMN codigo_estudiante VARCHAR(30) UNIQUE,
    ADD COLUMN carrera           VARCHAR(120) NOT NULL DEFAULT '',
    ADD COLUMN semestre          SMALLINT     NOT NULL DEFAULT 1
        CONSTRAINT chk_semestre CHECK (semestre BETWEEN 1 AND 12);

-- =========================================================
-- ADMINISTRADOR
-- =========================================================
CREATE TABLE administrador (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre        VARCHAR(120) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    cargo         VARCHAR(120) NOT NULL,
    area          VARCHAR(120) NOT NULL,
    creado_en     TIMESTAMP NOT NULL DEFAULT NOW(),
    activo        BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_admin_email ON administrador(email);
