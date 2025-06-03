import mysql.connector
import os
from datetime import datetime
import decimal

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'bruno123',
    'database': 'NODO'
}
CURRENT_USER = None

# Limpia la pantalla según el sistema operativo (Windows o Unix).
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# Pausa la ejecución hasta que el usuario presione Enter.
def pausar_pantalla():
    input("\nPresione Enter para continuar...")

# Establece una conexión con la base de datos usando DB_CONFIG.
def obtener_conexion_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        if err.errno == 1045:
            print(f"Acceso denegado para el usuario '{DB_CONFIG['user']}'@'{DB_CONFIG['host']}'. Verifique el usuario y la contraseña en DB_CONFIG.")
        elif err.errno == 1049:
            print(f"La base de datos '{DB_CONFIG['database']}' no existe. Asegúrese de haberla creado y ejecutado el DDL.")
        elif err.errno == 2003:
            print(f"No se pudo conectar al servidor MySQL en '{DB_CONFIG['host']}'. ¿Está el servidor en ejecución?")
        return None

# Ejecuta una consulta SQL y retorna resultados según los parámetros (fetch_one o fetch_all).
def ejecutar_consulta(query, params=None, fetch_one=False, fetch_all=False, connection=None):
    conn = connection or obtener_conexion_db()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None
        return result
    except mysql.connector.Error as err:
        print(f"Error al ejecutar la consulta: {err}")
        return None
    finally:
        cursor.close()
        if not connection:
            conn.close()

# Ejecuta una consulta de actualización (INSERT, UPDATE, DELETE) y maneja transacciones.
def ejecutar_actualizacion(query, params=None, connection=None):
    conn = connection or obtener_conexion_db()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error al ejecutar la actualización: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        if not connection:
            conn.close()

# Muestra datos en formato de tabla con encabezados personalizados.
def mostrar_tabla(data, headers):
    if not data:
        print("No hay datos para mostrar.")
        return
    if not isinstance(data, list):
        data = [data]
    if not data or not isinstance(data[0], dict):
        if isinstance(data[0], dict) and all(h in data[0] for h in headers):
            pass
        else:
            print("Formato de datos incorrecto para la tabla.")
            return
    col_widths = {header: len(header) for header in headers}
    for row in data:
        for header in headers:
            col_widths[header] = max(col_widths[header], len(str(row.get(header, ''))))
    header_line = " | ".join(header.ljust(col_widths[header]) for header in headers)
    print(header_line)
    print("-" * len(header_line))
    for row in data:
        row_line = " | ".join(str(row.get(header, '')).ljust(col_widths[header]) for header in headers)
        print(row_line)
    print("-" * len(header_line))

# Autentica al usuario verificando email y contraseña en la base de datos.
def iniciar_sesion():
    global CURRENT_USER
    limpiar_pantalla()
    print("--- Inicio de Sesión ---")
    email = input("Email: ")
    password = input("Contraseña: ")
    query = "SELECT id_usuario, nombre, rol, contrasenia FROM Usuarios WHERE email = %s"
    user_data = ejecutar_consulta(query, (email,), fetch_one=True)
    if user_data and user_data['contrasenia'] == password:
        CURRENT_USER = {
            'id_usuario': user_data['id_usuario'],
            'nombre': user_data['nombre'],
            'rol': user_data['rol']
        }
        print(f"\nBienvenido, {CURRENT_USER['nombre']} ({CURRENT_USER['rol']})!")
        return True
    else:
        print("\nEmail o contraseña incorrectos.")
        CURRENT_USER = None
        return False

# Cierra la sesión del usuario actual.
def cerrar_sesion():
    global CURRENT_USER
    CURRENT_USER = None
    print("\nSesión cerrada.")

# Muestra el menú principal para usuarios con rol de administrador y gestiona sus acciones.
def menu_administrador():
    while True:
        limpiar_pantalla()
        print(f"--- Menú Administrador: {CURRENT_USER['nombre']} ---")
        print("1. Matricular Usuario a Curso")
        print("2. Asignar Profesor a Curso")
        print("3. Ver Reportes")
        print("4. Acceder como Profesor (Simulado)")
        print("5. Acceder como Estudiante (Simulado)")
        print("0. Cerrar Sesión")
        choice = input("Seleccione una opción: ")
        if choice == '1':
            matricular_usuario_curso()
        elif choice == '2':
            asignar_profesor_curso()
        elif choice == '3':
            menu_reportes()
        elif choice == '4':
            original_user = CURRENT_USER.copy()
            CURRENT_USER['rol'] = 'Profesor'
            print("\nAccediendo a funciones de Profesor...")
            pausar_pantalla()
            menu_profesor()
            CURRENT_USER = original_user
            if not CURRENT_USER.get('id_usuario'):
                break
        elif choice == '5':
            original_user = CURRENT_USER.copy()
            CURRENT_USER['rol'] = 'Estudiante'
            print("\nAccediendo a funciones de Estudiante...")
            pausar_pantalla()
            menu_estudiante()
            CURRENT_USER = original_user
            if not CURRENT_USER.get('id_usuario'):
                break
        elif choice == '0':
            cerrar_sesion()
            break
        else:
            print("Opción no válida.")
        if CURRENT_USER and CURRENT_USER.get('id_usuario'):
            pausar_pantalla()

