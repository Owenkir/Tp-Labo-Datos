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










## df2
#%%
df2 = pd.read_csv(r"TablasOriginales/actividades_establecimientos.csv")

consultaSQL = """
            SELECT DISTINCT clae6, CAST(SUBSTRING(CAST(clae6 AS TEXT), 3) AS INTEGER) AS clae3, clae6_desc AS Actividad
            FROM df2
            ORDER BY clae6;
            """
df2_3FN = db.query(consultaSQL).df()










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

Tipos_Niveles.to_csv("TablasModelo/Tipos_Niveles.csv", index = False)
Niveles_EE.to_csv("TablasModelo/Niveles_EE.csv", index = False)
df2_3FN.to_csv("TablasModelo/Actividades_Establecimientos.csv", index = False)
Provincias.to_csv("TablasModelo/Provincias.csv", index = False)
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

#%%
# i)
consultaSQL = """
        SELECT Niveles_EE.Cueanexo, Provincias.provincia AS Provincia, Departamentos.id_departamento, Departamentos.departamento AS Departamento, Tipos_Niveles.nivel
        FROM Establecimientos_Educativos
        RIGHT OUTER JOIN Departamentos
            ON Departamentos.id_departamento = Establecimientos_Educativos.id_departamento
        LEFT OUTER JOIN Niveles_EE 
            ON Niveles_EE.Cueanexo = Establecimientos_Educativos.Cueanexo
        LEFT OUTER JOIN Provincias
            ON Provincias.id = Departamentos.id_provincia
        LEFT OUTER JOIN Tipos_Niveles
            ON Tipos_Niveles.id = Niveles_EE.id_nivel
"""
EsDepartamentos_Niv = db.query(consultaSQL).df()

consultaSQL = """
        SELECT
            Provincia,
            id_departamento,
            Departamento,
            SUM(CASE WHEN Nivel = 'Jardín maternal' OR Nivel = 'Jardín de infantes' THEN 1 ELSE 0 END) AS Jardines,
            SUM(CASE WHEN Nivel = 'Primario' THEN 1 ELSE 0 END) AS Primarios,
            SUM(CASE WHEN Nivel = 'Secundario' OR Nivel = 'Secundario - INET'THEN 1 ELSE 0 END) AS Secundarios,
        FROM EsDepartamentos_Niv
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

#%%
# ii) 
consultaSQL = """
WITH Empleo_Departamentos AS (
    SELECT id_departamento, 
        SUM(Empleo_Varones + Empleo_Mujeres) AS Empleados_Totales
    FROM Dep_Act_Sex
    WHERE anio = 2022
    GROUP BY id_departamento
)
    SELECT Provincias.provincia AS Provincia, Departamentos.departamento AS Departamento, 
        COALESCE(Empleo_Departamentos.Empleados_Totales, 0) AS "Cantidad total de empleados en 2022"
    FROM Departamentos
    JOIN Provincias ON Departamentos.id_provincia = Provincias.id
    LEFT JOIN Empleo_Departamentos ON Empleo_Departamentos.id_departamento = Departamentos.id_departamento
    ORDER BY Provincia ASC,
    "Cantidad total de empleados en 2022" DESC;

"""

Ej2 = db.query(consultaSQL).df()

#%%
# iii)
consultaSQL = """ SELECT
    Provincias.provincia AS Provincia,
    Departamentos.departamento AS Departamento,
    
    -- Convertimos todos los nulls a 0
    COALESCE(Dep_Act_Sex.Exportadoras_con_Empleo_Femenino, 0) AS "Cant_Expo_Mujeres",
    COALESCE(Establecimientos_Educativos.Cant_EE, 0) AS "Cant_EE",
    COALESCE(Padron_Poblacion.Poblacion_Total, 0) AS "Poblacion_Total"
    FROM Departamentos 
    JOIN Provincias ON Departamentos.id_provincia = Provincias.id
LEFT JOIN
    ( -- Cuento Establecimientos Educativos
        SELECT id_departamento,
            COUNT(Cueanexo) AS Cant_EE
        FROM Establecimientos_Educativos
        GROUP BY id_departamento
    ) AS Establecimientos_Educativos ON Departamentos.id_departamento = Establecimientos_Educativos.id_departamento
