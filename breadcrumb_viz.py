import argparse
from lonboard import Map, ScatterplotLayer
from lonboard.basemap import CartoStyle, MaplibreBasemap
from lonboard.colormap import apply_continuous_cmap
import geopandas as gpd
import pandas as pd
import numpy as np
import seaborn as sns

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, required=True, help='Input parquet file')
parser.add_argument('-o', '--output', type=str, required=True, help='Output HTML file')
args = parser.parse_args()


def plot_data(data_to_plot, color_by='time'):
    points = ScatterplotLayer.from_geopandas(
        gpd.GeoDataFrame(
            data_to_plot,
            geometry=gpd.points_from_xy(data_to_plot.longitude, data_to_plot.latitude),
            crs='EPSG:4326'
        )
    )
    points.get_radius = 5
    points.radius_units = 'pixels'
    normed_data = data_to_plot[color_by].values.astype(float)
    normed_data = (normed_data - normed_data.min()) / (normed_data.max() - normed_data.min())
    points.get_fill_color = apply_continuous_cmap(normed_data, cmap=sns.cm.mako)

    this_map = Map(layers=[points], basemap=MaplibreBasemap(mode='interleaved', style=CartoStyle.Voyager))
    return this_map


if __name__ == '__main__':
    data = pd.read_parquet(args.input).sort_values('time').reset_index(drop=True)
    data = data.drop_duplicates(['time']).reset_index(drop=True)

    non_continuous = np.diff(data['time'].values).astype('timedelta64[s]') != 5
    trip_ends = np.where(non_continuous)[0]
    trip_starts = np.insert(trip_ends + 1, 0, 0)
    trip_ends = np.append(trip_ends, len(data) - 1)
    for i, (start, end) in enumerate(zip(trip_starts, trip_ends)):
        trip_data = data.iloc[start:end]
        if len(trip_data) == 0:
            continue
        m = plot_data(trip_data, 'altitude')
        filename = f'{trip_data["time"].iloc[0].strftime("%Y-%m-%d_%H-%M-%S")}.html'
        m.to_html(f'{args.output}/{filename}')
        print(f'Wrote {filename} with {len(trip_data)} points')
