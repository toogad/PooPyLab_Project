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

from PooPyLab.unit_procs.streams import splitter, pipe, WAS
from PooPyLab.unit_procs.streams import influent, effluent
from PooPyLab.utils import pfd, run

if __name__ == "__main__":

    inf = influent()

    inf.set_fractions('ASM1', 'COD:BOD5', 3.0)
    inf.set_fractions('ASM1', 'SCOD:COD', 0.55)
    inf.set_fractions('ASM1', 'BSCOD:SCOD', 0.85)
    inf.set_fractions('ASM1', 'BPCOD:PCOD', 0.75)
    inf.set_fractions('ASM1', 'PORGN:VSS', 0.04)

    inf.get_main_outlet_concs()

