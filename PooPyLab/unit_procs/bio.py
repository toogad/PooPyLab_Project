# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment processes using International Water Association
# Activated Sludge Models.
#
#    Copyright (C) Kai Zhang
#
#    PooPyLab is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
#    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
#    later version.
#
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along with PooPyLab. If not, see
#    <http://www.gnu.org/licenses/>.
#
#
#    This is the definition of the ASM1 model to be imported as part of the Reactor object
#
#


"""Defines classes for biological reactors used in an WWTP.

    1) ASM Reactor (bioreactor using ASM models);

    2) Aerobic Digester (#TODO: add);

    3) ADM Reactor (bioreactor using Anaerobic Digestion Model) (#TODO: add)
"""
## @namespace bio
## @file bio.py

from ..unit_procs.streams import pipe
from ..ASMModel.asm_1 import ASM_1
#from ..ASMModel import constants

#from scipy.integrate import solve_ivp

# ----------------------------------------------------------------------------


class asm_reactor(pipe):
    """
    Bioreactor using ASM kinetics, derived as a "pipe" w/ active volume.

    Current design only uses ASM 1 model. Will need to add flexibility for using ASM 2d, ASM 3, and user revised
    versions of them.

    The "asm_reactor" contain sludge mixed liquor of a certain kinetics described by the chosen model.

    The integration of the model is also done by the "asm_reactor".
    """

    __id = 0

    def __init__(self, act_vol=38000, swd=3.5, ww_temp=20, DO=2, *args, **kw):
        """
        Init w/ active volume, water depth, water temperature, & dissolved O2.

        Args:
            act_vol:    active process volume, m3
            swd:        side water depth, m
            ww_temp:    wastewater temperature, degC
            DO:         dissolved oxygen, mg/L
            args:       (provision for other parameters for different models)
            kw:         (provision for other parameters)

        Return:
            None
        """

        pipe.__init__(self)
        self.__class__.__id += 1
        self._id = self.__class__.__id
        self._type = 'ASMReactor'
        self.__name__ = self._type + '_' + str(self._id)
        self._codename = self.__name__

        # active volume, m3
        self._active_vol = act_vol
        # side water depth, m
        self._swd = swd
        # plan view section area, m2
        self._area = self._active_vol / self._swd

        # sludge mixed liquor contained in the reactor
        self._sludge = ASM_1(ww_temp, DO)

        # storage of _sludge._dCdt for the current step
        self._del_C_del_t = [0.0] * len(self._sludge._comps)

        self._in_comps = [0.0] * len(self._sludge._comps)
        self._mo_comps = [0.0] * len(self._sludge._comps)

        # results of previous round
        #self._prev_mo_comps = [0.0] * len(self._sludge._comps)
        #self._prev_so_comps = self._prev_mo_comps

        self._upstream_set_mo_flow = True

        self._model_file_path = self.set_model_file_path()

        return None


    # ADJUSTMENTS TO COMMON INTERFACE
    #



    def assign_initial_guess(self, initial_guess):
        """
        Assign the intial guess to the unit before simulation.

        This function is re-implemented for "asm_reactor" which contains the "sludge" whose kinetics are described by  
        the model.                                                                                                     

        When passing the initial guess into an "asm_reactor", the reactor's inlet, mainstream outlet, and the "sludge" 
        in it all get the same list of model component concentrations.                                                 

        Args:
            initial_guess:  list of model components

        Return:
            None
        """
        self._sludge._comps = initial_guess[:]
        self._mo_comps = initial_guess[:]  # CSTR: outlet = mixed liquor
        return None


    def update_proj_conditions(self, ww_temp=20, elev=100, salinity=1.0):
        """
        Update the site conditions for the process unit.

        Args:
            ww_temp:    water/wastewater temperature, degC
            elev:       site elevation above mean sea level, meter
            salinity:   salinity of w/ww, GRAM/L

        Return:
            None

        See:
            get_saturated_DO().
        """
        if ww_temp > 4 and ww_temp <= 40\
                and elev >= 0 and elev <= 3000\
                and salinity >= 0:
            self._ww_temp = ww_temp
            self._elev = elev
            self._salinity = salinity
            self._DO_sat_T = self.get_saturated_DO()
            self.set_model_condition(self._ww_temp, self._sludge.get_bulk_DO())
        else:
            print(self.__name__, ' ERROR IN NEW PROJECT CONDITIONS. NO UPDATES')

        return None


    def get_config(self):
        """
        Generate the config info of the unit to be saved to file.

        Args:
            None

        Return:
            a config dict for json
        """

        # All Units are METRIC
        config = {
            'Codename': self._codename,
            'Name': self.__name__,
            'Type': self._type,
            'ID': str(self._id),
            'Num_Model_Components': str(self._num_comps),
            'Inlet_Arrayname': self._codename + '_in_comp',
            'Main_Outlet_Arrayname': self._codename + '_mo_comp',
            'Side_Outlet_Arrayname': self._codename + '_so_comp',
            'IN_Flow_Data_Source': str(self._in_flow_ds)[-3:],
            'MO_Flow_Data_Source': str(self._mo_flow_ds)[-3:],
            'SO_Flow_Data_Source': str(self._so_flow_ds)[-3:],
            'User_Defined_SO_Flow': self._so_flow,
            'Inlet_Codenames': ' '.join([k.get_codename() for k in self._inlet]) if self._inlet else 'None',
            'Main_Outlet_Codename': self._main_outlet.get_codename() if self._main_outlet else 'None',
            'Side_Outlet_Codename': self._side_outlet.get_codename() if self._side_outlet else 'None',
            'Is_SRT_Controller': 'True' if self._SRT_controller else 'False',
            'Active_Volume': str(self._active_vol), #unit: m3
            'Side_Water_Depth': str(self._swd),  #unit: m
            'Model_File_Path:': self.get_model_file_path()
        }

        return config
    # END OF ADJUSTMENTS TO COMMON INTERFACE


    # FUNCTIONS UNIQUE TO THE ASM_REACTOR CLASS
    #
    # (INSERT CODE HERE)
    #

    def set_active_vol(self, vol=380):
        """
        Set the active process volume.
        
        Args:
            vol:    active volume to be used. (m3)

        Return:
            None
        """
        if vol > 0:
            self._active_vol = vol
        else:
            print("ERROR:", self.__name__, "requires an active vol > 0 M3.")
        return None


    def get_active_vol(self):
        """
        Return the active process volume. (m3)
        """
        return self._active_vol


    def set_model_condition(self, ww_temp, DO):
        """
        Set the wastewater temperature and dissolved O2 for the model.

        This function updates the model conditions for the "sludge" the "asm_reactor" contains.                        

        Args:
            ww_temp:    wastewtaer temperature in degC;
            DO:         dissolved O2 concentration in mg/L.
        
        Return:
            None

        See:
            ASMModel.ASM_1.update().
        """
        if ww_temp > 4 and ww_temp <= 40 and DO >= 0:
            self._sludge.update(ww_temp, DO)
        else:
            print("ERROR:", self.__name__, "given crazy temperature or DO.")
        return None

   
    def get_model_params(self):
        """
        Return the kinetic parameters of the applied model.

        Return:
            {param_name, param_val_adjusted}

        See:
            ASMModel.ASM_1.get_params().
        """
        return self._sludge.get_params()


    def get_model_stoichs(self):
        """
        Return the stoichiometrics of the applied model.

        Return:
            {id_of_stoich, val}

        See:
            ASMModel.ASM_1.get_stoichs().
        """
        return self._sludge.get_stoichs()

    #
    # END OF FUNCTIONS UNIQUE TO THE ASM_REACTOR CLASS

