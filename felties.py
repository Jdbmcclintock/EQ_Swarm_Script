import pandas as pd
import requests

generic = "http://wfs.geonet.org.nz/geonet/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=geonet:quake_search_v1&outputFormat=json&cql_filter="

quakejson_sh = requests.get(generic + "magnitude>2.5+AND+origintime>=2016-04-27+AND+depth<40+AND+BBOX(origin_geom,163,-34,185,-50)").json()

quakejson_de = requests.get(generic + "magnitude>4+AND+origintime>=2016-04-27+AND+depth>40+AND+BBOX(origin_geom,163,-32,185,-50)").json()


print(len(quakejson_sh["features"]), len(quakejson_de["features"]))


