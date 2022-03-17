import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import csv
from scipy.fftpack import fft

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

# atoms = [1, 43, 72, 115, 304]
atoms = [0]
pos_arrays = get_pos_arrays(atoms, "shell_trap_output/pos.txt")

# Fourier transform

# Number of sample points
N = 1000
# Sample spacing
T = 4.0e-4
# FFT cutoff
lower_cutoff = 3
upper_cutoff = 150

xf = np.linspace(0.0, 1.0/T, N//2)

plot_all_atoms = False
if plot_all_atoms:
  fig, ax = plt.subplots(nrows=1, ncols=3)
  for j in range(0, 3):
    for i, atom in enumerate(atoms):
      pos_array = [pos[j] for pos in pos_arrays[i]]
      yf = fft(pos_array)

      atom_label = 'atom ' + str(atom)
      ax[j].plot(xf[:cutoff], np.abs(yf[:cutoff]), label=atom_label)

  ax[0].set_ylabel('fft amplitude')
  ax[0].set_xlabel('x frequency (Hz)')
  ax[1].set_xlabel('y frequency (Hz)')
  ax[2].set_xlabel('z frequency (Hz)')

  ax[0].grid(which='major', linestyle='-')
  ax[0].minorticks_on()
  ax[0].grid(which='minor', linestyle='-', color='lightgrey')
  ax[0].legend()

  ax[1].grid(which='major', linestyle='-')
  ax[1].minorticks_on()
  ax[1].grid(which='minor', linestyle='-', color='lightgrey')
  ax[1].legend()

  ax[2].grid(which='major', linestyle='-')
  ax[2].minorticks_on()
  ax[2].grid(which='minor', linestyle='-', color='lightgrey')
  ax[2].legend()

  fig.suptitle('Positions fourier transform')
  plt.show()

else:
  z_pos_array = [pos[2] for pos in pos_arrays[0]]
  yf = fft(z_pos_array)
  plt.plot(xf[lower_cutoff:upper_cutoff], np.abs(yf[lower_cutoff:upper_cutoff]), label='fourier transform of the z position')
  plt.xlabel('frequency (Hz)')
  plt.ylabel('FFT amplitude')

  plt.grid(which='major', linestyle='-')
  plt.minorticks_on()
  plt.grid(which='minor', linestyle='-', color='lightgrey')
  plt.vlines(132, 0, max([np.abs(x) for x in yf[lower_cutoff:upper_cutoff]]), color='red', label='resonant frequency from theory')
  plt.ylim(ymin=0)
  plt.xlim(xmin=0)
  plt.legend(loc='upper right')

  plt.show()

