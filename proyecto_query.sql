USE NODO;

-- 1. Listar todos los estudiantes (nombre completo, matrícula) de la base de datos ordenados alfabéticamente 
-- por nombre para un año y semestre concreto. 

SELECT u.nombre, MIN(p.numero_matricula) AS numero_matricula
FROM Usuarios u
JOIN Pagos p ON u.id_usuario = p.id_estudiante
JOIN Curso c ON p.id_curso = c.id_curso
WHERE u.rol = 'Estudiante'
  AND c.anio = 2026 
  AND c.semestre = '1'
GROUP BY u.id_usuario, u.nombre
ORDER BY u.nombre ASC;


-- 2. Listar todos los estudiantes (nombre completo) de la base de datos de un curso determinado 
-- para un año y semestre concreto.
SELECT u.nombre
FROM Usuarios u
JOIN Pagos p ON u.id_usuario = p.id_estudiante
JOIN Curso c ON p.id_curso = c.id_curso
WHERE u.rol = 'Estudiante'
  AND c.id_curso = 29 
  AND c.anio = 2026 
  AND c.semestre = '2'
ORDER BY u.nombre ASC;

-- 3. Listar todos los cursos que un estudiante ha tenido entre un rango de fechas en la base de datos.
SELECT c.nombre AS nombre_curso, c.fecha_inicio, c.fecha_fin
FROM Curso c
JOIN Pagos p ON c.id_curso = p.id_curso
JOIN Usuarios u ON p.id_estudiante = u.id_usuario
WHERE u.rol = 'Estudiante'
  AND u.id_usuario = 46
  AND c.fecha_inicio >= '2025-07-01' 
  AND c.fecha_fin <= '2025-12-31'
ORDER BY c.fecha_inicio;

-- 4. Listar los profesores (número de identificación, nombre completo) y los cursos que tiene asignados actualmente.
SELECT u.n_documento, u.nombre, c.nombre AS nombre_curso
FROM Usuarios u
JOIN Curso c ON u.id_usuario = c.id_profesor
WHERE u.rol = 'Profesor'
  AND c.fecha_fin >= CURDATE()
ORDER BY u.nombre, c.nombre;

-- 5. Listar todos los cursos ordenados por categoría. (nombre del curso, categoría).
SELECT nombre, categoria
FROM Curso
ORDER BY categoria, nombre;

-- 6. Listar los cursos con un rango de precio entre val_minimo y val_máximo
SELECT nombre, precio
FROM Curso
WHERE precio BETWEEN 500000.00 AND 1000000.00
ORDER BY precio;

-- 7. Listar los usuarios que están registrados, pero no están matriculados en ningún curso para un año y semestre específico.
SELECT u.id_usuario, u.nombre, u.email
FROM Usuarios u
WHERE u.rol = 'Estudiante'
  AND u.id_usuario NOT IN (
    SELECT p.id_estudiante
    FROM Pagos p
    JOIN Curso c ON p.id_curso = c.id_curso
    WHERE c.anio = 2025 AND c.semestre = '2'
)
ORDER BY u.nombre;

-- 8. Listar los cursos que se encuentran en una categoría (ejemplo: la categoría Informática).
SELECT id_curso, nombre, precio
FROM Curso
WHERE categoria = 'Ciencias'
ORDER BY nombre;

-- 9. Listar las tareas que los estudiantes deben realizar en el curso dado con identificador x
SELECT id_tarea, nombre, descripcion, fecha_limite
FROM Tarea
WHERE id_curso = 4
ORDER BY fecha_limite;

-- 10. Listar los materiales que el profesor ha publicado en un curso dado
SELECT id_material, titulo, descripcion, formato_archivo, nombre_archivo
FROM Material
WHERE id_curso = 3
ORDER BY id_material;

-- 11. Listar todos los mensajes de un foro en un curso, listando el id y nombre del que envió en mensaje
SELECT 
    m.id_mensaje,
    m.nombre AS titulo_mensaje,
    m.descripcion,
    m.tipo_usuario,
    m.fecha_envio,
    u.id_usuario,
    u.nombre AS nombre_usuario,
    m.id_replica,
    CASE 
        WHEN m.id_replica IS NULL THEN 'No es respuesta'
        ELSE CONCAT('Respuesta al mensaje ', m.id_replica)
    END AS es_respuesta
FROM Mensaje m
JOIN Usuarios u ON m.id_usuario = u.id_usuario
WHERE m.id_foro = 5
ORDER BY m.id_mensaje;

-- 12. Consulta adicional: Estadísticas de matriculación por curso (número de estudiantes matriculados por curso)
SELECT c.id_curso, c.nombre, COUNT(p.id_estudiante) AS total_estudiantes
FROM Curso c
LEFT JOIN Pagos p ON c.id_curso = p.id_curso
GROUP BY c.id_curso, c.nombre
ORDER BY total_estudiantes DESC;
