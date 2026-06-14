-- =========================================================
-- TIPOS ENUMERADOS
-- =========================================================

CREATE TYPE tipo_periodo AS ENUM (
    'mensual', 'bimestral', 'trimestral',
    'semestral', 'anual', 'personalizado'
);

CREATE TYPE tipo_clase AS ENUM (
    'clase', 'examen', 'exposicion'
);

CREATE TYPE estado_asistencia AS ENUM (
    'presente', 'pendiente', 'ausente', 'rechazada'
);

CREATE TYPE estado_inscripcion AS ENUM (
    'activa', 'aprobada', 'reprobada', 'retirada'
);

CREATE TYPE resultado_biometrico AS ENUM (
    'exitoso', 'baja_confianza',
    'rostro_no_detectado', 'error_procesamiento'
);

CREATE TYPE decision_revision AS ENUM (
    'aprobada', 'rechazada'
);

CREATE TYPE dia_semana AS ENUM (
    'lunes', 'martes', 'miercoles',
    'jueves', 'viernes', 'sabado', 'domingo'
);

-- =========================================================
-- DOCENTE
-- =========================================================
CREATE TABLE docente (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre        VARCHAR(120) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    profesion     VARCHAR(255) NOT NULL,
    titulo        VARCHAR(60)  NOT NULL DEFAULT '',
    departamento  VARCHAR(120) NOT NULL DEFAULT '',
    telefono      VARCHAR(20),
    creado_en     TIMESTAMP    NOT NULL DEFAULT NOW(),
    activo        BOOLEAN      NOT NULL DEFAULT TRUE
);

-- =========================================================
-- ESTUDIANTE
-- =========================================================
CREATE TABLE estudiante (
    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre            VARCHAR(120) NOT NULL,
    email             VARCHAR(255) NOT NULL UNIQUE,
    password_hash     VARCHAR(255) NOT NULL,
    codigo_estudiante VARCHAR(30)  UNIQUE,
    carrera           VARCHAR(120) NOT NULL DEFAULT '',
    semestre          SMALLINT     NOT NULL DEFAULT 1
        CONSTRAINT chk_semestre CHECK (semestre BETWEEN 1 AND 12),
    creado_en         TIMESTAMP    NOT NULL DEFAULT NOW(),
    activo            BOOLEAN      NOT NULL DEFAULT TRUE
);

-- =========================================================
-- ADMINISTRADOR
-- =========================================================
CREATE TABLE administrador (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre        VARCHAR(120) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    cargo         VARCHAR(120) NOT NULL,
    area          VARCHAR(120) NOT NULL,
    creado_en     TIMESTAMP    NOT NULL DEFAULT NOW(),
    activo        BOOLEAN      NOT NULL DEFAULT TRUE
);

-- =========================================================
-- PERFIL BIOMETRICO
-- =========================================================
CREATE TABLE perfil_biometrico (
    id                    UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
    estudiante_id         UUID      NOT NULL UNIQUE REFERENCES estudiante(id) ON DELETE CASCADE,
    imagen_referencia_url TEXT,
    vector_facial         FLOAT[],
    creado_en             TIMESTAMP NOT NULL DEFAULT NOW(),
    actualizado_en        TIMESTAMP NOT NULL DEFAULT NOW(),
    activo                BOOLEAN   NOT NULL DEFAULT TRUE
);

-- =========================================================
-- PERIODO ACADEMICO
-- =========================================================
CREATE TABLE periodo_academico (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    docente_id   UUID         NOT NULL REFERENCES docente(id) ON DELETE CASCADE,
    nombre       VARCHAR(120) NOT NULL,
    tipo         tipo_periodo NOT NULL,
    fecha_inicio DATE         NOT NULL,
    fecha_fin    DATE         NOT NULL,
    activo       BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en    TIMESTAMP    NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_fechas CHECK (fecha_fin > fecha_inicio)
);

-- =========================================================
-- MATERIA
-- =========================================================
CREATE TABLE materia (
    id         UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    docente_id UUID         NOT NULL REFERENCES docente(id) ON DELETE CASCADE,
    nombre     VARCHAR(120) NOT NULL,
    codigo     VARCHAR(30),
    descripcion TEXT,
    creado_en  TIMESTAMP    NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_materia_codigo_docente UNIQUE (docente_id, codigo)
);

