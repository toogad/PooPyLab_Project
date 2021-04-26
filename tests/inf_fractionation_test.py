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
#    Testing the influent fractionation.
#

from PooPyLab.unit_procs.streams import influent
from PooPyLab.utils.run import input_inf_concs

if __name__ == "__main__":

    inf = influent()

    input_inf_concs('ASM1', inf)

    inf.set_mainstream_flow(37800/2.0)
    inf.set_fractions('ASM1', 'COD:BOD5', 1.0)
    inf.set_fractions('ASM1', 'SCOD:COD', 0.5)
    inf.set_fractions('ASM1', 'BSCOD:SCOD', 0.8)
    inf.set_fractions('ASM1', 'BPCOD:PCOD', 0.7)
    inf.set_fractions('ASM1', 'SON:SCOD', 0.025)
    inf.set_fractions('ASM1', 'BSON:SON', 0.80)
    inf.set_fractions('ASM1', 'BPON:PON', 0.75)

    inf.blend_inlet_comps()
    inf.discharge()
    print(inf.get_main_outlet_concs())

