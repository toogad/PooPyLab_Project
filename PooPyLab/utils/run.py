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
#

"""Global functions for running simulations.
"""
## @namespace run
## @file run.py

from ..unit_procs.streams import pipe, influent, effluent, WAS, splitter
from ..unit_procs.bio import asm_reactor
from ..unit_procs.physchem import final_clarifier
from ..utils.datatypes import flow_data_src
from ..utils import pfd

import pdb, cProfile

def check_global_cnvg(wwtp):
    """
    Check global convergence of the WWTP PFD.

    Args:
        wwtp:   list of process units in a WWTP's PFD

    Return:
        bool
    """

    for unit in wwtp:
        if not unit.is_converged():
            #print(unit.__name__, 'not converged yet')
            return False
    return True


def show_concs(wwtp):
    """
    Print the concentrations of the branches of each unit in the WWTP's PFD.

    Args:
        wwtp:   list of process units in a WWTP's PFD

    Return:
        None
    """

    for elem in wwtp:
        print('{}: main out flow = {}, side out flow = {}, (m3/d)'.format(
            elem.__name__, elem.get_main_outflow(), elem.get_side_outflow()))
        print('     main outlet conc = {}'.format(
            elem.get_main_outlet_concs()))
        if elem.has_sidestream():
            print('     side outlet conc = {}'.format(
            elem.get_side_outlet_concs()))

    return None


def _wwtp_active_vol(reactors=[]):
    """
    Return the sum of asm reactors' active volume.

    Args:
        reactors:   list of reactors whose active volumes are of interest.

    Return:
        total active volume (float), m3
    """
    return sum([r.get_active_vol() for r in reactors])


def initial_guess(params={}, reactors=[], inf_flow=1.0, plant_inf=[]):
    """
    Return the initial guess as the start of integration towards steady state.

    The approach here is similar to that outlined in the IWA ASM1 report, where
    the total volume of all the reactors is treated as one CSTR.

    Args:
        params:     model parameters adjusted to the project temperature;
        reactors:   reactors whose volume will be used;
        inf_flow:   wwtp's influent flow rate, m3/d;
        plant_inf:  model components for the entire wwtp's influent.

    Return:
        list of ASM 1 component concentrations [float]    
    """
    
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
    print('eff. S_NH = {} (mg/L N)'.format(init_S_NH))

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

    
    # treat the entire plant's reactor vol. as a single hypothetical CSTR
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


def _forward(me, visited=[]):
    """
    Set the flow data source by visiting process units along the flow paths.

    This function is to be called by forward_set_flow(). It follows the flow
    paths and decide whether additional flow data sources can be decided based
    on what's known.

    Args:
        me:         current process unit under analysis;
        visisted:   list of process units visited already.

    Return:
        None

    See:
        forward_set_flow().
    """
    if me in visited or me == None:
        return None
    
    visited.append(me)

    _in = me.get_upstream()
    _mo = me.get_downstream_main()
    _so = me.get_downstream_side()

    _in_f_ds, _mo_f_ds, _so_f_ds = me.get_flow_data_src()

    _in_f_known = (_in_f_ds != flow_data_src.TBD)

    _mo_f_known = (_mo_f_ds != flow_data_src.TBD)

    _so_f_known = (_so_f_ds != flow_data_src.TBD)

    if _in_f_known:
        if _so == None:
            if not _mo_f_known:
                me.set_flow_data_src('Main', flow_data_src.UPS)
                _forward(_mo, visited)
            #else:
                #pass
        else:
            if not _mo_f_known:
                if _so_f_known:
                    me.set_flow_data_src('Main', flow_data_src.UPS)
                #else:
                    #pass
            else:
                if _so_f_known:
                    # both _mo_f_known and _so_f_known
                    return None
                else:
                    me.set_flow_data_src('Side', flow_data_src.UPS)
                    _forward(_so, visited)
    else:
        # _in_flow_data_src == TBD, can it be determined?
        _me_in_f_ds_known = True
        for _f in _in:
            _f_in_f_ds, _f_mo_f_ds, _f_so_f_ds = _f.get_flow_data_src()
            if _f.get_downstream_main() == me:
                if _f_mo_f_ds == flow_data_src.TBD:
                    _me_in_f_ds_known = False
                    break
            else:
                if _f_so_f_ds == flow_data_src.TBD:
                    _me_in_f_ds_known = False
                    break
        if _me_in_f_ds_known:
            me.set_flow_data_src('Inlet', flow_data_src.UPS)
            _forward(me, visited)
    return None


