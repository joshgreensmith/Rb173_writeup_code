import numpy as np
import matplotlib.pyplot as plt
import csv

filename = 'shell_trap_output/optimize_params_differential_out_9.csv'

# Get param evolution arrays from filename
def get_param_evolution_arrays(filename):
  param_evolution_array = [[], [], [], []]
  with open(filename, 'r') as f:
    reader = csv.DictReader(f)
    for line in reader:
      param_evolution_array[0].append(float(line['quad gradient']))
      param_evolution_array[1].append(float(line['rf frequency']))
      param_evolution_array[2].append(float(line['rf amplitude']))
      param_evolution_array[3].append(float(line['Phase space density']))

  return param_evolution_array

param_arrays = get_param_evolution_arrays(filename)

# Fit a polynomial to the evolution of the PSD
x = np.arange(0, len(param_arrays[3]), 1)
z = np.polyfit(x, param_arrays[3], 7)
p = np.poly1d(z)

# Plot param evolution and cost function evolution for the PSD case
fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(10,7.5))

ax[0][0].plot(param_arrays[0])
ax[0][0].set_title('Quad gradient evolution')
ax[0][0].set_xlabel('Iteration number')
ax[0][0].set_ylabel('Quad gradient (Gs/cm)')
ax[0][0].grid(which='major', linestyle='-')

ax[0][1].plot(param_arrays[1])
ax[0][1].set_title('RF frequency evolution')
ax[0][1].set_xlabel('Iteration number')
ax[0][1].set_ylabel('RF frequency (MHz)')
ax[0][1].grid(which='major', linestyle='-')

ax[1][0].plot(param_arrays[2])
ax[1][0].set_title('RF amplitude evolution')
ax[1][0].set_xlabel('Iteration number')
ax[1][0].set_ylabel('RF amplitude (Gs)')
ax[1][0].grid(which='major', linestyle='-')

ax[1][1].plot([-x for x in param_arrays[3]], label='PSD evolution')
ax[1][1].plot(x, -p(x), 'm-', label='PSD trendline')
ax[1][1].set_title('Cost function evolution')
ax[1][1].set_xlabel('Iteration number')
ax[1][1].set_ylabel('Phase space density')
ax[1][1].legend(loc='lower right', prop={'size': 8})
ax[1][1].grid(which='major', linestyle='-')

plt.subplots_adjust(wspace=0.3, hspace=0.4)

plt.show()
