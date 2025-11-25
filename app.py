# app.py - MOTOR DE IA CON GESTIÓN DE CRÉDITOS Y NIVELES (FINAL)

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import sqlite3
from datetime import datetime
import os

# --- CONFIGURACIÓN DE LA BASE DE DATOS Y LÍMITES ---
DATABASE = 'users.db'
BRONZE_CREDIT_LIMIT = 150
COST_PER_PRONO = 50
DAILY_PRONO_LIMIT = 2

# --- PARÁMETROS ESTADÍSTICOS GLOBALES ---
SUM_RANGE_MIN = 118
SUM_RANGE_MAX = 184
MEDIA_SUMA = 150.71
HOT_NUMBERS = [43, 26, 41, 6, 37] 
COLD_NUMBERS = [48, 30, 4, 7, 47]
ALL_NUMBERS = set(range(1, 49))
NEUTRAL_NUMBERS = list(ALL_NUMBERS - set(HOT_NUMBERS) - set(COLD_NUMBERS))


# 1. Configuración del Servidor Web
app = Flask(__name__)
CORS(app) 
app.config['ENV'] = 'production' 


# --- FUNCIONES DE LA BASE DE DATOS ---

def get_db_connection():
    """Conexión a la base de datos."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la tabla de usuarios."""
    with app.app_context():
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                nivel_suscripcion TEXT NOT NULL,
                creditos_disponibles INTEGER NOT NULL,
                prono_usados_hoy INTEGER NOT NULL,
                ultima_interaccion TEXT
            );
        ''')
        # SIMULACIÓN: Usuario de prueba Nivel BRONCE (si no existe)
        cursor = conn.execute("SELECT * FROM users WHERE user_id = 'test_user'")
        if cursor.fetchone() is None:
             conn.execute("INSERT INTO users (user_id, nivel_suscripcion, creditos_disponibles, prono_usados_hoy, ultima_interaccion) VALUES (?, ?, ?, ?, ?)",
                         ('test_user', 'BRONCE', BRONZE_CREDIT_LIMIT, 0, datetime.now().strftime('%Y-%m-%d')))
        
        conn.commit()
        conn.close()

# Inicializa la DB al arrancar el servidor
init_db()


# --- 2. Lógica del Motor de IA (Genera las combinaciones) ---

def generar_combinaciones_inteligente(cantidad=5):
    """Genera N combinaciones optimizadas."""
    # (Mantenemos la lógica de generación que ya funciona)
    combinaciones = []
    
    for _ in range(cantidad): 
        while True:
            try:
                hot_selection = random.sample(HOT_NUMBERS, 2)
                cold_selection = random.sample(COLD_NUMBERS, 2)
                neutral_selection = random.sample(NEUTRAL_NUMBERS, 2)
            except ValueError:
                break 
            
            combination = sorted(list(set(hot_selection + cold_selection + neutral_selection)))
            current_sum = sum(combination)
            
            if SUM_RANGE_MIN <= current_sum <= SUM_RANGE_MAX:
                score = int(100 - (abs(current_sum - MEDIA_SUMA) / 33.02) * 10)
                
                combinaciones.append({
                    "combinacion": combination,
                    "suma": current_sum,
                    "calidad_score": max(70, score),
                    "composicion": f"2H {hot_selection} / 2C {cold_selection} / 2N {neutral_selection}"
                })
                break
    return combinaciones


# --- 3. ENDPOINTS DE LA API (Puntos de Acceso) ---

# ENDPOINT PRINCIPAL: Genera la IA (Requiere user_id en la URL: ?user_id=X)
@app.route('/api/generar_ia', methods=['GET'])
def ia_endpoint():
    # El Frontend debe enviar el ID del usuario
    user_id = request.args.get('user_id', 'test_user') 
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    
    if not user:
        conn.close()
        return jsonify({"status": "error", "message": "Por favor, regístrese primero."}), 404

    # --- LÓGICA DE CRÉDITOS BRONCE ---
    if user['nivel_suscripcion'] == 'BRONCE':
        
        # Reiniciar contadores diarios si es un nuevo día
        today = datetime.now().strftime('%Y-%m-%d')
        if user['ultima_interaccion'] != today:
            conn.execute("UPDATE users SET prono_usados_hoy = 0, ultima_interaccion = ? WHERE user_id = ?", (today, user_id))
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone() 
        
        
        if user['prono_usados_hoy'] >= DAILY_PRONO_LIMIT:
            conn.close()
            return jsonify({"status": "limit", "message": "Límite diario (2 pronósticos) alcanzado. Vuelve mañana."}), 403

        if user['creditos_disponibles'] < COST_PER_PRONO:
            conn.close()
            return jsonify({"status": "no_credits", "message": f"Créditos insuficientes ({user['creditos_disponibles']}/{COST_PER_PRONO})."}), 403

        # Descontar créditos y registrar uso
        new_credits = user['creditos_disponibles'] - COST_PER_PRONO
        new_uses = user['prono_usados_hoy'] + 1
        
        conn.execute("UPDATE users SET creditos_disponibles = ?, prono_usados_hoy = ?, ultima_interaccion = ? WHERE user_id = ?", 
                     (new_credits, new_uses, today, user_id))
        conn.commit()
        
        pronos = generar_combinaciones_inteligente(cantidad=1) # Bronce solo 1 pronóstico

        conn.close()
        return jsonify({
            "status": "success", 
            "message": f"Pronóstico Bronce generado. Créditos restantes: {new_credits}", 
            "data": pronos,
            "creditos_restantes": new_credits
        })
    
    
    # --- LÓGICA DE NIVELES DE PAGO (Plata, Oro, Premium) ---
    else:
        # Asignar la cantidad de pronósticos según el nivel
        cantidad = 5 # Plata
        if user['nivel_suscripcion'] == 'ORO':
            cantidad = 10 
        elif user['nivel_suscripcion'] == 'PREMIUM':
            cantidad = 20 # Premium tiene el máximo

        pronos = generar_combinaciones_inteligente(cantidad=cantidad)
        conn.close()
        return jsonify({
            "status": "success", 
            "message": f"Pronóstico Ilimitado nivel {user['nivel_suscripcion']} generado.", 
            "data": pronos
        })


# ENDPOINT para obtener el estado del usuario (Útil para la web)
@app.route('/api/user_status', methods=['GET'])
def user_status():
    user_id = request.args.get('user_id', 'test_user')
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "user_id": user['user_id'],
            "nivel": user['nivel_suscripcion'],
            "creditos": user['creditos_disponibles'],
            "usos_hoy": user['prono_usados_hoy'],
            "max_usos": DAILY_PRONO_LIMIT
        })
    return jsonify({"status": "error", "message": "Usuario no encontrado."}), 404


@app.route('/', methods=['GET'])
def home():
    """ENDPOINT RAÍZ: Para que Render sepa que el servidor está activo."""
    return "Motor de IA de AzarPredictor Activo."
