#external imports
import copy
import json
import os
import shutil
import numpy as np

# internal imports
from controller import Controller
from properties import InjectionProperties
from solid.solid_prop import MaterialProperties
from utilities.postprocess_fracture import load_fractures, append_to_json_file
from utilities.utility import setup_logging_to_console


# setting up the verbosity level of the log at console
setup_logging_to_console(verbosity_level='info')

def check_make_folder(simdir):
    if os.path.isdir(simdir):
        print('  the folder exist')
    else:
        print('  the folder do not exist')
        os.mkdir(simdir)

def check_copy_file(dest_file, src_file):

    if os.path.isfile(dest_file):
        print('  the file exist')
    else:
        print('  the file does not exist: copying it')
        shutil.copy(src_file, dest_file,follow_symlinks=True)

def copy_dir(dest_folder, src_folder):

    if os.path.isdir(src_folder):
        print('  the folder exist: copying to the new location')
        if os.path.isdir(dest_folder):
            print('  the new location existed and it will be removed')
            shutil.rmtree(dest_folder)
        shutil.copytree(src_folder, dest_folder)
    else:
        print('  the folder does not exist: abort')
        raise SystemExit
# --------------------------------------------------------------
def smoothing(K1, K2, r, delta, x):
    # instead of having -10/10, take the MESHNAME.Ly/Lx (if mesh square)
    #### LINEAR - DIRAC DELTA ####
    x = np.abs(x)
    if  x < r-delta :
        return K1
    elif x >= r-delta and x<r :
        K12 = K1 + (K2-K1)*1.
        a = (K12 - K1) / (delta)
        b = K1 - a * (r - delta)
        return a * x + b
    elif x >= r:
        return K2
    else:
        print("ERROR")

class K1c_func_factory:
     def __init__(self, r, K_Ic, KIc_ratio, hx, hy, delta = 0.001):
         self.K_Ic = K_Ic # fracture toughness
         self.r = r # 1/2 height of the layer
         self.KIc_ratio = KIc_ratio
         self.delta = delta
         # check
         if delta > hx/20. or delta > hy/20.:
             print('regularization param > 1/20 cell size')

     def __call__(self, x, y, alpha):
         """ The function providing the toughness"""
         return smoothing(self.K_Ic, self.KIc_ratio * self.K_Ic, self.r, self.delta, x)

def sigmaO_func(x, y):
    return 0

# --------------------------------------------------------------
def get_fracture_sizes(Fr):
    # Now we are at a given time step.
    # This function returns the coordinates of the smallest rectangle containing the fracture footprint

    x_min_temp = 0.
    x_max_temp = 0.
    y_min_temp = 0.
    y_max_temp = 0.
    hx = Fr.mesh.hx; hy = Fr.mesh.hy
    # loop over the segments defining the fracture front
    for i in range(Fr.Ffront.shape[0]):
        segment = Fr.Ffront[i]

        # to find the x_max at this segment:
        if segment[0] > x_max_temp and np.abs(segment[1])<2.*hy:
            x_max_temp = segment[0]
        if segment[2] > x_max_temp and np.abs(segment[3])<2.*hy:
            x_max_temp = segment[2]

        # to find the n_min at this segment:
        if segment[0] < x_min_temp and np.abs(segment[1])<2.*hy:
            x_min_temp = segment[0]
        if segment[2] < x_min_temp and np.abs(segment[3])<2.*hy:
            x_min_temp = segment[2]

        # to find the y_max at this segment:
        if segment[1] > y_max_temp and np.abs(segment[0])<2.*hx:
            y_max_temp = segment[1]
        if segment[3] > y_max_temp and np.abs(segment[2])<2.*hx:
            y_max_temp = segment[3]

        # to find the y_min at this segment:
        if segment[1] < y_min_temp and np.abs(segment[0])<2.*hx:
            y_min_temp = segment[1]
        if segment[3] < y_min_temp and np.abs(segment[2])<2.*hx:
            y_min_temp = segment[3]

    return x_min_temp, x_max_temp, y_min_temp, y_max_temp

# --------------------------------------------------------------
# define the terminating criterion function
class terminating_criterion_factory:
    def __init__(self, aspect_ratio_target, xmax_lim, aspect_ratio_toll):
        self.x_lim = x_lim  # max value of x that can be reached during the simulation
        self.aspect_ratio_target = aspect_ratio_target  # target aspect ratio that can be reached during the simulation
        self.aspect_ratio_toll = aspect_ratio_toll

    def __call__(self, fracture):
        """ The implementing the terminating_criterion"""
        x_min, x_max, y_min, y_max = get_fracture_sizes(fracture)
        larger_abs_x = np.maximum(np.abs(x_min),x_max)
        x_dimension = np.abs(x_min) + x_max
        y_dimension = np.abs(y_min) + y_max
        aspect_ratio = y_dimension / x_dimension
        if  aspect_ratio < (self.aspect_ratio_target) and larger_abs_x < self.x_lim :
            return True
        else:
            return False

