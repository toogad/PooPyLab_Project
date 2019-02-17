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
# This is the definition of asm_reactor class. 
# 
# Reactor dimensions, inlet_list, outlet_list, dissolved oxygen,
# and mass balance will be defined for the public interface
# 
# Update Log: 
# 20190209 KZ: standardized import
# July 30, 2017 KZ: more pythonic style
# March 21, 2017 KZ: Migrated to Python3
# May 26, 2014 KZ: Updated Definition
# December 17, 2013 KZ: Added/revised blend_components() definition.
# December 07, 2013 Kai Zhang


from unit_procs.pipe import pipe
from ASMModel.asm_1 import ASM_1
from ASMModel import constants

class asm_reactor(pipe):
    __id = 0
    def __init__(self, ActiveVol=380, swd=3.5, \
                    Temperature=20, DO=2, *args, **kw):
        pipe.__init__(self) 
        self.__class__.__id += 1
        self.__name__ = "Reactor_" + str(self.__id)
        # swd = side water depth in meters, default = ~12 ft
        # ActiveVol in m^3, default value equals to 100,000 gallons
        # Temperature = 20 C by default
        # DO = dissolved oxygen, default = 2.0 mg/L

        self._active_vol = ActiveVol
        self._swd = swd
        self._area = self._active_vol / self._swd

        # _reactor_inf_comps[0]: Inf_X_I,
        # _reactor_inf_comps[1]: Inf_X_S,
        # _reactor_inf_comps[2]: Inf_X_BH,
        # _reactor_inf_comps[3]: Inf_X_BA,
        # _reactor_inf_comps[4]: Inf_X_D,
        # _reactor_inf_comps[5]: Inf_S_I,
        # _reactor_inf_comps[6]: Inf_S_S,
        # _reactor_inf_comps[7]: -Inf_S_DO, COD = -DO
        # _reactor_inf_comps[8]: Inf_S_NO,
        # _reactor_inf_comps[9]: Inf_S_NH,
        # _reactor_inf_comps[10]: Inf_S_NS,
        # _reactor_inf_comps[11]: Inf_X_NS,
        # _reactor_inf_comps[12]: Inf_S_ALK
        #
        self._reactor_inf_comps = [0] * constants._NUM_ASM1_COMPONENTS

        # the core material the ASMReactor stores
        self._sludge = ASM_1(Temperature, DO)
        
        # the max acceptable error for determining whether the simulation has converged.
        self._error_tolerance = 1E-4 # temporary number just to hold the place
        # a boolean flag to show convergence status
        self._converged = False

        # model components from the previous round
        self._pre_eff_comps = []

        print(self.__name__, " Initialized Successfully.")
        return None


    def blend_components(self):
        '''
            blend_components() for ASMReactor is different from that for Base.
            Here it blends the contents from upstream and passes the mixture
            to the reactor's INLET, while to the OUTLET in Base.
            This is because the Base definition is used in non-reacting units
            like Pipe, Splitter, etc.
        '''
        for index in range(constants._NUM_ASM1_COMPONENTS):
            temp = 0
            for unit in self._inlet:
                temp += unit.get_eff_comps()[index] * unit.get_outlet_flow()
            self._reactor_inf_comps[index] = temp / self._total_flow
            #TODO: how do we handle the _components_blended flag here?
        return None


    def get_active_vol(self):
        return self._active_vol


    def get_eff_comps(self):
        return self._eff_comps


    def get_inf_comps(self):
        return self._reactor_inf_comp


    def get_ASM_params(self):
        return self._sludge.get_params()


    def get_ASM_stoichs(self):
        return self._sludge.get_stoichs()

    def update_condition(self, Temperature, DO):
        self._sludge.update(Temperature, DO)
        return None

   
    def initial_guess(self):
        #TODO: NEED TO PUT IN FIRST GUESS OF MODEL COMPONENTS HERE

        # store the initial guess as the current state of the reactor
        self._eff_comps = self._pre_eff_comps[:]

    
    def estimate_current_state(self):
        # store the current componets received in the most recent iteration.
        self._pre_eff_comps = self._eff_comps[:]
        # get the components from the next iteration.
        self._eff_comps = self._sludge.steady_step(self._pre_eff_comps, \
                                                    self._total_flow, \
                                                    self._reactor_inf_comp, \
                                                    self._active_vol)

