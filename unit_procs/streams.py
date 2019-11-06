# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
#    
#    Copyright (C) Kai Zhang
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
# This file defines the following classes related to streams:
#       pipe, influent, effluent, splitter, WAS.
#
# ----------------------------------------------------------------------------


from unit_procs.base import poopy_lab_obj
from utils.datatypes import flow_data_src
from ASMModel import constants

# -----------------------------------------------------------------------------

class splitter(poopy_lab_obj):

    __id = 0

    def __init__(self):
        self.__class__.__id += 1
        self.__name__ = "Splitter_" + str(self.__id)

        self._type = "Splitter"

        # _inlet store the upstream units and their flow contribution
        # in the format of {unit, Flow}
        self._inlet = {}
        # outlets shall be a single receiver each
        self._main_outlet = None
        self._side_outlet = None
        
        # flag to indicate whether there are upstream units
        self._has_discharger = False
        self._has_sidestream = True  # always True for splitter
        # main outlet connection flag
        self._mo_connected = False
        # side outlet connection flag
        self._so_connected = False

        # determine how to calculate branch flows
        self._upstream_set_mo_flow = False

        # flow data source tags
        self._in_flow_ds = flow_data_src.TBD
        self._mo_flow_ds = flow_data_src.TBD
        self._so_flow_ds = flow_data_src.TBD


        # to confirm it has received _so_flow
        self._so_flow_defined = False

        # main outlet flow, m3/d
        self._mo_flow = 0.0
        # side outlet flow, m3/d
        self._so_flow = 0.0

        # total inlet flow calculated from all dischargers
        self._total_inflow = 0.0
        # inlet flow back calculated as (_mo_flow + _so_flow)
        #self._in_flow_backcalc = 0.0
        
        self._SRT_controller = False
        
        # influent/main_outlet/side_oulet model components:
        #    _comps[0]: S_DO as DO
        #    _comps[1]: S_I
        #    _comps[2]: S_S
        #    _comps[3]: S_NH
        #    _comps[4]: S_NS
        #    _comps[5]: S_NO
        #    _comps[6]: S_ALK
        #    _comps[7]: X_I
        #    _comps[8]: X_S
        #    _comps[9]: X_BH
        #    _comps[10]: X_BA
        #    _comps[11]: X_D
        #    _comps[12]: X_NS
        self._in_comps = [0.00001] * constants._NUM_ASM1_COMPONENTS 
        self._mo_comps = [0.00001] * constants._NUM_ASM1_COMPONENTS
        self._so_comps = [0.00001] * constants._NUM_ASM1_COMPONENTS

        # results of previous round
        self._prev_mo_comps = [0.00001] * constants._NUM_ASM1_COMPONENTS
        self._prev_so_comps = [0.00001] * constants._NUM_ASM1_COMPONENTS

        # convergence status for the unit itself
        self._converged = False

        return None


    # COMMON INTERFACES DEFINED IN POOPY_LAB_OBJ (BASE)
    #

    def set_flow_data_src(self, branch='Main', flow_ds=flow_data_src.TBD):
        # branch = 'Main'|'Side'|'Inlet'
        # flow_ds: flow_data_source.TBD|.UPS|.DNS|.PRG

        _in_flow_known = (self._in_flow_ds != flow_data_src.TBD)

        _so_flow_known = (self._so_flow_ds != flow_data_src.TBD)

        _mo_flow_known = (self._mo_flow_ds != flow_data_src.TBD)

        _chngd = False

        if branch == 'Main' and not _mo_flow_known:
            self._mo_flow_ds = flow_ds
            _chngd = True
        elif branch == 'Side' and not _so_flow_known:
            self._so_flow_ds = flow_ds
            _chngd = True
        elif branch == 'Inlet' and not _in_flow_known:
            self._in_flow_ds = flow_ds
            _chngd = True
        #else: do nothing

        if not _chngd:
            return None

        # auto evaluate the flow data source tags after setting one.
        # first get an updated set of flags after the change:
        _in_flow_known = (self._in_flow_ds != flow_data_src.TBD)

        _so_flow_known = (self._so_flow_ds != flow_data_src.TBD)

        _mo_flow_known = (self._mo_flow_ds != flow_data_src.TBD)

        _mo_flow_by_ext = (self._mo_flow_ds == flow_data_src.DNS
                        or self._mo_flow_ds == flow_data_src.PRG)

        _so_flow_by_ext = (self._so_flow_ds == flow_data_src.DNS
                        or self._so_flow_ds == flow_data_src.PRG)

        if _so_flow_known:
            if _so_flow_by_ext:
                if _mo_flow_by_ext:
                    self._upstream_set_mo_flow = False
                    if not _in_flow_known:
                        self._in_flow_ds = flow_data_src.DNS
                else:
                    if _mo_flow_known:
                        # i.e. _upstream_set_mo_flow = True
                        # i.e. _mo_flow_ds = UPS
                        self._upstream_set_mo_flow = True
                        if not _in_flow_known:
                            self._in_flow_ds = flow_data_src.UPS
                        #else:
                        #    pass
                    else:
                        if _in_flow_known:
                            self._upstream_set_mo_flow = True
                            self._mo_flow_ds = flow_data_src.UPS
                        #else:
                        #    pass
            else:
                # i.e. _so_flow set by UPS
                # i.e. _in_flow and _mo_flow must be set somewhere else
                self._upstream_set_mo_flow = False
        else:
            if _in_flow_known and _mo_flow_known:
                self._upstream_set_mo_flow = False
                self._mo_flow_ds = flow_data_src.UPS
            #else:
            #    pass
        return None


    def get_flow_data_src(self):
        return self._in_flow_ds, self._mo_flow_ds, self._so_flow_ds


    def assign_initial_guess(self, init_guess_lst):
        self._in_comps = init_guess_lst[:]
        self._mo_comps = init_guess_lst[:]
        self._so_comps = init_guess_lst[:]
        return None


    def is_converged(self, limit=1E-15):
        #print(self.__name__)
        #print('prev mo/so = {}, {}'.format(self._prev_mo_comps,
        #    self._prev_so_comps))

        _mo_cnvg = self._check_conc_cnvg(self._mo_comps,
                                        self._prev_mo_comps,
                                        limit)
                  
        _so_cnvg = self._check_conc_cnvg(self._so_comps,
                                        self._prev_so_comps,
                                        limit)

        _conc_cnvg = not (False in _mo_cnvg or False in _so_cnvg)
        _flow_cnvg = (abs(self._total_inflow - self._mo_flow - self._so_flow)
                        / self._total_inflow <= limit)

        self._converged = _conc_cnvg and _flow_cnvg

        #print('{} cnvg: flow {}, main {}, side{}'.format(
        #        self.__name__, _flow_cnvg, _mo_cnvg, _so_cnvg))

        return self._converged

        
    def get_type(self):
        return self._type


    def has_sidestream(self):
        return self._has_sidestream


    def add_upstream(self, discharger, upst_branch='Main'): 
        #Connect current unit to the specified branch of the upstream unit
        if discharger not in self._inlet:
            # Setting the flow to 0 is a place-holder when setting up
            # the Process Flow Diagram, because the actual total flow from
            # upstream unit may not have been completely configured. The
            # self.discharge() method of the upstream unit will totalize the
            # flow and blend the components before passing them into the
            # current unit.
            self._inlet[discharger] = 0
            self._has_discharger = True

            if upst_branch == 'Main':
                discharger.set_downstream_main(self)
            elif upst_branch == 'Side':
                discharger.set_downstream_side(self)
            else:
                print("ERROR: UNKNOWN BRANCH SPECIFIED.")

        return None


    def has_discharger(self):
        return self._has_discharger


    def get_upstream(self):
        return self._inlet


    def totalize_inflow(self):
        if self._upstream_set_mo_flow:
            self._total_inflow = sum(self._inlet.values())
        else:
            self._total_inflow = self._mo_flow + self._so_flow
        return self._total_inflow


    def blend_inlet_comps(self):
        if self._total_inflow:  # make sure it's not 0
            for i in range(constants._NUM_ASM1_COMPONENTS):
                temp = 0.0
                for unit in self._inlet:
                    if self == unit.get_downstream_main():
                        temp += unit.get_main_outlet_concs()[i]\
                                * unit.get_main_outflow()
                    else:
                        temp += unit.get_side_outlet_concs()[i]\
                                * unit.get_side_outflow()
                self._in_comps[i] = temp / self._total_inflow
        return None
    

    def update_combined_input(self):
        ''' Combined the flows and loads into the current unit'''

        self.totalize_inflow()
        self.blend_inlet_comps()
        return None
    

    def remove_upstream(self, discharger):
        if discharger in self._inlet:
            self._inlet.pop(discharger)
            self._upstream_set_mo_flow = False
            if discharger.get_downstream_main() == self:
                discharger.set_downstream_main(None)
            else:
                discharger.set_downstream_side(None)
            self._has_discharger = len(self._inlet) > 0
        else:
            print("ERROR:", self.__name__, "inlet unit not found for removal.")
        return None
    

    def set_downstream_main(self, rcvr):
        if rcvr == None:
            self._main_outlet = None
            self._mo_connected = False
        elif self._main_outlet != rcvr:
            if not isinstance(rcvr, influent):
                self._main_outlet = rcvr 
                self._mo_connected = True
                rcvr.add_upstream(self)
            else:
                print("ERROR: Influent types CAN NOT be the main outlet of",
                    self.__name__)
        return None
    

    def main_outlet_connected(self):
        return self._mo_connected


    def get_downstream_main(self):
        return self._main_outlet


    def set_mainstream_flow_by_upstream(self, f=True):
        self._upstream_set_mo_flow = f
        return None


    def set_mainstream_flow(self, flow=0):
        if flow >= 0:
            self._mo_flow = flow
            self._upstream_set_mo_flow = False
            self.set_flow_data_src('Main', flow_data_src.PRG)
        else:
            print("ERROR:", self.__name__, "given main flow < 0.")
            self._mo_flow = 0
        return None
            

    def get_main_outflow(self):
        #if not self._inflow_totalized:
        self.totalize_inflow()
        self._branch_flow_helper()
        if self._mo_flow < 0:
            print("WARN/ERROR:", self.__name__, "main outlet flow < 0.")
        return self._mo_flow


    def get_main_outlet_concs(self):
        #if self._in_comps_blended == False:
        #self.blend_inlet_comps()
        return self._mo_comps[:]
    

    def set_downstream_side(self, rcvr):
        if rcvr == None:
            self._side_outlet = None
            self._so_connected = False
        elif self._side_outlet != rcvr:
            if not isinstance(rcvr, influent):
                self._side_outlet = rcvr 
                self._so_connected = True
                rcvr.add_upstream(self, "Side")
            else:
                print("ERROR: Influent types CAN NOT be the side outlet of",
                        self.__name__)
        return None
                

    def side_outlet_connected(self):
        return self._so_connected


    def get_downstream_side(self):
        return self._side_outlet


    def set_sidestream_flow(self, flow=0):
        if flow >= 0:
            self._so_flow = flow
            self.set_flow_data_src('Side', flow_data_src.PRG)
            self._so_flow_defined = True
        else:
            self._so_flow_defined = False
            print('ERROR:', self.__name__, 'given side flow < 0')
        return None


    def sidestream_flow_defined(self):
        return self._so_flow_defined
    

    def get_side_outflow(self):
        #if not self._inflow_totalized:
        self.totalize_inflow()
        self._branch_flow_helper()
        if self._so_flow < 0:
            print("WARN/ERROR:", self.__name__,"side outlet flow < 0.")
        return self._so_flow


    def get_side_outlet_concs(self):
        return self._so_comps[:]
    

    def set_flow(self, dschgr, flow):
        if dschgr in self._inlet and flow >= 0:
            self._inlet[dschgr] = flow
        return None


    def _discharge_main_outlet(self):
        m = self.get_downstream_main()
        m.set_flow(self, self._mo_flow)
        m.update_combined_input()
        return None


    def _discharge_side_outlet(self):
        s = self.get_downstream_side()
        s.set_flow(self, self._so_flow)
        s.update_combined_input() 
        return None
 
 
    def discharge(self):
        self._prev_mo_comps = self._mo_comps[:]
        self._prev_so_comps = self._so_comps[:]

        self._branch_flow_helper()

        # for a typical splitter, concentrations at the main/side outlets equal
        # to those at the inlet
        self._mo_comps = self._in_comps[:]
        self._so_comps = self._in_comps[:]

        if self._main_outlet != None:            
            self._discharge_main_outlet()
        else:
            print("ERROR:", self.__name__, "main outlet incomplete")

        if self._side_outlet != None:
            self._discharge_side_outlet()
        elif self._has_sidestream:
            print("ERROR:", self.__name__, "side outlet incomplete")

        return None


    def get_TSS(self, br="Main_Out"):
        #TODO: need to make COD/TSS = 1.2 changeable for different type of
        # sludge
        index_list = [7, 8, 9, 10, 11]
        return self._sum_helper(br, index_list) / 1.2


    def get_VSS(self, br="Main_Out"):
        #TODO: need to make COD/VSS = 1.42 changeable for diff. type of sludge
        index_list = [7, 8, 9, 10, 11]
        return self._sum_helper(br, index_list) / 1.42
    

    def get_COD(self, br="Main_Out"):
        index_list = [1, 2, 7, 8, 9, 10, 11]
        return self._sum_helper(br, index_list)


    def get_sCOD(self, br="Main_Out"):
        index_list = [1, 2]
        return self._sum_helper(br, index_list)


    def get_pCOD(self, br="Main_Out"):
        return self.get_COD(br) - self.get_sCOD(br)


    def get_TN(self, br="Main_Out"):
        index_list = [3, 4, 5, 12]
        return self._sum_helper(br, index_list)


    def get_orgN(self, br="Main_Out"):
        index_list = [4, 12]
        return self._sum_helper(br, index_list)


    def get_inorgN(self, br="Main_Out"):
        return self.get_TN(br) - self.get_orgN(br)


    def get_pN(self, br="Main_Out"):
        return self._sum_helper(br, [12])


    def get_sN(self, br="Main_Out"):
        return self.get_TN(br) - self.get_pN(br)


    def _branch_flow_helper(self):
        # 1) Side outlet flow (_so_flow) can be set by
        #   1A) either WAS (_SRT_controller) or direct user input
        #
        #   ##2A) upstream (non _SRT_controller)##
        #
        # 2) Main outlet flow (_mo_flow) can be set by
        #
        #   2A) upstream automatically
        #
        #   2B) direct user/run_time input
        #
        # 3) Inlet flow is dependent on the two outlet branches' settings
        #       Back tracing will be required to make sure flows are balanced
        #       if both main and  side outlet flows are set either by user or
        #       run time SRT control.
        #
        if self._SRT_controller:  # i.e. _so_flow set by a WAS unit
            if self._upstream_set_mo_flow:
                #self._in_flow_backcalc = self._total_inflow
                #self._mo_flow = self._in_flow_backcalc - self._so_flow
                self._mo_flow = self._total_inflow - self._so_flow
            else:
                #self._in_flow_backcalc = self._mo_flow + self._so_flow
                self._total_inflow = self._mo_flow + self._so_flow
        elif self._upstream_set_mo_flow:
            #self._in_flow_backcalc = self._total_inflow
            #self._mo_flow = self._in_flow_backcalc - self._so_flow
            self._mo_flow = self._total_inflow - self._so_flow
        else:  # TODO: might be troubles here
            # if upstream doesn't set _mo_flow, it has to set _so_flow
            #self._in_flow_backcalc = self._total_inflow
            #self._so_flow = self._in_flow_backcalc - self._mo_flow
            self._so_flow = self._total_inflow - self._mo_flow
            self._so_flow_defined = True
        return None


    def _check_conc_cnvg(self, curr_comps=[], prev_comps=[], rel_lim=1E-3):
        # curr_comps: current model component state/results
        # prev_comps: previous round model component state/results
        # rel_lim: relative limit for convergence
        
        _nc = len(curr_comps)
        _cnvg = [False] * _nc
        rel_diff = []
        for i in range(_nc):
            if prev_comps[i] == 0 and curr_comps[i] == 0:
                _cnvg[i] = True
            else:
                #TODO: assuming prev_comps[i] > 0:
                _rd = abs(curr_comps[i] - prev_comps[i]) / prev_comps[i]
                rel_diff.append(_rd)
                _cnvg[i] = _rd <= rel_lim

        #print('rel_diff:', rel_diff)
        
        return _cnvg[:]

