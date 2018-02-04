#=============================================================================
# Python Implementation of the IWA Activated Sludge Model 1 (ASM1)
# Based on Grady Jr. et al (1999)
# ASM1 provides simulation basis for activated sludge processes with
#   1. COD removal
#   2. Nitrification 
#   3. Denitrification
# Biological phosphorus removal (BPR) is not part of ASM1
#
# This Python implementation is to focus on how to construct the model in 
#  computer programs. 
# pyASM1v0_6.py has successfully model the steady state of a single CSTR
#  with ASM1.
#
# Last Update: 2018-02-03...KZ..migrated to Python3
#=============================================================================


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

import scipy.optimize

# PARAMETER DEFINITIONS:

# 0.0 Default Growth Rates at 20 C. 
#   THEY SHALL BE ADJUSTED TO PROJECT SPECIFIC TEMPERATURE
#    S_DO, u_H, b_LH, u_A, b_LA 
#    K_S, K_OH, K_NH, K_OA, K_NO, k_h, K_X, k_a, Y_H, Y_A
#    f_D_, cf_h, cf_g, i_N_XB, i_N_XD

def SetGlobalParameters(Temp=20.0): # Temp = Temperature (unit: degree C)
    
    Delta_Temp = Temp - 20.0
    
    # define a Python Dictionary to store Global Parameters
    Global_Parameters = dict()
     
    #0.1 Ideal Growth Rate of Heterotrophs (u_H, unit: 1/DAY)
    Global_Parameters['u_H'] = 6.0 * pow(1.08, Delta_Temp)
    
    #0.2 Ideal Lysis Rate of Heterotrophs (b_LH, unit: 1/DAY)
    Global_Parameters['b_LH'] = 0.408 * pow(1.04, Delta_Temp)

    #0.3 Ideal Growth Rate of Autotrophs (u_A, unit: 1/DAY)
    Global_Parameters['u_A'] = 0.768 * pow(1.11, Delta_Temp)

    #0.4 Ideal Growth Rate of Autotrophs (b_LA, unit: 1/DAY)
    Global_Parameters['b_LA'] = 0.096 * pow(1.04, Delta_Temp)
    
    #0.5 Half Growth Rate Concentration of Heterotrophs (K_s, unit: mgCOD/L)
    Global_Parameters['K_S'] = 20.0

    #0.6 Switch Coefficient for Dissoved O2 of Hetero. (K_OH, unit: mgO2/L)
    Global_Parameters['K_OH'] = 0.1

    #0.7 Association Conc. for Dissoved O2 of Auto. (K_OA, unit: mgN/L)
    Global_Parameters['K_OA'] = 0.75

    #0.8 Association Conc. for NH3-N of Auto. (K_NH, unit: mgN/L)
    Global_Parameters['K_NH'] = 1.0 * pow(1.14, Delta_Temp)
    
    # 0.9 Association Conc. for NOx of Hetero. (K_NO, unit: mgN/L)
    Global_Parameters['K_NO'] = 0.2
    
    #0.10 Hydrolysis Rate (k_h, unit: mgCOD/mgBiomassCOD-day)
    Global_Parameters['k_h'] = 2.208 * pow(1.08, Delta_Temp)
    
    #0.11 Half Rate Conc. for Hetro. Growth on Part. COD 
    # (K_X, unit: mgCOD/mgBiomassCOD)
    Global_Parameters['K_X'] = 0.15
    
    #0.12 Ammonification of Org-N in biomass (k_a, unit: L/mgBiomassCOD-day)
    Global_Parameters['k_a'] = 0.1608 * pow(1.08, Delta_Temp)
    
    #0.13 Yield of Hetero. Growth on COD (Y_H, unit: mgBiomassCOD/mgCOD-removed)
    Global_Parameters['Y_H'] = 0.6 
    
    #0.14 Yield of Auto. Growth on TKN (Y_A, unit: mgBiomassCOD/mgTKN-oxidized)
    Global_Parameters['Y_A'] = 0.24
    
    #0.15 Fract. of Debris in Lysed Biomass(f_D_,unit: mgDebrisCOD/mgBiomassCOD)
    Global_Parameters['f_D_'] = 0.08
    
    #0.16 Correction Factor for Hydrolysis (cf_h, unitless)
    Global_Parameters['cf_h'] = 0.4
    
    #0.17 Correction Factor for Anoxic Heterotrophic Growth (cf_g, unitless)
    Global_Parameters['cf_g'] = 0.8
    
    #0.18 Ratio of N in Active Biomass (i_N_XB, unit: mgN/mgActiveBiomassCOD)
    Global_Parameters['i_N_XB'] = 0.086
    
    #0.19 Ratio of N in Debris Biomass (i_N_XD, unit: mgN/mgDebrisBiomassCOD)
    Global_Parameters['i_N_XD'] = 0.06
    
    return Global_Parameters
##==================================End of Section 0===========================


##============================End of Section 1.0============================

# 2.0 PROCESS RATE DEFINITIONS (Rj, unit: M/L^3/T):

# 2.1 Growth Rates:
# 2.1.1 Monod Factor of Sol.BioDegrad.COD on Hetero. (Monod) 
# 2.1.2 Monod Switch of Dissol. O2 on Hetero. (Monod)
# 2.1.3 Monod Switch of Dissol. O2 on Auto. (Monod)
# 2.1.4 Monod Factor of Ammonia-N on Autotrophs (Monod)
# 2.1.5 Monod Factor of NOx-N on Autotrophs (Monod)