# Permite al administrador matricular un estudiante en un curso.
def matricular_usuario_curso():
    limpiar_pantalla()
    print("--- Matricular Usuario a Curso ---")
    students = ejecutar_consulta("SELECT id_usuario, nombre, email FROM Usuarios WHERE rol = 'Estudiante' ORDER BY nombre", fetch_all=True)
    if not students:
        print("No hay estudiantes registrados.")
        return
    print("\nEstudiantes Disponibles:")
    mostrar_tabla(students, ['id_usuario', 'nombre', 'email'])
    try:
        student_id = int(input("ID del Estudiante a matricular: "))
        if not any(s['id_usuario'] == student_id for s in students):
            print("ID de estudiante no válido.")
            return
    except ValueError:
        print("ID de estudiante debe ser un número.")
        return
    courses = ejecutar_consulta("SELECT id_curso, nombre, categoria FROM Curso ORDER BY nombre", fetch_all=True)
    if not courses:
        print("No hay cursos disponibles.")
        return
    print("\nCursos Disponibles:")
    mostrar_tabla(courses, ['id_curso', 'nombre', 'categoria'])
    try:
        course_id = int(input("ID del Curso: "))
        if not any(c['id_curso'] == course_id for c in courses):
            print("ID de curso no válido.")
            return
    except ValueError:
        print("ID de curso debe ser un número.")
        return
    check_query = "SELECT 1 FROM Pagos WHERE id_estudiante = %s AND id_curso = %s"
    if ejecutar_consulta(check_query, (student_id, course_id), fetch_one=True):
        print("El estudiante ya está matriculado en este curso.")
        return
    enroll_query = "INSERT INTO Pagos (id_estudiante, id_curso) VALUES (%s, %s)"
    if ejecutar_actualizacion(enroll_query, (student_id, course_id)):
        print("Estudiante matriculado exitosamente.")
    else:
        print("Error al matricular al estudiante.")

# Permite al administrador asignar un profesor a un curso.
def asignar_profesor_curso():
    limpiar_pantalla()
    print("--- Asignar Profesor a Curso ---")
    professors = ejecutar_consulta("SELECT id_usuario, nombre, email FROM Usuarios WHERE rol = 'Profesor' ORDER BY nombre", fetch_all=True)
    if not professors:
        print("No hay profesores registrados.")
        return
    print("\nProfesores Disponibles:")
    mostrar_tabla(professors, ['id_usuario', 'nombre', 'email'])
    try:
        profesor_id = int(input("ID del Profesor a asignar: "))
        if not any(p['id_usuario'] == profesor_id for p in professors):
            print("ID de profesor no válido.")
            return
    except ValueError:
        print("ID de profesor debe ser un número.")
        return
    courses = ejecutar_consulta("SELECT c.id_curso, c.nombre, c.categoria, u.nombre as profesor_actual FROM Curso c LEFT JOIN Usuarios u ON c.id_profesor = u.id_usuario ORDER BY c.nombre", fetch_all=True)
    if not courses:
        print("No hay cursos disponibles.")
        return
    print("\nCursos Disponibles:")
    mostrar_tabla(courses, ['id_curso', 'nombre', 'categoria', 'profesor_actual'])
    try:
        course_id = int(input("ID del Curso para asignar profesor: "))
        if not any(c['id_curso'] == course_id for c in courses):
            print("ID de curso no válido.")
            return
    except ValueError:
        print("ID de curso debe ser un número.")
        return
    assign_query = "UPDATE Curso SET id_profesor = %s WHERE id_curso = %s"
    if ejecutar_actualizacion(assign_query, (profesor_id, course_id)):
        print("Profesor asignado al curso exitosamente.")
    else:
        print("Error al asignar el profesor.")

# Muestra un menú para que el administrador acceda a diferentes reportes.
def menu_reportes():
    while True:
        limpiar_pantalla()
        print("--- Menú de Reportes ---")
        print("1. Listar todos los Cursos (con filtros)")
        print("2. Ver Información de un Curso Específico")
        print("3. Listar Usuarios (con filtros)")
        print("0. Volver al Menú Principal de Administrador")
        choice = input("Seleccione una opción: ")
        if choice == '1':
            reporte_listar_cursos()
        elif choice == '2':
            reporte_ver_info_curso()
        elif choice == '3':
            reporte_listar_usuarios()
        elif choice == '0':
            break
        else:
            print("Opción no válida.")
        pausar_pantalla()

