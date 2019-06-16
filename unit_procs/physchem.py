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
#    Definition of physical-chemical process units.
#    Author: Kai Zhang
#
# ----------------------------------------------------------------------------


from unit_procs.streams import splitter


# ----------------------------------------------------------------------------

# final_clarifier class - Change Log: 
# 20190612 KZ: migrated to new base
# 20190209 KZ: standardized import
#   July 30, 2017 KZ: made it more pythonic.
#   March 21, 2017 KZ: Migrated to Python3
#   May 26, 2014 KZ: Changed base class from Base to Splitter
#   July 11, 2013 KZ: Initial commit

class final_clarifier(splitter):
    # In order to keep the PooPyLab package simple and focused on the
    # biological processes, the final clarifier is assumed to be an ideal one.
    # No detail solids settling model is implemented, as least for now.

    # However, surface overflow rate, solids loading rate, and HRT will be
    # checked and warnings will be given to user if they are out of normal
    # ranges. Simulation will not proceed until all parameters are within
    # proper ranges. TODO: Add actual solids sedimentation model.

    # By default, the mainstream and sidestream outlets are overflow and
    # underflow, respectively, of the final clarifier.

    __id = 0
    def __init__(self, active_vol=380, SWD=3.5):
        splitter.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "FinalClarifier_" + str(self.__id)

        # SWD = side water depth in meters, default = ~12 ft
        # active_vol in m^3, default value equals to 100,000 gallons
        # active_vol assumed not to include bottom cone
        self._active_vol = active_vol
        self._SWD = SWD
        self._area = self._active_vol / self._SWD

        # user defined solids capture rate, fraction less than 1.0;
        # Typically, this is set to 0.95 but user can change the value.
        self._capture_rate = 0.95

        # user defined underflow solids, mg/L
        self._under_TSS = 12000

        print(self.__name__, " initiated successfully.")
        return None


    # FUNCTIONS UNIQUE TO FINAL_CLARIFIER
    #
    # (INSERT CODE HERE)
    def _valid_under_TSS(self, uf_TSS):
        self.update_combined_input()
        _in_tss = self.get_TSS("Inlet")
        return _in_tss <= uf_TSS < 15000


    def _settle_solids(self, index_list=[0, 1, 2, 3, 4, 11]):
        if not self._valid_under_TSS(self._under_TSS):
            print("ERROR:", self.__name__, "has invalid underflow TSS.")
            return None

        _in_tss = self.get_TSS("Inlet")
        self._so_flow = (self._total_inflow * _in_tss * self._capture_rate
                        / self._under_TSS)
        self._side_flow_defined = True  # TODO: CONTINUE HERE
        self._mo_flow = self._total_inflow - self._so_flow

        # overflow TSS
        _of_tss = (self._total_inflow * _in_tss * (1 - self._capture_rate)
                        / self._mo_flow)
        
        # initiate _mo_comps and _so_comps so that all dissolved components
        # (S_*) are identical among the three streams
        self._mo_comps = self._in_comps[:]
        self._so_comps = self._in_comps[:]

        # split the ASM model components associated with solids (X_*), assuming
        # each component is split into the overflow and underflow keeping its
        # fraction in clarifier inlet TSS.
        for i in index_list:
            _frac = self._in_comps[i] / _in_tss
            self._mo_comps[i] = _of_tss * _frac
            self._so_comps[i] = self._under_TSS * _frac
        
        return None
             
 
    def set_capture_rate(self, capture_rate=0.95):
        if 0 < capture_rate < 1:
            self._capture_rate = capture_rate
        else:
            print("ERROR:", self.__name__, "given unrealistic capture rate.")
        return None


    def set_underflow_TSS(self, uf_TSS=12000):
        if self._valid_under_TSS(uf_TSS):
            self._under_TSS = uf_TSS
        else:
            print("ERROR:", self.__name__, "given crazy underflow TSS.")
        return None

    #
    # END OF FUNCTIONS UNQIUE TO FINAL_CLARIFIER


    # ADJUSTMENTS TO COMMON INTERFACE TO FIT THE NEEDS OF FINAL_CLARIFIER
    #
    def set_as_SRT_controller(self, setting=False):
        print("ERROR:", self.__name__, "can't be set as SRT controller")
        return None

    def set_sidestream_flow(self, flow=0):
        print("ERROR:", self.__name__, "doesn't accept sidestream flow input.")
        return None


    def discharge(self):
        self.update_combined_input()
        self._settle_solids()
        self._discharge_main_outlet()
        self._discharge_side_outlet()
        return None
           
        
    #
    # END ADJUSTMENTS TO COMMON INTERFACE
        
        

        
