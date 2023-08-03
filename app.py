# -*- coding: utf-8 -*-
"""
Gestion de Reportes Tecnonorte v.3.5.0
Created on Wed Feb  9 12:33:55 2022
@author: Ing.Leander Perez

Esta obra está bajo una Licencia Creative Commons 
Atribución-NoComercial-SinDerivadas 4.0 Internacional.
(CC by-nc-nd)
https://creativecommons.org/licenses/by-nc-nd/4.0/deed.es
"""

from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash_auth
# import os
# import locale
import passwords
# locale.setlocale(locale.LC_ALL,'es_ES.UTF-8')



#%% Procesamiento de datos

# RM22 = os.listdir('//192.168.123.252/Compartida/24 OPERACIONES/REFERENCIAS RM/RM22')
# RM23 = os.listdir('//192.168.123.252/Compartida/24 OPERACIONES/REFERENCIAS RM/RM23')

bitacoras = pd.read_excel('Consol.xlsx')
bitacoras['FECHA DE REPORTE'] = pd.to_datetime(bitacoras['FECHA DE REPORTE'], format='%d-%m-%Y')
bitacoras['RECARGA DE REFRIGERANTE (KG)'] = bitacoras['RECARGA DE REFRIGERANTE (KG)'].replace(',', '.', regex=True)
bitacoras['RECARGA DE REFRIGERANTE (KG)'] = bitacoras['RECARGA DE REFRIGERANTE (KG)'].astype(float)

reportes = bitacoras.groupby('CLIENTE')['SUCURSAL'].value_counts().rename('Reportes')
reportes = reportes.reset_index()

