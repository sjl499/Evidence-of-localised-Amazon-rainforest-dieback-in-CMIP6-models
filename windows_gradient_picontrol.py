# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 12:01:16 2021

@author: Paul

Generate control run data relevant for determining abrupt shifts using the 
detection algorithm third criterion.
"""

import netCDF4 as nc
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.io import savemat

# Name of control run experiment
experiment = 'piControl'#'1pctCO2'

################# Specify model here ################################## 
model ='EC-Earth3-Veg'
# model = 'GFDL-ESM4'
# model = 'MPI-ESM1-2-LR'
# model = 'NorCPM1'
# model='TaiESM1'
# model = 'SAM0-UNICON'
# model = 'UKESM1-0-LL'

print('Model: '+model)

################ Specify variant_id of model used ###################
variant_id = 'r1i1p1f1'

################# Specify variable of interest ######################
# var2 is the same as var but all lower case
var = 'cVeg'
var2 = 'cveg'

# var = 'tas'
# var2 = 'tas'

if var == 'tas':
    dir_name_append='_monthly'
    file_name_append='_mon'
else:
    dir_name_append=''
    file_name_append=''

################# Specify date range in file name #####################
# date_range = '0000-1000'
# Specific entries for the 3 models initially used
if model == 'EC-Earth3-Veg':

    grid_label = '_gr'
    date_range = []
    if experiment=='1pctCO2':
        for k in np.arange(151):
            date_range.extend([str(1850+k)+'01-'+str(1850+k)+'12'])
        total_years = 151
        date_range2 = '1850-2000'
    else:
        print('Only first 500 years of dataset being read in')
        for k in np.arange(500):
            date_range.extend([str(1850+k)+'01-'+str(1850+k)+'12'])
        total_years = 500
        date_range2 = '1850-2349'

elif model == 'GFDL-ESM4':
    
    grid_label = '_gr1'
    if experiment=='1pctCO2':
        date_range = ['000101-010012', '010101-015012']
        total_years = 150
        date_range2 = '1850-1999'
    elif experiment=='piControl':
        date_range = ['000101-010012', '010101-020012', 
                       '020101-030012', '030101-040012',
                       '040101-050012']
        total_years = 500
        date_range2 = '1850-2349'
    else:
        raise ValueError("Date ranges for experiment unknown")
    
elif model == 'MPI-ESM1-2-LR':
    
    grid_label = '_gn'
    date_range = []
    if experiment=='1pctCO2':
        for k in np.arange(8):
            date_range.extend([str(1850+k*20)+'01-'+str(1850+((k+1)*20)-1)+'12'])
        date_range.extend(['201001-201412'])
        total_years = 165
        date_range2 = '1850-2014'
    elif experiment=='piControl':
        print('Only first 500 years of dataset being read in')
        # for k in np.arange(50):
        for k in np.arange(25):
            date_range.extend([str(1850+k*20)+'01-'+str(1850+((k+1)*20)-1)+'12'])
        # date_range.extend(['201001-201412'])
        # total_years = 1000
        # date_range2 = '1850-2850'
        total_years = 500
        date_range2 = '1850-2350'
    else:
        raise ValueError("Date ranges for experiment unknown")
        

elif model == 'NorCPM1':
    grid_label = '_gn'

    if experiment=='1pctCO2':
        date_range = ['000102-016412']
        total_years = 164
        date_range2 = '1850-2013'
    elif experiment=='piControl':
        date_range = ['000102-010012',
                       '010101-020012',
                       '020101-030012',
                       '030101-040012',
                       '040101-050012'
                       ]
        total_years = 501
        date_range2 = '1850-2350'
    else:
        raise ValueError('Date range for experiment unknown')

elif model == 'TaiESM1':
    grid_label = '_gn'
    if experiment=='1pctCO2':
        date_range = ['000102-015012']
        total_years = 150
        date_range2 = '1850-2000'#
    elif experiment=='piControl':
        date_range = ['020102-030012',
                        '030101-040012',
                        '040101-050012',
                        '050101-060012',
                        '060101-070012'
                        ]
        total_years = 500
        date_range2 = '1850-2349'
    else:
        raise ValueError('Date range for experiment unknown')
    
elif model == 'SAM0-UNICON':
    grid_label = '_gn'
    date_range = []
    if experiment=='1pctCO2':
        for k in np.arange(15):
            date_range.extend([str(1850+(k*10))+'01-'+str(1859+(k*10))+'12'])
        total_years = 150
        date_range2 = '1850-1999'
    elif experiment=='piControl':
        print('Only first 500 years of dataset being read in')
        for k in np.arange(50):
            if k<28:
                date_range.extend([str((k*10+1)).zfill(4)+'01-'+str(((k+1)*10)).zfill(4)+'12'])
            else:
                date_range.extend([str((k*10+1)).zfill(4)+'01_'+str(((k+1)*10)).zfill(4)+'12'])
        # total_years = 700
        # date_range2 = '1850-2550'#
        total_years = 500
        date_range2 = '1850-2350'#
        print(date_range)
    else:
        raise ValueError('Date range for experiment unknown')
        
    
elif model == 'UKESM1-0-LL':
    grid_label = '_gn'
    if experiment=='1pctCO2':
        date_range = ['185001-194912', 
                    '195001-199912']
        total_years = 150
        date_range2 = '1850-2000'#
    elif experiment=='piControl':
        date_range = ['196001-204912',
                       '205001-214912',
                       '215001-224912',
                       '225001-234912',
                       '235001-244912']#,
                    #    '245001-254912',
                    #    '255001-264912',
                    #    '265001-274912',
                    #    '275001-284912',
                    #    '285001-294912',
                    #    '295001-304912',
                    #    '305001-305912',
                    #    '306001-314912',
                    #    '315001-324912',
                    #    '325001-334912',
                    #    '335001-344912',
                    #    '345001-354912',
                    #    '355001-364912',
                    #    '365001-374912',
                    #    '375001-383912']
        # total_years = 1880
        # date_range2 = '1960-3840'#
        total_years = 490
        date_range2 = '1960-2450'#
        print(date_range)
    else:
        raise ValueError('Date range for experiment unknown')

# Is variable measured in per second?
PERSEC = False

####### Specify name of directory of data which you want to run algorithm on ############
region = 'Amazon'#'World'#
region= 'World'

############ Specify name of directory of that stores analysis data #################
region2 = 'Amazon'#'World'#
region2 = 'World'

################## Specify path to processed data directory #####################
path = 'P:/09442_PREDICT_ESA/Data/CMPI6/'+var+'/'+experiment+'/Processed_data_Parry_2022'+dir_name_append+'/'+region+'/'

################## Specify path to analysis data directory #####################
path2 = 'P:/09442_PREDICT_ESA/Data/CMPI6/'+var+'/'+experiment+'/Analysis_data_Parry_2022'+dir_name_append+'/'+region2+'/'

# Determine window length for period of abrupt shift
wl = 15

# File name of the data
fname = path+var+'_'+model+'_'+experiment+'_'+variant_id+'_'+date_range2+file_name_append+'_'+region+'.nc'

# Extract data
f = nc.Dataset(fname,'r')

# Extract longitudes and latitudes
longitude = f.variables['lon'][:]
latitude = f.variables['lat'][:]

# Extract variable data and convert to yearly units if applicable
if PERSEC:
    x = f.variables[var2][:,:,:]*3600*24*360
else:
    x = f.variables[var2][:,:,:]

# Close dataset
f.close()

# Determine dimensions of 3d array though use only first 150 years of data
nt = int(len(x[:,0,0]))
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

# print(latitude)
# print(f2.variables['latitude'][:])

# print(longitude)
# print(f2.variables['longitude'][:])

# print('values before mask')
# print(sftlf[80,112])
# print(x[-400:,80,112])

sftlf_mask = np.broadcast_to(sftlf, (nt, ny,nx))



x[np.where(sftlf_mask <= 0)] = np.nan  
x[np.where(~np.isfinite(sftlf_mask))] = np.nan
f2.close()

# print('values after mask')
# print(x[-400:,80,112])

# Time parameters
t2 = np.linspace(0, wl-1, wl)

# Initialise array
control_grads = np.zeros((nt,ny,nx))

# Initialise counter
count = 0

# Create meshgrid of longitude and latitude
Lon, Lat = np.meshgrid(longitude, latitude)

# Loops over each gridpoint    
for i in range(nx):
    for j in range(ny):
        
        # If ocean all arrays are assigned a NaN 
        if not np.isfinite(x[0,j,i]) or all(x[:,j,i] == 0.0):
            control_grads[:,j,i] = np.nan*np.ones(nt)
        
        else:

            # Loop over a sliding window
            for k in range(nt-wl):
                
                # Sliding window of variable
                x2 = x[k:wl+k,j,i]
                
                # Linear regression over sliding window
                regressor2 = LinearRegression()  
                regressor2.fit(t2.reshape(-1,1), x2)
                
                # From linear regression determine absolute change over sliding window
                # print(regressor2.coef_)
                control_grads[k,j,i] = regressor2.coef_[0]


ind=np.where(np.isnan(control_grads)==False)
print(control_grads[ind])

# Create dictionary of data to save                
mdic = {'Lon': Lon, 'Lat': Lat, 'control_grads': control_grads}

############# Save data as a matifle - Specify filename #############
savemat(path2+var+'_'+model+'_wl'+str(wl)+'_data_'+experiment+'_'+region2+'.mat', mdic)
