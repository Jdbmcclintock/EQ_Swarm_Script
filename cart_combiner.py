import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from matplotlib import gridspec

from data_pull import *

import io
from PIL import Image


quakes = quakedata("2021p169083", 30, 0, radius=100)
quake_df = json_extraction(quakes)

"""coords_east = (176, 180, -40, -35)
coords_west = (-177, -179.999, -40, -35)

width_e = coords_east[1] - coords_east[0]
width_w = coords_west[0] - coords_west[1]


osm_img = cimgt.OSM()
fig = plt.figure(figsize = (12,12))
gs1 = gridspec.GridSpec(1,2, width_ratios = [width_e, width_w])
gs1.update(wspace = 0, hspace = 0)

ax1 = plt.subplot(gs1[0], projection = osm_img.crs)

ax2 = plt.subplot(gs1[1], projection = osm_img.crs)

ax1.set_extent(coords_east)
ax1.add_image(osm_img, 9)

ax2.set_extent(coords_west)
ax2.add_image(osm_img, 9)
#ax1.spines["right"].set_visible(False)
#ax2.spines["left"].set_visible(False)
ax1.spines["geo"].set_linewidth(0)
ax2.spines["geo"].set_linewidth(0)

fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)
ax1.scatter([177], [-37], s = 200, transform = ccrs.PlateCarree(), marker = 'o', c = 'red')
plt.savefig("ass.png", pad_inches = 0.1, bbox_inches = 'tight')"""

def coord_splitter(minlon, maxlon, minlat, maxlat):
    coords_east = (minlon, 180, minlat, maxlat)
    coords_west = (maxlon - 360, -179.99999, minlat, maxlat)
    return coords_east, coords_west


def two_maps(coords_east, coords_west, extent):
    osm_img = cimgt.OSM()
    fig = plt.figure(figsize=(20, 26), dpi = 200)
    width_e = coords_east[1] - coords_east[0]
    width_w = coords_west[0] - coords_west[1]
    gs1 = gridspec.GridSpec(1, 2, width_ratios=[width_e, width_w])
    gs1.update(wspace=0, hspace=0)
    axes = [plt.subplot(gs1[0], projection=ccrs.PlateCarree()), plt.subplot(gs1[1], projection=ccrs.PlateCarree())]
    axes[0].set_extent(coords_east)
    axes[1].set_extent(coords_west)
    for ax in axes:
        ax.add_image(osm_img, 6, interpolation = 'spline36')
        ax.spines["geo"].set_linewidth(0)
    fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)
    plt.savefig("internal.png", pad_inches=0.1, bbox_inches='tight')
"""    fig.clf()
    image = plt.imread("internal.png")
    ax = plt.axes(projection=ccrs.Orthographic(central_longitude=175, central_latitude=-40))
    ax.imshow(image, extent=extent, aspect=1.5,
              transform=ccrs.Orthographic(central_longitude=175, central_latitude=-40))
    plt.tight_layout()
    return fig"""

"""def df_split(df):
    negative_lon_df = df[df["lon"] < 0]
    positive_lon_df = df[df["lon"] > 0]
    return positive_lon_df, negative_lon_df,"""

"""def plot_eqs_twomap(df):
    for ind, val in enumerate(df["lon"]):
        if val < 0:
            df["lon"][ind] = val + 360
    coords = [df.iloc[0]["lon"] - 3,
              df.iloc[0]["lon"] + 3,
              df.iloc[0]["lat"] - 1.5,
              df.iloc[0]["lat"] + 1.5]
    coords_east, coords_west= coord_splitter(coords[0], coords[1], coords[2], coords[3])
    fig = two_maps(coords_east, coords_west, coords)
    colormap_style = 'magma'
    plt.scatter(df["lon"],
             df["lat"],
             s=[(int(str(i)[0]) + 1) ** 3.1 * 4 for i in df['magnitude']],
             marker='o',
             # parameter for colorbar is "time since origin"
             c=df["since_origin"],
             cmap=colormap_style,
             edgecolors='black',
             linewidths=0.6,
             # transparency value to show markers below
             alpha=0.6)

    return plt.show()
"""
e, w = coord_splitter(163, 185, -50, -32)

fig = two_maps(e, w, [163, 185, -50, -32])

#fig.savefig("banana.png", bbox_inches = 'tight', pad_inches = 0)
