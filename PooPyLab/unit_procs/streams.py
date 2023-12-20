# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment processes using International Water
# Association Activated Sludge Models.
#
#    Copyright (C) Kai Zhang
#
#    This program is free software: you can redistribute it and/or modify it under the terms of the GNU
#    General Public License as published by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
#    the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
#    License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program. If not, see
#    <http://www.gnu.org/licenses/>.
#
#
# This file defines the following classes related to streams: pipe, influent, effluent, splitter, WAS.
#
# ----------------------------------------------------------------------------


"""Defines basic stream elements for a wastewater treatment plant (WWTP):

    1) Splitter

    2) Pipe

    3) Influent

    4) Effluent

    5) Waste Activated Sludge (WAS)
"""
## @namespace streams
## @file streams.py

import math

from ..unit_procs.base import poopy_lab_obj
from ..utils.datatypes import flow_data_src
#from ..ASMModel import constants

# -----------------------------------------------------------------------------


class splitter(poopy_lab_obj):
    """
    Stream element with an inlet, a mainstream outlet, and a sidestream outlet.

    There are three connection points for the flows to get in and out of a splitter: an inlet, a mainstream
    outlet, and a sidestream outlet.

    General Functions:

        It is assumed that there is no significant biochemical reactions happening across a splitter unit.
        It only maintains the flow balance around the three connections. Therefore, the model components (as
        concentrations) are identical for all the connections after proper flow and load updates.

        Flow balance is maintained using the flow data source tags of two of the three connection points (see
        below for more details).

    Special Functions:

        When specified as an SRT (solids retention time) controller, a splitter would have to be connected
    with a WAS (waste activated sludge) unit at its sidestream. """

    __id = 0

    def __init__(self):
        """
        Constructor for "splitter"
        """
        ## type string of the process unit
        self._type = "Splitter"

        self.__class__.__id += 1
        self._id = self.__class__.__id

        self.__name__ = "Splitter_" + str(self._id)

        ## code name is for use in system equation writing:
        self._codename = self.__name__ + '_' + self._type + '_' + str(self._id)

        ## TODO: save the specification in a file (in what format?)

        ## upstream units and their flows in the format of {unit: Flow}
        self._inlet = {}
        ## mainstream outlet, a single receiver
        self._main_outlet = None
        ## sidestream outlet, a single receiver
        self._side_outlet = None

        ## flag on whether there are upstream units
        self._has_discharger = False
        ## flag on whether there is a sidestream, always True for a splitter
        self._has_sidestream = True

        ## flag on whether the mainstream outlet is connected
        self._mo_connected = False
        ## flag on whether the sidestream outlet is connected
        self._so_connected = False

        ## whether the mainstream outflow is by inflow - sidestream outflow
        self._upstream_set_mo_flow = False

        ## flow data source tag for inlet
        self._in_flow_ds = flow_data_src.TBD
        ## flow data source tag for mainstream outlet
        self._mo_flow_ds = flow_data_src.TBD
        ## flow data source tag for sidestream outlet
        self._so_flow_ds = flow_data_src.TBD


        ## TODO: This flag can probably be removed when a specification file is used
        ## flag to confirm it has received _so_flow > 0 m3/d
        self._so_flow_defined = False

##        ## mainstream outflow, m3/d
##        self._mo_flow = 0.0
##        ## sidestream outflow, m3/d
##        self._so_flow = 0.0
##        ## total inlet flow, m3/d
##        self._total_inflow = 0.0
##
        # TODO: not sure why saturated DO estimate is here.
        # site elevation, meter above MSL
        self._elev = 100.0
        # water salinity, GRAM/L
        self._salinity = 1.0
        # water temperature, degC
        self._ww_temp = 20.0
        # saturated DO conc. under the side condition
        self._DO_sat_T = self.get_saturated_DO()

        ## flag on whether this splitter is SRT controller
        self._SRT_controller = False

        # inlet/main_outlet/side_oulet model components:
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
        #
        ## TODO: With equation based solving system, these can probably simply be empty lists
        ## inlet model components
        self._in_comps = []
        ## mainstream outlet model components
        self._mo_comps = []
        ## sidestream outlet model components
        self._so_comps = []

