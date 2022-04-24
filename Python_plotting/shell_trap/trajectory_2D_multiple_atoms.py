import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import csv
from tqdm import tqdm

# Function to get all position arrays of atoms from the output from AtomECS
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
fig, ax = plt.subplots(figsize=(11,7))

atoms = np.arange(0, 100, 1)
pos_arrays = get_pos_arrays(atoms, "shell_trap_output/pos.txt")

for i, atom in enumerate(atoms):
  x_arr = [pos[0] * 1e3 for pos in pos_arrays[i]]
  z_arr = [pos[2] * 1e3 for pos in pos_arrays[i]]

  if i == 0:
    ax.plot(x_arr, z_arr, color=(1.0, 0.0, 0.0, 0.05), label='atom trajectory')
  else:
    ax.plot(x_arr, z_arr, color=(1.0, 0.0, 0.0, 0.05))

# Draw resonant spheroid ellipse
z0 = 0.00042 * 1e3
ellipse = Ellipse(
  (0,0),
  width=4*z0,
  height=2*z0,
  facecolor='none',
  edgecolor='red',
  linestyle='--',
  label='resonant spheroid outline')

ax.add_artist(ellipse)
ax.set_xticks(np.arange(-1.5, 1.6, 0.25))
ax.set_xlabel('x (mm)')
ax.set_ylabel('z (mm)')
ax.grid(which='major', linestyle='-')
ax.legend(loc='upper right')



plt.show()