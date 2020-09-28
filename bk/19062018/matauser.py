#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  matauser.py
#  
#  Copyright 2017 lykos users <lykos@linux-4368>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  09-09-2017 Jose Lobinho RJ 19:47

import os
import sys
import commands

"""  Mata todos os processos do usuario selecionado  """
saida = commands.getstatusoutput("killall -9 -u  "+str( sys.argv[1]  ) )
print("Matando processo do usuario "+str( sys.argv[1] ), saida)