# Genera un reporte de cursos con filtros opcionales por código, profesor, categoría o fechas.
def reporte_listar_cursos():
    limpiar_pantalla()
    print("--- Reporte: Listar Cursos ---")
    base_query = "SELECT c.id_curso, c.nombre, c.categoria, c.semestre, c.anio, c.fecha_inicio, c.fecha_fin, u.nombre as nombre_profesor, c.precio FROM Curso c LEFT JOIN Usuarios u ON c.id_profesor = u.id_usuario"
    filters = []
    params = []
    print("\nOpciones de Filtro (deje en blanco para no aplicar):")
    cod_curso = input("Filtrar por Código de Curso (ID): ")
    if cod_curso:
        try:
            filters.append("c.id_curso = %s")
            params.append(int(cod_curso))
        except ValueError: print("Código de curso debe ser numérico.")
    cod_profesor = input("Filtrar por Código de Profesor (ID): ")
    if cod_profesor:
        try:
            filters.append("c.id_profesor = %s")
            params.append(int(cod_profesor))
        except ValueError: print("Código de profesor debe ser numérico.")
    categoria = input("Filtrar por Categoría (ej: Informática, Matemáticas): ")
    if categoria:
        filters.append("c.categoria LIKE %s")
        params.append(f"%{categoria}%")
    fecha_inicio_desde = input("Filtrar por Fecha de Inicio DESDE (YYYY-MM-DD): ")
    fecha_inicio_hasta = input("Filtrar por Fecha de Inicio HASTA (YYYY-MM-DD): ")
    if fecha_inicio_desde:
        try:
            datetime.strptime(fecha_inicio_desde, '%Y-%m-%d')
            filters.append("c.fecha_inicio >= %s")
            params.append(fecha_inicio_desde)
        except ValueError: print("Formato de fecha DESDE incorrecto.")
    if fecha_inicio_hasta:
        try:
            datetime.strptime(fecha_inicio_hasta, '%Y-%m-%d')
            filters.append("c.fecha_inicio <= %s")
            params.append(fecha_inicio_hasta)
        except ValueError: print("Formato de fecha HASTA incorrecto.")
    if filters:
        base_query += " WHERE " + " AND ".join(filters)
    base_query += " ORDER BY c.anio DESC, c.semestre DESC, c.nombre ASC"
    cursos = ejecutar_consulta(base_query, tuple(params), fetch_all=True)
    if cursos:
        print("\n--- Lista de Cursos ---")
        mostrar_tabla(cursos, ['id_curso', 'nombre', 'categoria', 'semestre', 'anio', 'fecha_inicio', 'fecha_fin', 'nombre_profesor', 'precio'])
    else:
        print("No se encontraron cursos con los filtros aplicados.")

# Muestra detalles de un curso específico, incluyendo estudiantes matriculados.
def reporte_ver_info_curso():
    limpiar_pantalla()
    print("--- Reporte: Información de Curso Específico ---")
    try:
        course_id = int(input("Ingrese el ID del Curso: "))
    except ValueError:
        print("ID de curso debe ser un número.")
        return
    course_query = """
        SELECT c.id_curso, c.nombre, c.url, c.semestre, c.anio, c.fecha_inicio, c.fecha_fin,
               c.categoria, c.precio, u.nombre as nombre_profesor, u.email as email_profesor
        FROM Curso c
        LEFT JOIN Usuarios u ON c.id_profesor = u.id_usuario
        WHERE c.id_curso = %s
    """
    course_details = ejecutar_consulta(course_query, (course_id,), fetch_one=True)
    if not course_details:
        print(f"No se encontró el curso con ID {course_id}.")
        return
    print("\n--- Detalles del Curso ---")
    for key, value in course_details.items():
        print(f"{key.replace('_', ' ').capitalize()}: {value}")
    students_query = """
        SELECT u.id_usuario, u.nombre, u.email
        FROM Usuarios u
        JOIN Pagos p ON u.id_usuario = p.id_estudiante
        WHERE p.id_curso = %s AND u.rol = 'Estudiante'
        ORDER BY u.nombre
    """
    students = ejecutar_consulta(students_query, (course_id,), fetch_all=True)
    print("\n--- Estudiantes Matriculados ---")
    if students:
        mostrar_tabla(students, ['id_usuario', 'nombre', 'email'])
    else:
        print("No hay estudiantes matriculados en este curso.")

# Genera un reporte de usuarios con filtros opcionales por ID, rol o nombre.
def reporte_listar_usuarios():
    limpiar_pantalla()
    print("--- Reporte: Listar Usuarios ---")
    base_query = "SELECT id_usuario, nombre, email, rol, n_documento, genero, telefono FROM Usuarios"
    filters = []
    params = []
    print("\nOpciones de Filtro (deje en blanco para no aplicar):")
    user_id_filter = input("Filtrar por ID de Usuario: ")
    if user_id_filter:
        try:
            filters.append("id_usuario = %s")
            params.append(int(user_id_filter))
        except ValueError: print("ID de usuario debe ser numérico.")
    role_filter = input("Filtrar por Rol (Estudiante, Profesor, Administrador): ")
    if role_filter:
        if role_filter.capitalize() in ['Estudiante', 'Profesor', 'Administrador']:
            filters.append("rol = %s")
            params.append(role_filter.capitalize())
        else: print("Rol no válido. Use Estudiante, Profesor o Administrador.")
    nombre_filter = input("Filtrar por Nombre (parcial): ")
    if nombre_filter:
        filters.append("nombre LIKE %s")
        params.append(f"%{nombre_filter}%")
    if filters:
        base_query += " WHERE " + " AND ".join(filters)
    base_query += " ORDER BY rol, nombre"
    users = ejecutar_consulta(base_query, tuple(params), fetch_all=True)
    if users:
        print("\n--- Lista de Usuarios ---")
        mostrar_tabla(users, ['id_usuario', 'nombre', 'email', 'rol', 'n_documento', 'genero', 'telefono'])
    else:
        print("No se encontraron usuarios con los filtros aplicados.")

