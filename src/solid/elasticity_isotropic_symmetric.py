# -*- coding: utf-8 -*-
"""
This file is part of PyFrac.

Created by Haseeb Zia on Tue Dec 27 17:41:56 2016.
Copyright (c) "ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, Geo-Energy Laboratory", 2016-2020.
All rights reserved. See the LICENSE.TXT file for more details.
"""

# external imports
import numpy as np

# internal imports
from mesh_obj.symmetry import get_symetric_elements, get_active_symmetric_elements


def symmetric_elasticity_matrix_from_full(C, mesh):

    all_elmnts, pos_qdrnt, boundary_x, boundary_y = get_active_symmetric_elements(mesh)

    no_elements = len(pos_qdrnt) + len(boundary_x) + len(boundary_y) + 1
    C_sym = np.empty((no_elements, no_elements), dtype=np.float32)

    indx_boun_x = len(pos_qdrnt)
    indx_boun_y = indx_boun_x + len(boundary_x)
    indx_cntr_elm = indx_boun_y + len(boundary_y)

    sym_elements = get_symetric_elements(mesh, pos_qdrnt)
    sym_elem_xbound = get_symetric_elements(mesh, boundary_x)
    sym_elem_ybound = get_symetric_elements(mesh, boundary_y)


    # influence on elements
    for i in range(len(pos_qdrnt)):
        C_sym[i, 0: indx_boun_x] = C[pos_qdrnt[i], sym_elements[:, 0]] + \
                                   C[pos_qdrnt[i], sym_elements[:, 1]] + \
                                   C[pos_qdrnt[i], sym_elements[:, 2]] + \
                                   C[pos_qdrnt[i], sym_elements[:, 3]]

        C_sym[i, indx_boun_x: indx_boun_y] = C[pos_qdrnt[i], sym_elem_xbound[:, 0]] + \
                                             C[pos_qdrnt[i], sym_elem_xbound[:, 3]]

        C_sym[i, indx_boun_y: indx_cntr_elm] = C[pos_qdrnt[i], sym_elem_ybound[:, 0]] + \
                                               C[pos_qdrnt[i], sym_elem_ybound[:, 1]]

    C_sym[0:indx_boun_x, -1] = C[pos_qdrnt, mesh.CenterElts[0]]


    # influence on x boundary elements
    for i in range(len(boundary_x)):
        C_sym[i + indx_boun_x, 0: indx_boun_x] = C[boundary_x[i], sym_elements[:, 0]] + \
                                                 C[boundary_x[i], sym_elements[:, 1]] + \
                                                 C[boundary_x[i], sym_elements[:, 2]] + \
                                                 C[boundary_x[i], sym_elements[:, 3]]

        C_sym[i + indx_boun_x, indx_boun_x: indx_boun_y] = C[boundary_x[i], sym_elem_xbound[:, 0]] + \
                                                           C[boundary_x[i], sym_elem_xbound[:, 3]]

        C_sym[i + indx_boun_x, indx_boun_y: indx_cntr_elm] = C[boundary_x[i], sym_elem_ybound[:, 0]] + \
                                                             C[boundary_x[i], sym_elem_ybound[:, 1]]

    C_sym[indx_boun_x: indx_boun_y, -1] = C[boundary_x, mesh.CenterElts[0]]


    # influence on y boundary elements
    for i in range(len(boundary_y)):
        C_sym[i + indx_boun_y, 0: indx_boun_x] = C[boundary_y[i], sym_elements[:, 0]] + \
                                                 C[boundary_y[i], sym_elements[:, 1]] + \
                                                 C[boundary_y[i], sym_elements[:, 2]] + \
                                                 C[boundary_y[i], sym_elements[:, 3]]

        C_sym[i + indx_boun_y, indx_boun_x: indx_boun_y] = C[boundary_y[i], sym_elem_xbound[:, 0]] + \
                                                           C[boundary_y[i], sym_elem_xbound[:, 3]]

        C_sym[i + indx_boun_y, indx_boun_y: indx_cntr_elm] = C[boundary_y[i], sym_elem_ybound[:, 0]] + \
                                                             C[boundary_y[i], sym_elem_ybound[:, 1]]

    C_sym[indx_boun_y: indx_cntr_elm, -1] = C[boundary_y, mesh.CenterElts[0]]


    #influence on center element
    C_sym[-1, 0: len(pos_qdrnt)] = C[mesh.CenterElts[0], sym_elements[:, 0]] + \
                                   C[mesh.CenterElts[0], sym_elements[:, 1]] + \
                                   C[mesh.CenterElts[0], sym_elements[:, 2]] + \
                                   C[mesh.CenterElts[0], sym_elements[:, 3]]

    C_sym[-1, indx_boun_x: indx_boun_y] = C[mesh.CenterElts[0], sym_elem_xbound[:, 0]] + \
                                          C[mesh.CenterElts[0], sym_elem_xbound[:, 3]]

    C_sym[-1, indx_boun_y: indx_cntr_elm] = C[mesh.CenterElts[0], sym_elem_ybound[:, 0]] + \
                                            C[mesh.CenterElts[0], sym_elem_ybound[:, 1]]

    C_sym[-1, -1] = C[mesh.CenterElts[0], mesh.CenterElts[0]]

    return C_sym