-- =========================================================
-- GRUPO
-- =========================================================
CREATE TABLE grupo (
    id                   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    periodo_academico_id UUID         NOT NULL REFERENCES periodo_academico(id) ON DELETE RESTRICT,
    materia_id           UUID         NOT NULL REFERENCES materia(id) ON DELETE RESTRICT,
    nombre               VARCHAR(120) NOT NULL,
    codigo_invitacion    VARCHAR(12)  UNIQUE,
    cupo_maximo          INTEGER,
    activo               BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en            TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- =========================================================
-- HORARIO SEMANAL
-- =========================================================
CREATE TABLE horario_semanal (
    id          UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
    grupo_id    UUID      NOT NULL REFERENCES grupo(id) ON DELETE CASCADE,
    dia_semana  dia_semana NOT NULL,
    hora_inicio TIME      NOT NULL,
    hora_fin    TIME      NOT NULL,
    CONSTRAINT chk_horario_horas CHECK (hora_fin > hora_inicio),
    CONSTRAINT uq_horario_grupo_dia UNIQUE (grupo_id, dia_semana, hora_inicio)
);

-- =========================================================
-- CLASE
-- =========================================================
CREATE TABLE clase (
    id            UUID       PRIMARY KEY DEFAULT gen_random_uuid(),
    grupo_id      UUID       NOT NULL REFERENCES grupo(id) ON DELETE CASCADE,
    fecha         DATE       NOT NULL,
    hora_inicio   TIME       NOT NULL,
    hora_fin      TIME       NOT NULL,
    tipo          tipo_clase NOT NULL DEFAULT 'clase',
    cancelada     BOOLEAN    NOT NULL DEFAULT FALSE,
    observaciones TEXT,
    creado_en     TIMESTAMP  NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_clase_grupo_fecha_hora UNIQUE (grupo_id, fecha, hora_inicio)
);

-- =========================================================
-- INSCRIPCION
-- =========================================================
CREATE TABLE inscripcion (
    id                UUID               PRIMARY KEY DEFAULT gen_random_uuid(),
    grupo_id          UUID               NOT NULL REFERENCES grupo(id) ON DELETE CASCADE,
    estudiante_id     UUID               NOT NULL REFERENCES estudiante(id) ON DELETE CASCADE,
    fecha_inscripcion TIMESTAMP          NOT NULL DEFAULT NOW(),
    estado            estado_inscripcion NOT NULL DEFAULT 'activa',
    CONSTRAINT uq_inscripcion UNIQUE (grupo_id, estudiante_id)
);

-- =========================================================
-- INTENTO BIOMETRICO
-- =========================================================
CREATE TABLE intento_biometrico (
    id                   UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    estudiante_id        UUID                NOT NULL REFERENCES estudiante(id) ON DELETE CASCADE,
    clase_id             UUID                NOT NULL REFERENCES clase(id) ON DELETE CASCADE,
    imagen_capturada_url TEXT,
    puntaje_confianza    FLOAT,
    resultado            resultado_biometrico NOT NULL,
    latitud              DECIMAL(10, 8),
    longitud             DECIMAL(11, 8),
    precision_metros     FLOAT,
    fecha_intento        TIMESTAMP           NOT NULL DEFAULT NOW()
);

-- =========================================================
-- ASISTENCIA
-- =========================================================
CREATE TABLE asistencia (
    id                    UUID              PRIMARY KEY DEFAULT gen_random_uuid(),
    clase_id              UUID              NOT NULL REFERENCES clase(id) ON DELETE CASCADE,
    inscripcion_id        UUID              NOT NULL REFERENCES inscripcion(id) ON DELETE CASCADE,
    intento_biometrico_id UUID              REFERENCES intento_biometrico(id) ON DELETE SET NULL,
    estado                estado_asistencia NOT NULL DEFAULT 'ausente',
    latitud               DECIMAL(10, 8),
    longitud              DECIMAL(11, 8),
    precision_metros      FLOAT,
    fecha_marcado         TIMESTAMP,
    observaciones         TEXT,
    CONSTRAINT uq_asistencia UNIQUE (clase_id, inscripcion_id)
);

-- =========================================================
-- REVISION MANUAL
-- =========================================================
CREATE TABLE revision_manual (
    id            UUID              PRIMARY KEY DEFAULT gen_random_uuid(),
    asistencia_id UUID              NOT NULL UNIQUE REFERENCES asistencia(id) ON DELETE CASCADE,
    docente_id    UUID              NOT NULL REFERENCES docente(id) ON DELETE RESTRICT,
    decision      decision_revision NOT NULL,
    justificacion TEXT,
    revisado_en   TIMESTAMP         NOT NULL DEFAULT NOW()
);

-- =========================================================
-- INDICES
-- =========================================================
CREATE INDEX idx_admin_email         ON administrador(email);
CREATE INDEX idx_periodo_docente     ON periodo_academico(docente_id);
CREATE INDEX idx_materia_docente     ON materia(docente_id);
CREATE INDEX idx_grupo_periodo       ON grupo(periodo_academico_id);
CREATE INDEX idx_grupo_materia       ON grupo(materia_id);
CREATE INDEX idx_horario_grupo       ON horario_semanal(grupo_id);
CREATE INDEX idx_clase_grupo         ON clase(grupo_id);
CREATE INDEX idx_clase_fecha         ON clase(fecha);
CREATE INDEX idx_inscripcion_grupo   ON inscripcion(grupo_id);
CREATE INDEX idx_inscripcion_est     ON inscripcion(estudiante_id);
CREATE INDEX idx_inscripcion_estado  ON inscripcion(estado);
CREATE INDEX idx_asistencia_clase    ON asistencia(clase_id);
CREATE INDEX idx_intento_estudiante  ON intento_biometrico(estudiante_id);
CREATE INDEX idx_intento_clase       ON intento_biometrico(clase_id);