##        ## mainstream outlet model components for the previous round
##        self._prev_mo_comps = [0.00001] * constants._NUM_ASM1_COMPONENTS
##        ## sidestream outlet model components for the previous round
##        self._prev_so_comps = [0.00001] * constants._NUM_ASM1_COMPONENTS
##
##        ## flag on convergence status
##        self._converged = False
##
        return None


    # COMMON INTERFACES DEFINED IN POOPY_LAB_OBJ (BASE)
    #


    def set_name(self, new_name='New_Name_Not_Given'):
        self.__name__ = new_name
        self._codename = self.__name__ + '_' + self._type + '_' + str(self._id)
        return None


    def get_name(self):
        return self.__name__


    def get_codename(self):
        return self._codename


    def set_flow_data_src(self, branch='Main', flow_ds=flow_data_src.TBD):
        """
        Set the flow data source of the branch specified by the user.

        This function helps to decide how a stream process unit (splitter, pipe, influent, effluent, WAS,
        etc.) performs flow balance calculations.

        For instance, if the user defines both the mainstream and sidestream outlet flow rates, then the
        inlet flow rate will be calculated as the sum of the two branches. As another example, if the user
        only defines the sidestream branch flow rate, then the mainstream branch flow will be determined as
        (total_inflow - sidestream_outflow).

        When setting the flow data source of a branch, the function will check to see whether the flow data
        sources for the other two brachnes can also be determined.

        Args:
            branch:     'Main'|'Side'|'Inlet'
            flow_ds:    flow_data_source.TBD|.UPS|.DNS|.PRG

        Return:
            None

        See:
            _branch_flow_helper(),
            set_mainstream_flow_by_upstream(),
            totalize_inflow(),
            utils.flow_data_src.
        """

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

        _mo_flow_by_ext = (self._mo_flow_ds == flow_data_src.DNS or self._mo_flow_ds == flow_data_src.PRG)

        _so_flow_by_ext = (self._so_flow_ds == flow_data_src.DNS or self._so_flow_ds == flow_data_src.PRG)

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
        """
        Return the flow data source tags of all three branches.
        """

        return self._in_flow_ds, self._mo_flow_ds, self._so_flow_ds


    def assign_initial_guess(self, init_guess_lst):
        """
        Assign the intial guess to the unit before simulation.

        All three branches of a stream element will get the same model components.

        Args:
            init_guess_lst: list of model components (concentrations)

        Return:
            None
        """

        self._in_comps = init_guess_lst[:]
        self._mo_comps = init_guess_lst[:]
        self._so_comps = init_guess_lst[:]
        return None


    def get_type(self):
        """
        Return the type string of the process unit.

        Args:
            None

        Return:
            str
        """
        return self._type


    def has_sidestream(self):
        """
        Return whether the unit has a sidestream.

        Args:
            None

        Return:
            bool
        """
        return self._has_sidestream


    def add_upstream(self, discharger, upst_branch='Main'):
        """
        Add the discharger's branch to inlet.

        This function add an upstream unit's (discharger's) outlet, as specified by the ups_branch parameter,
        to the current inlet.

        The function first checks whether the specified discharger is already in self._inlet. If so, does
        nothing. Otherwise, add the discharger into self._inlet and put 0.0 m3/d as a place holder for the
        corresponding flow rate.

        An error message will display if upst_branch is neither 'Main' nor 'Side'. And the specified
        discharger will NOT be added to self._inlet as a result.

        After adding the discharger into self._inlet. This function calls the discharger's
        set_downstream_main()/set_downstream_side() to connect its mainstream/sidestream outlet to the
        current unit's inlet.

        Upon sucessful addition of the specified discharger and its branch, the self._has_discharger flag is
        set to True.

        Args:
            discharger: the process unit to be added to self._inlet;
            upst_branch: branch of the discharger to get flow from.

        See:
            set_downstream_main(),
            set_downstream_side(),
            remove_upstream().
        """

        if discharger not in self._inlet:
            self._inlet[discharger] = 0.0  # place holder
            if upst_branch == 'Main':
                self._has_discharger = True
                discharger.set_downstream_main(self)
            elif upst_branch == 'Side':
                self._has_discharger = True
                discharger.set_downstream_side(self)
            else:
                print("ERROR: UNKNOWN BRANCH SPECIFIED.")

        return None


    def get_upstream(self):
        """
        Return the _inlet {} of the unit.

        Args:
            None

        Return:
            {unit_addr: flow into self._inlet}
        """
        return self._inlet


    def has_discharger(self):
        """
        Return whether the unit's inlet has been connected.

        Args:
            None

        Return:
            bool
        """
        return self._has_discharger


    def remove_upstream(self, discharger):
        """
        Remove an existing discharger from inlet.

        This function first checks whether the specified discharger to be removed exists in self._inlet:

            If so, proceed and remove it from self._inlet. Then it finds out which branch of the discharger
            is originally connected to current unit's inlet, inform the original discharger to update its
            corresponding branch's connection. The _has_discharger flag will be checked and updated when an
            upstream discharger is removed successfully.

            If not, an error message will be displayed and nothing will be removed from the self._inlet.

        Args:
            discharger: An inlet unit to be removed.

        Return:
            None

        See:
            add_upstream()
        """

        if discharger in self._inlet:
            self._inlet.pop(discharger)
            self._upstream_set_mo_flow = False
            if discharger.get_downstream_main() == self:
                discharger.set_downstream_main(None)
            else:
                discharger.set_downstream_side(None)
            self._has_discharger = len(self._inlet) > 0
        else:
            print('ERROR:', self.__name__, 'inlet unit not found for removal.')
        return None


    def set_downstream_main(self, rcvr):
        """
        Define the downstream main outlet by specifying the receiving process unit.

        An influent unit can not receive any flow from the current unit. An error message will be displayed
        if the specified receiver is of the influent type.

        If the specified receiver is already connected to the current unit's mainstream outlet branch,
        nothing will be done.

        Successful connection of the receiver and current unit's mainstream outlet will set the _mo_connected
        flag to True.

        Args:
            rcvr: A receiver of the current unit's mainstream outlet flow.

        Return:
            None

        See:
            add_upstream(),
            set_downstream_side().
        """

        if rcvr is None:
            self._main_outlet = None
            self._mo_connected = False
        elif self._main_outlet != rcvr:
            if not isinstance(rcvr, influent):
                self._main_outlet = rcvr
                self._mo_connected = True
                rcvr.add_upstream(self)
            else:
                print('ERROR: Influent types CAN NOT be the main outlet of',
                        self.__name__)
        return None


    def main_outlet_connected(self):
        """
        Return whether the mainstream outlet is connected.

        Args:
            None

        Return:
            bool
        """
        return self._mo_connected


    def get_downstream_main(self):
        """
        Return the process unit connected at the mainstream outlet.

        Args:
            None

        Return:
            poopy_lab_obj
        """
        return self._main_outlet


    def set_downstream_side(self, rcvr):
        """
        Define the downstream side outlet's connection.

        An influent unit can not receive any flow from the current unit. An error message will be displayed
        if the specified receiver is of the influent type.

        If the specified receiver is already connected to the current unit's sidestream outlet branch,
        nothing will be done.

        Successful connection of the receiver and current unit's sidestream outlet will set the _so_connected
        flag to True.

        Args:
            rcvr: receiver of the current unit's sidestream outlet flow.

        See:
            add_upstream(),
            set_downstream_main().
        """

        if rcvr is None:
            self._side_outlet = None
            self._so_connected = False
        elif self._side_outlet != rcvr:
            if not isinstance(rcvr, influent):
                self._side_outlet = rcvr
                self._so_connected = True
                rcvr.add_upstream(self, 'Side')
            else:
                print("ERROR: Influent types CAN NOT be the side outlet of", self.__name__)
        return None


    def side_outlet_connected(self):
        """
        Return True if the main outlet is connected, False if not.

        Args:
            None

        Return:
            bool
        """
        return self._so_connected


    def get_downstream_side(self):
        """
        Return the process unit connected to the side outlet.

        Args:
            None

        Return:
            poopy_lab_obj
        """
        return self._side_outlet


    def sidestream_flow_defined(self):
        """
        Return whether the sidestream flow rate has been defined.

        Args:
            None

        Return:
            bool
        """
        return self._so_flow_defined


    def get_side_outlet_concs(self):
        """
        Return a copy of the sidestream outlet concentrations.

        Args:
            None

        Return:
            list
        """
        return self._so_comps[:]


    def get_TSS(self, br='Main'):
        """
        Return the Total Suspended Solids of the specified branch.
        """
        #TODO: need to make COD/TSS = 1.2 changeable for different type of
        # sludge
        index_list = [7, 8, 9, 10, 11]
        return self._sum_helper(br, index_list) / 1.2


    def get_VSS(self, br='Main'):
        """
        Return the Volatile Suspended Solids of the specified branch.
        """
        #TODO: need to make COD/VSS = 1.42 changeable for diff. type of sludge
        index_list = [7, 8, 9, 10, 11]
        return self._sum_helper(br, index_list) / 1.42


    def get_COD(self, br='Main'):
        """
        Return the Chemical Oxygen Demand (total) of the specified branch.
        """
        index_list = [1, 2, 7, 8, 9, 10, 11]
        return self._sum_helper(br, index_list)


    def get_sCOD(self, br='Main'):
        """
        Return the soluble COD of the specified branch.
        """
        index_list = [1, 2]
        return self._sum_helper(br, index_list)


    def get_pCOD(self, br='Main'):
        """
        Return the particultate COD of the specified branch.
        """
        return self.get_COD(br) - self.get_sCOD(br)


    def get_TN(self, br='Main'):
        """
        Return the total nitrogen of the specified branch.

        TN = TKN + NOx_N
        """
        index_list = [3, 4, 5, 12]
        return self._sum_helper(br, index_list)


    def get_orgN(self, br='Main'):
        """
        Return the organic nitrogen of the specified branch.
        """
        index_list = [4, 12]
        return self._sum_helper(br, index_list)


    def get_inorgN(self, br='Main'):
        """
        Return the inorganic nitrogen of the specified branch.
        """
        return self.get_TN(br) - self.get_orgN(br)


    def get_pN(self, br='Main'):
        """
        Return the particulate nitrogen of the specified branch.
        """
        return self._sum_helper(br, [12])


    def get_sN(self, br='Main'):
        """
        Return the soluble nitrogen of the specified branch.
        """
        return self.get_TN(br) - self.get_pN(br)


    def update_proj_conditions(self, ww_temp=20, elev=100, salinity=1.0):
        """
        Update the site conditions for the process unit.

        Args:
            ww_temp:    water/wastewater temperature, degC
            elev:       site elevation above mean sea level, meter
            salinity:   salinity of w/ww, GRAM/L

        Return:
            None

        See:
            get_saturated_DO().
        """
        if ww_temp > 4 and ww_temp <= 40\
                and elev >= 0 and elev <= 3000\
                and salinity >= 0:
            self._ww_temp = ww_temp
            self._elev = elev
            self._salinity = salinity
            self._DO_sat_T = self.get_saturated_DO()
        else:
            print(self.__name__, ' ERROR IN NEW PROJECT CONDITIONS. NO UPDATES')

        return None


    def get_saturated_DO(self):
        """
        Calculate the saturated DO conc. based on current project conditions.

        Current project conditions are defined in self._ww_temp, self._elev, and self._salinity

        Reference:
            USCIS Office of Water Quality Technical Memorandum 2011.03 Change to Solubility Equations
            for Oxygen in Water

        Args:
            None

        Return:
            O2 Solubility (saturation conc.), mg/L
        """

        T = self._ww_temp + 273.15  # convert degC to degK

        # first, estimate the DO_sat_0 at 0 salinity and 1 atm, which is done by
        # using the Benson-Krause equations:
        DO_sat_0 = math.exp(- 139.34411 + 1.575701E5 / T
                            - 6.642308E7 / T**2 + 1.2438E10 / T**3
                            - 8.621949E11 / T**4)

        # second, estimate the salinity factor, Fs
        Fs = math.exp(-self._salinity * (0.017674 - 10.754/T + 2140.7/T**2))

        # third, estimate the pressure factor, Fp
        Patm_in_bar = 1.01325 * (1 - 2.25577E-5 * self._elev)**5.25588

        theta_0 = 0.000975 - 1.426E-5 * self._ww_temp + 6.436E-8 * self._ww_temp**2

        vapor_pres_water = math.exp(11.8571 - 3840.7 / T - 216961.0 / T**2)

        Fp = (Patm_in_bar - vapor_pres_water) * (1.0 - theta_0 * Patm_in_bar)\
                / (1.0 - vapor_pres_water) / (1.0 - theta_0)

        # finally, calculate the DO_sat for the site conditions
        DO_sat_T = DO_sat_0 * Fs * Fp

        return DO_sat_T

    # END OF COMMON INTERFACE DEFINITIONS


    # FUNCTIONS UNIQUE TO SPLITTER
    #

    def set_as_SRT_controller(self, setting=False):
        """
        Set the current splitter as an Solids Retention Time controller.

        There are specific rules for connected an SRT controlling splitter. Once set, the splitter shall have
        a sidestream connected to a pipe followed by a WAS (waste activated sludge) unit.

        Once set True, the sidestream flow will be determined during simulation by the downstream WAS unit.

        Args:
            setting: True/False

        Return:
            None

        See:
            utils.pfd.check();
            utils.pfd._check_connection().
        """

        self._SRT_controller = setting
        #TODO: add notes here
        self._so_flow_defined = setting
        #TODO: HOW DOES THIS IMPACT WAS FLOW BASED ON USER SPECIFIED SRT?
        return None


    def is_SRT_controller(self):
        """
        Return whether a splitter is an SRT controller.
        """
        return self._SRT_controller


