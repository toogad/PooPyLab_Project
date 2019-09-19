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
# 20190916 KZ: updated to match asm1 matrix (component index)
# 20190726 KZ: revised discharge() to match the add. of is_converged()
# 20190612 KZ: migrated to new base
# 20190715 KZ: added self._type
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

    # ASM components
    # The Components the ASM components IN THE REACTOR
    # For ASM #1:
    #
    #    self._comps[0]: S_DO as DO
    #    self._comps[1]: S_I
    #    self._comps[2]: S_S
    #    self._comps[3]: S_NH
    #    self._comps[4]: S_NS
    #    self._comps[5]: S_NO
    #    self._comps[6]: S_ALK
    #    self._comps[7]: X_I
    #    self._comps[8]: X_S
    #    self._comps[9]: X_BH
    #    self._comps[10]: X_BA
    #    self._comps[11]: X_D
    #    self._comps[12]: X_NS

    __id = 0
    def __init__(self, active_vol=380, SWD=3.5):
        splitter.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "FinalClarifier_" + str(self.__id)

        self._type = "Final_Clarifier"

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
        self._under_TSS = 15000

        return None


    # ADJUSTMENTS TO COMMON INTERFACE TO FIT THE NEEDS OF FINAL_CLARIFIER
    #
    def set_as_SRT_controller(self, setting=False):
        print("ERROR:", self.__name__, "can't be set as SRT controller")
        return None

    def set_sidestream_flow(self, flow=0):
        print("ERROR:", self.__name__, "doesn't accept sidestream flow input.")
        return None


    def discharge(self):
        # record last round's results before updating/discharging:
        self._prev_mo_comps = self._mo_comps[:]
        self._prev_so_comps = self._so_comps[:]

        #self.update_combined_input()

        # for a clarifier, the main and side outlets have different solids
        # concentrations than the inlet's
        self._settle_solids()

        self._discharge_main_outlet()
        self._discharge_side_outlet()

        return None
    #
    # END ADJUSTMENTS TO COMMON INTERFACE


    # FUNCTIONS UNIQUE TO FINAL_CLARIFIER
    #
    # (INSERT CODE HERE)
    def _valid_under_TSS(self, uf_TSS):
        self.update_combined_input()
        _in_tss = self.get_TSS('Inlet')
        return _in_tss <= uf_TSS <= 18000


    def _settle_solids(self, particulate_index=[7,8,9,10,11,12]):
        if not self._valid_under_TSS(self._under_TSS):
            print('ERROR:', self.__name__, 'has invalid underflow TSS.')
            return None

        _in_tss = self.get_TSS('Inlet')
        self._so_flow = (self._total_inflow * _in_tss * self._capture_rate
                        / self._under_TSS)
        self._side_flow_defined = True
        self._mo_flow = self._total_inflow - self._so_flow

        # overflow TSS
        if self._mo_flow > 0:
            _of_tss = (self._total_inflow * _in_tss * (1 - self._capture_rate)
                            / self._mo_flow)
        else:
            _of_tss = 30  #TODO: is this ok?
        
        # initiate _mo_comps and _so_comps so that all dissolved components
        # (S_*) are identical among the three streams
        self._mo_comps = self._in_comps[:]
        self._so_comps = self._in_comps[:]

        # split the ASM model components associated with solids (X_*), assuming
        # each component is split into the overflow and underflow keeping its
        # fraction in clarifier inlet TSS.
        for i in particulate_index:
            if _in_tss > 0:
                _frac = self._in_comps[i] / _in_tss
            else:
                _frac = 0
            self._mo_comps[i] = _of_tss * _frac
            self._so_comps[i] = self._under_TSS * _frac
        
        return None
             
 
    def set_capture_rate(self, capture_rate=0.95):
        if 0 < capture_rate < 1:
            self._capture_rate = capture_rate
        else:
            print("ERROR:", self.__name__, "given unrealistic capture rate.")
        return None


    def set_underflow_TSS(self, uf_TSS=15000):
        if self._valid_under_TSS(uf_TSS):
            self._under_TSS = uf_TSS
        else:
            print("ERROR:", self.__name__, "given crazy underflow TSS.")
        return None

    #
    # END OF FUNCTIONS UNQIUE TO FINAL_CLARIFIER