LEFT JOIN
    (-- Sumo la Poblacion Total
        SELECT id_departamento,
            SUM(Casos) AS Poblacion_Total
        FROM Padron_Poblacion
        GROUP BY id_departamento
    ) AS Padron_Poblacion ON Departamentos.id_departamento = Padron_Poblacion.id_departamento
LEFT JOIN
    (-- Sumo empresas exportadoras que emplean mujeres
        SELECT id_departamento,
            SUM(CASE
                    WHEN Empleo_Mujeres > 0 THEN empresas_exportadoras
                    ELSE 0
                END
            ) AS Exportadoras_con_Empleo_Femenino
        FROM Dep_Act_Sex
        WHERE anio = 2022
        GROUP BY id_departamento
    ) AS Dep_Act_Sex ON Departamentos.id_departamento = Dep_Act_Sex.id_departamento

ORDER BY
    "Cant_EE" DESC,
    "Cant_Expo_Mujeres" DESC,
    Provincia ASC,
    Departamento ASC;
"""

Ej3 = db.query(consultaSQL).df()

#%%
# iv)
consultaSQL = """ -- Calculo del total de empleo por cada departamento
WITH Empleo_Departamentos AS (
    SELECT id_departamento, SUM(Empleo_Varones + Empleo_Mujeres) AS Total_Empleo
    FROM Dep_Act_Sex
    WHERE anio = 2022
    GROUP BY id_departamento
),

-- Calculo del promedio de empleo a nivel provincial, el promedio de los totales de sus departamentos
Promedio_Provincial AS (
    SELECT Departamentos.id_provincia, AVG(Empleo_Departamentos.Total_Empleo) AS Promedio_Empleo_Prov
    FROM Empleo_Departamentos
    JOIN Departamentos ON Empleo_Departamentos.id_departamento = Departamentos.id_departamento
    GROUP BY Departamentos.id_provincia
),

-- Identificar los departamentos que superan el promedio
Departamentos_Filtrados AS (
    SELECT Empleo_Departamentos.id_departamento, Departamentos.id_provincia
    FROM Empleo_Departamentos
    JOIN Departamentos ON Empleo_Departamentos.id_departamento = Departamentos.id_departamento
    JOIN Promedio_Provincial ON Departamentos.id_provincia = Promedio_Provincial.id_provincia
    WHERE Empleo_Departamentos.Total_Empleo > Promedio_Provincial.Promedio_Empleo_Prov
),

-- Calculo del empleo por rubro para cada departamento
-- uso printf('%06d', clae6) para rellenar con zeros si no llega a 6 numeros
-- uso SUBSTR(-,1,3) para agarrar los primeros 3 digitos
Empleo_por_Rubro AS (
    SELECT id_departamento, SUBSTR(printf('%06d', clae6), 1, 3) AS clae3, SUM(Empleo_Varones + Empleo_Mujeres) AS Empleo_Rubro
    FROM Dep_Act_Sex
    WHERE anio = 2022
    GROUP BY id_departamento, clae3
),

-- Busco el mejor rubro por cada departamento
Top_Rubro_Deptal AS (
    SELECT id_departamento, clae3, Empleo_Rubro,        
        ROW_NUMBER() OVER(
            PARTITION BY id_departamento 
            ORDER BY Empleo_Rubro DESC
        ) AS Ranking_Rubros
    FROM Empleo_por_Rubro
)

-- Unimos la info filtrando por los deptos sobre promedio y el mejor rubro 
    SELECT Provincias.provincia AS Provincia, Departamentos.departamento AS Departamento, Top_Rubro_Deptal.clae3 AS "CLAE3", Top_Rubro_Deptal.Empleo_Rubro AS "Cant. empleos"
    FROM Departamentos_Filtrados
    JOIN Departamentos ON Departamentos_Filtrados.id_departamento = Departamentos.id_departamento
    JOIN Provincias ON Departamentos.id_provincia = Provincias.id
    JOIN Top_Rubro_Deptal ON Departamentos_Filtrados.id_departamento = Top_Rubro_Deptal.id_departamento
    WHERE Top_Rubro_Deptal.Ranking_Rubros = 1  
    ORDER BY
        Provincia,
        "Cant. empleos" DESC;
    
