
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import geopandas 


# In[4]:


import pandas as pd


# In[5]:


#open the medicare dataset (originally a stata file)

df = pd.read_stata('medicarenyc2015.dta')


# In[6]:


#look at the medicare dataset to see if it was imported correctly
df 


# In[7]:


#rename the NPI column 
df = df.rename(index=str, columns={"Ã¯nationalprovideridentifier": "NPI"})
df


# In[8]:


#rename the zipcode columns and convert to a string
df = df.rename(index=str, columns={"zipcodeoftheprovider": "zipcode"})
df['zipcode'] = df['zipcode'].astype(str)
df['zipcode']


# In[9]:


#slice the zipcode. This is important for merging datasets in future steps, since the second dataset only has 5 digit
#zipcodes, not ones with such granular detail.
df['zipcode'] = df['zipcode'].map(lambda x : x[:5])
df['zipcode']


# In[10]:


#remove commas from the following columns to avoid calculation errors. convert to int after:
df['numberofmedicarebeneficiaries'] = df['numberofmedicarebeneficiaries'].astype(str)
df['numberofmedicarebeneficiaries'] = df['numberofmedicarebeneficiaries'].apply(lambda x: x.replace(',', ''))
df['numberofmedicarebeneficiaries'] = df['numberofmedicarebeneficiaries'].astype(int)


df['numberofdistinctmedicarebenefici'] = df['numberofdistinctmedicarebenefici'].astype(str)
df['numberofdistinctmedicarebenefici'] = df['numberofdistinctmedicarebenefici'].apply(lambda x: x.replace(',', ''))
df['numberofdistinctmedicarebenefici'] = df['numberofdistinctmedicarebenefici'].astype(int)

df['numberofservices'] = df['numberofservices'].astype(str)
df['numberofservices'] = df['numberofservices'].apply(lambda x: x.replace(',', ''))
df['numberofservices'] = df['numberofservices'].astype(int)

#convert these three columns to int
df['averagemedicarestandardizedamoun'] = df['averagemedicarestandardizedamoun'].astype(str)
df['averagemedicarestandardizedamoun'] = df['averagemedicarestandardizedamoun'].apply(lambda x: x.replace(',', ''))
df['averagemedicarestandardizedamoun'] = df['averagemedicarestandardizedamoun'].astype(float)

df['averagemedicarepaymentamount'] = df['averagemedicarepaymentamount'].astype(str)
df['averagemedicarepaymentamount'] = df['averagemedicarepaymentamount'].apply(lambda x: x.replace(',', ''))
df['averagemedicarepaymentamount'] = df['averagemedicarepaymentamount'].astype(float)

df['averagemedicareallowedamount'] = df['averagemedicareallowedamount'].astype(str)
df['averagemedicareallowedamount'] = df['averagemedicareallowedamount'].apply(lambda x: x.replace(',', ''))
df['averagemedicareallowedamount'] = df['averagemedicareallowedamount'].astype(float)


# In[11]:


#look at the mean number of services by zipcode
df.groupby('zipcode')['numberofservices'].mean()


# In[12]:


#import zipcode/neighborhood/borough file from excel
df3 = pd.read_excel('nyczipcodes.xlsx')


# In[13]:


#rename zipcode column to match zipcode column name in df
df3 = df3.rename(index=str, columns={"Zip Code": "zipcode"})


# In[14]:


df3


# In[15]:


#look at the type of the column
print(type(df3['zipcode']))


# In[16]:


#read in the demographic averages by geographic location dataset from nyc.gov
df4 = pd.read_excel('dempercents.xlsx')


# In[17]:


df4


# In[18]:


#merge df3 to df4 on the "Neighborhood" column
df5 = pd.merge(df3,
               df4,
               on='Neighborhood', 
               how='left')


# In[19]:


df5


# In[20]:


#rename df5 to neighborhoods
neighborhoods = df5


# In[21]:


