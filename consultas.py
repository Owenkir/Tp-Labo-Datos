#%%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import duckdb as db
import numpy as np

## df1
#%%
df1 = pd.read_excel(r"TablasOriginales\2022_padron_oficial_establecimientos_educativos.xlsx",skiprows=6)

consultaSQL = """
            SELECT
            Cueanexo,
            "Jurisdicción" AS Provincia,
            CAST(SUBSTRING(CAST("Código de localidad" AS TEXT) FROM 1 FOR LENGTH(CAST("Código de localidad" AS TEXT)) - 3) AS INTEGER) AS id_departamento,
            Departamento AS departamento,
            "Nivel inicial - Jardín maternal" AS "Jardín maternal",
            "Nivel inicial - Jardín de infantes" AS "Jardín de infantes",
            Primario,
            Secundario,
            "Secundario - INET",
            FROM df1
            WHERE TRY_CAST(Común AS INT) = 1
            """
df1 = db.query(consultaSQL).df()

niveles = ["Jardín maternal",
            "Jardín de infantes",
            "Primario",
            "Secundario",
            "Secundario - INET",]

Tipos_Niveles = pd.DataFrame({
    "id": range(len(niveles)),
    "nivel": niveles
})

rows = []

for id, nivel in enumerate(niveles):
    df1[nivel] = pd.to_numeric(df1[nivel], errors='coerce')
    df = df1.loc[df1[nivel] == 1, ["Cueanexo"]].copy()
    df["id_nivel"] = id
    rows.append(df)

Niveles_EE = pd.concat(rows, ignore_index=True)

consultaSQL = """
            SELECT DISTINCT
            id_departamento,
            departamento,
            FROM df1
            """
Departamentos1 = db.query(consultaSQL).df()

consultaSQL = """
            SELECT
            Cueanexo, 
            id_departamento
            FROM df1;
            """
df1_3FN = db.query(consultaSQL).df()

Tipos_Niveles.to_csv("TablasModelo/Tipos_Niveles.csv", index = False)
Niveles_EE.to_csv("TablasModelo/Niveles_EE.csv", index = False)









## df2
#%%
df2 = pd.read_csv(r"TablasOriginales/actividades_establecimientos.csv")

consultaSQL = """
            SELECT DISTINCT clae6, CAST(SUBSTRING(CAST(clae6 AS TEXT), 3) AS INTEGER) AS clae3, clae6_desc AS Actividad
            FROM df2
            ORDER BY clae6;
            """
df2_3FN = db.query(consultaSQL).df()

df2_3FN.to_csv("TablasModelo/Actividades_Establecimientos.csv", index = False)










## df3
#%%
df3 = pd.read_csv(r"TablasOriginales/Datos_por_departamento_actividad_y_sexo.csv")

consultaSQL = """
            SELECT DISTINCT provincia_id AS id, provincia
            FROM df3
            ORDER BY id;
            """
Provincias = db.query(consultaSQL).df()

consultaSQL = """
            SELECT DISTINCT 
                id_departamento, 
                departamento,
                Provincias.id AS id_provincia, 
            FROM Departamentos1
            FULL OUTER JOIN Provincias
                ON CAST(id_departamento AS VARCHAR) LIKE CAST(Provincias.id AS VARCHAR) || '___'
            ORDER BY id_departamento;
            """
Departamentos1 = db.query(consultaSQL).df()

#Cambiamos dptos para que solo las iniciales tengan mayúsuculas
Departamentos1["departamento"] = Departamentos1["departamento"].str.title()


consultaSQL = """
            SELECT DISTINCT 
                in_departamentos AS id_departamento, 
                departamento,
                provincia_id AS id_provincia, 
            FROM df3
            ORDER BY id_departamento;
            """
Departamentos2 = db.query(consultaSQL).df()

V = df3[df3["genero"]=="Varones"]
M = df3[df3["genero"]=="Mujeres"]
consultaSQL = """
            SELECT
                COALESCE(V.anio, M.anio) AS anio,
                COALESCE(V.in_departamentos, M.in_departamentos) AS id_departamento,
                COALESCE(V.clae6, M.clae6) AS clae6,
                COALESCE(V.Empleo, 0) AS Empleo_Varones,
                COALESCE(M.Empleo, 0) AS Empleo_Mujeres,
                COALESCE(V.Establecimientos, 0) AS Establecimientos_Varones,
                COALESCE(M.Establecimientos, 0) AS Establecimientos_Mujeres,
                COALESCE(V.empresas_exportadoras, M.empresas_exportadoras) AS empresas_exportadoras
            FROM (
                SELECT *
                FROM df3
                WHERE genero = 'Varones'
            ) AS V
            JOIN (
                SELECT *
                FROM df3
                WHERE genero = 'Mujeres'
            ) AS M
            ON V.anio = M.anio
            AND V.in_departamentos = M.in_departamentos
            AND V.departamento = M.departamento
            AND V.provincia_id = M.provincia_id
            AND V.provincia = M.provincia
            AND V.clae6 = M.clae6
            AND V.clae2 = M.clae2
        """
