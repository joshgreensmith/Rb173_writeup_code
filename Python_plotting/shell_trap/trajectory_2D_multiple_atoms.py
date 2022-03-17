import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import csv
from math import floor
from tqdm import tqdm

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
fig, axs = plt.subplots(3, 3, figsize=(11,7), sharex=True, sharey=True)

atoms = np.arange(10, 19, 1)
pos_arrays = get_pos_arrays(atoms, "shell_trap_output/pos.txt")

for i, atom in enumerate(atoms):
  x_arr = [pos[0] for pos in pos_arrays[i]]
  z_arr = [pos[2] for pos in pos_arrays[i]]

  axs[floor(i/3)][i%3].plot(x_arr, z_arr, label='atom trajectory')
  axs[floor(i/3)][i%3].plot(x_arr[0], z_arr[0], 'ro', label='starting position')

  # Draw resonant spheroid ellipse
  z0 = 0.00042
  ellipse = Ellipse(
    (0,0),
    width=4*z0,
    height=2*z0,
    facecolor='none',
    edgecolor='red',
    linestyle='--')
  axs[floor(i/3)][i%3].add_artist(ellipse)
  axs[floor(i/3)][i%3].grid(which='major', linestyle='-')


custom_xlim = (-z0*2.5, z0*2.5)
custom_ylim = (-z0*2, z0*2)
plt.setp(axs, xlim=custom_xlim, ylim=custom_ylim)

plt.setp(axs[-1, :], xlabel='x (m)')
plt.setp(axs[:, 0], ylabel='z (m)')

plt.show()