##    def _sum_helper(self, branch='Main', index_list=[]):
##        """
##        Sum up the model components indicated by the index_list.
##
##        Args:
##            branch: {'Inlet'|'Main'|'Side'}
##            index_list: a list of indices for the model components to use
##
##        Return:
##            float
##        """
##
##        _sum = 0.0
##        if branch == 'Main':
##            _sum = sum(self._mo_comps[i] for i in index_list)
##        elif branch == 'Inlet':
##            _sum = sum(self._in_comps[i] for i in index_list)
##        elif branch == 'Side' and self.has_sidestream():
##            _sum = sum(self._so_comps[i] for i in index_list)
##        return _sum
    #
    # END OF FUNCTIONS UNIQUE TO SPLITTER


# ----------------------------------------------------------------------------

class pipe(splitter):
    """
    A derived "splitter" class with a blinded sidestream.

    No biochemical reactions are modelled in the pipe class. A pipe is only used to connect process units.

    A pipe can have multiple upstream dischargers but only one downstream (main) receiver.
    """

    __id = 0

    def __init__(self):
        """
        A few special steps are taken when initializing a "pipe":

            1) Its sidestream is connected to None, with the sidestream flow is fixed at 0 m3/d, and the
            _so_flow_defined set to True;

            2) Its _has_sidestream flag is fixed to False;

            3) Its sidestream flow data source (_so_flow_ds) is set to flow_data_src.PRG.
        """

        splitter.__init__(self)

        self.__class__.__id += 1

        ## type string of the process unit
        self._type = 'Pipe'

        self._id = self.__class__.__id

        self.__name__ = "Pipe_" + str(self._id)

        ## code name is for use in system equation writing:
        self._codename = self.__name__ + '_' + self._type + '_' + str(self._id)

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
##    def _branch_flow_helper(self):
##        """
##        Calculate 1 of the 3 branches' flow based on the other 2.
##
##        For a "pipe", the sidestream flow is set to 0 m3/d. The mainstream outlet flow always equals to the
##        total inlet flow.
##        """
##        if self._upstream_set_mo_flow:
##            self._mo_flow = self._total_inflow
##        else:
##            self._total_inflow = self._mo_flow
##        return None
##

    def set_downstream_side(self, receiver):
        """
        Define the downstream side outlet's connection.

        A "pipe" has no sidestream (set to "None"). This function is essentially by-passed with a warning
        message if called.
        """
        print("WARN:", self.__name__, "has no sidestream.")
        return None


