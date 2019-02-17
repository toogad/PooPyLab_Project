# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
#    
#    Copyright (C) Kai Zhang
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
# This file defines the following classes related to streams:
#       pipe, influent, effluent, splitter, WAS.
#
# ----------------------------------------------------------------------------


from unit_procs.base import base
from ASMModel import constants


# ----------------------------------------------------------------------------
# pipe class - Change Log:
# 20190209 KZ: standardized import
#   Jan 12, 2019 KZ: resume and cleaned up
#   Jul 28, 2017 KZ: made it more pythonic
#   Mar 21, 2017 KZ: Migrated to Python3
#   Jun 24, 2015 KZ: Updated AddUpstreamUnit() to differential main/side 
#   Jun 16, 2015 KZ: Removed _PreFix, _Group status and 
#                       Set(Get)PreFixStatus(), Set(Get)GroupStatus.
#                       Renamed _Done to _visited, SetAs(Is)Visited() to
#                       SetAs(Is)Visited()
#   Mar 20, 2015 KZ: Added _PreFix, _Group, _Done status and 
#                       Set(Get)PreFixStatus(), Set(Get)GroupStatus, 
#                       SetAs(Is)Done().
#   Nov 24, 2014 KZ: revised RemoveUpstreamUnit() to be able to remove units
#                       with sidestream
#   Nov 23, 2014 KZ: revised RemoveUpstreamUnit() to check availability to the
#                       upstream unit specified
#   Nov 12, 2014 KZ: added: _has_discharger and _MainOutletConnected flags;
#                       UpstreamConnected() and MainOutletConnected() functions
#   Sep 26, 2014 KZ: removed test code
#   Jun 29, 2014 KZ: Added GetXXX() definitions for solids and COD summary. 
#   Mar 15, 2014 KZ: AddUpstreamUnit(), RemoveUpstreamUnit(), and
#                       SetDownstreamMainUnit() begin here
#   Mar 08, 2014 KZ: Rewrite according to the new class structure
#   Dec 07, 2013 Kai Zhang

