#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pa.py
#  
#  Copyright 2016 lykos users <lykos@linux-714r.site>
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
#  
import os

__arquivo  = open("srv/aliquotas.csv","r").readlines()
al = "RJ"
iT = "BA"
ps = 0
print al

alor = ""
alds = ""
aliT = ""


for l in __arquivo:

	if l !="" and l.split(";")[1] == iT:
		ps=( int( l.split(";")[0] )+ 1)
		alds = l.split(";")[int(l.split(";")[0])+1]
		break
	

for i in __arquivo:
	
	if i !="" and i.split(";")[1] == al:
		
		alor = i.split(";")[int(i.split(";")[0])+1]
		aliT = i.split(";")[ps]
		break

print "Aliquota Origem.: ",alor
print "Aliquota Destino: ",alds
print "InterEstadual...: ",aliT

