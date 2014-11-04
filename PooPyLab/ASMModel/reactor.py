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
#This is the definition of ASMReactor object.
#
#Reactor dimensions, inlet_list, outlet_list, dissolved oxygen,
#and mass balance will be defined for the public interface
#
#Update Log: 
#May 26, 2014 KZ: Updated Definition
#December 17, 2013 KZ: Added/revised BlendComponents() definition.
#December 07, 2013 Kai Zhang


import asm, pipe
import constants

class ASMReactor(pipe.Pipe):
    __id = 0
    def __init__(self, ActiveVol=380.0, SWD=3.5, Temperature=20.0, DO=2.0, *args, **kw):
        #super(ASMReactor, self).__init__()
        pipe.Pipe.__init__(self) 
        self.__class__.__id += 1
        self.__name__ = "Reactor_" + str(self.__id)
        # SWD = side water depth in meters, default = ~12 ft
        # ActiveVol in m^3, default value equals to 100,000 gallons
        # Temperature = 20 C by default
        # DO = dissolved oxygen, default = 2.0 mg/L

        self._ActiveVol = ActiveVol
        self._SWD = SWD
        self._Area = self._ActiveVol / self._SWD

        # _ReactorInfComp[0]: Inf_X_I,
        # _ReactorInfComp[1]: Inf_X_S,
        # _ReactorInfComp[2]: Inf_X_BH,
        # _ReactorInfComp[3]: Inf_X_BA,
        # _ReactorInfComp[4]: Inf_X_D,
        # _ReactorInfComp[5]: Inf_S_I,
        # _ReactorInfComp[6]: Inf_S_S,
        # _ReactorInfComp[7]: -Inf_S_DO, COD = -DO
        # _ReactorInfComp[8]: Inf_S_NO,
        # _ReactorInfComp[9]: Inf_S_NH,
        # _ReactorInfComp[10]: Inf_S_NS,
        # _ReactorInfComp[11]: Inf_X_NS,
        # _ReactorInfComp[12]: Inf_S_ALK
        #
        self._ReactorInfComp = [0.0] * constants._NUM_ASM1_COMPONENTS

        # _Sludge is the core material the ASMReactor stores
        self._Sludge = asm.ASM1(Temperature, DO)
        
        # _ErrorTolerance is the max acceptable error for determining whether the simulation has converged.
        self._ErrorTolerance = 10E-4 # temporary number just to hold the place
        # _Converged is a flag to show convergence status
        self._Converged = False

        print self.__name__, " Initialized Successfully."
        return None

    def BlendComponents(self):
        '''
            BlendComponents() for ASMReactor is different from that for Base.
            Here it blends the contents from upstream and passes the mixture
            to the reactor's INLET, while to the OUTLET in Base.
            This is because the Base definition is used in non-reacting units
            like Pipe, Splitter, etc.
        '''
        for Index in range(constants._NUM_ASM1_COMPONENTS):
            tempComp = 0.0
            for unit in self._Inlet:
                tempComp += unit.GetEffComp()[Index] * unit.ReadFlow()
            self._ReactorInfComp[Index] = tempComp / self._TotalFlow

    def GetActiveVolume(self):
        return self._ActiveVol

    def GetEffComp(self):
        return self._EffComp

    def GetInfComp(self):
        return self._ReactorInfComp

    def GetASMParameters(self):
        return self._Sludge.GetParameters()

    def GetASMStoichiometrics(self):
        return self._Sludge.GetStoichiometrics()

    def UpdateCondition(self, Temperature, DO):
        self._Sludge.Update(Temperature, DO)
   
    def InitialGuess(self):
        #TODO: NEED TO PUT IN FIRST GUESS OF MODEL COMPONENTS HERE

        # store the initial guess as the current state of the reactor
        self._EffComp = self._PrevComp[:]
    
    def EstimateCurrentState(self):
        #First store the current componets received in the most recent iteration.
        self._PrevComp = self._EffComp[:]
        # Then get the components from the next iteration.
        self._EffComp = self._Sludge.SteadyStep(self._PrevComp, \
                                                        self._TotalFlow, \
                                                        self._ReactorInfComp,\
                                                        self._ActiveVol)


