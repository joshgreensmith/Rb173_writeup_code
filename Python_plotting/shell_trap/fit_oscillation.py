import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy import optimize

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

def oscillator(x, a, b, c):
  return a + b * np.cos(c * x)

atoms = [1, 2, 3]
pos_arrays = get_pos_arrays([1, 2, 3], "shell_trap_output/pos.txt")

time_steps = np.arange(1, 501, 1)
z_pos_0 = [pos[2] for pos in pos_arrays[0]]
print(len(z_pos_0))

guess = [-0.0011, 0.0002, 0.16]
params, params_covariance = optimize.curve_fit(
  oscillator, 
  time_steps, 
  z_pos_0, 
  p0=guess, 
  # bounds=(-1.0e-9, 1.0e9)
)

print(params)
print(params_covariance)
plt.plot(time_steps, z_pos_0, label='actual z data')
plt.plot(time_steps, oscillator(time_steps, params[0], params[1], params[2]), label='fitted z data')
plt.plot(time_steps, oscillator(time_steps, guess[0], guess[1], guess[2]), label='guess')
plt.xlabel('time step')
plt.ylabel('z position')
plt.legend()
plt.grid(which='major', linestyle='-')
plt.show()