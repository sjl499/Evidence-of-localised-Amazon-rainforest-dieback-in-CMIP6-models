# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 10:14:22 2020

@author: pdlr201

Script to plot changes in 1pctCO2 CMIP6 data runs using imshow
"""
from pathlib import Path
import iris
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
#from Abrupt_detection import as_detect, as_type
from netCDF4 import Dataset
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
from scipy.stats import variation


experiment = '1pctCO2'
variant_id = 'r1i1p1f1'

################# Specify variable of interest ######################
# var2 is the same as var but all lower case
var = 'cVeg' # or treeFrac
var2 = 'cveg' # or treefrac

############## Specify units of variable ###########################
units = '$kg/m^2$'

################# Specify model here ################################## 
model ='EC-Earth3-Veg'
# model = 'GFDL-ESM4'
# model = 'MPI-ESM1-2-LR'
# model = 'NorCPM1'
# model='TaiESM1'
# model = 'SAM0-UNICON'
# model = 'UKESM1-0-LL'

print('Model: '+model)

# Specific entries for the 3 models initially used
if model == 'EC-Earth3-Veg':

    date_range = '1850-2000'
    
elif model == 'GFDL-ESM4':
    #modified to fit date range on downloaded data 
    date_range = '1850-1999'
    
elif model == 'MPI-ESM1-2-LR':
    
    date_range = '1850-2014'

elif model == 'NorCPM1':
    
    date_range = '1850-2013'

elif model == 'TaiESM1':
    
    date_range = '1850-2000'

elif model == 'SAM0-UNICON':
    
    date_range = '1850-1999'
    
elif model == 'UKESM1-0-LL':
    date_range = '1850-2000'
    
##################### Set RELDIFF True if taking relative differennce #################
##################### False if absolute difference ####################################    
RELDIFF = False

# Is variable measured in per second?
PERSEC = False

############ Specify name of directory of data which you want to plot #################
region = 'Amazon'

############ Specify name of directory of that stores the figures #################
region2 = 'Amazon'

################## Specify path to processed data directory #####################
path = 'P:/09442_PREDICT_ESA/Data/CMPI6/'+var+'/'+experiment+'/Processed_data_Parry_2022/'+region+'/'


# Longitude, latitude min, max, step and figure size for region of interest
if region == 'World':
    lonmin = -180-0.5
    lonmax = 180+0.5
    latmin = -60-0.5
    latmax = 80+0.5
    lonstep = 10
    latstep = 10
    figsizes = (19, 9.5)
elif region == 'Amazon':
    lonmin = -83-0.5
    lonmax = -35+0.5
    latmin = -20-0.5
    latmax = 13+0.5
    lonstep = 10
    latstep = 10
    figsizes = (6, 5.75)


# File name of interpolated data
fname = path+var+'_'+model+'_'+experiment+'_'+variant_id+'_'+date_range+'_'+region+'.nc'
fname = Path(fname)

# Load in data
f = nc.Dataset(fname,'r')

# Extract longitude and latitude
longitude = f.variables['lon'][:]
latitude = f.variables['lat'][:]

# Extract data and if measured in per second convert to per year
if PERSEC:
    x = f.variables[var2][:]*3600*24*360
else:
    x = f.variables[var2][:]
    
# Close dataset
f.close()

# Obtain dimension sizes
nt = int(len(x[:,0,0]))
ny = int(len(x[0,:,0]))
nx = int(len(x[0,0,:]))

############ Specify path to land mask ######################
fname2 = r'C:\Users\simloc\OneDrive - UKCEH\Documents\PREDICT (ESA)\PREDICT-uncertainty-codes\Geographical_masks\NSA_grid_land_mask.nc'
fname2 = Path(fname2)

# Load in land mask and remove any ocean values
f2 = nc.Dataset(fname2,'r')
mask_latitude = f2.variables['latitude'][:]
mask_longitude = f2.variables['longitude'][:]
sftlf = np.ma.filled(f2.variables['mask'][:].astype(float), np.nan)

# Check that the mask and data use the same grid before applying the mask.
if sftlf.shape != (ny, nx):
    raise ValueError(f'Mask shape {sftlf.shape} does not match data grid {(ny, nx)}')
if latitude.shape != mask_latitude.shape or not np.allclose(
        latitude, mask_latitude, rtol=0, atol=1e-6):
    raise ValueError('Latitude of data and mask do not match')
if longitude.shape != mask_longitude.shape or not np.allclose(
        longitude, mask_longitude, rtol=0, atol=1e-6):
    raise ValueError('Longitude of data and mask do not match')

land_mask = np.isfinite(sftlf) & (sftlf > 0)
x[:, ~land_mask] = np.nan
f2.close()

# Find mean of first 30 years and between 120 and 150 years per grid point 
x_hist = np.nanmean(x[:30,:,:],axis=0)
x_futr = np.nanmean(x[120:150,:,:],axis=0)

# Calculate absolute difference or relative difference and define colour intervals,
# colour maps
if RELDIFF:
    x_tot_change = (x_futr - x_hist)/x_hist*100
    vc = np.concatenate([[-100], np.arange(-90, -9, 40), np.arange(10, 101, 40), [100]])
    cmap_name = 'RdYlGn'#'RdBu'#'RdYlGn'#'PRGn'#'RdBu_r'
    cmap = plt.get_cmap(cmap_name,len(vc))
    colors1 = list(cmap(np.arange(len(vc))))
    cmap = colors.ListedColormap(colors1[:-1], "") 
    cmap.set_over(colors1[-1])     # set over-color to firstst color of list 
    norm = colors.BoundaryNorm(vc, cmap.N)
else:
    x_tot_change = (x_futr - x_hist)
    vc = np.concatenate([np.arange(-10, 0, 2.0), np.arange(2, 12, 2.0)])
    cmap_name = 'RdYlGn'#'RdBu'#'RdYlGn'#'PRGn'#'RdBu_r'
    cmap = plt.get_cmap(cmap_name,len(vc)+1)
    colors1 = list(cmap(np.arange(len(vc)+1)))
    cmap = colors.ListedColormap(colors1[1:-1], "")
    cmap.set_under(colors1[0])     # set under-color to last color of list 
    cmap.set_over(colors1[-1])     # set over-color to firstst color of list 
    norm = colors.BoundaryNorm(vc, cmap.N)

# Define colour intervals, and colour maps of 30 year mean plots
vr = np.arange(0, 30, step=5)
cmap_name2 = 'Greens'#'RdYlBu_r'#'YlGnBu'#'Greens'#'PRGn'#'RdBu_r'
cmap2 = plt.get_cmap(cmap_name2,len(vr))
if var == 'cVeg':
    colors2 = list(cmap2(np.arange(len(vr))))
    cmap2 = colors.ListedColormap(colors2[:-1], "")
    cmap2.set_over(colors2[-1])     # set over-color to last color of list 
norm2 = colors.BoundaryNorm(vr, cmap2.N)

############# Plotting the figures, specify where you want the figures saved ############
proj = ccrs.Mercator(central_longitude=-59, min_latitude=latmin, max_latitude=latmax)   

fig, ax = plt.subplots(subplot_kw=dict(projection=proj),figsize=figsizes)
ax.set_extent([lonmin ,lonmax, latmin, latmax], crs=ccrs.PlateCarree())   
ax.add_feature(cfeature.COASTLINE, zorder=10)
ax.set_xticks(np.arange(-80,-30,lonstep),crs=ccrs.PlateCarree())
ax.set_xticklabels(np.arange(-80,-30,lonstep))
ax.set_yticks(np.arange(-20,20,latstep),crs=ccrs.PlateCarree())
ax.set_yticklabels(np.arange(-20,20,latstep))
lon_formatter = cticker.LongitudeFormatter()
lat_formatter = cticker.LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)
ax.grid(linewidth=0.5, color='black', linestyle='--')
# im = ax.imshow(x_tot_change,cmap=cmap,norm=norm,transform=ccrs.PlateCarree(),extent=[lonmin ,lonmax, latmax, latmin])
im = ax.pcolormesh(
    longitude, latitude, x_tot_change,
    cmap=cmap, norm=norm,
    transform=ccrs.PlateCarree(),
    shading="auto"
)

if RELDIFF:
    cbar = fig.colorbar(im, spacing="proportional", pad=0.08, orientation='horizontal', extend='max')
    cbar.set_label('Relative change %')
    plt.title(model)
    fig.tight_layout()
    fig.savefig('P:/09442_PREDICT_ESA/Data/CMPI6/Parry_2022_Figures/Start_finish_change/'+var+'_tot_rel_change_'+experiment+'_'+model+'_'+region2+'.png', bbox_inches='tight')
else:
    cbar = fig.colorbar(im, spacing="proportional", pad=0.08, orientation='horizontal', extend='both')
    cbar.set_label(var+' overall absolute change ('+units+')')
    plt.title(model)
    fig.tight_layout()
    fig.savefig('P:/09442_PREDICT_ESA/Data/CMPI6/Parry_2022_Figures/Start_finish_change/'+var+'_tot_abs_change_'+experiment+'_'+model+'_'+region2+'.png', bbox_inches='tight')

fig, ax = plt.subplots(subplot_kw=dict(projection=proj),figsize=figsizes)
ax.set_extent([lonmin ,lonmax, latmin, latmax], crs=ccrs.PlateCarree())   
ax.add_feature(cfeature.COASTLINE, zorder=10)
ax.set_xticks(np.arange(-80,-30,lonstep),crs=ccrs.PlateCarree())
ax.set_xticklabels(np.arange(-80,-30,lonstep))
ax.set_yticks(np.arange(-20,20,latstep),crs=ccrs.PlateCarree())
ax.set_yticklabels(np.arange(-20,20,latstep))
lon_formatter = cticker.LongitudeFormatter()
lat_formatter = cticker.LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)
ax.grid(linewidth=0.5, color='black', linestyle='--')

x_hist_filtered = np.where(x_hist > 0, 20.0, np.nan)

# im = ax.imshow(x_hist,cmap=cmap2,norm=norm2,transform=ccrs.PlateCarree(),extent=[lonmin ,lonmax, latmax, latmin])
im = ax.pcolormesh(
    longitude, latitude, x_hist_filtered,
    cmap=cmap2, norm=norm2,
    transform=ccrs.PlateCarree(),
    shading="auto"
)
if var == 'cVeg':
    cbar = fig.colorbar(im, spacing="proportional", pad=0.08, orientation='horizontal',extend='max')
else:
    cbar = fig.colorbar(im, spacing="proportional", pad=0.08, orientation='horizontal')
cbar.set_label(var+' ('+units+')')
plt.title(model)
fig.tight_layout()
fig.savefig('P:/09442_PREDICT_ESA/Data/CMPI6/Parry_2022_Figures/Start_finish_change/'+var+'_start_'+experiment+'_'+model+'_'+region2+'.png', bbox_inches='tight')

fig, ax = plt.subplots(subplot_kw=dict(projection=proj),figsize=figsizes)
ax.set_extent([lonmin ,lonmax, latmin, latmax], crs=ccrs.PlateCarree())   
ax.add_feature(cfeature.COASTLINE, zorder=10)
ax.set_xticks(np.arange(-80,-30,lonstep),crs=ccrs.PlateCarree())
ax.set_xticklabels(np.arange(-80,-30,lonstep))
ax.set_yticks(np.arange(-20,20,latstep),crs=ccrs.PlateCarree())
ax.set_yticklabels(np.arange(-20,20,latstep))
lon_formatter = cticker.LongitudeFormatter()
lat_formatter = cticker.LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)
ax.grid(linewidth=0.5, color='black', linestyle='--')
# im = ax.imshow(x_futr,cmap=cmap2,norm=norm2,transform=ccrs.PlateCarree(),extent=[lonmin ,lonmax, latmax, latmin])
im = ax.pcolormesh(
    longitude, latitude, x_futr,
    cmap=cmap2, norm=norm2,
    transform=ccrs.PlateCarree(),
    shading="auto"
)
if var == 'cVeg':
    cbar = fig.colorbar(im, spacing="proportional", pad=0.08, orientation='horizontal',extend='max')
else:
    cbar = fig.colorbar(im, spacing="proportional", pad=0.08, orientation='horizontal')
cbar.set_label(var+' ('+units+')')
plt.title(model)
fig.tight_layout()

### specify location to save the figure ###
fig.savefig('P:/09442_PREDICT_ESA/Data/CMPI6/Parry_2022_Figures/Start_finish_change/'+var+'_end_'+experiment+'_'+model+'_'+region2+'.png', bbox_inches='tight')