##    def set_sidestream_flow(self, flow):
##        """
##        Define the flow rate for the sidestream.
##
##        This function is bypassed for a "pipe" whose sidestream is set to "None" and sidestream flow 0 m3/d.
##        A warning message is displayed if called.
##        """
##        print("WARN:", self.__name__, "has sidestream flow of ZERO.")
##        return None
##
    #
    # END OF ADJUSTMENT TO COMMON INTERFACE


    # FUNCTIONS UNIQUE TO PIPE GO HERE:
    #
    # (INSERT CODE HERE)
    #
    # END OF FUNCTIONS UNIQUE TO PIPE


# -----------------------------------------------------------------------------

class influent(pipe):
    """
    A derived "pipe" class with its inlet being "None".
    """

    __id = 0

    def __init__(self):
        """
        Special initialization steps for "influent".

        Reasons:

        1) has no further inlet;

        2) has no sidestream outlet;

        3) has no further upstream;

        4) convergence is irrelevant here;

        5) is the only source of flow/load to the WWTP.
        """

        pipe.__init__(self)

        self.__class__.__id += 1
        self._id = self.__class__.__id

        self._type = 'Influent'

        self.__name__ = 'Influent_' + str(self._id)

        ## code name is for use in system equation writing:
        self._codename = self.__name__ + '_' + self._type + '_' + str(self._id)

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
        self._NH3N = 28.0
        self._NOxN = 0.0
        self._TP = 10.0
        self._Alk = 6.0  # in mmol/L as CaCO3
        self._DO = 0.0

        # Fractionations of the influent. The fractions stored are for the raw
        # influent wastewater without any active biomass.
        # If influent with active biomass (X_BH, X_BA, etc.) is needed,
        # a dedicated Bio-Augmentation unit should be used with only model
        # components related to the biomass.
        self._model_fracs = {
                            'ASM1': 
                                {
                                    'COD:BOD5': 2.04,
                                    'SCOD:COD': 0.50,  #SCOD+PCOD = COD
                                    'RBCOD:SCOD': 0.80,  #RBCOD + UBSCOD = SCOD
                                    'SBCOD:PCOD': 0.70,  #SBCOD + UBPCOD = PCOD
                                    'SON:SCOD': 0.01,  #Sol.Org.N as a frac of SCOD
                                    'RBON:SON': 0.8,  #RBON + UBSON = SON
                                    'SBON:PON': 0.75  #SBON + UBPON = PON
                                },
                            'ASM2d':{},  #TODO: define for ASM-2d
                            'ASM3': {}   #TODO: define for ASM3
                            }

        # Plant influent flow in M3/DAY
        # TODO: will be user-input from GUI. FROM THE GUI, USER
        #   will use MGD. DEFAULT VALUE = 10 MGD.
        self._design_flow = 37800

        return None

    # ADJUSTMENTS TO THE COMMON INTERFACE TO FIT THE NEEDS OF INFLUENT
    #