def Monod (My_Eff_S_TBD, My_K_TBD):
    return My_Eff_S_TBD / (My_Eff_S_TBD + My_K_TBD)

# 2.1.6 Aerobic Growth Rate of Heterotrophs (r1_AerGH, unit: mgCOD/L/day)
def r1_AerGH (CompList, Parameters, Bulk_DO):
    return  Parameters['u_H'] * Monod(CompList[7], Parameters['K_S']) \
            * Monod(Bulk_DO, Parameters['K_OH']) * CompList[3]

# 2.1.7 Anoxic Growth Rate of Heterotrophs (r2_AxGH, unit: mgCOD/L/day)
def r2_AxGH (CompList, Parameters, Bulk_DO): 
    return  Parameters['u_H'] * Monod(CompList[7], Parameters['K_S']) \
            * Monod(Parameters['K_OH'], Bulk_DO) \
            * Monod(CompList[9], Parameters['K_NO']) \
            * Parameters['cf_g'] * CompList[3]
        
#2.1.8 Aerobic Growth Rate of Autotrophs (r3_AerGA, unit: mgCOD/L/day)
def r3_AerGA(CompList, Parameters, Bulk_DO): 
    return  Parameters['u_A'] * Monod(CompList[10], Parameters['K_NH']) \
            * Monod(Bulk_DO, Parameters['K_OA']) * CompList[4]

#2.1.9 Death and Lysis Rate of Heterotrophs (r4_DLH, unit: mgCOD/L/day)
def r4_DLH(CompList, Parameters):
    return  Parameters['b_LH'] * CompList[3]

#2.1.10 Death and Lysis Rate of Autotrophs (r5_DLA, unit: mgCOD/L/day)
def r5_DLA(CompList, Parameters):
    return  Parameters['b_LA'] * CompList[4]

#2.1.11 Ammonification Rate of Soluable Organic N (r6_AmmSN, unit: mgN/L/day)
def r6_AmmSN(CompList, Parameters): 
    return  Parameters['k_a'] * CompList[11] * CompList[3]

#2.1.12 Hydrolysis Rate of Particulate Organics (r7_HydX, unit: mgCOD/L/day)
def r7_HydX(CompList, Parameters, Bulk_DO): 
    return  Parameters['k_h'] \
            * Monod(CompList[2] / CompList[3], Parameters['K_X']) \
            * (Monod(Bulk_DO, Parameters['K_OH']) \
                + Parameters['cf_h'] * Monod(Parameters['K_OH'], Bulk_DO) \
                    * Monod(CompList[9], Parameters['K_NO'])) \
            * CompList[3]

#2.1.13 Hydrolysis Rate of Part. Organic N (r8_HydXN, unit: mgN/L/day)
def r8_HydXN(CompList, Parameters, Bulk_DO):
    return r7_HydX(CompList, Parameters, Bulk_DO) * CompList[12] / CompList[2]

##========================== End of Section 2 =================================



#3.0 STOCHIOMETRIC MATRIX (Use the Table 6.1, p193, Grady Jr. et al 1999)
def SetStochiometrics(Global_Parameters):
    
    Stochiometrics = dict()
        
    Stochiometrics['1_3'] = 1.0
    
    Stochiometrics['1_7'] = -1.0 / Global_Parameters['Y_H']
    
    Stochiometrics['1_8'] = -(1.0 - Global_Parameters['Y_H']) \
                            / Global_Parameters['Y_H']
                            #multiply -1.0 to express as oxygen

    Stochiometrics['1_10'] = -Global_Parameters['i_N_XB'] 

    Stochiometrics['1_13'] = -Global_Parameters['i_N_XB'] / 14.0
    
    Stochiometrics['2_3'] = 1.0
    
    Stochiometrics['2_7'] = -1.0 / Global_Parameters['Y_H']
    
    Stochiometrics['2_9'] = -(1.0 - Global_Parameters['Y_H']) \
                            / (2.86 * Global_Parameters['Y_H'])
    
    Stochiometrics['2_10'] = -Global_Parameters['i_N_XB']
    
    Stochiometrics['2_13'] = (1.0 - Global_Parameters['Y_H']) \
                            / (14.0 * 2.86 * Global_Parameters['Y_H']) \
                            - Global_Parameters['i_N_XB'] / 14.0
    
    Stochiometrics['3_4'] = 1.0
    
    Stochiometrics['3_8'] = -(4.57 - Global_Parameters['Y_A']) \
                            / Global_Parameters['Y_A'] 
                            #multiply -1.0 to express as oxygen
    
    Stochiometrics['3_9'] = 1.0 / Global_Parameters['Y_A']
    
    Stochiometrics['3_10'] = -Global_Parameters['i_N_XB'] \
                            - 1.0 / Global_Parameters['Y_A']
    
    Stochiometrics['3_13'] = (-1.0) * Global_Parameters['i_N_XB'] / 14.0 \
                            - 1.0 / (7.0 * Global_Parameters['Y_A'])
    
    Stochiometrics['4_2'] = 1.0 - Global_Parameters['f_D_']
    
    Stochiometrics['4_3'] = -1.0
    
    Stochiometrics['4_5'] = Global_Parameters['f_D_']
    
    Stochiometrics['4_12'] = Global_Parameters['i_N_XB'] \
                            - Global_Parameters['f_D_'] \
                            * Global_Parameters['i_N_XD']
    
    Stochiometrics['5_2'] = 1.0 - Global_Parameters['f_D_']
    
    Stochiometrics['5_4'] = -1.0
    
    Stochiometrics['5_5'] = Global_Parameters['f_D_']
    
    Stochiometrics['5_12'] = Global_Parameters['i_N_XB'] \
                            - Global_Parameters['f_D_'] \
                            * Global_Parameters['i_N_XD']
    
    Stochiometrics['6_10'] = 1.0
    
    Stochiometrics['6_11'] = -1.0
    
    Stochiometrics['6_13'] = 1.0 / 14.0
    
    Stochiometrics['7_2'] = -1.0
    
    Stochiometrics['7_7'] = 1.0
    
    Stochiometrics['8_11'] = 1.0
    
    Stochiometrics['8_12'] = -1.0
    
    return Stochiometrics
