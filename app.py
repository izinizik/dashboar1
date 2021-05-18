import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

df=pd.read_excel('elektrownie_pl.xlsx', sheet_name='elektrownie')

countries = df['kraj'].unique()
initial_countries = ['Belgia', 'Dania', 'Finlandia', 'Francja', 'Hiszpania', 'Indie', 'Irlandia',
                     'Kanada', 'Korea Południowa', 'Meksyk', 'Niemcy', 'Polska', 'Portugalia',
                     'Rosja', 'Szwecja', 'USA', 'Wielka Brytania', 'Arabia Saudyjska',
                     'Chiny', 'Czechy', 'Grecja', 'Iran', 'Izrael', 'Japonia', 
                     'Kazachstan', 'Pakistan', 'Turcja', 'Włochy', 'Afghanistan',
                     'Austria', 'Białoruś', 'Chorwacja', 'Holandia', 'Irak', 
                     'Norwegia','Ukraina', 'Szwajcaria', 'Korea Północna']

color_map = {'(?)':'black', 'Biomasa':'#33a02c', 'Kogeneracja':'#01665e', 'Energia słoneczna':'#fd8d3c', 'Gaz ziemny':'#662506',
       'Energia geotermalna':'#e31a1c', 'Energia jądrowa':'#c51b7d', 'Odpady':'#4a1486', 'Olej opałowy':'#a6611a',
       'Inne':'#e9a3c9', 'Koks ponaftowy':'#999999', 'Szczytowo-pompowa':'#5ab4ac', 'Fale i pływy':'#0c2c84',
       'Węgiel':'#404040', 'Wiatr':'#abd9e9', 'Woda':'#2c7bb6'}
bg_color = '#132639'
font_color = '#bdbdbd'
app = dash.Dash(__name__)
server = app.server

SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '27rem',
    'padding': '2rem 1rem',
}

CONTENT_STYLE = {
    'margin-left': '28rem',
    'margin-right': '0rem',
    'padding': '2rem 1rem',
    'display':'inline-block'
}

DROPDOWN_STYLE = {
    'background-color': 'black'
}

sidebar = html.Div([
        html.H3('Energetyka w świecie'),
        html.Hr(),
        html.P(
            'Rozkład elektrowni według krajów oraz mocy zainstalowanej', className='lead'
        ),
          dbc.FormGroup([
                dbc.Label('Wybierz kraj'),
                dcc.Dropdown(id='country',
                             placeholder='Wybierz kraj',
                             options=[{'label': i, 'value': i} for i in countries],
                             value=initial_countries,
                             multi=True,
                             className="custom-dropdown"
                           ),
            ]),
        html.Hr(),
        dbc.FormGroup([
                dbc.Label('Kliknij w wybraną elektrownię aby uzyskać więcej informacji'),
                dcc.Markdown(id='plant_summary')
            ]),
        html.Hr(),
            html.A('Źródło danych', href='https://datasets.wri.org/dataset/globalpowerplantdatabase', target="_blank")          
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([
    dcc.Graph(id='map',clickData={'points': [{'hovertext': 'EC PKN Orlen'}]}),
    dcc.Graph(id='fig')],style=CONTENT_STYLE)

app.layout = html.Div([sidebar, content])


@app.callback(
    Output('map', 'figure'),
    Output('fig', 'figure'),
    Input('country', 'value'))
def update_map(countries):    
    dff = df[df.kraj.isin(countries)]
    map_scatter = px.scatter_mapbox(dff, lat='lat', lon='lon',
                        hover_name='nazwa', hover_data=['kraj', 'paliwo1'],
                        color='paliwo1',zoom=1.3,
                        center = {'lat': 45, 'lon' :-25},opacity = 0.8,
                        color_discrete_map=color_map,
                        mapbox_style='carto-darkmatter',
                        labels = {'paliwo1': 'Rodzaj paliwa', 'lon':'Długość geograficzna', 
                                  'lat':'Szerokość geograficzna','kraj':'Kraj', 'moc_mw': 'Moc (MW)'},
                        size = 'moc_mw')
    map_scatter.update_layout(
        font_color=font_color,
        paper_bgcolor=bg_color,
        width=1200, height=450,
        margin=go.layout.Margin(l=0, r=0, t=0, b=0),
        legend=dict( title= None, orientation='h', y=1.01, yanchor='top', x=0.5, xanchor='center')
    )
    grouped = dff.groupby(['kraj','paliwo1']).agg({'moc_mw': 'sum'}).reset_index()
    grouped['all'] = ''
    fig = px.treemap(grouped,
                path=['all','kraj','paliwo1'],
                values='moc_mw',
                color='paliwo1',
                color_discrete_map=color_map,
            )
    fig.data[0].hovertemplate = '%{parent}<br>%{label}<br>Moc (MW)=%{value}'
    fig.update_layout(
        title='Wybrane kraje według sumarycznej mocy',
        paper_bgcolor=bg_color,
        font_color=font_color,
        hovermode='x',width=1200, height=450
    )
    return map_scatter, fig
  
  @app.callback(dash.dependencies.Output('plant_summary', 'children'),
              [dash.dependencies.Input('map', 'clickData')])
def update_summary(click_Data):
    plant_name  = click_Data['points'][0]['hovertext']
    source = df[df['nazwa'] == plant_name]['źródło'].iloc[0]
    capacity_mw = df[df['nazwa'] == plant_name]['moc_mw'].iloc[0]
    country = df[df['nazwa'] == plant_name]['kraj'].iloc[0]
    fuel = df[df['nazwa'] == plant_name]['paliwo1'].iloc[0]
    url = df[df['nazwa'] == plant_name]['url'].iloc[0]
   
    update = f'''
                    **Podsumowanie dla *{plant_name}*:**
                    - Kraj: {country}
                    - Moc (MW): {capacity_mw}
                    - Główne paliwo: {fuel}
                    - Więcej informacji: [{source}]({url})
                    
                    
                    
                    **Uwaga**: nan oznacza brak informacji w bazie
                    '''
    return update
  
  if __name__ == '__main__':
    app.run_server(debug=True)
