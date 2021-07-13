# -*- coding: utf-8 -*-
"""
This file is part of PyFrac.

Created by Carlo Peruzzo and Andreas Möri on Tue 11:26:51 2021.
Copyright (c) "ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, Geo-Energy Laboratory", 2016-2021.
All rights reserved. See the LICENSE.TXT file for more details.
"""
import numpy as np

# local imports
from mesh import CartesianMesh
from properties import MaterialProperties, FluidProperties, InjectionProperties, SimulationProperties
from fracture import Fracture
from controller import Controller
from fracture_initialization import Geometry, InitializationParameters
from utility import setup_logging_to_console

# -------------- Physical parameter -------------- #

# -- Solid -- #

sigma_o = 1e9
# confining stress [Pa]

E = 1e10
# Young's modulus [Pa]

nu = 0.25
# Poisson's ratio [-]

KIc = 1.5e6
# Fracture toughness of the solid [Pa m^(1/2)]

rho_s = 2700
# density of the solid [kg m^(-3)]

cl = 1e-10
# Carters leak of coefficient [m s^^-1/2)]

# -- Fluid -- #

mu = 1e-3
# dynamic fluid viscosity [Pa s]

rho_f = 1e3
# fluid density [kg m^(-3)]


# -- Injection -- #

t_change = [0.0, 600, 1000, 1600]
# times when the injection rate changes [s]
# Note: For a continuous injection use "t_change = []". For other injection histories the first entry always needs
# to be 0.0!

Qo = [0.01, 0.0, 0.015, 0.0]
# Injection rates in the time windows defined in t_change [m^3/s]
# Note: For a continuous injection use "Qo = your_injection_rate". For injection histries the number of entries in Qo
# must match with the number of entries in t_change. First entry of Qo is injection for t between the first and second
# entry of t_change.

# -- Geometry -- #

r_init = 5e-4
# initial radius of the fracture [m]


# -------------- Essential simulation parameter -------------- #

# -- Space discretization -- #

domain_limits = [-5, 5, -5, 5]
# Limits of the simulated domain [m]. Defined as [min(x), max(x), min(y), max(y)] for the fracture in a x|y plane.

number_of_elements = [61, 61]
# Number of elements [-]. First is the number of elements in direction x, second in direction y.
# Note: We recommend to use a discretization with a minimum of 41 elements (precision) and a maximum of 101 elements
# (computational cost) per direction.

# -- Time discretization (optional) -- #
# Note: Time discretisation is optional as an automatic time-stepping is implemented. You can however specify some
# features that are important for your simulation.

fixed_times = [300, 750, 1500]
# The fracture will automatically be saved at the times fixed within fixed_times [s]. If you leave it empty "fixed_times
# = []" the default scheme is applied.

max_timestep = np.inf
# The maximum a time step can take [s].
# Using np.inf means that we do not fix a maximum for the time-step


# -- Miscellaneous -- #

sim_name = 'Sample_Simulation'
# Name you want to give your simulation. The folder where the data is stored will appear as such.

save_folder = "./Data/Sample_Simulations"
# The folder where the results of your simulation get saved within.

final_time = 1e5
# The time when your simulation should stop [s]


# -------------- Simulation run (do not modify this part) -------------- #
Ep = E/(1 - nu * nu)
mup = 12 * mu
Kp = np.sqrt(32/np.pi)*KIc
if type(Qo) == list:
    Lmk = Ep ** 3 * Qo[0] * mup / Kp ** 4
    Injection = InjectionProperties(Q0, Mesh)
else:
    Lmk = Ep ** 3 * Qo * mup / Kp ** 4
    Injection = InjectionProperties(Q0, Mesh)

if r_init <= 2.7e-3 * Lmk:
    regime = 'M'
elif r_init >= 85.5 * Lmk:
    regime = 'K'
else:
    string_warning = "The intial radius is not represented by the K or M limit.\nChoose either r_init < " + \
                     str(2.7e-3 * Lmk) + " [m] to initiate in the M-regime,\nor r_init > " + str(85.5 * Lmk) + \
                     " [m] to initiate in the K-regime."

    print(string_warning)
    exit(0)

# setting up the verbosity level of the log at console
setup_logging_to_console(verbosity_level='info')

# creating mesh
Mesh = CartesianMesh(domain_limits[:2], domain_limits[3:], number_of_elements[0], number_of_elements[1])

# material properties
Solid = MaterialProperties(Mesh,
                           Ep,
                           KIc,
                           Carters_coef=cl)

# fluid properties
viscosity = 0.001 / 12  # mu' =0.001
Fluid = FluidProperties(viscosity=viscosity)

# simulation properties
simulProp = SimulationProperties()
simulProp.finalTime = 1e7  # the time at which the simulation stops
simulProp.saveTSJump, simulProp.plotTSJump = 5, 5  # save and plot after every 5 time steps
simulProp.set_outputFolder("./Data/MtoK_leakoff")  # the disk address where the files are saved
simulProp.frontAdvancing = 'explicit'  # setting up explicit front advancing
simulProp.plotVar = ['regime', 'w']

# initializing fracture
Fr_geometry = Geometry('radial')
init_param = InitializationParameters(Fr_geometry, regime='M', time=0.5)

# creating fracture object
Fr = Fracture(Mesh,
              init_param,
              Solid,
              Fluid,
              Injection,
              simulProp)

# create a Controller
controller = Controller(Fr,
                        Solid,
                        Fluid,
                        Injection,
                        simulProp)

# run the simulation
controller.run()

# -------------- Post Processing -------------- #