class pipe(base):
    __id = 0

    def __init__(self):
        self.__class__.__id += 1
        self.__name__ = 'Pipe_' + str(self.__id)
                
        # _inlet store the upstream units and their flow contribution
        # in the format of {unit, Flow}
        self._inlet = {}
        
        # a SINGLE unit that receives all the flows from the
        # current unit
        self._main_outlet = None #By default this is the MAIN OUTLET.
        
        # flag to indicate whether there are upstream units
        self._has_discharger = False

        # flag to indicate whether there are units in MAIN downstream
        self._main_outlet_connected = False

        # the Total Inflow, which is the same as the outflow for a pipe obj.
        self._total_flow = 0         
        
        # flag to indicate whether _total_flow has been updated
        self._flow_totalized = False

        # flag to indicate whether _eff_comps[] have been blended
        self._components_blended = False

        # flag on whether the loop finding process has finished
        #   analyzing the unit
        self._visited = False

        #  THIS IS WHERE THE CURRENT STATE OF THE UNIT IS STORED:
        self._eff_comps = [0] * constants._NUM_ASM1_COMPONENTS
        # _eff_comps[0]: X_I,
        # _eff_comps[1]: X_S,
        # _eff_comps[2]: X_BH,
        # _eff_comps[3]: X_BA,
        # _eff_comps[4]: X_D,
        # _eff_comps[5]: S_I,
        # _eff_comps[6]: S_S,
        # _eff_comps[7]: -S_DO, COD = -DO
        # _eff_comps[8]: S_NO,
        # _eff_comps[9]: S_NH,
        # _eff_comps[10]: S_NS,
        # _eff_comps[11]: X_NS,
        # _eff_comps[12]: S_ALK

        print(self.__name__,' initialized successfully.')
        return None


    def add_upstream(self, discharger, branch='Main'): 
        #Connect current unit to the specified branch of the upstream unit
        if discharger not in self._inlet:
            # Setting the flow to 0.0 is a place-holder when setting up
            # the Process Flow Diagram, because the actual total flow from
            # upstream unit may not have been completely configured. The
            # self.discharge() method of the upstream unit will totalize the
            # flow and blend the components before passing them into the
            # current unit.
            self._inlet[discharger] = 0.0
            self._flow_totalized = self._components_blended = False
            self._has_discharger = True
            if branch == 'Main':
                discharger.set_downstream_main(self)
            elif branch == 'Side':
                discharger.set_downstream_side(self)
            else:
                print("ERROR: UNKNOWN BRANCH SPECIFIED.")
        return None


    def remove_upstream(self, discharger):
        if discharger in self._inlet:
            self._inlet.pop(discharger)
            if discharger.get_downstream_main() == self:
                discharger.set_downstream_main(None)
            else:
                discharger.set_downstream_side(None)
            self._flow_totalized = self._components_blended = False
            self._has_discharger = len(self._inlet) > 0
        else:
            print('ERROR: UPSTREAM UNIT NOT FOUND')
        return None


    def set_downstream_main(self, receiver):
        ''' Set the mainstream unit that will receive effluent from the
            current unit
        '''
        if self._main_outlet != receiver:  # if the receiver hasn't been added
            self._main_outlet = receiver
            self._main_outlet_connected = receiver != None
            if receiver != None:
                receiver.add_upstream(self)
        return None


    def get_upstream(self):
        return self._inlet


    def get_downstream_main(self):
        return self._main_outlet


    def totalize_flow(self):
        ''' Totalize all the flows entering the current unit.
        '''
        self._total_flow = sum(self._inlet.values())
        self._flow_totalized = True
        return None


    def blend_components(self):
        '''
            blend_components() for Base mixes the contents in all inlet
            components and send to the OUTLET, assuming no reaction
            takes palce.
            The definition is changed in ASMReactor where the mixture
            is passed to the INLET of the reactor before reactions.
        '''
        if self._flow_totalized == False:
            self.totalize_flow()
        if self._total_flow:
            for index in range(constants._NUM_ASM1_COMPONENTS):
                temp = 0
                for unit in self._inlet:
                    temp += unit.get_outlet_concs()[index] \
                            * unit.get_outlet_flow()
                self._eff_comps[index] = temp / self._total_flow
        self._components_blended = True
        return None
    

    def update_combined_input(self):
        ''' Combined the flows and loads into the current unit'''
        if self._flow_totalized == False:
            self.totalize_flow()
        if self._components_blended == False:
            self.blend_components()
        return None
    

    def get_outlet_flow(self):
        ''' Return the total out flow of the current unit (mainstream)
        '''
        if self._flow_totalized == False:
            self.totalize_flow()
        return self._total_flow
    

    def get_outlet_concs(self):
        ''' Return the effluent concentrations of the current unit (mainstream)
        '''
        if self._components_blended == False:
            self.blend_components()
        return self._eff_comps.copy()
    

    def discharge(self):
        ''' Pass the total flow and blended components to the next unit.
        '''
        self.update_combined_input()
        if self._main_outlet != None:
            #TODO: need to make sure the downstream unit get the current
            #  unit's info 
            m = self.get_downstream_main()
            m.set_flow(self, self._total_flow)
            m.update_combined_input()
        return None
    

    def has_discharger(self):
        ''' Get the status of upstream connection'''
        return self._has_discharger


    def main_outlet_connected(self):
        ''' Get the status of downstream main connection'''
        return self._main_outlet_connected


    def set_flow(self, dschgr, flow):
        if dschgr in self._inlet and flow >= 0:
            self._inlet[dschgr] = flow
            self._flow_totalized = False
        return None


    def set_as_visited(self, status=False):
        self._visited = status
        return None


    def is_visited(self):
        return self._visited


    def _sum_helper(self, index_list=[]):
        ''' sum up the model components indicated by the index_list'''
        sum = 0.0
        for element in index_list:
            sum += self._eff_comps[element]
        return sum


    def get_TSS(self):
        #TODO: need to make COD/TSS = 1.2 changeable for different type of
        # sludge
        index_list = [0, 1, 2, 3, 4]
        return self._sum_helper(index_list) / 1.2


    def get_VSS(self):
        #TODO: need to make COD/VSS = 1.42 changeable for diff. type of sludge
        index_list = [0, 1, 2, 3, 4]
        return self._sum_helper(index_list) / 1.42
    

    def get_total_COD(self):
        index_list = [0, 1, 2, 3, 4, 5, 6]
        return self._sum_helper(index_list)


    def get_soluble_COD(self):
        index_list = [5, 6]
        return self._sum_helper(index_list)


    def get_particulate_COD(self):
        return self.GetTotalCOD - self.getSoluableCOD()


    def get_TN(self):
        index_list = [8, 9, 10, 11]
        return self._sum_helper(index_list)


    def get_organic_N(self):
        index_list = [10, 11]
        return self._sum_helper(index_list)


    def get_inorganic_N(self):
        index_list = [8, 9]
        return self._sum_helper(index_list)


    def get_particulate_N(self):
        return self._eff_comps[11]


    def get_soluble_N(self):
        return self.GetTN() - self.getParticulateN()


    def has_sidestream(self):
        return False  # always False for a pipe


# -----------------------------------------------------------------------------
# influent class - Change Log:
# 20190209 KZ: standardized import
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

