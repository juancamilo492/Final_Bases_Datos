# README.md

# Info de la materia: SI2003-251, Bases de Datos, Universidad EAFIT
**Estudiante(s):**  
Juan Camilo Bolaños García, jcbolanosg@eafit.edu.co

**Profesor:**  
Edwin Nelson Montoya Munera, emontoya@eafit.edu.co


# Sistema de Gestión Académica NODO

## 1. Breve descripción de la actividad
El proyecto "Sistema de Gestión Académica NODO" es una aplicación diseñada para gestionar cursos, usuarios, tareas, foros y materiales en un entorno universitario. Utiliza una base de datos MySQL para almacenar la información y una interfaz en consola desarrollada en Python que permite a administradores, profesores y estudiantes interactuar con el sistema. El objetivo es facilitar la administración de cursos, la entrega de tareas, la participación en foros y la generación de reportes para el semestre actual (2025-1).

### 1.1. Aspectos cumplidos o desarrollados de la actividad propuesta por el profesor
- **Base de datos**: Implementada en MySQL con el archivo `proyecto_ddl.sql`, que crea la base de datos `NODO` y las tablas con integridad referencial (Usuarios, Curso, Tarea, Tarea_Entrega, Foro, Mensaje, Material, Pagos, interes_curso).
- **Consultas SQL**: Implementadas todas las consultas solicitadas en `proyecto_query.sql`, incluyendo:
  - Listado de estudiantes por año y semestre.
  - Estudiantes de un curso específico.
  - Cursos de un estudiante en un rango de fechas.
  - Profesores y sus cursos asignados.
  - Cursos por categoría y rango de precio.
  - Usuarios no matriculados en un año/semestre.
  - Tareas y materiales de un curso.
  - Mensajes de un foro.
  - Consulta adicional: estadísticas de matriculación por curso.
- **Aplicación CRUD**: Desarrollada en Python (`App_Final.py`) con las siguientes funcionalidades:
  - **Login/Logout**: Autenticación de usuarios con email y contraseña.
  - **Administrador**: Matricular usuarios, asignar profesores, acceder a funciones de profesor/estudiante, y reportes (listar cursos, información de curso, listar usuarios).
  - **Profesor**: Listar cursos, gestionar alumnos, materiales, foros, tareas (subir materiales, crear foros, calificar tareas).
  - **Estudiante**: Listar cursos, ver materiales, participar en foros, entregar/ver calificaciones de tareas.
- **Requerimientos no funcionales**: 
  - Uso de consultas parametrizadas para prevenir inyección SQL.
  - Manejo de errores en la conexión a la base de datos y ejecución de consultas.
  - Interfaz de consola clara con menús de navegación.

### 1.2. Aspectos NO cumplidos o desarrollados
- **Interfaz gráfica**: La aplicación se desarrolló en modo consola, como se recomendó, pero no incluye una interfaz gráfica, lo que podría ser una limitación para usuarios menos técnicos.

# 2. Información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas
- **Arquitectura**: Cliente-servidor con una base de datos relacional MySQL como backend y una aplicación en Python como frontend (interfaz en consola). La base de datos maneja toda la lógica de almacenamiento, mientras que la aplicación gestiona la interacción con el usuario y las consultas.
- **Patrones de diseño**: 
  - **Modularización**: El código Python está organizado en funciones específicas para cada tarea (autenticación, menús, consultas, actualizaciones), siguiendo el principio de responsabilidad única.
  - **Capas**: Separación de responsabilidades entre la lógica de presentación (menús en consola), la lógica de negocio (funciones de consulta/actualización) y el acceso a datos (consultas SQL).
- **Mejores prácticas**:
  - Uso de consultas parametrizadas en `mysql-connector-python` para evitar inyección SQL.
  - Manejo de excepciones para errores de conexión a la base de datos y ejecución de consultas.
  - Transacciones gestionadas con `commit` y `rollback` para operaciones de actualización.
  - Formato tabular claro para mostrar resultados usando la función `mostrar_tabla`.
  - Código comentado para mejorar la legibilidad y mantenimiento.
  - Validación de entradas del usuario (por ejemplo, IDs numéricos, fechas en formato correcto).

# 3. Descripción del ambiente de desarrollo y técnico
- **Lenguaje de programación**: Python 3.9 o superior.
- **Base de datos**: MySQL 8.0.
- **Librerías y paquetes**:
  - `mysql-connector-python==8.0.33` para la conexión con MySQL.
  - Módulos estándar de Python: `os`, `datetime`, `decimal`.
- **Cómo se compila y ejecuta**:
  1. Asegúrate de tener MySQL instalado y en ejecución.
  2. Crea la base de datos ejecutando `proyecto_ddl.sql` en MySQL.
  3. Pobla la base de datos ejecutando `proyecto_dml.sql`.
  4. Instala la librería `mysql-connector-python`:
     ```bash
     pip install mysql-connector-python==8.0.33
     ```
  5. Configura las credenciales de la base de datos en `App_Final.py` (variable `DB_CONFIG`).
  6. Ejecuta la aplicación:
     ```bash
     python App_Final.py
     ```
- **Detalles del desarrollo**:
  - Desarrollado en un entorno local usando un Visual Studio Code y MySQL Workbench.
  - Se utilizó un entorno virtual de Python para gestionar dependencias.
  - Las consultas SQL fueron probadas en MySQL Workbench antes de integrarlas en la aplicación.
- **Detalles técnicos**:
  - La base de datos `NODO` utiliza claves primarias, foráneas y restricciones de integridad (como CHECK para puntajes y roles).
  - La aplicación maneja conexiones dinámicas a la base de datos, cerrándolas después de cada operación para evitar fugas de recursos.
