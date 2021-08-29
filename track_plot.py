import numpy as np
import plotly.graph_objects as go
from spacecraft import Spacecraft


def base_figure():
    """Instantiate baseline Plotly Geo figure."""
    fig = go.Figure(go.Scattergeo())
    fig.update_geos(
        #resolution=50,
        showcoastlines=True,
        coastlinecolor='#919191',
        showland=True,
        landcolor='#787878',
        showocean=True,
        oceancolor='black',
        showcountries=True,
        countrycolor='#919191',
        showlakes=False,
        visible=False
    )
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        showlegend=False,
        dragmode=False,
        paper_bgcolor='black',
    )
    return fig


def add_track(fig, times, lat, lon, alt):
    """Add ground track to Plotly Geo figure."""
    fmt_times = [x.strftime(r'%Y-%j %H:%M:%Sz') for x in times]
    fig.add_trace(
        go.Scattergeo(
            lat = lat,
            lon = lon,
            customdata=np.c_[fmt_times, alt],
            mode = 'lines',
            line = dict(color='#ffed78'),
            hovertemplate='<br>'.join([
                'Time: %{customdata[0]}',
                'Latitude: %{lat:.2f}\u00B0',
                'Longitude: %{lon:.2f}\u00B0',
                'Altitude: %{customdata[1]:.0f} km<extra></extra>'
            ]),
        )
    )
    return fig


def add_spacecraft(fig, name, lat, lon):
    """Add spacecraft marker to Plotly Geo figure."""
    for symbol in ['arrow-left', 'arrow-right', 'circle']:
        hover_name = None
        if symbol == 'circle':
            hover_name = name + '<extra></extra>'
        fig.add_trace(
            go.Scattergeo(
                lat = lat,
                lon = lon,
                mode='markers',
                marker_symbol=symbol,
                marker_line_color='black',
                marker_color='#ffed78',
                hovertemplate=hover_name,
                marker_line_width=2,
                marker_size=15,
            )
        )
    return fig


def add_stations(fig, stations):
    """Add ground station markers to Plotly Geo figure."""
    for name, loc in stations.items():
        for symbol in ['arrow-up', 'triangle-sw']:
            hover_name = None
            if symbol == 'triangle-sw':
                hover_name = '<br>'.join([
                    f'<b>{name}</b>',
                    f'Latitude: {loc["Lat"]:.2f}\u00B0',
                    f'Longitude: {loc["Lon"]:.2f}\u00B0',
                    f'Altitude: {loc["Alt"]:.0f} km<extra></extra>'
                ])
            fig.add_trace(
                go.Scattergeo(
                    lat = [loc['Lat']],
                    lon = [loc['Lon']],
                    mode='markers',
                    marker_symbol=symbol,
                    marker_line_color='white',
                    marker_color='black',
                    hovertemplate=hover_name,
                    marker_line_width=2,
                    marker_size=15,
                )
            )
    return fig


def add_visibility_lines(fig, i, el_con, sc_lat, sc_lon, stations):
    """If spacecraft is in ground stations FOV, add line from spacecraft
    to station on Plotly Geo figure."""
    for _, details in stations.items():
        if details['Elevation'][i] > el_con:
            fig.add_trace(
                go.Scattergeo(
                    lat = [sc_lat, details['Lat']],
                    lon = [sc_lon, details['Lon']],
                    mode='lines',
                    line = dict(color='#32ff2b'),
                    hoverinfo='skip'
                )
            )
    return fig


def copy_fig(fig):
    """Copy a Plotly Geo figure object."""
    return go.Figure(fig)


def main():
    name = 'Cryosat 2'
    sc = Spacecraft(name, tle_file='inputs/platform.tle')
    fig = base_figure()
    fig = add_stations(fig, sc.stations)
    fig = add_track(fig, sc.times, sc.lat, sc.lon, sc.alt)
    fig = add_spacecraft(fig, name, sc.lat[:1], sc.lon[:1])
    fig.show()
    #print(sc.passes)


if __name__ == '__main__':
    main()