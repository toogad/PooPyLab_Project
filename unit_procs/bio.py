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
# This is the definition of class related to biological processes. 
# 
# ----------------------------------------------------------------------------


from unit_procs.streams import pipe
from ASMModel.asm_1 import ASM_1
from ASMModel import constants


# ----------------------------------------------------------------------------
# Update Log: 
# 20190813 KZ: fixed discharge() side outlet
# 20190812 KZ: corrected a few params in solver func.
# 20190726 KZ: revised to match the is_converged()
# 20190715 KZ: added self._type
# 20190612 KZ: migrated to match the new base (poopy_lab_obj) and new "pipe"
# 20190209 KZ: standardized import
# July 30, 2017 KZ: more pythonic style
# March 21, 2017 KZ: Migrated to Python3
# May 26, 2014 KZ: Updated Definition
# December 17, 2013 KZ: Added/revised blend_components() definition.
# December 07, 2013 Kai Zhang

class asm_reactor(pipe):
    __id = 0

    def __init__(self, ActiveVol=380, swd=3.5,
                    Temperature=20, DO=2, *args, **kw):
        # swd = side water depth in meters, default = ~12 ft
        # ActiveVol in m^3, default value equals to 100,000 gallons
        # Temperature = 20 C by default
        # DO = dissolved oxygen, default = 2.0 mg/L

        pipe.__init__(self) 
        self.__class__.__id += 1
        self.__name__ = "Reactor_" + str(self.__id)

        self._type = "ASMReactor"

        self._active_vol = ActiveVol
        self._swd = swd
        self._area = self._active_vol / self._swd

        self._sludge = ASM_1(Temperature, DO)

        self._in_comps = [0.0] * constants._NUM_ASM1_COMPONENTS 
        self._mo_comps = [0.0] * constants._NUM_ASM1_COMPONENTS
        # make _so_comps alias of _mo_comps since there is no side stream for a
        # bioreactor
        self._so_comps = self._mo_comps

        # results of previous round
        self._prev_mo_comps = [0.0] * constants._NUM_ASM1_COMPONENTS
        self._prev_so_comps = [0.0] * constants._NUM_ASM1_COMPONENTS

        print(self.__name__, " Initialized Successfully.")
        return None


    # ADJUSTMENTS TO COMMON INTERFACE
    #
    def discharge(self):
        # record last round's results before updating/discharging:
        self._prev_mo_comps = self._mo_comps[:]
        self._prev_so_comps = self._so_comps[:]

        self.update_combined_input()
        # for a reactor, the outlet has different component
        # concentrations than the inlet
        self.estimate_current_state()

        self._discharge_main_outlet()

        return None
    # END OF ADJUSTMENTS TO COMMON INTERFACE

    
    # FUNCTIONS UNIQUE TO THE ASM_REACTOR CLASS
    #
    # (INSERT CODE HERE)
    #
    def set_active_vol(self, vol=380):
        # vol in M3
        if vol > 0:
            self._active_vol = vol
        else:
            print("ERROR:", self.__name__, "requires an active vol > 0 M3.")
        return None


    def get_active_vol(self):
        return self._active_vol


    def set_ASM_condition(self, Temperature, DO):
        if Temperature >= 4 and DO > 0:
            self._sludge.update(Temperature, DO)
        else:
            print("ERROR:", self.__name__, "given crazy temperature or DO.")
        return None

   
    def get_ASM_params(self):
        return self._sludge.get_params()


    def get_ASM_stoichs(self):
        return self._sludge.get_stoichs()


    def initial_guess(self):
        #TODO: NEED TO PUT IN FIRST GUESS OF MODEL COMPONENTS HERE
        pass

    
    def estimate_current_state(self):
        # get the components from the next iteration.
        self._mo_comps = self._sludge.steady_step(self._prev_mo_comps,
                                                    self._mo_flow,
                                                    self._in_comps,
                                                    self._active_vol)
        # _so_comps is already an aliase of _mo_comps
        return None
    #
    # END OF FUNCTIONS UNIQUE TO THE ASM_REACTOR CLASS

