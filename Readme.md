# 🧩 Hootka — Creador de Preguntas tipo Kahoot

Hootka es una aplicación web hecha con **Flask (Python)** que permite:

- Iniciar sesión con usuarios almacenados en **MySQL**.
- Crear preguntas estilo **Kahoot** (4 opciones, una correcta).
- Visualizar las preguntas creadas.
- Vaciar la lista de preguntas con un botón.

El proyecto está pensado para ejecutarse **localmente** con **XAMPP** como servidor de base de datos.

---

## 📋 Requisitos previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

### 🐍 Python

- Versión recomendada: **3.10 o superior**
- Descarga desde: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Durante la instalación en Windows, **marca la opción** “Add Python to PATH”.

Verifica la instalación:

```bash
python --version
```

### 🧱 XAMPP (MySQL)

- Descarga desde: [https://www.apachefriends.org/es/index.html]
- Instala con los componentes:

  - ✅ Apache
  - ✅ MySQL

- Inicia ambos desde el Panel de Control de XAMPP (deben ponerse en verde).
- Apache → [http://localhost]
- MySQL/PHPMyAdmin → [http://localhost/phpmyadmin]

### ⚙️ Configuración de la base de datos

1. Entra a [http://localhost/phpmyadmin]
2. Crea una nueva base de datos llamada:

```sql
CREATE DATABASE hootka_db;
USE hootka_db;
```

3. Abre la pestaña SQL y ejecuta este script:

```sql
CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL
);
```

4. 📘 Tabla cuestionarios

Contiene los cuestionarios creados por los usuarios.

```sql
CREATE TABLE IF NOT EXISTS cuestionarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  titulo VARCHAR(255) NOT NULL,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

5. ❓ Tabla preguntas

Cada pregunta pertenece a un cuestionario.
Soporta distintos tipos de pregunta y tipos de respuesta (abierta, única o múltiple).

```sql
CREATE TABLE IF NOT EXISTS preguntas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  cuestionario_id INT NOT NULL,
  tipo_pregunta ENUM('texto', 'imagen', 'mixta') NOT NULL,
  tipo_respuesta ENUM('abierta', 'unica', 'multiple') NOT NULL,
  pregunta TEXT,
  imagen LONGTEXT,
  FOREIGN KEY (cuestionario_id) REFERENCES cuestionarios(id) ON DELETE CASCADE
);
```

6. 💬 Tabla respuestas

Contiene las posibles respuestas de cada pregunta.
El campo es_correcta indica si la respuesta es la correcta (1) o no (0).

```sql
CREATE TABLE IF NOT EXISTS respuestas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  pregunta_id INT NOT NULL,
  texto VARCHAR(255),
  es_correcta TINYINT(1) DEFAULT 0,
  FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE
);

INSERT INTO usuarios (usuario, password) VALUES
('admin', '1234'),
('daniel', '4321')
ON DUPLICATE KEY UPDATE password=VALUES(password);
```

### 🔐 Credenciales por defecto de MySQL (XAMPP):

- Host: localhost

- Usuario: root

- Contraseña: (vacía por defecto)

- Puerto: 3306

### 📁 Estructura del proyecto

```arduino
hootka/
├─ app.py
├─ config/
│  └─ db.py
├─ templates/
│  ├─ login.html
│  └─ register.html
│  └─ crear_pregunta.html
├─ static/
│  └─ style.css
├─ requirements.txt
└─ .env
```

### 📦 Instalación del proyecto

1. Abre una terminal en la carpeta donde guardarás el proyecto.

2. Clona o descarga el repositorio:

```bash
git clone https://github.com/danielfruizt-code/Hookta
cd hootka
```

(O simplemente copia todos los archivos en una carpeta local.)

3. Crea un entorno virtual:

```bash
python -m venv .venv
```

4. Activa el entorno virtual:

   - Windows:

   ```bash
    .venv\Scripts\activate
   ```

   - Linux / macOS:

   ```bash
    .source venv/bin/activate
   ```

5. Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

### 🚀 Ejecución del proyecto

1. Asegúrate de que MySQL esté corriendo en XAMPP.

2. Desde tu terminal (con el entorno virtual activo):

```bash
python app.py
```

3. Si todo está bien, deberías ver algo como:

```csharp
* Running on http://127.0.0.1:5000
* Press CTRL+C to quit
```

4. Abre en tu navegador:

   👉 http://127.0.0.1:5000

### 🌍 Verificar funcionamiento

1. Entra a [http://127.0.0.1:5000]

2. Inicia sesión con alguno de los usuarios.

3. Crea una pregunta tipo Kahoot (4 opciones, una correcta).

4. Verifica que la pregunta aparezca en el panel derecho.

5. Usa el botón "Vaciar Preguntas" para limpiar la lista.

6. Usa el botón "Cerrar sesión" para salir.
