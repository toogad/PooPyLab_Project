# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
# 
# Copyright (C) Kai Zhang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Definition of the plant Effluent unit
# 
# Update Log: 
# Jul 30, 2017 KZ: Made it more pythonic.
# Mar 21, 2017 KZ: Migrated to Python3
# Sep 26, 2014 KZ: removed test code   
# July 2, 2014 KZ: change base class to Pipe.
# June 29, 2014 KZ: removed Convert() that converts model parameters for
#                   user parameters
# December 25, 2013 KZ: commented out the BlendComponent() function in
#                       ReceiveFrom()
# December 17, 2013 KZ: Added _PrevComp[0..12] to store state variables from 
#                       previous iteration
#
# December 07, 2013 Kai Zhang
    

import pipe

class effluent(pipe.pipe):
    __id = 0

    def __init__(self):
        pipe.pipe.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "Effluent_" + str(self.__id)
        self._main_outlet_connected = True  # dummy
        print(self.__name__, "initialized successfully.")

