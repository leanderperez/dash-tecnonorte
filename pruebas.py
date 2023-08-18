# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 13:48:34 2023

@author: Leander
"""

from datetime import date, datetime
from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash_auth
# import os
import passwords
import locale 
locale.setlocale(locale.LC_ALL,'es_ES.UTF-8')


df = pd.read_excel('Consol.xlsx')
df['FECHA DE REPORTE'] = pd.to_datetime(df['FECHA DE REPORTE']).dt.date
df['FECHA DE REPORTE'] = pd.to_datetime(df['FECHA DE REPORTE']).dt.month_name(locale='es_ES.UTF-8')



# df['FECHA DE REPORTE'] = pd.to_datetime(df['FECHA DE REPORTE']).dt.month_name(locale = 'Spanish')
# df = df.groupby(['FECHA DE REPORTE'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')
# new_order = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
# df = df.reindex(new_order, axis=0)
# df = df.fillna(0)