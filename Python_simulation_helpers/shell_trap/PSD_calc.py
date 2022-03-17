def calculate_PSD(pos_filename, vel_filename, mass, number_of_steps, z0):
  atom_positions = []
  atom_velocities_squared = []

  # Extract positions and velocities in the final time step from the files given
  with open(pos_filename, 'r') as f:
    reached_last_step = False 
    for line in f:
      if reached_last_step:
        x = float(line.split('(')[1].split(',')[0])
        y = float(line.split('(')[1].split(',')[1])
        z = float(line.split('(')[1].split(',')[1].split(')')[0])

        atom_positions.append([x,y,z])

      if line.startswith("step-" + str(number_of_steps)):
        reached_last_step = True

  with open(vel_filename, 'r') as f:
    reached_last_step = False
    for line in f:
      if reached_last_step:
        vx = float(line.split('(')[1].split(',')[0])
        vy = float(line.split('(')[1].split(',')[1])
        vz = float(line.split('(')[1].split(',')[1].split(')')[0])

        v2 = vx**2 + vy**2 + vz**2
        atom_velocities_squared.append(v2)

      if line.startswith("step-" + str(number_of_steps)):
        reached_last_step = True

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