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
#    Definition of global utility functions related to the process flow
#    diagram (PFD).
#
#    Author: Kai Zhang
#
# Change Log: 
#   2019-07-26 KZ: added get_all_units() to group specific types of units
#   2019-07-16 KZ: replaced all isinstance() with get_type() wherever we can
#   2019-03-17 KZ: revised _check_WAS()
#   2019-03-17 KZ: revised _check_sidestream_flows(); _find_main_only_prefix()
#   2019-03-03 KZ: added PFD checking fucntions
#   2019-02-12 KZ: init
#


from unit_procs.streams import influent, effluent, WAS, pipe, splitter
from unit_procs.bio import asm_reactor
from unit_procs.physchem import final_clarifier


def _check_connection(pfd=[]):
    loose_end = 0
    for unit in pfd:
        if not unit.has_discharger():
            print(unit.__name__, 'upstream is not connected')
            loose_end += 1
        if unit.has_sidestream():
            if not unit.side_outlet_connected():
                print(unit.__name__, 'sidestream is not connected')
                loose_end += 1
        elif not unit.main_outlet_connected():
            print(unit.__name__,'main downstream is not connected')
            loose_end +=1 
    if loose_end == 0:
        print('The units on the PFD are all connected.')
    else:
        print(loose_end, 'connecton(s) to be fixed.')
    return loose_end


def _id_upstream_type(me, upds):
    # identify the type of an upstream discharger (upds) of (me)
    # me: a process unit
    # upds: an upstream discharger of 'me'

    if me.get_type() == 'Influent':
        return 'VOID'
    elif upds.get_type() == 'Influent':
        return 'INFLUENT'
    elif isinstance(upds, splitter):  # splitter & all its derived types
        if me == upds.get_downstream_main():
            return 'SPLITTER_MAIN'
        else:
            return 'SPLITTER_SIDE'
    elif isinstance(upds, pipe):  # pipe & its derived types
        return 'PIPE'
    
 
def _check_WAS(mywas):
    # Check the validity of the WAS units in the pfd. 
    #   1) All WAS units shall be connected to side streams of splitters via
    #   ONE pipe;
    #   2) There can only be 0 or 1 SRT controlling WAS (via its upstream
    #   splitter side);
    # Satisfying the above requirements will allow the SRT controlling splitter
    # to be moved to the front of the pfd.


    # SRT Controlling splitter to be found:
    _srt_ctrl_splt = None  
    _was_connect_ok = True
    _srt_ctrl_count = 0

    for _u in mywas:
        for _upds in _u.get_upstream():
            if _upds.get_type() == 'Pipe':
                if len(_upds.get_upstream()) == 1:
                    _xu = [q for q in _upds.get_upstream()][0]
                    if _id_upstream_type(_upds, _xu) != 'SPLITTER_SIDE':
                        print('CONNECTION ERROR:', _u.__name__, 
                                'shall be [SIDESTREAM->PIPE->WAS].')
                        _was_connect_ok = False
                        break
                    if _xu.is_SRT_controller():
                        _srt_ctrl_splt = _xu
                        _srt_ctrl_count += 1

    if _srt_ctrl_count > 1:
        print('PFD ERROR: More than ONE SRT controlling splitters.')
        _was_connect_ok = False
    elif _srt_ctrl_count == 0:
        print('PFD ERROR: No SRT controlling splitter was specified.')
        _was_connect_ok = False

    return _was_connect_ok, _srt_ctrl_splt


def _check_sidestream_flows(mysplitters):
    # Check the validity of the sidestreams of all splitter types
    # All side stream flows shall be defined by user except for the
    # SRT_Controller's or the final_clarifier's.
    # The sidestream flow of a final clarifier is determined during runtime.
    # The main loop shall update its side outlet or main outlet flows.

    _undefined = 0
    for _u in mysplitters:
        if not _u.sidestream_flow_defined():
            _undefined += 1
            print('PFD ERROR: Sidestream flow undefined:', _u.__name__)

    return _undefined == 0
            

def _find_main_only_prefix(cur, pms):
    if cur in pms:
        # found a mainstream-only loop
        return True

    if cur == None or cur.get_type() == 'Effluent'  or cur.get_type() == 'WAS':
        # current ms_prefix leads to dead end
        if len(pms) > 0:
            pms.pop()
        return False

    pms.append(cur)

    if _find_main_only_prefix(cur.get_downstream_main(), pms):
        return True
    elif len(pms) > 0:
        pms.pop()
        return False
    else:
        return False


def _has_main_only_loops(pfd):
    # Loops with mainstreams only are not allowed in the PFD

    for _u in pfd:
        prefix_ms = []         
        if _find_main_only_prefix(_u, prefix_ms):
            print('PFD ERROR: Found a mainstream-only loop.')
            print(' Loop={}'.format([x.__name__ for x in prefix_ms]))
            return True
        else:
            return False


def get_all_units(wwtp, type='ASMReactor'):
    return [w for w in wwtp if w.get_type() == type]


def check(wwtp):

    _all_WAS = get_all_units(wwtp, 'WAS')

    _all_splitters = get_all_units(wwtp, 'Splitter')

    _le = _check_connection(wwtp)
    _WAS_ok, _srt_ctrl_ = _check_WAS(_all_WAS)
    _side_flow_defined = _check_sidestream_flows(_all_splitters)
    _has_ms_loops = _has_main_only_loops(wwtp)

    if  _le == 0 and _WAS_ok and _side_flow_defined and _has_ms_loops == False:
        print('Found one SRT controller splitter; Moved to the back of PFD')
        wwtp.remove(_srt_ctrl_)
        wwtp.append(_srt_ctrl_)
        print('PFD READY')
    else:
        print('FIXED PFD ERRORS BEFORE PROCEEDING')

    return None


def show(wwtp=[]):
    print('Current PFD Configuration:')
    for unit in wwtp:
        print(unit.__name__, ': receives from:', end=' ')
        if unit.get_type() == 'Influent':
            print("None")
        else:
            upstr = unit.get_upstream()
            for dschgr in upstr:
                print(dschgr.__name__, ',', end=' ')
            print()

        print('         : discharges to:', end=' ')
        if (isinstance(unit, effluent) or isinstance(unit, WAS) 
                or not unit.main_outlet_connected()):
            print('None')
        elif unit.main_outlet_connected():
            print(unit.get_downstream_main().__name__, end='(main)')
        else:
            print('None')
        if unit.has_sidestream():
            print(', and ', end=' ')
            if unit.get_downstream_side() == None:
                print('None', end='')
            else:
                print(unit.get_downstream_side().__name__, end='')
            print('(side)')
        else:
            print()
    return None