##    def _branch_flow_helper(self):
##        """
##        Calculate 1 of the 3 branches' flow based on the other 2.
##
##        For an "influent" unit, the mainstream outflow always equals to its design flow.
##        """
##
##        self._mo_flow = self._design_flow
##        self._so_flow = 0.0
##        return None


    def assign_initial_guess(self, init_guess_lst):
        """
        Assign the intial guess to the unit before simulation.

        There is no need for assigning any initial guesses to an "influent" unit. This function is by-passed
        for "influent".
        """
        pass


##    def is_converged(self, limit=1E-6):
##        """
##        Return the convergence status of the unit.
##
##        The "influent" unit gets flows and loads from the user. Convergence is irrelevant here. This function
##        is by-passed for "influent" by setting the _converged to True.
##        """
##        return self._converged  # which is always True


    def add_upstream(self, discharger, branch):
        """
        Add the discharger's branch to inlet.

        The "influent" has no further upstream within the context of simulation. This function is by-passed
        with an ERROR message displayed.
        """
        print("ERROR:", self.__name__, "has NO upstream.")
        return None


##    def totalize_inflow(self):
##        """
##        Combine the individual flows specified in the self._inlet into one.
##
##        For an "influent" unit, there is no further upstream. The total inflow is the design flow.
##
##        See:
##            _branch_flow_helper()
##        """
##        self._branch_flow_helper()
##        return self._design_flow
##
##
##    def blend_inlet_comps(self):
##        """
##        Calculate the flow weighted average model component concentrations.
##
##        This function is re-implemented for the "influent" who doesn't have further upstream units
##        discharging into it. Rather, this function becomes a wrapper for the _convert_to_model_comps() which
##        fractions the wastewater constituents measured in BOD, TSS, VSS, TKN, NH3-N, etc. into the model
##        components such as substrate COD, slowly biodegradable COD, inert suspended solids, etc.
##
##        Args:
##            None
##
##        Return:
##            Copy of the blended influent components.
##
##        See:
##            _convert_to_model_comps().
##        """
##        self._in_comps = self._convert_to_model_comps(asm_ver='ASM1', verbose=False)
##        return self._in_comps[:]
##

    def remove_upstream(self, discharger):
        """
        Remove an existing discharger from inlet.

        This function is bypassed for the "influent" who has no further upstream. An error message displays
        when called.
        """
        print("ERROR:", self.__name__, "has no upstream")
        return None


