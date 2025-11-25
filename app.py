# app.py - Motor de IA de la Web App

from flask import Flask, jsonify
from flask_cors import CORS
import random
import os

# --- PARÁMETROS ESTADÍSTICOS GLOBALES ---
# Basado en el análisis de 8119 sorteos históricos
SUM_RANGE_MIN = 118
SUM_RANGE_MAX = 184
MEDIA_SUMA = 150.71
HOT_NUMBERS = [43, 26, 41, 6, 37] 
COLD_NUMBERS = [48, 30, 4, 7, 47]
ALL_NUMBERS = set(range(1, 49)) # Del 1 al 49
NEUTRAL_NUMBERS = list(ALL_NUMBERS - set(HOT_NUMBERS) - set(COLD_NUMBERS))


# 1. Configuración del Servidor Web
app = Flask(__name__)
# Permitir que el Frontend (Netlify) se comunique con este Backend (Render)
CORS(app) 

# Ajuste para Render: Fuerza el ambiente de producción y seguridad
app.config['ENV'] = 'production' 


# --- 2. Lógica del Motor de IA ---
def generar_combinaciones_inteligente(cantidad=5):
    """Genera combinaciones que cumplen con las reglas de suma y racha."""
    combinaciones = []
    
    for _ in range(cantidad): 
        while True:
            # Estrategia: 2 Hot, 2 Cold, 2 Neutral
            try:
                hot_selection = random.sample(HOT_NUMBERS, 2)
                cold_selection = random.sample(COLD_NUMBERS, 2)
                neutral_selection = random.sample(NEUTRAL_NUMBERS, 2)
            except ValueError:
                # Si una lista se vacía (improbable), reinicia
                continue 
            
            combination = sorted(list(set(hot_selection + cold_selection + neutral_selection)))
            current_sum = sum(combination)
            
            # Validación de la Regla de Suma (118 a 184)
            if SUM_RANGE_MIN <= current_sum <= SUM_RANGE_MAX:
                # Calcula la puntuación heurística basada en la cercanía a la media
                score = int(100 - (abs(current_sum - MEDIA_SUMA) / 33.02) * 10)
                
                combinaciones.append({
                    "combinacion": combination,
                    "suma": current_sum,
                    "calidad_score": max(70, score),
                    "composicion": f"2H {hot_selection} / 2C {cold_selection} / 2N {neutral_selection}"
                })
                break
    return combinaciones

# 3. ENDPOINTS DE LA API (Puntos de Acceso)

@app.route('/api/generar_ia', methods=['GET'])
def ia_endpoint():
    """ENDPOINT PREMIUM: Devuelve 5 combinaciones optimizadas."""
    # Aquí iría la lógica de verificación de la suscripción antes de devolver los datos.
    data = generar_combinaciones_inteligente(cantidad=5)
    return jsonify({
        "status": "success",
        "message": "Combinaciones generadas por Motor IA.",
        "data": data
    })

@app.route('/', methods=['GET'])
def home():
    """ENDPOINT RAÍZ: Para que Render sepa que el servidor está activo."""
    return "Motor de IA de AzarPredictor Activo."
