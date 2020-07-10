#!/usr/bin/env python
# coding: utf-8

# # Segmenting and Clustering neighbourhoods in Toronto

# ## 1. Description 

# In this assignment, you will be required to explore, segment, and cluster the neighborhoods in the city of Toronto.
# 
# For the Toronto neighborhood data, a Wikipedia page exists that has all the information we need to explore and cluster the neighborhoods in Toronto. You will be required to scrape the Wikipedia page and wrangle the data, clean it, and then read it into a pandas dataframe so that it is in a structured format like the New York dataset.
# 
# Once the data is in a structured format, you can replicate the analysis that we did to the New York City dataset to explore and cluster the neighborhoods in the city of Toronto.

# # 2. Scrap content from wiki page

# Importing necessary packages
# 
# 

# In[6]:


import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
from pandas.io.json import json_normalize  # tranform JSON file into a pandas dataframe


# Scraping the "raw" table.

# In[7]:


source = requests.get("https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M").text
soup = BeautifulSoup(source, 'lxml')

table = soup.find("table")
table_rows = table.tbody.find_all("tr")

res = []
for tr in table_rows:
    td = tr.find_all("td")
    row = [tr.text for tr in td]
    if row != [] and row[1] != "Not assigned\n":
        if "Not assigned\n" in row[2]: 
            row[2] = row[1]
        res.append(row)
        
df = pd.DataFrame(res, columns = ["PostalCode", "Borough", "Neighborhood"])
df


# In[8]:


df["PostalCode"] = df["PostalCode"].str.replace("\n","")
df["Borough"] = df["Borough"].str.replace("\n","")
df["Neighborhood"] = df["Neighborhood"].str.replace("\n","")
df.head()


# Grouping all neighborhoods with the same postal code
# 
# 

# In[9]:


df = df.groupby(["PostalCode", "Borough"])["Neighborhood"].apply(", ".join).reset_index()
df.head()


# In[10]:


print("Shape: ", df.shape)


# # 3. Get the latitude and the longitude coordinates of each neighborhood.

# In[11]:


df_geo_coor = pd.read_csv("https://cocl.us/Geospatial_data")
df_geo_coor.head()


#  Coupling 2 dataframes "df" and "df_geo_coor" into one dataframe.

# In[12]:


df_toronto = pd.merge(df, df_geo_coor, how='left', left_on = 'PostalCode', right_on = 'Postal Code')
# removing the "Postal Code" column
df_toronto.drop("Postal Code", axis=1, inplace=True)
df_toronto


# In[13]:


get_ipython().system('conda install -c conda-forge folium -y')


# In[14]:


from geopy.geocoders import Nominatim # convert an address into latitude and longitude values
from pandas.io.json import json_normalize  # tranform JSON file into a pandas dataframe

import folium # map rendering library

# import k-means from clustering stage
from sklearn.cluster import KMeans

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors
address = "Toronto, ON"

geolocator = Nominatim(user_agent="toronto_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto city are {}, {}.'.format(latitude, longitude))


# In[17]:


map_toronto = folium.Map(location=[latitude, longitude], zoom_start=10)


# In[18]:


map_toronto


# In[15]:


for lat, lng, borough, neighborhood in zip(
        df_toronto['Latitude'], 
        df_toronto['Longitude'], 
        df_toronto['Borough'], 
        df_toronto['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)  

map_toronto


# In[19]:


df_toronto_denc = df_toronto[df_toronto['Borough'].str.contains("Toronto")].reset_index(drop=True)
df_toronto_denc.head()


# In[20]:


map_toronto_denc = folium.Map(location=[latitude, longitude], zoom_start=12)
for lat, lng, borough, neighborhood in zip(
        df_toronto_denc['Latitude'], 
        df_toronto_denc['Longitude'], 
        df_toronto_denc['Borough'], 
        df_toronto_denc['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto_denc)  

map_toronto_denc

