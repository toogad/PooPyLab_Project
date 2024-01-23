# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment processes using International Water Association
# Activated Sludge Models.
#
#    Copyright (C) Kai Zhang
#
#    PooPyLab is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
#    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
#    later version.
#
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along with PooPyLab. If not, see
#    <http://www.gnu.org/licenses/>.
#
#



""" Definitions of common interface for all PooPyLab objects.

The documentations for the abstract interface here are also abstract. Please see more details in specific
implementations.
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
    def set_name(self, new_name):
        pass


    @abstractmethod
    def get_name(self):
        pass


    @abstractmethod
    def get_codename(self):
        pass


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
    def get_upstream(self):
        pass


    @abstractmethod
    def inlet_connected(self):
        """
        Return True if upstream is connected, False if not.
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
    def sidestream_flow_defined(self):
        """
        Return whether the sidestream flow rate has been defined.
        """
        pass


    @abstractmethod
    def get_side_outlet_concs(self):
        """
        Return a copy of the sidestream outlet concentrations.
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
    def update_proj_conditions(self, ww_temp, elevation, salinity):
        """
        Set the project site conditions for the process unit.
        """
        pass


    @abstractmethod
    def get_saturated_DO(self):
        """
        Calculate the saturated DO concentration under the site conditions.
        """
        #TODO: not sure why this needs to be here for polymorphism
        pass


    @abstractmethod
    def get_config(self):
        """
        Save the configuration of the unit to a file.
        """
        pass
