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
            print(unit.__name__, "'s upstream is not connected")
            loose_end += 1
        if unit.has_sidestream():
            if not unit.side_outlet_connected():
                print(unit.__name__, "'s sidestream is not connected")
                loose_end += 1
        elif not unit.main_outlet_connected():
            print(unit.__name__,"'s main downstream is not connected")
            loose_end +=1 
    if loose_end == 0:
        print("The PFD is ready for simulation")
    else:
        print(loose_end, " connecton(s) to be fixed.")
    return loose_end


def _id_upstream_type(me, upds):
    # identify the type of an upstream discharger (upds) of (me)
    # me: a process unit
    # upds: an upstream discharger of "me"

    if isinstance(me, influent):
        return "VOID"
    elif isinstance(upds, influent):
        return "INFLUENT"
    elif isinstance(upds, splitter):  # splitter & its derived types
        if me == upds.get_downstream_main():
            return "SPLITTER_MAIN"
        else:
            return "SPLITTER_SIDE"
    elif isinstance(upds, pipe):  # pipe & its derived types
        return "PIPE"
    
## testing _id_upstream_type() func:
#for unit in wwtp:
#    if isinstance(unit, influent):
#        print(unit.__name__, "is influent without upstream.")
#    else:
#        print(unit.__name__," upstream:")
#        up = unit.get_upstream()
#        for d in up:
#            print("   ", d.__name__, "is of", _id_upstream_type(unit, d))

 
def _check_WAS(pfd):
    # Check the validity of the WAS units in the pfd. 
    #   1) All WAS units shall be connected to side streams of splitters via
    #   ONE pipe;
    #   2) There can only be 0 or 1 SRT controlling WAS (via its upstream
    #   splitter side);
    # Satisfying the above requirements will allow the SRT controlling splitter
    # to be moved to the front of the pfd.


    # SRT Controlling splitter to be found:
    _srt_ctrl_splt = None  
    _was_connect_ok = False
    _srt_ctrl_count = 0

    for _u in pfd:
        if isinstance(_u, WAS):
            _u_upstr = _u.get_upstream().keys()
            for _upds in _u_upstr:
                if isinstance(_upds, pipe) \
                        and not isinstance(_upds, asm_reactor):
                    _xu = _upds.get_upstream().keys()
                    if len(_xu) == 1:
                        for _uu in _xu:
                            if _id_upstream_type(_upds, _uu) != "SPLITTER_SIDE":
                                print("CONNECTION ERROR:", _u.__name__, 
                                        "shall be 'SIDESTREAM->PIPE->WAS'.")
                                _was_connect_ok = False
                                break
                            if _uu.is_SRT_controller():
                                _srt_ctrl_splt = _uu
                                _srt_ctrl_count += 1

    if _srt_ctrl_count > 1:
        print("PFD ERROR: More than ONE SRT controlling splitters.")
    elif _srt_ctrl_count == 0:
        print("PFD ERROR: No SRT controlling splitter was specified.")
    else:
        print("Found one SRT controller splitter; Moved to the front of PFD")
        pfd.remove(_srt_ctrl_splt)
        pfd.insert(0, _srt_ctrl_splt)

    return _was_connect_ok


def _check_sidestream_flows(pfd):
    # Check the validity of the sidestreams of all splitter types
    # All side stream flows shall be defined by user except for the
    # SRT_Controller's.

    _sidestream_flow_defined = True
    for _u in pfd:
        if isinstance(_u, splitter) and not _u.sidestream_flow_defined():
            print("PFD ERROR: Sidestream feeding", _u.__name__, \
                    "needs its flow defined.")
    return _sidestream_flow_defined
            

def _find_main_only_prefix(cur, done, prefix_ms):
    # cur: current unit being visited
    # done: units whose upstream dischargers have all beenn analyzed
    # prefix_ms: the previous mainstream units leading to cur.
    if isinstance(cur, influent):
        done.append(cur)
        return None

    if cur in prefix_ms:
        return None

    prefix_ms.append(cur)
    _upstr = cur.get_upstream()

    for _k in _upstr:
        if _k not in done and _id_upstream_type(cur, _k) != "SPLITTER_SIDE":
            _find_main_only_prefix(_k, done, prefix_ms) 

    done.append(cur)
    return None


def _has_main_only_loops(pfd):
    # Loops with mainstreams only are not allowed in the PFD
    done = []
    prefix_ms = []

    for _u in pfd:
        _find_main_only_prefix(_u, done, prefix_ms)

    if len(prefix_ms) > 0:
        return True
    else:
        return False


def check_pfd(wwtp):
    _le = _check_connection(wwtp)
    _WAS_ok = _check_WAS(wwtp)
    _side_flow_defined = _check_sidestream_flows(wwtp)
    _has_ms_loops = _has_main_only_loops(wwtp)

    if  _le == 0 and _WAS_ok and _side_flow_defined and _has_ms_loops == False:
        print("PFD READY")
    else:
        print("FIXED PFD ERRORS BEFORE PROCEEDING")

    return None


def show_pfd(wwtp=[]):
    for unit in wwtp:
        print(unit.__name__, ": receives from:", end=" ")
        if isinstance(unit, influent):
            print("None")
        else:
            upstr = unit.get_upstream()
            for dschgr in upstr:
                print(dschgr.__name__, ",", end=" ")
            print()
        print("         : discharges to:", end=" ")
        if isinstance(unit, effluent) or not unit.main_outlet_connected():
            print("None")
        elif unit.main_outlet_connected():
            print(unit.get_downstream_main().__name__, end="(main)")
        else:
            print("None")
        if unit.has_sidestream():
            print(", and ", end=" ")
            if unit.get_downstream_side() == None:
                print("None", end="")
            else:
                print(unit.get_downstream_side().__name__, end="")
            print("(side)")
        else:
            print()
    return None

