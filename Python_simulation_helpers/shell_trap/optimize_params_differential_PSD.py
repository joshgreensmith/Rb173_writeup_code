import json 
import os
import numpy as np
import matplotlib.pyplot as plt
import csv
import math
from scipy.optimize import differential_evolution

# Parameter ranges for optimisation
# Quad gradient = 50G/cm - 150G/cm, RF frequency = 2MHz - 20MHz, RF amplitude = 50kHz - 250kHz

debug = False

iteration_num = 0
current_PSD = 0
num_sim_steps = 10000
initial_velocity_std = 0.02779
params_file_name = 'shell_trap_output/optimize_params_differential_out_10.csv'
standard_params = {
  "atom_number": 10000, 
  "num_steps": num_sim_steps, 
  "quad_grad_initial": 120.0, 
  "timestep": 4e-05, 
  "rf_amp": 0.02, 
  "rf_frequency": 7.0, 
  "mot_position_x": 0.0, 
  "mot_position_y": 0.0, 
  "mot_position_z": 0.0, 
  "initial_velocity": 0.0,
  "initial_velocity_std": initial_velocity_std,
  "initial_pos_std": 1e-4,
  "gravity": True
}

# Calculate the average KE of atoms in the trap (for the final time step only)
def calculate_average_KE(vel_filename, mass, number_of_steps):
  with open(vel_filename, 'r') as f:
    reached_last_step = False
    atom_KEs = []
    for line in f:
      if reached_last_step:
        vx = float(line.split('(')[1].split(',')[0])
        vy = float(line.split('(')[1].split(',')[1])
        vz = float(line.split('(')[1].split(',')[1].split(')')[0])

        v = math.sqrt(vx**2 + vy**2 + vz**2)
        KinEnergy = 0.5 * mass * v**2

        atom_KEs.append(KinEnergy)

      if line.startswith("step-" + str(number_of_steps)):
        reached_last_step = True
  
  return np.average(atom_KEs)

# Function to calculate the size of the resonant shell trapping spheroid
def calculate_z0(rf_frequency, quad_grad):
  z0_cm = (rf_frequency) / (2 * 0.7 * quad_grad)
  return z0_cm * 1e-2

# Function to calculate the equivalent PSD at a given timestep
def calculate_timestep_PSD(pos_filename, vel_filename, mass, timestep, z0):
  atom_positions = []
  atom_velocities_squared = []

  # Extract positions and velocities in the final time step from the files given
  with open(pos_filename, 'r') as f:
    reached_time_step = False 
    for line in f:
      if line.startswith("step-" + str(timestep)):
        reached_time_step = True
        continue
      elif line.startswith("step-") and int(line.split('-')[1].split(',')[0]) > timestep:
        break

      if reached_time_step:
        x = float(line.split('(')[1].split(',')[0])
        y = float(line.split('(')[1].split(',')[1])
        z = float(line.split('(')[1].split(',')[1].split(')')[0])

        atom_positions.append([x,y,z])

  with open(vel_filename, 'r') as f:
    reached_time_step = False
    for line in f:
      if line.startswith("step-" + str(timestep)):
        reached_time_step = True
        continue
      elif line.startswith("step-") and int(line.split('-')[1].split(',')[0]) > timestep:
        break

      if reached_time_step:
        vx = float(line.split('(')[1].split(',')[0])
        vy = float(line.split('(')[1].split(',')[1])
        vz = float(line.split('(')[1].split(',')[1].split(')')[0])

        v2 = vx**2 + vy**2 + vz**2
        atom_velocities_squared.append(v2)    

  # Calculate the range of x values in the shell trap and the size of the PSD bounding box
  x_min = np.array(atom_positions).min(axis=0)[0]
  x_max = np.array(atom_positions).max(axis=0)[0]
  x_range = x_max - x_min
  bounding_box_width = 0.5 * 0.05 * x_range

  # Calculate the atoms inside the bounding box
  bounded_atom_indexes = []
  for i, atom_pos in enumerate(atom_positions):
    if np.abs(atom_pos[0]) < bounding_box_width:
      bounded_atom_indexes.append(i)

  num_bounded_atoms = len(bounded_atom_indexes)

  # Calculate the average kinetic energy for the bounded atoms
  atom_KEs_total = 0
  for i in bounded_atom_indexes:
    atom_KEs_total += 0.5 * mass * atom_velocities_squared[i]
  
  atom_KE_average = atom_KEs_total / num_bounded_atoms

  # Calculate the atom density and the phase space density
  n = num_bounded_atoms / math.pow(bounding_box_width * 2, 3)
  phase_space_density = n / math.pow(atom_KE_average, 1.5)

  return phase_space_density

# Function to return the time averaged PSD
def get_PSD(params_arr):
  quad_grad, rf_freq, rf_amp = params_arr
  global current_PSD

  z0 = calculate_z0(rf_freq, quad_grad)

  params = standard_params
  params['quad_grad_initial'] = quad_grad
  params['rf_frequency'] = rf_freq
  params['rf_amp'] = rf_amp
  params['mot_position_z'] = -z0

  with open('input.json', 'w') as f:
    json.dump(params, f)
    f.flush()

  cmd = 'cargo run --example mode_match_shell --release'
  os.system(cmd)

  psd_array = []
  for timestep in np.arange(7500, 10001, 100):
    psd_array.append(calculate_timestep_PSD(
      'shell_trap_output/pos.txt', 
      'shell_trap_output/vel.txt', 
      1.0, 
      timestep, 
      z0
    ))
    
  current_PSD = np.average(psd_array)
  return -current_PSD

# Output function to write parameters to file in scipy callback
def write_params_to_file(params_arr, convergence):
  quad_grad, rf_freq, rf_amp = params_arr
  global iteration_num
  global current_PSD
  writer.writerow([iteration_num, quad_grad, rf_freq, rf_amp, current_PSD])
  f.flush()
  iteration_num += 1

if debug:
  print(calculate_z0(7, 120))
  # print(calculate_z0(15.7, 50))
  # print(calculate_timestep_PSD("shell_trap_output/pos.txt", "shell_trap_output/vel.txt", 1.0, 9000, 520e-6))

else:
  # Run differential evolution and output parameter evolution to a file
  kHzToGauss = 0.002857
  bounds = [(25, 100), (14, 16), (50 * kHzToGauss, 250 * kHzToGauss)]
  with open(params_file_name, 'w') as f:
    header = ['iteration number', 'quad gradient', 'rf frequency', 'rf amplitude', 'Phase space density']
    writer = csv.writer(f)
    writer.writerow(header)
    res = differential_evolution(
      get_PSD, 
      bounds, 
      maxiter=10000,
      popsize=15,
      mutation=0.7,
      callback=write_params_to_file
    )

  print(res)
