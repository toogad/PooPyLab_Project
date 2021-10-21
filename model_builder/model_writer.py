#!/usr/bin/python3

#   This file is part of PooPyLab.
#
#    PooPyLab is a simulation software for biological wastewater treatment processes using the International Water
#    Association Activated Sludge Models.
#
#    Copyright (C) Kai Zhang
#
#    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
#    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
#    later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along with this program. If not, see
#    <http://www.gnu.org/licenses/>.
#
#
#  Definition of the equation writing functions.
#

def get_model_components(all_rows):
    """ Initialize lists for model components and their names."""

    _num_comps = len([cell for cell in all_rows[0] if cell != ''])
    _comps = []

    for i in range(_num_comps):
        _comps.append([all_rows[1][i], all_rows[2][i], all_rows[3][i]])

    return _comps


def get_model_params(all_rows=[]):
    """ Initialize the model parameters. """
    _params = {}

    # first row of actual parameter list
    _frap = all_rows.index([_row for _row in all_rows if _row[0] == 'PARAMETERS'][0]) + 1
    for row in all_rows[_frap:]:
        _params[row[0]] = row[1:5]

    return _params


def get_model_stoichs(all_rows=[], num_comps=13):
    """ Initialize the stoichiometrics."""

    starting_row_index = 4

    # count the number of rate equations first
    row_counter = 0
    while (not(all_rows[row_counter][0] == 'END_STOICH' or all_rows[row_counter][0] == 'END_EQTNS')):
        # 'END_STOICH' is the same Stop sign as 'END_EQTNS' in the Peterson matrix format
        row_counter += 1

    num_eqs = row_counter - starting_row_index

    # _stoichs stores the stoichiometrics in the form of a 2-d array of text;
    # the 1st index of _stoichs is the id of the model component, starting at 0
    # and the 2nd index of _stoichs is the id of the rate equation, starting at 0
    _stoichs = []

    for comp_id in range(num_comps):
        _stoichs.append([0]*num_eqs)
        for eq_id in range(num_eqs):
            _stoichs[comp_id][eq_id] = all_rows[starting_row_index + eq_id][comp_id]

    return _stoichs, num_eqs


def get_rate_equations(all_rows=[], num_comps=13, num_eqtns=8):
    """ Extract the rate equation's individual terms """

    # The definition of rate equations starting at Row 3 (Row Index = 2), one (1) column down from the last model
    # component and its stoichiometric column: term type row and term unit row included
    eqs_start_row_index = 2

    # looks stupidly redundant, but for readability: convert to index
    eqs_start_col_index = (num_comps - 1) + 1

    # _rate_eqs stores the rate equations in the form of a 2-d array of text:
    # the 1st row defines the types of the individual terms in the rate equations at the corresponding index;
    # the 2nd row of _rate_eqs is the unit of the individual rate equation terms;
    _rate_eqs = []

    # all_rows[] indexing: added 2 due to the term type row and the term unit row
    for row in all_rows[eqs_start_row_index:(eqs_start_row_index + 2 + num_eqtns)]:
        _rate_eqs.append(row[eqs_start_col_index:])

    return _rate_eqs


def check_monod_term(term=''):
    """ check if the target term is in the form of a Monod or Inhibition term """

    if '/' in term:
        numerator, denominator = term.split('/')
    else:
        return False


    return


