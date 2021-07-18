#!/usr/bin/env python3

import numpy as np
import datetime as dt
import idlsave 
import matplotlib.cm as cm
import matplotlib.colors as mplc
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import lines

# Constants
SMC_FILE = 'gitm_baselinecube_newion_smc.save'
OUTPUT_FILE = 'GITM_ALT_KEO.jpg'
SHOULD_OPEN_FILE = False

def plot(gitm, althigh, altlow, latslow, latshigh, lonlow, lonhigh, gtimelow, gtimeshigh, mltplot):
    # MARK: Setup
    lines.lineStyles.keys()
    glats = gitm.gitmdatacubelats
    glons = gitm.gitmdatacubelons
    galts = gitm.gitmdatacubealts
    gdatatimes = gitm.gitmdatacubeUT
    gjuldate = gitm.gitmdatacubejulian2000

    # Transpose to get in terms of times,lons,lats,alts
    gtemp = np.transpose(gitm.gitmdatacubetemp)
    gmlt = np.transpose(gitm.gitmdatacubemlt)
    gmaglats = np.transpose(gitm.gitmdatacubemaglats)

    # Filter data to bounds
    new_times = gjuldate[(gjuldate >= gtimelow ) & (gjuldate <= gtimeshigh)]
    new_lats = glats[(glats > latslow) & (glats < latshigh)]
    new_lons = glons[(glons > lonlow) & (glons < lonhigh)]
    new_alts= galts[(galts > altlow) & (galts < althigh)]

    nlats = len(new_lats)
    nlons = len(new_lons)
    nalts = len(new_alts)  #should be for this plotting 
    ntimes = len(new_times)

    # Subset of Altitudes
    new_mlts = gmlt[ :,:,:,0] # same for all Alt
    new_maglats = gmaglats[ :,:,:,0]  #same for all alt
    new_temp = gtemp[ :,:,:,(galts > altlow) & (galts < althigh)]

    # Subset of Latitudes
    new_mlts = new_mlts[:,:,(glats > latslow) & (glats < latshigh)]
    new_maglats = new_maglats[:,:,(glats > latslow) & (glats < latshigh)]
    new_temp = new_temp[:,:,(glats > latslow) & (glats < latshigh),:]

    # Subset of Longitudes
    new_mlts=new_mlts[:,(glons > lonlow) & (glons < lonhigh)]
    new_maglats=new_maglats[:,(glons > lonlow) & (glons < lonhigh),:]
    new_temp=new_temp[:,(glons > lonlow) & (glons < lonhigh),:,:]


    # Reset the data into MLT and Maglat coordinates
    nlatlon = nlats * nlons

    plot_maglats = np.reshape(new_maglats,(ntimes,nlatlon))
    plot_mlts = np.reshape(new_mlts, (ntimes,nlatlon))
    plot_temp = np.reshape(new_temp, (ntimes,nlatlon,nalts))

    #mlts out of GITM -12 to 12 change to 0 to 24
    plot_mlts[plot_mlts < 0] = plot_mlts[plot_mlts <0] + 24.

    #maglats 90-50 steps of 0.5 then 80.
    lat_plot = [80, 75, 70, 65, 60, 55]

    fig, ax = plt.subplots(len(lat_plot), 1, figsize=(7, 9))

    for lat in lat_plot:
        
        plotdata1 = np.ndarray(shape=(ntimes,nalts), dtype=float)
        pmaglats = np.ndarray(shape=(ntimes), dtype=float)
        pmlts = np.ndarray(shape=(ntimes), dtype=float)
       
        for x in range(ntimes):
          
            xmlt=plot_mlts[x,:]
            xmaglat=plot_maglats[x,:]
            xdata=plot_temp[x,:,:]
        
            pmaglats[x] = np.mean(xmaglat[(xmaglat >= lat - .64) & (xmaglat < lat + .44) & (xmlt <= mltplot + .23) & (xmlt > mltplot - .23)])
        
            x_pos =  (xmaglat >= lat - .63) & (xmaglat < lat + .43) & (xmlt <= mltplot+.23) & (xmlt > mltplot-.23)
            pmlts[x] = np.mean(xmlt[x_pos])

            
            for y in range(nalts):
                plotdata1[x,y] = np.mean(xdata[x_pos, y])
           
        index = lat_plot.index(lat)
        ax[index].set_yticks([ 250, 300, 350, 400, 450, 500])
        ax[index].set_ylabel('Altitude (km)')

        ax[index].xaxis.set_major_locator(plt.MaxNLocator(6))

        if index < 5:
           ax[index].set_xticks([])
        else:
           ax[index].set_xlabel('UT Time')
        
        
        zz = np.array(range(72))
        plotdata = np.transpose(plotdata1)
        cs = ax[index].contourf(zz, new_alts, plotdata, 200, cmap=cm.rainbow, vmin=500, vmax=2000)
        
       
        ax[index].text(30, 505, 'Mag Latitude: %s ' % lat, fontsize=10)
      
    # MARK: Plot and save
       
    m = plt.cm.ScalarMappable(cmap=cm.rainbow)
    m.set_clim(vmin=500, vmax=2000)

    cbar_ax = fig.add_axes([0.85, 0.35, 0.02, 0.3])
    cbar = fig.colorbar(m,cax=cbar_ax)
    cbar.set_label('Kelvin')

    fig.subplots_adjust(right=0.80)
    fig.text(.35,.94,'1997 02 23 (SMC)',fontsize=17)
    fig.text(.25,.90,'Temperature',fontsize =12)
    fig.text(.70,.90,'MLT: %s' % int(mltplot),fontsize=12)

    fig.savefig(OUTPUT_FILE, dpi=300)

    return OUTPUT_FILE
