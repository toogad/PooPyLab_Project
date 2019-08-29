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
#
#
#    This is the definition of the ASM1 model to be imported
#    as part of the Reactor object
#
# Change Log:
# 2019-08-27 KZ: added integrate()
# 2019-02-09 KZ: standardized import
# 2019-08-12 KZ: fixed typos
#    Dec 13, 2017 KZ: Fixed a few mismatched parentheses 
#    Jul 20, 2017 KZ: Changed to pythonic style
#    Mar 21, 2017 KZ: Changed to Python3
#    Jun 07, 2014 KZ: Spelling Fix
#
# NOMENCLATURE:
# rb:   readily biodegradable
# nrb:  non-readily biodegradable
# O:    Oxygen
# NH:   Ammonia
# L:    Lysis
# H:    Heterotrophs
# h:    Hydrolysis
# a:    Ammonification
# i:    ratio
# f:    fraction
# cf:   correction factor
# A:    Autotrophs
# B:    Biomass (active)
# D:    Debris
# NO:   NOx (oxidized nitrogen)
# I:    Inert
# ALK:  Alkalinity
# S:    Substrate (COD or TKN, mg/L)
# X:    Particulate matter as COD ( mg/L)
# S:    Soluble
# Inf:  Influent
# Eff:  Effluent
# TBD:  To Be Determined by user


from ASMModel import constants
from scipy.optimize import fsolve