df3_3FN = db.query(consultaSQL).df()
df3_3FN["Empleo_Varones"] = df3_3FN["Empleo_Varones"].fillna(0)
df3_3FN["Empleo_Mujeres"] = df3_3FN["Empleo_Mujeres"].fillna(0)
df3_3FN["Establecimientos_Varones"] = df3_3FN["Establecimientos_Varones"].fillna(0)
df3_3FN["Establecimientos_Mujeres"] = df3_3FN["Establecimientos_Mujeres"].fillna(0)

Provincias.to_csv("TablasModelo/Provincias.csv", index = False)










## df4
#%%
df4 = pd.read_excel(r"TablasOriginales/padron_poblacion.xlsX")

df4.columns = ["blank","Edad", "Casos", "Porcentaje", "Porcentaje_Acumulado"]

rows = []
for index, row in df4.iterrows():
    if row["Edad"] == "RESUMEN":
        break
    else:
        if isinstance(row["Edad"], (int, np.integer)):
            r = row.to_dict()
            r["id_departamento"] = id_dept
            r["departamento"] = dept
            rows.append(r)
        else:
            if pd.notnull(row["Edad"]) and row["Edad"][0] == "A":
                id_dept = int(row["Edad"][-5:])
                dept = row["Casos"]

grupos = pd.DataFrame(rows).reset_index(drop=True)

consultaSQL = """
            SELECT DISTINCT id_departamento, departamento, Provincias.id AS id_provincia
            FROM grupos
            FULL OUTER JOIN Provincias
                ON CAST(id_departamento AS VARCHAR) LIKE CAST(Provincias.id AS VARCHAR) || '___'
            ORDER BY id_departamento;
            """
Departamentos3 = db.query(consultaSQL).df()

consultaSQL = """
            SELECT id_departamento, Edad, Casos
            FROM grupos
            """
df4_3FN = db.query(consultaSQL).df()









# %%
# Unimos los dptos de los distintos dataset y sacamos repeticiones de las 15 comunas (estan indexadas distinto en Departamentos1)
Departamentos1["id_departamento"] = Departamentos1["id_departamento"].astype(int)
Departamentos2["id_departamento"] = Departamentos2["id_departamento"].astype(int)
Departamentos3["id_departamento"] = Departamentos3["id_departamento"].astype(int)
consultaSQL = """
    SELECT 
        COALESCE(Departamentos3.id_departamento, Departamentos2.id_departamento, Departamentos1_0.id_departamento) AS id_departamento,
        COALESCE(Departamentos3.departamento, Departamentos2.departamento, Departamentos1_0.departamento) AS departamento,
        COALESCE(Departamentos3.id_provincia, Departamentos2.id_provincia, Departamentos1_0.id_provincia) AS id_provincia
    FROM 
        (SELECT * FROM Departamentos1 ORDER BY id_departamento OFFSET 15) AS Departamentos1_0
    FULL OUTER JOIN Departamentos2
        ON Departamentos1_0.id_departamento = Departamentos2.id_departamento
    FULL OUTER JOIN Departamentos3
        ON COALESCE(Departamentos1_0.id_departamento, Departamentos2.id_departamento) = Departamentos3.id_departamento
    ORDER BY id_departamento
"""
Departamentos = db.query(consultaSQL).df()

#%%
#Filtramos las filas con ids cercanos y mismo nombre de dpto
filas_a_eliminar = []
id_a_cambiar = []
for i in range(len(Departamentos) - 1):
     dep_actual = Departamentos.loc[i, "departamento"]
     dep_siguiente = Departamentos.loc[i + 1, "departamento"]
     if dep_actual == dep_siguiente:
         id_a_cambiar.append(Departamentos.loc[i + 1, "id_departamento"])
         filas_a_eliminar.append(i+1)

Departamentos = Departamentos.drop(list(filas_a_eliminar)).reset_index(drop=True)

