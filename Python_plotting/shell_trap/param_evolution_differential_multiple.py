import numpy as np
import matplotlib.pyplot as plt
import csv

plt.rcParams.update({'font.size': 12})

filenames = [
  'shell_trap_output/optimize_params_differential_out_11.csv',
  'shell_trap_output/optimize_params_differential_out_12.csv',
  'shell_trap_output/optimize_params_differential_out_13.csv',
]

# Get param evolution arrays from filename
def get_param_evolution_arrays(filename):
  param_evolution_array = [[], [], [], []]
  with open(filename, 'r') as f:
    reader = csv.DictReader(f)
    for line in reader:
      param_evolution_array[0].append(float(line['quad gradient']))
      param_evolution_array[1].append(float(line['rf frequency']))
      param_evolution_array[2].append(float(line['rf amplitude']))
      param_evolution_array[3].append(float(line['current temperature']))

  return param_evolution_array

# Plot the param and cost function evolution in different subplots for each run
fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(10,7.5))

cutoff_iteration = 60
for i, filename in enumerate(filenames):
  param_arrays = get_param_evolution_arrays(filename)
  label = 'Run ' + str(i+1)
  ax[0][0].plot(param_arrays[0][:cutoff_iteration], label=label)
  ax[0][0].legend()
  ax[0][1].plot(param_arrays[1][:cutoff_iteration])
  ax[1][0].plot(param_arrays[2][:cutoff_iteration])
  ax[1][1].plot(param_arrays[3][:cutoff_iteration])


ax[0][0].set_title('Quadrupole gradient')
ax[0][0].set_xlabel('Iteration number')
ax[0][0].set_ylabel('Quad. gradient (Gs/cm)')
ax[0][0].set_xticks([0, 10, 20, 30, 40, 50, 60])
ax[0][0].grid(which='major', linestyle='-')

ax[0][1].set_title('RF frequency')
ax[0][1].set_xlabel('Iteration number')
ax[0][1].set_ylabel('RF frequency (MHz)')
ax[0][1].set_xticks([0, 10, 20, 30, 40, 50, 60])
ax[0][1].grid(which='major', linestyle='-')

ax[1][0].set_title('RF amplitude')
ax[1][0].set_xlabel('Iteration number')
ax[1][0].set_ylabel('RF amplitude (Gs)')
ax[1][0].set_xticks([0, 10, 20, 30, 40, 50, 60])
ax[1][0].grid(which='major', linestyle='-')

ax[1][1].set_title('Thermalisation temp.')
ax[1][1].set_xlabel('Iteration number')
ax[1][1].set_ylabel('Thermalisation temp. (K)')
ax[1][1].set_xticks([0, 10, 20, 30, 40, 50, 60])
ax[1][1].legend(loc='upper right', prop={'size': 8})
ax[1][1].grid(which='major', linestyle='-')

plt.subplots_adjust(wspace=0.3, hspace=0.5)

plt.show()
