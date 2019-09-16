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
# 20190911 KZ: eliminated divided_by_zero errors by assigning init_X_S
# 20190903 KZ: corrected b_H & b_A in initial_guess()
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


def initial_guess(params={}, reactors=[], inf_flow=1.0, plant_inf=[]):
    '''
    Generate the initial guess to be used for the starting point of model
    integration towards a steady state solution.

    The approach here is similar to that outlined in the IWA ASM1 report, where
    the total volume of all the reactors is treated as one CSTR.
    '''
    # params: model parameters adjusted to the project temperature
    # reactors: asm_reactors whose volume will be used
    # inf_flow: wwtp's influent flow rate, m3/d
    # plant_inf: model components for the entire wwtp's influent
    
    inf_S_S = plant_inf[2]
    inf_S_NH = plant_inf[3]
    inf_X_S = plant_inf[8]
    inf_TKN = inf_S_NH + plant_inf[4] + plant_inf[12]
    # assume outlet bsCOD
    eff_S_S = 100.0  # mg/L

    # assume full nitrification (if inf TKN is sufficient)
    eff_S_NH = 1.0  # mgN/L

    #Safety Factor
    SF = 1.25

    # OXIC SRT required for eff_S_S, assuming DO is sufficiently high
    SRT_OXIC_H = 1.0 \
            / (params['u_max_H'] * eff_S_S / (eff_S_S + params['K_S'])
                    - params['b_LH'])

    # Oxic SRT required for eff_S_NH, assuming DO is sufficiently high
    SRT_OXIC_A = 1.0 \
            / (params['u_max_A'] * eff_S_NH / (eff_S_NH + params['K_NH'])
                    - params['b_LA'])

    SRT_OXIC = max(SRT_OXIC_A, SRT_OXIC_H) * SF

    print('Min Oxic SRT for Heterotrophs = {} (day)'.format(SRT_OXIC_H))
    print('Min Oxic SRT for Autotrophs = {} (day)'.format(SRT_OXIC_A))
    print('SELECTED Oxic SRT = {} (day)'.format(SRT_OXIC))

    # Initial guesses of S_S and S_NH based on the selected oxic SRT
    init_S_S = params['K_S'] * (1.0 / SRT_OXIC + params['b_LH']) \
            / (params['u_max_H'] - (1.0 / SRT_OXIC + params['b_LH']))

    init_S_NH = params['K_NH'] * (1.0 / SRT_OXIC + params['b_LA']) \
            / (params['u_max_A'] - (1.0 / SRT_OXIC + params['b_LA']))

    print('eff. S_S = {} (mg/L COD)'.format(init_S_S))
    print('eff. S_NH = {} (mg/L COD)'.format(init_S_NH))

    # daily active heterotrphic biomass production, unit: gCOD/day
    daily_heter_biomass_prod = inf_flow  * (inf_S_S + inf_X_S - init_S_S)\
            * params['Y_H'] / (1.0 + params['b_LH'] * SRT_OXIC)

    # Nitrogen Requried for assimilation
    NR = 0.087 * params['Y_H'] \
            * (1.0 + params['f_D'] * params['b_LH'] * SRT_OXIC) \
            / (1.0 + params['b_LH'] * SRT_OXIC)
    
    init_S_NO = (inf_TKN - NR * (inf_S_S + inf_X_S - init_S_S) - init_S_NH)

    # daily active autotrophic biomass production, unit: gCOD/day
    daily_auto_biomass_prod = inf_flow \
            * init_S_NO \
            * params['Y_A'] / (1.0 + params['b_LA'] * SRT_OXIC)

    # daily heterotrphic debris production, unit: gCOD/day
    daily_heter_debris_prod = daily_heter_biomass_prod \
            * (params['f_D'] * params['b_LH'] * SRT_OXIC)

    # daily autotrophic debris production, unit: gCOD/day
    daily_auto_debris_prod = daily_auto_biomass_prod \
            * (params['f_D'] * params['b_LA'] * SRT_OXIC)

    
    # treat the entire plant's reactor active vol as a single CSTR
    _hyp_cstr_vol = _wwtp_active_vol(reactors)

    # initial guesses of X_BH, X_BA, and X_D
    init_X_BH = SRT_OXIC * daily_heter_biomass_prod / _hyp_cstr_vol
    init_X_BA = SRT_OXIC * daily_auto_biomass_prod / _hyp_cstr_vol
    init_X_D = SRT_OXIC \
            * (daily_heter_debris_prod + daily_auto_debris_prod) \
            / _hyp_cstr_vol

    # TODO: ALWAYS make sure the indecies are correct as per the model
    init_S_DO = 2.0  # assume full aerobic for the hypothetical CSTR
    init_S_I = plant_inf[1]
    # init_S_S above
    # init_S_NH above
    init_S_NS = inf_TKN * 0.01  # TODO: assume 1% influent TKN as sol.org.N
    # init_S_NO above
    init_S_ALK = plant_inf[6] - 7.14 * (init_S_NO - plant_inf[5]) / 50.0
    init_X_I = plant_inf[7]
    init_X_S = 0.1 * inf_X_S  # assumed 10% remain
    # init_X_BH above
    # init_X_BA above
    # init_X_D above
    init_X_NS = params['i_N_XB'] * (init_X_BH + init_X_BA)\
                + params['i_N_XD'] * init_X_D

    return [init_S_DO, init_S_I, init_S_S, init_S_NH, init_S_NS, init_S_NO,
            init_S_ALK,
            init_X_I, init_X_S, init_X_BH, init_X_BA, init_X_D, init_X_NS]
#    return [2.0, init_S_I, 1.0, 1.0, 1.0, 1.0, 5, init_X_I, 1.0, 500, 20, 1.0,
#            1.0]
