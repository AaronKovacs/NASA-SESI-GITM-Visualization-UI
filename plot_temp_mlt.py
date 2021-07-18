import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import idlsave 
from matplotlib import lines
lines.lineStyles.keys()
import matplotlib.cm as cm

OUTPUT_FILE = 'plot_temp'

def plot_temp_mlt(gitm, altset, latslow, latshigh, lonlow, lonhigh, gtimelow, gtimeshigh, nmaglats):
    glats=gitm.gitmdatacubelats
    glons=gitm.gitmdatacubelons
    galts=gitm.gitmdatacubealts
    gdatatimes=gitm.gitmdatacubeUT
    gjuldate=gitm.gitmdatacubejulian2000

    gtemp=np.transpose(gitm.gitmdatacubeintegratedhall)
    gmlt=np.transpose(gitm.gitmdatacubemlt)
    gmaglats=np.transpose(gitm.gitmdatacubemaglats)

    #set up new terms with out extra "stuff"
    new_times=gjuldate[(gjuldate >= gtimelow ) & (gjuldate <= gtimeshigh)]
    new_lats=glats[(glats > latslow) & (glats < latshigh)]
    new_lons=glons[(glons > lonlow) & (glons < lonhigh)]
    new_alts=galts[(galts > altset-2.) & (galts < altset+2)]

    nlats=len(new_lats)
    nlons=len(new_lons)
    nalts=len(new_alts)  #should be for this plotting 
    ntimes=len(new_times)

    #subset of Altitudes
    new_mlts=gmlt[ :,:,:,(galts > altset-2.) & (galts < altset+2)]
    new_maglats=gmaglats[ :,:,:,(galts > altset-2.) & (galts < altset+2)]
    new_temp=gtemp[ :,:,:,(galts > altset-2.) & (galts < altset+2)]

    #subset of latitudes
    new_mlts=new_mlts[:,:,(glats > latslow) & (glats < latshigh)]
    new_maglats=new_maglats[:,:,(glats > latslow) & (glats < latshigh)]
    new_temp=new_temp[:,:,(glats > latslow) & (glats < latshigh)]


    #subset of longitudes
    new_mlts=new_mlts[:,(glons > lonlow) & (glons < lonhigh),:]
    new_maglats=new_maglats[:,(glons > lonlow) & (glons < lonhigh),:]
    new_temp=new_temp[:,(glons > lonlow) & (glons < lonhigh),:]

    #add subset of times if needed
    mltplot=[21,22,23,24,1,2,3]
    mltplot_print=['21','22','23','24','1','2','3']

    #reset the data into MLT and Maglat coordinates
    plot_maglats=np.reshape(new_maglats,(72, nlons*nlats))
    plot_mlts=np.reshape(new_mlts, (72,nlons*nlats))
    plot_temp=np.reshape(new_temp, (72,nlons*nlats))

    #mlts out of GITM -12 to 12 change to 0 to 24
    plot_mlts[plot_mlts < 0]=plot_mlts[plot_mlts <0]+24.

    fig,ax=plt.subplots(7,1,figsize=(7,9))

    j=0
    for i in mltplot:
        
        plotdata1=np.ndarray(shape=(ntimes,nmaglats),dtype=float)
        pmaglats=np.ndarray(shape=(nmaglats),dtype=float)

        #pull out the data for the correct MLT to plot
        for x in range(ntimes):
           if i != 24:
               mlts=plot_mlts[x,:]
               mlts2=mlts[(mlts < i+.6) & (mlts > i-.4)]
            
               maglats=plot_maglats[x,:]
               maglats=maglats[(mlts < i+.6) & (mlts > i-.4)]
               plot_data=plot_temp[x,:]
               plotdata=plot_data[(mlts < i+.6) & (mlts > i-.4)]
           else:
               mlts=plot_mlts[x,:]
               mlts2=mlts[(mlts < .6)^(mlts > 23.4)]
            
               maglats=plot_maglats[x,:]
               maglats=maglats[(mlts < .6)^(mlts > 23.4)]
               plot_data=plot_temp[x,:]
               plotdata=plot_data[(mlts < .6)^(mlts > 23.4)]
                      
           #put the data in order of maglatitude to plot
           z=90
           for y in range(80): 
               plotdata1[x,y]=np.mean(plotdata[(maglats <= z+.5) & (maglats > z-.5)])
               z=z-0.5
               pmaglats[y]=np.mean(maglats[(maglats <= z+.5) & (maglats > z-.5)])
              
                   
                  

        
        
        ax[j].xaxis.set_major_locator(plt.MaxNLocator(6))
        if j < 6:
           ax[j].set_xticks([])
        else:
           ax[j].set_xlabel('UT Time')
            
        t=np.array(range(72))
        zzy=np.array(range(100,180))/2.
        #ax[j].imshow(np.transpose(plotdata1))
            
            
        plotdata2=np.flipud(np.transpose(plotdata1))
        ax[j].contourf(t,zzy,plotdata2,200,cmap=cm.rainbow,vmin=0,vmax=50)
        
        ax[j].text(30,90.5,'MLT: '+mltplot_print[j],fontsize=10)
        
        ax[j].set_yticks([50,60,70,80,90])
        ax[j].set_ylabel('Mag. Lat.')

        j=j+1

    m=plt.cm.ScalarMappable(cmap=cm.rainbow)

    m.set_clim(vmin=0,vmax=50)

    fig.subplots_adjust(right=0.80)
    cbar_ax=fig.add_axes([0.85,0.35,0.02,0.3])
    cbar=fig.colorbar(m,cax=cbar_ax)
    cbar.set_label('mhos')


    fig.text(.35,.94,'1997 02 23 (SMC)',fontsize=17)
    fig.text(.25,.90,'Sigma Hall',fontsize =12)
    fig.text(.70,.90,'Altitude: %s km' % altset,fontsize=12)

    fig.savefig('%s%s.jpg' % (OUTPUT_FILE, altset), dpi=300)
    return '%s%s.jpg' % (OUTPUT_FILE, altset)