##=========================== End of Stochiometrics ===========================



#5.0 STEADY STATE EQUATION DEFINITION
# Calculation of Steady State
def Steady(CompList, Parameters, Stochiometrics, InfComp, SRT, Vol, Bulk_DO):
    
# CompList is a Python List that represents key design parameters 
#    CompList[0]: WAS_FLOW (M3/day, already calculated)
#    CompList[1]: X_I
#    CompList[2]: X_S 
#    CompList[3]: X_BH
#    CompList[4]: X_BA
#    CompList[5]: X_D 
#    CompList[6]: S_I
#    CompList[7]: S_S
#    CompList[8]: S_DO
#    CompList[9]: S_NO 
#    CompList[10]: S_NH 
#    CompList[11]: S_NS
#    CompList[12]: X_NS
#    CompList[13]: S_ALK
#    

# Parameters is a Python Dictionary that holds the ASM1 model parameters after initiation according to design temp. (C)

# Stochiometrics is a Python Dictionary that holds the stochoimetrics 

# InfComp is Python List that represent the Influent values of the ASM1 Components 
#  with the exception of InfComp[0] which is the Inf_Flow (m3/day)
#    0_Inf_Flow
#    1_X_I, 2_X_S, 3_X_BH, 4_X_BA, 5_X_D 
#    6_S_I, 7_S_S, 8_S_DO, 9_S_NO, 10_S_NH, 11_S_NS, 12_X_NS, 13_S_ALK


# MLSS is the Mixed Liquor Suspended Solids in mgCOD/L, within which X_I is fixed.

