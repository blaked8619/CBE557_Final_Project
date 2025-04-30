from pygran import simulation
from pygran.params import organic, glass
import io

params = {
	# Define the system
	'boundary': ('f','f','p'),
	'box':  (-1e-3, 1e-3, -1e-3, 1e-3, -0.5e-3, 3e-3),

	# Define component(s)
	'species': ({'material': organic, 'radius': ('constant', 5e-5)},),

	# Setup I/O params
	'traj': {'freq':1000, 'style': 'custom/vtk', 'pfile': 'particles*.vtk', 'mfile': 'mesh*.vtk'},

	# Output dir name
        'output': 'DEM_flow',

	# Define computational parameters
	'dt': 1e-6,

	# Apply a gravitional force in the negative direction along the z-axis
	'gravity': (9.81, 0, 0, -1),

	# Import hopper + impeller mesh
	 'mesh': {
		'hopper': {'file': 'mesh/silo.stl', 'mtype': 'mesh/surface', 'material': glass, \
                   'args': {'scale': 1e-3}},
		'sphere': {'file': 'mesh/sphere.stl', 'mtype': 'mesh/surface', 'material': glass, \
                'args': {'heal': 'auto_remove_duplicates', 'move': (0, 0, 0.4e1), 'scale': 2.75e-4}},
	},

	# Stage runs
	'stages': {'insertion': 1e5, 'run': 5e5},   # I think 10e5 will be a good run number
}


# Create an instance of the DEM class
sim = simulation.DEM(**params)

# Setup a primitive static wall (stopper) along the xoy plane at z=0 of material propreties defined in species 1
stopper = sim.setupWall(species=1, wtype='primitive', plane = 'zplane', peq = 0.0)

# Insert particles every 1e4 steps in a rectangular region of length/width 1e-3 m and height 1e-3 m. Insertion is done here based on region volume fraction approaching 1.0
insert = sim.insert(species=1, region=('block', -5e-4, 5e-4, -5e-4, 5e-4, 2e-3, 3e-3), \
                    mech='volumefraction_region', value=1, freq=1e4)

# Run simulation for 1e5 steps then stop insertion
sim.run(params['stages']['insertion'], params['dt'])
sim.remove(insert)

# Rotate the impeller along the z-axis around the origin and of period 5e-2 s.
#rotImp = sim.moveMesh('impeller', rotate=('origin', 0, 0, 0), axis=(0, 0, 1), period=5e-2)

# Blend the system by running for 1e5 steps then stop impeller rotation
#sim.run(params['stages']['run'], params['dt'])
#sim.remove(rotImp)

# Remove stopper then run the system for another 1e5 steps (flow stage)
sim.remove(stopper)
sim.run(params['stages']['run'], params['dt'])

# Play video
#video = io.open('movie/flow.mp4', 'r+b').read()
