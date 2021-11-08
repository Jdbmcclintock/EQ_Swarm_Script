import pandas as pd
from pyproj import Proj, transform, Transformer
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as feature
import requests
import math


func = Transformer.from_crs("EPSG:4236", "EPSG:2193")


def mytran(lat, lon):
    return func.transform(lat, lon)
json = requests.get("http://api.geonet.org.nz/intensity?type=reported&publicID=2019p665658").json()
lon, lat = [],[]

lon = [i['geometry']['coordinates'][0] for i in json['features']]
lat = [i['geometry']['coordinates'][1] for i in json['features']]
def round_five(x, base=5):
    return int(base * round(float(x) / base))





extracted = json['features'][2]['properties']['count_mmi']
counts = json['features'][2]['properties']['count']
weighted_av = [int(i[0]) * i[1] for i in extracted.items()]
weighted_val = []
for a in json['features']:
    total_count = a['properties']['count']
    list_of_vals  = [int(i[0]) * i[1] for i in a['properties']['count_mmi'].items()]
    weighted_val.append((a['geometry']['coordinates'][0],a['geometry']['coordinates'][1], total_count))
df = pd.DataFrame(weighted_val, columns = ['longitude', 'latitude', 'count'])

df["northing"], df["easting"] = mytran(df.latitude.tolist(), df.longitude.tolist())

north_events, east_events = df.northing.tolist(), df.easting.tolist()
list_tuples = [(north_events[i], east_events[i]) for i in range(len(north_events))]

df["ltrb"] = [(math.floor(i[1] / 5000) * 5000,
        math.floor(i[0]/ 5000) * 5000,
        math.ceil(i[1]/ 5000) * 5000,
        math.ceil(i[0]/ 5000) * 5000) for i in list_tuples]



df_grouped = df.groupby('ltrb')['count'].sum().reset_index()

df2 = pd.read_csv('nz-1km-pop-grid.csv')
df2["Left"] = [math.floor(i / 5000) * 5000 for i in df2.Left.tolist()]
df2["Top"] = [math.floor(i / 5000) * 5000 for i in df2.Top.tolist()]
df2["Right"] = [math.ceil(i / 5000) * 5000 for i in df2.Right.tolist()]
df2["Bottom"] = [math.ceil(i / 5000) * 5000 for i in df2.Bottom.tolist()]

l, t, r, b = df2.Left.tolist(), df2.Top.tolist(), df2.Right.tolist(),df2.Bottom.tolist()
df2['ltrb'] = [(l[i], t[i], r[i], b[i]) for i in range(len(l))]
df2 = df2.groupby('ltrb')['totpop'].sum().reset_index()

print(df2.sort_values(by='totpop'))

potato = df_grouped.merge(df2,how='inner', on = 'ltrb')
potato["counts_per_cap"] = potato['count'] / potato['totpop']
potato.replace([np.inf, -np.inf], 0, inplace=True)
potato = potato[potato['totpop'] > 1]
potato['centre'] = [(int((i[0] + i[2]) / 2), int((i[1] + i[3]) / 2)) for i in potato.ltrb.tolist()]
print(potato.sort_values(by='counts_per_cap'))
list_north = list(range(4640000, 6500000, 5000))
list_east = list(range(850000, 2450000, 5000))
list_north = [i + 2500 for i in list_north]
list_east = [i + 2500 for i in list_east]

grouped = df.groupby(['northing', 'easting'], as_index=False).count()

north_events, east_events = df.northing.tolist(), df.easting.tolist()
df["tuples"] = [(north_events[i], east_events[i]) for i in range(len(north_events))]

full = []
for a in list_north:
    full.append([(a, i) for i in list_east])

flat_list = [item for sublist in full for item in sublist]


blank_df = pd.DataFrame(flat_list, columns=["n", "e"])
blank_df["centre"] = [(i[1], i[0]) for i in flat_list]

count_df = potato[["centre", "counts_per_cap", "totpop", "count"]]

tomato = blank_df.merge(count_df, on='centre', how='outer')
tomato = tomato.fillna(0)
print(tomato.sort_values(by='counts_per_cap'))
counts = tomato.counts_per_cap.tolist()

for ind, val in enumerate(counts):
    if val == 0:
        counts[ind] = -1

zc_new = np.ndarray((len(list_north), len(list_east)))
for a in range(0, len(list_north)):
    for b in range(0, len(list_east)):
        zc_new[a][b] = counts[b + a * len(list_east)]

from matplotlib.cm import ScalarMappable
import matplotlib.pyplot as plt

levels_array = [i/200 for i in range(0, 20, 1)]
levels = 300
vmin = -.005
vmax = .1


level_boundaries = np.linspace(vmin, vmax, levels + 1)

cbarticks = [i/400 for i in range(0, 20, 1)]

fig = plt.figure(figsize=(15, 15))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_title("Felt reports per capita", fontsize=25, pad=10)

ax.set_extent([165, 180, -48, -33], crs=ccrs.PlateCarree())

cf = plt.contourf(list_east, list_north, zc_new, levels=levels_array, vmin=vmin,
                  vmax=vmax, alpha = 0.8, cmap = 'gist_heat_r', transform= ccrs.epsg(2193), extend = 'both')
ax.coastlines(linewidth=0.5, color='black')

cb = fig.colorbar(
    ScalarMappable(norm=cf.norm, cmap=cf.cmap),
    ticks=[i/200 for i in range(0, 20, 1)],
    boundaries=level_boundaries,
    values=(level_boundaries[:-1] + level_boundaries[1:]) / 2,fraction=0.046, pad=0.01
)
ax.add_feature(feature.OCEAN, zorder=0)
ax.add_feature(feature.LAND, zorder=0)
cb.ax.tick_params(labelsize=15)
plt.tight_layout()
plt.savefig("bang_bing.png",  bbox_inches = "tight")