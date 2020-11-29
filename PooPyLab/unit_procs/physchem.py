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

"""Defines classes for physical/chemical treatment processes.

    1) Final Clarifier;

    2) Primary Clarifier (#TODO: add);

    3) Dissolved Air Flotation (#TODO: add);

    4) Media Filter (#TODO: add);

    5) Membrane Filtration (#TODO: add);
"""
## @namespace physchem
## @file physchem.py


from ..unit_procs.streams import splitter


# ----------------------------------------------------------------------------


class final_clarifier(splitter):
    """
    A "splitter" w/ different particulate concentrations at inlet/outlets.

    In order to keep the PooPyLab package simple and focused on the biological 
    processes, the final clarifier is assumed to be an ideal one. No detail    
    solids settling model is implemented, as least for now.                    

    However, surface overflow rate, solids loading rate, and HRT will be       
    checked and warnings will be given to user if they are out of normal       
    ranges. Simulation will not proceed until all parameters are within proper 
    ranges. TODO: Add actual solids sedimentation model.                       

    By default, the mainstream and sidestream outlets are overflow and         
    underflow, respectively, of the final clarifier.                           
    """

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

    def __init__(self, active_vol=9500, SWD=3.5):
        """
        Constructor for final_clarifier.
        
        The "final_clarifier" is modeled as an ideal solids-liquid separation
        process that capture the solids from the inlet into the underflow as
        per the user given capture rate. 

        Essentially, the "final_clarifier" is a "splitter" with different
        particulate concentrations among its three branches, while those
        concentrations will be identical for all the branches of an ideal
        "splitter".

        Args:
            active_vol:     active clarifier volume excluding storage cone, m3;
            SWD:            side water depth, m.

        Return:
            None
        """
        splitter.__init__(self)
        self.__class__.__id += 1
        self.__name__ = 'Final_Clarifier_' + str(self.__id)

        self._type = 'Final_Clarifier'

        ## clarifier active volume, bottom cone volume excluded, m3
        self._active_vol = active_vol
        ## side water depth of the active volume, m
        self._swd = SWD
        ## plan section area, m2
        self._area = self._active_vol / self._swd

        self._upstream_set_mo_flow = True

        ## user defined solids capture rate, fraction less than 1.0;
        self._capture_rate = 0.95

        ## underflow solids, mg/L
        self._under_TSS = 15000

        return None


    # ADJUSTMENTS TO COMMON INTERFACE TO FIT THE NEEDS OF FINAL_CLARIFIER
    #
    def set_as_SRT_controller(self, setting=False):
        """
        Set the current splitter as an Solids Retention Time controller.

        This function is bypassed for "final_clarifier".
        """
        print('ERROR:', self.__name__, "can't be set as SRT controller")
        return None


    def discharge(self):
        """
        Pass the total flow and blended components to the downstreams.

        This function is re-implemented for "final_clarifier" because of the   
        need to settle the solids (particulate) and concentrate them at the    
        sidestream (underflow). The function first calls _branch_flow_helper() 
        to set the flows for inlet, mainstream outlet, and sidestream outlet,  
        then calls _settle_solids() to fractions the particulate components    
        according to the branch flows and user set percent solids capture.     

        See:
            _settle_solids();
            set_capture_rate();
            _branch_flow_helper().
        """
        # record last round's results before updating/discharging:
        self._prev_mo_comps = self._mo_comps[:]
        self._prev_so_comps = self._so_comps[:]

        self._branch_flow_helper()

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
    def set_capture_rate(self, capture_rate=0.95):
        """
        Set the percent solids capture for the final clarifier.

        This function is valid only when the "final_clarifier" is treated as a
        perfect solids-liquid separation without actual modeling of the
        settling process (for simplicity purpose at this stage). 

        Future update of PooPyLab will include settling model to determine how
        much solids can be captured based on the configuration of the
        clarifier.

        Args:
            capture_rate:   fraction of total inlet solids captured (< 1.0).

        Return:
            None

        See:
            _settle_solids().
        """
        if 0 < capture_rate < 1:
            self._capture_rate = capture_rate
        else:
            print('ERROR:', self.__name__, 'given unrealistic capture rate.')
        return None


    def _valid_under_TSS(self, uf_TSS):
        """
        Check whether the underflow TSS is realistic.

        Args:
            uf_TSS: current underflow TSS, mg/L.
        
        Return:
            bool

        See:    
            update_combined_input();
            get_TSS().
        """
        self.update_combined_input()
        _in_tss = self.get_TSS('Inlet')
        return _in_tss <= uf_TSS <= 18000


    def _settle_solids(self, particulate_index=[7,8,9,10,11,12]):
        """
        Split the incoming solids into the main- and sidestream outlets.

        Assumptions:
            
            1) All particulate model components settle in the identical fashion
            in the clarifier.

        This function first calculate the updated inlet TSS concentration.

        Then based on the capture rate, split the inlet TSS to the mainstream  
        and sidestream outlets, as if the "final_clarifier" behaved exactly    
        like a "splitter".                                                     

        The fractions of each particulate model components in inlet TSS is then
        calculated. These fractions is then applied to the main- and sidestream
        outlet TSS to back calculate the corresponding particulate model
        components for that branch.

        The soluble model components are identical for all three branches.

        Args:
            particulate_index:  list of index for particulate model components.

        Return:
            None

        See:
            get_TSS();
            _branch_flow_helper();
            totalize_inflow();
            update_combined_input();
        """


        #if not self._valid_under_TSS(self._under_TSS):
        #    print('WARN:', self.__name__, 'has unrealistic underflow TSS.')
        #    return None

        _in_tss = self.get_TSS('Inlet')
        self._under_TSS = (self._total_inflow * _in_tss * self._capture_rate
                        / self._so_flow)

        _of_tss = (self._total_inflow * _in_tss * (1 - self._capture_rate)
                            / self._mo_flow)

        
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
        
        # arbitarily adjust the DO according to the HRT of the final clarifier
        
        _HRT = self._active_vol / self._total_inflow

        if _HRT > 15/1440:  # 15 min HRT
            self._mo_comps[0] = 0.0
            self._so_comps[0] = 0.0

        return None
             
    #
    # END OF FUNCTIONS UNQIUE TO FINAL_CLARIFIER