neighborhoods


# In[22]:


#rename the "Borough_x" column to "Borough"
neighborhoods = neighborhoods.rename(index=str, columns={"Borough_x": "Borough"})

#drop the 'Borough_y' column
neighborhoods = neighborhoods.drop(columns='Borough_y')


# In[23]:


#look at the neighborhoods dataset to make sure the drop worked correctly
neighborhoods


# In[24]:


#this nested for loop splices the zip code column at the commas and then generates a new row for each zip code with all the other
#row elements copied into the new row
df_zip = pd.DataFrame(columns=neighborhoods.columns)
new_index = 0
#source for iterrows(): https://stackoverflow.com/a/16476974
for index, row in neighborhoods.iterrows():
    index = int(index)
    try:
        zipcodes = row['zipcode'].split(',')
    except AttributeError:
        # this means there's only one zip code so don't change anything in the row/no need to split 
        df_zip.loc[new_index] = neighborhoods.iloc[index].copy()#row
        new_index += 1
        continue
    # create a new row for each zip code 
    for zipcode in zipcodes:
        zipcode = zipcode.strip()
        #source:https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.copy.html
        new_row = neighborhoods.iloc[index].copy()#row.copy()
        new_row['zipcode']  = zipcode
        #at the new location for each new index copy a new row which is a copy of the old row but with single zip replacement
        #source: https://stackoverflow.com/a/30990015
        df_zip.loc[new_index] = new_row
        #need to increment each new index for each zip code since we don't want to overwrite the same row
        new_index += 1
    
df_zip


# In[25]:


#merge df_zip with the medicare df
df6 = pd.merge(df_zip,
               df,
               on='zipcode', 
               how='left')


# In[26]:


df6


# In[27]:


#I decided to drop all observations with missing values for zip codes. source for dropna: https://stackoverflow.com/a/36506759
df7 = df6.dropna(subset=['zipcode'])


# In[28]:


df7


# In[29]:


#keep columns of interest
df7 = df6[['Borough','Neighborhood','zipcode','Percent Fair or Poor Health', 'Percent Diabetes', 'providertype','averagemedicarestandardizedamoun','averagemedicarepaymentamount','averagemedicareallowedamount','numberofdistinctmedicarebenefici','numberofmedicarebeneficiaries','medicareparticipationindicator', 'numberofservices']]


# In[30]:


#eventually I decided to drop all observations which included a missing value
df8 = df7.dropna()


# In[31]:


df8


# In[32]:


#to avoid settingwithcopywarning generated by pandas following the previous zip code string splicing step, export df8
#as a csv file and re-import.
df8.to_csv(r'C:\Users\krygi\Documents\mailman_fall_2018\Fall 2018 Python Course\finaldataset.csv')


# In[33]:


#read the csv file back into jupyter
df8 = pd.read_csv('finaldataset.csv')
df8


# In[34]:


#this previous step caused the generation of a  new index column, 'unnamed: 0'. drop this column.
df8 = df8.drop(columns='Unnamed: 0')

df8


# In[35]:


from collections import Counter
providers = Counter()
for index, row in df8.iterrows():
    providers[row['zipcode']] += 1 
providers
# providers per zipcode in above counter


# In[42]:


#source for nyc zip codes: https://data.cityofnewyork.us/widgets/i8iw-xf4u


# In[40]:


percent_diab = dict()
for index, row in df8.iterrows():
    percent_diab[row['zipcode']] = row['Percent Diabetes'] 
percent_diab

merged_list = list()
for zipcode, numproviders in providers.items():
    merged_tuple = (zipcode, numproviders, percent_diab[zipcode])
    merged_list.append(merged_tuple)
df_gis = pd.DataFrame(merged_list, columns=['Zipcode', 'Number of Providers', 'Percent Diabetes'])
df_gis


# In[ ]:


nyc = geopandas.read_file('nyc_zip.shp')
nyc.plot()
