import json
import os
import numpy as np
import matplotlib.pyplot as plt
import csv

old_filename = 'cell_mot_output/detunings_offsets_run_3.csv'
new_filename = 'cell_mot_output/detunings_offsets_run_4.csv'

# Function for running a 3D Pyramid MOT simulation with a specific detuning
def simulate(offset_delta, detuning, number_of_steps, number_of_sims):
  # Create the interface file
  params = {
    "offset_delta": offset_delta,
    "detuning": detuning,
    "number_of_steps": number_of_steps
  }

  with open("offsets.json", "w") as outfile:
    json.dump(params, outfile)

  capture_fractions = []
  for i in range(number_of_sims):
    print('\nRunning sim number ' + str(i+1) + ' for offset delta ' + str(offset_delta) + ' and detuning ' + str(detuning) +'\n')
    # Run the rust sim
    cmd = "cargo run --example cell_mot_offsets_detuning --release"
    os.system(cmd)

    capture_fraction = calculate_capture_fraction("cell_mot_output/pos.txt", number_of_steps, 1000)
    capture_fractions.append(capture_fraction)

  return capture_fractions

def calculate_capture_fraction(filename, number_of_steps, number_of_atoms):
  with open(filename, 'r') as fh:
    for line in fh:
        if line.startswith("step-" + str(number_of_steps)):
          return int(line.split(', ')[1]) / number_of_atoms

already_simulated = {}
header = ['detuning', 'offset delta', 'number of steps', 'capture fraction array']
with open(old_filename, 'r') as old_f, open(new_filename, 'w') as new_f:
  reader = csv.reader(old_f)
  writer = csv.writer(new_f)
  writer.writerow(header)

  # Loop through output file and store already outputted offsets and detunings
  for line in reader:
    if len(line) > 0 and line[0] != 'detuning':
      writer.writerow(line)
      detuning = float(line[0])
      offset = float(line[1])
      if offset in already_simulated.keys():
        already_simulated[offset].append(detuning)
      else:
        already_simulated[offset] = [detuning]

  new_f.flush()

  # Output sim results to csv file for retrospective analysis with file flushing
  number_of_steps = 5000
  for offset_delta in np.arange(0.0, 0.0051, 0.0005):
    for detuning in np.arange(10.0, 81.0, 1.0):

      if offset_delta in already_simulated.keys() and detuning in already_simulated[offset_delta]:
        print('Skipping offset ' + str(offset_delta) + ' and detuning ' + str(detuning))
      else:
        capture_fractions = simulate(
          offset_delta=offset_delta,
          detuning=-detuning, 
          number_of_steps=number_of_steps, 
          number_of_sims=100)

        data = [detuning, offset_delta, number_of_steps, capture_fractions]
        writer.writerow(data)
        new_f.flush()
  