# Lista los cursos asignados al usuario (estudiante o profesor).
def listar_mis_cursos():
    limpiar_pantalla()
    print(f"--- Mis Cursos: {CURRENT_USER['nombre']} ---")
    query = ""
    params = (CURRENT_USER['id_usuario'],)
    if CURRENT_USER['rol'] == 'Estudiante':
        query = """
            SELECT c.id_curso, c.nombre, c.categoria, u.nombre as profesor_nombre
            FROM Curso c
            JOIN Pagos p ON c.id_curso = p.id_curso
            LEFT JOIN Usuarios u ON c.id_profesor = u.id_usuario
            WHERE p.id_estudiante = %s
            ORDER BY c.nombre
        """
    elif CURRENT_USER['rol'] == 'Profesor':
        query = """
            SELECT c.id_curso, c.nombre, c.categoria
            FROM Curso c
            WHERE c.id_profesor = %s
            ORDER BY c.nombre
        """
    else:
        print("Rol no válido para esta función.")
        return []
    cursos = ejecutar_consulta(query, params, fetch_all=True)
    if cursos:
        headers = ['id_curso', 'nombre', 'categoria']
        if CURRENT_USER['rol'] == 'Estudiante':
            headers.append('profesor_nombre')
        mostrar_tabla(cursos, headers)
    else:
        print("No tienes cursos asignados o matriculados.")
    return cursos if cursos else []

# Interfaz para que un estudiante entregue una tarea o vea su calificación.
def entregar_tarea_interfaz(course_id):
    limpiar_pantalla()
    print(f"--- Entregar Tarea para el Curso (ID: {course_id}) ---")
    student_id = CURRENT_USER['id_usuario']
    tasks = listar_tareas_curso(course_id, display_title=False)
    if not tasks:
        print("No hay tareas definidas para este curso.")
        return
    try:
        task_id_to_submit = int(input("Ingrese el ID de la tarea que desea entregar/ver la calificación: "))
        selected_task = next((t for t in tasks if t['id_tarea'] == task_id_to_submit), None)
        if not selected_task:
            print("ID de tarea no válido para este curso.")
            return
    except ValueError:
        print("ID de tarea debe ser numérico.")
        return
    print(f"\nEntregando tarea: '{selected_task['nombre']}'")
    prev_submissions_query = """
        SELECT id_entrega, nombre_archivo, formato_archivo, fecha_entrega, puntaje_obtenido
        FROM Tarea_Entrega
        WHERE id_tarea = %s AND id_curso = %s AND id_estudiante = %s
        ORDER BY fecha_entrega DESC
    """
    prev_submissions = ejecutar_consulta(prev_submissions_query, (task_id_to_submit, course_id, student_id), fetch_all=True)
    if prev_submissions:
        print("\n--- Tus Entregas Anteriores para esta Tarea ---")
        mostrar_tabla(prev_submissions, ['id_entrega', 'nombre_archivo', 'formato_archivo', 'fecha_entrega', 'puntaje_obtenido'])
        re_submit = input("Ya has entregado esta tarea. ¿Deseas realizar una nueva entrega? (s/n): ")
        if re_submit.lower() != 's':
            return
    nombre_archivo_entrega = input("Nombre del archivo de tu entrega (ej: mi_tarea.pdf, solucion.docx): ")
    formato_archivo_entrega = input("Formato del archivo (ej: pdf, docx, py): ")
    if not nombre_archivo_entrega or not formato_archivo_entrega:
        print("El nombre y el formato del archivo son obligatorios.")
        return
    insert_query = """
        INSERT INTO Tarea_Entrega
            (id_tarea, id_curso, id_estudiante, nombre_archivo, formato_archivo, fecha_entrega, puntaje_obtenido)
        VALUES (%s, %s, %s, %s, %s, NOW(), NULL)
    """
    params = (task_id_to_submit, course_id, student_id, nombre_archivo_entrega, formato_archivo_entrega)
    if ejecutar_actualizacion(insert_query, params):
        print("Tarea entregada exitosamente. Quedará pendiente de calificación.")
    else:
        print("Error al entregar la tarea.")

