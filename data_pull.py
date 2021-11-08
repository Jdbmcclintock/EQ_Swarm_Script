import requests
import dateutil
import pandas as pd
from datetime import timedelta

def locinfo(quakeid):
    mainshock_json = requests.get("https://api.geonet.org.nz/quake/" + quakeid).json()
    main_lon, main_lat = mainshock_json['features'][0]['geometry']['coordinates']
    return (main_lat, main_lon)


def quakedata(quakeid, days, minimum_magnitude, radius=100):
    """
    Pull aftershock informaton for a defined period of time after the mainshock and produce plots of it
    for analysis.
    :param quakeid:
    :param days:
    :param radius:
    :return:
    """

    mainshock_json = requests.get("https://api.geonet.org.nz/quake/" + quakeid).json()
    mainshock_time = mainshock_json['features'][0]['properties']['time']
    start_time = mainshock_time[:19]
    main_lon, main_lat = mainshock_json['features'][0]['geometry']['coordinates']
    location = str(main_lon) + "+" + str(main_lat)
    end_time = (dateutil.parser.isoparse(mainshock_time) + timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S')
    sequence_json = requests.get("http://wfs.geonet.org.nz/geonet/ows?service=WFS&version=1.0.0&request=" +
                                 "GetFeature&typeName=geonet:quake_search_v1&outputFormat=json&cql_filter=" +
                                 "origintime>=" + start_time + "+AND+origintime<=" + end_time +
                                 "+AND+depth<400+AND+magnitude>=" + str(minimum_magnitude) +
                                 "+AND+DWITHIN(origin_geom,Point+(" + location + ")," + str(
        radius) + "000,meters)").json()

    return sequence_json

def json_extraction(wfs_json):

    magnitude, origtime, depth, lon, lat, url = ([] for i in range(6))
    for a in range(len(wfs_json['features'])):
        magnitude.append(wfs_json['features'][a]['properties']['magnitude'])
        origtime.append(wfs_json['features'][a]['properties']['origintime'])
        depth.append(wfs_json['features'][a]['properties']['depth'])
        lon.append(wfs_json['features'][a]['geometry']['coordinates'][0])
        lat.append(wfs_json['features'][a]['geometry']['coordinates'][1])
        url.append("https://www.geonet.org.nz/earthquake/" + wfs_json['features'][a]['properties']['publicid'])
    time_since = [dateutil.parser.isoparse(origtime[0]) - dateutil.parser.isoparse(i) for i in origtime]
    in_hours = [i.total_seconds() / 3600.0 for i in time_since]
    df = pd.DataFrame({"magnitude":magnitude, "origtime":origtime, "depth":depth,
                       "lon":lon, "lat":lat, "url":url, "since_origin":in_hours})
    return df

