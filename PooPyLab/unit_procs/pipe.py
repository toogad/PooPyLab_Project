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
# This is the definition of the "pipe" class.
#
# Update Log:
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


from unit_procs.base import base
from ASMModel import constants

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
        ''' Connect current unit to the specified branch of the upstream unit
        '''
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
            self.get_downstream_main().update_combined_input()
    

    def has_discharger(self):
        ''' Get the status of upstream connection'''
        return self._has_discharger


    def main_outlet_connected(self):
        ''' Get the status of downstream main connection'''
        return self._main_outlet_connected


    def set_as_visited(self, status=False):
        self._visited = status


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