# Interfaz para que un profesor califique las entregas de tareas.
def calificar_tarea_interfaz(course_id):
    limpiar_pantalla()
    print(f"--- Calificar Tareas para el Curso (ID: {course_id}) ---")
    tasks = listar_tareas_curso(course_id, display_title=False)
    if not tasks:
        print("No hay tareas definidas para este curso para calificar.")
        return
    try:
        task_id_to_grade = int(input("Ingrese el ID de la tarea para la cual desea calificar entregas: "))
        selected_task = next((t for t in tasks if t['id_tarea'] == task_id_to_grade), None)
        if not selected_task:
            print("ID de tarea no válido para este curso.")
            return
    except ValueError:
        print("ID de tarea debe ser numérico.")
        return
    print(f"\n--- Calificando Entregas para Tarea: '{selected_task['nombre']}' (ID: {task_id_to_grade}) ---")
    submissions_query = """
        SELECT te.id_entrega, u.nombre as estudiante_nombre, u.email as estudiante_email,
               te.nombre_archivo, te.formato_archivo, te.fecha_entrega, te.puntaje_obtenido
        FROM Tarea_Entrega te
        JOIN Usuarios u ON te.id_estudiante = u.id_usuario
        WHERE te.id_tarea = %s AND te.id_curso = %s
        ORDER BY (te.puntaje_obtenido IS NULL) DESC, u.nombre, te.fecha_entrega
    """
    submissions = ejecutar_consulta(submissions_query, (task_id_to_grade, course_id), fetch_all=True)
    if not submissions:
        print("No hay entregas para esta tarea aún.")
        return
    print("\n--- Entregas Recibidas ---")
    mostrar_tabla(submissions, ['id_entrega', 'estudiante_nombre', 'estudiante_email', 'nombre_archivo', 'formato_archivo', 'fecha_entrega', 'puntaje_obtenido'])
    try:
        entrega_id_to_grade = int(input("Ingrese el ID de la entrega que desea calificar (o 0 para no calificar): "))
        if entrega_id_to_grade == 0:
            return
        selected_submission = next((s for s in submissions if s['id_entrega'] == entrega_id_to_grade), None)
        if not selected_submission:
            print("ID de entrega no válido.")
            return
    except ValueError:
        print("ID de entrega debe ser numérico.")
        return
    print(f"\nCalificando entrega de: {selected_submission['estudiante_nombre']}")
    print(f"Archivo: {selected_submission['nombre_archivo']} ({selected_submission['formato_archivo']})")
    print(f"Puntaje actual: {selected_submission['puntaje_obtenido'] if selected_submission['puntaje_obtenido'] is not None else 'Sin calificar'}")
    while True:
        try:
            score_str = input("Ingrese el puntaje (0.00 - 5.00): ")
            score = decimal.Decimal(score_str)
            if not (decimal.Decimal('0.00') <= score <= decimal.Decimal('5.00')):
                raise ValueError("El puntaje debe estar entre 0.00 y 5.00.")
            if score.as_tuple().exponent < -2:
                raise ValueError("El puntaje no puede tener más de dos decimales.")
            break
        except ValueError as e:
            print(f"Entrada no válida: {e}")
        except decimal.InvalidOperation:
            print("Entrada no válida: Ingrese un número decimal para el puntaje.")
    update_query = "UPDATE Tarea_Entrega SET puntaje_obtenido = %s WHERE id_entrega = %s"
    if ejecutar_actualizacion(update_query, (score, entrega_id_to_grade)):
        print("Calificación asignada exitosamente.")
    else:
        print("Error al asignar la calificación.")

# Lista los estudiantes matriculados en un curso.
def listar_alumnos_curso(course_id):
    limpiar_pantalla()
    print(f"--- Alumnos del Curso (ID: {course_id}) ---")
    query = """
        SELECT u.id_usuario, u.nombre, u.email
        FROM Usuarios u
        JOIN Pagos p ON u.id_usuario = p.id_estudiante
        WHERE p.id_curso = %s AND u.rol = 'Estudiante'
        ORDER BY u.nombre
    """
    alumnos = ejecutar_consulta(query, (course_id,), fetch_all=True)
    if alumnos:
        mostrar_tabla(alumnos, ['id_usuario', 'nombre', 'email'])
    else:
        print("No hay alumnos matriculados en este curso.")

# Lista los materiales disponibles para un curso.
def listar_materiales_curso(course_id):
    limpiar_pantalla()
    print(f"--- Materiales del Curso (ID: {course_id}) ---")
    query = "SELECT id_material, titulo, descripcion, formato_archivo, nombre_archivo FROM Material WHERE id_curso = %s ORDER BY titulo"
    materiales = ejecutar_consulta(query, (course_id,), fetch_all=True)
    if materiales:
        mostrar_tabla(materiales, ['id_material', 'titulo', 'descripcion', 'formato_archivo', 'nombre_archivo'])
    else:
        print("No hay materiales disponibles para este curso.")

