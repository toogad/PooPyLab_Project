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
"""Definitions of specific data types used in the PooPyLab project.
"""
## @namespace datatypes
## @file datatype.py


from enum import Enum

# Flow Data Source
class flow_data_src(Enum):
    """
    Data type "flow_data_src" is an enumerate of four possible sources.

        TBD='ToBeDetermined'
        UPS='Upstream'
        DNS='Downstream'
        PRG='Program'
    
    This is mainly used to specify the controlling source of flow of a
    particular branch of a process unit. 

    TBD(ToBeDetermined):

        When a process unit is created, flow data sources for all branches
        are set to TBD. Some process units, such as influent/effluent, may
        have different initial flow data source settings since they are known.
        The user can specify flow data source while building the process flow
        diagram (PFD) by connecting process units and setting desired flow
        rates to specific branches (e.g. RAS flow).

    UPS(Upstream): 

        When set on the inlet of a process unit, the total inflow will be the
        sum of all the flows received from its upstream.

        When set on either the mainstream or sidestream outlet branch, the
        branch's flow rate will be the delta of total inflow and the third
        branch. The third branch's flow will then have to be specified by the
        user or downstream (DNS) during run time.

    DNS(Downstream):

        When set on the inlet of a process unit, the total inflow will be the
        sum of all the flows received from its upstream. As a result, either
        the user or runtime will have to provide the flow rates for the
        mainstream and sidestream outlet branches.

        When set on the mainstream/sidestream outlet branches, the flow rate
        data have to be provided by downstream processes. This scenario can be
        encountered in a final clarifier's sidestream outlet which is the
        underflow. This underflow feeds into a flow splitter inlet. The
        splitter's mainstream outlet branch is used as RAS stream whose flow
        rate is set by the user. The sidestream of the splitter is used as WAS
        whose flow rate is set by the overall treatment plant. As a result, the
        splitter's inlet flow as well as the final clarifier's underflow
        (sidestream outlet) both get their flow data from downstreams (DNS).

    PRG(Program):
        
        When the flow rate of a particular branch is to be set by the
        simulation program run time, PRG will be set to that branch. An example
        would be the WAS unit's flow rate which is calculated based on the
        design solids retention time, effluent total suspended solids, and
        solids inventory in all bioreactors.


    The main loop will analyze the process flow diagram before the simulation
    begins and set the flow Based upon the flow sources, a process unit
    maintains its flow balance during simulation by:

        1) total_inflow = mainstream_outflow + sidestream_outflow;
        2) mainstream_outflow = total_inflow - sidestream_outflow; or
        3) sidestream_outflow = total_inflow - mainstream_outflow.

    See Also:
        streams.splitter.set_flow_data_src()
    """

    TBD='ToBeDetermined'
    UPS='Upstream'
    DNS='Downstream'
    PRG='Program'
    
