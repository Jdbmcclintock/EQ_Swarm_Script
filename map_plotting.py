from data_pull import *
import folium
import branca.colormap as cm
import matplotlib.cm

cmap = matplotlib.cm.get_cmap('magma', 5)
rgba = []
for i in range(cmap.N):
    rgba.append(cmap(i))


quakes = quakedata("2021p061879", 3, 0, radius=10)
quake_df = json_extraction(quakes)

coordds = locinfo("2021p061879")

rounded_max_time = quake_df.iloc[-1]["since_origin"].round()

colormap = cm.LinearColormap(colors = rgba, vmin = 0, vmax = rounded_max_time)


m = folium.Map(location=[coordds[0],coordds[1]], tiles= 'OpenStreetMap', zoom_start= 12)


for i in range(0, len(quake_df)):
    folium.CircleMarker(location = [quake_df.iloc[i]["lat"], quake_df.iloc[i]["lon"]],
                  radius = (quake_df.iloc[i]['magnitude'] + 2) **2.5 / 5,
                  popup = folium.Popup('Mag = '
                                       + str(round(quake_df.iloc[i]['magnitude'],1))
                                       + "<br>Depth = "
                                       + str(round(quake_df.iloc[i]['depth'],1))
                                       + " km<br>Origin time = "
                                       + quake_df.iloc[i]['origtime'][0:19]
                                       +'<br><a href="'
                                       + quake_df.iloc[i]["url"]
                                       +' "target="_blank"> [Geonet Webpage]</a>',
                                       max_width = 200),
                  color = colormap(quake_df.iloc[i]["since_origin"]), fill = True, fill_opacity = 0.3).add_to(m)
m.add_child(colormap)

m.save('banana.html')


