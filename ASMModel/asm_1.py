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
#    This is the definition of the ASM1 model to be imported
#    as part of the Reactor object
#
#


from ASMModel import constants

"""@package asm_1
Definition of the IWA Activated Sludge Model #1.

"SUBSCRIPTS" USED IN VARIABLE NAMES:
 rb:   readily biodegradable
 nrb:  non-readily biodegradable
 O:    Oxygen
 NH:   Ammonia
 L:    Lysis
 H:    Heterotrophs
 h:    Hydrolysis
 a:    Ammonification
 i:    ratio
 f:    fraction
 cf:   correction factor
 A:    Autotrophs
 B:    Biomass (active)
 D:    Debris
 NO:   NOx (oxidized nitrogen)
 I:    Inert
 ALK:  Alkalinity
 S:    Substrate (COD or TKN, mg/L)
 X:    Particulate matter as COD ( mg/L)
 S:    Soluble
 Inf:  Influent
 Eff:  Effluent
 TBD:  To Be Determined by user
"""

class ASM_1():

    def __init__(self, WWtemp=20, DO=2):

        self._temperature = WWtemp
        self._bulk_DO = DO 
        
        # define the model parameters and stochoimetrics as dict() so that it
        # is easier to keep track of names and values
        self._params = {}
        self._stoichs = {}
        self._delta_t = 20.0 - self._temperature
        
        self._set_params()
        
        self._set_stoichs()
        
        # ASM components
        # The Components the ASM components IN THE REACTOR
        # For ASM #1:
        #
        #    self._comps[0]: S_DO as COD
        #    self._comps[1]: S_I
        #    self._comps[2]: S_S
        #    self._comps[3]: S_NH
        #    self._comps[4]: S_NS
        #    self._comps[5]: S_NO
        #    self._comps[6]: S_ALK
        #    self._comps[7]: X_I
        #    self._comps[8]: X_S
        #    self._comps[9]: X_BH
        #    self._comps[10]: X_BA
        #    self._comps[11]: X_D
        #    self._comps[12]: X_NS
        #
        self._comps = [0.0] * constants._NUM_ASM1_COMPONENTS

        return


    #====================== Public Interface ==================================


    def update(self, ww_temp, dissolved_O2):
        """ Update the ASM model with new Temperature and Bulk_DO. """
        self._temperature = ww_temp
        self._bulk_DO = dissolved_O2
        self._delta_t = self._temperature - 20.0
        self._param = self._set_params()
        self._stoich = self._set_stoichs()
        return 0


    def get_params(self):
        return self._params.copy()


    def get_stoichs(self):
        return self._stoichs.copy()


    def get_all_comps(self):
        return self._comps[:]


    def get_bulk_DO(self):
        return self._bulk_DO

    #====================== End of Public Interface ==================

    def _set_params(self):

        # Ideal Growth Rate of Heterotrophs (u_max_H, 1/DAY)
        self._params['u_max_H'] = 6.0 * pow(1.072, self._delta_t)

        # Decay Rate of Heterotrophs (b_H, 1/DAY)
        self._params['b_LH'] = 0.62 * pow(1.12, self._delta_t)

        # Ideal Growth Rate of Autotrophs (u_max_A, 1/DAY)
        self._params['u_max_A'] = 0.8 * pow(1.103, self._delta_t)

        # Decay Rate of Autotrophs (b_A, 1/DAY)
        # A wide range exists. Table 6.3 on Grady 1999 shows 0.096 (1/d). IWA's
        # ASM report did not even show b_A on its table for typical value. ASIM
        # software show a value of "0.000", probably cut off by the print
        # function. I can only assume it was < 0.0005 (1/d) at 20C.
        #self._params['b_LA'] = 0.096 * pow(1.114, self._delta_t)
        self._params['b_LA'] = 0.0007 * pow(1.114, self._delta_t)

        # Half Growth Rate Concentration of Heterotrophs (K_s, mgCOD/L)
        self._params['K_S'] = 20.0

        # Switch Coefficient for Dissoved O2 of Hetero. (K_OH, mgO2/L)
        self._params['K_OH'] = 0.2

        # Association Conc. for Dissoved O2 of Auto. (K_OA, mgN/L)
        self._params['K_OA'] = 0.4

        # Association Conc. for NH3-N of Auto. (K_NH, mgN/L)
        self._params['K_NH'] = 1.0

        # Association Conc. for NOx of Hetero. (K_NO, mgN/L)
        self._params['K_NO'] = 0.5

        # Hydrolysis Rate (k_h, mgCOD/mgBiomassCOD-day)
        self._params['k_h'] = 3.0 * pow(1.116, self._delta_t)

        # Half Rate Conc. for Hetero. Growth on Part. COD
        # (K_X, mgCOD/mgBiomassCOD)
        self._params['K_X'] = 0.03 * pow(1.116, self._delta_t)

        # Ammonification of Org-N in biomass (k_a, L/mgBiomassCOD-day)
        self._params['k_a'] = 0.08 * pow(1.072, self._delta_t)

        # Yield of Hetero. Growth on COD (Y_H, mgBiomassCOD/mgCODremoved)
        self._params['Y_H'] = 0.67

        # Yield of Auto. Growth on TKN (Y_A, mgBiomassCOD/mgTKNoxidized)
        self._params['Y_A'] = 0.24

        # Fract. of Debris in Lysed Biomass(f_D, gDebrisCOD/gBiomassCOD)
        self._params['f_D'] = 0.08

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

    # STOCHIOMETRIC MATRIX 
    # (make sure to match the .csv model template file in the model_builder
    # folder, Sep 04, 2019)
    # _stoichs['x_y'] ==> x is process rate id, and y is component id
    def _set_stoichs(self):

        # S_O for aerobic hetero. growth, as O2
        self._stoichs['0_0'] = (self._params['Y_H'] - 1.0) \
                                / self._params['Y_H']

        # S_O for aerobic auto. growth, as O2
        self._stoichs['2_0'] = (self._params['Y_A'] - 4.57) \
                                / self._params['Y_A']
 

        # S_S for aerobic hetero. growth, as COD
        self._stoichs['0_2'] = -1.0 / self._params['Y_H'] 

        # S_S for anoxic hetero. growth, as COD
        self._stoichs['1_2'] = -1.0 / self._params['Y_H']  

        # S_S for hydrolysis of part. substrate
        self._stoichs['6_2'] = 1.0


        # S_NH required for aerobic hetero. growth, as N
        self._stoichs['0_3'] = -self._params['i_N_XB']

        # S_NH required for anoxic hetero. growth, as N
        self._stoichs['1_3'] = -self._params['i_N_XB']

        # S_NH required for aerobic auto. growth, as N
        self._stoichs['2_3'] = -self._params['i_N_XB'] \
                                - 1.0 / self._params['Y_A']

        # S_NH from ammonification, as N
        self._stoichs['5_3'] = 1.0

        
        # S_NS used by ammonification, as N
        self._stoichs['5_4'] = -1.0

        # S_NS from hydrolysis of part.TKN, as N
        self._stoichs['7_4'] = 1.0
        

        # S_NO for anoxic hetero. growth, as N
        self._stoichs['1_5'] = (self._params['Y_H'] - 1.0) \
                                / (2.86 * self._params['Y_H'])
 
        # S_NO from nitrification, as N
        self._stoichs['2_5'] = 1.0 / self._params['Y_A']

        # S_ALK consumed by aerobic hetero. growth, as mM CaCO3
        self._stoichs['0_6'] = -self._params['i_N_XB'] / 14.0

        # S_ALK generated by anoxic hetero. growth, as mM CaCO3
        self._stoichs['1_6'] = (1.0 - self._params['Y_H']) \
                                / (14.0 * 2.86 * self._params['Y_H']) \
                                - self._params['i_N_XB'] / 14.0

        # S_ALK consumed by aerobic auto. growth, as mM CaCO3
        self._stoichs['2_6'] = -self._params['i_N_XB'] / 14 \
                                - 1.0 / (7.0 * self._params['Y_A'])

        # S_ALK generated by ammonification, as mM CaCO3
        self._stoichs['5_6'] = 1.0 / 14.0


        # X_S from hetero. decay, as COD
        self._stoichs['3_8'] = 1.0 - self._params['f_D']

        # X_S from auto. decay, as COD
        self._stoichs['4_8'] = 1.0 - self._params['f_D']

        # X_S consumed by hydrolysis of biomass
        self._stoichs['6_8'] = -1.0


        # X_BH from aerobic hetero. growth, as COD
        self._stoichs['0_9'] = 1.0

        # X_BH from anoxic hetero. growth, as COD
        self._stoichs['1_9'] = 1.0

        # X_BH lost in hetero. decay, as COD
        self._stoichs['3_9'] = -1.0


        # X_BA from aerobic auto. growth, as COD
        self._stoichs['2_10'] = 1.0

        # X_BA lost in auto. decay, as COD
        self._stoichs['4_10'] = -1.0


        # X_D from hetero. decay, as COD
        self._stoichs['3_11'] = self._params['f_D']

        # X_D from auto. decay, as COD
        self._stoichs['4_11'] = self._params['f_D']


        # X_NS from hetero. decay, as N
        self._stoichs['3_12'] = self._params['i_N_XB'] - self._params['f_D'] \
                                * self._params['i_N_XD']

        # X_NS from auto. decay, as COD
        self._stoichs['4_12'] = self._params['i_N_XB'] - self._params['f_D'] \
                                * self._params['i_N_XD']

        # X_NS consumed in hydrolysis of part. TKN, as N
        self._stoichs['7_12'] = -1.0

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
    def _monod(self, term_in_nom_denom, term_only_in_denom):
        return term_in_nom_denom / (term_in_nom_denom + term_only_in_denom)


    # Aerobic Growth Rate of Heterotrophs (_r0_AerGH, mgCOD/L/day)
    def _r0_AerGH(self, comps):
        return  self._params['u_max_H'] \
                * self._monod(comps[2], self._params['K_S']) \
                * self._monod(self._bulk_DO, self._params['K_OH']) \
                * comps[9]


    # Anoxic Growth Rate of Heterotrophs (_r1_AxGH, mgCOD/L/day)
    def _r1_AxGH(self, comps):
        return  self._params['u_max_H'] \
                * self._monod(comps[2], self._params['K_S']) \
                * self._monod(self._params['K_OH'], self._bulk_DO) \
                * self._monod(comps[5], self._params['K_NO']) \
                * self._params['cf_g'] \
                * comps[9]


    # Aerobic Growth Rate of Autotrophs (_r2_AerGA, mgCOD/L/day)
    def _r2_AerGA(self, comps):
        return  self._params['u_max_A'] \
                * self._monod(comps[3], self._params['K_NH']) \
                * self._monod(self._bulk_DO, self._params['K_OA']) \
                * comps[10]


    # Death and Lysis Rate of Heterotrophs (_r3_DLH, mgCOD/L/day)
    def _r3_DLH(self, comps):
        return  self._params['b_LH'] * comps[9]


    # Death and Lysis Rate of Autotrophs (_r4_DLA, mgCOD/L/day)
    def _r4_DLA(self, comps):
        return  self._params['b_LA'] * comps[10]


    # Ammonification Rate of Soluable Organic N (_r5_AmmSN, mgN/L/day)
    def _r5_AmmSN(self, comps):
        return  self._params['k_a'] \
                * comps[4] \
                * comps[9]


    # Hydrolysis Rate of Particulate Organics (_r6_HydX, mgCOD/L/day)
    def _r6_HydX(self, comps):
        return  self._params['k_h'] \
                * self._monod(comps[8] / comps[9], \
                                self._params['K_X']) \
                * (self._monod(self._bulk_DO, self._params['K_OH']) \
                    + self._params['cf_h'] \
                    * self._monod(self._params['K_OH'], self._bulk_DO) \
                    * self._monod(comps[5], self._params['K_NO'])) \
                * comps[9]


    # Hydrolysis Rate of Part. Organic N (_r7_HydXN, mgN/L/day)
    def _r7_HydXN(self, comps):
        return self._r6_HydX(comps) * comps[12] / comps[8]


    #---------Overall Process Rate Equations for Individual Components---

    def _rate0_S_DO(self, comps):
        return self._stoichs['0_0'] * self._r0_AerGH(comps)\
                + self._stoichs['2_0'] * self._r2_AerGA(comps)


    def _rate1_S_I(self, comps):
        return 0


    def _rate2_S_S(self, comps):
        return self._stoichs['0_2'] * self._r0_AerGH(comps)\
                + self._stoichs['1_2'] * self._r1_AxGH(comps)\
                + self._stoichs['6_2'] * self._r6_HydX(comps)


    def _rate3_S_NH(self, comps):
        return self._stoichs['0_3'] * self._r0_AerGH(comps)\
                + self._stoichs['1_3'] * self._r1_AxGH(comps)\
                + self._stoichs['2_3'] * self._r2_AerGA(comps)\
                + self._stoichs['5_3'] * self._r5_AmmSN(comps)


    def _rate4_S_NS(self, comps):
        return self._stoichs['5_4'] * self._r5_AmmSN(comps)\
                + self._stoichs['7_4'] * self._r7_HydXN(comps)


    def _rate5_S_NO(self, comps):
        return self._stoichs['1_5'] * self._r1_AxGH(comps)\
                + self._stoichs['2_5'] * self._r2_AerGA(comps)


    def _rate6_S_ALK(self, comps):
        return self._stoichs['0_6'] * self._r0_AerGH(comps)\
                + self._stoichs['1_6'] * self._r1_AxGH(comps)\
                + self._stoichs['2_6'] * self._r2_AerGA(comps)\
                + self._stoichs['5_6'] * self._r5_AmmSN(comps)


    def _rate7_X_I(self, comps):
        return 0


    def _rate8_X_S(self, comps):
        return self._stoichs['3_8'] * self._r3_DLH(comps)\
                + self._stoichs['4_8'] * self._r4_DLA(comps)\
                + self._stoichs['6_8'] * self._r6_HydX(comps)


    def _rate9_X_BH(self, comps):
        return self._stoichs['0_9'] * self._r0_AerGH(comps)\
                + self._stoichs['1_9'] * self._r1_AxGH(comps)\
                + self._stoichs['3_9'] * self._r3_DLH(comps)


    def _rate10_X_BA(self, comps):
        return self._stoichs['2_10'] * self._r2_AerGA(comps)\
                + self._stoichs['4_10'] * self._r4_DLA(comps)


    def _rate11_X_D(self, comps):
        return self._stoichs['3_11'] * self._r3_DLH(comps)\
                + self._stoichs['4_11'] * self._r4_DLA(comps)


    def _rate12_X_NS(self, comps):
        return self._stoichs['3_12'] * self._r3_DLH(comps)\
                + self._stoichs['4_12'] * self._r4_DLA(comps)\
                + self._stoichs['7_12'] * self._r7_HydXN(comps)


    def _dCdt(self, vol, flow, in_comps, mo_comps):
        '''
        Defines dC/dt for the system:
        in_comps/mo_comps are lists that represent the inlet/mainstream outlet 
        values of the ASM1 Components:
            
        0_S_DO, 1_S_I, 2_S_S, 3_S_NH, 4_S_NS, 5_S_NO, 6_S_ALK
        7_X_I, 8_X_S, 9_X_BH, 10_X_BA, 11_X_D, 12_X_NS
        '''
        # in_comps: inlet model components (concentrations)
        # mo_comps: outlet model components, this is provided to 

        # Overall mass balance:
        # dComp/dt == InfFlow / Actvol * (in_comps - mo_comps) + GrowthRate
        #          == (in_comps - mo_comps) / HRT + GrowthRate
        
        _HRT = vol / flow
        
        #result = [(in_comps[0] - mo_comps[0]) / _HRT 
        #                + self._rate0_S_DO()]

        # set DO rate to zero since DO is set to a fix conc.
        result = [0.0]

        result.append((in_comps[1] - mo_comps[1]) / _HRT 
                        + self._rate1_S_I(mo_comps))

        result.append((in_comps[2] - mo_comps[2]) / _HRT
                        + self._rate2_S_S(mo_comps))

        result.append((in_comps[3] - mo_comps[3]) / _HRT
                        + self._rate3_S_NH(mo_comps))

        result.append((in_comps[4] - mo_comps[4]) / _HRT
                        + self._rate4_S_NS(mo_comps))

        result.append((in_comps[5] - mo_comps[5]) / _HRT
                        + self._rate5_S_NO(mo_comps))

        result.append((in_comps[6] - mo_comps[6]) / _HRT
                        + self._rate6_S_ALK(mo_comps))

        result.append((in_comps[7] - mo_comps[7]) / _HRT
                        + self._rate7_X_I(mo_comps))

        result.append((in_comps[8] - mo_comps[8]) / _HRT
                        + self._rate8_X_S(mo_comps))

        result.append((in_comps[9] - mo_comps[9]) / _HRT
                        + self._rate9_X_BH(mo_comps))

        result.append((in_comps[10] - mo_comps[10]) / _HRT
                        + self._rate10_X_BA(mo_comps))

        result.append((in_comps[11] - mo_comps[11]) / _HRT
                        + self._rate11_X_D(mo_comps))

        result.append((in_comps[12] - mo_comps[12]) / _HRT
                        + self._rate12_X_NS(mo_comps))

        return result[:]