class ASM_1():

    def __init__(self, WWtemp=20, DO=2):

        self._temperature = WWtemp
        self._bulk_DO = DO 
        
        # define the model parameters and stochoimetrics as dict() so that it
        # is easier to keep track of names and values
        self._params = {}
        self._stoichs = {}
        self._delta_t = 20 - self._temperature
        
        # define a Python Dictionary to store Parameters
        self._set_params()
        
        # define a Python Dictionary to store Stochoimetrics
        self._set_stoichs()
        
        # define a Python List to store ASM components
        # The Components the ASM components IN THE REACTOR. JULY 10, 2013
        # For ASM #1:
        #
        #    self._comps[0]: X_I
        #    self._comps[1]: X_S
        #    self._comps[2]: X_BH
        #    self._comps[3]: X_BA
        #    self._comps[4]: X_D
        #    self._comps[5]: S_I
        #    self._comps[6]: S_S
        #    self._comps[7]: S_DO as COD
        #    self._comps[8]: S_NO
        #    self._comps[9]: S_NH
        #    self._comps[10]: S_NS
        #    self._comps[11]: X_NS
        #    self._comps[12]: S_ALK
        #
        self._comps = [1.0] * constants._NUM_ASM1_COMPONENTS

        return



    #====================== Public Interface ==================================

    def steady_step(self, guess, inflow, infcomp, vol):
        '''
            Calculate the state of this round of iteration.
            Pass the results to the storing List() in the ASMReactor.
            The results of this calculation should be compared with those of
            the last round, and determine whether the reactor has reached a
            steady state.
        '''
        current_state = fsolve(self._steady, guess, (inflow, infcomp, vol))
        return current_state




    def integrate(self, prevComp, 
                        InFlow, InfComp, 
                        Vol, 
                        step_size=1.0/24.0):
        ''' integrate _dCdt() forward in time '''
        # Inflow: inlet flow (i.e. outlet flow)
        # prevComp: list of previous round of model components
        # step_size: unit=day

        _curComp = []

        _conc = prevComp[:]
        
        _dC_ = self._dCdt(_conc, Inflow, InfComp, Vol) * step_size

        for i in range(len(_dC_)):
            _curComp = prevComp[i] + _dC_[i]

        return _curComp[:]


    def update(self, Temp, DO):
        ''' update the ASM model with new Temperature and Bulk_DO'''
        if Temp <= 4 or DO < 0:
            print("Error: New temperature or Bulk_DO too low.", \
                    "USING PREVIOUS VALUES FOR BOTH")
            return -1

        self._temperature = Temp
        self._bulk_DO = DO
        self._delta_t = 20 - self._temperature
        self._param = self._set_params()
        self._stoich = self._set_stoichs()
        return 0

    def get_params(self):
        return self._params.copy()

    def get_stoichs(self):
        return self._stoichs.copy()

    def get_all_comps(self):
        #TODO: Need to determine where to provide GetAllComponents(), in
        # ASMReactor or here?
        return self._comps[:]

    def get_bulk_DO(self):
        return self._bulk_DO

    #====================== End of Public Interface ==================

    def _set_params(self):

        # Ideal Growth Rate of Heterotrophs (u_H, 1/DAY)
        self._params['u_H'] = 6.0 * pow(1.08, self._delta_t)

        # Ideal Lysis Rate of Heterotrophs (b_LH, 1/DAY)
        self._params['b_LH'] = 0.408 * pow(1.04, self._delta_t)

        # Ideal Growth Rate of Autotrophs (u_A, 1/DAY)
        self._params['u_A'] = 0.768 * pow(1.11, self._delta_t)

        # Ideal Growth Rate of Autotrophs (b_LA, 1/DAY)
        self._params['b_LA'] = 0.096 * pow(1.04, self._delta_t)

        # Half Growth Rate Concentration of Heterotrophs (K_s, mgCOD/L)
        self._params['K_S'] = 20.0

        # Switch Coefficient for Dissoved O2 of Hetero. (K_OH, mgO2/L)
        self._params['K_OH'] = 0.1

        # Association Conc. for Dissoved O2 of Auto. (K_OA, mgN/L)
        self._params['K_OA'] = 0.75

        # Association Conc. for NH3-N of Auto. (K_NH, mgN/L)
        self._params['K_NH'] = 1.0 * pow(1.14, self._delta_t)

        # Association Conc. for NOx of Hetero. (K_NO, mgN/L)
        self._params['K_NO'] = 0.2

        # Hydrolysis Rate (k_h, mgCOD/mgBiomassCOD-day)
        self._params['k_h'] = 2.208 * pow(1.08, self._delta_t)

        # Half Rate Conc. for Hetero. Growth on Part. COD
        # (K_X, mgCOD/mgBiomassCOD)
        self._params['K_X'] = 0.15

        # Ammonification of Org-N in biomass (k_a, L/mgBiomassCOD-day)
        self._params['k_a'] = 0.1608 * pow(1.08, self._delta_t)

        # Yield of Hetero. Growth on COD (Y_H, mgBiomassCOD/mgCODremoved)
        self._params['Y_H'] = 0.6

        # Yield of Auto. Growth on TKN (Y_A, mgBiomassCOD/mgTKNoxidized)
        self._params['Y_A'] = 0.24

        # Fract. of Debris in Lysed Biomass(f_D_, gDebrisCOD/gBiomassCOD)
        self._params['f_D_'] = 0.08

        # Correction Factor for Hydrolysis (cf_h, unitless)
        self._params['cf_h'] = 0.4

        # Correction Factor for Anoxic Heterotrophic Growth (cf_g, unitless)
        self._params['cf_g'] = 0.8

        # Ratio of N in Active Biomass (i_N_XB, mgN/mgActiveBiomassCOD)
        self._params['i_N_XB'] = 0.086

        # Ratio of N in Debris Biomass (i_N_XD, mgN/mgDebrisBiomassCOD)
        self._params['i_N_XD'] = 0.06

        return None
    #=============================== End of Parameter Definition ==============

    # STOCHIOMETRIC MATRIX (Use the Table 6.1, p193, Grady Jr. et al 1999)
    def _set_stoichs(self):

        self._stoichs['0_2'] = 1.0

        self._stoichs['0_6'] = -1.0 / self._params['Y_H']

        self._stoichs['0_7'] = (1.0 - self._params['Y_H']) / self._params['Y_H']
        # TODO: multiply -1 to express as oxygen

        self._stoichs['0_9'] = -self._params['i_N_XB']

        self._stoichs['0_12'] = -self._params['i_N_XB'] / 14.0

        self._stoichs['1_2'] = 1.0

        self._stoichs['1_6'] = -1.0 / self._params['Y_H']

        self._stoichs['1_8'] = -(1.0 - self._params['Y_H']) \
                                / (2.86 * self._params['Y_H'])

        self._stoichs['1_9'] = -self._params['i_N_XB']

        self._stoichs['1_12'] = (1.0 - self._params['Y_H']) \
                                / (14.0 * 2.86 * self._params['Y_H']) \
                                - self._params['i_N_XB'] / 14.0

        self._stoichs['2_3'] = 1.0

        self._stoichs['2_7'] = (4.57 - self._params['Y_A']) \
                                / self._params['Y_A']
        # TODO: multiply -1 to express as oxygen

        self._stoichs['2_8'] = 1.0 / self._params['Y_A']

        self._stoichs['2_9'] = -self._params['i_N_XB'] \
                                - 1.0 / self._params['Y_A']

        self._stoichs['2_12'] = -self._params['i_N_XB'] / 14 \
                                - 1.0 / (7.0 * self._params['Y_A'])

        self._stoichs['3_1'] = 1.0 - self._params['f_D_']

        self._stoichs['3_2'] = -1.0

        self._stoichs['3_4'] = self._params['f_D_']

        self._stoichs['3_11'] = self._params['i_N_XB'] - self._params['f_D_'] \
                                * self._params['i_N_XD']

        self._stoichs['4_1'] = 1.0 - self._params['f_D_']

        self._stoichs['4_3'] = -1.0

        self._stoichs['4_4'] = self._params['f_D_']

        self._stoichs['4_11'] = self._params['i_N_XB'] - self._params['f_D_'] \
                                * self._params['i_N_XD']

        self._stoichs['5_9'] = 1.0

        self._stoichs['5_10'] = -1.0

        self._stoichs['5_12'] = 1.0 / 14.0

        self._stoichs['6_1'] = -1.0

        self._stoichs['6_6'] = 1.0

        self._stoichs['7_10'] = 1.0

        self._stoichs['7_11'] = -1.0

        return None
    ##=========================== End of Stoichiometrics =====================

    # PROCESS RATE DEFINITIONS (Rj, M/L^3/T):

    # The following factors/swithes all use the _monod() function
    # Monod Factor of Sol.BioDegrad.COD on Hetero.
    # Monod Switch of Dissol. O2 on Hetero.
    # Monod Switch of Dissol. O2 on Auto.
    # Monod Factor of Ammonia-N on Autotrophs
    # Monod Factor of NOx-N on Autotrophs
    #
    def _monod (self, My_Eff_S_TBD, My_K_TBD):
        return My_Eff_S_TBD / (My_Eff_S_TBD + My_K_TBD)

    # Aerobic Growth Rate of Heterotrophs (_r0_AerGH, mgCOD/L/day)
    def _r0_AerGH (self):
        return  self._params['u_H'] \
                * self._monod(self._comps[6], self._params['K_S']) \
                * self._monod(self._bulk_DO, self._params['K_OH']) \
                * self._comps[2]

    # Anoxic Growth Rate of Heterotrophs (_r1_AxGH, mgCOD/L/day)
    def _r1_AxGH (self):
        return  self._params['u_H'] \
                * self._monod(self._comps[6], self._params['K_S']) \
                * self._monod(self._params['K_OH'], self._bulk_DO) \
                * self._monod(self._comps[8], self._params['K_NO']) \
                * self._params['cf_g'] \
                * self._comps[2]

    # Aerobic Growth Rate of Autotrophs (_r2_AerGA, mgCOD/L/day)
    def _r2_AerGA(self):
        return  self._params['u_A'] \
                * self._monod(self._comps[9], self._params['K_NH']) \
                * self._monod(self._bulk_DO, self._params['K_OA']) \
                * self._comps[3]

    # Death and Lysis Rate of Heterotrophs (_r3_DLH, mgCOD/L/day)
    def _r3_DLH(self):
        return  self._params['b_LH'] * self._comps[2]

    # Death and Lysis Rate of Autotrophs (_r4_DLA, mgCOD/L/day)
    def _r4_DLA(self):
        return  self._params['b_LA'] * self._comps[3]

    # Ammonification Rate of Soluable Organic N (_r5_AmmSN, mgN/L/day)
    def _r5_AmmSN(self):
        return  self._params['k_a'] \
                * self._comps[10] \
                * self._comps[2]

    # Hydrolysis Rate of Particulate Organics (_r6_HydX, mgCOD/L/day)
    def _r6_HydX(self):
        return  self._params['k_h'] \
                * self._monod(self._comps[1] / self._comps[2], \
                                self._params['K_X']) \
                * (self._monod(self._bulk_DO, \
                                self._params['K_OH']) \
                    + self._params['cf_h'] \
                    * self._monod(self._params['K_OH'], self._bulk_DO) \
                    * self._monod(self._comps[8], \
                                    self._params['K_NO'])) \
                * self._comps[2]

    # Hydrolysis Rate of Part. Organic N (_r7_HydXN, mgN/L/day)
    def _r7_HydXN(self):
        return self._r6_HydX() * self._comps[11] / self._comps[1]

    #---------Overall Process Rate Equations for Individual Components---

    def _rate0_X_I(self):
        return 0

    def _rate1_X_S(self):
        return self._stoichs['3_1'] * self._r3_DLH() \
                + self._stoichs['4_1'] * self._r4_DLA() \
                + self._stoichs['6_1'] * self._r6_HydX()

    def _rate2_X_BH(self):
        return self._stoichs['0_2'] * self._r0_AerGH() \
                + self._stoichs['1_2'] * self._r1_AxGH() \
                + self._stoichs['3_2'] * self._r3_DLH()

    def _rate3_X_BA(self):
        return self._stoichs['2_3'] * self._r2_AerGA() \
                + self._stoichs['4_3'] * self._r4_DLA()

    def _rate4_X_D(self):
        return self._stoichs['3_4'] * self._r3_DLH() \
                + self._stoichs['4_4'] * self._r4_DLA()

    def _rate5_S_I(self):
        return 0

    def _rate6_S_S(self):
        return self._stoichs['0_6'] * self._r0_AerGH() \
                + self._stoichs['1_6'] * self._r1_AxGH() \
                + self._stoichs['6_6'] * self._r6_HydX()

    def _rate7_S_DO(self):
        return self._stoichs['0_7'] * self._r0_AerGH() \
                + self._stoichs['2_7'] * self._r2_AerGA()

    def _rate8_S_NO(self):
        return self._stoichs['1_8'] * self._r1_AxGH() \
                + self._stoichs['2_8'] * self._r2_AerGA()

    def _rate9_S_NH(self):
        return self._stoichs['0_9'] * self._r0_AerGH() \
                + self._stoichs['1_9'] * self._r1_AxGH() \
                + self._stoichs['2_9'] * self._r2_AerGA() \
                + self._stoichs['5_9'] * self._r5_AmmSN()

    def _rate10_S_NS(self):
        return self._stoichs['5_10'] * self._r5_AmmSN() \
                + self._stoichs['7_10'] * self._r7_HydXN()

    def _rate11_X_NS(self):
        return self._stoichs['3_11'] * self._r3_DLH() \
                + self._stoichs['4_11'] * self._r4_DLA() \
                + self._stoichs['7_11'] * self._r7_HydXN()

    def _rate12_S_Alk(self):
        return self._stoichs['0_12'] * self._r0_AerGH() \
                + self._stoichs['1_12'] * self._r1_AxGH() \
                + self._stoichs['2_12'] * self._r2_AerGA() \
                + self._stoichs['5_12'] * self._r5_AmmSN()


    def _steady(self, ExtCompList, InFlow, InfComp, Vol):
        '''
        Defines the steady state mass balance:
        Original variables in stand alone script: 
            (CompList, Parameters, Stoichiometrics, InfComp, SRT, Vol, Bulk_DO)
        InfComp is a List that represent the Influent values 
            (get them from the ASMReactor) of the ASM1 Components
        with the exception of InfComp[0] which is the Inf_Flow into the 
            reactor (m3/day), which may be different from 
            the overall plant influent.
            
            0_X_I, 1_X_S, 2_X_BH, 3_X_BA, 4_X_D
            5_S_I, 6_S_S, 7_S_DO, 8_S_NO, 9_S_NH, 10_S_NS, 11_X_NS, 12_S_ALK
        
        ASM1._bulk_DO in mgO2/L

        ExtCompList is a representation of self._Components in the
        definition of self._steady() in order to use scipy.optimize.fsolve(). 
        '''
        # TODO: The resulting ExtCompList values will need to be passed to
        #        self._Components
        # Steady state equations that calculate the simulation results:
        # FROM NOW ON: Reactor Influent Flow = Reactor Effluent Flow
        # Overall steady state mass balance:
        # InfFlow * (InfConc - EffConc) + GrowthRate * ActVol == 0


        # for C0_X_I, assume perfect solid-liquid separation 
        # (i.e. X_I = 0 mg/L in effluent)
        result = [InFlow * (InfComp[0] - ExtCompList[0]) \
                    + self._rate0_X_I() * Vol]

        # for C1_X_S, assume perfect solid-liquid separation 
        # (i.e. X_S = 0 mg/L in effluent)
        result.append(InFlow * (InfComp[1] - ExtCompList[1]) \
                        + self._rate1_X_S() * Vol)

        # for C2_X_BH, assume perfect solid-liquid separation 
        # (i.e. X_BH = 0 mg/L in effluent)
        result.append(InFlow * (InfComp[2] - ExtCompList[2]) \
                        + self._rate2_X_BH() * Vol)

        # for C3_X_BA, assume perfect solid-liquid separation 
        # (i.e. X_BA = 0 mg/L in effluent)
        result.append(InFlow * (InfComp[3] - ExtCompList[3]) \
                        + self._rate3_X_BA() * Vol)

        # for C4_X_D, assume perfect solid-liquid separation 
        # (i.e. X_D = 0.0 mg/L in effluent)
        result.append(InFlow * (InfComp[4] - ExtCompList[4]) \
                        + self._rate4_X_D() * Vol)

        #    for C5_S_I
        result.append(InFlow * (InfComp[5] - ExtCompList[5]) \
                        + self._rate5_S_I() * Vol)

        #    for C6_S_S
        result.append(InFlow * (InfComp[6] - ExtCompList[6]) \
                        + self._rate6_S_S() * Vol)

        #    for C7_S_DO
        result.append(InFlow * (InfComp[7] - ExtCompList[7]) \
                        + self._rate7_S_DO() * Vol)
        # result.append(CompList[8] - Bulk_DO)

        #    for C8_S_NO
        result.append(InFlow * (InfComp[8] - ExtCompList[8]) \
                        + self._rate8_S_NO() * Vol)

        #    for C9_S_NH
        result.append(InFlow * (InfComp[9] - ExtCompList[9]) \
                        + self._rate9_S_NH() * Vol)

        #    for C10_S_NS
        result.append(InFlow * (InfComp[10] - ExtCompList[10]) \
                        + self._rate10_S_NS() * Vol)

        #    for C11_X_NS
        result.append(InFlow * (InfComp[11] - ExtCompList[11]) \
                        + self._rate11_X_NS() * Vol)

        #    for C12_S_ALK
        result.append(InFlow * (InfComp[12] - ExtCompList[12]) \
                        + self._rate12_S_Alk() * Vol)

        return result


    def _dCdt(self, ExtCompList, InFlow, InfComp, Vol):
        '''
        Defines dC/dt for the system:
        Original variables in stand alone script: 
            (CompList, Parameters, Stoichiometrics, InfComp, SRT, Vol, Bulk_DO)
        InfComp is a List that represent the Influent values 
            (get them from the ASMReactor) of the ASM1 Components
            
            0_X_I, 1_X_S, 2_X_BH, 3_X_BA, 4_X_D
            5_S_I, 6_S_S, 7_S_DO, 8_S_NO, 9_S_NH, 10_S_NS, 11_X_NS, 12_S_ALK
        
        ASM1._bulk_DO in mgO2/L

        ExtCompList is a representation of self._Components in the
        definition of self._steady() in order to use scipy.optimize.fsolve(). 
        '''
        # TODO: The resulting ExtCompList values will need to be passed to
        #        self._Components
        # Steady state equations that calculate the simulation results:
        # FROM NOW ON: Reactor Influent Flow = Reactor Effluent Flow
        # Overall mass balance:
        # dComp/dt == InfFlow / ActVol * (InfConc - EffConc) + GrowthRate
        #          == (InfConc - EffConc) / HRT + GrowthRate

        _HRT = Vol / InFlow
        
        # for C0_X_I, assume perfect solid-liquid separation 
        # (i.e. X_I = 0 mg/L in effluent)
        result = [(InfComp[0] - ExtCompList[0]) / _HRT 
                        + self._rate0_X_I()]

        # for C1_X_S, assume perfect solid-liquid separation 
        # (i.e. X_S = 0 mg/L in effluent)
        result.append((InfComp[1] - ExtCompList[1]) / _HRT 
                        + self._rate1_X_S())

        # for C2_X_BH, assume perfect solid-liquid separation 
        # (i.e. X_BH = 0 mg/L in effluent)
        result.append((InfComp[2] - ExtCompList[2]) / _HRT
                        + self._rate2_X_BH())

        # for C3_X_BA, assume perfect solid-liquid separation 
        # (i.e. X_BA = 0 mg/L in effluent)
        result.append((InfComp[3] - ExtCompList[3]) / _HRT
                        + self._rate3_X_BA())

        # for C4_X_D, assume perfect solid-liquid separation 
        # (i.e. X_D = 0.0 mg/L in effluent)
        result.append((InfComp[4] - ExtCompList[4]) / _HRT
                        + self._rate4_X_D())

        #    for C5_S_I
        result.append((InfComp[5] - ExtCompList[5]) / _HRT
                        + self._rate5_S_I())

        #    for C6_S_S
        result.append((InfComp[6] - ExtCompList[6]) / _HRT
                        + self._rate6_S_S())

        #    for C7_S_DO
        result.append((InfComp[7] - ExtCompList[7]) / _HRT
                        + self._rate7_S_DO())
        # result.append(CompList[8] - Bulk_DO)

        #    for C8_S_NO
        result.append((InfComp[8] - ExtCompList[8]) / _HRT
                        + self._rate8_S_NO())

        #    for C9_S_NH
        result.append((InfComp[9] - ExtCompList[9]) / _HRT
                        + self._rate9_S_NH())

        #    for C10_S_NS
        result.append((InfComp[10] - ExtCompList[10]) / _HRT
                        + self._rate10_S_NS())

        #    for C11_X_NS
        result.append((InfComp[11] - ExtCompList[11]) / _HRT
                        + self._rate11_X_NS())

        #    for C12_S_ALK
        result.append((InfComp[12] - ExtCompList[12]) / _HRT
                        + self._rate12_S_Alk())

        return result
