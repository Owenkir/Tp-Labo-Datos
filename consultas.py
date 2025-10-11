#%%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import duckdb as db
import numpy as np

## df1
#%%
df1 = pd.read_excel(r"Datos\2022_padron_oficial_establecimientos_educativos.xlsx",skiprows=6)

consultaSQL = """
            SELECT
            Cueanexo,
            "Jurisdicción" AS Provincia,
            CAST(SUBSTRING(CAST("Código de localidad" AS TEXT) FROM 1 FOR LENGTH(CAST("Código de localidad" AS TEXT)) - 3) AS INTEGER) AS id_departamento,
            Departamento AS departamento,
            "Nivel inicial - Jardín maternal",
            "Nivel inicial - Jardín de infantes",
            Primario,
            Secundario,
            "Secundario - INET",
            FROM df1
            WHERE TRY_CAST(Común AS INT) = 1
            """
df1 = db.query(consultaSQL).df()

niveles = ["Nivel inicial - Jardín maternal",
            "Nivel inicial - Jardín de infantes",
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
Departamentos = db.query(consultaSQL).df()

consultaSQL = """
            SELECT
            Cueanexo, 
            id_departamento
            FROM df1;
            """
df1_3FN = db.query(consultaSQL).df()

df1_3FN.to_csv("Datos_3FN/Establecimientos_Educativos.csv", index = False)
Tipos_Niveles.to_csv("Datos_3FN/Tipos_Niveles.csv", index = False)
Niveles_EE.to_csv("Datos_3FN/Niveles_EE.csv", index = False)









## df2
#%%
df2 = pd.read_csv(r"Datos/actividades_establecimientos.csv")

consultaSQL = """
            SELECT DISTINCT clae6, CAST(SUBSTRING(CAST(clae6 AS TEXT), 3) AS INTEGER) AS clae3, clae6_desc AS Actividad
            FROM df2
            ORDER BY clae6;
            """
df2_3FN = db.query(consultaSQL).df()

df2_3FN.to_csv("Datos_3FN/Actividades_Establecimientos.csv", index = False)










## df3
#%%
df3 = pd.read_csv(r"Datos/Datos_por_departamento_actividad_y_sexo.csv")


## Igualar id y nombres provincias df1 y df3
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
            FROM Departamentos
            FULL OUTER JOIN Provincias
                ON CAST(id_departamento AS VARCHAR) LIKE CAST(Provincias.id AS VARCHAR) || '___'
            ORDER BY id_departamento;
            """
Departamentos = db.query(consultaSQL).df()

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

Provincias.to_csv("Datos_3FN/Provincias.csv", index = False)
Departamentos.to_csv("Datos_3FN/Departamentos.csv", index = False)
df3_3FN.to_csv("Datos_3FN/Dep_Act_Sex.csv", index = False)










## df4
#%%
df4 = pd.read_excel(r"Datos/padron_poblacion.xlsX")

df4.columns = ["blank","Edad", "Casos", "Porcentaje", "Porcentaje_Acumulado"]

rows = []
for index, row in df4.iterrows():
    if row["Edad"] == "RESUMEN":
        break
    else:
        if isinstance(row["Edad"], (int, np.integer)):
            r = row.to_dict()
            r["id_departamento"] = cont
            rows.append(r)
        else:
            if pd.notnull(row["Edad"]) and row["Edad"][0] == "A":
                cont = int(row["Edad"][-5:])

grupos = pd.DataFrame(rows).reset_index(drop=True)

consultaSQL = """
            SELECT id_departamento, Edad, Casos
            FROM grupos
            """
df4_3FN = db.query(consultaSQL).df()

df4_3FN.to_csv("Datos_3FN/Padron_Poblacion.csv", index = False)

# %%
