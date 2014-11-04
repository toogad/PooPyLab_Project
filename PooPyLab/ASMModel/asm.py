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
#
#
#
#    This is the definition of the ASM1 model to be imported
#    as part of the Reactor object
#
#Change Log:
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
# S:    Substrate (COD or TKN, unit: mg/L)
# X:    Particulate matter as COD (unit: mg/L)
# S:    Soluble
# Inf:  Influent
# Eff:  Effluent
# TBD:  To Be Determined by user


import constants
from scipy.optimize import fsolve

class ASM1(object):

    def __init__(self, Temperature = 20.0, Bulk_DO = 2.0):

        self._Temperature = Temperature * 1.0
        self._Bulk_DO = Bulk_DO * 1.0
        
        # define the model parameters and stochoimetrics as dict() so that it
        # is easier to keep track of names and values
        self._Parameters = {}
        self._Stoichiometrics = {}
        self._Delta_Temp = 20.0 - self._Temperature
        
        # define a Python Dictionary to store Parameters
        self._Parameters = self._SetParameters()
        
        # define a Python Dictionary to store Stochoimetrics
        self._Stoichiometrics = self._SetStoichiometrics()
        
        # define a Python List to store ASM components
        # The Components the ASM components IN THE REACTOR. JULY 10, 2013
        # For ASM #1:
        #
        #    self._Components[0]: X_I
        #    self._Components[1]: X_S
        #    self._Components[2]: X_BH
        #    self._Components[3]: X_BA
        #    self._Components[4]: X_D
        #    self._Components[5]: S_I
        #    self._Components[6]: S_S
        #    self._Components[7]: S_DO
        #    self._Components[8]: S_NO
        #    self._Components[9]: S_NH
        #    self._Components[10]: S_NS
        #    self._Components[11]: X_NS
        #    self._Components[12]: S_ALK
        #
        self._Components=[0.0] * constants._NUM_ASM1_COMPONENTS

        return

    def _SetParameters(self):

        # Ideal Growth Rate of Heterotrophs (u_H, unit: 1/DAY)
        self._Parameters['u_H'] = 6.0 * pow(1.08, self._Delta_Temp)

        # Ideal Lysis Rate of Heterotrophs (b_LH, unit: 1/DAY)
        self._Parameters['b_LH'] = 0.408 * pow(1.04, self._Delta_Temp)

        # Ideal Growth Rate of Autotrophs (u_A, unit: 1/DAY)
        self._Parameters['u_A'] = 0.768 * pow(1.11, self._Delta_Temp)

        # Ideal Growth Rate of Autotrophs (b_LA, unit: 1/DAY)
        self._Parameters['b_LA'] = 0.096 * pow(1.04, self._Delta_Temp)

        # Half Growth Rate Concentration of Heterotrophs (K_s, unit: mgCOD/L)
        self._Parameters['K_S'] = 20.0

        # Switch Coefficient for Dissoved O2 of Hetero. (K_OH, unit: mgO2/L)
        self._Parameters['K_OH'] = 0.1

        # Association Conc. for Dissoved O2 of Auto. (K_OA, unit: mgN/L)
        self._Parameters['K_OA'] = 0.75

        # Association Conc. for NH3-N of Auto. (K_NH, unit: mgN/L)
        self._Parameters['K_NH'] = 1.0 * pow(1.14, self._Delta_Temp)

        # Association Conc. for NOx of Hetero. (K_NO, unit: mgN/L)
        self._Parameters['K_NO'] = 0.2

        # Hydrolysis Rate (k_h, unit: mgCOD/mgBiomassCOD-day)
        self._Parameters['k_h'] = 2.208 * pow(1.08, self._Delta_Temp)

        # Half Rate Conc. for Hetro. Growth on Part. COD
        # (K_X, unit: mgCOD/mgBiomassCOD)
        self._Parameters['K_X'] = 0.15

        # Ammonification of Org-N in biomass (k_a, unit: L/mgBiomassCOD-day)
        self._Parameters['k_a'] = 0.1608 * pow(1.08, self._Delta_Temp)

        # Yield of Hetero. Growth on COD (Y_H, unit: mgBiomassCOD/mgCOD-removed)
        self._Parameters['Y_H'] = 0.6

        # Yield of Auto. Growth on TKN (Y_A, unit: mgBiomassCOD/mgTKN-oxidized)
        self._Parameters['Y_A'] = 0.24

        # Fract. of Debris in Lysed Biomass(f_D_,unit: mgDebrisCOD/mgBiomassCOD)
        self._Parameters['f_D_'] = 0.08

        # Correction Factor for Hydrolysis (cf_h, unitless)
        self._Parameters['cf_h'] = 0.4

        # Correction Factor for Anoxic Heterotrophic Growth (cf_g, unitless)
        self._Parameters['cf_g'] = 0.8

        # Ratio of N in Active Biomass (i_N_XB, unit: mgN/mgActiveBiomassCOD)
        self._Parameters['i_N_XB'] = 0.086

        # Ratio of N in Debris Biomass (i_N_XD, unit: mgN/mgDebrisBiomassCOD)
        self._Parameters['i_N_XD'] = 0.06

        return self._Parameters
    #=============================== End of Parameter Definition =====================

    # STOCHIOMETRIC MATRIX (Use the Table 6.1, p193, Grady Jr. et al 1999)
    def _SetStoichiometrics(self):

        self._Stoichiometrics['0_2'] = 1.0

        self._Stoichiometrics['0_6'] = -1.0 / self._Parameters['Y_H']

        self._Stoichiometrics['0_7'] = -(1.0 - self._Parameters['Y_H']) / \
                                        self._Parameters['Y_H']
                                        #multiply -1.0 to express as oxygen

        self._Stoichiometrics['0_9'] = -self._Parameters['i_N_XB']

        self._Stoichiometrics['0_12'] = -self._Parameters['i_N_XB'] / 14.0

        self._Stoichiometrics['1_2'] = 1.0

        self._Stoichiometrics['1_6'] = -1.0 / self._Parameters['Y_H']

        self._Stoichiometrics['1_8'] = -(1.0 - self._Parameters['Y_H']) / \
                                        (2.86 * self._Parameters['Y_H'])

        self._Stoichiometrics['1_9'] = -self._Parameters['i_N_XB']

        self._Stoichiometrics['1_12'] = (1.0 - self._Parameters['Y_H']) / \
                                        (14.0 * 2.86 * self._Parameters['Y_H']) - \
                                        self._Parameters['i_N_XB'] / 14.0

        self._Stoichiometrics['2_3'] = 1.0

        self._Stoichiometrics['2_7'] = -(4.57 - self._Parameters['Y_A']) / \
                                        self._Parameters['Y_A']
                                        #multiply -1.0 to express as oxygen

        self._Stoichiometrics['2_8'] = 1.0 / self._Parameters['Y_A']

        self._Stoichiometrics['2_9'] = -self._Parameters['i_N_XB'] - \
                                        1.0 / self._Parameters['Y_A']

        self._Stoichiometrics['2_12'] = (-1.0) * self._Parameters['i_N_XB'] / 14.0\
                                        - 1.0 / (7.0 * self._Parameters['Y_A'])

        self._Stoichiometrics['3_1'] = 1.0 - self._Parameters['f_D_']

        self._Stoichiometrics['3_2'] = -1.0

        self._Stoichiometrics['3_4'] = self._Parameters['f_D_']

        self._Stoichiometrics['3_11'] = self._Parameters['i_N_XB'] - \
                                        self._Parameters['f_D_'] * \
                                        self._Parameters['i_N_XD']

        self._Stoichiometrics['4_1'] = 1.0 - self._Parameters['f_D_']

        self._Stoichiometrics['4_3'] = -1.0

        self._Stoichiometrics['4_4'] = self._Parameters['f_D_']

        self._Stoichiometrics['4_11'] = self._Parameters['i_N_XB'] - \
                                        self._Parameters['f_D_'] * \
                                        self._Parameters['i_N_XD']

        self._Stoichiometrics['5_9'] = 1.0

        self._Stoichiometrics['5_10'] = -1.0

        self._Stoichiometrics['5_12'] = 1.0 / 14.0

        self._Stoichiometrics['6_1'] = -1.0

        self._Stoichiometrics['6_6'] = 1.0

        self._Stoichiometrics['7_10'] = 1.0

        self._Stoichiometrics['7_11'] = -1.0

        return self._Stoichiometrics
    ##=========================== End of Stoichiometrics ===========================

    # PROCESS RATE DEFINITIONS (Rj, unit: M/L^3/T):

    # The following factors/swithes all use the _Monod() function
    # Monod Factor of Sol.BioDegrad.COD on Hetero.
    # Monod Switch of Dissol. O2 on Hetero.
    # Monod Switch of Dissol. O2 on Auto.
    # Monod Factor of Ammonia-N on Autotrophs
    # Monod Factor of NOx-N on Autotrophs
    #
    def _Monod (self, My_Eff_S_TBD, My_K_TBD):
        return My_Eff_S_TBD / (My_Eff_S_TBD + My_K_TBD)

    # Aerobic Growth Rate of Heterotrophs (_r0_AerGH, unit: mgCOD/L/day)
    def _r0_AerGH (self):
        return  self._Parameters['u_H'] * \
                self._Monod(self._Components[6], self._Parameters['K_S']) * \
                self._Monod(self._Bulk_DO, self._Parameters['K_OH']) * \
                self._Components[2]

    # Anoxic Growth Rate of Heterotrophs (_r1_AxGH, unit: mgCOD/L/day)
    def _r1_AxGH (self):
        return  self._Parameters['u_H'] * \
                self._Monod(self._Components[6], self._Parameters['K_S']) * \
                self._Monod(self._Parameters['K_OH'], self._Bulk_DO) * \
                self._Monod(self._Components[8], self._Parameters['K_NO']) * \
                self._Parameters['cf_g'] * \
                self._Components[2]

    # Aerobic Growth Rate of Autotrophs (_r2_AerGA, unit: mgCOD/L/day)
    def _r2_AerGA(self):
        return  self._Parameters['u_A'] * \
                self._Monod(self._Components[9], self._Parameters['K_NH']) * \
                self._Monod(self._Bulk_DO, self._Parameters['K_OA']) * \
                self._Components[3]

    # Death and Lysis Rate of Heterotrophs (_r3_DLH, unit: mgCOD/L/day)
    def _r3_DLH(self):
        return  self._Parameters['b_LH'] * self._Components[2]

    # Death and Lysis Rate of Autotrophs (_r4_DLA, unit: mgCOD/L/day)
    def _r4_DLA(self):
        return  self._Parameters['b_LA'] * self._Components[3]

    # Ammonification Rate of Soluable Organic N (_r5_AmmSN, unit: mgN/L/day)
    def _r5_AmmSN(self):
        return  self._Parameters['k_a'] * self._Components[10] * self._Components[2]

    # Hydrolysis Rate of Particulate Organics (_r6_HydX, unit: mgCOD/L/day)
    def _r6_HydX(self):
        return  self._Parameters['k_h'] * \
                self._Monod(self._Components[1]/self._Components[2],self._Parameters['K_X'])*\
                (self._Monod(self._Bulk_DO, self._Parameters['K_OH']) + \
                 self._Parameters['cf_h'] * self._Monod(self._Parameters['K_OH'], self._Bulk_DO) * \
                 self._Monod(self._Components[8], self._Parameters['K_NO'])) * \
                 self._Components[2]

    # Hydrolysis Rate of Part. Organic N (_r7_HydXN, unit: mgN/L/day)
    def _r7_HydXN(self):
        return self._r6_HydX() * self._Components[11] / self._Components[1]

    #---------Overall Process Rate Equations for Individual Components---

    def _Rate0_X_I(self):
        return 0.0

    def _Rate1_X_S(self):
        return (self._Stoichiometrics['3_1'] * self._r3_DLH() + \
                   self._Stoichiometrics['4_1'] * self._r4_DLA() + \
                   self._Stoichiometrics['6_1'] * self._r6_HydX())

    def _Rate2_X_BH(self):
        return (self._Stoichiometrics['0_2'] * self._r0_AerGH() + \
                   self._Stoichiometrics['1_2'] * self._r1_AxGH() + \
                   self._Stoichiometrics['3_2'] * self._r3_DLH())

    def _Rate3_X_BA(self):
        return (self._Stoichiometrics['2_3'] * self._r2_AerGA() + \
                   self._Stoichiometrics['4_3'] * self._r4_DLA())

    def _Rate4_X_D(self):
        return (self._Stoichiometrics['3_4'] * self._r3_DLH() + \
                   self._Stoichiometrics['4_4'] * self._r4_DLA())

    def _Rate5_S_I(self):
        return 0.0

    def _Rate6_S_S(self):
        return (self._Stoichiometrics['0_6'] * self._r0_AerGH() + \
                   self._Stoichiometrics['1_6'] * self._r1_AxGH() + \
                   self._Stoichiometrics['6_6'] * self._r6_HydX())

    def _Rate7_S_DO(self):
        return (self._Stoichiometrics['0_7'] * self._r0_AerGH() + \
                   self._Stoichiometrics['2_7'] * self._r2_AerGA())

    def _Rate8_S_NO(self):
        return (self._Stoichiometrics['1_8'] * self._r1_AxGH() + \
                   self._Stoichiometrics['2_8'] * self._r2_AerGA())

    def _Rate9_S_NH(self):
        return (self._Stoichiometrics['0_9'] * self._r0_AerGH() + \
                   self._Stoichiometrics['1_9'] * self._r1_AxGH() + \
                   self._Stoichiometrics['2_9'] * self._r2_AerGA() + \
                   self._Stoichiometrics['5_9'] * self._r5_AmmSN())

    def _Rate10_S_NS(self):
        return (self._Stoichiometrics['5_10'] * self._r5_AmmSN() + \
                   self._Stoichiometrics['7_10'] * self._r7_HydXN())

    def _Rate11_X_NS(self):
        return (self._Stoichiometrics['3_11'] * self._r3_DLH() + \
                    self._Stoichiometrics['4_11'] * self._r4_DLA() + \
                    self._Stoichiometrics['7_11'] * self._r7_HydXN())

    def _Rate12_S_Alk(self):
        return (self._Stoichiometrics['0_12'] * self._r0_AerGH() + \
                    self._Stoichiometrics['1_12'] * self._r1_AxGH() + \
                    self._Stoichiometrics['2_12'] * self._r2_AerGA() + \
                    self._Stoichiometrics['5_123'] * self._r5_AmmSN())


    def _Steady(self, ExtCompList, InFlow, InfComp, Vol):
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
        
        ASM1._Bulk_DO in mgO2/L

        ExtCompList is a representation of self._Components in the
        definition of self._Steady() in order to use scipy.optimize.fsolve(). 
        #TODO: The resulting ExtCompList values will need to be passed to 
            self._Components
        '''
        # Steady state equations that calculate the simulation results:
        # FROM NOW ON: Reactor Influent Flow = Reactor Effluent Flow
        # Overall steady state mass balance:
        # InfFlow * (InfConc - EffConc) + GrowthRate * ActVol == 0


        # for C0_X_I, assume perfect solid-liquid separation (i.e. X_I = 0.0 mg/L
        # in effluent)
        result = [InFlow * (InfComp[0] - ExtCompList[0]) + self._Rate0_X_I() * Vol]

        # for C1_X_S, assume perfect solid-liquid separation (i.e. X_S = 0.0 mg/L
        # in effluent)
        result.append(InFlow * (InfComp[1] - ExtCompList[1]) + self._Rate1_X_S() * Vol)

        # for C2_X_BH, assume perfect solid-liquid separation (i.e. X_BH = 0.0
        # mg/L in effluent)
        result.append(InFlow * (InfComp[2] - ExtCompList[2]) + self._Rate2_X_BH() * Vol)

        # for C3_X_BA, assume perfect solid-liquid separation (i.e. X_BA = 0.0
        # mg/L in effluent)
        result.append(InFlow * (InfComp[3] - ExtCompList[3]) + self._Rate3_X_BA() * Vol)

        # for C4_X_D, assume perfect solid-liquid separation (i.e. X_D = 0.0 mg/L
        # in effluent)
        result.append(InFlow * (InfComp[4] - ExtCompList[4]) + self._Rate4_X_D() * Vol)

        #    for C5_S_I
        result.append(InFlow * (InfComp[5] - ExtCompList[5]) + self._Rate5_S_I() * Vol)

        #    for C6_S_S
        result.append(InFlow * (InfComp[6] - ExtCompList[6]) + self._Rate6_S_S() * Vol)

        #    for C7_S_DO
        result.append(InFlow * (InfComp[7] - ExtCompList[7]) + self._Rate7_S_DO() * Vol)
        # result.append(CompList[8] - Bulk_DO)

        #    for C8_S_NO
        result.append(InFlow * (InfComp[8] - ExtCompList[8]) + self._Rate8_S_NO() * Vol)

        #    for C9_S_NH
        result.append(InFlow * (InfComp[9] - ExtCompList[9]) + self._Rate9_S_NH() * Vol)

        #    for C10_S_NS
        result.append(InFlow * (InfComp[10] - ExtCompList[10]) + self._Rate10_S_NS() * Vol)

        #    for C11_X_NS
        result.append(InFlow * (InfComp[11] - ExtCompList[11]) + self._Rate11_X_NS() * Vol)

        #    for C12_S_ALK
        result.append(InFlow * (InfComp[12] - ExtCompList[12]) + self._Rate12_S_Alk() * Vol)

        return result
    #====================End of Private Fuction Definitions =========================


    #====================== Public Interface ===================================

    def SteadyStep(self, GuessState, Inflow, InfComp, Vol):
        '''
            Calculate the state of this round of iteration.
            Pass the results to the storing List() in the ASMReactor.
            The results of this calculation should be compared with those of the last round,
            and determine whether the reactor has reached a steady state.
        '''
        CurrentState = fsolve(self._Steady, GuessState, (Inflow, InfComp, Vol))
        return CurrentState

    def Update(self, Temperature, Bulk_DO):
        ''' update the ASM model with new Temperature and Bulk_DO'''
        if Temperature <= 4.0 or Bulk_DO < 0.0:
            print ("Error: New temperature or Bulk_DO too low. USING PREVIOUS VALUES FOR BOTH")
            return -1

        self._Temperature = Temperature * 1.0
        self._Bulk_DO = Bulk_DO * 1.0
        self._Delta_Temp = 20.0 - self._Temperature
        self._Parameters = self._SetParameters()
        self._Stoichiometrics = self._SetStoichiometrics()
        return None

    def GetParameters(self):
        return self._Parameters

    def GetStoichiometrics(self):
        return self._Stoichiometrics

    def GetAllComponents(self):
        #TODO: Need to determine where to provide GetAllComponents(), in ASMReactor or here?
        return self._Components

    def GetBulkDO(self):
        return self._Bulk_DO
    
     