##    def set_mainstream_flow(self, flow=37800):
##        """
##        Define the mainstream outlet flow.
##
##        This function is re-implemented for the "influent" and essentially becomes a wrapper for setting the
##        design flow (m3/d).
##
##        Args:
##            flow:   design flow of the influent, m3/d
##
##        Return:
##            None
##        """
##        if flow > 0:
##            self._design_flow = flow
##        else:
##            print("ERROR:", self.__name__, "shall have design flow > 0 M3/d."
##                    "Design flow NOT CHANGED due to error in user input.")
##        return None


    def set_mainstream_flow_by_upstream(self, f):
        """
        Set whether the mainstream flow = (total inflow - side outflow).

        This function is essentially bypassed for the "influent" since the design flow (influent mainstream
        outflow) is directly set by the user.
        """
        pass


##    def get_main_outflow(self):
##        """
##        Return the mainstream outlet flow.
##
##        For an "influent", this function will return the design flow.
##
##        Return:
##            self._design_flow
##        """
##        return self._design_flow
##
##
##    def set_flow(self, discharger, flow):
##        """
##        Specify the flow from the discharger.
##
##        This function is bypassed for the "influent".
##        """
##        pass
##
##
##    def discharge(self, method_name='BDF', fix_DO=True, DO_sat_T=10):
##        """
##        Pass the total flow and blended components to the downstreams.
##
##        This function is re-implemented for the "influent". An "influent" does not care the changes from the
##        previous round to the current since it is the source for the entire WWTP. Therefore, _prev_mo_comps,
##        _prev_so_comps, _mo_comps, and _so_comps all equal to _in_comps.
##
##        Args:
##            (see the note in the discharge() in the splitter class)
##
##        Return:
##            None
##        """
##
##        # influent concentrations don't change for steady state simulation
##        self._prev_mo_comps = self._prev_so_comps = self._in_comps[:]
##        self._mo_comps = self._so_comps = self._in_comps[:]
##
##        if self._main_outlet is not None:
##            self._discharge_main_outlet()
##        else:
##            print("ERROR:", self.__name__, "main outlet incomplete")
##
##        return None
    #
    # END OF ADJUSTMENT TO COMMON INTERFACE


    # FUNCTIONS UNIQUE TO INFLUENT
    #
    # (INSERT CODE HERE)
    #


    def set_constituents(self, asm_ver='ASM1', inf_concs=[]):
        """
        Set the conventional influent constituents.

        Usually called at top level when the entire inf_concs is defined and validated.

        Args:
            asm_ver:        version of ASM: ASM1 | ASM2d | ASM3
            inf_concs:      list of influent constituents (see Note)

        Return:
            None

        Note:
            There are 9 elements in inf_concs for ASM1:
                inf_concs[0] : self._BOD5
                inf_concs[1] : self._TSS
                inf_concs[2] : self._VSS
                inf_concs[3] : self._TKN
                inf_concs[4] : self._NH3N
                inf_concs[5] : self._NOxN
                inf_concs[6] : self._TP
                inf_concs[7] : self._Alk
                inf_concs[8] : self._DO
        """

        if asm_ver == 'ASM1' and len(inf_concs) == 9:
            self._BOD5 = inf_concs[0]
            self._TSS = inf_concs[1]
            self._VSS = inf_concs[2]
            self._TKN = inf_concs[3]
            self._NH3N = inf_concs[4]
            self._NOxN = inf_concs[5]
            self._TP = inf_concs[6]
            self._Alk = inf_concs[7]
            self._DO = inf_concs[8]

        return None


    def set_fractions(self, asm_ver, frac_name, frac_val):
        """
        Set fractions to convert wastewater constituents into model components

        Args:
            asm_ver:        ASM version: 'ASM1' | 'ASM2d' | 'ASM3'
            frac_name:      name of the fractionation, ASM version dependent
            frac_val:       new value of the fraction specified by 'frac_name'

        Return:
            self._model_fracs.copy()
        """

        if asm_ver in self._model_fracs.keys()\
                and frac_name in self._model_fracs[asm_ver]:
            if (frac_name == 'COD:BOD5' and frac_val > 1.0)\
                    or (frac_name != 'COD:BOD5' and 0 <= frac_val <= 1.0):
                self._model_fracs[asm_ver][frac_name] = frac_val
                return self._model_fracs.copy()
            else:
                print('ERROR in new fraction value: FRACTIONS NOT UPDATED,'
                        'DEFAULT FRACTIONS USED.')

        return self._model_fracs.copy()


    def _convert_to_model_comps(self, asm_ver='ASM1', verbose=False):
        """
        Fractions the wastewater constituents into model components.

        Wastewater constituents often are measured in units such as Biochemical Oxygen Demand (BOD), Total
        Suspended Solids (TSS), Volatile SS (VSS), etc. Many mathematical models including IWA ASMs, however,
        measured organic carbons in Chemical Oxygen Demand (COD). This applies to soluble and particulate
        constituents. As a result, conversions between the two are needed.

        Currently this fuction is mainly set up to convert municipal wastewater's constituents into IWA ASM1.
        Industrial wastewater can have very different conversions coefficients. Also, the fractions will need
        to be revised for models different from IWA ASM1.

        Args:
            asm_ver:    ASM Version: 'ASM1' | 'ASM2d' | 'ASM3'
            verbose:    bool for whether to print the influent model components

        Return:
            list of model components for the influent characteristics user
            defined.
        """


        _temp_comps = self._in_comps[:]

        if asm_ver == 'ASM1':
            # total COD
            _TCOD = self._model_fracs['ASM1']['COD:BOD5'] * self._BOD5

            # soluble COD
            _SCOD = self._model_fracs['ASM1']['SCOD:COD'] * _TCOD

            # particulate COD
            _PCOD = _TCOD - _SCOD

            # readily biodegradable COD (biodeg. soluble COD)
            _RBCOD = self._model_fracs['ASM1']['RBCOD:SCOD'] * _SCOD

            # nonbiodegradable soluble COD
            _NBSCOD = _SCOD - _RBCOD

            # slowly biodegradable COD (biodeg. particulate COD)
            _SBCOD = self._model_fracs['ASM1']['SBCOD:PCOD'] * _PCOD

            # nonbiodegradable particulate COD
            _NBPCOD = _PCOD - _SBCOD

            # total organic N
            _TON = self._TKN - self._NH3N

            # soluble organic N
            _SON = self._model_fracs['ASM1']['SON:SCOD'] * _SCOD

            # particulate organic N
            _PON = _TON - _SON

            # readily biodegradable organic N (biodeg.sol.org N)
            # assuming RBON:SON = RBCOD:SCOD
            _RBON = self._model_fracs['ASM1']['RBCOD:SCOD'] * _SON

            # nonbiodeg. sol. org. N
            _UBSON = _SON - _RBON

            # slowly biodegradable organic N (biodeg.part.org. N)
            # assuming SBON:PON = SBCOD:PCOD
            _SBON = self._model_fracs['ASM1']['SBCOD:PCOD'] * _PON

            # nonbiodeg. part. org. N
            _UBPON = _PON - _SBON

            _temp_comps = [self._DO,
                            _NBSCOD, _RBCOD, self._NH3N, _RBON, self._NOxN,
                            self._Alk,
                            _NBPCOD, _SBCOD, 0.0, 0.0, 0.0, _SBON]

            # check if any negative values from the fractionation
            for tc in _temp_comps:
                if tc < 0:
                    print('ERROR in fractions resulting in negative model',
                            ' components. Influent components NOT UPDATED')
                    return self._in_comps[:]  # nothing changed


            if asm_ver == 'ASM1' and verbose:
                print("Model = ASM1, Influent Fractions Summary::")
                print("Total COD = {}  Soluble COD = {}".format(_TCOD, _SCOD),
                        " Particulate COD =", _PCOD)
                print("Readily Biodegradable (biodeg. sol.) COD =", _RBCOD,
                        " Non-Biodegradable Sol. COD =", _NBSCOD)
                print("Slowly Biodegradable (biodeg. part.) COD =", _SBCOD,
                        " Non-Biodegradable Part. COD =", _NBPCOD)
                print("Total TKN = {}  NH3-N = {}  Total Org.N = {}".format(self._TKN, self._NH3N, _TON))
                print("Soluble Org. N = {}  Part. Org. N = {}".format(_SON, _PON))
                print("Readily Biodegradable (biodeg. sol.) Org. N =", _RBON,
                        " Non-Biodegradable Sol. Org. N =", _UBSON)
                print("Slowly Biodegradable (biodeg. part.) Org.N =", _SBON,
                        " Non-Biodegradable part.Org. N =", _UBPON)

            #TODO: Add accounting for nonbiod sol. orgN and nonbiod part orgN
            return _temp_comps[:]


    #
    # END OF FUNTIONS UNIQUE TO INFLUENT


