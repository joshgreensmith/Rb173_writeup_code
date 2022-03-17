import json 
import os
import numpy as np
import matplotlib.pyplot as plt
import csv
import math

# Function to calculate the average kinetic energy of the atoms from the velocity output
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

print(calculate_average_KE('shell_trap_output/vel.txt', 1.0, 20000))