"""

Ej4 = db.query(consultaSQL).df()

# %%
# VISUALIZACIONES
# i)
# Consulta SQL para sumar el empleo total por provincia para 2022 y ordenar
# Usamos 'df3_3FN' (que contiene los datos de Dep_Act_Sex), 
# filtramos por el año 2022, sumamos ambos empleos (varones y mujeres),
# y unimos con Departamentos y Provincias.

sql_empleo_prov = """
SELECT
    P.provincia,
    SUM(EP.Empleo_Varones + EP.Empleo_Mujeres) AS total_empleo
FROM Dep_Act_Sex AS EP
JOIN Departamentos AS D ON EP.id_departamento = D.id_departamento
JOIN Provincias AS P ON D.id_provincia = P.id
WHERE EP.anio = 2022
GROUP BY P.provincia
ORDER BY total_empleo DESC
"""

# Ejecutar la consulta
df_plot_empleo = db.query(sql_empleo_prov).df()

# Generar el gráfico
plt.figure(figsize=(12, 9)) # Tamaño adecuado para 24 provincias
ax_empleo = sns.barplot(
    data=df_plot_empleo,
    x='total_empleo',
    y='provincia',
    palette='inferno' # Usamos una paleta de colores
)

# Configurar títulos y etiquetas
ax_empleo.set_title('Cantidad Total de Empleados por Provincia (Año 2022)', fontsize=16, weight='bold')
ax_empleo.set_xlabel('Cantidad de Empleados (en millones)', fontsize=12)
ax_empleo.set_ylabel('Provincia', fontsize=12)

# Añadir las etiquetas de datos (cantidad) en cada barra
# Formateamos los números para que sean más legibles (ej: 1.5M)
def format_millones(x, pos):
    'Los valores son en millones'
    return f'{x*1e-6:.1f}M'

from matplotlib.ticker import FuncFormatter
ax_empleo.xaxis.set_major_formatter(FuncFormatter(format_millones))
ax_empleo.bar_label(ax_empleo.containers[0], fmt='%.0f', padding=3, fontsize=9)

plt.tight_layout()
plt.savefig('grafico_empleados_por_provincia_2022.png') # Guardar el gráfico
#%%
# ii)
# Consulta SQL para cruzar población y establecimientos por nivel
# Esta consulta unifica los datos por grupos etarios/niveles
sql_niveles_poblacion = """
WITH 
-- 1. Agrupar la población por departamento y grupo etario
Poblacion_Grupos AS (
    SELECT
        id_departamento,
        CASE
            WHEN Edad BETWEEN 0 AND 5 THEN 'Inicial (0-5)'
            WHEN Edad BETWEEN 6 AND 12 THEN 'Primario (6-12)'
            WHEN Edad BETWEEN 13 AND 17 THEN 'Secundario (13-17)'
            ELSE NULL
        END AS grupo_etario,
        SUM(Casos) AS poblacion_grupo
    FROM Padron_Poblacion -- Usamos la variable cargada del CSV
    WHERE grupo_etario IS NOT NULL
    GROUP BY id_departamento, grupo_etario
),

-- 2. Agrupar los niveles educativos en los mismos grupos
-- Usamos la variable 'Tipos_Niveles' que se crea al inicio del script
Niveles_Agrupados AS (
    SELECT
        id,
        CASE
            -- Tu script define 'Jardín maternal' y 'Jardín de infantes'
            WHEN nivel IN ('Jardín maternal', 'Jardín de infantes') THEN 'Inicial (0-5)'
            WHEN nivel = 'Primario' THEN 'Primario (6-12)'
            WHEN nivel IN ('Secundario', 'Secundario - INET') THEN 'Secundario (13-17)'
        END AS grupo_etario
    FROM Tipos_Niveles
    WHERE grupo_etario IS NOT NULL
),

-- 3. Contar establecimientos por departamento y grupo etario
-- Usamos 'Establecimientos_Educativos' y 'Niveles_EE'
EE_Grupos AS (
    SELECT
        EE.id_departamento,
        NA.grupo_etario,
        COUNT(DISTINCT EE.Cueanexo) AS cantidad_ee
    FROM Establecimientos_Educativos AS EE
    JOIN Niveles_EE AS NE ON EE.Cueanexo = NE.Cueanexo
    JOIN Niveles_Agrupados AS NA ON NE.id_nivel = NA.id
    GROUP BY EE.id_departamento, NA.grupo_etario
),