# Bulk_DO in mgO2/L

        
    #Steady state equations that calculate the simulation results:
    #    C[0] == WAS Flow for a SINGLE TANK REACTOR, DIRECT WASTING FROM REACTOR
    result = [CompList[0] - Vol / SRT]
    
    #    for C1_X_I, assume perfect solid-liquid separation (i.e. X_I = 0.0 mg/L in effluent)
    result.append(InfComp[0] * InfComp[1] \
            - (InfComp[0] - CompList[0]) * 0.0 - CompList[0] * CompList[1] \
            + 0.0 * Vol)
    
    #    for C2_X_S, assume perfect solid-liquid separation (i.e. X_S = 0.0 mg/L in effluent)
    result.append(InfComp[0] * InfComp[2] \
            - (InfComp[0] - CompList[0]) * 0.0 - CompList[0] * CompList[2] \
            + (Stochiometrics['4_2'] * r4_DLH(CompList, Parameters) \
            + Stochiometrics['5_2'] * r5_DLA(CompList, Parameters) \
                    + Stochiometrics['7_2'] * r7_HydX(CompList, Parameters, Bulk_DO)) \
                  * Vol)

        
    #    for C3_X_BH, assume perfect solid-liquid separation (i.e. X_BH = 0.0 mg/L in effluent)
    result.append(InfComp[0] * InfComp[3] \
            - (InfComp[0] - CompList[0]) * 0.0 - CompList[0] * CompList[3] \
            + (Stochiometrics['1_3'] * r1_AerGH(CompList, Parameters, Bulk_DO)\
            + Stochiometrics['2_3'] * r2_AxGH(CompList, Parameters, Bulk_DO) \
                    + Stochiometrics['4_3'] * r4_DLH(CompList, Parameters)) \
                  * Vol)
    
    #    for C4_X_BA, assume perfect solid-liquid separation (i.e. X_BA = 0.0 mg/L in effluent)
    result.append(InfComp[0] * InfComp[4] \
            - (InfComp[0] - CompList[0]) * 0.0 - CompList[0] * CompList[4] \
            + (Stochiometrics['3_4'] * r3_AerGA(CompList, Parameters, Bulk_DO)\
            + Stochiometrics['5_4'] * r5_DLA(CompList, Parameters)) \
                  * Vol)
    
    #    for C5_X_D, assume perfect solid-liquid separation (i.e. X_D = 0.0 mg/L in effluent)
    result.append(InfComp[0] * InfComp[5] \
            - (InfComp[0] - CompList[0]) * 0.0 - CompList[0] * CompList[5] \
            + (Stochiometrics['4_5'] * r4_DLH(CompList, Parameters) \
            + Stochiometrics['5_5'] * r5_DLA(CompList, Parameters)) \
                  * Vol)
        
    #    for C6_S_I
    result.append(InfComp[0] * InfComp[6] \
            - (InfComp[0] - CompList[0]) * CompList[6] \
            - CompList[0] * CompList[6] \
            + 0.0 * Vol)
    
    #    for C7_S_S
    result.append(InfComp[0] * InfComp[7] \
            - (InfComp[0] - CompList[0]) * CompList[7] \
            - CompList[0] * CompList[7] \
            + (Stochiometrics['1_7'] * r1_AerGH(CompList, Parameters, Bulk_DO)\
            + Stochiometrics['2_7'] * r2_AxGH(CompList, Parameters, Bulk_DO) \
                    + Stochiometrics['7_7'] \
                    * r7_HydX(CompList, Parameters, Bulk_DO)) \
            * Vol)
        
    #    for C8_S_DO
    result.append(InfComp[0] * InfComp[8] \
            - (InfComp[0] - CompList[0]) * CompList[8] \
            - CompList[0] * CompList[8] 
            + (Stochiometrics['1_8'] * r1_AerGH(CompList, Parameters, Bulk_DO)\
                    + Stochiometrics['3_8'] \
                    * r3_AerGA(CompList, Parameters, Bulk_DO)) \
            * Vol)
    #result.append(CompList[8] - Bulk_DO)
           
    #    for C9_S_NO
    result.append(InfComp[0] * InfComp[9] \
            - (InfComp[0] - CompList[0]) * CompList[9] \
            - CompList[0] * CompList[9] \
            + (Stochiometrics['2_9'] * r2_AxGH(CompList, Parameters, Bulk_DO) \
            + Stochiometrics['3_9'] * r3_AerGA(CompList, Parameters, Bulk_DO))\
            * Vol)
          
    #    for C10_S_NH
    result.append(InfComp[0] * InfComp[10] \
            - (InfComp[0] - CompList[0]) * CompList[10] \
            - CompList[0] * CompList[10] 
            + (Stochiometrics['1_10'] * r1_AerGH(CompList, Parameters,Bulk_DO)\
                    + Stochiometrics['2_10'] \
                    * r2_AxGH(CompList, Parameters, Bulk_DO) \
                            + Stochiometrics['3_10'] \
                            * r3_AerGA(CompList, Parameters, Bulk_DO) \
                            + Stochiometrics['6_10'] \
                            * r6_AmmSN(CompList, Parameters)) \
            * Vol)
        
    #    for C11_S_NS
    result.append(InfComp[0] * InfComp[11] \
            - (InfComp[0] - CompList[0]) * CompList[11] \
            - CompList[0] * CompList[11] \
            + (Stochiometrics['6_11'] * r6_AmmSN(CompList, Parameters) \
            + Stochiometrics['8_11'] * r8_HydXN(CompList, Parameters,Bulk_DO))\
            * Vol)
        
    #    for C12_X_NS
    result.append(InfComp[0] * InfComp[12] \
            - (InfComp[0] - CompList[0]) * 0.0 \
            - CompList[0] * CompList[12] \
            + (Stochiometrics['4_12'] * r4_DLH(CompList, Parameters) \
                    + Stochiometrics['5_12'] * r5_DLA(CompList, Parameters) \
                    + Stochiometrics['8_12'] \
                    * r8_HydXN(CompList, Parameters, Bulk_DO)) \
            * Vol)
            
    #    for C13_S_ALK
    result.append(InfComp[0] * InfComp[13] \
            - (InfComp[0] - CompList[0]) * CompList[13] \
            - CompList[0] * CompList[13] \
            + (Stochiometrics['1_13'] * r1_AerGH(CompList, Parameters,Bulk_DO)\
            + Stochiometrics['2_13'] * r2_AxGH(CompList, Parameters, Bulk_DO) \
                    + Stochiometrics['3_13'] \
                    * r3_AerGA(CompList, Parameters, Bulk_DO) \
                            + Stochiometrics['6_13'] \
                            * r6_AmmSN(CompList, Parameters)) \
            * Vol)

    return result


    

#=========================== TESTING PROGRAM ==================================


#6.0 USER-INPUT, PROJECT SPECIFIC DESIGN INFORMATION

#wastewater minimum and maximum temperature
MinWaterTemp = eval(input('Minimum Water Temperature (C) = '))
MaxWaterTemp = eval(input('Maximum Water Temperature (C) = '))

#Dissolved Oxygen in MLSS
Dissolved_Oxygen = eval(input('Reactor MLSS DO (mg/L) = '))

# Set Global Parameters according to the minimum wastewater temperature
GP = SetGlobalParameters(MinWaterTemp)
# Set stochiometrics constants
ST = SetStochiometrics(GP)

print("Global ASM1 Params at Min. Water Temperature ", MinWaterTemp, " C:")
print(GP)
print("Global ASM1 Stochs at Min. Water Temperature ",MinWaterTemp,"C:")
print(ST)

# Influent Flow, converted to M3/d    
Inf_Flow = eval(input('Design Flow (MGD) = ')) * 1000.0 * 3.78 
    
Inf_BOD5 = eval(input('Influent BOD5 (mg/L) = '))  #typical US Muni. WW = 240.0
#influent biodegradable COD, BOD/COD = 1.71 for typ. muni.WW
Inf_CODb = Inf_BOD5 * 1.71
#influent TSS (mgCOD/L), NOT IN InfC
Inf_TSS = eval(input('Influent TSS (mgTSS/L) = '))  #typ. US WW = 240.0
#influent VSS (mgCOD/L), 
Inf_VSS = 195.4 #eval(input('Influent VSS (mgVSS/L) = '))
#influent total COD, COD/BOD5 = 2.04 per BioWin
Inf_CODt = Inf_BOD5 * 2.04 #eval(input('Influent COD (mg/L) = '))
#influent total inner COD, 
Inf_CODi = Inf_CODt - Inf_CODb

Inf_S_I = 0.13 * Inf_CODt

Inf_X_I = Inf_CODi - Inf_S_I