def forward_set_flow(wwtp):
    """
    Set the _upstream_set_mo_flow flag of those influenced by the starters.

    Args:
        wwtp:   list of all units in a wwtp.

    Return:
        None

    See:
        _forward().
        backward_set_flow();
        _backward();
        _sum_of_known_inflows().
    """

    _visited = []
    _starters = []

    # find potential starters
    for _u in wwtp:
        _in_fds, _mo_fds, _so_fds = _u.get_flow_data_src()
        
        _in_f_known = (_in_fds == flow_data_src.UPS 
                        or _in_fds == flow_data_src.PRG)

        _mo_f_known = (_mo_fds == flow_data_src.UPS
                        or _mo_fds == flow_data_src.PRG)

        _so_f_known = (_so_fds == flow_data_src.UPS
                        or _so_fds == flow_data_src.PRG)

        if (_in_f_known or _mo_f_known or _so_f_known):
            _starters.append(_u)

    for _s in _starters:
        _forward(_s, _visited)
    
    return None



def _BFS(_to_visit, _visited):
    """
    Breadth First Search type of traverse.

    Args:
        _to_visit:      list of process units to be visited;
        _visited:       list of process units visited.

    Return:
        list of process units in their visited order.
    """

    if len(_to_visit) == 0:
        return [_u.__name__ for _u in _visited]

    _next = _to_visit.pop(0)

    if _next not in _visited:
        _visited.append(_next)
        _next.update_combined_input()
        _next.discharge()
        if _next.has_sidestream():
            _next_s = _next.get_downstream_side()
            if _next_s not in _visited:
                _to_visit.append(_next_s)
        _next_m = _next.get_downstream_main()
        if _next_m not in _visited and _next_m != None:
            _to_visit.append(_next_m)
        return _BFS(_to_visit, _visited)
    else:
        return [_u.__name__ for _u in _visited]


def traverse_plant(wwtp, plant_inf):
    """
    Visit every process units on the PFD starting from the influent.

    Args:
        wwtp:       list of all process units on the WWTP's PFD;
        plant_inf:  plant influent unit.

    Return:
        None

    See:
        _BFS();
    """

    _to_visit = [plant_inf]
    _visited = []
    _finished = []

    while len(_visited) < len(wwtp):
        _finished = _BFS(_to_visit, _visited)
    #print("visited:", _finished)

    return None


def _sum_of_known_inflows(me, my_inlet_of_unknown_flow):
    """
    Return the sum of all known flow rates of the inlet of a process unit.

    Args:
        me:                         current process unit;
        my_inlet_of_unknown_flow:   discharger w/ flow into "me" unknown.

    Return:
        float, m3/d
    """

    _sum = 0.0
    for _inlet in me.get_upstream():
        if _inlet != my_inlet_of_unknown_flow:
            if _inlet.get_downstream_main() == me:
                _sum += _inlet.get_main_outflow()
            else:
                _sum += _inlet.get_side_outflow()
    return _sum

     
def _backward(me):
    """
    Set the flow data source by visiting process units against the flow paths.

    This function is to be called by backward_set_flow(). It decide whether
    additional flow data sources can be decided based on (_mo_flow + _so_flow).
    If so, proceed and set the inflow and trace further upstream of "me".

    Args:
        me:         current process unit under analysis;
        visisted:   list of process units visited already.

    Return:
        None

    See:
        backward_set_flow();
        forward_set_flow();
        _forward().
    """

    _in_f_ds, _mo_f_ds, _so_f_ds = me.get_flow_data_src()

    _in_f_known = (_in_f_ds != flow_data_src.TBD)

    _mo_f_known = (_mo_f_ds != flow_data_src.TBD)

    _so_f_known = (_so_f_ds != flow_data_src.TBD)

    if _so_f_known:
        if _mo_f_known:
            if _in_f_known:
                if _in_f_ds == flow_data_src.UPS:
                    return None
            else:
                me.set_flow_data_src('Inlet', flow_data_src.DNS)
        else:
            if _in_f_known:
                me.set_flow_data_src('Main', flow_data_src.UPS)
                me._upstream_set_mo_flow = True
            else:
                return None
    else:
        if _mo_f_known:
            if _in_f_known:
                me.set_flow_data_src('Side', flow_data_src.UPS)
            else:
                return None
        else:
            return None
     
    _my_inlet = me.get_upstream()
    _my_inlet_allow = []
    if _my_inlet != None:
        _my_inlet_allow = [u for u in _my_inlet 
                if ((u.get_flow_data_src()[1] == flow_data_src.TBD
                    or u.get_flow_data_src()[1] == flow_data_src.DNS)
                    and u.get_downstream_main() == me) 
                    or
                    ((u.get_flow_data_src()[2] == flow_data_src.TBD
                    or u.get_flow_data_src()[2] == flow_data_src.DNS)
                    and u.get_downstream_side() == me)]
    
    _freedom = len(_my_inlet_allow)
    if _freedom == 0:  # all inlets have been set with flow source
        return None
    elif _freedom > 1:  # too many units for setting flows
        print('ERROR:{} has {} upstream units' 
                'with undefined flows.'.format(me.__name__, _freedom))
    else:
        _target = _my_inlet_allow[0]
        _known_sum = _sum_of_known_inflows(me, _target)
        _residual = me.totalize_inflow() - _known_sum

        if _target.get_downstream_main() == me:
            #_target.set_mainstream_flow_by_upstream(False)
            _target.set_flow_data_src('Main', flow_data_src.DNS)
            _target.set_mainstream_flow(_residual)
        else:
            _target.set_flow_data_src('Side', flow_data_src.DNS)
            _target.set_sidestream_flow(_residual)

        if _target.get_flow_data_src()[0] == flow_data_src.DNS:
            _backward(_target)

    return None


