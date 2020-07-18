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


"""Defines classes for biological reactors used in an WWTP.

    1) ASM Reactor (bioreactor using ASM models);

    2) Aerobic Digester (#TODO: add);

    3) ADM Reactor (bioreactor using Anaerobic Digestion Model) (#TODO: add)
"""
## @namespace bio
## @file bio.py

from scipy.optimize import root

from unit_procs.streams import pipe
from ASMModel.asm_1 import ASM_1
from ASMModel import constants


# ----------------------------------------------------------------------------

class asm_reactor(pipe):
    """
    Bioreactor using ASM kinetics, derived as a "pipe" w/ active volume.

    Current design only uses ASM 1 model. Will need to add flexibility for
    using ASM 2d, ASM 3, and user revised versions of them.

    The "asm_reactor" contain sludge mixed liquor of a certain kinetics
    described by the chosen model.

    The integration of the model is also done by the "asm_reactor".
    """

    __id = 0

    def __init__(self, act_vol=38000, swd=3.5,
                    ww_temp=20, DO=2, *args, **kw):
        """
        Init w/ active volume, water depth, water temperature, & dissolved O2.

        Args:
            act_vol:    active process volume, m3
            swd:        side water depth, m
            ww_temp:    wastewater temperature, degC
            DO:         dissolved oxygen, mg/L
            args:       (provision for other parameters for different models)
            kw:         (provision for other parameters)

        Return:
            None
        """

        pipe.__init__(self) 
        self.__class__.__id += 1
        self.__name__ = 'ASMReactor_' + str(self.__id)

        self._type = 'ASMReactor'

        ## active volume, m3
        self._active_vol = act_vol
        ## side water depth, m
        self._swd = swd
        ## plan section area, m2
        self._area = self._active_vol / self._swd

        ## sludge mixed liquor contained in the reactor
        self._sludge = ASM_1(ww_temp, DO)

        # storage of _sludge._dCdt for the current step
        self._del_C_del_t = [0.0] * constants._NUM_ASM1_COMPONENTS

        self._in_comps = [0.0] * constants._NUM_ASM1_COMPONENTS 
        self._mo_comps = [0.0] * constants._NUM_ASM1_COMPONENTS

        # results of previous round
        self._prev_mo_comps = [0.0] * constants._NUM_ASM1_COMPONENTS
        self._prev_so_comps = self._prev_mo_comps

        self._upstream_set_mo_flow = True

        ## step size for model integration, hr
        self._step = 0.5 / 24.0
        
        return None


    # ADJUSTMENTS TO COMMON INTERFACE
    #
    def is_converged(self, limit=1E-6):
        """
        Redefine the convergence evaluation for the asm_reactor because of the
        explicit definitions of dy/dt in the ASM model.

        Current default criteria for steady state (convergence):
            L2-norm of dy/dt < 1E-6

        Args:
            limit: Limit within which the simulation is considered converged

        Return:
            True/False
        """
        
        _der2 = [dcdt * dcdt for dcdt in self._del_C_del_t]
        _sum = sum(_der2)
        L2_norm = _sum ** 0.5

        print("dCdt:{}, L2norm={}".format(self._del_C_del_t, L2_norm))

        return L2_norm < limit


    def discharge(self):
        """
        Pass the total flow and blended components to the downstreams.

        This function is re-implemented for "asm_reactor". Because of the
        biological reactions "happening" in the "asm_reactor", integration of
        the model is carried out here before sending the results to the down
        stream.

        See:
            _integrate().
        """
        self._branch_flow_helper()
        self._prev_mo_comps = self._mo_comps[:]
        self._prev_so_comps = self._mo_comps[:]

        #self._integrate(7, 'Euler', 0.05, 2.0)
        #self._integrate(7, 'RK4', 0.05, 2.0)
        #self._integrate(7, 'RKF45', 0.05, 2.0)
        self._relax()
        self._so_comps = self._mo_comps[:]
        self._discharge_main_outlet()

        return None

    
    def assign_initial_guess(self, initial_guess):
        """
        Assign the intial guess to the unit before simulation.

        This function is re-implemented for "asm_reactor" which contains the
        "sludge" whose kinetics are described by the model. 

        When passing the initial guess into an "asm_reactor", the reactor's
        inlet, mainstream outlet, and the "sludge" in it all get the same list
        of model component concentrations.

        Args:
            initial_guess:  list of model components

        Return:
            None
        """
        self._sludge._comps = initial_guess[:]
        self._mo_comps = initial_guess[:]  # CSTR: outlet = mixed liquor
        return None

    # END OF ADJUSTMENTS TO COMMON INTERFACE


    # FUNCTIONS UNIQUE TO THE ASM_REACTOR CLASS
    #
    # (INSERT CODE HERE)
    #

    def set_active_vol(self, vol=380):
        """
        Set the active process volume.
        
        Args:
            vol:    active volume to be used. (m3)

        Return:
            None
        """
        if vol > 0:
            self._active_vol = vol
        else:
            print("ERROR:", self.__name__, "requires an active vol > 0 M3.")
        return None


    def get_active_vol(self):
        """
        Return the active process volume. (m3)
        """
        return self._active_vol


    def set_model_condition(self, ww_temp, DO):
        """
        Set the wastewater temperature and dissolved O2 for the model.

        This function updates the model conditions for the "sludge" the
        "asm_reactor" contains.

        Args:
            ww_temp:    wastewtaer temperature in degC;
            DO:         dissolved O2 concentration in mg/L.
        
        Return:
            None

        See:
            ASMModel.ASM_1.update().
        """
        if ww_temp >= 4 and DO >= 0:
            self._sludge.update(ww_temp, DO)
        else:
            print("ERROR:", self.__name__, "given crazy temperature or DO.")
        return None

   
    def get_model_params(self):
        """
        Return the kinetic parameters of the applied model.

        Return:
            {param_name, param_val_adjusted}

        See:
            ASMModel.ASM_1.get_params().
        """
        return self._sludge.get_params()


    def get_model_stoichs(self):
        """
        Return the stoichiometrics of the applied model.

        Return:
            {id_of_stoich, val}

        See:
            ASMModel.ASM_1.get_stoichs().
        """
        return self._sludge.get_stoichs()
    
    
    def _relax(self):
        """
        Relaxation into steady state.

        This function is to utilize the root finding routines in scipy.optimize
        module to solve the differential equation system that dC/dt = 0 instead
        of reaching the steady state with real time integration.

        Args:
            None

        Return:
            model components that satisify dC/dt = 0

        Note:
            Requires constant influent characterisitics and operating
            conditions.
        """
        
        root_ss = root(self._sludge._dCdt,
                        self._sludge._comps,
                        (self._active_vol, self._total_inflow, self._in_comps),
                        method='hybr',
                        options={'factor':0.1})

        print(root_ss)

        self._sludge._comps = root_ss.x[:]

        self._mo_comps = self._sludge._comps[:]

        return None


    def _integrate(self,
                    first_index_particulate=7,
                    method_name='RKF45',
                    f_s=0.05,
                    f_p=2.0):
        """
        Integrate the model forward in time.

        Starting from the initial guess, this function integrates the model
        forward in time. There are a few integration methods available in
        PooPyLab: Euler, Runge-Kutta 4th order, and Runge-Kutta-Felhberg 4/5.
        The default is RKF45.

        Args:
            first_index_particulate:    see Note 1 below
            method_name:        'RKF45'|'RK4'|'Euler'
            f_s:                see Note 2 below
            f_p:                see Note 2 below

        Notes:
            1. It is highly recommended the model components are arranged
            such that all the soluble ones are ahead of the particulate ones
            in the array. Generally, soluble components requires smaller    
            time steps than particulate ones. This kind of arrangement will
            enable quick identification of soluble/particulate components that
            may have very different suitable time step during integration.  
            Using appropriate but different time steps for the soluble and
            particulate components is required for fast integrations with
            correct results.

            2. The two parameters f_s and f_p came from the IWA Activated
            Sludge Model 1 Report where it talks about the appropriate
            integration step sizes for the soluble and particulate component.
            The report suggested that the integration step sizes can be
            determined by using the actual retention time of the constituent in
            the reactor times f_s (factor for solubles, typ. 5% to 20%) or f_p
            (factor for particulate, can go up to 200%). These two parameters
            were used in the Euler and RK4 methods, but not RKF45.


        Retrun:
            self._step

        See:
            _runge_kutta_fehlberg_45();
            _runge_kutta_4();
            _euler();
            discharge().
        """

        if method_name == 'RKF45':
            self._runge_kutta_fehlberg_45()
        elif method_name == 'RK4':
            self._runge_kutta_4(first_index_particulate, f_s, f_p)
        else:
            self._euler(first_index_particulate, f_s, f_p)
 
        return None


    def _max_steps(self, dCdt=[], last_index_sol_comp=7):
        """
        Determine the max acceptable integration steps for the model components.

        Args:
            last_index_sol_comp: last index of soluble component (see note).
    
        Return:
            max_step_sol, max_step_part

        Note:
            It is assumed that the model components are arranged in the list
            with all the soluble components at the front, followed by all the
            particulate ones. This will make using different time steps for the
            two types of model components to speed up the dynamic simulation
            possible.

       """
        _uppers_sol = [self._sludge._comps[i] / abs(dCdt[i]) 
                        for i in range(last_index_sol_comp)
                        if dCdt[i] != 0]

        _uppers_part = [self._sludge._comps[j] / abs(dCdt[j])
                        for j in range(last_index_sol_comp, len(dCdt))
                        if dCdt[j] != 0]

        _max_s_sol = min(_uppers_sol)
        _max_s_part = min(_uppers_part)

        return _max_s_sol, _max_s_part


    def _RKF45_ks(self):
        """
        Calculate k1...k6 used in RKF45 method.

        See:
            _runge_kutta_fehlberg_45();
            _RKF45_err().
        """

        # number of model components
        _nc = len(self._mo_comps)

        # update the step size using the current step size and the scalar from
        # previous round of RK4 vs RK5 comparison
        h = self._step

        f1 = self._sludge._dCdt(self._mo_comps,
                                self._active_vol,
                                self._total_inflow,
                                self._in_comps)

        
        k1 = [h * f1[j] for j in range(_nc)]


        _w2 = [self._sludge._comps[j] + k1[j] / 4
                for j in range(_nc)]

        f2 = self._sludge._dCdt(_w2,
                                self._active_vol,
                                self._total_inflow,
                                self._in_comps)

        k2 = [h * f2[j] for j in range(_nc)]


        # 3/32 = 0.09375; 9/32 = 0.28125
        _w3 = [self._sludge._comps[j] + 0.09375 * k1[j] + 0.28125 * k2[j]
                for j in range(_nc)]

        f3 = self._sludge._dCdt(_w3,
                                self._active_vol,
                                self._total_inflow,
                                self._in_comps)

        k3 = [h * f3[j] for j in range(_nc)]

        
        _w4 = [self._sludge._comps[j] + 1932/2197 * k1[j] - 7200/2197 * k2[j]
                + 7296/2197 * k3[j]
                for j in range(_nc)]

        f4 = self._sludge._dCdt(_w4,
                                self._active_vol,
                                self._total_inflow,
                                self._in_comps)

        k4 = [h * f4[j] for j in range(_nc)]


        _w5 = [self._sludge._comps[j] + 439/216 * k1[j] - 8 * k2[j]
                + 3680/513 * k3[j] - 845/4104 * k4[j]
                for j in range(_nc)]

        f5 = self._sludge._dCdt(_w5,
                                self._active_vol,
                                self._total_inflow,
                                self._in_comps)

        k5 = [h * f5[j] for j in range(_nc)]


        _w6 = [self._sludge._comps[j] - 8/27 * k1[j] + 2 * k2[j]
                - 3544/2565 * k3[j] + 1859/4104 * k4[j] - 11/40 * k5[j]
                for j in range(_nc)]

        f6 = self._sludge._dCdt(_w6,
                                self._active_vol,
                                self._total_inflow,
                                self._in_comps)

        k6 = [h * f6[j] for j in range(_nc)]

        return k1, k2, k3, k4, k5, k6

    
    def _RKF45_err(self, k1, k3, k4, k5, k6):
        """
        Calculate the norm of the error vector in RKF45 method.
        
        Args:
            k1, k3, ... ,k6: intermediate step vectors of RKF45

        Return:
            Norm of the error vector

        See:
            _runge_kutta_fehlberg_45();
            _RKF45_ks().
        """

        _nc = len(self._mo_comps)

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


        #_err_sqr = [(del_RK4[j] - del_RK5[j]) ** 2 for j in range(_nc)]
        
        #_err = sum(_err_sqr) ** 0.5
        _rk4_sqr_ = [(1/360.0 * k1[j] - 128/4275.0 * k3[j]
                    - 2197/75240.0 * k4[j] + 0.02 * k5[j] + 2/55 * k6[j]) ** 2
                    for j in range(_nc)]
        _err = sum(_rk4_sqr_) ** 0.5

        print('current err:', _err)

        return _err


    def _runge_kutta_fehlberg_45(self, tol=1E-6):
        """
        Integration by using the Runge-Kutta-Fehlberg (RKF45) method.

        Args:
            tol:    user defined tolerance of error
        
        Return:
            step size used

        See:
            _RKF45_ks();
            _RKF45_err().
        """

        self._del_C_del_t = self._sludge._dCdt(
                            self._mo_comps,
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps)

        #print('self._del_C_del_t:{}'.format(self._del_C_del_t))

        _max_step_sol, _max_step_part = self._max_steps(self._del_C_del_t, 7)

        while True:
            k1, k2, k3, k4, k5, k6 = self._RKF45_ks()

            _error = self._RKF45_err(k1, k3, k4, k5, k6)

            # (1/2) ^ (1/4) ~= 0.840896
            #_s = 0.840896 * (tol * h / _err) ** 0.25 
            _s = 0.84 * (tol * self._step / _error) ** 0.25 
            # potential new step:
            #h_new = min(self._step * _s, _max_step_sol)
            if _s < 0.75:
                self._step /= 2.0
            elif _s > 1.5 and self._step * _s < _max_step_sol:
                self._step *= 2.0

            print('h_old={}, scalar={}'.format(self._step, _s))

            if _error < tol or self._step < 1e-14:
                # update estimate using RK5 with current step size:
                #self._sludge._comps = [self._sludge._comps[j]
                #            + 16/135 * k1[j] + 6656/12825 * k3[j]
                #            + 28561/56430 * k4[j] - 9/50 * k5[j] + 2/55 * k6[j]
                #            for j in range(len(self._mo_comps))]
                print("RKF45 step=", self._step)
                self._sludge._comps = [self._sludge._comps[j]
                            + 25/216 * k1[j] + 1408/2565 * k3[j]
                            + 2197/4104 * k4[j] - 0.2 * k5[j] 
                            for j in range(len(self._mo_comps))]

                break

            # if the h_new offers significant speed gain, increase the
            # step size for the next round
            #if h_new / self._step >= 1.25 or h_new < self._step:
            #    self._step = h_new


        self._mo_comps = self._sludge._comps[:]

        return self._step


    def _runge_kutta_4(self, first_index_part, f_s, f_p):
        """
        Integration by using Runge-Kutta 4th order method.
        
        Args:
            first_index_part:   first index of particulate model component;
            f_s:                factor of max step for soluble components;
            f_p:                factor of max step for particulate components.

        Return:
            step size used  # TODO: REVISE TO RETURN STEP SIZE INSTEAD OF NONE

        See:
            _runge_kutta_fehlberg_45();
            _euler();
        """
        # Determine the next step size based on:
        #   C(t + del_t) = C(t) + (dC/dt) * del_t, where
        #   0 < del_t < Retention_Time_C_k, where
        #   C is the individual model component and k is the kth reactor
        self._del_C_del_t = self._sludge._dCdt(
                            self._mo_comps,
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps)

        #print('self._del_C_del_t:{}'.format(self._del_C_del_t))
        _max_step_sol, _max_step_part = self._max_steps(self._del_C_del_t, 7)

        _step_sol = f_s * _max_step_sol
        _step_part = f_p * _max_step_part

        #self._int_step_sol = min(self._int_step_sol, _new_step_sol)
        #print('step_sol = ', self._int_step_sol)

        #print('sol. step = {}, part. step = {}'.format(_step_sol, _step_part))

        # mid-point version of RK4, using half the given step size:
        #sz_2 = _step / 2
        sz_2 = _step_sol / 2  #TODO: use soluble step for all for now

        # _w1 = yn = self._mo_comps
        # k1 is idetical to self._del_C_del_t calculated above
        k1 = self._del_C_del_t 

        # _w2 = y_n + _step/2 * k1
        _w2 = [self._mo_comps[i] + sz_2 * k1[i] for i in range(len(k1))]

        k2 = self._sludge._dCdt(
                            _w2,
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps)

        # _w3 = y_n + _step/2 * k2
        _w3 = [self._mo_comps[i] + sz_2 * k2[i] for i in range(len(k2))]

        k3 = self._sludge._dCdt(
                            _w3,
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps)

        # _w4 = yn + _step * k3
        _w4 = [self._mo_comps[i] + _step_sol * k3[i] for i in range(len(k3))]

        k4 = self._sludge._dCdt(
                            _w4,
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps)

        self._sludge._comps = [self._sludge._comps[i]
                                + (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6
                                * _step_sol
                                for i in range(len(self._sludge._comps))]

        self._mo_comps = self._sludge._comps[:]

        return None


    def _euler(self, first_index_part=7, f_s=0.05, f_p=2.0):
        """
        Integration by using Euler's method, aka RK1
        
        Args:
            first_index_part: first index of particulate component;
            f_s:    factor of max step for soluble components;
            f_p:    factor of max step for particulate components.

        Return:
            step size used  # TODO: REVISE TO RETURN STEP SIZE INSTEAD OF NONE
            
        See:
            _runge_kutta_fehlberg_45();
            _runge_kutta_4();
        """

        # Determine the next step size based on:
        #   C(t + del_t) = C(t) + (dC/dt) * del_t, where
        #   0 < del_t < Retention_Time_C_k, where
        #   C is the individual model component and k is the kth reactor
        self._del_C_del_t = self._sludge._dCdt(
                            self._mo_comps,
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps)

        #print('self._del_C_del_t:{}'.format(self._del_C_del_t))
        _max_step_sol, _max_step_part = self._max_steps(self._del_C_del_t, 7)

        _step_sol = f_s * _max_step_sol
        _step_part = f_s * _max_step_part

        #self._int_step_sol = min(self._int_step_sol, _new_step_sol)
        #print('step_sol = ', self._int_step_sol)

        #print('sol. step = {}, part. step = {}'.format(_step_sol, _step_part))

        # TODO: use the same time step before further optimization
        #for i in range(first_index_particulate):
            #self._mo_comps[i] += self._del_C_del_t[i] * self._int_step_sol
            
        #for j in range(first_index_particulate, len(self._mo_comps)):
            #self._mo_comps[j] += self._del_C_del_t[j] * self._int_step_part

        for i in range(len(self._mo_comps)):
            self._sludge._comps[i] += self._del_C_del_t[i] * _step_sol

        self._mo_comps = self._sludge._comps[:]

        return None

            
    #
    # END OF FUNCTIONS UNIQUE TO THE ASM_REACTOR CLASS

