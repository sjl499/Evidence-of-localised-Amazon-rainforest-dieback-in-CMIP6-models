#- coding: utf-8 -*-
"""
Created on Mon Dec 16 09:01:27 2019

@author: pdlr201

Script to interpolate annual 1pctCO2 CMIP6 data onto 1 degree world grid for 
tas
"""
import iris
import numpy as np
import numpy.ma as ma
from iris.cube import Cube
# import netCDF4 as nc

def shiftlon(lon,lon_0):
    """returns original sequence of longitudes (in degrees) recentered
    in the interval [lon_0-180,lon_0+180]"""
    lon_shift = np.asarray(lon)
    lon_shift = np.where(lon_shift > lon_0+180, lon_shift-360 ,lon_shift)
    lon_shift = np.where(lon_shift < lon_0-180, lon_shift+360 ,lon_shift)
    itemindex = len(lon)-np.where(lon_shift[0:-1]-lon_shift[1:] >= 180)[0]
    return (np.roll(lon_shift,itemindex-1), itemindex-1)

temp_res = 'Amon'
experiment = '1pctCO2'
experiment = 'piControl'
variant_id = 'r1i1p1f1'

################# Specify variable of interest ######################
var = 'tas' # or treeFrac


#TESTING monthly cVeg data
temp_res = 'Lmon'
var = 'cVeg'

################# Specify model here ################################## 
model ='EC-Earth3-Veg'
# model = 'GFDL-ESM4'
# model = 'MPI-ESM1-2-LR'
# model = 'NorCPM1'
# model='TaiESM1'
# model = 'SAM0-UNICON'
# model = 'UKESM1-0-LL'

print('Model: '+model)

if model == 'EC-Earth3-Veg':

    grid_label = '_gr'
    date_ranges = []
    if experiment=='1pctCO2':
        for k in np.arange(151):
            date_ranges.extend([str(1850+k)+'01-'+str(1850+k)+'12'])
        total_years = 151
        date_range2 = '1850-2000'
    else:
        # for k in np.arange(1000):
        print('Only first 500 years of dataset being read in')
        for k in np.arange(500):
            date_ranges.extend([str(1850+k)+'01-'+str(1850+k)+'12'])
        
        # print(date_ranges)
        # total_years = 2001
        # date_range2 = '1850-3849'
        total_years = 500
        date_range2 = '1850-2349'

elif model == 'GFDL-ESM4':
    
    grid_label = '_gr1'
    if experiment=='1pctCO2':
        date_ranges = ['000101-010012', '010101-015012']
        total_years = 150
        date_range2 = '1850-1999'
    elif experiment=='piControl':
        date_ranges = ['000101-010012', '010101-020012', 
                       '020101-030012', '030101-040012',
                       '040101-050012']
        total_years = 500
        date_range2 = '1850-2349'
    else:
        raise ValueError("Date ranges for experiment unknown")
    
elif model == 'MPI-ESM1-2-LR':
    
    grid_label = '_gn'
    date_ranges = []
    if experiment=='1pctCO2':
        for k in np.arange(8):
            date_ranges.extend([str(1850+k*20)+'01-'+str(1850+((k+1)*20)-1)+'12'])
        date_ranges.extend(['201001-201412'])
        total_years = 165
        date_range2 = '1850-2014'
    elif experiment=='piControl':
        # for k in np.arange(50):
        print('Only first 500 years of dataset being read in')
        for k in np.arange(25):
            date_ranges.extend([str(1850+k*20)+'01-'+str(1850+((k+1)*20)-1)+'12'])
        # date_ranges.extend(['201001-201412'])
        # total_years = 1000
        # date_range2 = '1850-2850'

        total_years = 500
        date_range2 = '1850-2350'
    else:
        raise ValueError("Date ranges for experiment unknown")
        

elif model == 'NorCPM1':
    grid_label = '_gn'

    if experiment=='1pctCO2':
        date_ranges = ['000102-016412']
        total_years = 164
        date_range2 = '1850-2013'
    elif experiment=='piControl':
        date_ranges = ['000101-010012',
                                '010101-020012',
                                '020101-030012',
                                '030101-040012',
                                '040101-050012'
                                ]
        if var=='cVeg': date_ranges[0]='000102-010012' #Because this differs for unknown reasons
        total_years = 501
        date_range2 = '1850-2350'
    else:
        raise ValueError('Date range for experiment unknown')

elif model == 'TaiESM1':
    grid_label = '_gn'
    if experiment=='1pctCO2':
        date_ranges = ['000102-015012']
        total_years = 150
        date_range2 = '1850-2000'#
    elif experiment=='piControl':
        date_ranges = ['020101-030012',
                        '030101-040012',
                        '040101-050012',
                        '050101-060012',
                        '060101-070012'
                        ]
        if var=='cVeg': date_ranges[0]='020102-030012'
        total_years = 500
        date_range2 = '1850-2349'
    else:
        raise ValueError('Date range for experiment unknown')
    
