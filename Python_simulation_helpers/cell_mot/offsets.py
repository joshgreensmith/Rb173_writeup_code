import json
import os
import numpy as np
import matplotlib.pyplot as plt
import csv

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
    print(i)
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

# Output sim results to csv file for retrospective analysis with file flushing
header = ['detuning', 'offset delta', 'number of steps', 'capture fraction array']
with open('cell_mot_output/offsets_run_3.csv', 'w') as f:
  writer = csv.writer(f)
  writer.writerow(header)

  detuning = 12.0
  for offset_delta in np.arange(0.0e-3, 5.0e-3, 0.05e-3):

    capture_fractions = simulate(
      offset_delta=offset_delta,
      detuning=-detuning, 
      number_of_steps=5000,
      number_of_sims=100)

    data = [detuning, offset_delta, 5000, capture_fractions]
    writer.writerow(data)
    f.flush()
