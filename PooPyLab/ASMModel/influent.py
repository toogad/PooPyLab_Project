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
#    Definition of the plant Influent unit.
#
# Change Log:
#   July 31, 2017 KZ: Made it more pythonic and changed to python3.
#   June 16, 2015 KZ: Removed _prefix, _group status and 
#                       Set(Get)PreFixStatus(), Set(Get)GroupStatus;
#                       Renamed _Done to _visited, SetAs(Is)Done() to
#                       SetAs(Is)Visited().
#   March 20, 2015 KZ: Added _prefix, _group, _Done status and 
#                       Set(Get)PreFixStatus(), Set(Get)GroupStatus, 
#                       SetAs(Is)Done().
#   November 18, 2014 KZ: Added UpstreamConnected() and set to True
#   November 12, 2014 KZ: added _main_outlet_connected flag 
#                           and MainOutletConnected() function
#   October 19, 2014 KZ: removed test code
#   March 15, 2014: KZ: redefined for the new class structure.
#   December 07, 2013 Kai Zhang: first draft


import base, constants

class influent(base.base):
    __id = 0

    def __init__(self):
        self.__class__.__id += 1
        self.__name__ = "Influent_" + str(self.__id)

        # Store the influent characteristics in a list()
        # For ASM #1:
        #
        #    self._inf_comp[0]: X_I
        #    self._inf_comp[1]: X_S
        #    self._inf_comp[2]: X_BH
        #    self._inf_comp[3]: X_BA
        #    self._inf_comp[4]: X_D
        #    self._inf_comp[5]: S_I
        #    self._inf_comp[6]: S_S
        #    self._inf_comp[7]: S_DO
        #    self._inf_comp[8]: S_NO
        #    self._inf_comp[9]: S_NH
        #    self._inf_comp[10]: S_NS
        #    self._inf_comp[11]: X_NS
        #    self._inf_comp[12]: S_ALK
        self._inf_comp = [0.0] * constants._NUM_ASM1_COMPONENTS

        # Influent characteristics from user measurements/inputs
        # Setting default values for municipal wastewater in USA
        # Default Unit: mg/L except where noted differently
        self._BOD5 = 250.0
        self._TSS = 250.0
        self._VSS = 200.0
        self._TNK = 40.0
        self._NH3 = 28.0
        self._NO = 0.0
        self._TP = 10.0
        self._Alk = 6.0  # in mmol/L as CaCO3
        self._DO = 0.0 

        # Plant influent flow in M3/DAY
        # TODO: will be user-input from GUI. FROM THE GUI, USER
        #   will use MGD. DEFAULT VALUE = 10 MGD. 
        self._design_flow = 10 * 1000 / 3.78  # convert to M3/day

        # the reactor that receives the plant influent
        self._outlet = None
        
        # the status about whether there is a downstream unit
        self._main_outlet_connected = False

        # boolean on whether the unit is already visited by the loop
        # finding process
        self._prefix = False

        # _group is '' (empty string) if the unit has not been assigned to any
        #   specific group by the loop finding process.
        # If the unit is assigned to a group, _group will record the group ID.
        #TODO: IS THIS STILL USED AT ALL?
        self._group = ''

        # boolean on whether the loop finding process has finished
        #   analyzing the unit
        self._visited = False
        
        print self.__name__,' initialized successfully.'

    def get_upstream_units(self):
        ''' Get the {} that stores all the upstream units that feed into
            the current one
            Return Type: None (for Influent) or dict (for others)
        '''
        return None

    def set_downstream_main_unit(self, rcvr):
        ''' Set the downstream unit that will receive effluent from 
            the current unit
        '''
        if self._outlet != rcvr: #if the specified rcvr has not been added
            self._outlet = rcvr 
            self._main_outlet_connected = True
            if rcvr != None:
                rcvr.add_upstream_unit(self)
    
    def upstream_connected(self):
        '''Placeholder, always return True for Influent as it 
            doesn't need an upstream unit
        '''
        return True
    
    def main_outlet_connected(self):
        ''' Return the status of outlet connection'''
        return self._main_outlet_connected

    def get_downstream_main_unit(self):
        ''' Get the single unit downstream of the current one
            Return Type: base.Base
        '''
        return self._outlet

    def set_as_visited(self, status=False):
        self._visited = status

    def is_visited(self):
        return self._visited
    
    def totalize_flow(self):
        ''' Totalize all the flows entering the current unit.
            Return type: NO Return
            Does nothing for Influent object as the flow is fixed.
        '''
        pass

    def blend_components(self):
        '''
            blend_components() for Base mixes the contents in all inlet
            components and send to the OUTLET, assuming no reaction
            takes palce.
            The definition is changed in ASMReactor where the mixture
            is passed to the INLET of the reactor before reactions.
            Does nothing for Inlfuent object as the components are in a 
            single source.
        '''
        pass
    
    def update_combined_input(self):
        ''' Combined the flows and loads into the current unit
            Doesn't need to do anything since Influent object does not 
            receive any upstream input.
        '''
        pass

    def get_outlet_flow(self):
        ''' Return the total out flow of the current unit (mainstream)
        '''
        return self._design_flow

    def get_outlet_concs(self):
        ''' Return the effluent concentrations of the current unit (mainstream)
        '''
        return self._inf_comp

    def discharge(self):
        ''' Pass the total flow and blended components to the next unit.
        '''
        if self._outlet != None:
            self.get_downstream_main_unit().update_combined_input()
    
    def receive_from(self, dschgr=None):
        ''' Influent doesn't need to receive anything'''
        pass

    def interpret(self):
        ''' Convert user input parameters into the ones that the ASM model
            can understand
        '''
        #TODO: the first set of conversion available here is for municipal 
        #   wastewater. Industrial wastewater may have completely different
        #   conversion factors and needs to be tested.
        
        # influent biodegradable COD, BOD/COD = 1.71 for typ. muni.WW
        Inf_CODb = self._BOD5 * 1.71
        # influent total COD, COD/BOD5 = 2.04 per BioWin
        Inf_CODt = self._BOD5 * 2.04
        # influent total innert COD, 
        Inf_CODi = Inf_CODt - Inf_CODb
        # influent soluble innert COD
        Inf_S_I = 0.13 * Inf_CODt
        # influent particulate innert COD
        Inf_X_I = Inf_CODi - Inf_S_I
        # influent particulate biodegradable COD
        Inf_X_S = 1.6 * self._VSS - Inf_X_I
        # influent soluble biodegradable COD
        Inf_S_S = Inf_CODb - Inf_X_S
        # influent Heterotrophs (mgCOD/L), 
        Inf_X_BH = 0.0
        # influent Autotrophs (mgCOD/L), 
        Inf_X_BA = 0.0
        # influent Biomass Debris (mgCOD/L)
        Inf_X_D = 0.0
        
        # influent TKN (mgN/L), NOT IN InfC
        Inf_TKN = self._TNK
        # influent Ammonia-N (mgN/L), 
        Inf_S_NH = self._NH3
        # subdividing TKN into: 
        #  a) nonbiodegradable TKN 
        NonBiodegradable_TKN_Ratio = 0.03 # TODO: need to be configurable
        # NON-BIODEGRADABLE TKN WILL HAVE TO BE ADDED BACK TO THE EFFLUENT TN
        Inf_nb_TKN = Inf_TKN * NonBiodegradable_TKN_Ratio
        #  Grady 1999:
        Soluble_Biodegradable_OrgN_Ratio = Inf_S_S / (Inf_S_S + Inf_X_S)
        #  b) soluble biodegrable TKN,     
        Inf_S_NS = (Inf_TKN - Inf_S_NH - Inf_nb_TKN)\
                    * Soluble_Biodegradable_OrgN_Ratio
        #  c) particulate biodegradable TKN
        Inf_X_NS = (Inf_TKN - Inf_S_NH - Inf_nb_TKN)\
                    * (1.0 - Soluble_Biodegradable_OrgN_Ratio)
        
        # influent Nitrite + Nitrate (mgN/L)
        Inf_S_NO = self._NO
        
        Inf_S_ALK = self._Alk
        
        Inf_S_DO = self._DO
        
        #store the converted information in the ASM Components for the influent
        self._inf_comp = [Inf_X_I, Inf_X_S, Inf_X_BH, Inf_X_BA, Inf_X_D, \
                            Inf_S_I, Inf_S_S, -Inf_S_DO, Inf_S_NO, Inf_S_NH, \
                            Inf_S_NS, Inf_X_NS, Inf_S_ALK]
        
    def has_sidestream(self):
        ''' Check if the current unit has a sidestream discharge.
            Default = False, i.e. no sidestream
            Return type: boolean
        '''
        return False

    def set_flow(self, flow):
        if flow >= 0.0:
            self._design_flow = flow
        return self._design_flow
    
    def get_TSS(self):
        ''' Return the Total Suspsended Solids (TSS) in the unit '''
        return self._TSS

    def get_VSS(self):
        ''' Return the Volatile Suspended Solids (VSS) in the unit '''
        return self._VSS

    def get_total_COD(self):
        ''' Return the Total COD (both soluable and particulate) in the unit'''
        return self._inf_comp[0] + self._inf_comp[1] + self._inf_comp[2] \
                + self._inf_comp[3] + self._inf_comp[4] + self._inf_comp[5] \
                + self._inf_comp[6]

    def get_soluble_COD(self):
        ''' Return the SOLUABLE COD in the unit '''
        return self._inf_comp[5] + self._inf_comp[6]

    def get_particulate_COD(self):
        ''' Return the PARTICULATE COD in the unit '''
        return self.get_total_COD() - self.get_soluble_COD()
    
    def get_TN(self):
        ''' Return the Total Nitrogen of the unit '''
        return self._inf_comp[8] + self._inf_comp[9] \
                + self._inf_comp[10] + self._inf_comp[11]

    def get_particulate_N(self):
        ''' Return organic nitrogen of the unit '''
        return self._inf_comp[11]

    def get_soluble_N(self):
        ''' Return soluable nitrogen of the unit '''
        return self.get_TN() - self.get_particulate_N()

    def get_organic_N(self):
        ''' Return organic nitrogen of the unit '''
        return self._inf_comp[10] + self._inf_comp[11]

    def get_inorganic_N(self):
        ''' Return inorganic nitrogen of the unit '''
        return self._inf_comp[8] + self._inf_comp[9] 

