#   This file is part of PooPyLab.
#
#    PooPyLab is a simulation software for biological wastewater treatment
#    processes using the International Water Association Activated Sludge
#    Models.
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
# --------------------------------------------------------------------
#   Definition of the base class for WWTP components.
#


""" Definitions of common interface for all PooPyLab objects.

The documentations for the abstract interface here are also abstract. Please
see more details in specific implementations.
"""
## @namespace base
## @file base.py


from abc import ABCMeta, abstractmethod


class poopy_lab_obj(object):
    """
    Conceptual definition of common interface.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def set_flow_data_src(self, branch, flow_ds):
        """
        Set the flow data source of the selected branch.
        """
        pass


    @abstractmethod
    def get_flow_data_src(self):
        """
        Get the flow data source tags of the unit.
        """
        pass


    @abstractmethod
    def assign_initial_guess(self, init_guess_lst):
        """
        Assign the intial guess to the unit before simulation.
        """
        pass


    @abstractmethod
    def is_converged(self, limit):
        """
        Return the convergence status of the unit.
        """
        pass


    @abstractmethod
    def get_type(self):
        """
        Return the type of the current object.
        """
        pass


    @abstractmethod
    def has_sidestream(self):
        """ 
        Check if the current unit has a sidestream discharge.

        Default = True, i.e. splitter always has a sidestream.
        """
        pass


    @abstractmethod
    def add_upstream(self, discharger, branch):
        """
        Add the discharger's branch to inlet.
        """
        pass


    @abstractmethod
    def has_discharger(self):
        """
        Return True if upstream is connected, False if not.
        """
        pass


    @abstractmethod
    def get_upstream(self):
        """ 
        Get the dict that stores all the upstream units that feed into
        the current one.
        """
        pass


    @abstractmethod
    def totalize_inflow(self):
        """
        Combine the individual flows specified in the self._inlet into one.
        """
        pass


    @abstractmethod
    def blend_inlet_comps(self):
        """
        Calculate the flow weighted average model component concentrations.

        Note: This function does not totalize inlet flow. It only uses the
        current flow rates. It is adviced to call totalize_inflow() first.
        """
        pass


    @abstractmethod
    def update_combined_input(self):
        """
        Update both the flows and loads for the current unit.
        """
        pass


    @abstractmethod
    def remove_upstream(self, discharger):
        """
        Remove an existing discharger from inlet.
        """
        pass


    @abstractmethod
    def set_downstream_main(self, receiver):
        """
        Define the main outlet by specifying the receiving process unit.
        """
        pass


    @abstractmethod
    def main_outlet_connected(self):
        """
        Return whether the main outlet of the unit is defined (connected).
        """
        pass


    @abstractmethod
    def get_downstream_main(self):
        """
        Return the process unit that is connected to the main outlet.
        """
        pass


    @abstractmethod
    def set_mainstream_flow_by_upstream(self, flag):
        """
        Set whether the mainstream flow = (total inflow - side outflow).
        """
        pass


    @abstractmethod
    def set_mainstream_flow(self, flow):
        """
        Define the mainstream outlet flow.
        """
        pass


    @abstractmethod
    def get_main_outflow(self):
        """
        Return the mainstream outlet flow.
        """
        pass


    @abstractmethod
    def get_main_outlet_concs(self):
        """
        Return a copy of the mainstream outlet concentrations.
        """
        pass


    @abstractmethod
    def set_downstream_side(self, receiver):
        """
        Define the downstream side outlet's connection.
        """
        pass


    @abstractmethod
    def side_outlet_connected(self):
        """
        Return True if the main outlet is connected, False if not.
        """
        pass


    @abstractmethod
    def get_downstream_side(self):
        """
        Return the process unit connected to the side outlet.
        """
        pass


    @abstractmethod
    def set_sidestream_flow(self, flow):
        """
        Define the flow rate for the sidestream.
        """
        pass


    @abstractmethod
    def sidestream_flow_defined(self):
        """
        Return whether the sidestream flow rate has been defined.
        """
        pass


    @abstractmethod
    def get_side_outflow(self):
        """
        Return the sidestream outlet flow rate.
        """
        pass


    @abstractmethod
    def get_side_outlet_concs(self):
        """
        Return a copy of the sidestream outlet concentrations.
        """
        pass


    @abstractmethod
    def set_flow(self, discharger, flow):
        """
        Specify the flow from the discharger.
        """
        pass


    @abstractmethod
    def _discharge_main_outlet(self):
        """
        Pass the flow and concentrations to the main outlet.
        """
        pass


    @abstractmethod
    def _discharge_side_outlet(self):
        """
        Pass the flow and concentrations to the side outlet.
        """
        pass


    @abstractmethod
    def discharge(self):
        """
        Pass the total flow and blended components to the downstreams.
        """
        pass


    @abstractmethod
    def get_TSS(self, branch='Main'):
        """
        Return the Total Suspended Solids of the specified branch.
        """
        pass


    @abstractmethod
    def get_VSS(self, branch='Main'):
        """
        Return the Volatile Suspended Solids of the specified branch.
        """
        pass


    @abstractmethod
    def get_COD(self, branch='Main'):
        """
        Return the Chemical Oxygen Demand (total) of the specified branch.
        """
        pass


    @abstractmethod
    def get_sCOD(self, branch='Main'):
        """
        Return the soluble COD of the specified branch.
        """
        pass


    @abstractmethod
    def get_pCOD(self, branch='Main'):
        """
        Return the particultate COD of the specified branch.
        """
        pass


    @abstractmethod
    def get_TN(self, branch='Main'):
        """
        Return the total nitrogen of the specified branch.
        """
        pass


    @abstractmethod
    def get_orgN(self, branch='Main'):
        """
        Return the organic nitrogen of the specified branch.
        """
        pass


    @abstractmethod
    def get_inorgN(self, branch='Main'):
        """
        Return the inorganic nitrogen of the specified branch.
        """
        pass


    @abstractmethod
    def get_pN(self, branch='Main'):
        """
        Return the particulate nitrogen of the specified branch.
        """
        pass


    @abstractmethod
    def get_sN(self, branch='Main'):
        """
        Return the soluble nitrogen of the specified branch.
        """
        pass


    @abstractmethod
    def _branch_flow_helper(self):
        """
        Calculate 1 of the 3 branches' flow based on the other 2.
        """
        pass


    @abstractmethod
    def _check_conc_cnvg(self, curr_comps, prev_comps, rel_lim):
        """
        Check the convergence of model components (concentrations).
        """
        pass

