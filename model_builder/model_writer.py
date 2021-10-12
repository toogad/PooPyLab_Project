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

def set_model_components(all_rows):
    """ Initialize lists for model components and their names."""

    _num_comps = len([cell for cell in all_rows[0] if cell != ''])
    _comp_vals = [0.0] * _num_comps  # this may be unnecessary
    _comps = []

    for i in range(_num_comps):
        _comps.append([_comp_vals[i], all_rows[1][i], all_rows[2][i], all_rows[3][i]])

    return _comps


def set_model_params(all_rows=[]):
    """ Initialize the model parameters. """
    _params = {}

    # first row of actual parameter list
    _frap = all_rows.index([_row for _row in all_rows if _row[0] == 'PARAMETERS'][0]) + 1
    for row in all_rows[_frap:]:
        _params[row[0]] = row[1:5]

    return _params


def set_model_stoichs(all_rows=[], num_comps=13):
    """ Initialize the stoichiometrics."""

    starting_row_index = 4

    # count the number of rate equations first
    row_counter = 0
    while (all_rows[row_counter][0] != 'END_ST'):
        row_counter += 1

    num_eqs = row_counter - starting_row_index


    # the _stoichs stores the stoichiometrics in the form of a 2-d array of text;
    # the 1st index of _stoichs is the id of the model component, starting at 0
    # and the 2nd index of _stoichs is the id of the rate equation, starting at 0
    _stoichs = []

    for comp_id in range(num_comps):
        _stoichs.append([0]*num_eqs)
        for eq_id in range(num_eqs):
            _stoichs[comp_id][eq_id] = all_rows[starting_row_index + eq_id][comp_id]

    return _stoichs, num_eqs


if __name__ == '__main__':

    import csv

    csv_rows = []

    with open("template_asm1.csv", 'r') as csvf:
        r = csv.reader(csvf)
        for row in r:
            csv_rows.append(row)
            print(row)
    csvf.close()

    print()

    model_comps = set_model_components(csv_rows)
    num_comps = len(model_comps)

    print('Found', num_comps, 'Model Components:')
    print(model_comps)

    model_params = set_model_params(csv_rows)
    print(model_params)

    model_stoichs, num_eqs = set_model_stoichs(csv_rows, num_comps)

    print('Found', num_eqs, 'Rate Equations')
    print(model_stoichs)



#    with open("model.csv", 'r') as csvf:
#        dr = csv.DictReader(csvf)
#        for row in dr:
#            print(row)
#    csvf.close()
#
#    with open("model.csv", 'r') as csvf:
#        dr = csv.DictReader(csvf)
#        for row in dr:
#            print(row.keys())
#            print(row.values())
#    csvf.close()
#
