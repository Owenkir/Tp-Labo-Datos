import pandas as pd

#GQM Tabla 1 - Establecimientos Educativos

# Cargar el archivo de establecimientos educativos, omitiendo las primeras 6 filas que no contienen los datos de la tabla.
ee_df = pd.read_csv("C:\Users\andre\Downloads\2022_padron_oficial_establecimientos_educativos.xlsx", skiprows=6) 
                                        
# Renombrar la columna para facilitar el acceso
ee_df.rename(columns={'Mail': 'mail'}, inplace=True) 

total_registros = len(ee_df) # Total de registros en el DataFrame
mails_nulos = ee_df['mail'].isna().sum() # Contar valores nulos (NaN)
mails_espacio = (ee_df['mail'] == ' ').sum() # Contar registros que solo contienen un espacio en blanco ' '
total_vacios = mails_nulos + mails_espacio # El total de vacíos es la suma de los nulos y los que solo tienen un espacio

# Calcular la métrica como el porcentaje de vacíos sobre el total
metrica_mail = total_vacios / total_registros 

print(metrica_mail)

#GQM Tabla 2 - Establecimientos Productivos

# Cargar el archivo de establecimientos productivos
ep_df = pd.read_csv('Datos_por_departamento_actividad_y_sexo.csv')

# Sumar el empleo y los establecimientos
ep_df['total_empleo'] = ep_df['Empleo']
ep_df['total_establecimientos'] = ep_df['Establecimientos']

# Total de registros
total_registros_ep = len(ep_df)

# Filtrar para encontrar los registros lógicamente inconsistentes:
# Empleo > 0 Y Establecimientos = 0
inconsistentes = ep_df[(ep_df['total_empleo'] > 0) & (ep_df['total_establecimientos'] == 0)]

# Contar cuántos registros cumplen esa condición
cantidad_inconsistentes = len(inconsistentes)

# Calcular la métrica como el porcentaje de inconsistentes sobre el total
metrica_ep = cantidad_inconsistentes / total_registros_ep

print(metrica_ep)
