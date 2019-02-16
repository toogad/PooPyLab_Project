# testing connectivity of the PooPyLab objects.
#
# Author: Kai Zhang
#
# Change Log:
# 2019-02-10: passed connection/disconnection tests
# 2019-02-09: initial
#

from unit_procs.influent import influent
from unit_procs.effluent import effluent
from unit_procs.reactor import asm_reactor
from unit_procs.splitter import splitter
from unit_procs.pipe import pipe
from unit_procs.clarifier import final_clarifier
from unit_procs.was import WAS
from utils.pfd import check_connection, show_pfd
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
    
    


