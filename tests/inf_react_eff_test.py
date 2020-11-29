#   This file is part of PooPyLab.
#
#    PooPyLab is a simulation software for biological wastewater treatment
#    processes using the International Water Association Activated Sludge
#    Models.
#   
#    Copyright (C) Kai Zhang
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# --------------------------------------------------------------------
#    Testing the influent/effluent/pipe/reactor classes.
#
#
# Change Log:
# 20201129 KZ: re-run after package structure update
# 20200625 KZ: retested after updating the steadt state criteria
# 20191015 KZ: checked against ASIM results and passed.
# 20191014 KZ: re-test after flow data source tags implementation.
# 20190917 KZ: Matched ASIM results!!! - PASSED TEST!!
# 20190916 KZ: compared results against ASIM. ASIM has additional rate
#           adjustments including K_ALK and ammonia limitations. 
#           But the results are comparable!!
# 20190915 KZ: start to get reasonable integration results.
# 20190911 KZ: got the pfd to run with results. need to verify its validity
# 20190911 KZ: continued after rearraning ASM1 and integration function
# 20190815 KZ: init
#

from PooPyLab.unit_procs.streams import pipe, influent, effluent
from PooPyLab.unit_procs.bio import asm_reactor
from PooPyLab.utils import pfd, run
import pdb

if __name__ == '__main__':

    import INF_REACT_EFF

    wwtp = INF_REACT_EFF.construct()

    pfd.check(wwtp)

    pfd.show(wwtp)

    # identify units of different types
    _inf = pfd.get_all_units(wwtp, 'Influent')

    _reactors = pfd.get_all_units(wwtp, 'ASMReactor')

    _WAS = pfd.get_all_units(wwtp, 'WAS')

    _splitters = pfd.get_all_units(wwtp, 'Splitter')

    _srt_ctrl = [_u for _u in _splitters if _u.is_SRT_controller()]

    _final_clar = pfd.get_all_units(wwtp, 'Final_Clarifier')

    _eff = pfd.get_all_units(wwtp, 'Effluent')

    print('Influent in the PFD: {}'.format([_u.__name__ for _u in _inf]))

    _plant_inf_flow = sum([_u.get_main_outflow() for _u in _inf])
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

    for fc in _final_clar:
        fc.set_underflow_TSS(_uf_tss)

    # start the main loop
    _WAS_flow = 0.0  # M3/d

    _params = _reactors[0].get_model_params()
    print('Model parameters: {}'.format(_params))

    for _u in _inf:
        _u.update_combined_input()
        _u.discharge()

    # TODO: what if there are multiple influent units?
    _seed = run.initial_guess(_params, 
                                    _reactors,
                                    _inf[0].get_main_outflow(), 
                                    _inf[0].get_main_outlet_concs())

    print('Initial guess = {}'.format(_seed))

    for _r in _reactors:
        _r.assign_initial_guess(_seed)
    
    run.forward_set_flow(wwtp)
    run.traverse_plant(wwtp, _inf[0])

    i = 1
    while True:
        #_WAS[0].set_mainstream_flow(_WAS_flow)
        _eff[0].set_mainstream_flow(_plant_inf_flow - _WAS_flow)

        run.backward_set_flow(_eff)

        run.traverse_plant(wwtp, _inf[0])

        if run.check_global_cnvg(wwtp):
            break
        
        i += 1


    for elem in wwtp:
        print('{}: main out flow = {}, side out flow = {}, (m3/d)'.format(
            elem.__name__, elem.get_main_outflow(), elem.get_side_outflow()))
        print('     main out PREV conc = {}'.format(elem._prev_mo_comps))
        print('     side out PREV conc = {}'.format(elem._prev_so_comps))
        print('     main outlet conc = {}'.format(
            elem.get_main_outlet_concs()))
        print('     side outlet conc = {}'.format(
            elem.get_side_outlet_concs()))

    print("TOTAL ITERATION = ", i)

    print(_reactors[0].get_active_vol())
    print(_reactors[0].get_model_params())
    print(_reactors[0].get_model_stoichs())
