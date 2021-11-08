import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import pandas as pd
import numpy as np
import pandas as pd
from pyproj import Proj, transform, Transformer
from matplotlib import colors

df = pd.read_csv("earthquakes.csv")
df["moment"] = 10 ** (1.5 * df["magnitude"] + 16.1) / 10 ** 7

def figure(df)