# Muestra el menú de foros para un curso y permite gestionarlos.
def menu_foros_curso(course_id, course_name):
    while True:
        limpiar_pantalla()
        print(f"--- Foros del Curso: {course_name} (ID: {course_id}) ---")
        query_foros = "SELECT id_foro, nombre, descripcion, fecha_creacion, fecha_fin FROM Foro WHERE id_curso = %s ORDER BY fecha_creacion DESC"
        foros = ejecutar_consulta(query_foros, (course_id,), fetch_all=True)
        if not foros:
            print("No hay foros creados para este curso.")
            if CURRENT_USER['rol'] == 'Profesor':
                print("Puedes crear uno desde el menú del curso.")
        else:
            mostrar_tabla(foros, ['id_foro', 'nombre', 'descripcion', 'fecha_creacion', 'fecha_fin'])
        print("\nOpciones:")
        if foros:
            print("1. Ver Mensajes de un Foro")
        print("0. Volver al Menú del Curso")
        choice = input("Seleccione una opción: ")
        if choice == '1' and foros:
            try:
                forum_id_to_view = int(input("Ingrese el ID del foro para ver mensajes: "))
                if any(f['id_foro'] == forum_id_to_view for f in foros):
                    ver_mensajes_foro(forum_id_to_view, course_id)
                else:
                    print("ID de foro no válido.")
            except ValueError:
                print("ID de foro debe ser numérico.")
        elif choice == '0':
            break
        else:
            print("Opción no válida.")
        pausar_pantalla()

# Muestra los mensajes de un foro y permite enviar nuevos mensajes o respuestas.
def ver_mensajes_foro(forum_id, course_id):
    while True:
        limpiar_pantalla()
        forum_info = ejecutar_consulta("SELECT nombre FROM Foro WHERE id_foro = %s AND id_curso = %s", (forum_id, course_id), fetch_one=True)
        if not forum_info:
            print("Foro no encontrado.")
            return
        print(f"--- Mensajes del Foro: {forum_info['nombre']} (ID: {forum_id}) ---")
        messages_query = """
            SELECT m.id_mensaje, m.nombre AS titulo_mensaje, m.descripcion,
                   u.nombre AS remitente_nombre, m.tipo_usuario AS remitente_rol, m.fecha_envio,
                   m.id_replica
            FROM Mensaje m
            JOIN Usuarios u ON m.id_usuario = u.id_usuario
            WHERE m.id_foro = %s
            ORDER BY m.fecha_envio ASC
        """
        messages = ejecutar_consulta(messages_query, (forum_id,), fetch_all=True)
        if messages:
            print("-" * 80)
            for msg in messages:
                print(f"ID Mensaje: {msg['id_mensaje']} | Título: {msg['titulo_mensaje']}")
                print(f"De: {msg['remitente_nombre']} ({msg['remitente_rol']}) | Enviado: {msg['fecha_envio']}")
                if msg['id_replica']:
                    replied_msg_title_query = "SELECT nombre FROM Mensaje WHERE id_mensaje = %s AND id_foro = %s"
                    replied_msg_title_data = ejecutar_consulta(replied_msg_title_query, (msg['id_replica'], forum_id), fetch_one=True)
                    replied_to_title = f"'{replied_msg_title_data['nombre']}'" if replied_msg_title_data else ""
                    print(f"**Respuesta al mensaje ID: {msg['id_replica']} {replied_to_title}**")
                print(f"Mensaje: {msg['descripcion']}")
                print("-" * 80)
        else:
            print("No hay mensajes en este foro aún.")
        print("\nOpciones del Foro:")
        print("1. Enviar Nuevo Mensaje al Foro")
        if messages:
            print("2. Responder a un Mensaje")
        print("0. Volver a la lista de Foros")
        choice = input("Seleccione una opción: ")
        if choice == '1':
            enviar_mensaje_foro(forum_id)
        elif choice == '2' and messages:
            try:
                msg_id_to_reply = int(input("ID del mensaje al que desea responder: "))
                if any(m['id_mensaje'] == msg_id_to_reply for m in messages):
                    enviar_mensaje_foro(forum_id, replica_a_id=msg_id_to_reply)
                else:
                    print("ID de mensaje no válido para responder.")
            except ValueError:
                print("ID de mensaje debe ser numérico.")
        elif choice == '0':
            break
        else:
            print("Opción no válida.")
        pausar_pantalla()

# Permite enviar un nuevo mensaje o responder a uno existente en un foro.
def enviar_mensaje_foro(forum_id, replica_a_id=None):
    limpiar_pantalla()
    action = "Responder a Mensaje" if replica_a_id else "Enviar Nuevo Mensaje"
    print(f"--- {action} en Foro (ID: {forum_id}) ---")
    titulo = input("Título del mensaje: ")
    descripcion = input("Contenido del mensaje: ")
    tipo_usuario_mensaje = CURRENT_USER['rol']
    if tipo_usuario_mensaje not in ['Estudiante', 'Profesor']:
        print(f"Error: El rol '{tipo_usuario_mensaje}' no puede publicar mensajes directamente.")
        print("Los administradores deben usar las funciones de profesor/estudiante para interactuar (simulación).")
        return
    query = """
        INSERT INTO Mensaje (id_foro, nombre, descripcion, id_usuario, tipo_usuario, id_replica, fecha_envio)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """
    params = (forum_id, titulo, descripcion, CURRENT_USER['id_usuario'], tipo_usuario_mensaje, replica_a_id)
    if ejecutar_actualizacion(query, params):
        print("Mensaje enviado exitosamente.")
    else:
        print("Error al enviar el mensaje.")