Inf_X_S = 1.6 * Inf_VSS - Inf_X_I

Inf_S_S = Inf_CODb - Inf_X_S

#influent Heterotrophs (mgCOD/L), 
Inf_X_BH = 0.0
#influent Autotrophs (mgCOD/L), 
Inf_X_BA = 0.0
#influent Biomass Debris (mgCOD/L), 
Inf_X_D = 0.0

print("Influent Total COD (mg/L) = ", Inf_CODt)
print("Influent total biodegradable COD (mg/L) = ", Inf_CODb)
print("Influent soluble biodegradable COD (Inf_S_S, mg/L) = ", Inf_S_S)
print("Influent part. biodegradable COD (Inf_X_S, mg/L) = ", Inf_X_S)
print("Influent sol. non-biodegradable COD (Inf_S_I, mg/L) = ", Inf_S_I)
print("Influent part. non-biodegradable COD (Inf_X_I, mg/L) = ", Inf_X_I)

#assuming perfect solids-liquid separation
Eff_X_BH = 0.0

Eff_X_BA = 0.0 

Eff_X_D = 0.0   

Effluent_S_Total = eval(input("Effluent COD (mg/L) = "))
Eff_S_S = Effluent_S_Total - Inf_S_I
#check the relationship among Total Effluent COD, Effluent Sol. biodegrad. COD, 
# and sol. inert COD
while Eff_S_S <= 0.0:
    print("Error in specified Eff. or Inf. S_S and/or S_I. Please re-enter:")
    Effluent_S_Total = eval(input('Re-enter Eff. COD (mg/L) = '))
    Eff_S_S = Effluent_S_Total - Inf_S_I
  
#influent TKN (mgN/L), NOT IN InfC
Inf_TKN = eval(input('Influent TKN (mgN/L) = '))
#influent Ammonia-N (mgN/L), 
Inf_S_NH = eval(input('Influent Ammonia-N (mgN/L) = '))
#subdividing TKN into: 
# a) nonbiodegradable TKN 
NonBiodegradable_TKN_Ratio = 0.03
#NON-BIODEGRADABLE TKN WILL HAVE TO BE ADDED BACK TO THE EFFLUENT TN
Inf_nb_TKN = Inf_TKN * NonBiodegradable_TKN_Ratio
Soluble_Biodegradable_OrgN_Ratio = Inf_S_S / (Inf_S_S + Inf_X_S)#Grady et al '99
# b) soluble biodegrable TKN,     
Inf_S_NS = (Inf_TKN - Inf_S_NH - Inf_nb_TKN) * Soluble_Biodegradable_OrgN_Ratio
# c) particulate biodegradable TKN, 
Inf_X_NS = (Inf_TKN - Inf_S_NH - Inf_nb_TKN) \
        * (1.0 - Soluble_Biodegradable_OrgN_Ratio)

print("Inf. Non-Biodeg. TKN = ", Inf_nb_TKN, " mgN/L")
print("Inf. Sol. Biodeg. Organic N (Inf_S_NS, mgN/L) = ", Inf_S_NS)
print("Inf. Part. Biodeg. Organic N (Inf_X_NS, mgN/L = ", Inf_X_NS)

#Nowadays, ammonia removal is almost always required
Eff_S_NH = 1.0 #mgN/L

#Safety Factor
SF = 1.25
# convert b_LH and b_LA to b_H and b_A, respectively
b_H = GP['b_LH'] * (1 - GP['Y_H'] * (1.0 - GP['f_D_']))
b_A = GP['b_LA'] * (1 - GP['Y_A'] * (1.0 - GP['f_D_']))

#print "b_H = ", b_H, " b_A = ", b_A

#OXIC SRT required for Eff_S_S
SRT_OXIC_H = 1.0 / (GP['u_H'] * Monod(Eff_S_S, GP['K_S']) \
        * Monod(Dissolved_Oxygen, GP['K_OH']) - b_H)
#SRT required for Eff_S_NH
SRT_OXIC_A = 1.0 / (GP['u_A'] * Monod(Eff_S_NH, GP['K_NH']) \
        * Monod(Dissolved_Oxygen, GP['K_OA']) - b_A)
#Pick the larger of the two because nowadays nitrification is almost required
# in all WWTPs.
SRT_OXIC = max(SRT_OXIC_A, SRT_OXIC_H) * SF

print("Min Oxic SRT for Heterotrophs = ", SRT_OXIC_H, " days")
print("Min Oxic SRT for Autotrophs = ", SRT_OXIC_A, " days")
print("SELECTED Oxic SRT = ", SRT_OXIC, " days")

#Actual Effluent S_S and S_NH based on the actual oxic SRT
Eff_S_S = GP['K_S'] * (1.0 / SRT_OXIC + b_H) \
            / (GP['u_H'] - (1.0 / SRT_OXIC + b_H))

Eff_S_NH = GP['K_NH'] * (1.0 / SRT_OXIC + b_A) \
            / (GP['u_A'] - (1.0 / SRT_OXIC + b_A))

print("Eff. S_S = ", Eff_S_S, " (mgCOD/L)")
print("Eff. S_NH = ", Eff_S_NH, " (mgN/L)")

#when Oxic SRT is infinity:
#Eff_S_S_Min = GP['K_S'] * b_H / (GP['u_H'] - b_H) 
#Eff_S_NH_Min = GP['K_NH'] * b_A /(GP['u_A'] - b_A)