#
    # END OF COMMON INTERFACE DEFINITIONS
 
    
    # FUNCTIONS UNIQUE TO SPLITTER
    #
    def set_as_SRT_controller(self, setting=False):
        self._SRT_controller = setting
        #TODO: add notes here
        self._so_flow_defined = setting
        #TODO: HOW DOES THIS IMPACT WAS FLOW BASED ON USER SPECIFIED SRT?
        return None

    
    def is_SRT_controller(self):
        return self._SRT_controller


    def _sum_helper(self, branch="Main_Out", index_list=[]):
        ''' sum up the model components indicated by the index_list'''
        _sum = 0.0
        if branch == "Main_Out":
            _sum = sum(self._mo_comps[i] for i in index_list)
        elif branch == "Inlet":
            _sum = sum(self._in_comps[i] for i in index_list)
        elif branch == "Side_Out" and self.has_sidestream():
            _sum = sum(self._so_comps[i] for i in index_list)
        return _sum
    #
    # END OF FUNCTIONS UNIQUE TO SPLITTER

# ----------------------------------------------------------------------------

class pipe(splitter):
    __id = 0

    def __init__(self):
        splitter.__init__(self)
        self.__class__.__id += 1
        self.__name__ = 'Pipe_' + str(self.__id)

        self._type = "Pipe"
                
        # pipe has no sidestream
        self._has_sidestream = False

        # flow data source tags
        self._in_flow_ds = flow_data_src.TBD
        self._mo_flow_ds = flow_data_src.TBD
        self._so_flow_ds = flow_data_src.PRG

        # a pipe's sidestream flow IS DEFINED as ZERO
        self._so_flow_defined = True

        # inlet and main outlet components are identical for a pipe
        # make main outlet components an alias of the inlet components
        self._mo_comps = self._in_comps
        # side outlet components equal to the inlet, if they existed.
        # make side outlet components an alias of the inlet components
        self._so_comps = self._in_comps

        return None

    # ADJUSTMENTS TO COMMON INTERFACE TO FIT THE NEEDS OF PIPE:
    #
    def _branch_flow_helper(self):
        #self._in_flow_backcalc = self._mo_flow = self._total_inflow
        if self._upstream_set_mo_flow:
            self._mo_flow = self._total_inflow
        else:
            self._total_inflow = self._mo_flow
        return None


    #def set_mainstream_flow_by_upstream(self, f):
    #    print("WARN:", self.__name__, "main outlet flow source unchangeable.")
    #    return None


    #def set_mainstream_flow(self, flow):
    #    print("ERROR:", self.__name__, "main outlet flow not be set by user.")
    #    return None


    def set_downstream_side(self, receiver):
        print("WARN:", self.__name__, "has no sidestream.")
        return None
    

    def set_sidestream_flow(self, flow):
        print("WARN:", self.__name__,"has sidestream flow of ZERO.")
        return None

    #
    # END OF ADJUSTMENT TO COMMON INTERFACE


    # FUNCTIONS UNIQUE TO PIPE GO HERE:
    #
    # (INSERT CODE HERE)
    #
    # END OF FUNCTIONS UNIQUE TO PIPE


