# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
#    
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
#
#This is the definition of the Pipe() object, which is basically the Base()
#
#Update Log:
#   Nov 23, 2014 KZ: revised RemoveUpstreamUnit() to check availability to the upstream unit specified
#   Nov 12, 2014 KZ: added: _UpstreamConnected and _MainOutletConnected flags; UpstreamConnected() and
#                           MainOutletConnected() functions
#   Sep 26, 2014 KZ: removed test code
#   June 29, 2014 KZ: Added GetXXX() definitions for solids and COD summary. 
#   March 15, 2014 KZ: AddUpstreamUnit(), RemoveUpstreamUnit(), and SetDownstreamMainUnit() begin here
#   March 08, 2014 KZ: Rewrite according to the new class structure
#   December 07, 2013 Kai Zhang


import base, constants

class Pipe(base.Base):
    __id = 0
    def __init__(self):
        self.__class__.__id += 1
        self.__name__ = 'Pipe_' + str(self.__id)
                
        ## _Inlet store the upstream units and their flow contribution
        # in the format of {unit, Flow}
        self._Inlet = {}
        
        # _MainOutlet is a SINGLE unit that receives all the flows from the
        # current unit
        self._MainOutlet = None #By default this is the MAIN OUTLET.
        
        # _UpstreamConnected is a Boolean flag to indicate whether there are upstream units
        self._UpstreamConnected = False

        # _MainOutletConnected is a Boolean flag to indicate whether there are units 
        #   in MAIN downstream
        self._MainOutletConnected = False

        self._TotalFlow = 0.0 #This is the Total Inflow, which is the same as the outflow for Pipe
        # _TotalFlowUpdated is a Boolean flag to indicate whether _TotalFlow has been updated
        self._FlowTotalized = False

        # _ComponentsBlended is a Boolean flag to indicate whether _EffComp[] have been blended
        self._ComponentsBlended = False

        #  THIS IS WHERE THE CURRENT STATE OF THE REACTOR IS STORED:
        self._EffComp = [0.0] * constants._NUM_ASM1_COMPONENTS
        # _EffComp[0]: X_I,
        # _EffComp[1]: X_S,
        # _EffComp[2]: X_BH,
        # _EffComp[3]: X_BA,
        # _EffComp[4]: X_D,
        # _EffComp[5]: S_I,
        # _EffComp[6]: S_S,
        # _EffComp[7]: -S_DO, COD = -DO
        # _EffComp[8]: S_NO,
        # _EffComp[9]: S_NH,
        # _EffComp[10]: S_NS,
        # _EffComp[11]: X_NS,
        # _EffComp[12]: S_ALK
        print self.__name__,' initialized successfully.'
    # End of __init__()

    def AddUpstreamUnit(self, SingleDischarger):
        '''Add a single upstream unit to the current unit'''
        if not self._Inlet.has_key(SingleDischarger): 
            self._Inlet[SingleDischarger] = 0.0
            # Line above: Setting the flow to 0.0 is a place-holder when 
            # setting up the Process Flow Diagram, because the actual total flow from
            # upstream unit may not have been completely configured.
            # The self.Discharge() method of the upstream unit will totalize the flow, 
            # and blend the components before passing them into the current unit.
            self._FlowTotalized= False
            self._ComponentsBlended = False
            self._UpstreamConnected = True
            SingleDischarger.SetDownstreamMainUnit(self)

    def RemoveUpstreamUnit(self, SingleDischarger):
        ''' Remove a single upstream unit from feeding into the current unit'''
        if self._Inlet.has_key(SingleDischarger):
            self._Inlet.pop(SingleDischarger)
            self._FlowTotalized = False
            self._ComponentsBlended = False
            self._UpstreamConnected = False
            SingleDischarger.SetDownstreamMainUnit(None)


    def SetDownstreamMainUnit(self, SingleReceiver):
        ''' Set the downstream unit that will receive effluent from the current unit'''
        if self._MainOutlet != SingleReceiver: #if the specified SingleReceiver has not been added
            self._MainOutlet = SingleReceiver
            self._MainOutletConnected = True
            if SingleReceiver != None:
                SingleReceiver.AddUpstreamUnit(self)

    def GetUpstreamUnits(self):
        return self._Inlet

    def GetDownstreamMainUnit(self):
        return self._MainOutlet

    def TotalizeFlow(self):
        ''' Totalize all the flows entering the current unit.
            Return type: NO Return
        '''
        self._TotalFlow = 0.0
        for unit in self._Inlet:
            self._TotalFlow += self._Inlet[unit]
        self._FlowTotalized = True

    def BlendComponents(self):
        '''
            BlendComponents() for Base mixes the contents in all inlet
            components and send to the OUTLET, assuming no reaction
            takes palce.
            The definition is changed in ASMReactor where the mixture
            is passed to the INLET of the reactor before reactions.
        '''
        if self._FlowTotalized == False:
            self.TotalizeFlow()
        if self._TotalFlow:
            for Index in range(constants._NUM_ASM1_COMPONENTS):
                tempComp = 0.0
                for unit in self._Inlet:
                    tempComp += unit.GetOutletConcentrations()[Index] * unit.GetOutletFlow()
                self._EffComp[Index] = tempComp / self._TotalFlow
        self._ComponentsBlended = True
    
    def UpdateCombinedInput(self):
        ''' Combined the flows and loads into the current unit'''
        if self._FlowTotalized == False:
            self.TotalizeFlow()
        if self._ComponentsBlended == False:
            self.BlendComponents()
    
    def GetOutletFlow(self):
        ''' Return the total out flow of the current unit (mainstream)
            Return value type: float/double
        '''
        if self._FlowTotalized == False:
            self.TotalizeFlow()
        return self._TotalFlow
    
    def GetOutletConcentrations(self):
        ''' Return the effluent concentrations of the current unit (mainstream)
            Return type: list
        '''
        if self._ComponentsBlended == False:
            self.BlendComponents()
        return self._EffComp
    
    def Discharge(self):
        ''' Pass the total flow and blended components to the next unit.
        '''
        self.UpdateCombinedInput()
        if self._MainOutlet != None:
            #TODO: need to make sure the downstream unit Get the current unit's info 
            self.GetDownstreamMainUnit().UpdateCombinedInput()
    
    def UpstreamConnected(self):
        ''' Get the status of upstream connection'''
        return self._UpstreamConnected

    def MainOutletConnected(self):
        ''' Get the status of downstream main connection'''
        return self._MainOutletConnected

    def _sumHelper(self, ListOfIndex=[]):
        ''' sum up the model components indicated by the ListOfIndex '''
        sum = 0.0;
        for element in ListOfIndex:
            sum += self._EffComp[element]
        return sum

    def GetTSS(self):
        #TODO: need to make COD/TSS = 1.2 changeable for different type of sludge
        ListOfIndex = [0, 1, 2, 3, 4]
        return self._sumHelper(ListOfIndex) / 1.2


    def GetVSS(self):
        #TODO: need to make COD/VSS = 1.42 changeable for diff. type of sludge
        ListOfIndex = [0,1,2,3,4]
        return self._sumHelper(ListOfIndex) / 1.42
    
    def GetTotalCOD(self):
        ListOfIndex = [0, 1,2,3,4,5,6]
        return self._sumHelper(ListOfIndex)

    def GetSoluableCOD(self):
        ListOfIndex = [5, 6]
        return self._sumHelper(ListOfIndex)

    def GetParticulateCOD(self):
        return self.GetTotalCOD - self.getSoluableCOD()

    def GetTN(self):
        ListOfIndex = [8, 9, 10, 11]
        return self._sumHelper(ListOfIndex)

    def GetOrganicN(self):
        ListOfIndex = [10, 11]
        return self._sumHelper(ListOfIndex)

    def GetInorganicN(self):
        ListOfIndex = [8, 9]
        return self._sumHelper(ListOfIndex)

    def GetParticulateN(self):
        return self._EffComp[11]

    def GetSoluableN(self):
        return self.GetTN() - self.getParticulateN()


    def HasSidestream(self):
        ''' Check if the current unit has a sidestream discharge.
            Default = False, i.e. no sidestream
            Return type: boolean
        '''
        return False


