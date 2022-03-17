import json
import os
import numpy as np
import matplotlib.pyplot as plt
import csv
from ast import literal_eval

with open('cell_mot_output/run_3.csv', 'r') as f:
  reader = csv.DictReader(f)
  
  detunings = []
  capture_fractions_stdevs = []

  for line in reader:
    detunings.append(-float(line['detuning']))
    cf_arr = literal_eval(line['capture fraction array'])
    percent_std = (np.std(cf_arr) / np.mean(cf_arr)) * 100
    capture_fractions_stdevs.append(percent_std)


f = plt.figure(figsize=(8.8, 6.4))
plt.plot(detunings, capture_fractions_stdevs)

plt.xlabel('detuning (MHz)')
plt.ylabel('capture fraction percent stdev')

# plt.title('Capture fraction stdev against detuning for offset delta 0.0')

plt.legend()
# plt.minorticks_on()
plt.grid(which='major', linestyle='-')
# plt.grid(which='minor', linestyle='-', color='lightgrey')

ax = plt.gca()
ax.set_xticks(np.arange(-10.0, -80.1, -5.0))
# ax.set_yticks(np.arange(0, 0.021, 0.0025))
ax.invert_xaxis()

plt.show()
