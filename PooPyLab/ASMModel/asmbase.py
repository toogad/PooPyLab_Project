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
## @namespace asmbase
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
            _set_ideal_kinetics_20C_to_defaults();
            _set_params();
            _set_stoichs().
        """

        # wastewater temperature used in the model, degC
        self._temperature = ww_temp
        # mixed liquor bulk dissolved oxygen, mg/L
        self._bulk_DO = DO 
        
        # define the model parameters and stochoimetrics as dict() so that it
        # is easier to keep track of names and values

        # default kinetic constants AT 20 degree Celcius under ideal conditions
        self._kinetics_20C = {}

        # kinetic parameters AT PROJECT TEMPERATURE
        self._params = {}

        # stoichiometrics
        self._stoichs = {}

        # ASM model components
        self._comps = []

        # temperature difference b/t what's used and baseline (20C), degC
        self._delta_t = self._temperature - 20

        # oxygen transfer coefficient, mg/m3-day
        # placeholder for now, let
        #   OUR = 80 mg/L-hr;
        #   Saturation DO = 10 mg/L; and
        #   DO in mixed liquor = 2 mg/L
        self._KLa = 80 * 1000 * 24 / (10 - 2)

        return None


    def alter_kinetic_20C(self, name, new_val):
        """
        Alter a model kinetic constant at 20C (baseline temperature).

        Args:
            name:       name of the parameter to be altered (i.e. 'u_max_H');
            new_val:    new parameter numeric value at 20C

        Return:
            None

        See:
            update()
        """
        if new_val > 0 and name in self._kinetics_20C.keys():
            self._kinetics_20C[name] = new_val
        else:
            print('ERROR IN ALTERING 20C KINETICS. NO PARAMETER WAS CHANGED')

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


    def set_KLa(self, kla):
        """
        Set KLa value.

        Args:
            kla:    new KLa value, mg/m3-day

        Return:
            None
        """
        if kla > 0:
            self._KLa = kla
        else:
            print("ERROR IN USER GIVEN KLa VALUE. KLa NOT CHANGED")

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


    def _set_ideal_kinetics_20C_to_defaults(self):
        """
        Set the kinetic params/consts @ 20C to default ideal values.

        See:
            update();
            _set_params();
            _set_stoichs().
        """
        pass


    def _set_params(self):
        """
        Set the kinetic parameters/constants to the project temperature & DO.

        See:
            _set_ideal_kinetics_20C_to_defaults();
            _set_params();
            _set_stoichs();
            update().
        """
        pass
        

    def _set_stoichs(self):
        """
        Set the stoichiometrics for the model.

        Not implemented with details here but in actual models.

        Note:
            Make sure to match the .csv model template file in the
            model_builder folder, Sep 04, 2019):

            _stoichs['x_y'] ==> x is process rate id, and y is component id

        See:
            _set_params();
            _set_ideal_kinetics_20C_to_defaults();
            update().
        """
        pass

        
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

