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

	def contourVideo(data):
		folder = 'plot_video'
		MAX_ALT = len(data[0][0])
		images = []
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
			plt.xlabel("Latitude")
			plt.ylabel("Longitude")
			contour = plt.contourf(X, Y, newtemps, 20, cmap=cmap);
			cbar = plt.colorbar(contour)
			cbar.ax.set_ylabel(key)
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

	val = input("Type of plot:\n  1. Contour\n  2. Contour Video\nSelect: ")
	if val == '2':
		print('Generating video...')
		contourVideo(temps)
	else:
		altset = 0
		MAX_ALT = len(temps[0][0])
		MIN_ALT = 0

		val = input("Altitude (Available 0-%s): " % (MAX_ALT))
		altset = int(val)

		if altset > MAX_ALT:
			altset = MAX_ALT
		
		newtemps = []
		for a1 in temps:
			n = []
			for a2 in a1:
				n.append(a2[altset])
			newtemps.append(n)

		y = np.linspace(0, len(temps), len(temps))
		x = np.linspace(0, len(temps[0]), len(temps[0]))

		X, Y = np.meshgrid(x, y)

		# Clear plot
		plt.clf()
		plt.title('Plot %s (Z= %s)' % (key, altset))
		plt.xlabel("Latitude")
		plt.ylabel("Longitude")
		contour = plt.contourf(X, Y, newtemps, 20, cmap=cmap);
		cbar = plt.colorbar(contour)
		cbar.ax.set_ylabel(key)

		plt.savefig('demo.png',dpi=300)

		image = Image.open('demo.png')
		image.show()

	print('=================================')
	inp = input("Plot again? (y/n): ")
	if inp == 'n':
		print('Goodbye.')
		break
