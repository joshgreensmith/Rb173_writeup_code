import json
import os
import numpy as np
import matplotlib.pyplot as plt
import csv
from ast import literal_eval

color_gradient = [
  (33.0, 32.0, 109.0),
  (104.0, 20.0, 71.0),
  (159.0, 0.0, 38.0),
  (198.0, 0.0, 0.0),
  (217.0, 65.0, 0.0),
  (233.0, 112.0, 0.0)
]

color_grad_scaled = []
for color in color_gradient:
  color_grad_scaled.append((color[0]/255.0, color[1]/255.0, color[2]/255.0))

with open('cell_mot_output/detunings_offsets_run_4.csv', 'r') as f:
  reader = csv.DictReader(f)

  offset_capture_fractions = {}

  for line in reader:
    cf_arr = literal_eval(line['capture fraction array'])
    if np.mean(cf_arr) == 0:
      percent_std = 0
    else:
      percent_std = (np.std(cf_arr) / np.mean(cf_arr)) * 100
    if line['offset delta'] in offset_capture_fractions.keys():
      offset_capture_fractions[line['offset delta']].append(percent_std)
    else:
      offset_capture_fractions[line['offset delta']] = [percent_std]

f = plt.figure(figsize=(8.8, 6.4))
detunings = np.arange(-10.0, -81.0, -1.0)
detunings_to_plot = np.arange(-10.0, -56.0, -1.0)
offsets_to_plot = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
for offset in offset_capture_fractions.keys():
  offset_mm = round(literal_eval(offset)*1e3, 1)
  if offset_mm in offsets_to_plot:
    offset_label = str(offset_mm) + 'mm offset'
    # Fit trendline
    cf_stdev_fit = np.polyfit(detunings, offset_capture_fractions[offset], 11)
    p = np.poly1d(cf_stdev_fit)
    plt.plot(
      detunings_to_plot, 
      p(detunings_to_plot), 
      label=offset_label, 
      color=color_grad_scaled[offsets_to_plot.index(offset_mm)])

plt.xlabel('detuning (MHz)')
plt.ylabel('capture fraction percent stdev')

# plt.title('Capture fraction stdev against detuning for multiple offsets and 100 sim repeats')

plt.legend()
# plt.minorticks_on()
plt.grid(which='major', linestyle='-')
# plt.grid(which='minor', linestyle='-', color='lightgrey')

ax = plt.gca()
ax.set_xticks(np.arange(-10.0, -56.0, -5.0))
ax.set_yticks(np.arange(0, 810, 100))
ax.invert_xaxis()

plt.show()
