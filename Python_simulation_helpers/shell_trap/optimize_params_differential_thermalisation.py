import json 
import os
import numpy as np
import matplotlib.pyplot as plt
import csv
import math
from random import uniform
from scipy.optimize import differential_evolution

# Parameter ranges for optimisation
# Quad gradient = 50G/cm - 150G/cm, RF frequency = 2MHz - 20MHz, RF amplitude = 50kHz - 250kHz

debug = True

iteration_num = 0
current_temp = 0
num_sim_steps = 10000
output_freq = 100
initial_velocity_std = 0.02779
standard_params = {
  "atom_number": 10000, 
  "num_steps": num_sim_steps, 
  "quad_grad_initial": 120.0, 
  "timestep": 8e-05, 
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

# Function to calculate the size of the resonant shell trapping spheroid
def calculate_z0(rf_frequency, quad_grad):
  z0_cm = (rf_frequency) / (2 * 0.7 * quad_grad)
  return z0_cm * 1e-2

# Function to return an array of arrays of |v|^2 of each atom at each timestep
def get_vel_squared_arr(vel_filename, total_timesteps):
  vel_squared_arr = [[] for _ in range(total_timesteps)]
  with open(vel_filename, 'r') as f:
    step = -1
    for line in f:
      if line.startswith("step-"):
        step += 1
        continue

      vx = float(line.split('(')[1].split(',')[0])
      vy = float(line.split('(')[1].split(',')[1])
      vz = float(line.split('(')[1].split(',')[1].split(')')[0])

      v2 = vx**2 + vy**2 + vz**2
      vel_squared_arr[step].append(v2)

  return vel_squared_arr

# Function to return the equivalent thermalisation temperature from a given AtomECS output
def get_thermalisation_temp(params_arr):
  quad_grad, rf_freq, rf_amp = params_arr
  global current_temp

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

  # Calculate the averaged KE over the last 2500 timesteps
  vel_squared_arr = get_vel_squared_arr('shell_trap_output/vel.txt', int(num_sim_steps/output_freq))
  average_vel_squared_arr = [np.mean(vel_arr) for vel_arr in vel_squared_arr[int((num_sim_steps/output_freq)*0.75):]]
  average_vel_squared = np.mean(average_vel_squared_arr)
  average_KE = 0.5 * 87 * 1.66054e-27 * average_vel_squared
  current_temp = ((2/3) * average_KE) / 1.38065e-23

  return current_temp

# Output function to write parameters to file in scipy callback
def write_params_to_file(params_arr, convergence):
  quad_grad, rf_freq, rf_amp = params_arr
  global iteration_num
  global current_temp
  writer.writerow([iteration_num, quad_grad, rf_freq, rf_amp, current_temp])
  f.flush()
  iteration_num += 1

if debug:
  print(calculate_z0(14.5, 30.0))
  # print(calculate_timestep_PSD("shell_trap_output/pos.txt", "shell_trap_output/vel.txt", 1.0, 9000, 520e-6))

else:
  # Run the differential evolution function and output evolution to a file
  kHzToGauss = 0.002857
  bounds = [(25, 100), (14, 16), (50 * kHzToGauss, 250 * kHzToGauss)]
  for i in range(1, 100):
    params_file_name = 'shell_trap_output/optimize_params_differential_out_2.' + str(i) + '.csv'
    x0 = (uniform(25, 100), uniform(14, 16), uniform(50 * kHzToGauss, 250 * kHzToGauss))
    with open(params_file_name, 'w') as f:
      header = ['iteration number', 'quad gradient', 'rf frequency', 'rf amplitude', 'current temperature']
      writer = csv.writer(f)
      writer.writerow(header)
      res = differential_evolution(
        get_thermalisation_temp, 
        bounds, 
        maxiter=60,
        popsize=15,
        mutation=0.7,
        tol=1e-8,
        callback=write_params_to_file,
        x0=x0
      )

  print(res)
