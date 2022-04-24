import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import csv

# Function to return an array of arrays of positions of each atom at each timestep
def get_pos_arrays(atoms, filename):
  atom_positions = [[] for i in range(len(atoms))]
  atoms.sort()

  with open(filename, 'r') as f:
    # reader = csv.Reader(f)

    atom = 0
    step = 0
    for line in f:
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
fig, ax = plt.subplots(figsize=(11,7))

atoms = [15]
pos_arrays = get_pos_arrays(atoms, "shell_trap_output/pos.txt")

x_arr = [pos[0] for pos in pos_arrays[0]]
z_arr = [pos[2] for pos in pos_arrays[0]]

ax.plot(x_arr, z_arr, label='atom trajectory')
ax.plot(x_arr[0], z_arr[0], 'ro', label='starting position')

# Draw resonant spheroid ellipse
z0 = 0.00042
ellipse = Ellipse(
  (0,0),
  width=4*z0,
  height=2*z0,
  facecolor='none',
  edgecolor='red',
  linestyle='--',
  label='resonant spheroid outline')
ax.add_artist(ellipse)

ax.set_xlabel('x (m)')
ax.set_ylabel('z (m)')
ax.grid(which='major', linestyle='-')
ax.legend(loc='upper right')

plt.show()