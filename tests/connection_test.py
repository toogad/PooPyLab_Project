# testing connectivity of the PooPyLab objects.
#
# Author: Kai Zhang
#
# Change Log:
# 2019-07-07: rewritten some testing lines to match the new class struct.
# 2019-07-04: re-test after class restructuring.
# 2019-03-17: testing pfd_check()
# 2019-02-16: finding out flow discharge
# 2019-02-10: passed connection/disconnection tests
# 2019-02-09: initial
#

from unit_procs.streams import influent, effluent, WAS, splitter, pipe
from unit_procs.bio import asm_reactor
from unit_procs.physchem import final_clarifier
from utils.pfd import check_pfd, show_pfd
import pdb


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

    def construct_MLE():
        # make an MLE plant
        inlet.set_downstream_main(p1)
        p1.set_downstream_main(ra)
        ra.set_downstream_main(p2)
        p2.set_downstream_main(rb)
        rb.set_downstream_main(p3)
        p3.set_downstream_main(fc)
        fc.set_downstream_main(p4)
        fc.set_downstream_side(p5)
        #fc.set_sidestream_flow(0.1)
        p4.set_downstream_main(outlet)
        p5.set_downstream_main(splt)
        splt.set_downstream_main(RAS)
        splt.set_downstream_side(p6)
        splt.set_as_SRT_controller(True)
        RAS.set_downstream_main(ra)
        p6.set_downstream_main(waste)
        print("MLE PFD constructed.")
        return None

    def destroy_MLE():
        # disconnection is done by removing upstream dischargers of a unit
        p1.remove_upstream(inlet)
        p3.remove_upstream(p1)  # on purpose
        p3.remove_upstream(rb)
        splt.remove_upstream(p5)
        p6.remove_upstream(splt)
        ra.remove_upstream(RAS)
        outlet.remove_upstream(p4)
        print("MLE PFD destoryed")
        return None
        
    construct_MLE()
    check_pfd(wwtp)
    #pdb.set_trace()
    show_pfd(wwtp)

    destroy_MLE()
    check_pfd(wwtp)
    show_pfd(wwtp)

    print('\n', "Reconstructing PFD...")
    #pdb.set_trace()
    construct_MLE()
    check_pfd(wwtp)
    input("press a key")
    show_pfd(wwtp)


    inlet.set_mainstream_flow(0.1)  # mgd
    splt.set_sidestream_flow(0.01)


    print("Before Flow Balance:")
    for unit in wwtp:
        print(unit.__name__, ":total_inflow=", unit.totalize_inflow(), end="")
        if unit.has_sidestream():
            print(": main_outflow=", unit.get_main_outflow(),
                    " side_outflow=", unit.get_side_outflow())
        else:
            print(": total_outflow=", unit.get_main_outflow())

#    for unit in wwtp:

