import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import pandas as pd
import numpy as np
import pandas as pd
from pyproj import Proj, transform, Transformer
from matplotlib import colors

df = pd.read_csv("earthquakes_2000.csv")
df["moment"] = 10 ** (1.5 * df["magnitude"] + 16.1) / 10 ** 7

func = Transformer.from_crs("EPSG:4236", "EPSG:2193")

def mytran(lat, lon):
    return func.transform(lat, lon)

df["northing"], df["easting"] = mytran(df.latitude.tolist(), df.longitude.tolist())
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df = df.dropna(subset=['northing', 'easting'])

def round_five(x, base=5):
    return int(base * round(float(x) / base))


df["northing_round"] = df["northing"].apply(lambda x: round_five(x, base=2500))
df["easting_round"] = df["easting"].apply(lambda x: round_five(x, base=2500))


grouped = df.groupby(['northing_round', 'easting_round'], as_index=False).count()

countdf = grouped[["northing_round", "easting_round", "publicid"]]

#fig = countdf.plot("easting", "northing", kind='scatter', c='publicid', cmap='magma_r', figsize=(15, 15), s=1.56,
                #   marker='s', vmax=100)
#xmin, xmax = fig.get_ylim()
#plt.savefig("banana.png")


def heat_fig(df, title, color, vmax, vmin, s = 6, cmap = None, marker = 's', alpha = 1):
    fig = plt.figure(figsize = (15,15))
    ax = plt.axes(projection = ccrs.PlateCarree())
    ax.set_title(title, fontsize = 25, pad = 10)
    ax.set_extent([165, 180, -48, -33], crs = ccrs.PlateCarree())
    ax.coastlines(linewidth=0.5, color='black')
    scat = ax.scatter(df.easting_round,
            df.northing_round,
            c = color,
            transform= ccrs.epsg(2193),
            cmap = cmap,
            s =s,
            marker = marker,
            vmax = vmax,
            vmin = vmin,
            alpha = alpha)
    fig.tight_layout()
    if cmap != None:
        cbar = fig.colorbar(scat, fraction=0.046, pad=0.02)
        cbar.ax.tick_params(labelsize=15)
    return fig

df_4 = df[df["magnitude"] > 4]
grouped_4 = df_4.groupby(['northing_round', 'easting_round'], as_index=False).count()
countdf_4 = grouped_4[["northing_round", "easting_round", "publicid"]]
df_3 = df[df["magnitude"] > 3]
grouped_3 = df_3.groupby(['northing_round', 'easting_round'], as_index=False).count()
momentdf = df.groupby(['northing', 'easting'], as_index=False)["moment"].sum()

momentdf["cum_mag"] = (np.log10(momentdf["moment"] * 10 **7) - 16.1) / 1.5

to_scat = df[df["magnitude"] > 3.5]
depthdf = df.groupby(['northing_round', 'easting_round'], as_index=False)["depth"].agg(['count','mean']).reset_index()
depthdf = depthdf[depthdf["count"] > 2]
std = df.groupby(['northing_round', 'easting_round'], as_index=False)["depth"].agg(['count','std']).reset_index()
std = std[std["count"] > 2]
avmag_fix = df.groupby(['northing_round', 'easting_round'], as_index=False)["magnitude"].agg(['count','mean']).reset_index()
avmag_fix = avmag_fix[avmag_fix["count"] > 2]

def q1(x):
    return x.quantile(0.1)

quant = df.groupby(['northing_round', 'easting_round'], as_index=False)["magnitude"].agg(['count',q1]).reset_index()
quant = quant[quant["count"] > 2]

fig1 = heat_fig(countdf, "Frequency of earthquakes in Geonet catalog heatmap since 2000", countdf.publicid, 100, None, cmap = "magma_r")
plt.savefig("numeq_2000.png", bbox_inches = 'tight')

fig2 = heat_fig(countdf_4, "Frequency of earthquake in Geonet catalog heatmap since 2000 (M4+)", countdf_4.publicid, 10, None, cmap = "magma_r")
plt.savefig("numeq4_2000.png", bbox_inches = 'tight')

fig2 = heat_fig(grouped_3, "Frequency of earthquake in Geonet catalog heatmap since 2000 (M3+)", grouped_3.publicid, 20, None, cmap = "magma_r")
plt.savefig("numeq3_2000.png", bbox_inches = 'tight')

fig3 = heat_fig(to_scat, "Earthquake moment - NZ catalog", "red", 8.5, 3,  s = [(31 ** i / 10 **8)  for i in to_scat.magnitude], marker ='o', alpha = 0.5)
plt.savefig("eqsize_2000.png", bbox_inches = 'tight')

fig2 = heat_fig(depthdf, "Heatmap of mean depth of earthquakes since 2000", depthdf["mean"], 300, None, cmap = "magma_r")
plt.savefig("meandepth2000.png", bbox_inches = 'tight')

fig2 = heat_fig(std, "Heatmap of depth standard deviation earthquakes since 2000", std["std"], 100, None, cmap = "magma_r")
plt.savefig("std2000.png", bbox_inches = 'tight')

fig2 = heat_fig(avmag_fix, "Heatmap of mean magnitude since 2000", avmag_fix["mean"], 6, 0, cmap = "magma_r")
plt.savefig("meanmag2000.png")

fig2 = heat_fig(quant, "Heatmap of 10th percentile EQs", quant["q1"], 6, 0, cmap = "magma_r")
plt.savefig("quant.png")


"""
lat = df.latitude
lon = df.longitude

Z, xedges, yedges = np.histogram2d(np.array(lon, dtype=float),
                                   np.array(lat, dtype=float), bins = 4000)
ax1.pcolormesh(xedges, yedges, np.where(Z.T  == 0, np.nan, Z.T), vmin = 10, vmax = 300, cmap = 'YlOrRd')
plt.show()


Z, xedges, yedges = np.histogram2d(np.array(lon, dtype=float),
                                   np.array(lat, dtype=float), bins = 4000)


ax2 = plt.axes(projection = ccrs.PlateCarree())
ax2.set_title("Heatmap of number of earthquakes")
# uses coordinates of first earthquake to base map centering. May lead to unexpected behaviour... Should maybe
# change this to mean of each column? The default width is 0.8 degrees lon vs 0.4 degrees lat
coords = [165, 180, -48, -33]
# set the boundary of the map to these
ax2.set_extent(coords, crs= ccrs.PlateCarree())
# adds image time from openstreetmap, integer value is default zoom?
ax2.coastlines(linewidth=0.5, color='black')


ax2.pcolormesh(xedges, yedges, Z.T, cmap = 'YlOrRd')"""

