# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
#    
#    Copyright (C) Kai Zhang
#
#    PooPyLab is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PooPyLab is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PooPyLab.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Definition of global utility functions related to the initial guess
#    for the integration of the model's equation system.
#
#    Author: Kai Zhang
#
# CHANGE LOG:
# 20190828 KZ: init
#


from unit_procs.streams import pipe, influent, effluent, WAS, splitter
from unit_procs.bio import asm_reactor
from unit_procs.physchem import final_clarifier


def _wwtp_active_vol(reactors=[]):
    ''' 
    get the sum of asm reactors' active volume.
    '''
    return sum([r.get_active_vol() for r in reactors])


def initial_guess(params={}, reactors=[], Inf_Flow=1.0, plant_inf=[]):
    '''
    Generate the initial guess to be used for the starting point of model
    integration towards a steady state solution.

    The approach here is similar to that outlined in the IWA ASM1 report, where
    the total volume of all the reactors is treated as one CSTR.
    '''
    # params: dict of model parameters adjusted to the project temperature
    # reactors: list of asm_reactors whose volume will be used
    # Inf_Flow: wwtp's influent flow rate, m3/d
    # plant_inf: model components for the entire wwtp's influent
    
    # assume outlet bsCOD
    Eff_S_S = 100.0  # mg/L

    # assume full nitrification (if inf TKN is sufficient)
    Eff_S_NH = 1.0  # mgN/L

    #Safety Factor
    SF = 1.25

    # convert b_LH and b_LA to b_H and b_A, respectively
    b_H = params['b_LH'] * (1.0 - params['Y_H'] * (1.0 - params['f_D_']))
    b_A = params['b_LA'] * (1.0 - params['Y_A'] * (1.0 - params['f_D_']))

    # OXIC SRT required for Eff_S_S, assuming DO is sufficiently high
    SRT_OXIC_H = 1.0 \
            / (params['u_H'] * Eff_S_S / (Eff_S_S + params['K_S']) - b_H)

    # Oxic SRT required for Eff_S_NH, assuming DO is sufficiently high
    SRT_OXIC_A = 1.0 \
            / (params['u_A'] * Eff_S_NH / (Eff_S_NH + params['K_NH']) - b_A)

    SRT_OXIC = max(SRT_OXIC_A, SRT_OXIC_H) * SF

    print('Min Oxic SRT for Heterotrophs = {} (day)', SRT_OXIC_H)
    print('Min Oxic SRT for Autotrophs = {} (day)', SRT_OXIC_A)
    print('SELECTED Oxic SRT = {} (day)', SRT_OXIC)

    # Initial guesses of S_S and S_NH based on the selected oxic SRT
    init_S_S = params['K_S'] * (1.0 / SRT_OXIC + b_H) \
            / (params['u_H'] - (1.0 / SRT_OXIC + b_H))

    init_S_NH = params['K_NH'] * (1.0 / SRT_OXIC + b_A) \
            / (params['u_A'] - (1.0 / SRT_OXIC + b_A))

    print('Eff. S_S = {} (mg/L COD)', init_Eff_S_S)
    print('Eff. S_NH = {} (mg/L COD)', init_Eff_S_NH)

    # daily active heterotrphic biomass production, unit: gCOD/day
    daily_heter_biomass_prod = Inf_Flow  * (Inf_S_S + Inf_X_S - init_S_S)\
            * params['Y_H'] / (1.0 + b_H * SRT_OXIC)

    # Nitrogen Requried for assimilation
    NR = 0.087 * params['Y_H'] \
            * (1.0 + params['f_D_'] * params['b_LH'] * SRT_OXIC) \
            / (1.0 + b_H * SRT_OXIC)
    
    init_S_NO = (Inf_TKN - NR * (Inf_S_S + Inf_X_S - init_S_S) - init_S_NH)

    # daily active autotrophic biomass production, unit: gCOD/day
    daily_auto_biomass_prod = Inf_Flow \
            * init_S_NO \
            * params['Y_A'] / (1.0 + b_A * SRT_OXIC)

    # daily heterotrphic debris production, unit: gCOD/day
    daily_heter_debris_prod = daily_heter_biomass_prod \
            * (params['f_D_'] * params['b_LH'] * SRT_OXIC)

    # daily autotrophic debris production, unit: gCOD/day
    daily_auto_debris_prod = daily_auto_biomass_prod \
            * (params['f_D_'] * params['b_LA'] * SRT_OXIC)

    
    # treat the entire plant's reactor active vol as a single CSTR
    _hyp_cstr_vol = _wwtp_active_vol(reactors)

    # initial guesses of X_BH, X_BA, and X_D
    init_X_BH = SRT_OXIC * daily_heter_biomass_prod / _hyp_cstr_vol
    init_X_BA = SRT_OXIC * daily_auto_biomass_prod / _hyp_cstr_vol
    init_X_D = SRT_OXIC \
            * (daily_heter_debris_prod + daily_auto_debris_prod) \
            / _hyp_cstr_vol

    # TODO: ALWAYS make sure the indeces are correct as per the model
    init_X_I = plant_inf[0]
    init_X_S = 0.0  
    # init_X_BH above
    # init_X_BA above
    # init_X_D above
    init_S_I = plant_inf[5]
    # init_S_S above
    init_S_DO = 2.0  # assume full aerobic for the hypothetical CSTR
    # init_S_NO above
    # init_S_NH above
    init_S_NS = Inf_TKN * 0.01  # TODO: assume 1% influent TKN as sol.org.N
    init_X_NS = 0.087 * (init_X_BH + init_X_BA + init_X_D)
    init_S_Alk = plant_inf[12] - 7.14 * (init_S_NO - plant_inf[8]) / 50.0

    return [init_X_I, init_X_S, init_X_BH, init_X_BA, init_X_D, 
            init_S_I, init_S_S, init_S_DO, init_S_NO, init_S_NH,
            init_S_NS, init_X_NS, init_S_Alk]