# -----------------------------------------------------------------------------

class influent(pipe):
    __id = 0

    def __init__(self):
        pipe.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "Influent_" + str(self.__id)

        self._type = "Influent"

        # influent has no further upstream discharger
        self._inlet = None

        # Trick the system by setting True to _has_discharger flag
        self._has_discharger = True
        # influent has no sidestream
        self._has_sidestream = False

        # flow data source tags
        self._in_flow_ds = flow_data_src.UPS
        self._mo_flow_ds = flow_data_src.UPS
        self._so_flow_ds = flow_data_src.PRG

        self._upstream_set_mo_flow = True

        # an influent is always "converged" within the time frame of interest
        self._converged = True

        # Influent characteristics from user measurements/inputs
        # Setting default values for municipal wastewater in USA
        # Default Unit: mg/L except where noted differently
        self._BOD5 = 250.0
        self._TSS = 250.0
        self._VSS = 200.0
        self._TKN = 40.0
        self._NH3 = 28.0
        self._NO = 0.0
        self._TP = 10.0
        self._Alk = 6.0  # in mmol/L as CaCO3
        self._DO = 0.0 

        # Plant influent flow in M3/DAY
        # TODO: will be user-input from GUI. FROM THE GUI, USER
        #   will use MGD. DEFAULT VALUE = 10 MGD. 
        self._design_flow = 37800

        return None
    
    # ADJUSTMENTS TO THE COMMON INTERFACE TO FIT THE NEEDS OF INFLUENT
    #

    def _branch_flow_helper(self):
        self._mo_flow = self._design_flow
        self._so_flow = 0.0
        return None


    def assign_initial_guess(self, init_guess_lst):
        pass


    def is_converged(self, limit=1E-4):
        return self._converged  # which is always True


    def add_upstream(self, discharger, branch):
        print("ERROR:", self.__name__, "has NO upstream.")
        return None


    def totalize_inflow(self):
        self._branch_flow_helper()
        #self._inflow_totalized = True
        return self._design_flow


    def blend_inlet_comps(self):
        self._in_comps = self._convert_to_model_comps()
        return None


    def remove_upstream(self, discharger):
        print("ERROR:", self.__name__, "has no upstream")
        return None


    def set_mainstream_flow(self, flow=37800):
        if flow > 0:
            self._design_flow = flow
        else:
            print("ERROR:", self.__name__, "shall have design flow > 0 M3/d."
                    "Design flow NOT CHANGED due to error in user input.")
        return None


    def set_mainstream_flow_by_upstream(self, f):
        pass


    def get_main_outflow(self):
        return self._design_flow


    def set_flow(self, discharger, flow):
        pass


    def discharge(self):

        # influent concentrations don't change for steady state simulation
        self._prev_mo_comps = self._prev_so_comps = self._in_comps[:]
        self._mo_comps = self._so_comps = self._in_comps[:]
 
        if self._main_outlet != None:            
            self._discharge_main_outlet()
        else:
            print("ERROR:", self.__name__, "main outlet incomplete")

        return None
    #
    # END OF ADJUSTMENT TO COMMON INTERFACE

    
    # FUNCTIONS UNIQUE TO INFLUENT
    #
    # (INSERT CODE HERE)
    #
    def set_fractions(self):
        # TODO: set fractions for converting user measured influent
        # characteristics into ASM1 model components.
        pass

    def _convert_to_model_comps(self):
        #TODO: the first set of conversion available here is for municipal 
        #   wastewater. Industrial wastewater may have completely different
        #   conversion factors and needs to be tested.
        
        # influent biodegradable COD, BOD/COD = 1.71 for typ. muni.WW
        Inf_CODb = self._BOD5 * 1.71
        # influent total COD, COD/BOD5 = 2.04 per BioWin
        Inf_CODt = self._BOD5 * 2.04
        # influent total innert COD, 
        Inf_CODi = Inf_CODt - Inf_CODb
        # influent soluble innert COD
        Inf_S_I = 0.13 * Inf_CODt
        # influent particulate innert COD
        Inf_X_I = Inf_CODi - Inf_S_I
        # influent particulate biodegradable COD
        Inf_X_S = 1.6 * self._VSS - Inf_X_I
        # influent soluble biodegradable COD
        Inf_S_S = Inf_CODb - Inf_X_S
        # influent Heterotrophs (mgCOD/L), 
        Inf_X_BH = 0.0
        # influent Autotrophs (mgCOD/L), 
        Inf_X_BA = 0.0
        # influent Biomass Debris (mgCOD/L)
        Inf_X_D = 0.0
        
        # influent TKN (mgN/L), NOT IN InfC
        Inf_TKN = self._TKN
        # influent Ammonia-N (mgN/L), 
        Inf_S_NH = self._NH3
        # subdividing TKN into: 
        #  a) nonbiodegradable TKN 
        NonBiodegradable_TKN_Ratio = 0.03 # TODO: need to be configurable
        # NON-BIODEGRADABLE TKN WILL HAVE TO BE ADDED BACK TO THE EFFLUENT TN
        Inf_nb_TKN = Inf_TKN * NonBiodegradable_TKN_Ratio
        #  Grady 1999:
        Soluble_Biodegradable_OrgN_Ratio = Inf_S_S / (Inf_S_S + Inf_X_S)
        #  b) soluble biodegrable TKN,     
        Inf_S_NS = (Inf_TKN - Inf_S_NH - Inf_nb_TKN)\
                    * Soluble_Biodegradable_OrgN_Ratio
        #  c) particulate biodegradable TKN
        Inf_X_NS = (Inf_TKN - Inf_S_NH - Inf_nb_TKN)\
                    * (1.0 - Soluble_Biodegradable_OrgN_Ratio)
        
        # influent Nitrite + Nitrate (mgN/L)
        Inf_S_NO = self._NO
        
        Inf_S_ALK = self._Alk
        
        Inf_S_DO = self._DO
        
        _inf_concs = [Inf_S_DO, Inf_S_I, Inf_S_S, Inf_S_NH, Inf_S_NS, 
                        Inf_S_NO, Inf_S_ALK, 
                        Inf_X_I, Inf_X_S, Inf_X_BH, Inf_X_BA, Inf_X_D,
                        Inf_X_NS]
        return _inf_concs[:]
    # 
    # END OF FUNTIONS UNIQUE TO INFLUENT

