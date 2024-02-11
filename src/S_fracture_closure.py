#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 22:08:56 2024

@author: prescelliannanw
"""

from visualization import *
from fracture_initialization import Geometry, InitializationParameters
from controller import Controller
from fracture import Fracture
import numpy as np

# local imports
from mesh import CartesianMesh
from properties import MaterialProperties, FluidProperties, InjectionProperties, SimulationProperties

# creating mesh
Mesh = CartesianMesh(90, 66, 41, 27)

# solid properties
nu = 0.4                            # Poisson's ratio
youngs_mod = 4e10                   # Young's modulus
Eprime = youngs_mod / (1 - nu ** 2)  # plane strain modulus
K_Ic = 5.0e5                        # fracture toughness


def sigmaO_func(x, y):
    """ This function provides the confining stress over the domain"""
    if 0 < y < 7:
        return 5.25e6
    elif y < -50:
        return 5.25e6
    else:
        return 5.e6


# material properties
Solid = MaterialProperties(Mesh,
                           Eprime,
                           toughness=K_Ic,
                           confining_stress_func=sigmaO_func,
                           Carters_coef=1e-6)

# injection parameters
Q0 = np.asarray([[0, 6000], [0.001, 0]])
Injection = InjectionProperties(Q0,
                                Mesh,
                                source_coordinates=[0, -20])

# fluid properties
Fluid = FluidProperties(viscosity=1e-3)


# simulation properties
simulProp = SimulationProperties()
# the time at which the simulation stops
simulProp.finalTime = 1e5
# the disk address where the files are saved
simulProp.set_outputFolder("./Data/fracture_closure")
# setting the parameter for the mesh color coding
simulProp.bckColor = 'confining stress'
# set to plot every four time steps
simulProp.plotTSJump = 4
# setting the parameters that will be plotted
simulProp.plotVar = ['w', 'lk', 'footprint']
# decreasing the time step pre-factor after 6000s
simulProp.tmStpPrefactor = np.asarray([[0, 6000], [0.8, 0.4]])
# increase maximum iterations for the elastohydrodynamic solver
simulProp.maxSolverItrs = 120

# initialization parameters
Fr_geometry = Geometry('radial', radius=20)
init_param = InitializationParameters(Fr_geometry, regime='M')

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


# loading simulation results
time_srs = [230, 1000, 2200, 3200, 4500, 6000, 10388]
Fr_list, properties = load_fractures(address="./Data/fracture_closure",
                                     time_srs=time_srs)

# plot footprint
plt_prop = PlotProperties(color_map='Wistia', line_width=0.2)
Fig_FP = plot_fracture_list(Fr_list,
                            variable='mesh',
                            projection='2D',
                            mat_properties=Solid,
                            backGround_param='confining stress',
                            plot_prop=plt_prop
                            )
plot_prop1 = PlotProperties(plot_FP_time=False)
Fig_FP = plot_fracture_list(Fr_list,
                            variable='footprint',
                            projection='2D',
                            fig=Fig_FP,
                            plot_prop=plot_prop1)
Fig_FP.set_size_inches(5, 4)
plt.show(block=True)
