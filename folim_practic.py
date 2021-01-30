from data_pull import *
import folium
import branca.colormap as cm
import matplotlib.cm
from folium import IFrame
import io
from PIL import Image
from selenium import webdriver


cmap = matplotlib.cm.get_cmap('magma', 5)
rgba = []
for i in range(cmap.N):
    rgba.append(cmap(i))



quakes = quakedata("2021p061879", 3, 0, radius=10)
quake_df = json_extraction(quakes)

coordds = locinfo("2021p061879")

rounded_max_time = quake_df.iloc[-1]["since_origin"].round()

colormap = cm.LinearColormap(colors = rgba, vmin = 0, vmax = rounded_max_time, caption = "Hours since first quake")


m = folim_practic.Map(location=[coordds[0], coordds[1]], tiles='OpenStreetMap', zoom_start= 12)

magnitudes = [1, 2, 3, 4, 5, 6, 7]


for i in range(0, len(quake_df)):
    folim_practic.Circle(location = [quake_df.iloc[i]["lat"], quake_df.iloc[i]["lon"]],
                         radius = (quake_df.iloc[i]['magnitude'] + 2) **2.5 * 4,
                         scale_radius = True,
                         popup = folim_practic.Popup('Mag = '
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
folim_practic.Circle(location = [m.get_bounds()[0][0], m.get_bounds()[0][1]],
                     radius = (quake_df.iloc[0]['magnitude'] + 12) **2.5 * 4,
                     scale_radius = True).add_to(m)

html = '<div style="position: fixed; bottom: 50px; left: 50px; width: 200px; height: 50px; background-color: #FFFFFF; z-index:9000;">Hello</div>'
m.get_root().html.add_child(folim_practic.Element(html))

m.save('banana.html')

#data = m._to_png(5)
#img = Image.open(io.BytesIO(data))
#img.save('bananatime.png')
print(m.get_bounds()[0])