# defining the return function in case the simulation ends according to the terminating criterion function
def return_function(fracture):
    return fracture

class adapive_time_ref_factory():
    def __init__(self, aspect_ratio_max, aspect_ratio_toll, xmax_lim):
        self.xmax_lim = xmax_lim  # max value of x that can be reached during the simulation
        self.aspect_ratio_max = aspect_ratio_max  # max aspect ratio that can be reached during the simulation
        self.aspect_ratio_toll = aspect_ratio_toll
        self.active_adaptive_time_ref=False
        self.upper_time_bound=None
        self.lower_time_bound=None

    def __call__(self, Fr_current, Fr_new, timestep):
        """ checking how far we are from the goal of getting an aspect ratio close to 1"""
        x_min_c, x_max_c, y_min_c, y_max_c = get_fracture_sizes(Fr_current)
        larger_abs_x_c = np.maximum(np.abs(x_min_c), x_max_c)
        x_dimension_c = np.abs(x_min_c) + x_max_c
        y_dimension_c = np.abs(y_min_c) + y_max_c
        aspect_ratio_c = y_dimension_c / x_dimension_c

        x_min_n, x_max_n, y_min_n, y_max_n = get_fracture_sizes(Fr_new)
        larger_abs_x_n = np.maximum(np.abs(x_min_n),x_max_n)
        x_dimension_n = np.abs(x_min_n) + x_max_n
        y_dimension_n = np.abs(y_min_n) + y_max_n
        aspect_ratio_n = y_dimension_n / x_dimension_n

        aspect_ratio_bridging_target = (aspect_ratio_c < (self.aspect_ratio_max) and \
                aspect_ratio_n >= (self.aspect_ratio_max + self.aspect_ratio_toll))
        if aspect_ratio_bridging_target or self.active_adaptive_time_ref:
            if self.active_adaptive_time_ref == False:
                self.active_adaptive_time_ref = True
                self.lower_time_bound = Fr_current.time
                self.upper_time_bound = Fr_new.time
                # we should limit the time step
                timestep_new = np.abs(np.abs(self.upper_time_bound + self.lower_time_bound) * 0.5 - Fr_current.time)
                return  timestep_new, True
            elif self.active_adaptive_time_ref and aspect_ratio_n >= (self.aspect_ratio_max + self.aspect_ratio_toll):
                # the time step is still too large
                self.upper_time_bound = Fr_new.time
                # we should limit the time step and update the upper bound
                timestep_new = np.abs(np.abs(self.upper_time_bound + self.lower_time_bound) * 0.5 - Fr_current.time)
                return timestep_new, True
            elif self.active_adaptive_time_ref and aspect_ratio_n < (self.aspect_ratio_max):
                # the time step is too little
                self.lower_time_bound = Fr_new.time
                # we should increase the time step and update
                timestep_new = np.abs(np.abs(self.upper_time_bound + self.lower_time_bound) * 0.5 - Fr_current.time)
                return timestep_new, True
            elif self.active_adaptive_time_ref and (aspect_ratio_n >= self.aspect_ratio_max and aspect_ratio_n < (self.aspect_ratio_max + self.aspect_ratio_toll)):
                # accept time step!!! and restore active time ref
                self.active_adaptive_time_ref = False
                self.upper_time_bound = None
                self.lower_time_bound = None
                return timestep, False
            else:
                SystemExit("ERROR adapive_time_ref_factory: option not allowed")
        return timestep, False

def run(r_0, Solid_loaded, Injection, Fr, KIc_ratio, delta, simulProp, Fluid):
    # define the toughenss function
    K1c_func = K1c_func_factory(r_0, Solid_loaded.K1c[0], KIc_ratio, Fr.mesh.hx, Fr.mesh.hy, delta=delta)
    Solid = MaterialProperties(Fr.mesh,
                               Solid_loaded.Eprime,
                               K1c_func=K1c_func,
                               confining_stress_func=sigmaO_func,
                               confining_stress=0.,
                               minimum_width=0.)
    Injection = InjectionProperties(Injection.injectionRate[1, 0], Fr.mesh)
    simulProp.meshReductionPossible = False
    simulProp.meshExtensionAllDir = True
    simulProp.finalTime = 10. ** 30
    simulProp.maxFrontItrs = 45
    simulProp.tmStpPrefactor = 0.50
    simulProp.tolFractFront = 0.0001
    simulProp.set_outputFolder(simdir)
    simulProp.LHyst__ = []
    simulProp.tHyst__ = []
    # define the adaptive time step function to get the simulation reaching ar = ar_desired +/- toll
    simulProp.adaptive_time_refinement = adapive_time_ref_factory(aspect_ratio_max, aspect_ratio_toll, xmax_lim)

    # define the terminating criterion function
    simulProp.terminating_criterion = terminating_criterion_factory(aspect_ratio_target, x_lim, aspect_ratio_toll)

    # defining the return function in case the simulation ends according to the terminating criterion function
    simulProp.return_function = return_function

    # create a Controller
    controller = Controller(Fr,
                            Solid,
                            Fluid,
                            Injection,
                            simulProp)

    # run the simulation
    last_Fr = controller.run()
    return last_Fr