def create_model_class_init(model_name='User_Defined_Model', csv_file='template_asm1.csv', num_comps=13, num_eqs=8):
    """ create the file that store the model components, stoichiometry, and parameters/constants """

    from datetime import datetime

    _dt_stamp = datetime.now()

    _filename = model_name + '.py'

    _tab = ' ' * 4

    with open(_filename, 'w') as asmfile:
        asmwrite = asmfile.write

        asmwrite('#  This file defines the model named ' + model_name + '\n')
        asmwrite('#\n')
        asmwrite('#  Created Using:            PooPyLab Model Builder\n')
        asmwrite('#  User Specified Model in:  ' + csv_file + '\n')
        asmwrite('#  Created at:               ' + _dt_stamp.strftime("%H:%M:%S %Y-%B-%d") + '\n')
        asmwrite('#\n\n\n')

        asmwrite('from .asmbase import asm_model' + '\n'*3)

        asmwrite('class ' + model_name + '(asm_model):' + '\n')
        asmwrite(_tab + 'def __init__(self, ww_temp=20, DO=2):' + '\n')
        asmwrite(_tab*2 + '"""\n')
        asmwrite(_tab*2 + 'Args:\n')
        asmwrite(_tab*3 + 'ww_temp:    wastewater temperature, degC;\n')
        asmwrite(_tab*3 + 'DO:         dissoved oxygen, mg/L\n\n')
        asmwrite(_tab*2 + 'Return:\n')
        asmwrite(_tab*3 + 'None\n')
        asmwrite(_tab*2 + 'See:\n')
        asmwrite(_tab*3 + '_set_ideal_kinetics_20C();\n')
        asmwrite(_tab*3 + '_set_params();\n')
        asmwrite(_tab*3 + '_set_stoichs().\n')
        asmwrite(_tab*2 + '"""\n\n')

        asmwrite(_tab*2 + 'asm_model.__init__(self)' + '\n')
        asmwrite(_tab*2 + 'self.__class__.__id += 1' + '\n\n')

        asmwrite(_tab*2 + 'self._set_ideal_kinetics_20C_to_defaults()' + '\n\n')

        asmwrite(_tab*2 + '# wastewater temperature used in the model, degC' + '\n')
        asmwrite(_tab*2 + 'self._temperature = ww_temp' + '\n\n')

        asmwrite(_tab*2 + '# mixed liquor bulk dissolved oxygen, mg/L' + '\n')
        asmwrite(_tab*2 + 'self._bulk_DO = DO' + '\n\n')

        asmwrite(_tab*2 + "# temperature difference b/t what's used and baseline (20C), degC" + '\n')
        asmwrite(_tab*2 + 'self._delta_t = self._temperature - 20' + '\n\n')

        asmwrite(_tab*2 + 'self.update(ww_temp, DO)' + '\n\n')

        asmwrite(_tab*2 + '# ' + model_name + ' model components' + '\n')
        asmwrite(_tab*2 + 'self._comps = [0.0] * ' + str(num_comps) + '\n\n')

        asmwrite(_tab*2 + '# Intermediate results of rate expressions, M/L^3/T' + '\n')
        asmwrite(_tab*2 + '# The list is to help speed up the calculation by reducing redundant' + '\n')
        asmwrite(_tab*2 + '# calls of individual rate expressions in multiple mass balance equations' + '\n')
        asmwrite(_tab*2 + '# for the model components.' + '\n')
        asmwrite(_tab*2 + '# ' + model_name + ' has ' + str(num_eqs) + ' bio processes.' + '\n')
        asmwrite(_tab*2 + 'self._rate_res = [0.0] * ' + str(num_eqs) + '\n\n')

        #TODO: NEED TO HAVE THE MONOD TERMS PARSED FIRST
        # Intermediate results of Monod or Inhibition Terms
        #    self._monods = [1.0] * 7
        #TODO_END

        asmwrite(_tab*2 + 'return None' + '\n')

    asmfile.close()

    return None


if __name__ == '__main__':

    import csv

    csv_rows = []

    with open("template_asm1.csv", 'r') as csvf:
        r = csv.reader(csvf)
        for row in r:
            csv_rows.append(row)
    csvf.close()

    print()

    model_comps = get_model_components(csv_rows)
    num_comps = len(model_comps)

    print('Found', num_comps, 'Model Components:')
    print(model_comps)

    model_params = get_model_params(csv_rows)
    num_params = len(model_params)
    print('Found', num_params, 'Model Parameters/Constants:')
    print(model_params)

    model_stoichs, num_eqs = get_model_stoichs(csv_rows, num_comps)
    print(model_stoichs)

    print('Found', num_eqs, 'Rate Equations:')
    model_rate_eqs = get_rate_equations(csv_rows, num_comps, num_eqs)
    print(model_rate_eqs)

    create_model_class_init('KZTest', 'template_asm1.csv', num_comps, num_eqs)