#print "Min. Possible Eff. S_S = ", Eff_S_S_Min, " mgCOD/L"
#print "Min. Possible Eff. S_NH = ", Eff_S_NH_Min, " mgN/L"

#influent Nitrite + Nitrate (mgN/L), 
Inf_S_NO = eval(input('Influent Oxidized Nitrogen (NO2+NO3, mgN/L) = '))

Effluent_Total_N = eval(input('Effluent Total N (mgN/L) = '))
#Assuming complete nitrification of all biodegradable TKN
#Assume 6.0% N in biomass:

if Effluent_Total_N >= Inf_TKN - Inf_nb_TKN - Eff_S_NH \
        - GP['i_N_XD'] * (Inf_S_S + Inf_X_S - Effluent_S_Total) \
        * GP['Y_H']:
    #which means denitrification is not required
    Eff_S_NO = Inf_S_NO + Inf_TKN - Inf_nb_TKN - Eff_S_NH \
            - GP['i_N_XD'] * (Inf_S_S + Inf_X_S) * GP['Y_H']
    print("Denitrification is not required")
    S_NO_2B_DN = 0.0
else:# denitrification will be required
    Eff_S_NO = Effluent_Total_N - Inf_nb_TKN - Eff_S_NH
    print("DENITRIFICATION IS NEEDED:")
    S_NO_2B_DN = Inf_S_NO + Inf_TKN - Inf_nb_TKN - Eff_S_NH \
            - GP['i_N_XD'] * (Inf_S_S + Inf_X_S) * GP['Y_H'] \
            - Eff_S_NO

print("Oxic Basin Eff. S_NO = ", Eff_S_NO, " (mgN/L)")
print("S_NO to be Dentirified = ", S_NO_2B_DN, " (mgN/L)")
 
#Sizing the reactor volume
#Assume perfect hydrolysis of influent biodegradable solids 
#
#Global Parameters @ Max. Design Temperature
GP_MT = SetGlobalParameters(MaxWaterTemp)

#print "ASM1 Parameters at Max. Water Temperature (", MaxWaterTemp, " C):"
#print GP_MT

b_H_MT = GP_MT['b_LH'] * (1 - GP_MT['Y_H'] * (1.0 - GP_MT['f_D_']))
b_A_MT = GP_MT['b_LA'] * (1 - GP_MT['Y_A'] * (1.0 - GP_MT['f_D_']))

#Oxygen Requirement at Max Design Temp., unit: gO2/day
#heterotrophic:
Oxygen_Required_H_MT = Inf_Flow * (Inf_S_S + Inf_X_S - Eff_S_S) \
        * (1.0 - (1.0 + GP_MT['f_D_'] * GP_MT['b_LH'] * SRT_OXIC) \
        * GP_MT['Y_H'] / (1.0 + b_H_MT * SRT_OXIC))

#Nitrogen Requried for Biomass Growth                   
NR_MT = 0.087 * (1.0 + GP_MT['f_D_'] * GP_MT['b_LH'] * SRT_OXIC) \
        * GP_MT['Y_H'] / (1.0 + b_H_MT * SRT_OXIC)
#autotrophic:
Oxygen_Required_A_MT = Inf_Flow \
        * (Inf_TKN + Inf_S_NO - NR_MT * (Inf_S_S + Inf_X_S - Eff_S_S)) \
        * (4.57 - (1.0 + GP_MT['f_D_'] * GP_MT['b_LA'] * SRT_OXIC) \
        * GP_MT['Y_A'] / (1.0 + b_A_MT * SRT_OXIC))

#Nowadays, nitrification is typically required, converted unit to kgO2/HR
Oxygen_Required_Total_MT = (Oxygen_Required_H_MT + Oxygen_Required_A_MT) / 1000.0 / 24.0 

print("Summer Heterotrophic O2 Requirement = ", Oxygen_Required_H_MT, "gO2/day")
print("Summer Autotrophic O2 Requirement = ", Oxygen_Required_A_MT, "gO2/day")
print("Summer Total O2 Requirement = ", Oxygen_Required_Total_MT, "kgO2/HOUR")

#Lower Limit of Aerobic Reactor Volume 
#limited by Floc-Shear: 
#(when oxygen demand is high, more aeration is needed, thus more floc shearing)
Air_Flow_MT = 6.0 * Oxygen_Required_Total_MT / 10.0 # m3/min
#assume 90m3Air/1000m3 can be accepted w/o floc tearing 
Oxic_Vol_Min_FS = 1000.0 * Air_Flow_MT / 90.0 # m3 
#limited by sustainable Oxygen Transfer rate, assumed 10% O2 transfer efficiency
Oxic_Vol_Min_OT = Oxygen_Required_Total_MT / 0.1 
#use the larger of the above two as the minimum aerobic reactor volume
Oxic_Vol_Min = min(Oxic_Vol_Min_FS, Oxic_Vol_Min_OT)

print("Minimum Oxic Volume (limited by shear force) = ", Oxic_Vol_Min, " m3")


#Oxygen Requirement at Min Design Temp., unit: gO2/day
#heterotrophic:
Oxygen_Required_H = Inf_Flow * (Inf_S_S + Inf_X_S - Eff_S_S) \
        * (1.0 - (1.0 + GP['f_D_'] * GP['b_LH'] * SRT_OXIC) * GP['Y_H'] \
        / (1.0 + b_H * SRT_OXIC))

#Nitrogen Requried for Biomass Growth                   
NR = 0.087 * (1.0 + GP['f_D_'] * GP['b_LH'] * SRT_OXIC) * GP['Y_H'] \
        / (1.0 + b_H * SRT_OXIC)