# -----------------------------------------------------------------------------


class effluent(pipe):
    """
    A derived "pipe" class whose main outlet is "None".

    The "effluent" class is another form of a "pipe". It differs from the "pipe" class with its outlet being
    "None".
    """

    __id = 0

    def __init__(self):
        """
        Special initialization for the "effluent".

        Reason:

        1) Mainstream outlet is "None".
        """
        pipe.__init__(self)

        self.__class__.__id += 1

        self._id = self.__class__.__id

        self._type = 'Effluent'

        self.__name__ = 'Effluent_' + str(self._id)

        self._codename = self.__name__ + '_' + self._type + '_' + str(self._id)

        # flow data source tags
        self._in_flow_ds = flow_data_src.TBD
        self._mo_flow_ds = flow_data_src.TBD
        self._so_flow_ds = flow_data_src.PRG

        self._mo_connected = True  # dummy

        return None

    # ADJUSTMENTS TO COMMON INTERFACE TO FIT THE NEEDS OF EFFLUENT
    #

##    def _branch_flow_helper(self):
##        """
##        Calculate 1 of the 3 branches' flow based on the other 2.
##
##        This function is re-implemented for "effluent" because the actual effluent flow rate of a WWTP has
##        to do with its waste sludge flow (WAS flow). The WAS flow is set during simulation by PooPyLab. As a
##        result, the effluent flow rate is the balance of the plant influent flow and WAS flow.
##
##        Occasionally, there may be a WWTP without dedicated WAS unit when the effluent flow rate equals to
##        that of the influent.
##        """
##
##        # the _mo_flow of an effluent is set externally (global main loop)
##        if self._upstream_set_mo_flow:
##            self._mo_flow = self._total_inflow  # _so_flow = 0
##        return None


