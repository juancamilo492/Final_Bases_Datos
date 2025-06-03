CREATE DATABASE IF NOT EXISTS NODO;

USE NODO;

CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario INTEGER AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    n_documento VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    genero ENUM('F', 'M') NOT NULL,
    telefono VARCHAR(10) NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    rol ENUM('Estudiante', 'Profesor', 'Administrador') NOT NULL,
    area_principal VARCHAR(100),
    area_alternativa VARCHAR(100),
    CHECK (rol = 'Profesor' OR (area_principal IS NULL AND area_alternativa IS NULL))
);

CREATE TABLE IF NOT EXISTS Curso (
    id_curso INTEGER AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    semestre ENUM('1', '2') NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    anio YEAR NOT NULL,
    precio NUMERIC(10, 2) NOT NULL,
    id_profesor INTEGER,
    FOREIGN KEY (id_profesor) REFERENCES Usuarios(id_usuario)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Tarea (
    id_tarea INTEGER AUTO_INCREMENT,
    id_curso INTEGER,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_limite DATE NOT NULL,
    nombre_archivo VARCHAR(100) NOT NULL,
    formato_archivo VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_tarea, id_curso),
    FOREIGN KEY (id_curso) REFERENCES Curso(id_curso)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Tarea_Entrega (
    id_entrega INTEGER AUTO_INCREMENT,
    id_tarea INTEGER,
    id_curso INTEGER,
    id_estudiante INTEGER,
    nombre_archivo VARCHAR(100) NOT NULL,
    formato_archivo VARCHAR(50) NOT NULL,
    fecha_entrega TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    puntaje_obtenido NUMERIC(3,2) CHECK (puntaje_obtenido >= 0.00 AND puntaje_obtenido <= 5.00),
    PRIMARY KEY (id_entrega, id_tarea, id_curso),
    FOREIGN KEY (id_tarea, id_curso) REFERENCES Tarea(id_tarea, id_curso)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (id_estudiante) REFERENCES Usuarios(id_usuario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Foro (
    id_foro INTEGER AUTO_INCREMENT,
    id_curso INTEGER,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    fecha_creacion DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    PRIMARY KEY (id_foro, id_curso),
    UNIQUE (id_foro), -- Added UNIQUE constraint to allow FK reference from Mensaje
    FOREIGN KEY (id_curso) REFERENCES Curso(id_curso)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Mensaje (
    id_mensaje INTEGER AUTO_INCREMENT,
    id_foro INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    id_usuario INTEGER NOT NULL,
    tipo_usuario ENUM('Estudiante', 'Profesor') NOT NULL,
    id_replica INTEGER,
    fecha_envio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_mensaje), 
    FOREIGN KEY (id_foro) REFERENCES Foro(id_foro) -- Now references Foro.id_foro (which is UNIQUE)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (id_replica) REFERENCES Mensaje(id_mensaje) -- Self-referencing FK
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Material (
    id_material INTEGER AUTO_INCREMENT,
    id_curso INTEGER,
    titulo VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    formato_archivo VARCHAR(50) NOT NULL,
    nombre_archivo VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_material, id_curso),
    FOREIGN KEY (id_curso) REFERENCES Curso(id_curso)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Pagos (
    numero_matricula INTEGER AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INTEGER NOT NULL,
    id_curso INTEGER NOT NULL,
    fecha_pago TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_estudiante, id_curso),
    FOREIGN KEY (id_estudiante) REFERENCES Usuarios(id_usuario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (id_curso) REFERENCES Curso(id_curso)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS interes_curso (
    id_profesor INTEGER,
    id_curso INTEGER,
    PRIMARY KEY (id_profesor, id_curso),
    FOREIGN KEY (id_profesor) REFERENCES Usuarios(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (id_curso) REFERENCES Curso(id_curso)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
