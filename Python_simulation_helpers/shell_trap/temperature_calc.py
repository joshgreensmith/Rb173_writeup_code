import csv
import math

def mass1KEtoMicroKelvinTemperature(KE):
  kB = 1.38e-23
  actual_KE = KE * 87 * 1.67e-27
  return actual_KE * (2/3) * (1/kB) * 1e6

def numberOfAtomsBelowThreshold(filename, temp_threshold, number_of_steps):
  with open(filename, 'r') as f:
    reached_last_step = False
    atom_temps = []
    for line in f:
      if reached_last_step:
        vx = float(line.split('(')[1].split(',')[0])
        vy = float(line.split('(')[1].split(',')[1])
        vz = float(line.split('(')[1].split(',')[1].split(')')[0])

        v = math.sqrt(vx**2 + vy**2 + vz**2)
        KinEnergy = 0.5 * v**2
        temp = mass1KEtoMicroKelvinTemperature(KinEnergy)

        atom_temps.append(temp)

      if line.startswith("step-" + str(number_of_steps)):
        reached_last_step = True

  number_of_atoms_below_threshold = 0
  for atom_temp in atom_temps:
    if atom_temp < temp_threshold:
      number_of_atoms_below_threshold += 1

  return number_of_atoms_below_threshold

# print(numberOfAtomsBelowThreshold("shell_trap_output/vel.txt", 10, 5000))
print(mass1KEtoMicroKelvinTemperature(0.035))