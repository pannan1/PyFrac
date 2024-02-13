#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 21:47:28 2024

@author: prescelliannanw
"""
from visualization import *
from controller import Controller
from fracture import Fracture
from fracture_initialization import Geometry, InitializationParameters
from properties import InjectionProperties, FluidProperties, SimulationProperties
from properties import MaterialProperties
from mesh import CartesianMesh

# creating mesh
Mesh = CartesianMesh(20, 2.3, 71, 15)

# solid properties, take from QW main fault
nu = 0.29                          # Poisson's ratio
youngs_mod = 2e10                   # Young's modulus
Eprime = youngs_mod / (1 - nu ** 2)  # plane strain modulus, not changed
K_Ic = 5.0e5                        # fracture toughness , havent changed


def sigmaO_func(x, y):
    """ The function providing the confining stress"""
    if abs(y) > 3:
        return 7.5e6
    else:
        return 1e6


Solid = MaterialProperties(Mesh,
                           Eprime,
                           K_Ic,
                           confining_stress_func=sigmaO_func)

# fluid properties
Fluid = FluidProperties(viscosity=1.1e-3)

# injection parameters
Q0 = 0.0001  # injection rate
Injection = InjectionProperties(Q0, Mesh)

# simulation properties
simulProp = SimulationProperties()
simulProp.finalTime = 145.              # the time at which the simulation stops
# setting the parameter according to which the mesh is color coded
simulProp.bckColor = 'sigma0'
simulProp.set_outputFolder("./Data/height_contained")
simulProp.plotVar = ['footprint']       # plotting footprint

# initializing fracture
Fr_geometry = Geometry(shape='radial', radius=1.8)
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


Fr_list, properties = load_fractures(address="./Data/height_contained")
time_srs = get_fracture_variable(Fr_list, variable='time')
label = LabelProperties('d_max')
label.legend = 'fracture length'

plot_prop = PlotProperties(line_style='.',
                           graph_scaling='loglog')

Fig_r = plot_fracture_list(Fr_list,            # plotting fracture length
                           variable='d_max',
                           plot_prop=plot_prop,
                           labels=label)
label.legend = 'fracture length analytical (PKN)'
Fig_r = plot_analytical_solution('PKN',
                                 variable='d_max',
                                 mat_prop=Solid,
                                 inj_prop=Injection,
                                 fluid_prop=Fluid,
                                 fig=Fig_r,
                                 time_srs=time_srs,
                                 h=7.0,
                                 labels=label)

label.legend = 'radius analytical (viscosity dominated)'
plot_prop.lineColorAnal = 'b'
Fig_r = plot_analytical_solution('M',
                                 variable='d_max',
                                 mat_prop=Solid,
                                 inj_prop=Injection,
                                 fig=Fig_r,
                                 fluid_prop=Fluid,
                                 time_srs=time_srs,
                                 plot_prop=plot_prop,
                                 labels=label)

Fr_list, properties = load_fractures(address="./Data/height_contained",
                                     time_srs=np.asarray([1, 5, 20, 50, 80, 110, 140]))
time_srs = get_fracture_variable(Fr_list,
                                 variable='time')
plot_prop_mesh = PlotProperties(text_size=1.7, use_tex=True)
Fig_Fr = plot_fracture_list(Fr_list,  # plotting mesh
                            variable='mesh',
                            projection='3D',
                            backGround_param='sigma0',
                            mat_properties=properties[0],
                            plot_prop=plot_prop_mesh)

Fig_Fr = plot_fracture_list(Fr_list,  # plotting footprint
                            variable='footprint',
                            projection='3D',
                            fig=Fig_Fr)

Fig_Fr = plot_analytical_solution('PKN',  # plotting footprint analytical
                                  variable='footprint',
                                  mat_prop=Solid,
                                  inj_prop=Injection,
                                  fluid_prop=Fluid,
                                  fig=Fig_Fr,
                                  projection='3D',
                                  time_srs=time_srs[2:],
                                  h=7.0)
plt_prop = PlotProperties(line_color_anal='b')
Fig_Fr = plot_analytical_solution('M',
                                  variable='footprint',
                                  mat_prop=Solid,
                                  inj_prop=Injection,
                                  fluid_prop=Fluid,
                                  fig=Fig_Fr,
                                  projection='3D',
                                  time_srs=time_srs[:2],
                                  plot_prop=plt_prop)

plot_prop = PlotProperties(alpha=0.2, text_size=5)  # plotting width
Fig_Fr = plot_fracture_list(Fr_list,
                            variable='w',
                            projection='3D',
                            fig=Fig_Fr,
                            plot_prop=plot_prop)
ax = Fig_Fr.get_axes()[0]
ax.view_init(60, -114)
