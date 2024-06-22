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

from .model_builder_common import define_branch_arrays, assign_solver_array, collect_inlet_arrays
from .model_builder_common import substr_for_flow, substr_for_concs, generate_inlet_flow_weighted_avg


def select_model_template(unit):
    """ Select the model template for the unit

    Args:
        unit: the pipe unit under construction, {}
    Return:
        model template ['']
    """
    selected_model = []
    accept = False
    with open(unit['Model_File_Path'], 'rt') as tf:
        for line in tf:
            if unit['MO_Flow_Data_Source'] in line or accept == True:
                accept = True
            if accept == True and line[0]!='#' and line!="\n" and ('[' not in line) and (']' not in line):
                selected_model.append(line)
            elif selected_model and (unit['MO_Flow_Data_Source'] not in line) and ('[' in line and ']' in line):
                break
    return selected_model


def substitue_pipe_model(unit, selected_model, inlet_streams, start_eq_id):
    """ Construct a pipe model based on the selected template

    Args:
        unit: the pipe unit under construction, {}
        selected_model: ['']
        inlet_streams: list of inlet streams arrayname to "unit", ['']
        start_eq_id: starting equation id, int
    Return:
        C code statements as model equations for a pipe (str)
        updated eq_id (int)
    """

    pipe_model = ''
    eq_id = start_eq_id
    for line in selected_model:         # e.g. line = 'FLOW : 0 = MY_IN_FLOW - MY_MO_FLOW'
        splt = line.split(':')          #      splt = ['FLOW ', '0 = MY_IN_FLOW - MY_MO_FLOW']
        line = splt[1]                  #      line = '0 = MY_IN_FLOW - MY_MO_FLOW'
        rhs = line.split('=')[1]        #      rhs = 'MY_IN_FLOW - MY_MO_FLOW'
        model_terms = rhs.split('-')     #      flow_terms = ['MY_IN_FLOW ', ' MY_MO_FLOW']
        if splt[0].strip() == 'FLOW':
            for ft in model_terms:
                fts = ft.strip()
                line = line.replace(fts, substr_for_flow(unit, fts, inlet_streams))
            line = line.replace('ZERO','LHS[' + str(eq_id) + ']')
            pipe_model += line + '\n'
            eq_id += 1
        elif splt[0].strip() == 'CONC':
            if 'FWA' in line:
                line, eq_id = generate_inlet_flow_weighted_avg(unit, inlet_streams, eq_id)
            else:
                line, eq_id = substr_for_concs(unit, model_terms, eq_id)
            pipe_model += line + '\n'
    return pipe_model, eq_id


def compose_sys(pfd={}, tab=2):
    """ Compose the units' variable/array declarations and mass balance equations

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
    declars.append('sunindextype i;\n')

    nc = int(list(pfd['Flowsheet'].values())[0]['Num_Model_Components'])  # No. of model Components
    array_assign = assign_solver_array(array_names, nc)

    all_eqs = []
    id_eq = 0
    for c in pfd['Flowsheet'].values():
        inlet_streams = collect_inlet_arrays(pfd, c)
        if c['Type'] == 'Pipe' or c['Type'] == 'Splitter':
            selected_model = select_model_template(c)
            eqs, id_eq = substitue_pipe_model(c, selected_model, inlet_streams, id_eq)
            all_eqs.append(eqs)

    return declars, array_assign, all_eqs


def write_to_file(filename='syseqs.c', lines=[], write_mode='w'):
    with open(filename, write_mode) as eqf:
        for item in lines:
            eqf.write(item)
            eqf.write('\n')
    return None
