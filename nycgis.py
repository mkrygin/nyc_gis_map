# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 16:43:59 2019
From source: https://towardsdatascience.com/lets-make-a-map-using-geopandas-pandas-and-matplotlib-to-make-a-chloropleth-map-dddc31c1983d
Shapefile source: https://geo.nyu.edu/catalog/nyu-2451-34509   
@author: krygi
"""

import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_csv('nycgis.csv', header=0)
print(df)


import geopandas as gpd
#nyc = gpd.read_file(gpd.datasets.get_path('nybb'))
nyc = gpd.read_file('nyu_2451_34509.shp')
#nyc.plot()

df['zipcode'] = df['Zipcode'].astype(int)
nyc['zcta'] = nyc['zcta'].astype(int)
merged = nyc.set_index('zcta').join(df.set_index('zipcode'))

print(merged)
#print(nyc.dtypes)
#print(df.dtypes)

#assign vmin and vmax 
vmin = df['Number of Providers'].min()
vmax = df['Number of Providers'].max()


sm = plt.cm.ScalarMappable(cmap = 'YlGnBu', norm=plt.Normalize(vmin=vmin, vmax=vmax))
# empty array for the data range
sm._A = []


plot = merged.plot(column='Number of Providers', cmap = 'YlGnBu', scheme = 'quantiles')
fig = plot.get_figure()
# add the colorbar to the figure
cbar = fig.colorbar(sm)
fig.savefig('nycmap.svg')
