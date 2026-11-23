# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 11:45:14 2021

@author: impy2

Extract the seasonal cycle anomalies from the data to remove the seasonal
cyle from considerations and performing variance and autocorrelation calculations
"""
from pathlib import Path
import pandas as pd
import netCDF4 as nc
import numpy as np
from scipy.stats import variation
import statsmodels.tsa.stattools
# from auto_corr import auto_corr
from scipy import stats
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.io import savemat
################# Specify the experiment and models ################

experiment = '1pctCO2'
variant_id = 'r1i1p1f1'

################# Specify variable of interest ######################
# var2 is the same as var but all lower case
var = 'cVeg' # or treeFrac
var2 = 'cveg' # or treefrac

# var='tas'
# var2=var

flag_monthly=True
if flag_monthly:
    dir_name_append='_monthly'
    file_name_append='_mon'
else:
    dir_name_append=''
    file_name_append=''

############## Specify units of variable ###########################
units = '$kg/m^2$'

################# Specify model here ################################## 
model ='EC-Earth3-Veg'
model = 'GFDL-ESM4'
# model = 'MPI-ESM1-2-LR'
model = 'NorCPM1'
model='TaiESM1'
# model = 'SAM0-UNICON'
# model = 'UKESM1-0-LL'

print('Model: '+model)

############# Specif the longitude and latitude of the tipping point you wish to extract #########
# latitude = -5
# longitude = -65

latitude = 0
longitude = -60

######################## choose how much to calculate ########################
monthly_autocorr = True # True
diff_autocorr = True #True



# Specific entries for the 3 models initially used
if model == 'EC-Earth3-Veg':

    date_range = '1850-2000'
    total_years = 151
    
elif model == 'GFDL-ESM4':
    #modified to fit date range on downloaded data 
    date_range = '1850-1999'
    total_years = 150
    
elif model == 'MPI-ESM1-2-LR':
    
    date_range = '1850-2014'
    total_years = 165

elif model == 'NorCPM1':
    
    date_range = '1850-2013'
    total_years = 164

elif model == 'TaiESM1':
    
    date_range = '1850-2000'
    total_years = 150

elif model == 'SAM0-UNICON':
    
    date_range = '1850-1999'
    total_years = 150
    
elif model == 'UKESM1-0-LL':
    date_range = '1850-2000'
    total_years = 150
    
##################### Set RELDIFF True if taking relative differennce #################
##################### False if absolute difference ####################################    
RELDIFF = False

# Is variable measured in per second?
PERSEC = False
    
############ Specify name of directory of data which you want to plot #################
region = 'Amazon'
# region = 'World'

############ Specify name of directory of that stores the figures #################
region2 = 'Amazon'
# region2 = 'World'

# Window length used to calculate abrupt shift over
wl = 15

################## Specify path to processed data directory #####################
path = 'P:/09442_PREDICT_ESA/Data/CMPI6/'+var+'/'+experiment+'/Processed_data_Parry_2022'+dir_name_append+'/'+region+'/'

################## Specify path to analysis data directory #####################
path2 = 'P:/09442_PREDICT_ESA/Data/CMPI6/'+var+'/'+experiment+'/Analysis_data_Parry_2022'+'/'+region2+'/'

################## Specify path to statistical data directory #####################
path3= 'P:/09442_PREDICT_ESA/Data/CMPI6/'+var+'/'+experiment+'/Statistical_data_Parry_2022'+dir_name_append+'/'+region+'/'

# File name of interpolated data
fname = path+var+'_'+model+'_'+experiment+'_'+variant_id+'_'+date_range+file_name_append+'_'+region+'.nc'
fname = Path(fname)

# # Load in data
f = nc.Dataset(fname,'r')
mat = loadmat(path2+var+'_'+model+'_as_grads_wl'+str(wl)+'_data_'+experiment+'_'+region2+'.mat')
print(path2+var+'_'+model+'_as_grads_wl'+str(wl)+'_data_'+experiment+'_'+region2+'.mat')

#extract indicies of lon and lat in the matrices 
lon = np.array(f.variables['lon'])
lon_point = np.where(lon==longitude)

print('lon', lon_point, lon[lon_point], longitude)

lat = np.array(f.variables['lat'])
lat_point = np.where(lat==latitude)

print('lat', lat_point, lat[lat_point], latitude)

# Extract data and if measured in per second convert to per year
if PERSEC:
    x = f.variables[var2][:]*3600*24*360
else:
    x = f.variables[var2][:]

# Close dataset
f.close()

data = x[:, lat_point, lon_point]
print('data shape',np.shape(data))
data = data.flatten()
print('data shape',np.shape(data))
print('data size',data.size,np.size(data))
t = np.arange(1, data.size+1)

co2_start = 284.3186666723341
co2 = np.zeros(data.size)
for k in range(data.size):
    co2[k] = co2_start*(1.01**(k))

co2_start = 284.3186666723341
co2 = np.zeros(int(data.size/12))
for k in range(int(data.size/12)):
    co2[k] = co2_start*(1.01**k)

    
    
#extracting the CO2 conc and time point at which abrupt shift is detected 
co2_tip = mat['co2_tip']
co2_at_tip = co2_tip[lat_point, lon_point]
tip_index = np.where(co2==co2_at_tip)
time_at_tip = t[tip_index[1]] 
print('t size', np.size(t), tip_index, t[tip_index[1]*12])

#cut off the dataset and time series where the tipping point occurs
#including adjustment for monthly datapoints
print(tip_index)
if (np.isscalar(tip_index[1])==False) & (len(tip_index[1])>=1):
    a = int(tip_index[1][0]*12)#-12
else:
    a = int(tip_index[1]*12)#-12
# a = 80*12
print('a',a,a/12.)
dataf = data[0:a]
cveg_data = data[0:a]
t = np.arange(1, dataf.size+1)
print(dataf.size)

if monthly_autocorr == True:
    ####################### perform autocorrelation on the monthly data ##################
    window = 360
    ttot = np.size(t)
    mwind = ttot-window

    print(window,ttot,mwind)

    ar1_1 = np.zeros(mwind)
    stdev=np.zeros(mwind)
    ar1=np.zeros(mwind)
    skew=np.zeros(mwind)
    t1=t[0:mwind]
    stdev_d=np.zeros(mwind)
    ar1_d=np.zeros(mwind)
    skew_d=np.zeros(mwind)
    var1 = np.zeros(mwind)
    var_d = np.zeros(mwind)
    
    for m in range (0, mwind):
        m1 = m
        m2 = m+window
        veg = dataf[m1:m2]
        time = t[m1:m2]
        ####################### remove seasonal cycle ##############################
        #create arrays of data point indicies for each month
        month_points = np.zeros((12, 30))
        monthly_data = np.zeros((12,30))
        mon_avr = np.zeros(12)
        data2 = np.zeros(360)
        
        # extract monthly data points from the data
        for j in range (0,12):
            month_points[j, :] = np.arange(j, veg.size, 12)
            for i in range (0,30):
                monthly_data[j,i] = veg[int(month_points[j,i])]
                
            # find the average of each month
            mon_avr[j] = np.average(monthly_data[j,:])
        
         #subtract the average from each data point
        for j in range (0, 12):
            for i in range (0, 30):
                       data2[int(month_points[j,i])] = veg[int(month_points[j,i])] - mon_avr[j]
        
        time = np.arange(0, np.size(data2))
        plt.plot(time, data2)
        
        ###################### signal detrend ##########################
        b0, a0, r0, p0, e0 = stats.linregress(time,data2)
        dx=data2-(a0+b0*time) 
        
        #################### calculate statistics ###################
        stdev[m]=np.std(dx)
        var1[m] = stdev[m]**2
        # print(statsmodels.tsa.stattools.acf(dx, nlags=1,result_object=True,adjusted=True))
        # ar1_x = statsmodels.tsa.stattools.acf(dx, nlags=1, adjusted=False, fft=False)[1]

        # temp=dx-dx.mean()
        # lag1_manual = np.dot(temp[1:], temp[:-1]) / np.dot(temp,temp)

        # phi = np.sum(temp[1:] * temp[:-1]) / np.sum(temp**2)
        # noise_std = np.sqrt(np.var(temp) * (1 - phi**2))  

        def ar1_ols(window):
            """OLS slope of x[t] vs x[t-1]; can exceed 1.0 in trending windows."""
            x = np.asarray(window, dtype=float)
            x_prev, x_curr = x[:-1], x[1:]
            x_prev_anom = x_prev - np.mean(x_prev)
            x_curr_anom = x_curr - np.mean(x_curr)
            return float(np.sum(x_prev_anom * x_curr_anom) / np.sum(x_prev_anom**2))  

        ar1_x=ar1_ols(dx)

        # r = np.correlate(temp, temp, mode="full")[len(dx) - 1:]
        # lag1_numpy = r[1]/r[0]   
        # print(ar1_x, lag1_numpy, lag1_manual)

        # auto_corr(dx,1)
        # print('hereh',statsmodels.tsa.stattools.acf(dx, nlags=1,adjusted=True))
        # print(dkfsj)
        ar1_1[m]=ar1_x 
        skew_x=stats.skew(dx, bias=True)
        skew[m]=skew_x

print('ar1_1',np.size(ar1_1))

if diff_autocorr == True:    
    #################### calculate the change in vegetation carbon ###############
    data = pd.Series(data)
    veg_flux = data.diff()
    veg_flux = veg_flux.to_numpy()
    
    #################### cut off data at abrupt shift ############################
    veg_flux_f = veg_flux[0:a]
    flux_t = np.arange(1, veg_flux_f.size+1)

    #################### calculate variance and autocorrelation ##################
    window = 360
    ttot = np.size(flux_t)
    mwind = ttot-window
    ar1 = np.zeros(mwind)
    stdev=np.zeros(mwind)
    ar1_2=np.zeros(mwind)
    t1=flux_t[0:mwind]
    var2 = np.zeros(mwind)
    skew_d=np.zeros(mwind)
 
    for m in range (0, mwind):
        m1 = m
        m2 = m+window
        veg = veg_flux_f[m1:m2]
        time = flux_t[m1:m2]
        ####################### remove seasonal cycle ##############################
        #create arrays of data point indicies for each month
        month_points = np.zeros((12, 30))
        monthly_data = np.zeros((12,30))
        mon_avr = np.zeros(12)
        data_3 = np.zeros(360)
                
        # extract monthly data points from the data
        for j in range (0,12):
            month_points[j, :] = np.arange(j, veg.size, 12)
            for i in range (0,30):
                monthly_data[j,i] = veg[int(month_points[j,i])]
                
            # find the average of each month
            mon_avr[j] = np.average(monthly_data[j,:])
        
          #subtract the average from each data point
        for j in range (0, 12):
            for i in range (0, 30):
                        data_3[int(month_points[j,i])] = veg[int(month_points[j,i])] - mon_avr[j]
        
        ################## signal detrend ###################
        b0, a0, r0, p0, e0 = stats.linregress(time,data_3)
        dx=data_3-(a0+b0*time)
        ################# calculate statistics ##################
        stdev[m]=np.std(dx)
        var2[m] = stdev[m]**2
        # ar1_x, dar1_x = auto_corr(dx,1)
        ar1_x = statsmodels.tsa.stattools.acf(dx, nlags=1)[1]
        ar1_2[m]=ar1_x 
        skew_x=stats.skew(dx, bias=True)
        skew_d[m]=skew_x

print('ar1_2',np.size(ar1_2))

#Make sure variables for saving exist, if not assign them to None
try: cveg_data
except: cveg_data = np.ones(1,dtype=None)
try: veg_flux_f
except: veg_flux_f = np.ones(1,dtype=None)
try: ar1_1
except: ar1_1 = np.ones(1,dtype=None)
try: ar1_2
except: ar1_2 = np.ones(1,dtype=None)
try: var1
except: var1 = np.ones(1,dtype=None)
try: var2
except: var2 = np.ones(1,dtype=None)
try: skew
except: skew = np.ones(1,dtype=None)
try: skew_d
except: skew_d = np.ones(1,dtype=None)


################## save data as a mat file ################################
# Create dictionary of data to save                
mdic = {'cveg':cveg_data, 'cflux':veg_flux_f, 'ar1': ar1_1, 'flux_ar1': ar1_2, 'var': var1, 'flux_var': var2, 'skew':skew, 'skew_d':skew_d}

############# Save data as a matifle - Specify filename #############
savemat(path3+var+'_'+model+'_'+experiment+'_'+region2+'_lat'+str(latitude)+'_lon'+str(longitude)+'_statistical_data.mat', mdic)