# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
#    
#    Copyright (C) 2014  Kai Zhang
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
#    Definition of the plant Influent unit.
#
# Change Log:
#   June 16, 2015 KZ: Removed _PreFix, _Group status and 
#                       Set(Get)PreFixStatus(), Set(Get)GroupStatus;
#                       Renamed _Done to _Visited, SetAs(Is)Done() to
#                       SetAs(Is)Visited().
#   March 20, 2015 KZ: Added _PreFix, _Group, _Done status and 
#                       Set(Get)PreFixStatus(), Set(Get)GroupStatus, 
#                       SetAs(Is)Done().
#   November 18, 2014 KZ: Added UpstreamConnected() and set to True
#   November 12, 2014 KZ: added _MainOutletConnected flag 
#                           and MainOutletConnected() function
#   October 19, 2014 KZ: removed test code
#   March 15, 2014: KZ: redefined for the new class structure.
#   December 07, 2013 Kai Zhang: first draft


import base, constants

class Influent(base.Base):
    __id = 0

    def __init__(self):
        self.__class__.__id += 1
        self.__name__ = "Influent_" + str(self.__id)

        # Store the influent characteristics in a list()
        # For ASM #1:
        #
        #    self._InfComp[0]: X_I
        #    self._InfComp[1]: X_S
        #    self._InfComp[2]: X_BH
        #    self._InfComp[3]: X_BA
        #    self._InfComp[4]: X_D
        #    self._InfComp[5]: S_I
        #    self._InfComp[6]: S_S
        #    self._InfComp[7]: S_DO
        #    self._InfComp[8]: S_NO
        #    self._InfComp[9]: S_NH
        #    self._InfComp[10]: S_NS
        #    self._InfComp[11]: X_NS
        #    self._InfComp[12]: S_ALK
        self._InfComp = [0.0] * constants._NUM_ASM1_COMPONENTS

        # Influent characteristics from user measurements/inputs
        # Setting default values for municipal wastewater in USA
        # TODO: July 10, 2013, Default Unit: mg/L except where noted differently
        self._BOD5 = 250.0
        self._TSS = 250.0
        self._VSS = 200.0
        self._TNK = 40.0
        self._NH3 = 28.0
        self._NO = 0.0 #JULY 10, 2013
        self._TP = 10.0
        self._Alk = 6.0 #in mmol/L as CaCO3
        self._DO = 0.0 

        # Plant influent flow in M3/DAY, JULY 10, 2013
        # TODO: will be user-input from GUI, JULY 10, 2013. FROM THE GUI, USER
        #   will use MGD. DEFAULT VALUE = 10 MGD. 
        self._DesignFlow = 10.0 * 1000.0 / 3.78 #convert to M3/day, July 10, 2013

        # Store the unit that receives the plant influent
        self._Outlet = None
        
        # _MainOutletConnected is to store the status about whether there is a
        #   downstream unit.
        self._MainOutletConnected = False

        # _PreFix is True/False on whether the unit is already visited by the loop
        #   finding process
        self._PreFix = False

        # _Group is '' (empty string) if the unit has not been assigned to any 
        #   specific group by the loop finding process.
        # If the unit has been assigned to a group, _Group will record the group ID.
        self._Group = ''

        # _Visited is True/False on whether the loop finding process has finished
        #   analyzing the unit
        self._Visited = False
        
        print self.__name__,' initialized successfully.'

    def GetUpstreamUnits(self):
        ''' Get the dict that stores all the upstream units that feed into current one
            Return Type: None (for Influent) or dict (for others)
        '''
        return None

    def SetDownstreamMainUnit(self, SingleReceiver):
        ''' Set the downstream unit that will receive effluent from the current unit'''
        if self._Outlet != SingleReceiver: #if the specified SingleReceiver has not been added
            self._Outlet = SingleReceiver 
            self._MainOutletConnected = True
            if SingleReceiver != None:
                SingleReceiver.AddUpstreamUnit(self)
    
    def UpstreamConnected(self):
        '''Placeholder, always return True for Influent as it doesn't need an upstream unit'''
        return True
    
    def MainOutletConnected(self):
        ''' Return the status of outlet connection'''
        return self._MainOutletConnected

    def GetDownstreamMainUnit(self):
        ''' Get the single unit downstream of the current one
            Return Type: base.Base
        '''
        return self._Outlet

    def SetAsVisited(self, Status = False):
        self._Visited = Status

    def IsVisited(self):
        return self._Visited
    
    def TotalizeFlow(self):
        ''' Totalize all the flows entering the current unit.
            Return type: NO Return
            Does nothing for Influent object as the flow is fixed.
        '''
        pass

    def BlendComponents(self):
        '''
            BlendComponents() for Base mixes the contents in all inlet
            components and send to the OUTLET, assuming no reaction
            takes palce.
            The definition is changed in ASMReactor where the mixture
            is passed to the INLET of the reactor before reactions.
            Does nothing for Inlfuent object as the components are in a 
            single source.
        '''
        pass
    
    def UpdateCombinedInput(self):
        ''' Combined the flows and loads into the current unit
            Doesn't need to do anything since Influent object does not 
            receive any upstream input.
        '''
        pass

    def GetOutletFlow(self):
        ''' Return the total out flow of the current unit (mainstream)
            Return value type: float/double
        '''
        return self._DesignFlow

    def GetOutletConcentrations(self):
        ''' Return the effluent concentrations of the current unit (mainstream)
            Return type: list
        '''
        return self._InfComp

    def Discharge(self):
        ''' Pass the total flow and blended components to the next unit.
        '''
        if self._Outlet != None:
            self.GetDownstreamMainUnit().UpdateCombinedInput()
    
    def ReceiveFrom(self, SingleDischarger):
        ''' Influent doesn't need to receive anything'''
        pass

    def Interpret(self):
        ''' Convert user input parameters into the ones that the ASM model can understand '''
         #TODO: July 10, 2013: the first set of conversion available here is for municipal 
        #   wastewater. Industrial wastewater may have completely different
        #   conversion factors and needs to be tested.
        
        # JULY 10, 2013 ADDED
        #influent biodegradable COD, BOD/COD = 1.71 for typ. muni.WW
        Inf_CODb = self._BOD5 * 1.71
        #influent total COD, COD/BOD5 = 2.04 per BioWin
        Inf_CODt = self._BOD5 * 2.04
        #influent total innert COD, 
        Inf_CODi = Inf_CODt - Inf_CODb
        #influent soluble innert COD
        Inf_S_I = 0.13 * Inf_CODt
        #influent particulate innert COD
        Inf_X_I = Inf_CODi - Inf_S_I
        #influent particulate biodegradable COD
        Inf_X_S = 1.6 * self._VSS - Inf_X_I
        #influent soluble biodegradable COD
        Inf_S_S = Inf_CODb - Inf_X_S
        #influent Heterotrophs (mgCOD/L), 
        Inf_X_BH = 0.0
        #influent Autotrophs (mgCOD/L), 
        Inf_X_BA = 0.0
        #influent Biomass Debris (mgCOD/L), 
        Inf_X_D = 0.0
        
        #influent TKN (mgN/L), NOT IN InfC
        Inf_TKN = self._TNK
        #influent Ammonia-N (mgN/L), 
        Inf_S_NH = self._NH3
        #subdividing TKN into: 
        # a) nonbiodegradable TKN 
        NonBiodegradable_TKN_Ratio = 0.03 #TODO: need to be configurable
        #NON-BIODEGRADABLE TKN WILL HAVE TO BE ADDED BACK TO THE EFFLUENT TN
        Inf_nb_TKN = Inf_TKN * NonBiodegradable_TKN_Ratio
        Soluble_Biodegradable_OrgN_Ratio = Inf_S_S / (Inf_S_S + Inf_X_S)#Grady et al '99
        # b) soluble biodegrable TKN,     
        Inf_S_NS = (Inf_TKN - Inf_S_NH - Inf_nb_TKN) * Soluble_Biodegradable_OrgN_Ratio
        # c) particulate biodegradable TKN, 
        Inf_X_NS = (Inf_TKN - Inf_S_NH - Inf_nb_TKN) * \
                    (1.0 - Soluble_Biodegradable_OrgN_Ratio)
        
        #influent Nitrite + Nitrate (mgN/L), 
        Inf_S_NO = self._NO
        
        Inf_S_ALK = self._Alk
        
        Inf_S_DO = self._DO
        
        #store the converted information in the ASM Components for the influent
        self._InfComp = [Inf_X_I, Inf_X_S, Inf_X_BH, Inf_X_BA, Inf_X_D, \
                            Inf_S_I, Inf_S_S, -Inf_S_DO, Inf_S_NO, Inf_S_NH, \
                            Inf_S_NS, Inf_X_NS, Inf_S_ALK]
        
    def HasSidestream(self):
        ''' Check if the current unit has a sidestream discharge.
            Default = False, i.e. no sidestream
            Return type: boolean
        '''
        return False

    def SetFlow(self, Flow):
        if Flow >= 0.0:
            self._DesignFlow = Flow
        return self._DesignFlow
    
    def GetTSS(self):
        ''' Return the Total Suspsended Solids (TSS) in the unit '''
        return self._TSS

    def GetVSS(self):
        ''' Return the Volatile Suspended Solids (VSS) in the unit '''
        return self._VSS

    def GetTotalCOD(self):
        ''' Return the Total COD (both soluable and particulate) in the unit '''
        return self._InfComp[0] + self._InfComp[1] + self._InfComp[2] \
                + self._InfComp[3] + self._InfComp[4] + self._InfComp[5] \
                + self._InfComp[6]

    def GetSoluableCOD(self):
        ''' Return the SOLUABLE COD in the unit '''
        return self._InfComp[5] + self._InfComp[6]

    def GetParticulateCOD(self):
        ''' Return the PARTICULATE COD in the unit '''
        return self.GetTotalCOD() - self.GetSoluableCOD()
    
    def GetTN(self):
        ''' Return the Total Nitrogen of the unit '''
        return self._InfComp[8] + self._InfComp[9] \
                + self._InfComp[10] + self._InfComp[11]

    def GetParticulateN(self):
        ''' Return organic nitrogen of the unit '''
        return self._InfComp[11]

    def GetSoluableN(self):
        ''' Return soluable nitrogen of the unit '''
        return self.GetTN() - self.GetParticulateN()

    def GetOrganicN(self):
        ''' Return organic nitrogen of the unit '''
        return self._InfComp[10] + self._InfComp[11]

    def GetInorganicN(self):
        ''' Return inorganic nitrogen of the unit '''
        return self._InfComp[8] + self._InfComp[9] 

