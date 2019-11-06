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
# This is the definition of class related to biological processes. 
# 
# ----------------------------------------------------------------------------


from unit_procs.streams import pipe
from ASMModel.asm_1 import ASM_1
from ASMModel import constants


# ----------------------------------------------------------------------------

class asm_reactor(pipe):
    __id = 0

    def __init__(self, ActiveVol=38000, swd=3.5,
                    Temperature=20, DO=2, *args, **kw):
        # swd = side water depth in meters, default = ~12 ft
        # ActiveVol in m^3, default value equals to 100,000 gallons
        # Temperature = 20 C by default
        # DO = dissolved oxygen, default = 2.0 mg/L

        pipe.__init__(self) 
        self.__class__.__id += 1
        self.__name__ = "ASMReactor_" + str(self.__id)

        self._type = "ASMReactor"

        self._active_vol = ActiveVol
        self._swd = swd
        self._area = self._active_vol / self._swd

        self._sludge = ASM_1(Temperature, DO)

        self._in_comps = [0.0] * constants._NUM_ASM1_COMPONENTS 
        self._mo_comps = [0.0] * constants._NUM_ASM1_COMPONENTS

        # results of previous round
        self._prev_mo_comps = [0.0] * constants._NUM_ASM1_COMPONENTS
        self._prev_so_comps = self._prev_mo_comps

        self._upstream_set_mo_flow = True

        # scalar used for controlling integration step size in RKF45 method
        self._scalar = 1.0  # initial guess

        # step size for RKF45 method
        self._step = 10/1440.0
        
        return None


    # ADJUSTMENTS TO COMMON INTERFACE
    #
    def discharge(self):
        self._branch_flow_helper()
        self._prev_mo_comps = self._mo_comps[:]
        self._prev_so_comps = self._mo_comps[:]

        #self.integrate(7, 'Euler', 0.05, 2.0)
        #self.integrate(7, 'RK4', 0.05, 2.0)
        self.integrate(7, 'RKF45', 0.05, 2.0)
        self._so_comps = self._mo_comps[:]
        self._discharge_main_outlet()

        return None

    # END OF ADJUSTMENTS TO COMMON INTERFACE

    
    # FUNCTIONS UNIQUE TO THE ASM_REACTOR CLASS
    #
    # (INSERT CODE HERE)
    #

    def assign_initial_guess(self, initial_guess):
        ''' 
        Assign the initial guess into _sludge.comps
        '''
        self._sludge._comps = initial_guess[:]
        self._mo_comps = initial_guess[:]  # CSTR: outlet = mixed liquor
        return None


    def set_active_vol(self, vol=380):
        # vol in M3
        if vol > 0:
            self._active_vol = vol
        else:
            print("ERROR:", self.__name__, "requires an active vol > 0 M3.")
        return None


    def get_active_vol(self):
        return self._active_vol


    def set_model_condition(self, Temperature, DO):
        if Temperature >= 4 and DO >= 0:
            self._sludge.update(Temperature, DO)
        else:
            print("ERROR:", self.__name__, "given crazy temperature or DO.")
        return None

   
    def get_model_params(self):
        return self._sludge.get_params()


    def get_model_stoichs(self):
        return self._sludge.get_stoichs()


    def integrate(self, 
            first_index_particulate=7,
            method_name='RK4',
            f_s=0.05,
            f_p=2.0):
        '''
        Integrate the model forward in time.
        '''
        # first_index_particulate: first index of particulate model component 
        # method_name = 'RK4' | 'Euler'
        # f_s: fraction of max step for soluble model components, typ=5%-20%
        # f_p: fraction of max step for particulate model components, typ=2.0

        if method_name == 'RKF45':
            self._runge_kutta_fehlberg_45()
        elif method_name == 'RK4':
            self._runge_kutta_4(first_index_particulate, f_s, f_p)
        else:
            self._euler(first_index_particulate, f_s, f_p)
        
        return None


    def _runge_kutta_fehlberg_45(self, tol=1E-8):
        '''
        Integration by using the Runge-Kutta-Fehlberg (RKF45) method.

        tol: user defined tolerance of error
        
        '''

        # Number of model components
        _nc = len(self._mo_comps)

        # update the step size using the current step size and the scalar from
        # previous round of RK4 vs RK5 comparison
        h = self._step

        print('currently h = {}, s = {}'.format(h, self._scalar))

        f1 = self._sludge._dCdt(self._active_vol,
                                self._total_inflow,
                                self._in_comps,
                                self._sludge._comps)

        _uppers_sol = []
        _uppers_part = []

        for i in range(7):
            # screen out the zero items in _del_C_del_t
            if f1[i] != 0:
                #_uppers_sol.append(self._mo_comps[i] / abs(_del_C_del_t[i]))
                _uppers_sol.append(self._sludge._comps[i] 
                        / abs(f1[i]))

        for j in range(7, _nc):
            # screen out the zero items in _del_C_del_t
            if f1[j] != 0:
                #_uppers_part.append(self._mo_comps[j] / abs(_del_C_del_t[j]))
                _uppers_part.append(self._sludge._comps[j] 
                        / abs(f1[j]))

    
        _max_step_sol = min(_uppers_sol)
        _max_step_part = min(_uppers_part)


        k1 = [h * f1[j] for j in range(_nc)]


        _w2 = [self._sludge._comps[j] + k1[j] / 4
                for j in range(_nc)]

        f2 = self._sludge._dCdt(self._active_vol,
                                self._total_inflow,
                                self._in_comps,
                                _w2)

        k2 = [h * f2[j] for j in range(_nc)]


        # 3/32 = 0.09375; 9/32 = 0.28125
        _w3 = [self._sludge._comps[j] + 0.09375 * k1[j] + 0.28125 * k2[j]
                for j in range(_nc)]

        f3 = self._sludge._dCdt(self._active_vol,
                                self._total_inflow,
                                self._in_comps,
                                _w3)

        k3 = [h * f3[j] for j in range(_nc)]

        
        _w4 = [self._sludge._comps[j] + 1932/2197 * k1[j] - 7200/2197 * k2[j]
                + 7296/2197 * k3[j]
                for j in range(_nc)]

        f4 = self._sludge._dCdt(self._active_vol,
                                self._total_inflow,
                                self._in_comps,
                                _w4)

        k4 = [h * f4[j] for j in range(_nc)]


        _w5 = [self._sludge._comps[j] + 439/216 * k1[j] - 8 * k2[j]
                + 3680/513 * k3[j] - 845/4104 * k4[j]
                for j in range(_nc)]

        f5 = self._sludge._dCdt(self._active_vol,
                                self._total_inflow,
                                self._in_comps,
                                _w5)

        k5 = [h * f5[j] for j in range(_nc)]


        _w6 = [self._sludge._comps[j] - 8/27 * k1[j] + 2 * k2[j]
                - 3544/2565 * k3[j] + 1859/4104 * k4[j] - 11/40 * k5[j]
                for j in range(_nc)]

        f6 = self._sludge._dCdt(self._active_vol,
                                self._total_inflow,
                                self._in_comps,
                                _w6)

        k6 = [h * f6[j] for j in range(_nc)]


        # propose an estimate using RK4 with current step size, without the yk
        # term
        del_RK4 = [25/216 * k1[j] + 1408/2565 * k3[j]
                    + 2197/4101 * k4[j] - 0.2 * k5[j]
                    for j in range(_nc)]
                       

        # propose an estimate using RK5 with current step size, without the yk
        # term
        del_RK5 = [16/135 * k1[j] + 6656/12825 * k3[j]
                    + 28561/56430 * k4[j] - 9/50 * k5[j] + 2/55 * k6[j]
                    for j in range(_nc)]


        _err_sqr = [(del_RK4[j] - del_RK5[j]) ** 2 for j in range(_nc)]

        _err = sum(_err_sqr) ** 0.5

        print('current err:', _err)

        # scalar to adjust step size
        _s = 1.0
        if _err >= tol:
            # (1/2) ^ (1/4) ~= 0.840896
            #_s = 0.840896 * (tol * h / _err) ** 0.25 
            _s = (tol * h / _err) ** 0.25 
            self._scalar = _s
            print('h={}, scalar={}, h_new={}, max_h_sol={}'.format(
                self._step, _s, self._step * _s, _max_step_sol))
            self._step = min(self._step * self._scalar, _max_step_sol * 0.02)
            
                
        # re-evaluate based on new step size
        # yk does not change
        k1 = [self._step * self._sludge._comps[j] for j in range(_nc)]


        _w2 = [self._sludge._comps[j] + k1[j] / 4 for j in range(_nc)]

        f2 = self._sludge._dCdt(self._active_vol,
                                self._total_inflow,
                                self._in_comps,
                                _w2)

        k2 = [self._step * f2[j] for j in range(_nc)]


        # 3/32 = 0.09375; 9/32 = 0.28125
        _w3 = [self._sludge._comps[j] + 0.09375 * k1[j] + 0.28125 * k2[j]
                for j in range(_nc)]

        f3 = self._sludge._dCdt(self._active_vol,
                                self._total_inflow,
                                self._in_comps,
                                _w3)

        k3 = [self._step * f3[j] for j in range(_nc)]

        
        _w4 = [self._sludge._comps[j] + 1932/2197 * k1[j] - 7200/2197 * k2[j]
                + 7296/2197 * k3[j]
                for j in range(_nc)]

        f4 = self._sludge._dCdt(self._active_vol,
                                self._total_inflow,
                                self._in_comps,
                                _w4)

        k4 = [self._step * f4[j] for j in range(_nc)]


        _w5 = [self._sludge._comps[j] + 439/216 * k1[j] - 8 * k2[j]
                + 3680/513 * k3[j] - 845/4104 * k4[j]
                for j in range(_nc)]

        f5 = self._sludge._dCdt(self._active_vol,
                                self._total_inflow,
                                self._in_comps,
                                _w5)

        k5 = [self._step * f5[j] for j in range(_nc)]

        del_RK5 = [16/135 * k1[j] + 6656/12825 * k3[j]
                    + 28561/56430 * k4[j] - 9/50 * k5[j] + 2/55 * k6[j]
                    for j in range(_nc)]

        # update estimate using RK4 with current step size:
        #self._sludge._comps = [self._sludge._comps[j] + 25/216 * k1[j]
        #                + 1408/2565 * k3[j] + 2197/4101 * k4[j] - 0.2 * k5[j]
        #                for j in range(_nc)]
        self._sludge._comps = [self._sludge._comps[j] + del_RK5[j]
                                for j in range(_nc)]

        self._mo_comps = self._so_comps = self._sludge._comps[:]

        return None


    def _runge_kutta_4(self, first_index_part, f_s, f_p):
        '''
        Integration by using Runge-Kutta 4th order method.
        '''
        # first_index_part: first index of particulate model component,
        #   assuming all components before this index are soluble, and all
        #   starting this index are particulate in the matrix.
        # f_s: fraction of max step for soluble model components, typ=5%-20%
        # f_p: fraction of max step for particulate model components, typ=2.0

        # Determine the next step size based on:
        #   C(t + del_t) = C(t) + (dC/dt) * del_t, where
        #   0 < del_t < Retention_Time_C_k, where
        #   C is the individual model component and k is the kth reactor
        _del_C_del_t = self._sludge._dCdt(
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps, 
                            self._mo_comps)

        #print('_del_C_del_t:{}'.format(_del_C_del_t))

        _uppers_sol = []
        _uppers_part = []

        for i in range(first_index_part):
            # screen out the zero items in _del_C_del_t
            if _del_C_del_t[i] != 0:
                #_uppers_sol.append(self._mo_comps[i] / abs(_del_C_del_t[i]))
                _uppers_sol.append(self._sludge._comps[i] 
                        / abs(_del_C_del_t[i]))

        for j in range(first_index_part, len(_del_C_del_t)):
            # screen out the zero items in _del_C_del_t
            if _del_C_del_t[j] != 0:
                #_uppers_part.append(self._mo_comps[j] / abs(_del_C_del_t[j]))
                _uppers_part.append(self._sludge._comps[j] 
                        / abs(_del_C_del_t[j]))

    
        _max_step_sol = min(_uppers_sol)
        _max_step_part = min(_uppers_part)

        _step_sol = f_s * _max_step_sol
        _step_part = f_p * _max_step_part

        #self._int_step_sol = min(self._int_step_sol, _new_step_sol)
        #print('step_sol = ', self._int_step_sol)

        #print('sol. step = {}, part. step = {}'.format(_step_sol, _step_part))

        # mid-point version of RK4, using half the given step size:
        #sz_2 = _step / 2
        sz_2 = _step_sol / 2  #TODO: use soluble step for all for now

        # _w1 = yn = self._mo_comps
        # k1 is idetical to _del_C_del_t calculated above
        k1 = _del_C_del_t 

        # _w2 = y_n + _step/2 * k1
        _w2 = [self._mo_comps[i] + sz_2 * k1[i] for i in range(len(k1))]

        k2 = self._sludge._dCdt(
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps,
                            _w2)

        # _w3 = y_n + _step/2 * k2
        _w3 = [self._mo_comps[i] + sz_2 * k2[i] for i in range(len(k2))]

        k3 = self._sludge._dCdt(
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps,
                            _w3)

        # _w4 = yn + _step * k3
        _w4 = [self._mo_comps[i] + _step_sol * k3[i] for i in range(len(k3))]

        k4 = self._sludge._dCdt(
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps,
                            _w4)

        self._sludge._comps = [self._sludge._comps[i]
                                + (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6
                                * _step_sol
                                for i in range(len(self._sludge._comps))]

        self._mo_comps = self._so_comps = self._sludge._comps[:]

        return None


    def _euler(self, first_index_part=7, f_s=0.05, f_p=2.0):
        '''
        Integration by using Euler's method, aka RK1
        '''

        # first_index_part: first index of particulate model component,
        #   assuming all components before this index are soluble, and all
        #   starting this index are particulate in the matrix.
        # f_s: fraction of max step for soluble model components, typ=5%-20%
        # f_p: fraction of max step for particulate model components, typ=2.0

        # Determine the next step size based on:
        #   C(t + del_t) = C(t) + (dC/dt) * del_t, where
        #   0 < del_t < Retention_Time_C_k, where
        #   C is the individual model component and k is the kth reactor
        _del_C_del_t = self._sludge._dCdt(
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps, 
                            self._mo_comps)

        #print('_del_C_del_t:{}'.format(_del_C_del_t))

        _uppers_sol = []
        _uppers_part = []

        for i in range(first_index_part):
            # screen out the zero items in _del_C_del_t
            if _del_C_del_t[i] != 0:
                #_uppers_sol.append(self._mo_comps[i] / abs(_del_C_del_t[i]))
                _uppers_sol.append(self._sludge._comps[i] 
                        / abs(_del_C_del_t[i]))

        for j in range(first_index_part, len(_del_C_del_t)):
            # screen out the zero items in _del_C_del_t
            if _del_C_del_t[j] != 0:
                #_uppers_part.append(self._mo_comps[j] / abs(_del_C_del_t[j]))
                _uppers_part.append(self._sludge._comps[j] 
                        / abs(_del_C_del_t[j]))

    
        _max_step_sol = min(_uppers_sol)
        _max_step_part = min(_uppers_part)

        _step_sol = f_s * _max_step_sol
        _step_part = f_s * _max_step_part

        #self._int_step_sol = min(self._int_step_sol, _new_step_sol)
        #print('step_sol = ', self._int_step_sol)

        #print('sol. step = {}, part. step = {}'.format(_step_sol, _step_part))

        # TODO: use the same time step before further optimization
        #for i in range(first_index_particulate):
            #self._mo_comps[i] += _del_C_del_t[i] * self._int_step_sol
            
        #for j in range(first_index_particulate, len(self._mo_comps)):
            #self._mo_comps[j] += _del_C_del_t[j] * self._int_step_part

        for i in range(len(self._mo_comps)):
            self._sludge._comps[i] += _del_C_del_t[i] * _step_sol

        self._so_comps = self._mo_comps = self._sludge._comps[:]

        return None

            
    #
    # END OF FUNCTIONS UNIQUE TO THE ASM_REACTOR CLASS

