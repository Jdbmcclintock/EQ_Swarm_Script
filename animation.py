import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from matplotlib.animation import FFMpegWriter
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

import os
import requests
import dateutil.parser
from datetime import timedelta, datetime

firstquakeid = "2021p169083"  # user input Geonet public ID as a string
interval = 300  # interval in seconds
timelength = 4032  # total length of time to examine, in units of above interval
filename = "East_cape"  # string of filename


def aftershock_animation(quakeid, interval, timelength, filename):
    """This function takes a Geonet quakeid input and returns an animation.

    Data taken from the Geonet API. Some default parameters: aftershocks defined
    as within 50 km of epicentre, map defined by .25 degrees in any direction from
    epicentre. Presently designed for rapid maps of aftershocks, for multiple days
    would recommend changing framerate and the timelist and stime lists (the 60
    represents how many seconds per frame)"""

    # Queries Geonet API to retreive mainshock's data
    quake = requests.get("https://api.geonet.org.nz/quake/" + firstquakeid).json()

    # Origin time from json file, in datetime object
    starttime = dateutil.parser.isoparse(quake['features'][0]['properties']['time']) - timedelta(seconds=600)
    endtime = starttime + timedelta(days=20)  # end time, 5 days after, increase if needed

    # strings of times for wfs query
    start, end = starttime.strftime('%Y-%m-%dT%H:%M:%S'), endtime.strftime('%Y-%m-%dT%H:%M:%S')
    # longitude/latitude for query
    lon1 = quake['features'][0]['geometry']['coordinates'][0]
    lat1 = quake['features'][0]['geometry']['coordinates'][1]
    latlon = str(lon1) + "+" + str(lat1)

    # wfs query. For further info see wfs.geonet.org.nz
    quakejson = requests.get("http://wfs.geonet.org.nz/geonet/ows?service=WFS&version=1.0.0&request="
                             "GetFeature&typeName=geonet:quake_search_v1&outputFormat=json&cql_filter="
                             "origintime>=" + start + "+AND+origintime<=" + end + "+AND+DWITHIN"
                                                                                  "(origin_geom,Point+(" + latlon + "),100000,meters)+AND+depth<400").json()

    lat, lon, mag, time = ([] for i in range(4))  # empty lists for iterating
    # Following pulls quake data for plotting
    for a in range(len(quakejson['features'])):
        lon.append(quakejson['features'][a]['geometry']['coordinates'][0])
        lat.append(quakejson['features'][a]['geometry']['coordinates'][1])
        mag.append(quakejson['features'][a]['properties']['magnitude'])
        time.append(dateutil.parser.isoparse(quakejson['features'][a]['properties']['origintime']))
    # Dataframe of quake info
    for ind, val in enumerate(lon):
        if val < 0:
            lon[ind] = val + 360
    df = pd.DataFrame({"lat": lat, "lon": lon, "time": time, "mag": mag})
    # sort dataframe by origin time
    df = df.sort_values(by="time")
    # Initiate plot
    fig, ax = plt.subplots(figsize=(10, 12), dpi=100)
    # ax=fig.add_axes([0,0,1,1]) #removing whitespace
    image = plt.imread("osm.png")

    # Basemap plot - world topo map can be subbed for preferred map
    ax = plt.axes(projection=ccrs.Orthographic(central_longitude=175, central_latitude=-40))
    ax.imshow(image, extent=[176.935, 180.428, -39.601, -36.589], aspect=1.5,
              transform=ccrs.Orthographic(central_longitude=175, central_latitude=-40))

    # timestamp for every minute, up to a defined user limit.
    # this is used to create a frame for every minute, showing all quakes prior to said stamp
    timelist = [list(df['time'])[0] + timedelta(seconds=interval * x) for x in range(timelength)]
    # Strings of above to plot as annotation
    stime = [str(x)[0:19] for x in timelist]

    # Defining initial blank plot to offset to
    scat = ax.scatter([], [], alpha=0.6, edgecolor="black", linewidths=0.6, c='crimson', transform = ccrs.Orthographic(central_longitude=175, central_latitude=-40))

    # messy part defining size of legend elements, probably should be loop
    l2 = plt.scatter([], [], s=2 ** 3.2 * 2.5, c='crimson')
    l3 = plt.scatter([], [], s=3 ** 3.2 * 2.5, c='crimson')
    l4 = plt.scatter([], [], s=4 ** 3.2 * 2.5, c='crimson')
    l5 = plt.scatter([], [], s=5 ** 3.2 * 2.5, c='crimson')
    l6 = plt.scatter([], [], s=6 ** 3.2 * 2.5, c='crimson')
    l7 = plt.scatter([], [], s=7 ** 3.2 * 2.5, c='crimson')
    l8 = plt.scatter([], [], s=8 ** 3.2 * 2.5, c='crimson')
    # legend labels
    labels = [str(x + 1) + "-" + str(x + 2) for x in range(7)]
    plt.legend([l2, l3, l4, l5, l6, l7, l8], labels, title="Magnitude", loc='lower center',
               labelspacing=1, ncol=7, borderpad=1.7, columnspacing=2.3, handletextpad=1.2)

    # annotations - first one is the timestamp, second one is a count of the earthquakes
    annotation = ax.annotate(str(stime[0]), xy=(625, 950), xycoords='axes pixels',
                             fontsize=14, c='black')
    annotationcount = ax.annotate("Earthquake count: 0", xy=(20, 950), xycoords='axes pixels',
                                  fontsize=17, c='black')
    annotation.set_animated(True)
    annotationcount.set_animated(True)
    ax.set_aspect('auto')

    # "initial" blank function, negative values help hide "initial" circle
    def init():
        scat.set_offsets([[], []])
        return scat, annotation, annotationcount

    # animation function - plots all quakes before minute "a", including updating the annotations
    def update(a):
        df2 = df[df['time'] < timelist[a]]
        x,y = df2['lon'],df2['lat']
        scat.set_offsets(np.c_[x, y])
        scat._sizes = [(int(str(x)[0]) + 1) ** 3.2 * 2.5 for x in list(df2['mag'])]
        annotation.set_text(stime[a])
        annotationcount.set_text("Earthquake count: " + str(len(df2)))
        return scat,

    # function to write animation to an mp4, with the defined filename (automatically as an mp4)
    ani = animation.FuncAnimation(fig, update, init_func=init, blit=False, frames=len(timelist))
    writer = FFMpegWriter(fps=30, bitrate=1800)  # change fps if desired
    ani.save((filename + ".mp4"), writer=writer)


aftershock_animation(firstquakeid, interval, timelength, filename)