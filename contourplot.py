import matplotlib.pyplot as plt
import shapely
import requests
from shapely.geometry import Point
from pyproj import Proj, transform, Geod
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
import cartopy.crs as ccrs




json = requests.get("https://api.geonet.org.nz/network/sensor?sensorType=3,8,9&endDate=9999-01-01").json()

loc, code, end = [], [], []
for ind, val in enumerate(json['features']):
    loc.append(val["geometry"]["coordinates"])
    code.append(val["properties"]["Code"])
    end.append(val["properties"]["End"])

df = pd.DataFrame({"loc": loc, "code": code, "end": end})

df = df[df["end"] == "9999-01-01T00:00:00Z"]
df = df.drop_duplicates("code")
df = df.drop(df[df.code.isin(["HD60", "HD61", "HD62", "HD63", "HD64", "HD65", "CRSZ"])].index)

df["loc"] = tuple(df["loc"])


list_loc = df["loc"].tolist()
cor_loc = [t[::-1] for t in list_loc]

geod = Geod(ellps='WGS84')

list_lats = [i / 10 for i in list(range(-330, -500, -2))]
list_lon = [i / 10 for i in list(range(1650, 1820, 2))]

full = []
for a in list_lats:
    full.append([(a, i) for i in list_lon])

tendist = []
for a in full:
    for b in a:
        list_of_distances = []
        for c in list_loc:
            angle1, angle2, dist1 = geod.inv(b[1], b[0], c[0], c[1])
            list_of_distances.append(dist1)
        tendist.append((b, sorted(list_of_distances, reverse=True)[-9]))

z = [i[1]/1000 for i in tendist]

for ind, val in enumerate(z):
    if val > 400:
        z[ind] = 400

zc = np.ndarray((85, 85))
for a in range(0, len(list_lon)):
    for b in range(0, len(list_lats)):
        zc[a][b] = z[b + a * 85]


levels = 100
vmin = 0
vmax = 400


level_boundaries = np.linspace(vmin, vmax, levels + 1)

cbarticks = np.arange(0, vmax, 50)


"""contours = plt.contour(list_lon, list_lats, zp, 100, colors='black', a=0.6, vmin=8000, vmax=300000)
cf = plt.contourf(list_lon, list_lats, zp, levels=100, vmin=8000, vmax=300000)

fig.colorbar(
    ScalarMappable(norm=cf.norm, cmap=cf.cmap),
    ticks=range(vmin, vmax + 50000, 50000),
    boundaries=level_boundaries,
    values=(level_boundaries[:-1] + level_boundaries[1:]) / 2,
)
plt.show()"""


fig = plt.figure(figsize=(15, 15))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_title("Distance from tenth seismic station (km)", fontsize=25, pad=10)

ax.set_extent([165, 180, -48, -33], crs=ccrs.PlateCarree())

cf = plt.contourf(list_lon, list_lats, zc, levels=levels, vmin=8, vmax=vmax, alpha = 0.6, cmap = 'jet_r')

#plt.contourf(list_lon, list_lats, zp, levels=levels, vmin=8000, vmax=vmax, alpha = 0.6, cmap = 'rainbow_r')
#plt.contourf(list_lon, list_lats, zp, levels=levels, vmin=8000, vmax=vmax, alpha = 0.6, cmap = 'rainbow_r')


#cont = plt.contour(list_lon, list_lats, zc, levels = levels, vmin=8000, vmax=100, linewidths = 0.08, colors='black')


cb = fig.colorbar(
    ScalarMappable(norm=cf.norm, cmap=cf.cmap),
    ticks=range(vmin, vmax + 50, 50),
    boundaries=level_boundaries,
    values=(level_boundaries[:-1] + level_boundaries[1:]) / 2,
)
cb.ax.invert_yaxis()
ax.coastlines(linewidth=0.5, color='black')

plt.show()