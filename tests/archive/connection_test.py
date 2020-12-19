# testing connectivity of the PooPyLab objects.
#
# Author: Kai Zhang
#
# Change Log:
# 2019-07-24: move the MLE pfd construct() and destroy() into MLE module.
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
from utils.pfd import check, show
import CMAS
import pdb


if __name__ == "__main__":

    wwtp = CMAS.construct()
      
    check(wwtp)
    #pdb.set_trace()
    show(wwtp)

    CMAS.destroy()
    check(wwtp)
    show(wwtp)

    print('\n', "Reconstructing PFD...")
    #pdb.set_trace()
    CMAS.construct()
    check(wwtp)
    input("press a key")
    show(wwtp)



    print("Before Flow Balance:")
    for unit in wwtp:
        print(unit.__name__, ":total_inflow=", unit.totalize_inflow(), end=" ")
        if unit.has_sidestream():
            print(": main_outflow=", unit.get_main_outflow(),
                    " side_outflow=", unit.get_side_outflow())
        else:
            print(": total_outflow=", unit.get_main_outflow())

