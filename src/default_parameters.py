# -*- coding: utf-8 -*-
"""
This file is part of PyFrac.

Created by Haseeb Zia on 11.05.17.
Copyright (c) ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, Geo-Energy Laboratory, 2016-2019.
All rights reserved. See the LICENSE.TXT file for more details.
"""

# tolerances
toleranceFractureFront = 1.0e-3         # tolerance for the fracture front position solver.
toleranceEHL = 1.0e-4                   # tolerance for the elastohydrodynamic system solver.
tol_projection = 2.5e-3                 # tolerance for the toughness iteration.
toleranceVStagnant = 1e-6               # tolerance on the velocity to decide if a cell is stagnant.

# max iterations
max_front_itrs = 25                     # maximum iterations for the fracture front.
max_solver_itrs = 140                   # maximum iterations for the elastohydrodynamic solver.
max_proj_Itrs = 10                      # maximum projection iterations.

# time and time stepping
tmStp_prefactor = 0.8                   # time step prefactor(pf) to determine the time step(dt = pf*min(dx, dy)/max(v).
req_sol_at = None                       # times at which the solution is required.
final_time = None                       # time to stop the propagation.
maximum_steps = 2000                    # maximum time steps.
timeStep_limit = None                   # limit for the time step.
fixed_time_step = None                  # constant time step.

# time step re-attempt
max_reattemps = 8                       # maximum reattempts in case of time step failure.
reattempt_factor = 0.8                  # the factor by which time step is reduced on reattempts.

# output
plot_figure = True                      # if True, figure will be plotted after the given time period.
save_to_disk = True                     # if True, fracture will be saved after the given time period.
output_folder = None                    # the address to save the output data.
plot_analytical = False                 # if True, analytical solution will also be plotted.
analytical_sol = None                   # the analytical solution to be plotted.
bck_color = None                        # the parameter according to which background is color coded (see class doc).
sim_name = None                         # name given to the simulation.
block_figure = False                    # if true, the simulation will proceed after the figure is closed.
plot_var = ['w']                        # the list of variables to be plotted during simulation.
plot_proj = '2D_clrmap'                 # projection to be plotted with.
plot_time_period = None                 # the time period after which the variables given in plot_var are plotted.
plot_TS_jump = 1                        # the number of time steps after which the given variables are plotted.
save_time_period = None                 # the time period after which the output is saved to disk.
save_TS_jump = 1                        # the number of time steps after which the output is saved to disk.

# type of solver
elastohydr_solver = 'implicit_Anderson' # set the elasto-hydrodynamic system solver to implicit with Anderson iteration.
m_Anderson = 20                          # number of previous solutions to take into account in the Anderson scheme
relaxation_param = 1.0                  # parameter defining the under-relaxation performed (default is not relaxed)
mech_loading = False                    # if True, the mechanical loading solver will be used.
volume_control = False                  # if True, the volume control solver will be used.
viscous_injection = True                # if True, the viscous fluid solver solver will be used.
substitute_pressure = True              # if True, the pressure will be substituted with width to make the EHL system.
solve_deltaP = True                     # if True, the change in pressure, instead of pressure will be solved.
solve_stagnant_tip = False              # if True, stagnant tip cells will also be solved for
solve_tip_corr_rib = True               # if True, the corresponding tip cells to closed ribbon cells will be solved.
solve_sparse = None                     # if True, the fluid conductivity matrix will be made with sparse matrix.

# miscellaneous
tip_asymptote = 'U1'                    # the tip_asymptote to be used (see class documentation for details).
save_regime = False                     # if True, the the regime of the ribbon cells will also be saved.
verbosity = 2                           # the level of details about the ongoing simulation to be plotted.
enable_remeshing = True                 # if true, computation domain will be remeshed after reaching end of the domain.
remesh_factor = 2.                      # the factor by which the mesh is compressed.
front_advancing = 'predictor-corrector' # possible options include 'implicit', 'explicit' and 'predictor-corrector'.
collect_perf_data = False               # if True, performance data will be collected in the form of a tree.
param_from_tip = False                  # set the space dependant tip parameters to be taken from ribbon cell.
save_ReyNumb = False                    # if True, the Reynold's number at each edge will be saved.
save_fluid_flux = False                 # if True, the fluid flux at each edge will be saved.
save_fluid_vel = False                  # if True, the fluid vel at each edge will be saved.
save_fluid_flux_as_vector = False       # if True, the fluid flux at each edge will be saved as vector, i.e. with two components.
save_fluid_vel_as_vector = False        # if True, the fluid vel at each edge will be saved as vector, i.e. with two components.
save_effective_viscosity = False        # if True, the Newtonian equivalent viscosity of the non-Newtonian fluid will be saved.
save_yield_ratio = False                # if True, the ratio of the height of fluid column yielded to total width will be saved.
save_statistics_post_coalescence=False  # if True, the statistics post coalescence of two fractures are saved to json file
gravity = False                         # if True, the effect of gravity will be taken into account.
TI_Kernel_exec_path = '../TI_Kernel/build' # the folder containing the executable to calculate TI elasticity matrix.
explicit_projection = False             # if True, direction from last time step will be used to evaluate TI parameters.
symmetric = False                       # if True, only positive quarter of the cartesian coordinates will be solved.
enable_GPU = False                      # if True, GPU will be use to do the dense matrix vector product.
n_threads = 4                           # setting the number of threads for multi-threaded dot product for RKL scheme.
proj_method = 'ILSA_orig'               # set the method to evaluate projection on front to the original ILSA method.
double_fracture_vol_contr = False       # enable the volume control solver for two fractures
plot_at_sol_time_series = True          # plot when the time is in the requested time series

# Tip leak-off parameter
save_chi = False                        # Question if we save the tip asymptotics leak-off parameter

# Mesh extension
mesh_extension_direction = [False] * 4  # Per default the mesh is not extended in any direction
mesh_extension_factor = 2               # How many total elements we will have in this direction

# fracture geometry
height = None                           # fracture height to calculate the analytical solution for PKN or KGD geometry.
aspect_ratio = None                     # fracture aspect ratio to calculate the analytical solution for TI case.