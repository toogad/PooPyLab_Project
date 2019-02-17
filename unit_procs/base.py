#   This file is part of PooPyLab.
#
#    PooPyLab is a simulation software for biological wastewater treatment
#    processes using the International Water Association Activated Sludge md
#    Models.
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
#   Definition of the base class for WWTP components.
#
#   Update Log:
#   Jan 12, 2019 KZ: resumed and cleaned up
#   Feb 03, 2018 KZ: reviewed
#   Jul 21, 2017 KZ: made it more pythonic
#   Mar 21, 2017 KZ: Migrated to Python3
#   Jun 16, 2015 KZ: Removed Set(Get)PreFix(), Set(Get)Group();
#                       Renamed SetAs(Is)Done() to SetAs(Is)Visited()
#   Mar 20, 2015 KZ: Added Set(Get)PreFix(), Set(Get)Group(), 
#                       SetAs(Is)Done() for tracking status in loop finding
#   Nov 20, 2014 KZ: Added UpstreamConnected() and MainOutletConnected() 
#   Jun 29, 2014 KZ: Replace Interpret() with GetXXXX() functions
#   Jun 28, 2014 KZ: Added GetTSS(), getTotalCOD(), and getSoluableCOD()
#   Mar 15, 2014 KZ: Moved AddUpstreamUnit(), RemoveUpstreamUnit(), and 
#                       SetDownstreamMainUnit() to Pipe()
#   Mar 06, 2014 KZ: Re-wrote the common interface and change Base into an 
#                       abstract class
#   Dec 25, 2013 KZ: commented out the BlendComponent() function in 
#                       ReceiveFrom()
#   Dec 17, 2013 KZ: added _PrevComp[0:12] to store state variables from 
#                       previous iteration
#   Dec 07, 2013 Kai Zhang (KZ)



from abc import ABCMeta, abstractmethod 

class base(object):
    ''' 
    base() Object defines the common interfaces for all PooPyLab objects.
    '''
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_upstream(self):
        ''' Get the dict that stores all the upstream units that feed into
            current one
            Return Type: dict
        '''
        pass
    
    @abstractmethod
    def get_downstream_main(self):
        ''' Get the single unit downstream of the current one
            Return Type: base.Base
        '''
        pass

    @abstractmethod
    def totalize_flow(self):
        ''' Totalize all the flows entering the current unit.
            Return type: NO Return
        '''
        pass

    @abstractmethod
    def blend_components(self):
        '''
            blend_components() for Base mixes the contents in all inlet
            components and send to the OUTLET, assuming no reaction
            takes palce.
            The definition is changed in ASMReactor where the mixture
            is passed to the INLET of the reactor before reactions.
        '''
        pass
    
    @abstractmethod
    def update_combined_input(self):
        ''' Combined the flows and loads into the current unit'''
        pass

    @abstractmethod
    def get_outlet_flow(self):
        ''' Return the total out flow of the current unit (mainstream)
            Return value type: float/double
        '''
        pass

    @abstractmethod
    def get_outlet_concs(self):
        ''' Return the effluent concentrations of the current unit (mainstream)
            Return type: list
        '''
        pass
    
    @abstractmethod
    def discharge(self):
        ''' Pass the total flow and blended components to the next unit.
        '''
        pass

    @abstractmethod
    def has_sidestream(self):
        ''' Check if the current unit has a sidestream discharge.
            Default = False, i.e. no sidestream
            Return type: boolean
        '''
        pass
    
    @abstractmethod
    def get_TSS(self):
        pass

    @abstractmethod
    def get_VSS(self):
        pass

    @abstractmethod
    def get_total_COD(self):
        pass

    @abstractmethod
    def get_soluble_COD(self):
        pass

    @abstractmethod
    def get_particulate_COD(self):
        pass
    
    @abstractmethod
    def get_TN(self):
        pass

    @abstractmethod
    def get_particulate_N(self):
        pass

    @abstractmethod
    def get_soluble_N(self):
        pass

    @abstractmethod
    def get_organic_N(self):
        pass

    @abstractmethod
    def get_inorganic_N(self):
        pass

    @abstractmethod
    def has_discharger(self):
        ''' Return True if upstream is connected, False if not'''
        pass

    @abstractmethod
    def main_outlet_connected(self):
        ''' Return True if the downstream main outlet is connected,
            False if not.
        '''
        pass

    @abstractmethod
    def set_as_visited(self, Status):
        ''' Set the unit as True when done visiting it in the loop finding
            process. Status = False by default.
        '''
        pass

    @abstractmethod
    def is_visited(self):
        ''' Return True if the unit is labelled as visited, False otherwise '''
        pass

