import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import track_plot as tp

from dash.dependencies import Input, Output
from datetime import datetime, timedelta
from spacecraft import Spacecraft


def fetch_inputs():
    """Prompts user for inputs."""
    print('Enter spacecraft name as defined in TLE set, leave blank for CRYOSAT 2...')
    sc = input('->').upper()
    if sc == '':
        sc = 'CRYOSAT 2'
    print('Provide path to TLE file, leave blank to search Celestrak...')
    path = input('->')
    if path == '':
        path = None
    print('Processing...')
    return sc, path


def format_timedelta(td):
    """Returns timedelta object as string with format = 'HH:MM:SS'."""
    d = td.days
    h = td.seconds // 3600
    h += d * 24
    m = td.seconds // 60 % 60
    s = td.seconds % 3600 % 60
    return f'{h:02d}:{m:02d}:{s:02d}'


def calculate_countdowns(row):
    """Calculate the countdown to AOS/LOS and duration for each pass."""
    dur = row['LOS'] - row['AOS']
    cntd = row['AOS'] - NOW
    if cntd < timedelta(0):
        cntd = row['LOS'] - NOW
        dur = cntd
    return pd.Series([format_timedelta(dur), format_timedelta(cntd)])


def update_table(df):
    """Update pass table information."""
    df = df[df['LOS'] > NOW].copy(deep=True)
    df[['Duration', 'Countdown']] = df.apply(lambda x: calculate_countdowns(x), axis=1)
    df['on'] = df['AOS'].apply(lambda x: 1 if x < NOW else 0)  # turn on if now >= AOS
    for xos in ['AOS', 'LOS']:
        df[f'{xos} (UTC)'] = df.pop(xos).apply(lambda x: x.strftime(r'%Y-%m-%d %H:%M:%S'))
    df['Max.El (\N{DEGREE SIGN})'] = df.pop('Max.El').apply(lambda x: f'{x:{" "}>5.2f}')
    return df


def serve_layout():
    """Serve layout on each page refresh, not only when the app is started."""
    return html.Div(
        className='container',
        children=[
            dcc.Interval(
                id='interval-component-onesecond',
                interval=1*1000, # in milliseconds
                n_intervals=0
            ),
            dcc.Interval(
                id='interval-component-tensecond',
                interval=10*1000, # in milliseconds
                n_intervals=0
            ),
            html.Div(
                className='topbar',
                children=[
                    html.Div(
                        className='topbarWrapper',
                        children=[
                            html.Div(
                                className='spacecraftDetails',
                                children=[
                                    html.H1(SC.name + ' (', className='title'),
                                    html.P([SC.orb.tle.line1, html.Br(), SC.orb.tle.line1], className='title'),
                                    html.H1(')', className='title')
                                ]
                            ),
                            html.Div(
                                className='spacecraftLogo',
                                children=[
                                    html.Img(id='logo', src=app.get_asset_url('logo.png'))
                                ]
                            )
                        ]
                    ),
                    html.Div(
                        className='timeBar',
                        children=[
                            html.Div('Loading...', id='utc-clock')
                        ]
                    )
                ]
            ),
            html.Div(
                className='tableWrapper',
                children=[
                    dash_table.DataTable(
                        id='live-update-table',
                        columns=[
                            {'name': x, 'id': x, 'selectable': False}
                            for x in ['Station', 'Max.El (\N{DEGREE SIGN})', 'AOS (UTC)', 'LOS (UTC)', 'Duration', 'Countdown']
                        ] + [{'name': 'on', 'id': 'on', 'selectable': False}],
                        style_header={
                            'backgroundColor': 'black',
                            'fontWeight': 'bold',
                            'fontSize': 'large',
                            'textAlign': 'center'
                        },
                        style_cell={
                            'textAlign': 'center',
                            'backgroundColor': 'black',
                        },
                        style_data={
                            'whiteSpace': 'pre'
                        },
                        style_data_conditional=[
                            {
                                'if': {
                                    'filter_query': '{on} = 1'
                                },
                                'backgroundColor': '#32ff2b',
                                'color': 'black'
                            }
                        ],
                        style_cell_conditional=[
                            {
                                'if': {
                                    'column_id': 'on',
                                },
                                'display': 'None',
                            }
                        ],
                        data=None,
                        editable=False,
                        page_size=5
                    )
                ]
            ),
            html.Div(
                className='mapWrapper',
                children=[
                    dcc.Graph(
                        id='live-update-graph',
                        config={'displayModeBar': False}
                    )
                ]
            ),
        ]
    )


def instantiate_globals(name, tle_file):
    """Instantiate global variables on page load.

    Keyword arguments:
    name -- spacecraft name as defined in a two-line element set
    tle_file -- path to two-line element file
    
    Global variables:
    FIG -- baseline Plotly Geo map setup (inc. ground stations)
    SC -- spacecraft.Spacecraft class
    NOW -- datetime.datetime.utcnow()"""
    global FIG, NOW, SC
    SC = Spacecraft(name, tle_file=tle_file)
    NOW = datetime.utcnow()
    FIG = tp.add_stations(tp.base_figure(), SC.stations)


app = dash.Dash(__name__,
                title='Dashboard',
                update_title=None)


@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component-tensecond', 'n_intervals'))
def update_live_graph(n):
    """Updates spacecraft position, ground track and visibility lines
    every ten seconds."""
    mask_a = SC.times > NOW
    mask_b = SC.times < NOW + SC.T  # times less than one orbital period
    mask = mask_a * mask_b
    times = SC.times[mask]
    lat = SC.lat[mask]
    lon = SC.lon[mask]
    alt = SC.alt[mask]


    fig = tp.copy_fig(FIG)  # don't create from scratch
    fig = tp.add_track(fig, times, lat, lon, alt)
    fig = tp.add_spacecraft(fig, SC.name, lat[:1], lon[:1])
    i = np.where(mask_a)[0][0]  # index of first valid time
    fig = tp.add_visibility_lines(fig, i, SC.elevation_constraint,
                                  lat[0], lon[0], SC.stations)
    #fig.update_geos(center=dict(lon=lon[0]))
    return fig


@app.callback([Output('live-update-table', 'data'),
               Output('utc-clock', 'children')],
              Input('interval-component-onesecond', 'n_intervals'))
def update_live_table(n):
    """Updates pass countdowns, durations, and highlights every second."""
    global NOW
    NOW = datetime.utcnow()
    passes = update_table(SC.passes)
    return passes.to_dict('records'), html.H1(NOW.strftime(r'%Y-%m-%d %H:%M:%S UTC   (DoY %j)'))


def main():
    sc, path = fetch_inputs()  # define spacecraft and TLE from user inputs
    print(sc, path)
    instantiate_globals(sc, tle_file=path)
    app.layout = serve_layout
    app.run_server()


if __name__ == '__main__':
    main()