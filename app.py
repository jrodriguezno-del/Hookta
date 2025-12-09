from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from config.db import get_db_connection
import json

app = Flask(__name__)
app.secret_key = "hootka_secret_key"

preguntas = []

@app.route('/')
def home():
    if 'usuario' in session:
        return redirect(url_for('crear_pregunta'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE usuario=%s AND password=%s", (usuario, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session['usuario'] = usuario
                return redirect(url_for('crear_pregunta'))
            else:
                return render_template('login.html', error="Credenciales inválidas")
        else:
            return render_template('login.html', error="No se pudo conectar a la base de datos")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        confirmar = request.form['confirmar']

        if not usuario or not password or not confirmar:
            return render_template('register.html', error="Todos los campos son obligatorios")
        if password != confirmar:
            return render_template('register.html', error="Las contraseñas no coinciden")

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
            existente = cursor.fetchone()
            if existente:
                cursor.close()
                conn.close()
                return render_template('register.html', error="El usuario ya existe")

            cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (%s, %s)", (usuario, password))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('register.html', mensaje="✅ Usuario creado con éxito. Ahora puedes iniciar sesión.")
        else:
            return render_template('register.html', error="No se pudo conectar a la base de datos")

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/crear_pregunta', methods=['GET', 'POST'])
def crear_pregunta():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        pregunta = request.form['pregunta']
        opciones = [
            request.form['opcion1'],
            request.form['opcion2'],
            request.form['opcion3'],
            request.form['opcion4'],
        ]
        correcta = request.form['correcta']

        preguntas.append({
            "pregunta": pregunta,
            "opciones": opciones,
            "correcta": correcta
        })

        return render_template('crear_pregunta.html', mensaje="✅ Pregunta guardada!", preguntas=preguntas)

    return render_template('crear_pregunta.html', preguntas=preguntas)

@app.route('/vaciar', methods=['POST'])
def vaciar_preguntas():
    global preguntas
    preguntas.clear()
    return redirect(url_for('crear_pregunta'))

@app.route('/guardarEncuesta', methods=['POST'])
def guardarEncuesta():
    if 'usuario' not in session:
        return jsonify({"status": "error", "message": "No has iniciado sesión"}), 403

    try:
        data = request.form
        titulo = data.get('titulo')
        preguntas_json = data.get('preguntas')

        if not titulo or not preguntas_json:
            return jsonify({"status": "error", "message": "Datos incompletos"}), 400

        preguntas_data = json.loads(preguntas_json)

        conn = get_db_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Error de conexión a la base de datos"}), 500

        cursor = conn.cursor()

        # 🔹 Obtener ID del usuario actual
        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (session['usuario'],))
        usuario_row = cursor.fetchone()
        if not usuario_row:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

        usuario_id = usuario_row[0]

        # 🔹 Insertar el cuestionario
        cursor.execute("""
            INSERT INTO cuestionarios (usuario_id, titulo)
            VALUES (%s, %s)
        """, (usuario_id, titulo))
        cuestionario_id = cursor.lastrowid

        # 🔹 Insertar preguntas y respuestas
        for p in preguntas_data:
            tipo_pregunta = p.get('tipo_pregunta')
            tipo_respuesta = p.get('tipo_respuesta')
            pregunta_texto = p.get('pregunta')

            # ✅ Nuevo manejo de imagen
            imagen = None
            if p.get('imagenBase64'):  # Si llega en base64 desde el front
                imagen = p['imagenBase64']  # Se guarda directamente en DB
            elif p.get('imagen'):  # Si solo llegó el nombre del archivo
                imagen = p['imagen']

            cursor.execute("""
                INSERT INTO preguntas (cuestionario_id, tipo_pregunta, tipo_respuesta, pregunta, imagen)
                VALUES (%s, %s, %s, %s, %s)
            """, (cuestionario_id, tipo_pregunta, tipo_respuesta, pregunta_texto, imagen))
            pregunta_id = cursor.lastrowid

            # 🔸 Si la pregunta tiene opciones
            if tipo_respuesta in ['unica', 'multiple']:
                opciones = p.get('opciones', [])
                correctas = p.get('correctas', [])

                for i, texto_opcion in enumerate(opciones, start=1):
                    es_correcta = i in correctas
                    cursor.execute("""
                        INSERT INTO respuestas (pregunta_id, texto, es_correcta)
                        VALUES (%s, %s, %s)
                    """, (pregunta_id, texto_opcion, es_correcta))

            # 🔸 Si es abierta, insertar sin respuestas
            elif tipo_respuesta == 'abierta':
                cursor.execute("""
                    INSERT INTO respuestas (pregunta_id, texto, es_correcta)
                    VALUES (%s, %s, %s)
                """, (pregunta_id, None, None))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "✅ Cuestionario guardado correctamente",
            "cuestionario_id": cuestionario_id
        }), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == "__main__":
    app.run(port=5000, debug=True)
