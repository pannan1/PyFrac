# -*- coding: utf-8 -*-
"""
This file is part of PyFrac.

Created by Haseeb Zia on 03.04.17.
Copyright (c) ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, Geo-Energy Laboratory, 2016-2020.
All rights reserved. See the LICENSE.TXT file for more details.
"""

# external imports
import numpy as np


def turbulence_check_tip(vel, Fr, fluid, return_ReyNumb=False):
    """
    This function calculate the Reynolds number at the cell edges and check if any to the edge between the ribbon cells
    and the tip cells are turbulent (i.e. the Reynolds number is greater than 2100).

    Arguments:
        vel (ndarray-float):            -- the array giving velocity of each edge of the cells in domain
        Fr (Fracture object):           -- the fracture object to be checked
        fluid (FluidProperties):        -- fluid properties object
        return_ReyNumb (boolean):       -- if True, Reynolds number at all cell edges will also be returned

    Returns:
        - Re (ndarray)     -- Reynolds number of all the cells in the domain; row-wise in the following order, 0--left,\
                              1--right, 2--bottom, 3--top.
        - boolean          -- True if any of the edge between the ribbon and tip cells is turbulent (i.e. Reynolds \
                               number is more than 2100).
    """

    # width at the adges by averaging
    w_ribbon = Fr.w[Fr.EltRibbon]
    wLftEdge = (w_ribbon + Fr.w[Fr.mesh.NeiElements[Fr.EltRibbon, 0]]) / 2
    wRgtEdge = (w_ribbon + Fr.w[Fr.mesh.NeiElements[Fr.EltRibbon, 1]]) / 2
    wBtmEdge = (w_ribbon + Fr.w[Fr.mesh.NeiElements[Fr.EltRibbon, 2]]) / 2
    wTopEdge = (w_ribbon + Fr.w[Fr.mesh.NeiElements[Fr.EltRibbon, 3]]) / 2

    Re = np.zeros((4, Fr.EltRibbon.size,), dtype=np.float64)
    const = 4. / 3. * fluid.density / fluid.viscosity
    Re[0, :] = const * wLftEdge * vel[0, Fr.EltRibbon]
    Re[1, :] = const * wRgtEdge * vel[1, Fr.EltRibbon]
    Re[2, :] = const * wBtmEdge * vel[2, Fr.EltRibbon]
    Re[3, :] = const * wTopEdge * vel[3, Fr.EltRibbon]

    ReNum_Ribbon = []
    # adding Reynolds number of the edges between the ribbon and tip cells to a list
    for i in range(0, Fr.EltRibbon.size):
        for j in range(0, 4):
            # if the current neighbor (j) of the ribbon cells is in the tip elements list
            if np.where(Fr.mesh.NeiElements[Fr.EltRibbon[i], j] == Fr.EltTip)[0].size > 0:
                ReNum_Ribbon = np.append(ReNum_Ribbon, Re[j, i])

    if return_ReyNumb:
        wLftEdge = (Fr.w[Fr.EltCrack] + Fr.w[Fr.mesh.NeiElements[Fr.EltCrack, 0]]) / 2.
        wRgtEdge = (Fr.w[Fr.EltCrack] + Fr.w[Fr.mesh.NeiElements[Fr.EltCrack, 1]]) / 2.
        wBtmEdge = (Fr.w[Fr.EltCrack] + Fr.w[Fr.mesh.NeiElements[Fr.EltCrack, 2]]) / 2.
        wTopEdge = (Fr.w[Fr.EltCrack] + Fr.w[Fr.mesh.NeiElements[Fr.EltCrack, 3]]) / 2.

        Re = np.zeros((4, Fr.mesh.NumberOfElts,), dtype=np.float64)
        Re[0, Fr.EltCrack] = const * wLftEdge * vel[0, Fr.EltCrack]
        Re[1, Fr.EltCrack] = const * wRgtEdge * vel[1, Fr.EltCrack]
        Re[2, Fr.EltCrack] = const * wBtmEdge * vel[2, Fr.EltCrack]
        Re[3, Fr.EltCrack] = const * wTopEdge * vel[3, Fr.EltCrack]

        return Re, (ReNum_Ribbon > 2100.).any()
    else:
        return (ReNum_Ribbon > 2100.).any()

#-----------------------------------------------------------------------------------------------------------------------