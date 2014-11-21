#   This file is part of PooPyLab.
#
#    PooPyLab is a simulation software for biological wastewater treatment
#    processes using the International Water Association Activated Sludge Models.
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
#   Definition of the Base object for WWTP components such as
#   reactors.
#
#   Update Log:
#   November 20, 2014 KZ: Added UpstreamConnected() and MainOutletConnected() 
#   June 29, 2014 KZ: Replace Interpret() with GetXXXX() functions
#   June 28, 2014 KZ: Added GetTSS(), getTotalCOD(), and getSoluableCOD()
#   March 15, 2014 KZ: Moved AddUpstreamUnit(), RemoveUpstreamUnit(), and SetDownstreamMainUnit() to Pipe()
#   March 06, 2014 KZ: Re-wrote the common interface and change Base into an abstract class
#   December 25, 2013 KZ: commented out the BlendComponent() function in ReceiveFrom()
#   December 17, 2013 KZ: added _PrevComp[0:12] to store state variables from previous iteration
#   December 07, 2013 Kai Zhang (KZ)



from abc import ABCMeta, abstractmethod 

class Base(object):
    ''' 
    Base() Object defines the common interfaces for all PooPyLab objects.
    '''

    
    __metaclass__ = ABCMeta

    @abstractmethod
    def GetUpstreamUnits(self):
        ''' Get the dict that stores all the upstream units that feed into current one
            Return Type: dict
        '''
        pass
    
    @abstractmethod
    def GetDownstreamMainUnit(self):
        ''' Get the single unit downstream of the current one
            Return Type: base.Base
        '''
        pass

    @abstractmethod
    def TotalizeFlow(self):
        ''' Totalize all the flows entering the current unit.
            Return type: NO Return
        '''
        pass

    @abstractmethod
    def BlendComponents(self):
        '''
            BlendComponents() for Base mixes the contents in all inlet
            components and send to the OUTLET, assuming no reaction
            takes palce.
            The definition is changed in ASMReactor where the mixture
            is passed to the INLET of the reactor before reactions.
        '''
        pass
    
    @abstractmethod
    def UpdateCombinedInput(self):
        ''' Combined the flows and loads into the current unit'''
        pass

    @abstractmethod
    def GetOutletFlow(self):
        ''' Return the total out flow of the current unit (mainstream)
            Return value type: float/double
        '''
        pass

    @abstractmethod
    def GetOutletConcentrations(self):
        ''' Return the effluent concentrations of the current unit (mainstream)
            Return type: list
        '''
        pass
    
    @abstractmethod
    def Discharge(self):
        ''' Pass the total flow and blended components to the next unit.
        '''
        pass

    #@abstractmethod
    #def Interpret(self):
    #    ''' Convert user input to model components'''
        #for example, user may input BOD, TSS, VSS, TKN etc. this function
        #coverts those into influent model components for the solver
    #    pass
    
    @abstractmethod
    def HasSidestream(self):
        ''' Check if the current unit has a sidestream discharge.
            Default = False, i.e. no sidestream
            Return type: boolean
        '''
        pass
    
    @abstractmethod
    def GetTSS(self):
        ''' Return the Total Suspsended Solids (TSS) in the unit '''
        pass

    @abstractmethod
    def GetVSS(self):
        ''' Return the Volatile Suspended Solids (VSS) in the unit '''
        pass

    @abstractmethod
    def GetTotalCOD(self):
        ''' Return the Total COD (both soluable and particulate) in the unit '''
        pass

    @abstractmethod
    def GetSoluableCOD(self):
        ''' Return the SOLUABLE COD in the unit '''
        pass

    @abstractmethod
    def GetParticulateCOD(self):
        ''' Return the PARTICULATE COD in the unit '''
        pass
    
    @abstractmethod
    def GetTN(self):
        ''' Return the Total Nitrogen of the unit '''
        pass

    @abstractmethod
    def GetParticulateN(self):
        ''' Return organic nitrogen of the unit '''
        pass

    @abstractmethod
    def GetSoluableN(self):
        ''' Return soluable nitrogen of the unit '''
        pass

    @abstractmethod
    def GetOrganicN(self):
        ''' Return organic nitrogen of the unit '''
        pass

    @abstractmethod
    def GetInorganicN(self):
        ''' Return inorganic nitrogen of the unit '''
        pass

    @abstractmethod
    def UpstreamConnected(self):
        ''' Return True if upstream is connected, False if not'''
        pass

    @abstractmethod
    def MainOutletConnected(self):
        ''' Return True if the downstream main outlet is connected,
            False if not.
        '''
        pass
