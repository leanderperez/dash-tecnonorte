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

from datetime import date
from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash_auth
import os
import passwords

port = int(os.environ.get("PORT", 5000))


#%% Lanzamiento de la Aplicación y Autenticación
app = Dash(
    __name__, external_stylesheets=[dbc.themes.SOLAR])

VALID_USERNAME_PASSWORD_PAIRS = passwords.keys 
auth = dash_auth.BasicAuth(
    app, VALID_USERNAME_PASSWORD_PAIRS)

#%% Procesamiento de datos
bitacoras = pd.read_excel('Consol.xlsx')
bitacoras['FECHA DE REPORTE'] = pd.to_datetime(bitacoras['FECHA DE REPORTE']).dt.date
# df['FECHA DE REPORTE'] = pd.to_datetime(df['FECHA DE REPORTE']).dt.date
# bitacoras['FECHA DE REPORTE'] = pd.to_datetime(bitacoras['FECHA DE REPORTE']).dt.month_name()
bitacoras['RECARGA DE REFRIGERANTE (KG)'] = bitacoras['RECARGA DE REFRIGERANTE (KG)'].replace(',', '.', regex=True)
bitacoras['RECARGA DE REFRIGERANTE (KG)'] = bitacoras['RECARGA DE REFRIGERANTE (KG)'].astype(float)


