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

#    This is the definition of the WAS unit. WAS = Waste Activated Sludge
#    The control of Solids Retention Time (SRT) is through the WAS object.
#
#    Author: Kai Zhang
#

# Update Log:
# Sep 26, 2014 KZ: Change inheritance back from Splitter to Effluent
# Aug 25, 2014 KZ: Added InformSRTController function.
# Aug 23, 2014 KZ: Changed its inheritance to Effluent;
#                  Added variables and functions for WAS Flow calculation
# December 06, 2013 Kai Zhang: Initial design

    
import effluent

class WAS(effluent.Effluent): 
    __id = 0
    def __init__(self):
        
        effluent.Effluent.__init__(self)
        self.__class__.__id += 1
        self.__name__ = 'WAS_' + str(self.__id)
        self._WASFlow = 0.0 #Unit: m3/d 
        print self.__name__,' initialized successfully.'

    def GetSolidsInventory(self, ReactorList = []):
        ''' Calculate the total solids mass in active reactors '''
        # ReactorList stores the ASMReactor units that contribute
        # active biomass growth to the WWTP.
        # The result of this function will be used to determine the WAS
        # flow for the entire WWTP.
        #TODO: In the MAIN program, we will need to maintain a list of 
        # reactors that contribute active solids to the WWTP.
        Inventory = 0.0
        for unit in ReactorList:
            #TODO: IMPORTANT TO CHECK ALL THE UNITS IN THE ReactorList
            # HAD UPDATED TSS!!! THIS SHOULD BE THE CASE BECAUSE THE 
            # WAS UNIT IS THE LAST ELEMENT IN THE ITERATION LOOP. BUT
            # WILL NEED DOUBLE CHECK.
            Inventory += unit.GetTSS() * unit.GetActiveVol()
        Inventory = Inventory / 1000.0 # Convert unit to KiloGram
        return Inventory

    def GetWASFlow(self, ReactorList = [], SRT = 1.0):
        #SRT is the plant's SRT from user input
        self.UpdateCombinedInput()
        self._WASFlow = self.GetSolidsInventory(ReactorList) * 1000.0 \
                        / SRT / self.GetTSS()
        #TODO: in MAIN function, we need to check whether the WAS flow
        # is higher than the influent flow
        return self._WASFlow

    def InformSRTController(self):
        ''' Pass the WAS Flow to the upstream SRT Controlling Splitter '''
        UpstreamUnit = self.GetUpstreamUnits().keys()
        if len(UpstreamUnit) == 1 and isinstance(UpstreamUnit[0], splitter.Splitter):
            if UpstreamUnit[0].IsSRTController():
                UpstreamUnit[0].SetUpSidestream(self, self.GetWASFlow())
                UpstreamUnit[0].TotalizeFlow()
                UpstreamUnit[0].Discharge() #TODO: IS THIS LINE NEEDED??
            else:
                print "The unit upstream of WAS is not SRT controlling"
        else:
            print "Check the unit upstream of WAS. There shall be a splitter only"

