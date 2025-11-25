# app.py - Motor de IA de la Web App

from flask import Flask, jsonify
from flask_cors import CORS
import random

# --- PARÁMETROS ESTADÍSTICOS (Extraídos de tu análisis) ---
SUM_RANGE_MIN = 118
SUM_RANGE_MAX = 184
MEDIA_SUMA = 150.71
HOT_NUMBERS = [43, 26, 41, 6, 37] 
COLD_NUMBERS = [48, 30, 4, 7, 47]
ALL_NUMBERS = set(range(1, 50))
NEUTRAL_NUMBERS = list(ALL_NUMBERS - set(HOT_NUMBERS) - set(COLD_NUMBERS))

# 1. Configuración del Servidor Web
# app = Flask(__name__) # app.py - Ajuste del Puerto

from flask import Flask, jsonify
from flask_cors import CORS
# ... (otras importaciones)

app = Flask(__name__)
# CORS permite que tu página web (Frontend) se comunique con este servidor
CORS(app) 

# --- AÑADE ESTA LÍNEA AQUÍ ---
app.config['ENV'] = 'production'
# --- FIN DEL CÓDIGO A AÑADIR ---

# ... (resto de tu lógica de IA)
# CORS permite que tu página web (Frontend) se comunique con este servidor
CORS(app) 

# --- 2. Lógica de la Función IA ---
def generar_combinacion_inteligente(cantidad=5):
    """Genera combinaciones que cumplen con las reglas de suma y racha."""
    combinaciones = []
    
    for _ in range(cantidad): # Generaremos la cantidad solicitada (por defecto 5)
        while True:
            # Selecciona 2 Hot, 2 Cold, 2 Neutral para el balance
            try:
                hot_selection = random.sample(HOT_NUMBERS, 2)
                cold_selection = random.sample(COLD_NUMBERS, 2)
                neutral_selection = random.sample(NEUTRAL_NUMBERS, 2)
            except ValueError:
                break # Sale si hay un error en la selección
            
            # Combina y verifica la suma
            combination = sorted(list(set(hot_selection + cold_selection + neutral_selection)))
            current_sum = sum(combination)
            
            if SUM_RANGE_MIN <= current_sum <= SUM_RANGE_MAX:
                # Si cumple la regla, añade la combinación
                combinaciones.append({
                    "combinacion": combination,
                    "suma": current_sum,
                    "calidad_score": random.randint(75, 95) # Simulación de la puntuación
                })
                break
    return combinaciones

# 3. Definición del Punto de Acceso (Endpoint) para la IA
@app.route('/api/generar_ia', methods=['GET'])
def ia_endpoint():
    """Endpoint Premium: Devuelve 5 combinaciones generadas por la IA."""
    
    # NOTA: En la realidad, aquí se verifica si el usuario pagó la suscripción.
    
    data = generar_combinaciones_inteligente(cantidad=5)
    
    return jsonify({
        "status": "success",
        "message": "Combinaciones generadas por Motor IA.",
        "data": data
    })

# 4. Iniciar el Servidor (Solo para pruebas locales)
if __name__ == '__main__':
    # El puerto 5000 es el estándar de Flask

    app.run(debug=True, port=5000)