-- 4. Unir todo. Usamos LEFT JOIN desde Poblacion por si hay deptos sin escuelas
Plot_Data AS (
    SELECT
        PG.id_departamento,
        D.departamento,
        P.provincia,
        PG.grupo_etario,
        PG.poblacion_grupo,
        COALESCE(EEG.cantidad_ee, 0) AS cantidad_ee -- Rellenar con 0 donde no hay escuelas
    FROM Poblacion_Grupos AS PG
    LEFT JOIN EE_Grupos AS EEG 
        ON PG.id_departamento = EEG.id_departamento 
        AND PG.grupo_etario = EEG.grupo_etario
    JOIN Departamentos AS D ON PG.id_departamento = D.id_departamento
    JOIN Provincias AS P ON D.id_provincia = P.id
)

SELECT * FROM Plot_Data
"""

# Ejecutar la consulta
df_plot_niveles = db.query(sql_niveles_poblacion).df()

# Generar el gráfico de dispersión
plt.figure(figsize=(14, 8)) # Un gráfico más ancho para la leyenda
ax_scatter = sns.scatterplot(
    data=df_plot_niveles,
    x='poblacion_grupo',
    y='cantidad_ee',
    hue='grupo_etario',  # Color por grupo
    style='grupo_etario', # Forma del marcador por grupo
    palette='Set1',      # Paleta de colores distintivos
    alpha=0.7,           # Transparencia
    s=80                 # Tamaño de los puntos
)

# Configurar títulos y etiquetas
ax_scatter.set_title('Establecimientos Educativos vs. Población por Nivel y Grupo Etario (por Departamento)', fontsize=16, weight='bold')
ax_scatter.set_xlabel('Población en el Grupo Etario', fontsize=12)
ax_scatter.set_ylabel('Cantidad de Establecimientos del Nivel', fontsize=12)

# Formatear ejes para mejor lectura (ej: 10000 -> 10k)
from matplotlib.ticker import FuncFormatter
ax_scatter.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x/1000:.0f}k')) 

# Mover la leyenda fuera del gráfico para que no tape los puntos
ax_scatter.legend(title='Nivel (Grupo Etario)', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)

plt.tight_layout()
# bbox_inches='tight' es importante para asegurar que la leyenda se guarde
plt.savefig('grafico_ee_vs_poblacion_por_nivel.png', bbox_inches='tight') 

#%%
# iii)
# Consulta SQL para obtener la cantidad de EE por cada departamento y provincia
sql_box = """
SELECT
    P.provincia,
    D.departamento,
    COUNT(EE.Cueanexo) AS cantidad_ee
FROM Establecimientos_Educativos AS EE
JOIN Departamentos AS D ON EE.id_departamento = D.id_departamento
JOIN Provincias AS P ON D.id_provincia = P.id
GROUP BY P.provincia, D.departamento
"""

# Ejecutar la consulta
df_plot_box = db.query(sql_box).df()

# Calcular el orden de las provincias basado en su mediana
prov_order = df_plot_box.groupby('provincia')['cantidad_ee'] \
                      .median() \
                      .sort_values(ascending=False) \
                      .index

# Generar el gráfico
plt.figure(figsize=(12, 10)) 
ax_box = sns.boxplot(
    data=df_plot_box,
    x='cantidad_ee',
    y='provincia',
    order=prov_order,
    palette='viridis'
)

# Configurar títulos y etiquetas
ax_box.set_title('Distribución de Establecimientos Educativos (EE) por Departamento', fontsize=16, weight='bold')

# Añadimos la aclaración [Escala Logarítmica] a la etiqueta del eje X
ax_box.set_xlabel('Cantidad de Establecimientos Educativos (por Departamento) [Escala Logarítmica]', fontsize=12)


ax_box.set_ylabel('Provincia', fontsize=12)

# Mejorar la legibilidad del eje X
ax_box.xaxis.grid(True)
ax_box.set_xscale('log') # Aplicar la escala logarítmica
from matplotlib.ticker import ScalarFormatter
ax_box.xaxis.set_major_formatter(ScalarFormatter()) # Mostrar números (10, 100) en lugar de (10^1, 10^2)

plt.tight_layout()
plt.savefig('grafico_boxplot_ee_por_provincia.png')

#%%
# iv)
# Consulta para recolectar Empleados cada mil habitantes y Establecimientos Educativos cada mil habitantes
consultaSQL= """
WITH Poblacion_Total AS (SELECT id_departamento, SUM(Casos) AS Poblacion
                         FROM Padron_Poblacion
                         GROUP BY id_departamento
    ),