def load_isotropic_elasticity_matrix_symmetric(mesh, Ep):
    """
    Evaluate the elasticity matrix for the whole mesh.

    Arguments:
        mesh (object CartesianMesh):    -- a mesh object describing the domain.
        Ep (float):                     -- plain strain modulus.

    Returns:
        C_sym (ndarray):                -- the elasticity matrix for a symmetric fracture.
    """

    all_elmnts, pos_qdrnt, boundary_x, boundary_y = get_active_symmetric_elements(mesh)

    no_elements = len(pos_qdrnt) + len(boundary_x) + len(boundary_y) + 1
    C_sym = np.empty((no_elements, no_elements), dtype=np.float32)

    indx_boun_x = len(pos_qdrnt)
    indx_boun_y = indx_boun_x + len(boundary_x)
    indx_cntr_elm = indx_boun_y + len(boundary_y)

    sym_elements = get_symetric_elements(mesh, pos_qdrnt)
    sym_elem_xbound = get_symetric_elements(mesh, boundary_x)
    sym_elem_ybound = get_symetric_elements(mesh, boundary_y)

    a = mesh.hx / 2.
    b = mesh.hy / 2.

    # influence on elements
    for i in range(len(pos_qdrnt)):
        x = mesh.CenterCoor[pos_qdrnt[i], 0] - mesh.CenterCoor[:, 0]
        y = mesh.CenterCoor[pos_qdrnt[i], 1] - mesh.CenterCoor[:, 1]

        C_i = (Ep / (8. * np.pi)) * (np.sqrt(np.square(a - x) + np.square(b - y)) / ((a - x) * (b - y)) + np.sqrt(
            np.square(a + x) + np.square(b - y)) / ((a + x) * (b - y)) + np.sqrt(np.square(a - x) + np.square(b + y)
            ) / ((a - x) * (b + y)) + np.sqrt(np.square(a + x) + np.square(b + y)) / ((a + x) * (b + y)))

        C_sym[i, 0: indx_boun_x] = C_i[sym_elements[:, 0]] + \
                                   C_i[sym_elements[:, 1]] + \
                                   C_i[sym_elements[:, 2]] + \
                                   C_i[sym_elements[:, 3]]

        C_sym[i, indx_boun_x: indx_boun_y] = C_i[sym_elem_xbound[:, 0]] + \
                                             C_i[sym_elem_xbound[:, 3]]

        C_sym[i, indx_boun_y: indx_cntr_elm] = C_i[sym_elem_ybound[:, 0]] + \
                                               C_i[sym_elem_ybound[:, 1]]

        C_sym[i, -1] = C_i[mesh.CenterElts[0]]

    # influence on x boundary elements
    for i in range(len(boundary_x)):
        x = mesh.CenterCoor[boundary_x[i], 0] - mesh.CenterCoor[:, 0]
        y = mesh.CenterCoor[boundary_x[i], 1] - mesh.CenterCoor[:, 1]

        C_i = (Ep / (8. * np.pi)) * (np.sqrt(np.square(a - x) + np.square(b - y)) / ((a - x) * (b - y)) + np.sqrt(
            np.square(a + x) + np.square(b - y)) / ((a + x) * (b - y)) + np.sqrt(np.square(a - x) + np.square(b + y)
            ) / ((a - x) * (b + y)) + np.sqrt(np.square(a + x) + np.square(b + y)) / ((a + x) * (b + y)))

        C_sym[i + indx_boun_x, 0: indx_boun_x] = C_i[sym_elements[:, 0]] + \
                                                 C_i[sym_elements[:, 1]] + \
                                                 C_i[sym_elements[:, 2]] + \
                                                 C_i[sym_elements[:, 3]]

        C_sym[i + indx_boun_x, indx_boun_x: indx_boun_y] = C_i[sym_elem_xbound[:, 0]] + \
                                                           C_i[sym_elem_xbound[:, 3]]

        C_sym[i + indx_boun_x, indx_boun_y: indx_cntr_elm] = C_i[sym_elem_ybound[:, 0]] + \
                                                             C_i[sym_elem_ybound[:, 1]]

        C_sym[indx_boun_x + i, -1] = C_i[mesh.CenterElts[0]]

    # influence on y boundary elements
    for i in range(len(boundary_y)):
        x = mesh.CenterCoor[boundary_y[i], 0] - mesh.CenterCoor[:, 0]
        y = mesh.CenterCoor[boundary_y[i], 1] - mesh.CenterCoor[:, 1]

        C_i = (Ep / (8. * np.pi)) * (np.sqrt(np.square(a - x) + np.square(b - y)) / ((a - x) * (b - y)) + np.sqrt(
            np.square(a + x) + np.square(b - y)) / ((a + x) * (b - y)) + np.sqrt(np.square(a - x) + np.square(b + y)
            ) / ((a - x) * (b + y)) + np.sqrt(np.square(a + x) + np.square(b + y)) / ((a + x) * (b + y)))

        C_sym[i + indx_boun_y, 0: indx_boun_x] = C_i[sym_elements[:, 0]] + \
                                                 C_i[sym_elements[:, 1]] + \
                                                 C_i[sym_elements[:, 2]] + \
                                                 C_i[sym_elements[:, 3]]

        C_sym[i + indx_boun_y, indx_boun_x: indx_boun_y] = C_i[sym_elem_xbound[:, 0]] + \
                                                           C_i[sym_elem_xbound[:, 3]]

        C_sym[i + indx_boun_y, indx_boun_y: indx_cntr_elm] = C_i[sym_elem_ybound[:, 0]] + \
                                                             C_i[sym_elem_ybound[:, 1]]

        C_sym[indx_boun_y + i, -1] = C_i[mesh.CenterElts[0]]

    # influence on center element
    x = mesh.CenterCoor[mesh.CenterElts[0], 0] - mesh.CenterCoor[:, 0]
    y = mesh.CenterCoor[mesh.CenterElts[0], 1] - mesh.CenterCoor[:, 1]

    C_i = (Ep / (8. * np.pi)) * (np.sqrt(np.square(a - x) + np.square(b - y)) / ((a - x) * (b - y)) + np.sqrt(
        np.square(a + x) + np.square(b - y)) / ((a + x) * (b - y)) + np.sqrt(np.square(a - x) + np.square(b + y)
                                                                             ) / ((a - x) * (b + y)) + np.sqrt(
        np.square(a + x) + np.square(b + y)) / ((a + x) * (b + y)))

    C_sym[-1, 0: len(pos_qdrnt)] = C_i[sym_elements[:, 0]] + \
                                  C_i[sym_elements[:, 1]] + \
                                  C_i[sym_elements[:, 2]] + \
                                  C_i[sym_elements[:, 3]]

    C_sym[-1, indx_boun_x: indx_boun_y] = C_i[sym_elem_xbound[:, 0]] + \
                                          C_i[sym_elem_xbound[:, 3]]

    C_sym[-1, indx_boun_y: indx_cntr_elm] = C_i[sym_elem_ybound[:, 0]] + \
                                            C_i[sym_elem_ybound[:, 1]]

    C_sym[-1, -1] = C_i[mesh.CenterElts[0]]

    return C_sym


#-----------------------------------------------------------------------------------------------------------------------

def self_influence(mesh, Ep):
    a = mesh.hx / 2.
    b = mesh.hy / 2.
    return Ep / (2. * np.pi) * (a**2 + b**2)**0.5 / (a * b)