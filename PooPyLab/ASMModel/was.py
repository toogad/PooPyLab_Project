# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
    
#    Copyright (C) 2014  Kai Zhang
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
#    This is the definition of the WAS class. WAS = Waste Activated Sludge
#    The control of Solids Retention Time (SRT) is through the WAS object.
#
#    Author: Kai Zhang
#
# Update Log:
# Jul 30, 2017 KZ: made code more pythonic
# Mar 21, 2017 KZ: Migrated to Python3
# Sep 26, 2014 KZ: Change inheritance back from Splitter to Effluent
# Aug 25, 2014 KZ: Added InformSRTController function.
# Aug 23, 2014 KZ: Changed its inheritance to Effluent;
#                  Added variables and functions for WAS Flow calculation
# December 06, 2013 Kai Zhang: Initial design

    
import effluent

class WAS(effluent.effluent): 
    __id = 0
    def __init__(self):
        
        effluent.effluent.__init__(self)
        self.__class__.__id += 1
        self.__name__ = 'WAS_' + str(self.__id)
        self._WAS_flow = 0.0  # Unit: m3/d 
        print(self.__name__,' initialized successfully.')

    def get_solids_inventory(self, reactor_list=[]):
        ''' Calculate the total solids mass in active reactors '''
        # reactor_list stores the asm_reactor units that contribute
        # active biomass growth to the WWTP.
        # The result of this function will be used to determine the WAS
        # flow for the entire WWTP.
        #TODO: In the MAIN program, we will need to maintain a list of 
        # reactors that contribute active solids to the WWTP.
        inventory = 0.0
        for unit in reactor_list:
            #TODO: IMPORTANT TO CHECK ALL THE UNITS IN THE reactor_list
            # HAD UPDATED TSS!!! THIS SHOULD BE THE CASE BECAUSE THE 
            # WAS UNIT IS THE LAST ELEMENT IN THE ITERATION LOOP. BUT
            # WILL NEED DOUBLE CHECK.
            inventory += unit.get_TSS() * unit.get_active_vol()
        inventory = inventory / 1000.0  # Convert unit to Kg
        return inventory

    def get_WAS_flow(self, reactor_list=[], SRT=1):
        #SRT is the plant's SRT from user input
        self.update_combined_input()
        self._WAS_flow = self.get_solids_inventory(reactor_list) * 1000\
                        / SRT / self.get_TSS()
        #TODO: in MAIN function, we need to check whether the WAS flow
        # is higher than the influent flow
        return self._WAS_flow

    def inform_SRT_controller(self):
        ''' Pass the WAS Flow to the upstream SRT Controlling Splitter '''
        upstream_unit = self.get_upstream_units().keys()
        if len(upstream_unit) == 1 \
                and isinstance(upstream_unit[0], splitter.splitter):
            if upstream_unit[0].is_SRT_controller():
                upstream_unit[0].setup_sidestream(self, self.get_WAS_flow())
                upstream_unit[0].totalize_flow()
                upstream_unit[0].discharge()  #TODO: IS THIS NEEDED??
            else:
                print("The unit upstream of WAS is not SRT controlling")
        else:
            print("Check the unit upstream of WAS.\
                    There shall be a splitter only")