class influent(base):
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

        # prefix that leads to current unit, used by the loop
        # finding process
        self._prefix = False

        # _group is '' (empty string) if the unit has not been assigned to any
        #   specific group by the loop finding process.
        # If the unit is assigned to a group, _group will record the group ID.
        #TODO: IS THIS STILL USED AT ALL?
        self._group = ''

        self._visited = False
        
        print(self.__name__,' initialized successfully.')
        return None


    def get_upstream(self):
        ''' Get the {} that stores all the upstream units that feed into
            the current one
            Return Type: None (for Influent) or dict (for others)
        '''
        return None


    def set_downstream_main(self, rcvr):
        ''' Set the downstream unit that will receive effluent from 
            the current unit
        '''
        if isinstance(rcvr, influent):  # None is allowed as a place holder
            print("ERROR: WRONG RECEIVER GIVEN TO INFLUENT")
            return None
        if rcvr == None:
            self._outlet = None
            self._main_outlet_connected = False
        elif self._outlet != rcvr:
            self._outlet = rcvr 
            self._main_outlet_connected = True
            rcvr.add_upstream(self)
        return None
    

    def has_discharger(self):
        '''Placeholder, always return True for Influent as it 
            doesn't need an upstream unit
        '''
        return True
    

    def main_outlet_connected(self):
        ''' Return the status of outlet connection'''
        return self._main_outlet_connected


    def get_downstream_main(self):
        ''' Get the single unit downstream of the current one
            Return Type: base.Base
        '''
        return self._outlet


    def set_as_visited(self, status=False):
        self._visited = status
        return None


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
            m = self.get_downstream_main()
            m.set_flow(self, self._design_flow)
            m.update_combined_input()
        return None
    

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

        return None


    def has_sidestream(self):
        ''' Check if the current unit has a sidestream discharge.
            Default = False, i.e. no sidestream
            Return type: boolean
        '''
        return False


    def set_flow(self, flow):
        if flow >= 0:
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


# -----------------------------------------------------------------------------
# effluent class - Change Log: 
# 20190209 KZ: standardized import
# Jul 30, 2017 KZ: Made it more pythonic.
# Mar 21, 2017 KZ: Migrated to Python3
# Sep 26, 2014 KZ: removed test code   
# July 2, 2014 KZ: change base class to Pipe.
# June 29, 2014 KZ: removed Convert() that converts model parameters for
#                   user parameters
# December 25, 2013 KZ: commented out the BlendComponent() function in
#                       ReceiveFrom()
# December 17, 2013 KZ: Added _PrevComp[0..12] to store state variables from 
#                       previous iteration
#
# December 07, 2013 Kai Zhang
    

class effluent(pipe):
    __id = 0

    def __init__(self):
        pipe.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "Effluent_" + str(self.__id)
        self._main_outlet_connected = True  # dummy
        print(self.__name__, "initialized successfully.")
        return None


# -----------------------------------------------------------------------------
# splitter class - Change Log:
# 20190209 KZ: standardized import
# Feb 09, 2019 KZ: revised set_downstream_side()
# Jul 30, 2017 KZ: pythonic style
# Mar 21, 2017 KZ: Migrated to Python3
# Jun 24, 2015 KZ: Updated SetDownstreamSideUnit() to differential main/side
# Jun 23, 2015 KZ: Rewrote sidestream to eliminate Branch class
# Jun 18, 2015 KZ: Removed _PreFix and _Group status and 
#                     Set(Get)PreFixStatus(), Set(Get)GroupStatus;
#                     Renamed _Done to _Visited and SetAs(Is)Done() to
#                     SetAs(Is)Visited()
# Mar 20, 2015 KZ: Added _PreFix, _Group, _Done status and 
#                     Set(Get)PreFixStatus(), Set(Get)GroupStatus, 
#                     SetAs(Is)Done().
# Nov 18, 2014 KZ: renamed "SideStream" into "Sidestream";
#                         Added _SidestreamConnected and SideOutletConnected()
# Sep 26, 2014 KZ: fixed pipe.Pipe.__init__
# Apr 27, 2014 KZ: Change the sidestream class from Influent() to Sidestream()
# Apr 18, 2014 KZ: Rewrite definition based on the new class system structure
# Dec 25, 2013 KZ: commented out the BlendComponent() function in ReceiveFrom()
# Dec 07, 2013
#


