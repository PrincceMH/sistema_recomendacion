# Configuración para desarrollo
import os

class DevelopmentConfig:
    # Configuración de Flask
    DEBUG = True
    SECRET_KEY = 'dev-secret-key-change-in-production'
    
    # Configuración de datos
    DATA_PATH = "/mnt/datasets/ml-32m/ratings.csv"
    MOVIES_PATH = "/mnt/datasets/ml-32m/movies.csv"
    
    # Si los archivos principales no están disponibles, usar estos paths alternativos
    FALLBACK_DATA_PATH = "data/sample_ratings.csv"
    FALLBACK_MOVIES_PATH = "data/sample_movies.csv"
    
    # Configuración de muestreo para desarrollo (usar menos datos)
    USE_SAMPLE_DATA = True
    SAMPLE_FRACTION = 0.05  # Usar solo 5% de los datos
    
    # Configuración de CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:5000",
        "http://127.0.0.1:5000"
    ]
    
    # Configuración del servidor
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Configuración de logging
    LOG_LEVEL = 'DEBUG'

class ProductionConfig:
    # Configuración para producción
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key'
    
    # Usar datos completos en producción
    USE_SAMPLE_DATA = False
    SAMPLE_FRACTION = 1.0
    
    # Configuración más restrictiva de CORS
    CORS_ORIGINS = [
        "https://tu-dominio.com"
    ]
    
    # Configuración del servidor
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    
    LOG_LEVEL = 'INFO'

# Determinar qué configuración usar
config = DevelopmentConfig if os.environ.get('FLASK_ENV') != 'production' else ProductionConfig