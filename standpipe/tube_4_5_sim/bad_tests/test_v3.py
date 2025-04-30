from pygran import simulation
from pygran.params import organic, glass
import numpy as np
from lammps import LMP_STYLE_ATOM, LMP_TYPE_VECTOR

params = {
    # Define the system
    'boundary': ('f', 'f', 'p'),
    'box': (-1e-3, 1e-3, -1e-3, 1e-3, -4e-3, 4e-3),

    # Define component(s)
    'species': ({'material': organic, 'radius': ('constant', 5e-5)},),

    # Setup I/O params
    'traj': {'freq': 1000, 'style': 'custom/vtk', 'pfile': 'particles*.vtk', 'mfile': 'mesh*.vtk'},

    # Output dir name
    'output': 'DEM_flow',

    # Define computational parameters
    'dt': 1e-6,

    # Apply a gravitational force in the negative direction along the z-axis
    'gravity': (9.81, 0, 0, -1),

    # Import hopper + impeller mesh
    'mesh': {
        'hopper': {'file': 'mesh/silo.stl', 'mtype': 'mesh/surface', 'material': glass,
                   'args': {'scale': 1e-3}},
        'tube': {'file': 'mesh/tube.stl', 'mtype': 'mesh/surface', 'material': glass,
                 'args': {'move': (0, 0, -5.1e1), 'scale': 4e-5}},
    },

    # Stage runs
    'stages': {'insertion': 1e5, 'run': 2e5},
}

# Create an instance of the DEM class
sim = simulation.DEM(**params)

# Setup a primitive static wall (stopper) along the xoy plane at z=0 of material properties defined in species 1
stopper = sim.setupWall(species=1, wtype='primitive', plane='zplane', peq=0.0)

# Insert particles every 1e4 steps in a rectangular region of length/width 1e-3 m and height 1e-3 m.
# Insertion is done here based on region volume fraction approaching 1.0
insert = sim.insert(species=1, region=('block', -5e-4, 5e-4, -5e-4, 5e-4, 2e-3, 3e-3),
                    mech='volumefraction_region', value=1, freq=1e4)

# Run simulation for 1e5 steps then stop insertion
sim.run(params['stages']['insertion'], params['dt'])
sim.remove(insert)

# Remove stopper then run the system for another 1e5 steps (flow stage)
sim.remove(stopper)

sim.command('compute zpos all property/atom z')
# Helper function to grab current z positions
def get_z_positions():
    # Extract the 'z' coordinate data for all atoms
    buf = sim.extract_compute('zpos', LMP_STYLE_ATOM, LMP_TYPE_VECTOR)
    n_atoms = sim.get_natoms()
    # Convert the buffer to a NumPy array
    z_positions = np.frombuffer(buf, dtype=np.float64, count=n_atoms)
    return z_positions

# Define simulation parameters
zmin, zmax = params['box'][4], params['box'][5]
dt = params['dt']
total_steps = int(params['stages']['run'])
chunk = 1000
tol = 1e-8

# Initialize previous z positions
prev_z = get_z_positions()
times, rates = [], []

# Run the simulation in chunks and calculate flow rates
for step in range(0, total_steps, chunk):
    sim.run(chunk, dt)
    cur_z = get_z_positions()

    # Count wrap-arounds
    wrapped = (prev_z > zmax - tol) & (cur_z < zmin + tol)
    nwrap = wrapped.sum()

    t_now = (step + chunk) * dt
    rate_now = nwrap / (chunk * dt)

    print(f"{t_now:.6f}s: {rate_now:.2f} particles/s")
    times.append(t_now)
    rates.append(rate_now)

    prev_z = cur_z.copy()

