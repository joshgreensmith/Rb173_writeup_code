import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kde
from matplotlib.patches import Ellipse
import csv
from tqdm import tqdm

plt.rcParams.update({'font.size': 13})

# Function to return an array of arrays of positions of each atom at each timestep
def get_pos_arrays(atoms, filename):
  atom_positions = [[] for i in range(len(atoms))]
  atoms.sort()

  num_lines = sum(1 for line in open(filename,'r'))
  with open(filename, 'r') as f:
    # reader = csv.Reader(f)

    atom = 0
    step = 0
    for line in tqdm(f, total=num_lines):
      if line.startswith('step'):
        step += 1
        atom = 0
      else:
        if int(line.split(',')[1].split(':')[0]) in atoms:
          x = float(line.split('(')[1].split(',')[0])
          y = float(line.split('(')[1].split(',')[1])
          z = float(line.split('(')[1].split(',')[2].split(')')[0])

          atom_positions[atom].append((x, y, z))
          atom += 1

  return atom_positions

# Atoms has to be of length 1 in this case
z0 = 0.003478980147917478 * 1e3
x_min = -z0 * 0.8
x_max = z0 * 0.8
z_min = -z0 * 1.3
z_max = -z0 * 0.7

fig, ax = plt.subplots(figsize=(8, 6.4))

# Get atom positions
atoms = np.arange(0, 100, 1)
pos_arrays = get_pos_arrays(atoms, "shell_trap_output/pos.txt")

x_final_arr = []
z_final_arr = []
for i, atom in enumerate(atoms):
  x_final_pos = [pos[0] * 1e3 for pos in pos_arrays[i]][-1]
  z_final_pos = [pos[2] * 1e3 for pos in pos_arrays[i]][-1]

  x_final_arr.append(x_final_pos)
  z_final_arr.append(z_final_pos)

# Calculate and draw density of atoms
# https://python-graph-gallery.com/85-density-plot-with-matplotlib
nbins = 300
x_final_arr = np.asarray(x_final_arr)
z_final_arr = np.asarray(z_final_arr)
k = kde.gaussian_kde([x_final_arr, z_final_arr])
xi, zi = np.mgrid[x_min:x_max:nbins*1j, z_min:z_max:nbins*1j]
hi = k(np.vstack([xi.flatten(), zi.flatten()]))

ax.pcolormesh(xi, zi, hi.reshape(xi.shape), shading='auto', cmap='plasma', label='atom density')

# Draw resonant spheroid ellipse
ellipse = Ellipse(
  (0,0),
  width=4*z0,
  height=2*z0,
  facecolor='none',
  edgecolor='black',
  linestyle='--',
  label='resonant spheroid outline')

ax.add_artist(ellipse)
ax.set_xlim([x_min, x_max])
ax.set_ylim([z_min, z_max])
ax.set_xlabel('x (mm)')
ax.set_ylabel('z (mm)')
ax.legend()

plt.show()