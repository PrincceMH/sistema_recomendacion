#!/usr/bin/env python3
"""
Script para iniciar el servidor web del Sistema de Recomendación KNN
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    required_packages = ['flask', 'flask-cors', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dependencias faltantes:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Instala las dependencias con:")
        print("   pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_data_files():
    """Verificar que los archivos de datos existan"""
    data_paths = [
        "/mnt/datasets/ml-32m/ratings.csv",
        "/mnt/datasets/ml-32m/movies.csv"
    ]
    
    files_exist = all(Path(path).exists() for path in data_paths)
    
    if not files_exist:
        print("⚠️  Archivos de datos no encontrados en /mnt/datasets/ml-32m/")
        print("   El servidor usará datos de muestra para desarrollo")
    else:
        print("✅ Archivos de datos encontrados")
    
    return files_exist

def check_knn_modules():
    """Verificar que los módulos KNN estén disponibles"""
    try:
        from knn.load_data import cargar_rating_matrix
        from knn.knn import knn
        print("✅ Módulos KNN cargados correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error cargando módulos KNN: {e}")
        print("   Verifica que la carpeta 'knn' esté en el directorio del proyecto")
        return False

def create_sample_data():
    """Crear datos de muestra si no existen los originales"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Crear archivo de ratings de muestra
    sample_ratings = """userId,movieId,rating,timestamp
1,1,4.0,964982703
1,3,4.0,964981247
1,6,4.0,964982224
2,1,3.0,964982703
2,3,5.0,964981247
3,1,2.0,964982703
3,6,3.0,964982224"""
    
    # Crear archivo de películas de muestra
    sample_movies = """movieId,title,genres
1,Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy
2,Jumanji (1995),Adventure|Children|Fantasy
3,Grumpier Old Men (1995),Comedy|Romance
4,Waiting to Exhale (1995),Comedy|Drama|Romance
5,Father of the Bride Part II (1995),Comedy
6,Heat (1995),Action|Crime|Thriller"""
    
    ratings_file = data_dir / "sample_ratings.csv"
    movies_file = data_dir / "sample_movies.csv"
    
    if not ratings_file.exists():
        with open(ratings_file, 'w') as f:
            f.write(sample_ratings)
        print(f"✅ Creado {ratings_file}")
    
    if not movies_file.exists():
        with open(movies_file, 'w') as f:
            f.write(sample_movies)
        print(f"✅ Creado {movies_file}")

def start_server():
    """Iniciar el servidor Flask"""
    print("\n🚀 Iniciando Sistema de Recomendación KNN...")
    print("   Servidor: http://localhost:5000")
    print("   Interfaz Web: http://localhost:5000")
    print("\n💡 Presiona Ctrl+C para detener el servidor\n")
    
    try:
        # Ejecutar el servidor
        os.system("python app.py")
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
        sys.exit(0)

def main():
    """Función principal"""
    print("🎬 Sistema de Recomendación KNN - Iniciador")
    print("=" * 50)
    
    # Verificaciones previas
    if not check_dependencies():
        sys.exit(1)
    
    data_exists = check_data_files()
    
    if not check_knn_modules():
        sys.exit(1)
    
    # Crear datos de muestra si es necesario
    if not data_exists:
        create_sample_data()
    
    print("\n✅ Todas las verificaciones pasaron")
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main()