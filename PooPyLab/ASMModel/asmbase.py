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
#    This is the definition of the ASM1 model to be imported
#    as part of the Reactor object
#
#


"""Definition of the common interface for IWA Activated Sludge Models
"""
## @namespace asm_base
## @file asmbase.py


from ..ASMModel import constants

class asm_model(object):
    """
    Common interface for all IWA Activated Sludge Models
    """

    def __init__(self, ww_temp=20, DO=2):
        """
        Initialize the ASM 1 model with water temperature and dissolved O2.

        Args:
            ww_temp:    wastewater temperature, degC;
            DO:         dissoved oxygen, mg/L

        Return:
            None

        See:
            _set_params();
            _set_stoichs();
        """

        ## wastewater temperature used in the model, degC
        self._temperature = ww_temp
        ## mixed liquor bulk dissolved oxygen, mg/L
        self._bulk_DO = DO 
        
        # define the model parameters and stochoimetrics as dict() so that it
        # is easier to keep track of names and values

        ## kinetic constants
        self._params = {}

        ## stoichiometrics
        self._stoichs = {}

        ## temperature difference b/t what's used and baseline (20C), degC
        self._delta_t = self._temperature - 20
        
        self.update(ww_temp, DO)
        
        # The Components the ASM components IN THE REACTOR
        # For ASM #1:
        #
        #    self._comps[0]: S_DO as COD
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
        #
        ## ASM model components
        self._comps = []

        return None


    def update(self, ww_temp, DO):
        """ 
        Update the ASM model with new water temperature and dissolved O2. 

        Args:
            ww_temp:    wastewater temperature, degC;
            DO:         dissolved oxygen, mg/L

        Return:
            None

        See:
            _set_params();
            _set_stoichs().
        """
        self._temperature = ww_temp
        self._bulk_DO = DO
        self._delta_t = self._temperature - 20.0
        self._set_params()
        self._set_stoichs()
        return None


    def get_params(self):
        """
        Return the values of the kinetic parameter dictionary.
        """
        return self._params.copy()


    def get_stoichs(self):
        """
        Return the values of the stoichiometric dictionary.
        """
        return self._stoichs.copy()


    def get_all_comps(self):
        """
        Return a copy of the model components (concentrations).
        """
        return self._comps[:]


    def get_bulk_DO(self):
        """
        Return the bulk dissolved O2 concentration, mg/L.
        """
        return self._bulk_DO


    def _set_params(self):
        """
        Set the kinetic parameters/constants @ 20C for the ASM model.

        This function updates the self._params based on the model temperature
        and DO.

        Not implemented with details here but in actual models.

        See:
            update();
            _set_stoichs().
        """
        pass
        
    # STOCHIOMETRIC MATRIX 
    def _set_stoichs(self):
        """
        Set the stoichiometrics @ 20C for the ASM 1 model.

        Not implemented with details here but in actual models.

        Note:
            Make sure to match the .csv model template file in the
            model_builder folder, Sep 04, 2019):

            _stoichs['x_y'] ==> x is process rate id, and y is component id

        See:
            _set_params();
            update().
        """
        pass

        
    # PROCESS RATE DEFINITIONS (Rj, M/L^3/T):
    #
    def _monod(self, term_in_num_denum, term_only_in_denum):
        """
        Template for Monod kinetics or switches.

        The following kinetics/swithes all use the _monod() function:
            Monod kinetic of solube biodegradable COD on Heterotrophs;
            Monod switch of Dissol. O2 on Heterotrophs;
            Monod switch of Dissol. O2 on Autotrophs;
            Monod kinetic of Ammonia-N on Autotrophs;
            Monod kinetic of NOx-N on Autotrophs.
        
        Args:
            term_in_num_denum:      the term in both numerator & denumerator
            term_only_in_denum:     the term only in numerator

        Return:
            float
        """
        return term_in_num_denum / (term_in_num_denum + term_only_in_denum)


    def _dCdt(self, t, mo_comps, vol, flow, in_comps):
        '''
        Defines dC/dt for the reactor based on mass balance.

        Overall mass balance:
        dComp/dt == InfFlow / Actvol * (in_comps - mo_comps) + GrowthRate
                 == (in_comps - mo_comps) / HRT + GrowthRate
 
        Args:
            t:          time for use in ODE integration routine, d
            mo_comps:   list of model component for mainstream outlet, mg/L.
            vol:        reactor's active volume, m3;
            flow:       reactor's total inflow, m3/d
            in_comps:   list of model compoennts for inlet, mg/L;

        Return:
            dC/dt of the system ([float])
        
        ASM1 Components:
            0_S_DO, 1_S_I, 2_S_S, 3_S_NH, 4_S_NS, 5_S_NO, 6_S_ALK,
            7_X_I, 8_X_S, 9_X_BH, 10_X_BA, 11_X_D, 12_X_NS

        Not implemented with details here but in the actual models.
        '''
        pass

