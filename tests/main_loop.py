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
#    Testing the main loop of modular sequential approach.
#
#
# Change Log:
# 20190726 KZ: separate the units in a pfd into differenty type groups
# 20190724 KZ: init

#
from unit_procs.streams import splitter, pipe, influent, effluent, WAS
from unit_procs.bio import asm_reactor
from unit_procs.physchem import final_clarifier
import utils.pfd
import pdb

if __name__ == '__main__':

    import CMAS

    wwtp = CMAS.construct()
    utils.pfd.check_pfd(wwtp)
    utils.pfd.show_pfd(wwtp)
    CMAS.SRT = 5

    # identify units of different types
    _reactors = utils.pfd.get_all_units(wwtp, 'ASMReactor')
    _WAS = utils.pfd.get_all_units(wwtp, 'WAS')
    _splitters = utils.pfd.get_all_units(wwtp, 'Splitter')
    _srt_ctrl = [_u for _u in _splitters if _u.is_SRT_controller()]
    print('Reactors in the PFD: {}'.format([_u.__name__ for _u in _reactors]))
    print('WAS units in the PFD: {}'.format([_u.__name__ for _u in _WAS]))
    print('Splitters in the PFD: {}'.format(
        [_u.__name__ for _u in _splitters]))
    print('SRT Controlling Splitter in the PFD: {}'.format(
        [_u.__name__ for _u in _srt_ctrl]))

    

