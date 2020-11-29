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

from ..unit_procs.streams import pipe
from ..ASMModel.asm_1 import ASM_1
from ..ASMModel import constants

from scipy.integrate import solve_ivp

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

        # initial guess of step size for model integration, hr
        self._step = 1.0 / 24.0

        # local error for integration routine:
        self._prev_local_err = 1e-3

        # absolute tolerance for integration
        self._atol = 1e-5
        # relative tolerance for integration
        self._rtol = 1e-5

        #---------------------
        # solution of the integration
        self._solultion = None

        return None


    # ADJUSTMENTS TO COMMON INTERFACE
    #
    def is_converged(self, limit=0.01):
        """
        Redefine the convergence evaluation for the asm_reactor because of the
        explicit definitions of dy/dt in the ASM model.

        Current default criteria for steady state (convergence):
            L2-norm of dy/dt < limit

        Args:
            limit: Limit within which the simulation is considered converged

        Return:
            True/False

        """
        #L2_norm = (sum([dcdt ** 2 for dcdt in self._del_C_del_t])) ** 0.5
        #print("L2norm = ", L2_norm)
        #return L2_norm < limit

        accept = [abs(self._mo_comps[i] - self._prev_mo_comps[i])
                    < 1e-4 + 1e-4 * self._prev_mo_comps[i]
                    for i in range(len(self._mo_comps))]
        return not (False in accept)


    def discharge(self, method_name="BDF"):
        """
        Pass the total flow and blended components to the downstreams.

        This function is re-implemented for "asm_reactor". Because of the
        biological reactions "happening" in the "asm_reactor", integration of
        the model (Note 1) is carried out here before sending the results to
        the down stream.

        Args:
            method_name: "BDF", "RK45", "Radau", etc.(see Note 2 below)

        Retrun:
            self._sludge._comps

        Notes:
            1) It is highly recommended the model components are arranged
            such that all the soluble ones are ahead of the particulate ones
            in the array. Generally, soluble components requires smaller    
            time steps than particulate ones. This kind of arrangement will
            enable quick identification of soluble/particulate components that
            may have very different suitable time step during integration.  
            Using appropriate but different time steps for the soluble and
            particulate components is required for fast integrations with
            correct results. This is how the ODE partitioning method suggested
            in the IWA ASM1 report works. Although PooPyLab doesn't apply this
            relaxation scheme as of now, arranging the model components in such
            partitioned way will allow future exploration of optimization
            approaches.

            2) There are a few integration methods attempted for PooPyLab:
            Euler, Runge-Kutta 4th order, Runge-Kutta-Felhberg 4/5,
            RK-Dormand-Prince-4/5, and the ODE system partitioning scheme
            suggested in the IWA ASM1 report.  After much study, it is decided
            to settle with scipy.integrate.solve_ivp routine for now so that
            the rest of the PooPyLab development can progress, while KZ
            continues in his study of BDF methods and attempts for a home brew
            version.  
            Euler, RK4, RKF45, RKDP45, and Partitioned ODE methods
            have been coded and tested in the past but no longer in use as of
            now, except for RKF45. The unused code is moved to
            bio_py_funcs_not_used.txt for archiving.

        See:
            _runge_kutta_fehlberg_45()
        """
        self._branch_flow_helper()
        self._prev_mo_comps = self._mo_comps[:]
        self._prev_so_comps = self._mo_comps[:]

        # integration with home brew rkf45, currently NOT USED
        #self._runge_kutta_fehlberg_45()
        #return None

        # integration using scipy.integrate.solve_ivp()
        self._solultion = solve_ivp(self._sludge._dCdt, [0, 1], self._mo_comps,
                    method=method_name,
                    args=(self._active_vol, self._total_inflow, self._in_comps)
                    )
        #print(self._solultion.y)
        self._sludge._comps = [yi[-1] for yi in self._solultion.y]

        self._mo_comps = self._sludge._comps[:]
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

        #f1 should've been calculated in _runge_kutta_fehlberg_45()
        f1 = self._del_C_del_t  #calculated in _runge_kutta_fehlberg_45()

        
        k1 = [h * f1[j] for j in range(_nc)]


        _w2 = [self._sludge._comps[j] + k1[j] / 4
                for j in range(_nc)]

        f2 = self._sludge._dCdt_kz(_w2,
                                self._active_vol,
                                self._total_inflow,
                                self._in_comps)

        k2 = [h * f2[j] for j in range(_nc)]


        # 3/32 = 0.09375; 9/32 = 0.28125
        _w3 = [self._sludge._comps[j] + 0.09375 * k1[j] + 0.28125 * k2[j]
                for j in range(_nc)]

        f3 = self._sludge._dCdt_kz(_w3,
                                self._active_vol,
                                self._total_inflow,
                                self._in_comps)

        k3 = [h * f3[j] for j in range(_nc)]

        
        _w4 = [self._sludge._comps[j] + 1932/2197 * k1[j] - 7200/2197 * k2[j]
                + 7296/2197 * k3[j]
                for j in range(_nc)]

        f4 = self._sludge._dCdt_kz(_w4,
                                self._active_vol,
                                self._total_inflow,
                                self._in_comps)

        k4 = [h * f4[j] for j in range(_nc)]


        _w5 = [self._sludge._comps[j] + 439/216 * k1[j] - 8 * k2[j]
                + 3680/513 * k3[j] - 845/4104 * k4[j]
                for j in range(_nc)]

        f5 = self._sludge._dCdt_kz(_w5,
                                self._active_vol,
                                self._total_inflow,
                                self._in_comps)

        k5 = [h * f5[j] for j in range(_nc)]


        _w6 = [self._sludge._comps[j] - 8/27 * k1[j] + 2 * k2[j]
                - 3544/2565 * k3[j] + 1859/4104 * k4[j] - 11/40 * k5[j]
                for j in range(_nc)]

        f6 = self._sludge._dCdt_kz(_w6,
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

        #_rk4_sqr_ = [(1/360.0 * k1[j] - 128/4275.0 * k3[j]
        #            - 2197/75240.0 * k4[j] + 0.02 * k5[j] + 2/55 * k6[j]) ** 2
        #            for j in range(_nc)]
#
#        _err = sum(_rk4_sqr_) ** 0.5

        #print('current err:', _err)

        #return _err

        delta = [(1/360.0 * k1[j] - 128/4275.0 * k3[j]
                    - 2197/75240.0 * k4[j] + 0.02 * k5[j] + 2/55 * k6[j])
                    for j in range(_nc)]

        scale = [ self._atol + self._rtol * self._mo_comps[i]
                    for i in range(_nc) ]

        LE_sum = sum( [ (delta[i] / scale[i])**2 for i in range(_nc) ] )

        return (LE_sum / _nc)**0.5 



    def _runge_kutta_fehlberg_45(self, tol=1e-4):
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

        self._del_C_del_t = self._sludge._dCdt_kz(
                            self._mo_comps,
                            self._active_vol,
                            self._total_inflow,
                            self._in_comps)

        #print('self._del_C_del_t:{}'.format(self._del_C_del_t))

        while True:
            k1, k2, k3, k4, k5, k6 = self._RKF45_ks()

            self._prev_local_err = self._RKF45_err(k1, k3, k4, k5, k6)

            # (1/2) ^ (1/4) ~= 0.840896
            #_s = 0.840896 * (tol * h / _err) ** 0.25 
            _s = 0.84 * (tol * self._step / self._prev_local_err) ** 0.25 
            self._step *= _s

            #print('h_old={}, scalar={}'.format(self._step, _s))

            if self._prev_local_err < tol or self._step < 1e-5:
                #print("RKF45 step=", self._step)
                self._sludge._comps = [self._sludge._comps[j]
                            + 25/216 * k1[j] + 1408/2565 * k3[j]
                            + 2197/4104 * k4[j] - 0.2 * k5[j] 
                            for j in range(len(self._mo_comps))]
                break

        self._mo_comps = self._sludge._comps[:]

        return self._step

    #
    # END OF FUNCTIONS UNIQUE TO THE ASM_REACTOR CLASS

