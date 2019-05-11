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
    def __init__(self, ActiveVol=380, SWD=3.5):
        splitter.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "FinalClarifier_" + str(self.__id)

        # SWD = side water depth in meters, default = ~12 ft
        # ActiveVol in m^3, default value equals to 100,000 gallons
        self._active_vol = ActiveVol
        self._SWD = SWD
        self._area = self._active_vol / self._SWD

        # user defined solids capture rate, fraction less than 1.0;
        # Typically, this is set to 0.95 but user can change the value.
        self._capture_rate = 0.95

        # user defined underflow solids, mg/L
        self._under_TSS = 15000

        # calculated overflow TSS, mg/L
        self._over_TSS = 30  # place holder

        # calculated underflow based on TSS balance
        self._under_flow = 0  # place holder

        # calculated overflow based on flow balance
        self._over_flow = 0

        print(self.__name__, " initiated successfully.")
        return None

    def estimate_current_state(self):
        '''Determines the under/over flows based on TSS balance'''

        # functions like self.get_TSS(), get_TKN(), etc shall be reserved for
        # the overflow (effluent) conditions

        self.blend_components()

        # total inlet solids, kg/d
        _inlet_solids = self._total_flow * self.get_TSS() * 1E-3

        _under_solids = _inlet_solids * self._capture_rate  # kg/d

        self._under_flow = _under_solids * 1E3 / self._under_TSS

        self._over_flow = self._total_flow - self._under_flow





        
        

        
