import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import duckdb as db
import numpy as np

## Clean df1
#%%
df1 = pd.read_excel(r"Datos/2025.09.24_padron_oficial_establecimientos_educativos_die_icse_1.xlsx")


## Clean df2
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


## Clean df3
#%%
df3 = pd.read_csv(r"Datos/Datos_por_departamento_actividad_y_sexo.csv")




consultaSQL = """
            SELECT DISTINCT provincia_id, provincia
            FROM df3
            ORDER BY provincia_id;
            """
Provincias = db.query(consultaSQL).df()

consultaSQL = """
            SELECT DISTINCT in_departamentos, departamento
            FROM df3
            ORDER BY in_departamentos;
            """
Departamentos = db.query(consultaSQL).df()

consultaSQL = """
            SELECT
            COALESCE(V.anio, M.anio) AS anio,
            COALESCE(V.in_departamentos, M.in_departamentos) AS in_departamentos,
            COALESCE(V.clae6, M.clae6) AS clae6,
            COALESCE(V.letra, M.letra) AS letra,
            COALESCE(V.Empleo, 0) AS Empleo_Varones,
            COALESCE(V.Establecimientos, 0) AS Establecimientos_Varones,
            COALESCE(M.Empleo, 0) AS Empleo_Mujeres,
            COALESCE(M.Establecimientos, 0) AS Establecimientos_Mujeres,
            COALESCE(V.empresas_exportadoras, M.empresas_exportadoras) AS empresas_exportadoras,
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
            AND V.empresas_exportadoras = M.empresas_exportadoras;
            """
df3_3FN = db.query(consultaSQL).df()

## Clean df4
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
            SELECT in_departamentos, Edad, Casos
            FROM Departamentos1
            JOIN Departamentos
            ON Departamentos1.departamento = Departamentos.departamento
            JOIN grupos
            ON grupos.id_departamentos = Departamentos1.id
            """
df4_3FN = db.query(consultaSQL).df()
# %%