#autotrophic:
Oxygen_Required_A = Inf_Flow \
        * (Inf_TKN - NR * (Inf_S_S + Inf_X_S - Eff_S_S)) \
        * (4.57 - (1.0 + GP['f_D_'] * GP['b_LA'] * SRT_OXIC) * GP['Y_A'] \
        / (1.0 + b_A * SRT_OXIC))

#convert unit to kgO2/HR
Oxygen_Required_Total = (Oxygen_Required_H + Oxygen_Required_A) / 1000.0 / 24.0

print("Winter Heterotrophic O2 Requirement = ", Oxygen_Required_H, " gO2/day")
print("Winter Autotrophic O2 Requirement = ", Oxygen_Required_A, " gO2/day")
print("Winter Total O2 Requirement = ", Oxygen_Required_Total, " kgO2/HOUR")
 
#Upper Limit of Aerobic Reactor Volume 
#limited by biomass suspension: 
#(when oxygen demand is low, less mixing energy is available)
Air_Flow = 6.0 * Oxygen_Required_Total / 10.0 # m3/min
#assuming 20m3 Air/1000m3 needed for biomass suspension 
Oxic_Vol_Max = 1000.0 * Air_Flow / 20.0 # m3, 

print("Maximum Oxic Volume (limited by mixing energy) = ", Oxic_Vol_Max, "m3")
# NOW THE OXIC VOLUME IS BRACKETED BY Oxic_Vol_Min and Oxic_Vol_Max


#calculate daily solids production, unit: gCOD/day
Daily_Solids_Production_H = Inf_Flow \
        * (Inf_X_I + (1.0 + GP['f_D_'] * GP['b_LH'] * SRT_OXIC) \
        * GP['Y_H'] * (Inf_S_S + Inf_X_S - Eff_S_S) \
        / (1.0 + b_H * SRT_OXIC))

Daily_Solids_Production_A = Inf_Flow \
        * (1.0 + GP['f_D_'] * GP['b_LA'] * SRT_OXIC) * GP['Y_A'] \
        * (Inf_TKN - NR * (Inf_S_S + Inf_X_S - Eff_S_S) - Eff_S_NH) \
        / (1.0 + b_A * SRT_OXIC)

Daily_Solids_Production_Total = Daily_Solids_Production_H \
        + Daily_Solids_Production_A + Inf_Flow * (Inf_TSS - Inf_VSS) * 1.2

print("Solids Production Based on Min. Water Temperature:")
print("Hetero. Solids Prod.= ", Daily_Solids_Production_H / 1.2 / 1000.0, "kgTSS/d")
print("Autot. Solids Prod.= ", Daily_Solids_Production_A / 1.2 / 1000.0, "kgTSS/d")
print("Total Solids Prod.= ", Daily_Solids_Production_Total / 1.2 / 1000.0, "kgTSS/d")

#design MLSS in (mgCOD/L), convert to mgTSS/L
print("MLSS Range (mg/L): ", \
        Daily_Solids_Production_Total / 1.2 * SRT_OXIC / Oxic_Vol_Max, \
        " to ", Daily_Solids_Production_Total / 1.2 * SRT_OXIC / Oxic_Vol_Min)

MLSS = eval(input("Design MLSS (mg/L) = ")) * 1.0
Oxic_Vol = Daily_Solids_Production_Total / 1.20 * SRT_OXIC / MLSS

while Oxic_Vol <= Oxic_Vol_Min or Oxic_Vol > Oxic_Vol_Max:
    print("MLSS out of range, please re-enter")
    MLSS = eval(input("Design MLSS (mg/L) = ")) * 1.0
    Oxic_Vol = Daily_Solids_Production_Total / 1.20 * SRT_OXIC / MLSS


print("Calculated Oxic Vol = ", Oxic_Vol, " m3")

#calculate HRT of the Oxic Reactor
HRT_OXIC = Oxic_Vol / Inf_Flow

print("Oxic Basin HRT = ", HRT_OXIC * 24.0 , " hours")

#X_I within reactor
X_I = SRT_OXIC / HRT_OXIC * Inf_X_I

print("Inert Solids (X_I) = ", X_I / 1.20, "mgTSS/L" )
Eff_X_I = 0.0 #assume perfect solids-liquid separation
Eff_X_S = 0.0
Eff_S_I = Inf_S_I

Eff_S_DO = Dissolved_Oxygen

#influent TP
Inf_TP = eval(input('Influent TP (mgP/L) = '))
    
#influent Alkalinity as CaCO3 (mg/L), 
Inf_S_ALK = eval(input('Influent Alkalinity (mmol/L) = '))
    
#influent Dissolved Oxygen (mgO2/L), 
Inf_S_DO = eval(input('Influent DO (mgO2/L) = '))


#InfC is the Python List that represent the influent ASM1 model components, 
# to be passed onto the fsolve() func.     
InfC = list()
InfC = [Inf_Flow, \
        Inf_X_I, Inf_X_S, Inf_X_BH, Inf_X_BA, Inf_X_D, \
        Inf_S_I, Inf_S_S, -Inf_S_DO, Inf_S_NO, Inf_S_NH, \
        Inf_S_NS, Inf_X_NS, Inf_S_ALK]


