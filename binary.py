from spacepy.pybats import gitm
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from PIL import Image
from glob import glob
import subprocess, sys
import os

# Keys in the list are not graphable (Or wouldn't need to be graphed ex. time, lat, lon)
plot_blacklist = ['time', 'Longitude', 'Latitude', 'Magnetic latitude', 'Magnetic Longitude', 'Local Time']

gitm = gitm.GitmBin('./3DALL_t970223_000000.bin')
plt.style.use('seaborn-white')

cmap = 'Spectral_r'

while True:
	print('=================================')
	print('Welcome to GITM Binary plotter...')
	print('=================================')
	print('Select a key to plot on Z-Index:')

	for key in gitm.keys():
		index = list(gitm.keys()).index(key)
		print('%s: %s' % (index, key))

	print('[ Type \'exit\' to close program. ]')
	val = input("Please input key (0 - %s): " % (len(gitm.keys())))
	if val == 'exit':
		print('Goodbye.')
		break
	int_val = int(val)
	key = list(gitm.keys())[int_val]

	print('=================================')
	print('Selected Key: %s' % (key))

	def flatten3D(data, alt):
			Z = []
			for a1 in data:
				n = []
				for a2 in a1:
					n.append(a2[alt])
				Z.append(n)
			return Z

	def contourVideo(flat, data):
		folder = 'plot_video'
		MAX_ALT = len(data[0][0])
		images = []

		fvmax = 0
		for i in range(MAX_ALT):
			newtemps = []
			for a1 in data:
				n = []
				for a2 in a1:
					n.append(a2[i])
				newtemps.append(n)
			if np.max(newtemps) > fvmax:
				fvmax = np.max(newtemps)

		fvmin = 0
		for i in range(MAX_ALT):
			newtemps = []
			for a1 in data:
				n = []
				for a2 in a1:
					n.append(a2[i])
				newtemps.append(n)
			if np.min(newtemps) < fvmin:
				fvmin = np.min(newtemps)

		for i in range(MAX_ALT):
			newtemps = []
			for a1 in data:
				n = []
				for a2 in a1:
					n.append(a2[i])
				newtemps.append(n)

			y = np.linspace(0, len(data), len(data))
			x = np.linspace(0, len(data[0]), len(data[0]))
			X, Y = np.meshgrid(x, y)
			plt.clf()
			plt.title('Plot %s (Z= %s)' % (key, i))
			plt.xlabel("Longitude")
			plt.ylabel("Latitude")


			
			if flat:
				contour = plt.contourf(flatten3D(gitm['Longitude'], i), flatten3D(gitm['Latitude'], i), newtemps, 20, cmap=cmap, vmin=fvmin, vmax=fvmax);
				plt.clim(fvmin, fvmax)
				cbar = plt.colorbar(contour)
				cbar.ax.set_ylabel(key)
				plt.savefig(folder + "/file%02d.png" % i)
			else:
				ax = plt.axes(projection='3d')
				contour = ax.contourf(flatten3D(gitm['Longitude'], i), flatten3D(gitm['Latitude'], i), newtemps, 20, cmap=cmap, vmin=fvmin, vmax=fvmax, rstride=1, cstride=1, edgecolor='none', extend3d=True);
				plt.savefig(folder + "/file%02d.png" % i)

		os.chdir(folder)
		subprocess.call([
			'ffmpeg', '-framerate', '8', '-i', 'file%02d.png', '-r', '30', '-pix_fmt', 'yuv420p',
			'video_name.mp4'
		])
		for file_name in glob("*.png"):
			os.remove(file_name)

		opener = "open" if sys.platform == "darwin" else "xdg-open"
		subprocess.call([opener, './video_name.mp4'])
		os.chdir('../')

	temps = gitm[key]

	

	print('Available Colormaps:')
	for map in cm.__builtin_cmaps:
		index = cm.__builtin_cmaps.index(map)
		print('  %s: %s' % (index, map))
	cmap_index = input("Select colormap (Enter for default): ")
	if cmap_index != '':
		cmap = cm.__builtin_cmaps[int(cmap_index)]
	else:
		cmap = 'Spectral_r'
	print('Selected colormap: %s' % cmap)

	val = input("Type of plot:\n  1. Contour\n  2. Contour Video\n  3. 3D Contour Video\nSelect: ")
	if val == '2':
		print('Generating video...')
		contourVideo(True, temps)
	elif val == '3':
		print('Generating video...')
		contourVideo(False, temps)
	else:
		altset = 0
		MAX_ALT = len(temps[0][0])
		MIN_ALT = 0

		val = input("Altitude (Available 0-%s) [Plot multiple seperated by \',\']: " % (MAX_ALT))
		coms = val.split(',')
		alts = []
		for com in coms:
			alts.append(int(com))
		print(alts)
		
		def plotCoords(data, alt):
			Z = []
			for a1 in data:
				n = []
				for a2 in a1:
					n.append(a2[alt])
				Z.append(n)

			y = np.linspace(0, len(data), len(data))
			x = np.linspace(0, len(data[0]), len(data[0]))

			'''
			for i in y:
				index = y.index(i)
				for l in i:
					index2 = i.index(l)
					y[index][index2] = gitm['Longitude'][index][index2]
			'''

			X, Y = np.meshgrid(x, y)
			return X, Y, Z

		plt.clf()
		fig, axs = plt.subplots(len(alts), figsize=(5,3 * len(alts)))
		fig.suptitle('Plot %s' % (key))
		
		for i in range(len(alts)):

			X, Y, Z = plotCoords(temps, alts[i])
			
			axs[i].set_title('Z= %s' % (alts[i]))
			axs[i].set(xlabel='Longitude', ylabel='Latitude')

			contour = axs[i].contourf(flatten3D(gitm['Longitude'], alts[i]), flatten3D(gitm['Latitude'], alts[i]), Z, 20, cmap=cmap);
			cbar = fig.colorbar(contour, ax=axs[i])
			cbar.ax.set_ylabel(key)
		
		fig.tight_layout()
		
		
		fig.savefig('demo.png',dpi=300)

		image = Image.open('demo.png')
		image.show()

		plt.cla()

	print('=================================')
	inp = input("Plot again? (y/n): ")
	if inp == 'n':
		print('Goodbye.')
		break
