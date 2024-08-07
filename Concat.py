# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 08:09:27 2024

@author: Lperez
"""
import pandas as pd

# Crea los DataFrames
df1 = pd.read_excel("Consol.xlsx")
df2 = pd.read_excel("Consol_plus042024.xlsx")
# df3 = pd.read_excel("octavio.xlsx")


# Concatena los DataFrames y elimina los duplicados
df4 = pd.concat([df1, df2], axis=0)
df4 = df4.drop_duplicates(subset=["REFERENCIA", "REPORTE", "FECHA DE REPORTE"], keep="first")
df4 = df4.fillna('')

# Crea un nuevo Excel
df4.to_excel("new_consol.xlsx")