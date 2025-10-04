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
            SELECT DISTINCT letra, clae2, clae6
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
            COALESCE(M.anio, F.anio) AS anio,
            COALESCE(M.in_departamentos, F.in_departamentos) AS in_departamentos,
            COALESCE(M.provincia_id, F.provincia_id) AS provincia_id,
            COALESCE(M.clae6, F.clae6) AS clae6,
            COALESCE(M.clae2, F.clae2) AS clae2,
            COALESCE(M.letra, F.letra) AS letra,
            M.Empleo AS Empleo_M,
            M.Establecimientos AS Establecimientos_M,
            F.Empleo AS Empleo_F,
            F.Establecimientos AS Establecimientos_F,
            COALESCE(M.empresas_exportadoras, F.empresas_exportadoras) AS empresas_exportadoras,
            FROM (
                SELECT *
                FROM df3
                WHERE genero = 'Varones'
            ) AS M
            FULL OUTER JOIN (
                SELECT *
                FROM df3
                WHERE genero = 'Mujeres'
            ) AS F
            ON M.anio = F.anio
            AND M.in_departamentos = F.in_departamentos
            AND M.departamento = F.departamento
            AND M.provincia_id = F.provincia_id
            AND M.provincia = F.provincia
            AND M.clae6 = F.clae6
            AND M.clae2 = F.clae2
            AND M.letra = F.letra
            AND M.empresas_exportadoras = F.empresas_exportadoras;
            """
df3_3FN = db.query(consultaSQL).df()

## Clean df4
#%%
df4 = pd.read_excel(r"Datos/padron_poblacion.xlsX")





df4.columns = ["blank","Edad", "Casos", "Porcentaje", "Porcentaje_Acumulado"]
df = []
cont = 0
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