# -----------------------------------------------------------------------------

class effluent(pipe):
    __id = 0

    def __init__(self):
        pipe.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "Effluent_" + str(self.__id)

        self._type = "Effluent"

        # flow data source tags
        self._in_flow_ds = flow_data_src.TBD
        self._mo_flow_ds = flow_data_src.TBD
        self._so_flow_ds = flow_data_src.PRG

        #self._upstream_set_mo_flow = True
        self._mo_connected = True  # dummy

        return None

    # ADJUSTMENTS TO COMMON INTERFACE TO FIT THE NEEDS OF EFFLUENT
    #

    def _branch_flow_helper(self):
        # the _mo_flow of an effluent is set externally (global main loop)
        if self._upstream_set_mo_flow:
            self._mo_flow = self._total_inflow  # _so_flow = 0
        return None


    def set_downstream_main(self, rcvr):
        print("ERROR:", self.__name__,"shall not have any receiver.")
        return None


    def set_mainstream_flow(self, flow=0):
        if flow >= 0:
            self._mo_flow = flow
            self.set_flow_data_src('Main', flow_data_src.PRG)
            self._upstream_set_mo_flow = False
        else:
            print("ERROR:", self.__name__, "receives flow < 0.")
            self._mo_flow = 0.0
        return None


    def discharge(self):
        self._prev_mo_comps = self._mo_comps[:]
        self._prev_so_comps = self._so_comps[:]

        self._branch_flow_helper()

        self._mo_comps = self._in_comps[:]
        self._so_comps = self._in_comps[:]

        return None

    #
    # END OF ADJUSTMENTS TO COMMON INTERFACE

    # FUNCTIONS UNIQUE TO EFFLUENT
    #
    # (INSERT CODE HERE)
    #
    # END OF FUNCTIONS UNIQUE TO EFFLUENT



