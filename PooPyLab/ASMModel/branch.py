# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
#    
#    Copyright (C) 2014  Kai Zhang
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
# This is the definition of the SideStream unit which will be embedded in 
# objects like Splitter and Clarifier
# It is just a wrapper of the Influent class.

# Change Log:
#   2014.11.24 KZ: corrected initialization and naming of the branch 
#   2014.04.27 KZ: Initial commit

import influent

class Branch(influent.Influent):
    __id = 0
    def __init__(self):
        influent.Influent.__init__(self)
        self.__class__.__id += 1
        self.__name__ = 'Branch_' + str(self.__id)
        print self.__name__,' initialized successfully.'