#1.0 MODEL COMPONENTS (Ci, M/L^3)
# C is the ASM1 Model Components represented by a Python Dictionary
# C will store the results from the FSOLVE function in the main testing program
# C represent the concentrations WITHIN the reactor
C = dict()
#1.0 WAS Flow is set by the SRT, ASSUMING DIRECTLY WASTING FROM REACTOR
C['0_WAS_Flow'] = Oxic_Vol / SRT_OXIC #m3/day, 
#print "WAS Flow = ", C['0_WAS_Flow']
#1.1 Inert Particulate COD (C1_X_I, mgCOD/L)
C['1_X_I'] = X_I
#1.2 Slowly Biodegradable Particulate COD (C2_X_S, mgCOD/L)
#    to be calculated in FSOLVE()
C['2_X_S'] = 0.0
#1.7 Effluent Soluble Readily Biodegradable Substrate (C7_S_S, mgCOD/L)
C['7_S_S'] = Eff_S_S
#1.3 Active Heterotrophic Biomass (C3_X_BH, mgCOD/L)
C['3_X_BH'] = SRT_OXIC / HRT_OXIC \
        * (InfC[7] + InfC[2] - C['7_S_S']) * GP['Y_H'] \
        / (1.0 + b_H * SRT_OXIC)
#print "X_BH = ", C['3_X_BH']

#1.5 Debris from Biomass Decay (C5_X_D, mgCOD/L)
C['5_X_D'] = SRT_OXIC * GP['f_D_'] * GP['b_LH'] * SRT_OXIC / HRT_OXIC \
        * (InfC[7] - C['7_S_S']) * GP['Y_H'] / (1 + b_H * SRT_OXIC)
#1.6 Inert Soluble Readily Biodegradable Substrate (C6_S_I, mgCOD/L)
C['6_S_I'] = Inf_S_I
#print "X_D = ", C['5_X_D']  

#1.8 Oxygen Requirement (C8_S_DO, mgCOD/L)
#    to be calculated in FSOLVE()
C['8_S_DO'] = 0.0   
#1.9 Nitrite and Nitrate Combined Cocentration (C9_S_NO, mgN/L)
C['9_S_NO'] = Eff_S_NO
#1.10 Ammonia Concentration (C10_S_NH, mgN/L)
C['10_S_NH'] = Eff_S_NH  
#1.11 Soluble Biodegradable Organic Nitrogen (C11_S_NS, mgN/L)
#    to be calculated in FSOLVE()
C['11_S_NS'] = 0.0    
#1.12 Particulate Biodegradable Organic Nitrogen (C12_X_NS, mgN/L)
#    to be calculated in FSOLVE()
C['12_X_NS'] = 0.0    
#1.13 Alkalinity (C13_S_ALK, mgCaCO3/L)
#    to be calculated in FSOLVE()
C['13_S_ALK'] = 0.0

#1.4 Active Autotrophic Biomass (C4_X_BA, mgCOD/L)
C['4_X_BA'] = SRT_OXIC / HRT_OXIC * (InfC[10] - C['10_S_NH']) * GP['Y_A'] \
        / (1.0 + b_A * SRT_OXIC)
#print "X_BA = ", C['4_X_BA']
 

#rename the model components to meet requirements for scipy.optimize.fsolve()
DesignComponents_Guess = list()
DesignComponents_Guess = [C['0_WAS_Flow'], \
                          C['1_X_I'], InfC[2], C['3_X_BH'], C['4_X_BA'], \
                          C['5_X_D'], InfC[6], C['7_S_S'], InfC[8], \
                          C['9_S_NO'], C['10_S_NH'], InfC[11], InfC[12], \
                          InfC[13]]

SteadyState = scipy.optimize.fsolve(Steady, \
                                      DesignComponents_Guess, \
                                      (GP, ST, InfC, SRT_OXIC, Oxic_Vol, \
                                       Dissolved_Oxygen))

print("Influent Components = ", InfC)

print("Steady State Results: " )
#print SteadyState
C['0_WAS_Flow'] = SteadyState[0] #m3/day, 
C['1_X_I'] = SteadyState[1]
C['2_X_S'] = SteadyState[2]
C['3_X_BH'] = SteadyState[3]
C['4_X_BA'] = SteadyState[4]
C['5_X_D'] = SteadyState[5]
C['6_S_I'] = SteadyState[6]
C['7_S_S'] = SteadyState[7]
C['8_S_DO'] = SteadyState[8]   
C['9_S_NO'] = SteadyState[9]
C['10_S_NH'] = SteadyState[10]
C['11_S_NS'] = SteadyState[11]
C['12_X_NS'] = SteadyState[12]
C['13_S_ALK'] = SteadyState[13]

print(C)
print()
print("Oxic Basin Solids Conc. (mgMLSS/L) = ", (SteadyState[1] + SteadyState[2] + \
                                                SteadyState[3] + SteadyState[4] + \
                                                SteadyState[5]) / 1.2 + \
                                                SRT_OXIC / HRT_OXIC * \
                                                (Inf_TSS - Inf_VSS))

print("Actual Oxygen Requirement (AOR, lbO2/day) = ", \
        - SteadyState[8] * Inf_Flow / 1000.0 * 2.2)

print("Eff. COD (mg/L) = ", SteadyState[6] + SteadyState[7])

print("Eff. NH3-N (mgN/L) = ", SteadyState[10])

print("Eff. TKN (mgN/L) = ", SteadyState[10] + SteadyState[11])

print("Eff. TN (mgN/L) = ", SteadyState[9] + SteadyState[10] \
                            + SteadyState[11] + Inf_nb_TKN)

print("Eff. Alk. (mgCaCO3/L) = ", SteadyState[13] * 50.0)
                                             