refrigerante = bitacoras.groupby(['CLIENTE', 'SUCURSAL'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')
refrigerante = refrigerante.reset_index()

locaciones = pd.read_excel('Locations.xlsx')
locaciones = locaciones.merge(reportes, how='outer')
locaciones = locaciones.merge(refrigerante, how='outer')
locaciones =locaciones.dropna(0)
# locaciones = locaciones.fillna(0)

Ingeniero = bitacoras['INGENIERO DE SERVICIO'].value_counts().rename('Ingeniero')

meses = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
# template = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]

#%% Autenticación
app = Dash(external_stylesheets=[dbc.themes.SOLAR])
server = app.server

VALID_USERNAME_PASSWORD_PAIRS = passwords.keys 
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

#%% Funciones
def Mapbox(df, Color):
    
    fig = px.scatter_mapbox(df, lat="Lat", lon="Lon", 
                            hover_name='SUCURSAL', 
                            hover_data=["Reportes", "Refrigerante"],
                            color= Color, 
                            size='Reportes', 
                            zoom=5, height=522,
                            template='plotly')
    fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def Reportes(df, col):
    fig = px.bar(df, df["index"], df["Reportes"],
                 hover_data=['index', 'Reportes'], color='Reportes',
                 labels={'index': col},
                 template='ggplot2')
    fig.update_layout(height=245, margin={'l': 10, 'b': 0, 'r': 10, 't': 10})
    return fig

def Reportes4Mes(b):
    b['FECHA DE REPORTE'] = b['FECHA DE REPORTE'].dt.month_name(locale = 'Spanish')
    df = b.groupby(['FECHA DE REPORTE']).size().rename('REPORTES')
    new_order = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    df = df.reindex(new_order, axis=0)
    df = df.fillna(0)
    
    fig = px.line(df, x=df.index, y="REPORTES", 
                  markers=True,
                  template='seaborn')
    fig.update_layout(height=225, margin={'l': 10, 'b': 10, 'r': 60, 't': 10})
    return fig

def Year(year_selec):
    if year_selec == '2022':
        b = bitacoras.loc[(bitacoras['FECHA DE REPORTE'] >= '2022') & (bitacoras['FECHA DE REPORTE'] < '2023')]
    elif year_selec == '2023':
        b = bitacoras.loc[(bitacoras['FECHA DE REPORTE'] >= '2023')]
    else: 
        b = bitacoras
    return b

def Locaciones(b):
    r = b.groupby('CLIENTE')['SUCURSAL'].value_counts().rename('Reportes')
    r = r.reset_index()
    
    rr = b.groupby(['CLIENTE', 'SUCURSAL'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')
    rr = rr.reset_index()
    
    l = pd.read_excel('Locations.xlsx')
    l = l.merge(r, how='outer')
    l = l.merge(rr, how='outer')
    l = l.fillna(0)
    return l



#%% Layout
app.layout = html.Div([
    
    #Header
    html.Header(
        id="header",
        children=[
            
            html.Img(id="logo", src=app.get_asset_url("dash-logo.png")),
           
            html.H4(children="Gestión de Reportes - Tecnonorte"),
            html.P(
                id="description",
                children="Aplicacion para la gestion de reportes")
                ]),
    
    
    #App
    html.Div(
        id='contenedor_app', children=[
            
        html.Div([
            html.Label('Años'),
            dcc.RadioItems(
                ['2022', '2023'],
                'Linear',
                id='year',
                labelStyle={'display': 'inline-block'})],
                style={'width': '20%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label('Clientes'),
            dcc.Dropdown([*set(locaciones['CLIENTE'])],
                         id='clientes')],
                style={'width': '70%', 'float': 'right', 'display': 'inline-block'}),
        
        html.Div([
            html.Label('Sucursales'),
            dcc.Dropdown(id='sucursales', multi=True)]),
        
        html.Div([
            #html.Br(),
            html.Label('Grafico de sucursales'),
            
            html.Div([
                dcc.Graph(id="Mapbox")], 
                    style={'width': '50%', 'display': 'inline-block', 'padding': '0 20'}),
            
            html.Div([
                dbc.Tabs(
                    [
                        dbc.Tab(
                            dbc.Col([
                                dbc.Row(dcc.Graph(id='ReportesFCliente')),
                                html.Br(),
                                dbc.Row(dcc.Graph(id='ReportesFMes'))
                                ]), label="Reportes"),
                        
                        dbc.Tab(
                            dbc.Col([
                                dbc.Row(dcc.Graph(id='FugasFCliente')),
                                html.Br(),
                                dbc.Row(dcc.Graph(id='FugasFMes'))
                                ]), label="Fugas"),
                        
                        dbc.Tab(dcc.Graph(id='Visita'), label="Visitas"),
                        
                        dbc.Tab(html.Pre(id='click-data', 
                                         style={
                                             'border': 'thin lightgrey solid',
                                             'overflowY': 'scroll',
                                             'height': 400,
                                             'backgroundColor': 'rgb(31, 38, 48)'
                                         }), label="Información")
                    ]
                )],
                style={'display': 'inline-block', 'width': '49%', 'float': 'right'})
        ]),
        
        html.Div([
        #html.Br(),
        html.Label('Rango de meses'),
        dcc.RangeSlider(
            min=1,
            max=12,
            step=None,
            marks=meses,
            value=[1, 12],
            allowCross=False,
            id='range_slider'),
        ]),
        
        html.Br(),
        dash_table.DataTable(
            
            page_size=15,
            style_table={'overflowX': 'auto'},
            style_header={
            'backgroundColor': 'rgb(37, 46, 63)',
            'color': 'rgb(127, 175, 223)',
            'textAlign': 'left'},
            style_data={
            'backgroundColor': 'rgb(31, 38, 48)',
            'color': 'rgb(127, 175, 223)',
            'height': 'auto',
            'lineHeight': '15px',
            'textAlign': 'left'},
            id='table'),
        
        dcc.Download(id="download")
        
        ]),
    
    #Footer
    html.Div([
        html.Footer([
            html.A(
                html.P("Desarrollado por: Ing. Leander Pérez"),
                href="https://wa.me/584241200737"),
            ]),
        html.Br(),
        ]),
    ], style={'backgroundColor': 'rgb(31, 38, 48)'})
                             
#%% Callbacks

@app.callback(
    Output('clientes', 'options'),
    Input('year', 'value'))
def clientes_options(year_selec):
    b = Year(year_selec)
    return [*set(b['CLIENTE'])]

@app.callback(
    Output('sucursales', 'options'),
    Input('clientes', 'value'))
def sucursales_options(cliente_seleccionado):
    return [*set(locaciones['SUCURSAL'][locaciones['CLIENTE']==cliente_seleccionado])]

@app.callback(
    Output('Mapbox', 'figure'),
    Input('year', 'value'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'),
    Input('range_slider', 'value'))
def update_Mapbox(year_selec, cliente_seleccionado, sucursales_selec, RangeS):
    b = Year(year_selec)
    b = b.loc[(b['FECHA DE REPORTE'].dt.month >= RangeS[0]) & (b['FECHA DE REPORTE'].dt.month <= RangeS[-1])]
    l = Locaciones(b)
    if cliente_seleccionado == None:
        fig = Mapbox(l, 'CLIENTE')
    else:
        df = l[l['CLIENTE']==cliente_seleccionado]
        fig= Mapbox(df, 'SUCURSAL')
    if sucursales_selec != None:
        df2 = l[l['SUCURSAL'].isin(sucursales_selec)]
        fig= Mapbox(df2, 'SUCURSAL')
    return fig

@app.callback(
    Output('ReportesFCliente', 'figure'),
    Input('year', 'value'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'),
    Input('range_slider', 'value'))
def update_reportes(year_selec, cliente_seleccionado, sucursales_selec, RangeS):
    b = Year(year_selec)
    b = b.loc[(b['FECHA DE REPORTE'].dt.month >= RangeS[0]) & (b['FECHA DE REPORTE'].dt.month <= RangeS[-1])]
    if cliente_seleccionado == None:
        df = b.CLIENTE.value_counts().rename('Reportes')
        df = df.reset_index()
        df.dropna()
        fig = Reportes(df, 'Cliente')
    else:
        df = b[b['CLIENTE'] == cliente_seleccionado]
        df = df.SUCURSAL.value_counts().rename('Reportes')
        df = df.reset_index()
        df.dropna()
        fig = Reportes(df, 'Sucursal')
    if sucursales_selec != None:
        df = b[b['SUCURSAL'].isin(sucursales_selec)]
        df = df.SUCURSAL.value_counts().rename('Reportes')
        df = df.reset_index()
        fig = Reportes(df, 'Sucursal')
    return fig

@app.callback(
    Output('ReportesFMes', 'figure'),
    Input('year', 'value'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'),
    Input('range_slider', 'value'))
def update_reportes4mes(year_selec, cliente_seleccionado, sucursales_selec, RangeS):
    b = Year(year_selec)
    b = b.loc[(b['FECHA DE REPORTE'].dt.month >= RangeS[0]) & (b['FECHA DE REPORTE'].dt.month <= RangeS[-1])]
    if cliente_seleccionado == None:
        fig = Reportes4Mes(b)
    else:
        df = b[b['CLIENTE'] == cliente_seleccionado]
        fig = Reportes4Mes(df)
    if sucursales_selec != None:
        fig = go.Figure()
        for sucursal in sucursales_selec:
            df = b[b['CLIENTE'] == cliente_seleccionado]
            dff = df[df['SUCURSAL'] == sucursal]
            dff['FECHA DE REPORTE'] = dff['FECHA DE REPORTE'].dt.month_name(locale = 'Spanish')
            dff = dff.groupby(['FECHA DE REPORTE']).size().rename('REPORTES')
            new_order = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            dff = dff.reindex(new_order, axis=0)
            dff = dff.fillna(0)
            
            fig.add_trace(go.Scatter(x=dff.index, y=dff, 
                                  mode='lines+markers', name=sucursal))
            fig.update_layout(height=225, margin={'l': 10, 'b': 10, 'r': 60, 't': 10})
    return fig

@app.callback(
    Output('FugasFCliente', 'figure'),
    Input('year', 'value'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'),
    Input('range_slider', 'value'))
def update_fugas(year_selec, cliente_seleccionado, sucursales_selec, RangeS):
    b = Year(year_selec)
    b = b.loc[(b['FECHA DE REPORTE'].dt.month >= RangeS[0]) & (b['FECHA DE REPORTE'].dt.month <= RangeS[-1])]
    if cliente_seleccionado == None:
        df = Locaciones(b)
        df = df.groupby(['CLIENTE'])['Refrigerante'].sum().reset_index().sort_values(by='Refrigerante', ascending=False)
        fig = px.bar(df, df.CLIENTE, df.Refrigerante,
                     hover_data=['CLIENTE', 'Refrigerante'], color='Refrigerante',
                     template='ggplot2')
        fig.update_layout(height=245, margin={'l': 10, 'b': 0, 'r': 10, 't': 10})
    else:
        df = b[b['CLIENTE'] == cliente_seleccionado]
        df = df.groupby(['SUCURSAL'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')\
            .reset_index().sort_values(by='Refrigerante', ascending=False)
        fig = px.bar(df, df.SUCURSAL, df.Refrigerante,
                     hover_data=['SUCURSAL', 'Refrigerante'], color='Refrigerante',
                     template='ggplot2')
        fig.update_layout(height=245, margin={'l': 10, 'b': 0, 'r': 10, 't': 10})
    if sucursales_selec != None:
        df = b[b['SUCURSAL'].isin(sucursales_selec)]
        df = df.groupby(['SUCURSAL'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')\
            .reset_index().sort_values(by='Refrigerante', ascending=False)
        fig = px.bar(df, df.SUCURSAL, df.Refrigerante,
                     hover_data=['SUCURSAL', 'Refrigerante'], color='Refrigerante',
                     template='ggplot2')
        fig.update_layout(height=245, margin={'l': 10, 'b': 0, 'r': 10, 't': 10})
    return fig

@app.callback(
    Output('FugasFMes', 'figure'),
    Input('year', 'value'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'),
    Input('range_slider', 'value'))
def update_fugas4mes(year_selec, cliente_seleccionado, sucursales_selec, RangeS):
    b = Year(year_selec)
    b = b.loc[(b['FECHA DE REPORTE'].dt.month >= RangeS[0]) & (b['FECHA DE REPORTE'].dt.month <= RangeS[-1])]
    if cliente_seleccionado == None:
        
        b['FECHA DE REPORTE'] = b['FECHA DE REPORTE'].dt.month_name(locale = 'Spanish')
        df = b.groupby(['FECHA DE REPORTE'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')
        new_order = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        df = df.reindex(new_order, axis=0)
        df = df.fillna(0)
        fig = px.line(df, x=df.index, y="Refrigerante", 
                      markers=True,
                      template='seaborn')
        fig.update_layout(height=225, margin={'l': 10, 'b': 10, 'r': 60, 't': 10})
        
    else:
        b = b[b['CLIENTE'] == cliente_seleccionado]
        b['FECHA DE REPORTE'] = b['FECHA DE REPORTE'].dt.month_name(locale = 'es_ES')
        df = b.groupby(['FECHA DE REPORTE'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')
        new_order = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        df = df.reindex(new_order, axis=0)
        df = df.fillna(0)
        fig = px.line(df, x=df.index, y="Refrigerante", 
                      markers=True,
                      template='seaborn')
        fig.update_layout(height=225, margin={'l': 10, 'b': 10, 'r': 60, 't': 10})
        
    if sucursales_selec != None:
        fig = go.Figure()
        for sucursal in sucursales_selec:
            df = b[b['CLIENTE'] == cliente_seleccionado]
            dff = df[df['SUCURSAL'] == sucursal]
            # dff['FECHA DE REPORTE'] = dff['FECHA DE REPORTE'].dt.month_name(locale = 'Spanish')
            dff = dff.groupby(['FECHA DE REPORTE'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')
            new_order = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            dff = dff.reindex(new_order, axis=0)
            dff = dff.fillna(0)
            
            fig.add_trace(go.Scatter(x=dff.index, y=dff, 
                                  mode='lines+markers', name=sucursal))
            fig.update_layout(height=225, margin={'l': 10, 'b': 10, 'r': 60, 't': 10})
    return fig

@app.callback(
    Output('Visita', 'figure'),
    Input('year', 'value'),
    Input('clientes', 'value'),
    Input('Mapbox', 'clickData'),
    Input('range_slider', 'value'))
def update_Visitas(year_selec, cliente_seleccionado, clickData, RangeS):
    b = Year(year_selec)
    b = b.loc[(b['FECHA DE REPORTE'].dt.month >= RangeS[0]) & (b['FECHA DE REPORTE'].dt.month <= RangeS[-1])]
    if cliente_seleccionado == None:
        df = b['TIPO DE FALLA'].value_counts().rename('Visitas')
        fig = px.pie(df, values='Visitas', names=df.index,
                     title= 'Motivos de la visita',
                     labels={'index': 'Motivo de visita'},
                     #template='seaborn',
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_traces(textposition='inside', textinfo='percent')
        fig.update_layout(height=400, margin={'l': 20, 'b': 20, 'r': 0, 't': 50})
    else:
        df = b[b['CLIENTE'] == cliente_seleccionado]
        dff = df['TIPO DE FALLA'].value_counts().rename('Visitas')
        fig = px.pie(dff, values='Visitas', names=dff.index,
                     title= f'Motivos de la visita a {cliente_seleccionado}',
                     labels={'index': 'Motivo de visita'},
                     #template='seaborn',
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_traces(textposition='inside', textinfo='percent')
        fig.update_layout(height=400, margin={'l': 20, 'b': 20, 'r': 0, 't': 50})
    if clickData != None:
        sucursal = clickData['points'][0]['hovertext']
        df = b[b['CLIENTE'] == cliente_seleccionado]
        df = b[b['SUCURSAL'] == sucursal]
        dff = df['TIPO DE FALLA'].value_counts().rename('Visitas')
        fig = px.pie(dff, values='Visitas', names=dff.index,
                     title= f'Motivos de la visita a {cliente_seleccionado} - {sucursal}',
                     labels={'index': 'Motivo de visita'},
                     #template='seaborn',
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_traces(textposition='inside', textinfo='percent')
        fig.update_layout(height=400, margin={'l': 20, 'b': 20, 'r': 0, 't': 50})
    return fig
    
@app.callback(
    Output('table', 'data'),
    Input('year', 'value'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'),
    Input('range_slider', 'value'),
    Input('table', 'active_cell'))
def update_table(year_selec, cliente_seleccionado, sucursales_selec, RangeS, active_cell):
    b = Year(year_selec)
    b = b.loc[(b['FECHA DE REPORTE'].dt.month >= RangeS[0]) & (b['FECHA DE REPORTE'].dt.month <= RangeS[-1])]
    b['FECHA DE REPORTE'] = b['FECHA DE REPORTE'].dt.strftime('%d/%m/%Y')
    if cliente_seleccionado == None:
        b
    else:
        b = b[b['CLIENTE'] == cliente_seleccionado]
    if sucursales_selec != None:
        b = b[b['SUCURSAL'].isin(sucursales_selec)]
    return b.to_dict('records')


# @app.callback(
#     Output('download', 'data'),
#     Input('year', 'value'),
#     Input('clientes', 'value'),
#     Input('sucursales', 'value'),
#     Input('range_slider', 'value'),
#     Input('table', 'active_cell'),
#     prevent_initial_call=True)
# def update_descarga(year_selec, cliente_seleccionado, sucursales_selec, RangeS, active_cell):
#     b = Year(year_selec)
#     b = b.loc[(b['FECHA DE REPORTE'].dt.month >= RangeS[0]) & (b['FECHA DE REPORTE'].dt.month <= RangeS[-1])]
#     b['FECHA DE REPORTE'] = b['FECHA DE REPORTE'].dt.strftime('%d/%m/%Y')
#     if cliente_seleccionado == None:
#         b
#     else:
#         b = b[b['CLIENTE'] == cliente_seleccionado]
#     if sucursales_selec != None:
#         b = b[b['SUCURSAL'].isin(sucursales_selec)]
#     if active_cell != None:
#         ods = b.iloc[active_cell['row'], active_cell['column']]
#         if ods+'.pdf' in RM22:
#             return dcc.send_file(f'//192.168.123.252/Compartida/24 OPERACIONES/REFERENCIAS RM/RM22/{ods}.pdf')
#         elif ods+'.pdf' in RM23:
#             return dcc.send_file(f'//192.168.123.252/Compartida/24 OPERACIONES/REFERENCIAS RM/RM23/{ods}.pdf')


@app.callback(
    Output('click-data', 'children'),
    Input('year', 'value'),
    Input('Mapbox', 'clickData'),
    Input('table', 'active_cell'),
    Input('range_slider', 'value'))
def display_click_data(year_selec, clickData, active_cell, RangeS):
    b = Year(year_selec)
    b = b.loc[(b['FECHA DE REPORTE'].dt.month >= RangeS[0]) & (b['FECHA DE REPORTE'].dt.month <= RangeS[-1])]
    b['FECHA DE REPORTE'] = b['FECHA DE REPORTE'].dt.strftime('%d/%m/%Y')
    if clickData == None and active_cell == None:
        msj = (' NaN')
    else:
        sucursal = clickData['points'][0]['hovertext']
        msj = (f' Sucursal: {sucursal}')
    
    return msj


if __name__ == '__main__':
    app.run_server(debug=True)
