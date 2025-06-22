from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/tecnica', methods=['POST'])
def mi_funcion():
    data = request.json
    nombre = data.get('nombre', 'persona misteriosa')
    return jsonify({'respuesta': f'¡Olé tú, {nombre}!'})

if __name__ == '__main__':
    app.run()