# --------------------------------------------------------------
# --------------------------------------------------------------
print('STARTING SIMULATION:')
# educated  guess
TR = np.asarray([106.917185481925, 23.988447321363665, 7.999417382598588, 7.078244250253137, 6.674610843009765, 4.25540730566231, 1.7741874780639637, 1.4287380449729226, 1.4060753589175625, 1.34375, 110.2154412738598, 77.24778713486634, 32.87565342867487, 31.879539259028782, 49.53006308329436, 45.55276195149959, 117.87413570419311, 91.80141011018539, 56.847730402357456, 44.90514509436578, 27.647511224415616, 27.823979905656486, 64.6152790349907, 25.237905789552585, 21.474085895589518, 16.277029034014507, 13.629805293793265, 11.683741966638067, 10.099601610262912, 10.25443151013145, 9.340843671961121, 5.850190820510264, 5.697990573314791, 4.936385510414589, 5.003375991127431, 4.550624892690718, 3.848481392454521, 2.8963250655543007, 2.449034498944342, 2.1680369874482697, 1.8200747720671098, 1.6121301060492836, 1.5840184937241348, 1.5514235878663767, 1.3124865389282827, 1.2975685012603453, 1.210736583581057, 1.2061131990555705, 1.4152003420871764, 1.4039258535445787, 1.2109375, 1.2754254657920683, 1.2049531456395393, 1.0544406793105026, 1.1247531793105026, 1.3172580621230026, 1.1467716727514226, 1.049220173014882, 1.2777413159664945, 1.10205078125, 1.1152692157920683, 1.0796001517557432, 1.0830205056228568, 1.189253663087742, 58.10357100799947, 37.79264252139599, 1.075421473714736])
SIM_ID = np.asarray([10, 420, 720, 760, 770, 910, 1190, 1330, 1340, 1640, 20, 80, 320, 330, 220, 230, 0, 30, 170, 270, 370, 380, 130, 430, 470, 520, 570, 620, 660, 670, 710, 810, 820, 860, 870, 920, 960, 1010, 1060, 1110, 1180, 1250, 1260, 1270, 1400, 1410, 1480, 1490, 1560, 1570, 1630, 1720, 1890, 1960, 1970, 1980, 2050, 2060, 1420, 1650, 1710, 1730, 1800, 1810, 180, 280, 1880])

file_name = "AR_high_K.json"
globalpath = '/home/peruzzo/PycharmProjects/PyFrac/03_Three_toughness_layers/Data_final/10space_inv'
date_ext = '2022-02-02__09_02_40'
basename = '/simulation__'+date_ext+'_file_'

todo = []
todo_n = []
locallist = SIM_ID
recompute = []

for number in locallist:
    if number not in todo_n:
        todo.append(str(number))
todo_n = len(todo)

# copy the file for safety!
baseloc = "/home/peruzzo/PycharmProjects/PyFrac/03_Three_toughness_layers/Data_final/10space_inv/"
file_name_copy = "AR_high_K_copy.json"
if os.path.isfile(file_name):
    shutil.copyfile(baseloc+file_name, baseloc+file_name_copy)

# initialize some vars
results = {"toughness ratio" : [],
            "sim id" : [],
            "aspect ratio" : [],
            "aspect_ratio_toll": [],
            "aspect_ratio_target": [],
            "x_max": [],
            "x_min": [],
            "x_lim": [],
            "xmax_lim": [],
            "delta": [],
            "halfH": [],
            }
KIc_ratio = None

# define the results or read them
if not os.path.isfile(file_name):
    content = results
    action = 'dump_this_dictionary'
    append_to_json_file(file_name, [content], action, delete_existing_filename=False)
else:
    with open(file_name, "r+") as json_file:
        results = json.load(json_file)[0]  # get the data