class splitter(pipe):

    __id = 0

    def __init__(self):
        pipe.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "Splitter_" + str(self.__id)

        # the main outlet is defined in pipe.pipe as _main_outlet
        # therefore add the _side_outlet only here.
        self._side_outlet = None
        
        self._main_outlet_flow = 0
        self._side_outlet_flow = 0
        
        self._side_outlet_connected = False

        self._SRT_controller = False

        print(self.__name__, "initialized successfully.")

        return None
    

    def is_SRT_controller(self):
        ''' Mark the splitter whether it controls the plant's Solids Retention
            Time.
            Default value: False
        '''
        return self._SRT_controller


    def set_as_SRT_controller(self, setting=False):
        self._SRT_controller = setting
        #TODO: HOW DOES THIS IMPACT WAS FLOW BASED ON USER SPECIFIED SRT?
        return None


    def set_sidestream_flow(self, flow):
        self._side_outlet_flow = flow
        #TODO: Need to be able to dynamically update the sidestream flow
        return None
    

    def totalize_flow(self):
        self._total_flow = sum(self._inlet.values())
        #TODO: Need to pay attention to the flow balance below during runtime
        #TODO: Need to check: _main_outlet_flow > 0?
        self._main_outlet_flow = self._total_flow - self._side_outlet_flow
        self._flow_totalized = True
        return None


    def set_downstream_side(self, rcvr):
        if isinstance(rcvr, influent):
            print("ERROR: WRONG RECEIVER GIVEN TO SIDESTREAM")
            return None
        if self._side_outlet != rcvr:
            self._side_outlet = rcvr
            self._side_outlet_connected = rcvr != None
            if rcvr != None:
                rcvr.add_upstream(self, "Side")
        return None
                

    def get_downstream_side(self):
        return self._side_outlet


    def discharge(self):
        ''' Pass the total flow and blended components to the next unit.
            Both mainstream and sidestream units shall receive their flows 
            and component concentratons.
        '''
        self.update_combined_input()
        if self._main_outlet != None and self.set_sidestream_flow != None:
            m = self.get_downstream_main()
            m.set_flow(self, self._main_outlet_flow)
            m.update_combined_input()
            s = self.get_downstream_side()
            s.set_flow(self, self._side_outlet_flow)
            s.update_combined_input() 
        else:
            print("ERROR: ", self.__name__, "downstream unit setup incomplete")
        return None


    def has_sidestream(self):
        return True  # always True for a splitter


    def side_outlet_connected(self):
        return self._side_outlet_connected


    def set_as_visited(self, status=False):
        self._visited = status
        return None


    def is_visited(self):
        return self._visited
 
    #def GetWAS(self, WWTP, TargetSRT): 
    #    '''Get the mass of DRY solids to be wasted (WAS) in KiloGram'''
    #    #WWTP is a list that stores all the process units
    #    TotalSolids = 0.0 #as TSS in KiloGram
    #    if self._SRTController:
    #        for unit in WWTP:
    #            if isinstance(unit, ASMReactor):
    #                TotalSolids += unit.GetTSS() \
    #                               * unit.GetActiveVolume() / 1000.0
    #    if TargetSRT > 0:
    #        return TotalSolids / TargetSRT
    #    else:
    #        print("Error in Target SRT <=  0 day; GetWAS() returns 0.")
    #        return 0;


# ------------------------------------------------------------------------------
# WAS class - Change Log:
# 20190209 KZ: standardized import
# Jul 30, 2017 KZ: made code more pythonic
# Mar 21, 2017 KZ: Migrated to Python3
# Sep 26, 2014 KZ: Change inheritance back from Splitter to Effluent
# Aug 25, 2014 KZ: Added InformSRTController function.
# Aug 23, 2014 KZ: Changed its inheritance to Effluent;
#                  Added variables and functions for WAS Flow calculation
# December 06, 2013 Kai Zhang: Initial design

    
class WAS(effluent): 
    __id = 0
    def __init__(self):
        
        effluent.__init__(self)
        self.__class__.__id += 1
        self.__name__ = 'WAS_' + str(self.__id)
        self._WAS_flow = 0.0  # Unit: m3/d 
        print(self.__name__,' initialized successfully.')
        return None


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
        self._WAS_flow = self.get_solids_inventory(reactor_list) * 1000 \
                        / SRT / self.get_TSS()
        #TODO: in MAIN function, we need to check whether the WAS flow
        # is higher than the influent flow
        return self._WAS_flow


    def inform_SRT_controller(self):
        ''' Pass the WAS Flow to the upstream SRT Controlling Splitter '''
        upstream = self.get_upstream().keys()
        if len(upstream) == 1 \
                and isinstance(upstream[0], splitter):
            if upstream[0].is_SRT_controller():
                upstream[0].setup_sidestream(self, self.get_WAS_flow())
                upstream[0].totalize_flow()
                upstream[0].discharge()  #TODO: IS THIS NEEDED??
            else:
                print("The unit upstream of WAS is not SRT controlling")
        else:
            print("Check the unit upstream of WAS. \
                    There shall be a splitter only")
        return None

