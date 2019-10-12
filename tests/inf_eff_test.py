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
#    Testing the influent/effluent classes.
#
#
# Change Log:
# 20191011 KZ: retested after flow_data_src implementation and passed
# 20190815 KZ: init and passed
#

from unit_procs.streams import pipe, influent, effluent
import utils.pfd
import utils.run
import pdb

if __name__ == '__main__':

    import INF_EFF

    wwtp = INF_EFF.construct()

    utils.pfd.check(wwtp)

    utils.pfd.show(wwtp)

    # identify units of different types
    _inf = utils.pfd.get_all_units(wwtp, 'Influent')

    _reactors = utils.pfd.get_all_units(wwtp, 'ASMReactor')

    _WAS = utils.pfd.get_all_units(wwtp, 'WAS')

    _splitters = utils.pfd.get_all_units(wwtp, 'Splitter')

    _srt_ctrl = [_u for _u in _splitters if _u.is_SRT_controller()]

    _final_clar = utils.pfd.get_all_units(wwtp, 'Final_Clarifier')

    _eff = utils.pfd.get_all_units(wwtp, 'Effluent')

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

    # start the main loop
    _WAS_flow = 0.0  # M3/d
    # there is no need to seed the system in this example

    utils.run.forward_set_flow(wwtp, _inf[0])
    utils.run.traverse_plant(wwtp, _inf[0])
    
    #pdb.set_trace()

    while True:

        utils.run.backward_set_flow(_eff)

        utils.run.traverse_plant(wwtp, _inf[0])

        _eff[0].set_mainstream_flow(_plant_inf_flow - _WAS_flow)

        if utils.run.check_global_cnvg(wwtp):
            break


    for elem in wwtp:
        print('{}: main out flow = {}, side out flow = {}, (m3/d)'.format(
            elem.__name__, elem.get_main_outflow(), elem.get_side_outflow()))
        print('     main outlet conc = {}'.format(
            elem.get_main_outlet_concs()))
        print('     side outlet conc = {}'.format(
            elem.get_side_outlet_concs()))

