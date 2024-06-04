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
#    This is the definition of the ASM1 model to be imported as part of the Reactor object
#
#

from .model_builder_common import define_branch_arrays, assign_solver_array
from .model_builder_common import collect_inlet_arrays
from .model_builder_common import generate_flow_totalizer, generate_flow_weighted_avg


def substitue_pipe_model(unit):
    selected_model = []
    accept = False
    with open(unit['Model_File_Path'], 'rt') as tf:
        for line in tf:
            if unit['MO_Flow_Data_Source'] in line or accept == True:
                accept = True
            if accept == True and line[0] != '#' and ('[' not in line) and (']' not in line):
                selected_model.append(line)
            elif selected_model and (unit['MO_Flow_Data_Source'] not in line) and ('[' in line and ']' in line):
                break
    return selected_model


def compose_sys(pfd={}, tab=2):
    """
    Compose the units' variable/array declarations and mass balance equations

    Args:
        pfd: dict storing the process flowsheet
        tab: size of a "tab"
    Return:
        declaration of the arrays
        equations of all the units in pfd
    """
    # declare the arrays as SUNDIALS realtype
    array_names = ['//Error in ' + unit['Codename'] + ' configs...' if define_branch_arrays(unit) == ''
                   else define_branch_arrays(unit) + ';'
                   for unit in pfd["Flowsheet"].values()]
    declars = ['sunrealtype ' + aname if aname[:2] != '//'
               else aname
               for aname in array_names]
    declars.append('sunindextype i;')

    nc = int(list(pfd['Flowsheet'].values())[0]['Num_Model_Components'])  # No. of model Components
    array_assign = assign_solver_array(array_names, nc)

    all_eqs = []
    id_eq = 0
    for c in pfd['Flowsheet'].values():
        print(c['Codename'])
        if c['Type'] == 'Pipe':
            inlet_streams = collect_inlet_arrays(pfd, c)
            inlet_flow_totalizer = generate_flow_totalizer(c, inlet_streams, id_eq)
            id_eq += 1
            all_eqs.append(inlet_flow_totalizer)
            all_eqs.append(generate_flow_weighted_avg(c, inlet_streams, id_eq))
            id_eq += int(c['Num_Model_Components']) - 1
            #TODO: double check the 'i=1' below: [0] is flow and handled by inlet_flow_totalizer
#            all_eqs.append('for (i=1; i<' + c['Num_Model_Components'] + '; i++){')
#            all_eqs.append(' ' * tab
#                            + 'LHS[' + str(id_eq) + '+i] = '
#                            + c['Codename'] + '_in_comp[i]'
#                            + ' - INF1_Influent_2_mo_comp[i];')
#            id_eq += int(c['Num_Model_Components'])
#            all_eqs.append('  LHS[' + str(id_eq) + '+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];')
#            id_eq += int(c['Num_Model_Components'])
#            all_eqs.append('}\n')

    return declars, array_assign, all_eqs


def write_to_file(filename='syseqs.c', lines=[], write_mode='w'):
    with open(filename, write_mode) as eqf:
        for item in lines:
            eqf.write(item)
            eqf.write('\n')
    return None
