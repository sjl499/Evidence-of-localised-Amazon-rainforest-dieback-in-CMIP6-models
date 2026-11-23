# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 09:44:28 2021

@author: Paul

Generate data for determining abrupt shifts. 
New statistics used: fraction of abrupt shift to overall shift and size of 
abrupt shift over 15 years of time series
"""

import netCDF4 as nc
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.io import savemat


experiment = '1pctCO2'
# experiment = 'piControl'
variant_id = 'r1i1p1f1'

################# Specify variable of interest ######################
var = 'cVeg'
var2 = 'cveg'

flag_monthly=True
if flag_monthly:
    dir_name_append='_monthly'
    file_name_append='_mon'
else:
    dir_name_append=''
    file_name_append=''

################# Specify model here ################################## 
model ='EC-Earth3-Veg'
model = 'GFDL-ESM4'
# model = 'MPI-ESM1-2-LR'
model = 'NorCPM1'
model='TaiESM1'
# model = 'SAM0-UNICON'
# model = 'UKESM1-0-LL'

print('Model: '+model)

################# Specify date range of model ########################
# Specific entries for the 3 models initially used
if model == 'EC-Earth3-Veg':

    date_range = '1850-2000'

elif model == 'GFDL-ESM4':
    
    date_range = '1850-1999'
    
elif model == 'MPI-ESM1-2-LR':
    
    date_range = '1850-2014'

elif model == 'NorCPM1':
    date_range = '1850-2013'

elif model == 'TaiESM1':
    date_range = '1850-2000'

elif model == 'SAM0-UNICON':
    date_range = '1850-1999'

elif model =='UKESM1-0-LL':
    date_range = '1850-2000'


# Is variable measured in per second?
PERSEC = False

####### Specify name of directory of data which you want to run algorithm on ############
region = 'Amazon'#'World'#
region = 'World'

############ Specify name of directory of that stores analysis data #################
region2 = 'Amazon'#'World'#
region2 = 'World'

path = 'P:/09442_PREDICT_ESA/Data/CMPI6/'+var+'/'+experiment+'/Processed_data_Parry_2022'+dir_name_append+'/'+region+'/'

################## Specify path to analysis data directory #####################
path2 = 'P:/09442_PREDICT_ESA/Data/CMPI6/'+var+'/'+experiment+'/Analysis_data_Parry_2022'+dir_name_append+'/'+region2+'/'

# Determine window length for period of abrupt shift
wl = 15

# File name of the data
fname = path+var+'_'+model+'_'+experiment+'_'+variant_id+'_'+date_range+file_name_append+'_'+region+'.nc'
# Extract data
f = nc.Dataset(fname,'r')

# Extract longitudes and latitudes
longitude = f.variables['lon'][:]
latitude = f.variables['lat'][:]

# Extract variable data and convert to yearly units if applicable
if PERSEC:
    x = f.variables[var2][:150,:,:]*3600*24*360
else:
    x = f.variables[var2][:150,:,:]

# Close dataset
f.close()

# Determine dimensions of 3d array though use only first 150 years of data
nt = 150
ny = int(len(x[0,:,0]))
nx = int(len(x[0,0,:]))

############ Specify path to land mask ######################
if region=='Amazon':
    fname2 = r'C:\Users\simloc\OneDrive - UKCEH\Documents\PREDICT (ESA)\PREDICT-uncertainty-codes\Geographical_masks\NSA_grid_land_mask.nc'
else:
    fname2 = r'C:\Users\simloc\OneDrive - UKCEH\Documents\PREDICT (ESA)\PREDICT-uncertainty-codes\Geographical_masks\Parry_2022_SA_grid_land_mask.nc'


# Load in land mask and remove any ocean values
f2 = nc.Dataset(fname2,'r')
sftlf = f2.variables['mask'][:]

sftlf_mask = np.broadcast_to(sftlf, (nt, ny,nx))
x[np.where(sftlf_mask <= 0)] = np.nan  
x[np.where(~np.isfinite(sftlf_mask))] = np.nan
f2.close()


# Time parameters
tstart = 0                         # Start time
tend = tstart+nt-1                           # End time
t = np.linspace(tstart, tend, nt)     # Time values
t2 = np.linspace(0, wl-1, wl)

# Create array of CO2 for 1pctCO2 run
co2_start = 284.3186666723341
co2 = np.zeros(164)
for k in range(164):
    co2[k] = co2_start*(1.01**k)

# Initialise arrays
t_ind = np.zeros((ny,nx))
as_grad = np.zeros((ny,nx))
as_change = np.zeros((ny,nx))
co2_tip = np.zeros((ny,nx))
ovr_change = np.zeros((ny,nx))
as_grads = np.zeros((nt-wl,ny,nx))

# Initialise counter
count = 0

# Create meshgrid of longitude and latitude
Lon, Lat = np.meshgrid(longitude, latitude)

# Loops over each gridpoint    
for i in range(nx):
    for j in range(ny):

                # If ocean all arrays are assigned a NaN 
        if not np.isfinite(x[0,j,i]) or all(x[:,j,i] == 0.0):
            t_ind[j,i], as_grad[j,i], as_grads[:,j,i], co2_tip[j,i], ovr_change[j,i] = np.nan, np.nan, np.nan, np.nan, np.nan
        
        else:

            # Loop over a sliding window
            for k in range(nt-wl):
                
                # Sliding window of variable
                x2 = x[k:wl+k,j,i]
                
                # Linear regression over sliding window
                regressor2 = LinearRegression()  
                regressor2.fit(t2.reshape(-1,1), x2)
                
                # From linear regression determine absolute change over sliding window
                as_grads[k,j,i] = regressor2.coef_[0]
                                        
            # Store index of sliding window with maximum absolute change
            t_ind[j,i] = np.argmax(np.abs(as_grads[:,j,i]))
            
            # Store the max change (+ve or -ve) and corresponding CO2 value
            as_grad[j,i] = as_grads[int(t_ind[j,i]),j,i]
            co2_tip[j,i] = co2[int(t_ind[j,i]+wl/2)]
            as_change[j,i] = np.nanmean(x[int(t_ind[j,i]+wl-2):int(t_ind[j,i]+wl+3),j,i]) - np.nanmean(x[int(np.maximum(t_ind[j,i]-2,0)):int(t_ind[j,i]+3),j,i])
            
            # Store overall gradient 
            ovr_change[j,i] = np.nanmean(x[-5:,j,i]) - np.nanmean(x[:5,j,i])#regressor.coef_


# Create dictionary of data to save                
mdic = {'Lon': Lon, 'Lat': Lat, 'as_grad': as_grad, 'as_change': as_change, 'as_grads': as_grads, 'co2_tip': co2_tip, 'ovr_change': ovr_change}

# ############# Save data as a matifle - Specify filename #############
savemat(path2+var+'_'+model+'_as_grads_wl'+str(wl)+'_data_'+experiment+'_'+region2+'.mat', mdic)

