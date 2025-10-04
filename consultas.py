import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import duckdb as db
import numpy as np

## Clean df1
#%%
df1 = pd.read_excel(r"Datos/2025.09.24_padron_oficial_establecimientos_educativos_die_icse_1.xlsx",skiprows=12)

df1 = df1.rename(columns={
    'Unnamed: 37': 'Talleres Artística',
    'Unnamed: 38': 'Servicios complementarios',
    'Unnamed: 39': 'Validez titulos',
    'Unnamed: 40': 'Total de hogares',
    'Unnamed: 41': 'Hogares con población de 3 a 17',
    'Unnamed: 42': 'Poblacion de 3 a 17'
})

consultaSQL = """
            SELECT
            "Jurisdicción" AS Provincia,
            "Departamento",
            "Código de departamento" AS id_departamento,
            "Localidad",
            "Código de localidad" AS id_localidad,
            "Cueanexo",
            "Nivel inicial - Jardín maternal",
            "Nivel inicial - Jardín de infantes",
            "Primario",
            "Secundario",
            "Secundario - INET",
            "SNU",
            "SNU - INET",
            "SNU - Cursos",
            "Total de hogares",
            "Hogares con población de 3 a 17",
            "Poblacion de 3 a 17"
            FROM df1
            WHERE Común = 1
            """
df1 = db.query(consultaSQL).df()

consultaSQL = """
            SELECT DISTINCT id_localidad as id, localidad
            FROM df1;
            """
Localidades = db.query(consultaSQL).df()


niveles = ["Nivel inicial - Jardín maternal",
            "Nivel inicial - Jardín de infantes",
            "Primario",
            "Secundario",
            "Secundario - INET",
            "SNU",
            "SNU - INET",
            "SNU - Cursos"]

Tipos_Niveles = pd.DataFrame({
    "id": range(len(niveles)),
    "nivel": niveles
})

rows = []

for id, nivel in enumerate(niveles):
    df = df1[df1[nivel] == 1][["Cueanexo"]].copy()
    df["id"] = id
    rows.append(df)

Niveles_EE = pd.concat(rows, ignore_index=True)

consultaSQL = """
            SELECT
            Cueanexo,
            id_localidad,
            "Total de hogares",
            "Hogares con población de 3 a 17",
            "Poblacion de 3 a 17"
            FROM df1;
            """
df1_3FN = db.query(consultaSQL).df()

df1_3FN.to_csv("Datos_3FN/Establecimientos_Educativos.csv", index = False)
Tipos_Niveles.to_csv("Datos_3FN/Tipos_Niveles.csv", index = False)
Niveles_EE.to_csv("Datos_3FN/Niveles_EE.csv", index = False)
Localidades.to_csv("Datos_3FN/Localidades.csv", index = False)










## df2
#%%
df2 = pd.read_csv(r"Datos/actividades_establecimientos.csv")

consultaSQL = """
            SELECT DISTINCT letra, letra_desc
            FROM df2
            ORDER BY letra;
            """
letra_desc = db.query(consultaSQL).df()
consultaSQL = """
            SELECT DISTINCT clae2, clae2_desc
            FROM df2
            ORDER BY clae2;
            """
clae2_desc = db.query(consultaSQL).df()
consultaSQL = """
            SELECT DISTINCT clae6, clae6_desc
            FROM df2
            ORDER BY clae6;
            """
clae6_desc = db.query(consultaSQL).df()
consultaSQL = """
            SELECT DISTINCT letra, clae6
            FROM df2
            """
df2_3FN = db.query(consultaSQL).df()

letra_desc.to_csv("Datos_3FN/Letras.csv", index = False)
clae2_desc.to_csv("Datos_3FN/clae2.csv", index = False)
clae6_desc.to_csv("Datos_3FN/clae6.csv", index = False)
df2_3FN.to_csv("Datos_3FN/Actividades_Establecimientos.csv", index = False)










## df3
#%%
df3 = pd.read_csv(r"Datos/Datos_por_departamento_actividad_y_sexo.csv")

consultaSQL = """
            SELECT DISTINCT provincia_id AS id, provincia
            FROM df3
            ORDER BY provincia_id;
            """
Provincias = db.query(consultaSQL).df()

consultaSQL = """
            SELECT DISTINCT in_departamentos as id, departamento
            FROM df3
            ORDER BY id;
            """
Departamentos = db.query(consultaSQL).df()

V = df3[df3["genero"]=="Varones"]
M = df3[df3["genero"]=="Mujeres"]
consultaSQL = """
            SELECT
                COALESCE(V.anio, M.anio) AS anio,
                COALESCE(V.in_departamentos, M.in_departamentos) AS id_departamentos,
                COALESCE(V.departamento, M.departamento) AS departamento,
                COALESCE(V.provincia_id, M.provincia_id) AS provincia_id,
                COALESCE(V.provincia, M.provincia) AS provincia,
                COALESCE(V.clae6, M.clae6) AS clae6,
                COALESCE(V.clae2, M.clae2) AS clae2,
                COALESCE(V.letra, M.letra) AS letra,
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
            FULL OUTER JOIN (
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
            AND V.letra = M.letra
        """
df3_3FN = db.query(consultaSQL).df()
df3_3FN["Empleo_Varones"] = df3_3FN["Empleo_Varones"].fillna(0)
df3_3FN["Empleo_Mujeres"] = df3_3FN["Empleo_Mujeres"].fillna(0)
df3_3FN["Establecimientos_Varones"] = df3_3FN["Establecimientos_Varones"].fillna(0)
df3_3FN["Establecimientos_Mujeres"] = df3_3FN["Establecimientos_Mujeres"].fillna(0)

Departamentos.to_csv("Datos_3FN/Departamentos.csv", index = False)
df3_3FN.to_csv("Datos_3FN/Dep_Act_Sex.csv", index = False)










## df4
#%%
df4 = pd.read_excel(r"Datos/padron_poblacion.xlsX")

df4.columns = ["blank","Edad", "Casos", "Porcentaje", "Porcentaje_Acumulado"]
consultaSQL = """
            SELECT DISTINCT ROW_NUMBER() OVER () AS id, Casos as departamento
            FROM df4
            WHERE Edad LIKE 'AREA%'
            ORDER BY id;
            """
Departamentos1 = db.query(consultaSQL).df()
rows = []
cont = 0
for index, row in df4.iterrows():
    if row["Edad"] == "RESUMEN":
        break
    if row["Casos"] == "Casos":
        cont += 1
    else:
        if isinstance(row["Edad"], (int, np.integer)):
            r = row.to_dict()
            r["id_departamentos"] = cont
            rows.append(r)

grupos = pd.DataFrame(rows).reset_index(drop=True)
consultaSQL = """
            SELECT id_departamentos, Edad, Casos
            FROM Departamentos1
            JOIN Departamentos
            ON Departamentos1.departamento = Departamentos.departamento
            JOIN grupos
            ON grupos.id_departamentos = Departamentos1.id
            """
df4_3FN = db.query(consultaSQL).df()

df4_3FN.to_csv("Datos_3FN/Padron_Poblacion.csv", index = False)
