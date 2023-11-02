from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tecsup'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/api/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')

        if not email:
            return jsonify({'error': 'Faltan datos obligatorios'}), 400

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            return jsonify({'user_id': user['id']}), 200

    return jsonify({'error': 'Credenciales inválidas'}), 401
    

@app.route('/api/usuarios', methods=['POST'])
def agregar_usuario():
    if request.method == 'POST':
        # Obtener los datos del nuevo usuario desde la solicitud
        nombre = request.json.get('nombre')
        apellidos = request.json.get('apellidos')
        email = request.json.get('email')
        password = request.json.get('password')
        telefono = request.json.get('telefono')

        # Validar que los campos requeridos no estén vacíos
        if not nombre or not apellidos or not email or not password:
            return jsonify({'error': 'Faltan datos obligatorios'}), 400

        try:
            # Insertar el nuevo usuario en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (nombre, apellidos, email, password, telefono) VALUES (%s, %s, %s, %s, %s)",
                        (nombre, apellidos, email, bcrypt.generate_password_hash(password).decode('utf-8'), telefono))
            mysql.connection.commit()
            cur.close()
            return jsonify({'message': 'Usuario agregado correctamente'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Ruta para obtener todos los usuarios (Listar)
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    return jsonify(usuarios)

# Ruta para eliminar un usuario por su ID
@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Usuario eliminado'})


if __name__ == '__main__':
    app.run(debug=True)