df1_3FN.loc[df1_3FN["id_departamento"].isin(id_a_cambiar), "id_departamento"] -= 1
df3_3FN.loc[df3_3FN["id_departamento"].isin(id_a_cambiar), "id_departamento"] -= 1
df4_3FN.loc[df4_3FN["id_departamento"].isin(id_a_cambiar), "id_departamento"] -= 1

Departamentos.to_csv("TablasModelo/Departamentos.csv", index = False)

#%%
#Cambiamos id_departamento de Comunas en df1
id_comunas = []
for i in range(len(Departamentos2)):
    if Departamentos2.loc[i, "departamento"].startswith("Comuna"):
        id_comunas.append(Departamentos2.loc[i, "id_departamento"])

for i in range(len(df1_3FN)):
    id_dep = df1_3FN.loc[i, "id_departamento"]
    if 2100 <= id_dep <= 2115:
        df1_3FN.at[i, "id_departamento"] = id_comunas[id_dep - 2101]

df1_3FN.to_csv("TablasModelo/Establecimientos_Educativos.csv", index = False)
df3_3FN.to_csv("TablasModelo/Dep_Act_Sex.csv", index = False)
df4_3FN.to_csv("TablasModelo/Padron_Poblacion.csv", index = False)









#%%
# Análisis de Datos

Actividades_Establecimientos = pd.read_csv(r"TablasModelo\Actividades_Establecimientos.csv")
Dep_Act_Sex = pd.read_csv(r"TablasModelo\Dep_Act_Sex.csv")
Departamentos = pd.read_csv(r"TablasModelo\Departamentos.csv")
Establecimientos_Educativos = pd.read_csv(r"TablasModelo\Establecimientos_Educativos.csv")
Niveles_EE = pd.read_csv(r"TablasModelo\Niveles_EE.csv")
Padron_Poblacion = pd.read_csv(r"TablasModelo\Padron_Poblacion.csv")
Provincias = pd.read_csv(r"TablasModelo\Provincias.csv")
Tipos_Niveles = pd.read_csv(r"TablasModelo\Tipos_Niveles.csv")

# i)
consultaSQL = """
        SELECT Niveles_EE.Cueanexo, Provincias.provincia AS Provincia, Departamentos.id_departamento, Departamentos.departamento AS Departamento, Tipos_Niveles.nivel
        FROM Establecimientos_Educativos
        JOIN Departamentos
            ON Departamentos.id_departamento = Establecimientos_Educativos.id_departamento
        JOIN Niveles_EE 
            ON Niveles_EE.Cueanexo = Establecimientos_Educativos.Cueanexo
        JOIN Provincias
            ON Provincias.id = Departamentos.id_provincia
        JOIN Tipos_Niveles
            ON Tipos_Niveles.id = Niveles_EE.id_nivel
"""
Est_Dep_Niv = db.query(consultaSQL).df()

consultaSQL = """
        SELECT
            Provincia,
            id_departamento,
            Departamento,
            SUM(CASE WHEN Nivel = 'Jardín maternal' OR Nivel = 'Jardín de infantes' THEN 1 ELSE 0 END) AS Jardines,
            SUM(CASE WHEN Nivel = 'Primario' THEN 1 ELSE 0 END) AS Primarios,
            SUM(CASE WHEN Nivel = 'Secundario' OR Nivel = 'Secundario - INET'THEN 1 ELSE 0 END) AS Secundarios,
        FROM Est_Dep_Niv
        GROUP BY
            Provincia,
            Departamento,
            id_departamento
        ORDER BY
            Provincia,
            Departamento;
"""
Ej1 = db.query(consultaSQL).df()

consultaSQL = """
        SELECT
            Provincia,
            Departamento,
            "Jardines",
            SUM(CASE WHEN Padron_Poblacion.Edad <= 5 THEN Padron_Poblacion.Casos ELSE 0 END) AS "Población Jardín",
            Primarios,
            SUM(CASE WHEN Padron_Poblacion.Edad >= 6 AND Padron_Poblacion.Edad <= 11 THEN Padron_Poblacion.Casos ELSE 0 END) AS "Población Primario",
            Secundarios,
            SUM(CASE WHEN Padron_Poblacion.Edad >= 12 AND Padron_Poblacion.Edad <= 18 THEN Padron_Poblacion.Casos ELSE 0 END) AS "Población Secundario",
        FROM Ej1
        LEFT OUTER JOIN Padron_Poblacion
            ON Padron_Poblacion.id_departamento = Ej1.id_departamento
        GROUP BY
            Provincia,
            Departamento,
            Jardines,
            Primarios,
            Secundarios,
"""
Ej1 = db.query(consultaSQL).df()
# ii)

# iii)

# iv)

# v)

# %%