def backward_set_flow(start=[]):
    """
    Back tracing to set the flows of the inlet units for those in starters.

    Args:
        start: list of units whose inflow = mainstream flow + sidestream flow.

    Return:
        None

    See:
        _backward();
        forward_set_flow();
        _forward();
        _sum_of_known_inflows().
    """
    for _u in start:
        _backward(_u)
    
    return None


def get_steady_state(wwtp=[], target_SRT=5, verbose=False, diagnose=False):
    """
    Integrate the entire plant towards a steady state at the target SRT.

    Constant influent flows and loads are required. If the user only knows the
    dynamic influent characteristics, the averages should be used as the
    influent conditions.

    Args:
        wwtp:       all process units in a wastewater treatment plant
        target_SRT: target solids retention time (d) for the steady state
        verbose:    flag for more detailed output
        diagnose:   flag for the use of cProfile for performance analysis

    Return:
        None

    See:
        utils.pdf;
        forward_set_flow();
        backward_set_flow();
        traverse_plant()
    """

    # identify units of different types
    _inf = pfd.get_all_units(wwtp, 'Influent')
    _reactors = pfd.get_all_units(wwtp, 'ASMReactor')

    # TODO: _WAS may be an empty []
    _WAS = pfd.get_all_units(wwtp, 'WAS')

    _splitters = pfd.get_all_units(wwtp, 'Splitter')
    _srt_ctrl = [_u for _u in _splitters if _u.is_SRT_controller()]
    _final_clar = pfd.get_all_units(wwtp, 'Final_Clarifier')
    _eff = pfd.get_all_units(wwtp, 'Effluent')
    _plant_inf_flow = sum([_u.get_main_outflow() for _u in _inf])

    if verbose:
        print('Influent in the PFD: {}'.format([_u.__name__ for _u in _inf]))
        print(' Total influent flow into plant:', _plant_inf_flow)
        print('Reactors in the PFD: {}'.format([_u.__name__ for _u in _reactors]))
        print('WAS units in the PFD: {}'.format([_u.__name__ for _u in _WAS]))
        print('Splitters in the PFD: {}'.format(
            [_u.__name__ for _u in _splitters]))
        print('SRT Controlling Splitter in the PFD: {}'.format(
            [_u.__name__ for _u in _srt_ctrl]))
        print('Final Clarifier in the PFD: {}'.format(
            [_u.__name__ for _u in _final_clar]))
        print('Effluent in the PFD: {}'.format([_u.__name__ for _u in _eff]))
        print()
        for i in range(len(_reactors)):
            print(_reactors[i].get_active_vol())
            print(_reactors[i].get_model_params())
            print(_reactors[i].get_model_stoichs())


    # start the main loop
    _WAS_flow = 0.0  # M3/d
    _SRT = target_SRT

    # get the influent ready
    for _u in _inf:
        _u.update_combined_input()
        _u.discharge()

    # TODO: what if there are multiple influent units?
    _params = _reactors[0].get_model_params()
    _seed = initial_guess(_params, 
                            _reactors,
                            _inf[0].get_main_outflow(), 
                            _inf[0].get_main_outlet_concs())
    
    print('Initial guess = {}'.format(_seed))

    for _r in wwtp:
        _r.assign_initial_guess(_seed)

    for fc in _final_clar:
        fc.set_capture_rate(0.992)

    forward_set_flow(wwtp)

    # collect all the possible starting points for backward flow setting
    _backward_start_points = [_w for _w in _WAS] + [_e for _e in _eff]
    
    if len(_WAS) == 0:
        _WAS_flow = 0
    else:
        _WAS_flow = _WAS[0].set_WAS_flow(_SRT, _reactors, _eff)
        _WAS[0].set_mainstream_flow(_WAS_flow)
    _eff[0].set_mainstream_flow(_plant_inf_flow - _WAS_flow)
    backward_set_flow(_backward_start_points)
    traverse_plant(wwtp, _inf[0])
    
    if diagnose:
        profile = cProfile.Profile()
        profile.enable()

    r = 1
    while True:
        if len(_WAS) == 0:
            _WAS_flow = 0
        else:
            _WAS_flow = _WAS[0].set_WAS_flow(_SRT, _reactors, _eff)
            _WAS[0].set_mainstream_flow(_WAS_flow)
        _eff[0].set_mainstream_flow(_plant_inf_flow - _WAS_flow)
        backward_set_flow(_backward_start_points)
        traverse_plant(wwtp, _inf[0])

        if check_global_cnvg(wwtp):
            break
        r += 1

    if diagnose:
        profile.disable()

    show_concs(wwtp)

    if verbose:
        print("TOTAL ITERATION = ", r)

    if diagnose:
        profile.print_stats()
