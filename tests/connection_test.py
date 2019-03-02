# testing connectivity of the PooPyLab objects.
#
# Author: Kai Zhang
#
# Change Log:
# 2019-02-16: finding out flow discharge
# 2019-02-10: passed connection/disconnection tests
# 2019-02-09: initial
#

from unit_procs.streams import influent, effluent, WAS, splitter, pipe
from unit_procs.bio import asm_reactor
from unit_procs.physchem import final_clarifier
from utils.pfd import check_connection, show_pfd
import pdb


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
    

def _check_WAS(pfd):
    # Check the validity of the WAS units in the pfd. 
    #   1) All WAS units shall be connected to side streams of splitters;
    #   2) There can only be 0 or 1 SRT controlling WAS (via its upstream
    #   splitter side);
    # Satisfying the above requirements will allow the SRT controlling splitter
    # to be moved to the front of the pfd.


    # SRT Controlling splitter to be found:
    _srt_ctrl_splt = None  
    _was_connect_error = False
    _srt_ctrl_count = 0

    for _u in pfd:
        if isinstance(_u, WAS):
            _u_upstr = _u.get_upstream()
            for _upds in _u_upstr:
                if _id_upstream_type(_u, _upds) != "SPLITTER_SIDE":
                    print("CONNECTION ERROR:", _u.__name__, 
                            "shall connect to a side stream.")
                    _was_connect_error = True
                    break
                elif _upds.is_SRT_controller():
                    _srt_ctrl_splt = _upds
                    _srt_ctrl_count += 1

    if _was_connect_error:
        return None

    if _srt_ctrl_count > 1:
        print("PFD ERROR: More than ONE SRT controlling splitters.")
    elif _srt_ctrl_count == 0:
        print("PFD ERROR: No SRT controlling splitter was specified.")
    else:
        print("Found one SRT controller splitter; Moved to the front of PFD")
        pfd.remove(_srt_ctrl)
        pfd.insert(0, _srt_ctrl)

    return None





    

def _move_SRT_Controller_to_front(pfd):

    for _u in pfd:
        if isinstance(_u, WAS):
            pfd.remove(_u)
            pfd.insert(0, _u)
            break
    return None








            




if __name__ == "__main__":

    inlet = influent()

    p1 = pipe()

    ra = asm_reactor()

    p2 = pipe()

    rb = asm_reactor()
    p3 = pipe()

    fc = final_clarifier()
    p4 = pipe()  # to outlet
    p5 = pipe()  # to splt

    outlet = effluent()

    splt = splitter()
    p6 = pipe()  # to waste
    RAS = pipe()  # to ra

    waste = WAS()

    wwtp = [inlet,
            p1, p2, p3, p4, p5, p6,
            ra, rb, fc, outlet,
            RAS, waste, splt]

    def construct_pfd():
        # make an MLE plant
        inlet.set_downstream_main(p1)
        p1.set_downstream_main(ra)
        ra.set_downstream_main(p2)
        p2.set_downstream_main(rb)
        rb.set_downstream_main(p3)
        p3.set_downstream_main(fc)
        fc.set_downstream_main(p4)
        fc.set_downstream_side(p5)
        p4.set_downstream_main(outlet)
        p5.set_downstream_main(splt)
        splt.set_downstream_main(RAS)
        splt.set_downstream_side(p6)
        RAS.set_downstream_main(ra)
        p6.set_downstream_main(waste)
        print("PFD constructed.")
        return None

    def destroy_pfd():
        # disconnection is done by removing upstream dischargers of a unit
        p1.remove_upstream(inlet)
        p3.remove_upstream(p1)  # on purpose
        p3.remove_upstream(rb)
        splt.remove_upstream(p5)
        p6.remove_upstream(splt)
        ra.remove_upstream(RAS)
        outlet.remove_upstream(p4)
        print("PFD destoryed")
        return None
        
    construct_pfd()
    check_connection(wwtp)
    show_pfd(wwtp)

    destroy_pfd()
    check_connection(wwtp)
    show_pfd(wwtp)

    print('\n', "Reconstructing PFD...")
    construct_pfd()
    check_connection(wwtp)
    show_pfd(wwtp)


    inlet.set_flow(0.1)  # mgd
    fc.set_sidestream_flow(0.16)
    splt.set_sidestream_flow(0.01)


    for unit in wwtp:
        print(unit.__name__, ":total_inflow=", unit.get_outlet_flow(), end="")
        if unit.has_sidestream():
            print(": main_outflow=", unit._main_outlet_flow,
                    " side_outflow=", unit._side_outlet_flow)
        else:
            print(": total_outflow=", unit.get_outlet_flow())


    # testing _id_upstream_type() func:
    for unit in wwtp:
        if isinstance(unit, influent):
            print(unit.__name__, "is influent without upstream.")
        else:
            print(unit.__name__," upstream:")
            up = unit.get_upstream()
            for d in up:
                print("   ", d.__name__, "is of", _id_upstream_type(unit, d))

            

    






    
    


