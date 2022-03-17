import numpy as np
import matplotlib.pyplot as plt
import csv

def get_pos_arrays(atoms, filename):
  atom_positions = [[] for i in range(len(atoms))]
  atoms.sort()

  with open(filename, 'r') as f:
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

# atoms = np.arange(0, 30, 1)
atoms = [8,9,10,11,12,13,14]
pos_arrays = get_pos_arrays(atoms, "cell_mot_output/pos.txt")

x_cutoff = 0.03
z_cutoff = 0.0032
for i, atom in enumerate(atoms):
  x_arr = []
  z_arr = []
  for pos in pos_arrays[i]:
    if abs(pos[0]) < x_cutoff and abs(pos[2]) < z_cutoff:
      x_arr.append(pos[0])
      z_arr.append(pos[2])

  if i==0:
    plt.plot(x_arr, z_arr, 'b-', label='atom trajectories')
  else:
    plt.plot(x_arr, z_arr, 'b-')

  plt.xlabel('x (m)')
  plt.ylabel('z (m)')
  plt.grid(which='major', linestyle='-')

# Draw laser boundaries onto the plot for easier visualisation
# plt.axhline(y=5e-3, color='red', linestyle='--')
# plt.axhline(y=-5e-3, color='red', linestyle='--')
plt.axvline(x=5e-3, color='red', linestyle='--', label='laser beam path')
plt.axvline(x=-5e-3, color='red', linestyle='--')

plt.legend()
plt.title('Trajectories for atoms entering the cell MOT')
plt.show()