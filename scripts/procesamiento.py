from pathlib import Path
import pandas as pd
import psycopg 

# =========================
# Lectura del dataset 
# =========================

csv_file = Path(__file__).resolve().parent.parent / "data" / "dataset.csv"

df = pd.read_csv(csv_file, sep=";")

print("Dataset original")
print(df)

# =========================
# Limpieza de datos
# =========================

# Eliminación de duplicados
df = df.drop_duplicates()

# Reemplazo de valores nulos
df = df.fillna(0)

print("Dataset limpio")
print(df)

# =========================
# Exportación de dataset limpio
# =========================

# 1. Creamos un objeto Path con la ruta de destino
output_file = Path("output/dataset_limpio.csv")

# 2. Creamos la carpeta 'output' si no existe (parents=True permite crear subcarpetas)
output_file.parent.mkdir(parents=True, exist_ok=True)

# 3. Crea una fila del encabezado
df.columns = df.columns.str.strip().str.lower()

# 4. Crea el archivo de salida
df.to_csv(output_file, sep=",", index=False)

print("Archivo exportado correctamente")

# =========================
# Conexión PostgreSQL
# =========================

conn = psycopg.connect(
    host="localhost",
    port="5433",    
    dbname="laboratorio",
    user="postgres",
    password="12345678"
)
cursor = conn.cursor()

print("Conexión PostgreSQL exitosa")

# =========================
# Creación de tabla
# =========================

cursor.execute("""

CREATE TABLE IF NOT EXISTS clientes (
    id INT,
    nombre VARCHAR(50),
    edad INT,
    ciudad VARCHAR(50)
)

""")

conn.commit()

print("Tabla creada correctamente")

# =========================
# Inserción de registros
# =========================

cursor.execute("DELETE FROM clientes") 
conn.commit()

for index, row in df.iterrows():
    # Manejo seguro de Edad (si es nulo, envía None a PostgreSQL)
    edad_val = None if pd.isna(row['edad']) else int(float(row['edad']))
    id_val = None if pd.isna(row['id']) else int(float(row['id']))

    cursor.execute(
        """
        INSERT INTO clientes (id,nombre,edad,ciudad)
        VALUES (%s, %s, %s, %s)
        """,
        (
            id_val,
            row['nombre'],
            edad_val,
            row['ciudad']
        )
    )
conn.commit()

print("Datos insertados correctamente")

# =========================
# Validación final
# =========================

cursor.execute("SELECT * FROM clientes")

resultado = cursor.fetchall()
print(f"Total registros: {len(resultado)}")

print("Datos almacenados en PostgreSQL")

for fila in resultado:
    print(fila)

# =========================
# Cierre de conexión
# =========================

cursor.close()
conn.close()

print("Proceso finalizado correctamente")