#    def set_mainstream_flow(self, flow=0):
#        """
#        Define the mainstream outlet flow.
#
#        """
#        if flow >= 0:
#            self._mo_flow = flow
#            self.set_flow_data_src('Main', flow_data_src.PRG)
#            self._upstream_set_mo_flow = False
#        else:
#            print("ERROR:", self.__name__, "receives flow < 0.")
#            self._mo_flow = 0.0
#        return None
##
##
##    def discharge(self, method_name='BDF', fix_DO=True, DO_sat_T=10):
##        """
##        Pass the total flow and blended components to the downstreams.
##
##        This function is re-implemented for "effluent" because there is no further downstream units on either
##        the main or side outlet.
##
##        Args:
##            (see the note in the discharge() defined in the splitter class)
##
##        Return:
##            None
##
##        """
##        self._prev_mo_comps = self._mo_comps[:]
##        self._prev_so_comps = self._so_comps[:]
##
##        self._branch_flow_helper()
##
##        self._mo_comps = self._in_comps[:]
##        self._so_comps = self._in_comps[:]
##
##        return None
##
##    #
##    # END OF ADJUSTMENTS TO COMMON INTERFACE
##
##    # FUNCTIONS UNIQUE TO EFFLUENT
##    #
##    # (INSERT CODE HERE)
##    #
##    # END OF FUNCTIONS UNIQUE TO EFFLUENT
##


# ------------------------------------------------------------------------------



class WAS(pipe):
    """
    Waste Activated Sludge, basically a "pipe" with special functionality.

    A WAS unit has the capability of calculating its own flow based on:

        1) User defined solids retention time (SRT);

        2) Solids inventory in bioreactors it sees; and

        3) Its inlet's total suspended solids (TSS).

    It also differs from a "pipe" at its (mainstream) outlet which can be set as "None" or another process
    unit, a sludge digester for instance. The outlet of a "pipe", however, shall always be connected to
    another process unit.
    """

    __id = 0

    def __init__(self):
        """
        Special initialization for "WAS".

        Reasons:

        1) WAS flow is determined during simulation;

        2) WAS flow rate is passed onto upstream units for plant flow balance;

        3) WAS mainstream outlet can be either "None" or a process unit.
        """

        pipe.__init__(self)

        self.__class__.__id += 1
        self._id = self.__class__.__id

        self._type = 'WAS'
        self.__name__ = 'WAS_' + str(self._id)
        self._codename = self.__name__ + '_' + self._type + '_' + str(self._id)

        # flow data source tags
        self._in_flow_ds = flow_data_src.DNS
        self._mo_flow_ds = flow_data_src.PRG
        self._so_flow_ds = flow_data_src.PRG

        # assume something always receives WAS
        self._mo_connected = True

        return None

    # ADJUSTMENTS TO COMMON INTERFACE TO FIT THE NEEDS OF WAS OBJ.
    #
##    def discharge(self, method_name='BDF', fix_DO=True, DO_sat_T=10):
##        """
##        Pass the total flow and blended components to the downstreams.
##
##        WAS typically functions as an effluent obj. However, it can also be a pipe obj. that connects to
##        solids management process units. Therefore, the discharge function allows a None at the main outlet.
##
##        Args:
##            (see the note in discharge() defined in the splitter class)
##
##        Return:
##            None
##
##        """
##
##        self._prev_mo_comps = self._mo_comps[:]
##        self._prev_so_comps = self._so_comps[:]
##
##        self._branch_flow_helper()
##
##        # see doc string above
##        if self._main_outlet is not None:
##            self._discharge_main_outlet()
##
##        self._mo_comps = self._in_comps[:]
##        self._so_comps = self._in_comps[:]
##
##        return None
##
    #
    # END OF ADJUSTMENTS TO COMMON INTERFACE


    # FUNCTIONS UNIQUE TO WAS
    #
    # (INSERT CODE HERE)
    #


    def get_solids_inventory(self, reactor_list=[]):
        """
        Calculate the total solids mass in active reactors.

        Args:
            reactor_list: list of the asm_reactors with active treatment;

        Return:
            solids inventory (float) in grams.

        See:
            set_WAS_flow().
        """

        inventory = 0.0
        for unit in reactor_list:
            inventory += unit.get_TSS() * unit.get_active_vol()

        return inventory


    def set_WAS_flow(self, SRT=5, reactor_list=[], effluent_list=[]):
        """
        Set the waste sludge flow to meet the WWTP's solids retention time.

        Args:
            SRT:            WWTP's SRT in days;
            reactor_list:   list of active asm_reactors;
            effluent_list:  list of all effluent units in the WWTP.

        Return:
            Mainstream outflow in m3/d

        See:
            get_solids_inventory().
        """

        # TODO: Need to re-write this function
        #
        #self.update_combined_input()

        _eff_solids = 0.0
        for _u in effluent_list:
            _eff_solids += _u.get_TSS() * _u.get_main_outflow()

        _wf = 0.0
        if self.get_TSS() != 0:
            _wf = ((self.get_solids_inventory(reactor_list) / SRT
                    - _eff_solids) / self.get_TSS())

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
