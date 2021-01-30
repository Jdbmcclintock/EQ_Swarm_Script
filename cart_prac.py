from data_pull import *
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

quakes = quakedata("2021p061879", 3, 0, radius=10)
quake_df = json_extraction(quakes)

def plot_scatter_map(quake_df, title, colormap_style = 'magma'):
    """Function to generate a PNG of a scatter plot on a map of earthquake locations, magnitudes and time since
    occurence.
    :param quake_df: a dataframe generated by the json_extraction function from data_pull.py. Contains columns on
    magnitude, origin time, depth, lat/lon, a Geonet URL and time since origin. Geonet URL not needed currently?
    :param title: the title to appear above the plot
    :param colormap_style: the color scheme for the colorbar for time since earthquake origin. Default is magma but
    other styles available in Matplotlib documentation.
    """

    # OpenStreetMap preferred map style - easy to use and locations fairly identifiable. This pulls map tiles for OSM.
    osm_img = cimgt.OSM()
    # figsize arbitrary, maybe should be an option to change?
    fig = plt.figure(figsize = (12,15))
    # sets axes for plotting
    ax1 = plt.axes(projection = osm_img.crs)
    ax1.set_title(title)
    # uses coordinates of first earthquake to base map centering. May lead to unexpected behaviour... Should maybe
    # change this to mean of each column? The default width is 0.8 degrees lon vs 0.4 degrees lat
    coords = [quake_df.iloc[0]["lon"] - 0.4,
              quake_df.iloc[0]["lon"] + 0.4,
              quake_df.iloc[0]["lat"] - 0.2,
              quake_df.iloc[0]["lat"] + 0.2]
    # set the boundary of the map to these
    ax1.set_extent(coords)
    # adds image time from openstreetmap, integer value is default zoom?
    ax1.add_image(osm_img, 14)
    # plot the scattermap over the empty axis.
    scatter = ax1.scatter(quake_df["lon"],
                          quake_df["lat"],
                          # s for Size of marker - arbitrary function to make larger mags exponentially greater in radius
                          s= [(int(str(i)[0]) + 1) ** 3.1 * 4 for i in quake_df['magnitude']],
                          marker = 'o',
                          # parameter for colorbar is "time since origin"
                          c = quake_df["since_origin"],
                          cmap = colormap_style,
                          edgecolors = 'black',
                          linewidths = 0.6,
                          transform = ccrs.PlateCarree(),
                          # transparency value to show markers below
                          alpha = 0.6)
    # display colorbar within plot - negative pad means it's inside.
    cbar = plt.colorbar(scatter, shrink = 0.25, pad  = -0.025)
    cbar.set_label("Hours since initial quake", rotation = 270, labelpad = 20, fontsize = 12)
    # remove whitespace
    fig.subplots_adjust(left=0.05, right = 0.95, bottom = 0.05, top = 0.95)
    # worth making name of file configurable? Removes even more whitespace.
    plt.savefig("Swarm_Map.png", pad_inches = 0.1, bbox_inches = 'tight')