# Lista las tareas asignadas a un curso.
def listar_tareas_curso(course_id, display_title=True):
    if display_title:
        limpiar_pantalla()
        print(f"--- Tareas del Curso (ID: {course_id}) ---")
    query = """
        SELECT id_tarea, nombre, descripcion, fecha_limite, nombre_archivo, formato_archivo
        FROM Tarea
        WHERE id_curso = %s
        ORDER BY fecha_limite
    """
    tareas = ejecutar_consulta(query, (course_id,), fetch_all=True)
    if tareas:
        mostrar_tabla(tareas, ['id_tarea', 'nombre', 'descripcion', 'fecha_limite', 'nombre_archivo', 'formato_archivo'])
    elif display_title:
        print("No hay tareas asignadas para este curso.")
    return tareas if tareas else []

# Permite a un profesor subir material a un curso.
def subir_material_curso(course_id):
    limpiar_pantalla()
    print(f"--- Subir Material al Curso (ID: {course_id}) ---")
    titulo = input("Título del material: ")
    descripcion = input("Descripción del material (opcional): ")
    formato_archivo = input("Formato del archivo (ej: pdf, docx, py, url): ")
    nombre_archivo_url = input("Nombre del archivo o URL del material: ")
    if not titulo or not formato_archivo or not nombre_archivo_url:
        print("Título, formato y nombre/URL son obligatorios.")
        return
    query = """
        INSERT INTO Material (id_curso, titulo, descripcion, formato_archivo, nombre_archivo)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (course_id, titulo, descripcion, formato_archivo, nombre_archivo_url)
    if ejecutar_actualizacion(query, params):
        print("Material subido exitosamente.")
    else:
        print("Error al subir el material.")

# Permite a un profesor crear un nuevo foro para un curso.
def crear_foro_curso(course_id):
    limpiar_pantalla()
    print(f"--- Crear Nuevo Foro en Curso (ID: {course_id}) ---")
    nombre = input("Nombre del foro: ")
    descripcion = input("Descripción del foro (opcional): ")
    while True:
        fecha_creacion_str = input("Fecha de creación (YYYY-MM-DD, o Enter para hoy): ")
        if not fecha_creacion_str:
            fecha_creacion = datetime.now().strftime('%Y-%m-%d')
            break
        try:
            fecha_creacion = datetime.strptime(fecha_creacion_str, '%Y-%m-%d').strftime('%Y-%m-%d')
            break
        except ValueError:
            print("Formato de fecha incorrecto. Use YYYY-MM-DD.")
    while True:
        fecha_fin_str = input("Fecha de finalización del foro (YYYY-MM-DD): ")
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').strftime('%Y-%m-%d')
            if fecha_fin < fecha_creacion:
                print("La fecha de fin no puede ser anterior a la fecha de creación.")
            else:
                break
        except ValueError:
            print("Formato de fecha incorrecto. Use YYYY-MM-DD.")
    if not nombre or not fecha_fin_str:
        print("Nombre del foro y fecha de finalización son obligatorios.")
        return
    query = """
        INSERT INTO Foro (id_curso, nombre, descripcion, fecha_creacion, fecha_fin)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (course_id, nombre, descripcion, fecha_creacion, fecha_fin)
    if ejecutar_actualizacion(query, params):
        print("Foro creado exitosamente.")
    else:
        print("Error al crear el foro.")

# Muestra el menú de un curso específico con opciones según el rol del usuario.
def ingresar_menu_curso(course_id, course_name):
    while True:
        limpiar_pantalla()
        print(f"--- Curso: {course_name} (ID: {course_id}) ---")
        print(f"--- Usuario: {CURRENT_USER['nombre']} ({CURRENT_USER['rol']}) ---")
        menu_options = {
            "1": "Listar Alumnos del Curso",
            "2": "Listar Materiales del Curso",
            "3": "Ver Foros del Curso",
            "4": "Ver Tareas del Curso"
        }
        current_option_number = 4
        if CURRENT_USER['rol'] == 'Estudiante':
            current_option_number += 1
            menu_options[str(current_option_number)] = "Entregar/Ver calificación Tarea"
        if CURRENT_USER['rol'] == 'Profesor':
            current_option_number += 1
            menu_options[str(current_option_number)] = "Subir Material al Curso"
            current_option_number += 1
            menu_options[str(current_option_number)] = "Crear Foro en el Curso"
            current_option_number += 1
            menu_options[str(current_option_number)] = "Calificar Entregas de Tarea"
        menu_options["0"] = "Salir del Curso (Volver a Mis Cursos)"
        for key, value in menu_options.items():
            print(f"{key}. {value}")
        choice = input("Seleccione una opción: ")
        action_taken = False
        if choice == '1':
            listar_alumnos_curso(course_id)
            action_taken = True
        elif choice == '2':
            listar_materiales_curso(course_id)
            action_taken = True
        elif choice == '3':
            menu_foros_curso(course_id, course_name)
            action_taken = True
        elif choice == '4':
            listar_tareas_curso(course_id)
            action_taken = True
        elif choice == '0':
            break
        else:
            temp_option_number = 4
            if CURRENT_USER['rol'] == 'Estudiante':
                temp_option_number += 1
                if choice == str(temp_option_number):
                    entregar_tarea_interfaz(course_id)
                    action_taken = True
            elif CURRENT_USER['rol'] == 'Profesor':
                temp_option_number += 1
                if choice == str(temp_option_number):
                    subir_material_curso(course_id)
                    action_taken = True
                else:
                    temp_option_number += 1
                    if choice == str(temp_option_number):
                        crear_foro_curso(course_id)
                        action_taken = True
                    else:
                        temp_option_number += 1
                        if choice == str(temp_option_number):
                            calificar_tarea_interfaz(course_id)
                            action_taken = True
            if not action_taken:
                print("Opción no válida.")
        if action_taken or choice != '0':
            pausar_pantalla()

