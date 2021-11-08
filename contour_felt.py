import pandas as pd
from pyproj import Proj, transform, Transformer
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as feature
import requests

func = Transformer.from_crs("EPSG:4236", "EPSG:2193")


def mytran(lat, lon):
    return func.transform(lat, lon)

json = requests.get("http://api.geonet.org.nz/intensity?type=reported&publicID=2016p858000").json()
lon, lat = [],[]

extracted = json['features'][2]['properties']['count_mmi']
counts = json['features'][2]['properties']['count']
weighted_av = [int(i[0]) * i[1] for i in extracted.items()]
weighted_val = []
for a in json['features']:
    total_count = a['properties']['count']
    list_of_vals  = [int(i[0]) * i[1] for i in a['properties']['count_mmi'].items()]
    weighted_val.append((a['geometry']['coordinates'][0] ,a['geometry']['coordinates'][1], sum(list_of_vals) / total_count))
df = pd.DataFrame(weighted_val, columns = ['longitude','latitude', 'count'])

df["northing"], df["easting"] = mytran(df.latitude.tolist(), df.longitude.tolist())
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df = df.dropna(subset=['northing', 'easting'])
df = df[(df["northing"] > 4640000) & (df["northing"] < 6450000) & (df["easting"] > 880000) & (df["easting"] < 2420000)]


def round_five(x, base=5):
    return int(base * round(float(x) / base))


df["northing"] = df["northing"].apply(lambda x: round_five(x, base=5000))
df["easting"] = df["easting"].apply(lambda x: round_five(x, base=5000))

list_north = list(range(4640000, 6500000, 5000))
list_east = list(range(850000, 2450000, 5000))
grouped = df.groupby(['northing', 'easting'], as_index=False)['count'].agg('mean')
north_events, east_events = df.northing.tolist(), df.easting.tolist()
df["tuples"] = [(north_events[i], east_events[i]) for i in range(len(north_events))]

full = []
for a in list_north:
    full.append([(a, i) for i in list_east])

flat_list = [item for sublist in full for item in sublist]

blank_df = pd.DataFrame(flat_list, columns=["n", "e"])
blank_df["tuples"] = [(i[0], i[1]) for i in flat_list]
grouped = df.groupby("tuples", as_index = False)['count'].agg('mean')
countdf = grouped[["tuples", "count"]]

indexed = blank_df.set_index("tuples")
countdf_ind = countdf.set_index("tuples")
banana = pd.concat([indexed, countdf_ind])
banana['count'] = banana['count'].fillna(0)

df_banana = banana.groupby(banana.index).last()
counts = df_banana.sort_values(by=['n', 'e'])['count'].tolist()

for ind, val in enumerate(counts):
    if val == 0:
        counts[ind] = -1

zc_new = np.ndarray((len(list_north), len(list_east)))
for a in range(0, len(list_north)):
    for b in range(0, len(list_east)):
        zc_new[a][b] = counts[b + a * len(list_east)]

from matplotlib.cm import ScalarMappable
import matplotlib.pyplot as plt

levels_array = list(range(0, 11, 1))
levels = 10
vmin = 0
vmax = 10


level_boundaries = np.linspace(vmin, vmax, levels + 1)

cbarticks = np.arange(0, 100, 1)

fig = plt.figure(figsize=(15, 15))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_title("M3 + <100 km deep EQ density per 10 sq km - Geonet catalog", fontsize=25, pad=10)

ax.set_extent([165, 180, -48, -33], crs=ccrs.PlateCarree())

cf = plt.contourf(list_east, list_north, zc_new, levels=levels_array, vmin=vmin, vmax=vmax, alpha = 0.8, cmap = 'gist_heat_r', transform= ccrs.epsg(2193), extend = 'both')
ax.coastlines(linewidth=0.5, color='black')

cb = fig.colorbar(
    ScalarMappable(norm=cf.norm, cmap=cf.cmap),
    ticks=range(vmin, vmax + 1, 10),
    boundaries=level_boundaries,
    values=(level_boundaries[:-1] + level_boundaries[1:]) / 2,fraction=0.046, pad=0.01
)
ax.add_feature(feature.OCEAN, zorder=0)
ax.add_feature(feature.LAND, zorder=0)
cb.ax.tick_params(labelsize=15)
plt.tight_layout()
plt.savefig("felt_kai.png",  bbox_inches = "tight")