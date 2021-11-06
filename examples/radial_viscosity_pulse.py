# -*- coding: utf-8 -*-
"""
This file is part of PyFrac.

Created by Haseeb Zia on Fri Dec 16 17:49:21 2017.
Copyright (c) "ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, Geo-Energy Laboratory", 2016-2019.
All rights reserved. See the LICENSE.TXT file for more details.
"""

# External imports
import numpy as np
import os

# local imports
from mesh.mesh import CartesianMesh
from solid.solid_prop import MaterialProperties
from fluid.fluid_prop import FluidProperties
from properties import InjectionProperties, SimulationProperties
from fracture.fracture import Fracture
from controller import Controller
from fracture.fracture_initialization import Geometry, InitializationParameters
from utilities.utility import setup_logging_to_console
from utilities.postprocess_fracture import load_fractures

# setting up the verbosity level of the log at console
setup_logging_to_console(verbosity_level='info')

# creating mesh
Mesh = CartesianMesh(2, 2, 41, 41)

# solid properties
nu = 0.4                            # Poisson's ratio
youngs_mod = 3.3e10                 # Young's modulus
Eprime = youngs_mod / (1 - nu**2)   # plain strain modulus
K1c = 0                             # Zero toughness case


# material properties
Solid = MaterialProperties(Mesh,
                           Eprime,
                           K1c)

# injection parameters
Q0 = np.asarray([[0.0, 50],
                 [0.01, 0]])  # injection rate

Injection = InjectionProperties(Q0, Mesh)

# fluid properties
viscosity = 0.001
Fluid = FluidProperties(viscosity=viscosity)

# simulation properties
simulProp = SimulationProperties()
simulProp.finalTime = 5e6                          # the time at which the simulation stops
simulProp.saveTSJump, simulProp.plotTSJump = 3, 3   # save and plot after every 5 time steps
simulProp.set_outputFolder("./Data/Pulse")   # the disk address where the files are saved

# initializing fracture
Fr_geometry = Geometry('radial')
init_param = InitializationParameters(Fr_geometry, regime='M', time=0.05)

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


####################
# plotting results #
####################

if not os.path.isfile('./batch_run.txt'):  # We only visualize for runs of specific examples

    from utilities.visualization import *

    # loading simulation results
    Fr_list, properties = load_fractures(address="./Data/Pulse")       # load all fractures
    time_srs = get_fracture_variable(Fr_list,                             # list of times
                                     variable='time')

    # plot fracture radius
    plot_prop = PlotProperties()
    plot_prop.lineStyle = '.'               # setting the linestyle to point
    plot_prop.graphScaling = 'loglog'       # setting to log log plot
    label = LabelProperties('d_mean')
    label.legend = 'radius'
    Fig_R = plot_fracture_list(Fr_list,
                               variable='d_mean',
                               plot_prop=plot_prop) # numerical radius

    # plot analytical M-vertex solution for radius
    plt_prop = PlotProperties(line_color_anal='b')
    label = LabelProperties('d_mean')
    label.legend = 'M solution'
    Fig_R = plot_analytical_solution(regime='M',
                                     variable='d_mean',
                                     labels=label,
                                     mat_prop=properties[0],
                                     inj_prop=properties[2],
                                     fluid_prop=properties[1],
                                     time_srs=time_srs,
                                     plot_prop=plt_prop,
                                     fig=Fig_R)

    # plot analytical M-pulse-vertex solution for radius
    plt_prop = PlotProperties(line_color_anal='m')
    label = LabelProperties('d_mean')
    label.legend = 'M-pulse solution'
    Fig_R = plot_analytical_solution(regime='Mp',
                                     variable='d_mean',
                                     labels=label,
                                     mat_prop=properties[0],
                                     inj_prop=properties[2],
                                     fluid_prop=properties[1],
                                     time_srs=time_srs,
                                     plot_prop=plt_prop,
                                     fig=Fig_R)

    # plot slice of width
    time_slice = np.asarray([0.5, 5, 45, 5e4, 5e5, 5e6])
    Fr_slice, properties = load_fractures(address="./Data/pulse",
                                          time_srs=time_slice)       # load specific fractures
    time_slice = get_fracture_variable(Fr_slice,
                                       variable='time')

    ext_pnts = np.empty((2, 2), dtype=np.float64)
    Fig_WS_M = plot_fracture_list_slice(Fr_slice[:3],
                                      variable='w',
                                      projection='2D',
                                      plot_cell_center=True,
                                      extreme_points=ext_pnts)
    # plot slice of width analytical
    Fig_WS_M = plot_analytical_solution_slice('M',
                                            'w',
                                            Solid,
                                            Injection,
                                            time_srs=time_slice[:3],
                                            fluid_prop=Fluid,
                                            fig=Fig_WS_M,
                                            point1=ext_pnts[0],
                                            point2=ext_pnts[1])


    ext_pnts = np.empty((2, 2), dtype=np.float64)
    Fig_WS_Mp = plot_fracture_list_slice(Fr_slice[3:],
                                      variable='w',
                                      projection='2D',
                                      plot_cell_center=True,
                                      extreme_points=ext_pnts)
    # plot slice of width analytical
    Fig_WS_Mp = plot_analytical_solution_slice('Mp',
                                            'w',
                                            Solid,
                                            Injection,
                                            time_srs=time_slice[3:],
                                            fluid_prop=Fluid,
                                            fig=Fig_WS_Mp,
                                            point1=ext_pnts[0],
                                            point2=ext_pnts[1])

    # plot slice of pressure
    ext_pnts = np.empty((2, 2), dtype=np.float64)
    Fig_PS_M = plot_fracture_list_slice(Fr_slice[:3],
                                      variable='pn',
                                      projection='2D',
                                      plot_cell_center=True,
                                      extreme_points=ext_pnts)
    # plot slice of width analytical
    Fig_PS_M = plot_analytical_solution_slice('M',
                                            'pn',
                                            Solid,
                                            Injection,
                                            time_srs=time_slice[:3],
                                            fluid_prop=Fluid,
                                            fig=Fig_PS_M,
                                            point1=ext_pnts[0],
                                            point2=ext_pnts[1])


    ext_pnts = np.empty((2, 2), dtype=np.float64)
    Fig_PS_Mp = plot_fracture_list_slice(Fr_slice[3:],
                                      variable='pn',
                                      projection='2D',
                                      plot_cell_center=True,
                                      extreme_points=ext_pnts)
    # plot slice of width analytical
    Fig_PS_Mp = plot_analytical_solution_slice('Mp',
                                            'pn',
                                            Solid,
                                            Injection,
                                            time_srs=time_slice[3:],
                                            fluid_prop=Fluid,
                                            fig=Fig_PS_Mp,
                                            point1=ext_pnts[0],
                                            point2=ext_pnts[1])

    plt.show(block=True)