for num_id, num in enumerate(todo):

    print(f'sim {num_id+1} of {todo_n}\n')

    calc = False
    if int(num) not in results["sim id"]:
        calc = True
    elif int(num) in recompute and int(num) in results["sim id"]:
        pos = np.where(np.asarray(results["sim id"]) == int(num))[0][0]
        results["toughness ratio"].pop(pos)
        results["sim id"].pop(pos)
        results["aspect ratio"].pop(pos)
        results["aspect_ratio_toll"].pop(pos)
        results["aspect_ratio_target"].pop(pos)
        results["x_max"].pop(pos)
        results["x_min"].pop(pos)
        results["x_lim"].pop(pos)
        results["xmax_lim"].pop(pos)
        results["delta"].pop(pos)
        results["halfH"].pop(pos)
        calc = True
        # remove the folder
        if os.path.isdir(globalpath + '/bt/simulation_' + num + '__' + date_ext):
            shutil.rmtree(globalpath + '/bt/simulation_' + num + '__' + date_ext)
        if os.path.isdir(globalpath + '/bt/simulation_' + num + '__' + date_ext + '_copy'):
            shutil.rmtree(globalpath + '/bt/simulation_' + num + '__' + date_ext + '_copy')

    if calc:
        simdir = globalpath + '/bt/simulation_'+num+'__' + date_ext

        # make the folder if it does not exist
        print(' -check if the folder existed')
        check_make_folder(simdir)

        # copy properties if they do not exist
        print('\n -check if the properties existed')
        dest_file = simdir + '/properties'
        src_file = globalpath + '/simulation__' + date_ext + '/properties'
        check_copy_file(dest_file, src_file)

        # check if the timestep exist in the source dir and copy
        print('\n -check if the initial file existed')
        dest_file = simdir + '/simulation_'+num+'__' + date_ext +'_file_0'
        src_file = globalpath + '/simulation__' + date_ext + '/simulation__' + date_ext + '_file_' + num
        check_copy_file(dest_file, src_file)

        # make a copy of the input folder
        print('\n -check if the newly created folder exist and make a copy of it')
        dest_folder = simdir + '_copy'
        src_folder = simdir
        copy_dir(dest_folder, src_folder)

        # load the fracture obj
        Fr_list, properties = load_fractures(address=globalpath + '/bt', step_size=100, sim_name='simulation_' + num)
        Solid_loaded, Fluid, Injection, simulProp = properties
        contunue_loop = True

        if not len(Fr_list[-1].EltCrack) > 8000:
            increase_KIc = True
            while increase_KIc:
                Fr = copy.deepcopy(Fr_list[-1])

                # define the hard limit
                x_min, x_max, y_min, y_max = get_fracture_sizes(Fr)
                r_0 = np.maximum(np.abs(x_min), np.abs(x_max)) + Fr.mesh.hx
                delta = Fr.mesh.hx / 100.
                x_lim = r_0

                # tollerance aspect ratio
                aspect_ratio_toll = 0.001
                # target aspect ratio
                aspect_ratio_max = 1.02
                # aspect ratio when to stop the simulation
                aspect_ratio_target = aspect_ratio_max

                # tollerance xmax
                toll_xmax = delta
                xmax_lim = x_lim + toll_xmax

                # current state variables
                if int(num) in SIM_ID:
                    pos = np.where(SIM_ID==int(num))[0][0]
                    KIc_ratio = TR[pos] * 1.2
                else:
                    KIc_ratio = 150.


                print(f'\n ID: {num}')
                print(f' toughness ratio: {KIc_ratio}')
                last_Fr = run(r_0, Solid_loaded, Injection, Fr, KIc_ratio, delta, simulProp, Fluid)

                # check if xmax < xlim
                x_min_c, x_max_c, y_min_c, y_max_c = get_fracture_sizes(last_Fr)
                larger_abs_x_c = np.maximum(np.abs(x_min_c), x_max_c)
                x_dimension_c = np.abs(x_min_c) + x_max_c
                y_dimension_c = np.abs(y_min_c) + y_max_c
                aspect_ratio_c = y_dimension_c / x_dimension_c

                if larger_abs_x_c < x_lim:
                    increase_KIc = False
                    results["toughness ratio"].append(KIc_ratio)
                    results["sim id"].append(int(num))
                    results["aspect ratio"].append(aspect_ratio_c)
                    results["aspect_ratio_toll"].append(aspect_ratio_toll)
                    results["aspect_ratio_target"].append(aspect_ratio_target)
                    results["x_max"].append(x_max_c)
                    results["x_min"].append(x_min_c)
                    results["x_lim"].append(x_lim)
                    results["xmax_lim"].append(xmax_lim)
                    results["delta"].append(delta)
                    results["halfH"].append(r_0)

                    print(" Saving to file")
                    content = results
                    action = 'dump_this_dictionary'
                    append_to_json_file(file_name, [content], action, delete_existing_filename=True)

                    # make a copy of the input folder
                    print(' delete the copy of the starting folder')
                    dest_folder = simdir + '_copy'
                    shutil.rmtree(dest_folder)
                    print('-----------------------------')
                else:
                    increase_KIc = True
                    KIc_ratio = KIc_ratio + 5.

print("Done")