- **Configuración de parámetros**:
  - Edita la variable `DB_CONFIG` en `App_Final.py` para configurar:
    ```python
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'bruno123',  # Reemplazar con la contraseña real
        'database': 'NODO'
    }
    ```
  - No se utilizan variables de entorno en esta versión, pero podrían añadirse para mayor seguridad.
- **Estructura de directorios**:
  ```
  proyecto/
  ├── App_Final.py           # Aplicación principal en Python
  ├── proyecto_ddl.sql       # Script de creación de la base de datos
  ├── proyecto_dml.sql       # Script de población de datos
  ├── proyecto_query.sql     # Consultas SQL solicitadas
  ```
  *Nota: Ejecuta `tree` en Linux para obtener esta estructura si es necesario.*

# 4. Descripción del ambiente de ejecución (en producción)
- **Ambiente de ejecución**: Similar al de desarrollo (MySQL 8.0 y Python 3.9 en un servidor local o en la nube). En producción, se recomienda un servidor MySQL dedicado y un entorno Python con dependencias instaladas.
- **Lenguaje y librerías**: Igual que en desarrollo (`mysql-connector-python==8.0.33`, Python estándar).
- **IP o nombres de dominio**:
  - En un entorno local: `localhost` (puerto predeterminado de MySQL: 3306).
  - En producción: Configura la IP o dominio del servidor MySQL en `DB_CONFIG['host']`.
- **Configuración de parámetros**:
  - Configura `DB_CONFIG` en `App_Final.py` con las credenciales del servidor MySQL.
  - Asegúrate de que el servidor MySQL permita conexiones remotas si no está en la misma máquina.
  - Opcionalmente, usa variables de entorno para las credenciales:
    ```bash
    export DB_HOST='servidor.ejemplo.com'
    export DB_USER='usuario'
    export DB_PASSWORD='contraseña'
    export DB_NAME='NODO'
    ```
  - Configura el puerto si no es el predeterminado (3306).
- **Cómo se lanza el servidor**:
  1. Asegúrate de que el servidor MySQL esté en ejecución.
  2. Copia los archivos del proyecto al servidor.
  3. Instala dependencias: `pip install mysql-connector-python==8.0.33`.
  4. Ejecuta: `python App_Final.py`.
- **Mini guía para el usuario**:
  1. **Inicio de sesión**: Ingresa tu email y contraseña. Ejemplo:
      - **Estudiante**: Ana María Gómez, `ana.gomez@eafit.edu.co`. Inscrita en el curso "Matemáticas I" (ID_CURSO: 1) para el semestre 2025-1. Puede listar sus cursos, consultar materiales, entregar tareas y participar en foros.
      - **Profesor**: Carlos Andrés López, `carlos.lopez@eafit.edu.co`. Asignado como profesor del curso "Matemáticas I" (ID_CURSO: 1) para el semestre 2025-1. Puede gestionar materiales, crear foros, calificar tareas y listar alumnos.
      - **Administrador**: Carlos Andrés López, `carlos.lopez@eafit.edu.co`. Asignado como profesor del curso "Matemáticas I" (ID_CURSO: 1) para el semestre 2025-1. Puede gestionar materiales, crear foros, calificar tareas y listar alumnos.
  2. **Administrador**:
     - Matricula estudiantes seleccionando su ID y el ID del curso.
     - Asigna profesores a cursos.
     - Genera reportes (cursos, usuarios, detalles de un curso).
     - Simula roles de profesor/estudiante.
  3. **Profesor**:
     - Lista tus cursos (por ejemplo, "Matemáticas I") y selecciona uno.
     - Sube materiales (título, descripción, URL ficticia).
     - Crea foros y califica tareas.
     - Participa en foros enviando mensajes o respuestas.
  4. **Estudiante**:
     - Lista tus cursos (por ejemplo, "Matemáticas I") y selecciona uno.
     - Consulta materiales y tareas.
     - Entrega tareas (nombre y formato de archivo simulados).
     - Participa en foros enviando mensajes o respuestas.
  5. **Cerrar sesión**: Selecciona la opción 0 en cualquier menú principal.

# 5. Otra información relevante
- **Desafíos enfrentados**:
  - Implementar una interfaz en consola que fuera clara y fácil de usar para todos los roles.
  - Gestionar la integridad referencial en la base de datos, especialmente en tablas con claves compuestas (como Tarea, Foro, Tarea_Entrega).
  - Validar entradas de usuario para evitar errores (por ejemplo, IDs no numéricos o fechas inválidas).
- **Limitaciones conocidas**:
  - La aplicación no maneja la carga física de archivos; solo simula la subida con nombres/URLs.
  - No hay autenticación segura (las contraseñas están en texto plano en la base de datos).
  - Algunas consultas podrían optimizarse con índices para bases de datos grandes.
- **Funcionalidades adicionales**:
  - Consulta adicional en `proyecto_query.sql` para estadísticas de matriculación por curso.
  - Interfaz tabular para mostrar datos de forma clara en la consola.
  - Validación de entregas previas de tareas para evitar duplicados innecesarios.

# Referencias
- Documentación oficial de MySQL: https://dev.mysql.com/doc/
- Documentación de `mysql-connector-python`: https://dev.mysql.com/doc/connector-python/en/
- Tutorial de Python y MySQL en Real Python: https://realpython.com/python-mysql/
- Guía de mejores prácticas para consultas SQL seguras: https://www.sqlshack.com/how-to-prevent-sql-injection-in-mysql/
- Documentación de Python sobre manejo de excepciones: https://docs.python.org/3/tutorial/errors.html
- Stack Overflow (consultas específicas sobre `mysql-connector-python`): https://stackoverflow.com/questions/tagged/mysql-connector-python