EE_Por_Depto AS (SELECT id_departamento, COUNT(Cueanexo) AS cantidad_EE
                 FROM Establecimientos_Educativos
                 GROUP BY id_departamento
    ),
Empleados_Por_Depto AS (SELECT id_departamento, SUM(Empleo_Varones + Empleo_Mujeres) AS Cant_Empleados
                        FROM Dep_Act_Sex
                        WHERE anio = 2022
                        GROUP BY id_departamento
    )


    SELECT Provincias.provincia, Departamentos.departamento, COALESCE(EE_Por_Depto.cantidad_EE,0) AS cantidad_EE, COALESCE(Empleados_Por_Depto.Cant_Empleados, 0) AS Cant_Empleados, Poblacion_Total.Poblacion,
        (COALESCE(Empleados_Por_Depto.Cant_Empleados,0) * 1000 / Poblacion_Total.Poblacion) AS Empleados_Cada_Mil,
        (COALESCE(EE_Por_Depto.cantidad_EE,0) * 1000 / Poblacion_Total.Poblacion) AS EE_Cada_Mil
    
    FROM Poblacion_Total
    JOIN Departamentos ON Poblacion_Total.id_departamento = Departamentos.id_departamento
    JOIN Provincias ON Departamentos.id_provincia = Provincias.id
    LEFT JOIN EE_Por_Depto ON Poblacion_Total.id_departamento = EE_Por_Depto.id_departamento
    LEFT JOIN Empleados_Por_Depto ON Poblacion_Total.id_departamento = Empleados_Por_Depto.id_departamento
    WHERE Poblacion_Total.Poblacion > 1000;
--filtro a los deptos con poblacion menor a 1000 para que no distorsione el grafico dividiendo por un numero muy chico, resultando en valores grandes fuera de lo normal.

"""

dfVis4 = db.query(consultaSQL).df()

# Intervalos de poblacion total
dfVis4['Poblacion_Intervalos'] = pd.cut(dfVis4['Poblacion'], 
    bins=[0,100000,400000,800000,np.inf], 
    labels=['0 - 100k', '100k - 400k', '400k - 800k', '800k +'], 
    right=False #asi es un intervalo cerrado y abierto [a,b)
)
# Filtramos por quantil 0.99 para sacar los casos extremos y que no quede lo demas todo junto
quantil_emp = dfVis4['Empleados_Cada_Mil'].quantile(0.99)
quantil_ee = dfVis4['EE_Cada_Mil'].quantile(0.99)

dfVis4_filtrado = dfVis4[(dfVis4['Empleados_Cada_Mil'] <= quantil_emp) & (dfVis4['EE_Cada_Mil'] <= quantil_ee)]

sns.scatterplot(
    data=dfVis4_filtrado, 
    x='EE_Cada_Mil', 
    y='Empleados_Cada_Mil', 
    size='Poblacion',  
    hue='Poblacion_Intervalos',
    sizes=(30, 1200),        
    alpha=0.7,                          
)

plt.title('Relación Empleados vs Establecimientos Educativos por Departamento.', fontsize=12)
plt.xlabel('Establecimientos Educativos cada 1000 habitantes', fontsize=8)
plt.ylabel('Empleados cada 1000 habitantes', fontsize=8)

#%%
# v)
# IMPORTANTE: Esta consulta usa el DataFrame 'df3' (el CSV original) 
# que se cargó en la sección ## df3, NO el 'Dep_Act_Sex.csv' procesado.

# 1. Calcular el promedio general de empleo femenino (usando df3)
sql_promedio_fem = """
SELECT
    -- Multiplicamos por 1.0 para asegurar división flotante
    SUM(CASE WHEN genero = 'Mujeres' THEN Empleo ELSE 0 END) * 1.0 / 
    SUM(Empleo)
FROM df3 -- <-- Usando el df3 original (largo)
WHERE anio = 2022
"""
promedio_general = db.query(sql_promedio_fem).fetchone()[0]


# 2. Consulta SQL para obtener el Top 5 y Bottom 5 de actividades (usando df3)
sql_top_bottom = """
WITH
-- 1. Calcular el empleo total por actividad (clae6) para 2022, usando el df3 original
Empleo_por_Actividad AS (
    SELECT
        clae6,
        SUM(CASE WHEN genero = 'Mujeres' THEN Empleo ELSE 0 END) AS total_mujeres,
        SUM(CASE WHEN genero = 'Varones' THEN Empleo ELSE 0 END) AS total_varones
    FROM df3 -- <-- Usando el df3 original (largo)
    WHERE anio = 2022
    GROUP BY clae6
),