elif model == 'SAM0-UNICON':
    grid_label = '_gn'
    date_ranges = []
    if experiment=='1pctCO2':
        for k in np.arange(15):
            date_ranges.extend([str(1850+(k*10))+'01-'+str(1859+(k*10))+'12'])
        total_years = 150
        date_range2 = '1850-1999'
    elif experiment=='piControl':
        print('Only first 500 years of dataset being read in')
        # for k in np.arange(70):
        ind_underscore=np.inf
        if var=='cVeg': ind_underscore=28

        for k in np.arange(50):
            if k<ind_underscore:
                date_ranges.extend([str((k*10+1)).zfill(4)+'01-'+str(((k+1)*10)).zfill(4)+'12'])
            else:
                date_ranges.extend([str((k*10+1)).zfill(4)+'01_'+str(((k+1)*10)).zfill(4)+'12'])
            
        # total_years = 700
        # date_range2 = '1850-2550'#
        total_years = 500
        date_range2 = '1850-2350'
        print(date_ranges)
    else:
        raise ValueError('Date range for experiment unknown')
        
    
elif model == 'UKESM1-0-LL':
    grid_label = '_gn'
    if experiment=='1pctCO2':
        date_ranges = ['185001-194912', 
                    '195001-199912']
        total_years = 150
        date_range2 = '1850-2000'#
    elif experiment=='piControl':
        print('Only first 490 years of dataset being read in')
        date_ranges = ['196001-204912',
                        '205001-214912',
                       '215001-224912',
                       '225001-234912',
                       '235001-244912']
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
        date_range2 = '1960-2450'
        print(date_ranges)
    else:
        raise ValueError('Date range for experiment unknown')

    
######################## Specify path to data ##########################
path = 'P:/09442_PREDICT_ESA/Data/CMPI6/'+var+'/'+experiment

######################## Specify directory of raw data ##################
raw_data = '/Original_data/'

######################## Specify directory of processed data ##################
processed_data = '/Processed_data_Parry_2022_monthly/'

############ Specify directory within processed data directory for the region interpolated #################
region = 'World'

# Define latitude and longitude (uses 1 degree by 1 degree grid) 
my_lats=['latitude',np.arange(-90,91,step=1)]
my_lons=['longitude',np.arange(-180,181,step=1)]

# Months in the year
freq = 12
chunk_size= 1

# Initialise counters
count = 0
sub_total_months = 0

# Loop through data files
for i in range(len(date_ranges)):
    
    # File name of data
    fname = path+raw_data+var+'_'+temp_res+'_'+model+'_'+experiment+'_'+variant_id+grid_label+'_'+date_ranges[i]+'.nc'

    # Load file contents into an iris cube
    x = iris.load_cube(fname)
    
    # Extract data values
    data = x.data

    # Determine lengths of data dimensions
    nt = int(len(data[:,0,0]))
    ny = int(len(data[0,:,0]))
    nx = int(len(data[0,0,:]))
    
    months = nt
    
    # On first loop through create a new empty cube with original coordinates
    if count == 0:
    
        new_coord = iris.coords.DimCoord(range(total_years*freq), long_name='time', units=1)
        coord1 = x.coord('latitude')
        coord2 = x.coord('longitude')
        
        cube = Cube(ma.zeros((total_years*freq,ny,nx),np.float32),dim_coords_and_dims=[(new_coord,0),(coord1,1),(coord2,2)])
    
    count2 = 0
    
    # Stack all data into 1 cube 
    for j in range(sub_total_months, sub_total_months+months):

        cube.data[j,:,:] = data[count2,:,:]
        
        count2 = count2 + 1
  
    sub_total_months = sub_total_months + months
    count = count+1

# Centre coordinates about longitude 0
cube.coord('longitude').points, rollindex = shiftlon(cube.coord('longitude').points, 0)

# Roll data to be consistent with longitude 0
cube.data = np.roll(cube.data, rollindex, axis=2)

# Interpolate data onto new coordinate system
region_cube = cube.interpolate([my_lats, my_lons],iris.analysis.Linear(extrapolation_mode='nan'))

# chunk_months = 1200

# for i in range(0, x.shape[0], chunk_months):
#     source_chunk = x[i:i + chunk_months]
#     region_chunk = source_chunk.interpolate(
#         [my_lats, my_lons],
#         iris.analysis.Linear(extrapolation_mode="nan"),
#     )
#     region_chunk.rename(var)

#     # New file name for data
#     outname = path+processed_data+region+'/'+var+'_'+model+'_'+experiment+'_'+variant_id+'_'+date_range2+'_mon_'+region+'_'+str(i)+'.nc'

#     iris.save(region_chunk, outname, unlimited_dimensions=["time"])

# Ensure new cube has correct name
region_cube.rename(var)

# New file name for data
outname = path+processed_data+region+'/'+var+'_'+model+'_'+experiment+'_'+variant_id+'_'+date_range2+'_mon_'+region+'.nc'

# Save data to file name
iris.save(region_cube, outname, unlimited_dimensions=[])
