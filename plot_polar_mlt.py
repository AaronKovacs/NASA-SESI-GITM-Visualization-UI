import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import idlsave 
from matplotlib import lines
lines.lineStyles.keys()
import matplotlib.cm as cm

def plot_polar_mlt(gitm, altset, latslow, latshigh, lonlow, lonhigh, gtimelow, gtimeshigh, nmlt, nlat):
    glats=gitm.gitmdatacubelats
    glons=gitm.gitmdatacubelons
    galts=gitm.gitmdatacubealts
    gdatatimes=gitm.gitmdatacubeUT
    gjuldate=gitm.gitmdatacubejulian2000

    #transpose to get in terms of times,lons,lats,alts
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

    #reset the data into MLT and Maglat coordinates
    plot_maglats=np.reshape(new_maglats,(72, nlons*nlats))
    plot_mlts=np.reshape(new_mlts, (72,nlons*nlats))
    plot_temp=np.reshape(new_temp, (72,nlons*nlats))

    #mlts out of GITM -12 to 12 change to 0 to 24
    plot_mlts[plot_mlts < 0]=plot_mlts[plot_mlts <0]+24.

    #to plot in polar make an array of the data in MLT by Mag Lat 
    mlts=np.array(range(nmlt))

    #creates lats from 90 to 44 by 2s
    lats=np.flip(np.array(range(50,92,2)))
    lat2d=np.ndarray(shape=(nmlt,nlat),dtype=float)
    lon2d=np.ndarray(shape=(nmlt,nlat),dtype=float)

    for i in range(nmlt):
        lat2d[i,:]=lats
        
    for i in range(nlat):
        lon2d[:,i]=np.deg2rad(mlts*15.)-np.pi/2.
        
    x = (90.-lat2d)*np.cos(lon2d)
    y = (90.-lat2d)*np.sin(lon2d)

    #creat cirlces to plot over potentials
    circlex=np.ndarray(shape=(6,361),dtype=float)
    circley=np.ndarray(shape=(6,361),dtype=float)

    zz=np.deg2rad(np.array(range(361)))

    for p in range(5):
      circlex[p,:]=np.transpose(p*10.*np.cos(zz)) 
      circley[p,:]=np.transpose(p*10.*np.sin(zz))

    nn=6
    mm=4

    fig,ax=plt.subplots(nn,mm,figsize=(7,9))

    k=20

    for n in range(nn):
       for m in range(mm):   
        
         plotdata=np.ndarray(shape=(nmlt,nlat),dtype=float)
         datamlts=np.ndarray(shape=(nmlt),dtype=float)
         datalats=np.ndarray(shape=(nlat),dtype=float)
         plotdata1=plot_temp[k,:]
         dmlts=plot_mlts[k,:]
         dlats=plot_maglats[k,:]

        #pull out MLTs
         for i in range(nmlt):
             
            if i == 24 or i ==0:
                datamlts[i]=np.mean(dmlts[(dmlts >= 23.5) ^ (dmlts < .5)])
                dlatsnew=dlats[(dmlts >= 23.5) ^ (dmlts < .5)]
                plotdatanew=plotdata1[(dmlts >= 23.5) ^ (dmlts < .5)]
            
            else:
                datamlts[i]=np.mean(dmlts[(dmlts >= i-.5) & (dmlts < i+.5)])
                dlatsnew=dlats[(dmlts >= i-.5) & (dmlts < i+.5)]
                plotdatanew=plotdata1[(dmlts >= i-.5) & (dmlts < i+.5)]
            
            
            #pull out maglats (90 - 50 by 2)
            
            for j in range(nlat):
                if lats[j] > 86:
                    datalats[j]=lats[j]
                    plotdata[i,j]=0.
                else:

                    datalats[j]=np.mean(dlatsnew[(dlatsnew >= lats[j]-1.) & (dlatsnew < lats[j]+1.)])
                    plotdata[i,j]=max(plotdatanew[(dlatsnew >= lats[j]-1.) & (dlatsnew < lats[j]+1.)])
                
                
         ax[n,m].set_axis_off()
                
                
         cs = ax[n,m].contourf(x,y,plotdata,200,cmap=cm.rainbow,vmin=0,vmax=50)

         for z in range(5):
            ax[n,m].plot(circlex[z,:],circley[z,:],'k--',linewidth=0.5)
        
         ax[n,m].plot((-40,40),(0,0),'k--',linewidth=0.5)
         ax[n,m].plot((0,0),(-40,40),'k--',linewidth=0.5)

         q=40*np.cos(np.deg2rad(45))

         ax[n,m].plot((q,-q),(q,-q),'k--',linewidth=0.5)
         ax[n,m].plot((q,-q),(-q,q),'k--', linewidth=0.5)      
         
         plotmax=str(int(np.max(plotdata)))
         plotmin=str(int(np.min(plotdata)))        
         ax[n,m].text(-40,-40 ,plotmin,fontsize=8)    
         ax[n,m].text(q,-40 ,plotmax,fontsize=8)       
         
         k=k+1

    m=plt.cm.ScalarMappable(cmap=cm.rainbow)
    m.set_clim(vmin=0,vmax=50)
    fig.subplots_adjust(right=0.80)


    cbar_ax=fig.add_axes([0.85,0.35,0.02,0.3])
    cbar=fig.colorbar(m,cax=cbar_ax)
    cbar.set_label('kV')


    fig.savefig('smc_polar_mlt.jpg',dpi=300)
    return 'smc_polar_mlt.jpg'
