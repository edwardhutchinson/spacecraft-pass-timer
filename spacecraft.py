import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pyorbital.orbital import Orbital


class Spacecraft:
    def __init__(self, spacecraft_name, tle_file=None, **kwargs):
        """Instantiate OrbitalData class."""
        self._set_kwargs(**kwargs)
        self.name = spacecraft_name
        self.orb = Orbital(self.name, tle_file=tle_file)
        self.T = timedelta(days=1/self.orb.tle.mean_motion)
        self._set_stations()  # get station info. from file
        self._get_ground_track()  # calculate ground track
        self._get_pass_data()  # calculate pass info.


    def _set_stations(self):
        """Ingest ground station data from .json file only for now."""
        self.stations = None
        if self.stations_from.lower() == 'json':
            self.stations = json.load(open('inputs/ground_stations.json', 'r'))


    def _get_ground_track(self, start_time=datetime.utcnow()):
        """Get lon, lat, alt."""
        #orbit_period = timedelta(days=1/self.orb.tle.mean_motion)
        array_length = self.duration / self.resolution
        #array_length = orbit_period / self.resolution
        self.times = np.arange(array_length) * self.resolution + start_time
        self.lon, self.lat, self.alt = self.orb.get_lonlatalt(self.times)


    def _get_pass_data(self):
        """Calculates spacecraft pass timings based elevation constraint w.r.t. each
        ground station."""
        if self.stations is None:
            return None
        passes = []
        for station, loc in self.stations.items():
            _az, _el = self.orb.get_observer_look(self.times, loc['Lon'], loc['Lat'], loc['Alt'])
            self.stations[station]['Azimuth'] = _az  # add azimuth to station info.
            self.stations[station]['Elevation'] = _el  # add elevation to station info.
            i_valid_horizon = np.where(_el > self.elevation_constraint)  # remove non-pass values
            if i_valid_horizon[0].shape[0] < 1:
                continue
            az = _az[i_valid_horizon]
            el = _el[i_valid_horizon]
            t = self.times[i_valid_horizon]
            t_shift = np.roll(t, 1)  # shift all times by 1 in array
            new_pass = t - t_shift != self.resolution  # same pass if: times - roll == resolution
            pass_index = np.cumsum(new_pass)
            self.stations[station]['pass_index'] = pass_index
            for i in np.arange(1, pass_index.max()+1):
                pass_times = np.where(pass_index == i)
                passes.append({'Station': station,
                               'AOS': t[pass_times][0],
                               'LOS': t[pass_times][-1],
                               'Max.El': el[pass_times].max()})
        self.passes = pd.DataFrame.from_dict(sorted(passes, key=lambda x: x['AOS']))


    def _set_kwargs(self, **kwargs):
        """Update model defaults if required."""
        if 'resolution' in kwargs:
            self.resolution = kwargs['resolution']
        else:
            self.resolution = timedelta(seconds=10)
        if 'duration' in kwargs:
            self.duration = kwargs['duration']
        else:
            self.duration = timedelta(hours=24*7)
        if 'stations_from' in kwargs:
            self.stations_from = kwargs['stations_from']
        else:
            self.stations_from = 'json'
        if 'elevation_constraint' in kwargs:
            self.elevation_constraint = kwargs['elevation_constraint']
        else:
            self.elevation_constraint = 5


def main():
    x = Spacecraft('Cryosat 2', 'inputs/platform.tle')  # testing
    print(x.times[0], x.lon[0], x.lat[0])
    print(x.orb.tle.line1)


if __name__ == '__main__':
    main()