-- 2. Calcular la proporción, filtrando actividades
Proporciones_Actividad AS (
    SELECT
        clae6,
        total_mujeres,
        total_varones,
        (total_mujeres + total_varones) AS total_empleo,
        (total_mujeres * 1.0) / (total_mujeres + total_varones) AS proporcion_mujeres
    FROM Empleo_por_Actividad
    -- Filtramos para que sea significativo (más de 100 empleados en total)
    -- y para evitar división por cero (aunque COALESCE abajo lo manejaría)
    WHERE (total_mujeres + total_varones) > 100 
),

-- 3. Rankear todas las actividades
Ranked AS (
    SELECT *,
        -- Rango de 1 a N para las más altas
        ROW_NUMBER() OVER(ORDER BY proporcion_mujeres DESC) as rank_desc,
        -- Rango de 1 a N para las más bajas
        ROW_NUMBER() OVER(ORDER BY proporcion_mujeres ASC) as rank_asc
    FROM Proporciones_Actividad
    -- Nos aseguramos de que no haya NaN (si 0/0 ocurre)
    WHERE proporcion_mujeres IS NOT NULL
)

-- 4. Seleccionar el Top 5 y Bottom 5 y unir con sus descripciones
SELECT 
    R.clae6,
    A.Actividad,
    R.proporcion_mujeres,
    R.total_empleo,
    -- Etiqueta para colorear el gráfico
    CASE
        WHEN R.rank_desc <= 5 THEN 'Top 5 (Mayor Proporción)'
        ELSE 'Bottom 5 (Menor Proporción)'
    END AS tipo
FROM Ranked AS R
-- Unimos con 'Actividades_Establecimientos' que ya está en memoria
JOIN Actividades_Establecimientos AS A ON R.clae6 = A.clae6
WHERE R.rank_desc <= 5 OR R.rank_asc <= 5
ORDER BY R.proporcion_mujeres DESC
"""

# Ejecutar la consulta
df_plot_fem = db.query(sql_top_bottom).df()

# 3. Crear etiquetas legibles para el gráfico (acortando las descripciones)
df_plot_fem['label_actividad'] = df_plot_fem['Actividad'].str.slice(0, 45) + \
                                 '... (' + df_plot_fem['clae6'].astype(str) + ')'

# 4. Generar el gráfico
plt.figure(figsize=(14, 10))
ax_fem = sns.barplot(
    data=df_plot_fem,
    x='proporcion_mujeres',
    y='label_actividad',
    hue='tipo',
    palette={'Top 5 (Mayor Proporción)':'#34a853', 'Bottom 5 (Menor Proporción)':'#ea4335'},
    dodge=False 
)

# 5. Formatear el eje X como porcentaje
from matplotlib.ticker import FuncFormatter
ax_fem.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x * 100:.0f}%'))

# 6. Añadir la línea del promedio general
ax_fem.axvline(
    x=promedio_general,
    color='blue',
    linestyle='--',
    linewidth=2.5,
    label=f'Promedio General ({promedio_general * 100:.1f}%)'
)

# 7. Añadir etiquetas de datos (el porcentaje) en cada barra
labels = [f'{p * 100:.1f}%' for p in df_plot_fem['proporcion_mujeres']]
ax_fem.bar_label(ax_fem.containers[0], labels=labels, padding=3, fontsize=10)
if len(ax_fem.containers) > 1:
    ax_fem.bar_label(ax_fem.containers[1], labels=labels, padding=3, fontsize=10)


# 8. Configurar títulos, leyenda y etiquetas
ax_fem.set_title('Top 5 y Bottom 5 Actividades por Proporción de Empleo Femenino (2022)', fontsize=16, weight='bold')
ax_fem.set_xlabel('Proporción de Empleo Femenino', fontsize=12)
ax_fem.set_ylabel('Actividad (CLAE6)', fontsize=12)
ax_fem.legend(loc='lower right', fontsize=12)

ax_fem.set_xlim(right=ax_fem.get_xlim()[1] * 1.1) 

plt.tight_layout()
plt.savefig('grafico_top_bottom_5_empleo_femenino.png')