# Muestra el menú principal para profesores y gestiona sus acciones.
def menu_profesor():
    while True:
        if not CURRENT_USER or CURRENT_USER.get('rol') != 'Profesor':
            break
        limpiar_pantalla()
        print(f"--- Menú Profesor: {CURRENT_USER['nombre']} ---")
        print("1. Listar Mis Cursos")
        print("0. Cerrar Sesión")
        choice = input("Seleccione una opción: ")
        if choice == '1':
            mis_cursos = listar_mis_cursos()
            if mis_cursos:
                try:
                    course_id_selection_str = input("Ingrese el ID del curso para gestionarlo (o 0 para volver): ")
                    if course_id_selection_str == '0':
                        continue
                    course_id_selection = int(course_id_selection_str)
                    selected_course = next((c for c in mis_cursos if c['id_curso'] == course_id_selection), None)
                    if selected_course:
                        ingresar_menu_curso(selected_course['id_curso'], selected_course['nombre'])
                    else:
                        print("ID de curso no válido.")
                except ValueError:
                    print("Entrada no válida.")
                pausar_pantalla()
        elif choice == '0':
            cerrar_sesion()
            break
        else:
            print("Opción no válida.")
            pausar_pantalla()

# Muestra el menú principal para estudiantes y gestiona sus acciones.
def menu_estudiante():
    while True:
        if not CURRENT_USER or CURRENT_USER.get('rol') != 'Estudiante':
            break
        limpiar_pantalla()
        print(f"--- Menú Estudiante: {CURRENT_USER['nombre']} ---")
        print("1. Listar Mis Cursos")
        print("0. Cerrar Sesión")
        choice = input("Seleccione una opción: ")
        if choice == '1':
            mis_cursos = listar_mis_cursos()
            if mis_cursos:
                try:
                    course_id_selection_str = input("Ingrese el ID del curso para ver detalles (o 0 para volver): ")
                    if course_id_selection_str == '0':
                        continue
                    course_id_selection = int(course_id_selection_str)
                    selected_course = next((c for c in mis_cursos if c['id_curso'] == course_id_selection), None)
                    if selected_course:
                        ingresar_menu_curso(selected_course['id_curso'], selected_course['nombre'])
                    else:
                        print("ID de curso no válido.")
                except ValueError:
                    print("Entrada no válida.")
                pausar_pantalla()
        elif choice == '0':
            cerrar_sesion()
            break
        else:
            print("Opción no válida.")
            pausar_pantalla()

# Función principal que inicia la aplicación y controla el flujo general.
def main():
    global CURRENT_USER
    print("Intentando conectar a la base de datos (usando configuración predefinida)...")
    conn_test = obtener_conexion_db()
    if not conn_test:
        print("\nNo se pudo conectar a la base de datos con la configuración predefinida.")
        print(f"Verifique que DB_CONFIG en el script sea correcta (usuario: '{DB_CONFIG['user']}') y que su servidor MySQL esté en ejecución y accesible.")
        print(f"Base de datos esperada: '{DB_CONFIG['database']}'. Asegúrese de haberla creado y ejecutado los scripts DDL y DML.")
        return
    conn_test.close()
    print("Conexión a la base de datos exitosa.")
    pausar_pantalla()
    while True:
        if not CURRENT_USER or not CURRENT_USER.get('id_usuario'):
            if not iniciar_sesion():
                retry = input("¿Intentar de nuevo (s/n)? ")
                if retry.lower() != 's':
                    break
                continue
            pausar_pantalla()
        if not CURRENT_USER or not CURRENT_USER.get('rol'):
            print("Error de usuario. Saliendo.")
            break
        user_role = CURRENT_USER.get('rol')
        if user_role == 'Administrador':
            menu_administrador()
        elif user_role == 'Profesor':
            menu_profesor()
        elif user_role == 'Estudiante':
            menu_estudiante()
        else:
            print(f"Rol de usuario desconocido: {user_role}. Cerrando sesión.")
            cerrar_sesion()
        if not CURRENT_USER or not CURRENT_USER.get('id_usuario'):
            pass
    print("\nGracias por usar la aplicación NODO. ¡Hasta pronto!")

if __name__ == "__main__":
    main()