# ------------------------------------------------------------------------------

class WAS(pipe):
    __id = 0

    def __init__(self):
        pipe.__init__(self)
        self.__class__.__id += 1
        self.__name__ = 'WAS_' + str(self.__id)
        
        self._type = "WAS"

        # flow data source tags
        self._in_flow_ds = flow_data_src.DNS
        self._mo_flow_ds = flow_data_src.PRG
        self._so_flow_ds = flow_data_src.PRG

        # assume something always receives WAS
        self._mo_connected = True

        return None

    # ADJUSTMENTS TO COMMON INTERFACE TO FIT THE NEEDS OF WAS OBJ.
    #
    def discharge(self):
        self._prev_mo_comps = self._mo_comps[:]
        self._prev_so_comps = self._so_comps[:]

        self._branch_flow_helper()

        # WAS typically functions as an effluent obj. However, it can also be
        # a pipe obj. that connects to solids management process units.
        # Therefore, the discharge function allows a None at the main outlet.
        if self._main_outlet != None:            
            self._discharge_main_outlet() 

        self._mo_comps = self._in_comps[:]
        self._so_comps = self._in_comps[:]

        return None

    #
    # END OF ADJUSTMENTS TO COMMON INTERFACE


    # FUNCTIONS UNIQUE TO WAS
    #
    # (INSERT CODE HERE)
    #

    def get_solids_inventory(self, reactor_list=[]):
        ''' Calculate the total solids mass in active reactors '''
        # reactor_list stores the asm_reactor units that contribute
        # active biomass growth to the WWTP.
        # The result of this function will be used to determine the WAS
        # flow for the entire WWTP.
        #TODO: In the MAIN program, we will need to maintain a list of 
        # reactors that contribute active solids to the WWTP.

        inventory = 0.0
        for unit in reactor_list:
            inventory += unit.get_TSS() * unit.get_active_vol()

        #inventory = inventory / 1000.0  # Convert unit to Kg

        return inventory


    def set_WAS_flow(self, SRT=5, reactor_list=[], effluent_list=[]):
        #SRT is the plant's SRT from user input. Default 5 days.
        self.update_combined_input()

        _eff_solids = 0.0
        for _u in effluent_list:
            _eff_solids += _u.get_TSS() * _u.get_main_outflow()

        _wf = 0.0
        if self.get_TSS() != 0:
            _wf = ((self.get_solids_inventory(reactor_list) / SRT
                    - _eff_solids ) / self.get_TSS())

        # screen out the potential < 0 WAS flow
        if _wf < 0:
            print('WARN: SRT specified can not be achieved.')
            self._mo_flow = 0.0
        else:
            self._mo_flow = _wf

        #TODO: in MAIN function, we need to check whether the WAS flow
        # is higher than the influent flow; The WAS flow is then passed to the
        # SRT controlling splitter by the main loop.
        return self._mo_flow

    #
    # END OF FUNCTIONS UNIQUE TO WAS