#%% Funciones
def Mapbox(df, color):
    
    fig = px.scatter_mapbox(df, lat="Lat", lon="Lon", 
                            hover_name='SUCURSAL', 
                            hover_data=["Reportes", "Refrigerante"],
                            color= color, 
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

def Fugas(df):
    fig = px.bar(df, df["index"], df.Refrigerante,
                hover_data=['index', 'Refrigerante'], color='Refrigerante',
                template='ggplot2')
    fig.update_layout(height=245, margin={'l': 10, 'b': 0, 'r': 10, 't': 10})
    return

def Reportes4Mes(df):
    df['FECHA DE REPORTE'] = pd.to_datetime(df['FECHA DE REPORTE']).dt.month_name()
    df = df.groupby(['FECHA DE REPORTE']).size().rename('REPORTES')
    df = df.fillna(0)
    
    fig = px.line(df, x=df.index, y="REPORTES", 
                  markers=True,
                  template='seaborn')
    fig.update_layout(height=225, margin={'l': 10, 'b': 10, 'r': 60, 't': 10})
    return fig


def Locaciones(bitacora):
    reportes = bitacora.groupby('CLIENTE')['SUCURSAL'].value_counts().rename('Reportes')
    reportes = reportes.reset_index()
    
    refrigerante = bitacora.groupby(['CLIENTE', 'SUCURSAL'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')
    refrigerante = refrigerante.reset_index()
    
    locaciones = pd.read_excel('Locations.xlsx')
    locaciones = locaciones.merge(reportes, how='outer')
    locaciones = locaciones.merge(refrigerante, how='outer')
    locaciones = locaciones.fillna(0)
    return locaciones



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
            html.Label('Rango de Fecha'),
            dcc.DatePickerRange(
                id='date',
                # start_date_placeholder_text="Inicio",
                end_date_placeholder_text="Fin",
                calendar_orientation='horizontal',
                start_date=date(2022, 1, 1),
                style={'width': '30%', 'float': 'left', 'display': 'inline-block'}
                )]),
        
        html.Div([
            html.Label('Clientes'),
            dcc.Dropdown([*set(Locaciones(bitacoras)['CLIENTE'])],
                         id='clientes')],
                style={'width': '70%', 'float': 'right', 'display': 'inline-block'}),
        
        html.Div([
            html.Label('Sucursales'),
            dcc.Dropdown(id='sucursales', multi=True)]),
        
        html.Div([
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


# %% Callbacks

@app.callback(
    Output('sucursales', 'options'),
    Input('clientes', 'value'))
def sucursales_options(cliente_seleccionado):
    locaciones=Locaciones(bitacoras)
    return [*set(locaciones['SUCURSAL'][locaciones['CLIENTE']==cliente_seleccionado])]

@app.callback(
    Output('Mapbox', 'figure'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'))
def update_Mapbox(cliente_seleccionado, sucursales_selec):
    locaciones = Locaciones(bitacoras)
    if cliente_seleccionado == None:
        fig = Mapbox(locaciones, 'CLIENTE')
    else:
        df = locaciones[locaciones['CLIENTE']==cliente_seleccionado]
        fig= Mapbox(df, 'SUCURSAL')
    if sucursales_selec != None:
        df2 = locaciones[locaciones['SUCURSAL'].isin(sucursales_selec)]
        fig= Mapbox(df2, 'SUCURSAL')
    return fig

@app.callback(
    Output('ReportesFCliente', 'figure'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'))
def update_reportes(cliente_seleccionado, sucursales_selec):
    if cliente_seleccionado == None:
        df = bitacoras.CLIENTE.value_counts().rename('Reportes')
        df = df.reset_index()
        df.dropna()
        fig = Reportes(df, 'Cliente')
    else:
        df = bitacoras[bitacoras['CLIENTE'] == cliente_seleccionado]
        df = df.SUCURSAL.value_counts().rename('Reportes')
        df = df.reset_index()
        df.dropna()
        fig = Reportes(df, 'Sucursal')
    if sucursales_selec != None:
        df = bitacoras[bitacoras['SUCURSAL'].isin(sucursales_selec)]
        df = df.SUCURSAL.value_counts().rename('Reportes')
        df = df.reset_index()
        fig = Reportes(df, 'Sucursal')
    return fig

@app.callback(
    Output('ReportesFMes', 'figure'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'))
def update_reportes4mes(cliente_seleccionado, sucursales_selec):
    if cliente_seleccionado == None:
        fig = Reportes4Mes(bitacoras)
    else:
        df = bitacoras[bitacoras['CLIENTE'] == cliente_seleccionado]
        fig = Reportes4Mes(df)
    if sucursales_selec != None:
        fig = go.Figure()
        for sucursal in sucursales_selec:
            df = bitacoras[bitacoras['CLIENTE'] == cliente_seleccionado]
            dff = df[df['SUCURSAL'] == sucursal]
            dff['FECHA DE REPORTE'] = dff['FECHA DE REPORTE'].dt.month_name()
            dff = dff.groupby(['FECHA DE REPORTE']).size().rename('REPORTES')
            dff = dff.fillna(0)
            
            fig.add_trace(go.Scatter(x=dff.index, y=dff, 
                                  mode='lines+markers', name=sucursal))
            fig.update_layout(height=225, margin={'l': 10, 'b': 10, 'r': 60, 't': 10})
    return fig

@app.callback(
    Output('FugasFCliente', 'figure'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'))
def update_fugas(cliente_seleccionado, sucursales_selec):
    if cliente_seleccionado == None:
        df = Locaciones(bitacoras)
        df = df.groupby(['CLIENTE'])['Refrigerante'].sum().reset_index().sort_values(by='Refrigerante', ascending=False)
        fig = px.bar(df, df.CLIENTE, df.Refrigerante,
                     hover_data=['CLIENTE', 'Refrigerante'], color='Refrigerante',
                     template='ggplot2')
        fig.update_layout(height=245, margin={'l': 10, 'b': 0, 'r': 10, 't': 10})
    else:
        df = bitacoras[bitacoras['CLIENTE'] == cliente_seleccionado]
        df = df.groupby(['SUCURSAL'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')\
            .reset_index().sort_values(by='Refrigerante', ascending=False)
        fig = px.bar(df, df.SUCURSAL, df.Refrigerante,
                     hover_data=['SUCURSAL', 'Refrigerante'], color='Refrigerante',
                     template='ggplot2')
        fig.update_layout(height=245, margin={'l': 10, 'b': 0, 'r': 10, 't': 10})
    if sucursales_selec != None:
        df = bitacoras[bitacoras['SUCURSAL'].isin(sucursales_selec)]
        df = df.groupby(['SUCURSAL'])['RECARGA DE REFRIGERANTE (KG)'].sum().rename('Refrigerante')\
            .reset_index().sort_values(by='Refrigerante', ascending=False)
        fig = px.bar(df, df.SUCURSAL, df.Refrigerante,
                     hover_data=['SUCURSAL', 'Refrigerante'], color='Refrigerante',
                     template='ggplot2')
        fig.update_layout(height=245, margin={'l': 10, 'b': 0, 'r': 10, 't': 10})
    return fig

@app.callback(
    Output('FugasFMes', 'figure'),
    Input('clientes', 'value'),
    Input('sucursales', 'value'))
def update_fugas4mes(cliente_seleccionado, sucursales_selec):
    b = Year(b = b.loc[(b['FECHA DE REPORTE'].dt.month >[0]) & (b['FECHA DE REPORTE'].dt.month <[-1])])
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
            dff = dff.fillna(0)
            
            fig.add_trace(go.Scatter(x=dff.index, y=dff, 
                                  mode='lines+markers', name=sucursal))
            fig.update_layout(height=225, margin={'l': 10, 'b': 10, 'r': 60, 't': 10})
    return fig

@app.callback(
    Output('Visita', 'figure'),
    Input('clientes', 'value'),
    Input('Mapbox', 'clickData'))
def update_Visitas(cliente_seleccionado, clickData):
    if cliente_seleccionado == None:
        df = bitacoras['TIPO DE FALLA'].value_counts().rename('Visitas')
        fig = px.pie(df, values='Visitas', names=df.index,
                     title= 'Motivos de la visita',
                     labels={'index': 'Motivo de visita'},
                     #template='seaborn',
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_traces(textposition='inside', textinfo='percent')
        fig.update_layout(height=400, margin={'l': 20, 'b': 20, 'r': 0, 't': 50})
    else:
        df = bitacoras[bitacoras['CLIENTE'] == cliente_seleccionado]
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
        df = bitacoras[bitacoras['CLIENTE'] == cliente_seleccionado]
        df = bitacoras[bitacoras['SUCURSAL'] == sucursal]
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
    Input('clientes', 'value'),
    Input('sucursales', 'value'))
def update_table(cliente_seleccionado, sucursales_selec):
    df = bitacoras
    #bitacoras['FECHA DE REPORTE'] = bitacoras['FECHA DE REPORTE'].dt.strftime('%d/%m/%Y')
    if cliente_seleccionado == None:
        df
    else:
        df = df[df['CLIENTE'] == cliente_seleccionado]
    if sucursales_selec != None:
        df = df[df['SUCURSAL'].isin(sucursales_selec)]
    return df.to_dict('records')


@app.callback(
    Output('click-data', 'children'),
    Input('Mapbox', 'clickData'),
    Input('date', 'start_date'),
    Input('date', 'end_date'))
def display_click_data(clickData, start_date, end_date):
    
    if clickData == None:
        msj = [start_date, end_date]
    else:
        sucursal = clickData['points'][0]['hovertext']
        msj = (f' Sucursal: {sucursal}')
    
    return msj


if __name__ == '__main__':
    app.run_server(port=port, debug=True)
