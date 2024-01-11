# -*- coding: utf-8 -*-
"""
This file is part of PyFrac.

Created by Haseeb Zia on Tue Dec 27 19:01:22 2016.
Copyright (c) "ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, Geo-Energy Laboratory", 2016-2020.
All rights reserved. See the LICENSE.TXT file for more details.
"""

# external imports
import numpy as np


def  get_front_region(mesh, EltRibbon, sgndDist_k_EltRibbon):
    """
    It returns a list of elements that form a band where the location of the tip is expected to be.
    Args:
        mesh:
        EltRibbon:
        sgndDist_k_EltRibbon:
        EltChannel_lstTmStp:

    Returns:

    """
    front_region = []
    advancing_fast = []
    # take the cells in a circle drown from each ribbon cell with radius equal to the distance to the front from the tip inversion
    for i in range(len(EltRibbon)):
        cell_i = EltRibbon[i]
        if np.abs(sgndDist_k_EltRibbon[i]) > mesh.hx and np.abs(sgndDist_k_EltRibbon[i]) > mesh.hy :
            radius_i = np.abs(sgndDist_k_EltRibbon[i]) + 2.5 * mesh.cellDiag
            advancing_fast.append(cell_i)
        else:
            radius_i = np.abs(sgndDist_k_EltRibbon[i]) + 1.5 * mesh.cellDiag
        center_i = mesh.CenterCoor[cell_i]
        new_cells = mesh.get_cells_inside_circle(radius_i, center_i)
        for j in new_cells:
            front_region.append(j)
    front_region = np.unique(front_region)

    # Sanity check:
    # find the cells that are out and surrounded by in and add them to the front region
    #
    #       o----o
    #       | in |
    #  o----o----o----o
    #  | in |out | in |
    #  o----o----o----o
    #       | in |
    #       o----o
    #   -look among the neielem of the current front_region
    probably_out = np.ndarray.flatten(mesh.NeiElements[front_region,:])
    probably_out = np.unique(probably_out)
    #   -take out the current front_region
    probably_out = np.setdiff1d(probably_out, front_region)
    #   -loop over
    probably_out_nei = mesh.NeiElements[probably_out,:]
    out_to_add = []
    i = 0
    for nei in probably_out_nei:
        common = np.intersect1d(front_region, nei, assume_unique=True)
        if len(common)>3:
            out_to_add.append(probably_out[i])
        i = i+1
    if len(out_to_add)>0:
        front_region = np.concatenate((front_region,out_to_add))


    # take out the ribbon (we let them inside as anyway we do not recalculte the level set there)
    # front_region =np.setdiff1d(front_region, EltRibbon)

    # from utility import plot_as_matrix
    # K = np.zeros((mesh.NumberOfElts,), )
    # K[front_region] = 1
    # K[EltRibbon] = 2
    # plot_as_matrix(K, mesh)
    return front_region


def get_LS_on_cell_vertexes(lvlSet_enclosing, lvlSet_cell):
    """
    It returns the level set at the vertexes of a given cell.

       o----o----o----o
       |enc6|enc5|enc4|
       o----3----2----o
       |enc7|cell|enc3|
       o----0----1----o
       |enc0|enc1|enc2|
       o----o----o----o

    :param lvlSet_enclosing:
    :param lvlSet_cell:
    :return:
    """
    ls_vertexes = np.empty(4, dtype=float)
    [enc0, enc1, enc2, enc3, enc4, enc5, enc6, enc7] = lvlSet_enclosing[:]
    ls_vertexes[0] = np.mean([enc0, enc1, enc7, lvlSet_cell])
    ls_vertexes[1] = np.mean([enc1, enc2, enc3, lvlSet_cell])
    ls_vertexes[2] = np.mean([enc3, enc4, enc5, lvlSet_cell])
    ls_vertexes[3] = np.mean([enc5, enc6, enc7, lvlSet_cell])
    return ls_vertexes


def get_LSangle_on_cell_vertexes(lvlSet_enclosing, lvlSet_cell):
    """
    It returns the level set at the vertexes of a given cell.

       o----o----o----o
       |enc6|enc5|enc4|
       o----3----2----o
       |enc7|cell|enc3|
       o----0----1----o
       |enc0|enc1|enc2|
       o----o----o----o

    :param lvlSet_enclosing:
    :param lvlSet_cell:
    :return:
    """
    ls_angle_vertexes = np.empty(4, dtype=float)
    [enc0, enc1, enc2, enc3, enc4, enc5, enc6, enc7] = lvlSet_enclosing[:]

    dx_couples = [[enc1, enc0, enc7, lvlSet_cell],
                  [enc1, enc2, enc3, lvlSet_cell],
                  [enc4, enc5, enc3, lvlSet_cell],
                  [enc6, enc5, enc7, lvlSet_cell]]

    dy_couples = [[enc7, enc0, enc1, lvlSet_cell],
                  [enc2, enc3, enc1, lvlSet_cell],
                  [enc4, enc3, enc5, lvlSet_cell],
                  [enc6, enc7, enc5, lvlSet_cell]]

    for i in range(4):
        # vertex i
        dx_couple = dx_couples[i]
        dx = np.mean([np.abs(dx_couple[0] - dx_couple[1]), np.abs(dx_couple[2] - dx_couple[3])])
        dy_couple = dy_couples[i]
        dy = np.mean([np.abs(dy_couple[0] - dy_couple[1]), np.abs(dy_couple[2] - dy_couple[3])])
        if dx == 0.:
            ls_angle_vertexes[i] = np.pi/2.
        else:
            ls_angle_vertexes[i] = np.arctan(dy/dx)

    return ls_angle_vertexes