import json
import os
import numpy as np
import matplotlib.pyplot as plt
import csv
from ast import literal_eval

with open('cell_mot_output/offsets_run_3.csv', 'r') as f:
  reader = csv.DictReader(f)
  
  offset_deltas = []
  capture_fractions = []

  for line in reader:
    offset_deltas.append(float(line['offset delta']))
    capture_fractions.append(np.mean(literal_eval(line['capture fraction array'])))

plt.plot(offset_deltas, capture_fractions)

plt.xlabel('offset deltas (m)')
plt.ylabel('capture fraction')

plt.title('Capture fraction against offset delta for detuning -12MHz')

# plt.legend()
# plt.minorticks_on()
plt.grid(which='major', linestyle='-')
# plt.grid(which='minor', linestyle='-', color='lightgrey')

plt.show()
