#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  lykosxrdp.py
#  
#  Copyright 2018 lykos users <lykos@linux-kknt>
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
# Geometria: TK, Jose de almeida lobinho 11,2018 22:00
# Conexao via rdesktop utilizando a geometria do monitor com a barra de ferramentas visivel  

import tkinter as tk
from tkinter import messagebox
import commands
import sys, os

os.system("clear")

root = tk.Tk()
root.withdraw()
sw = root.winfo_screenwidth()
sh =  ( root.winfo_screenheight() * 0.97 )
argumentos = sys.argv

parametros = ""
if argumentos and len( argumentos ) >=2:	parametros = argumentos[1]
else:	parametros = ""

abrir = commands.getstatusoutput("rdesktop -T Direto-Lykos -D -g"+str( sw )+"x"+str( sh ) +" "+ parametros)

if abrir[0] !=16128:
	messagebox.showinfo("Erro na abertura do rdesktop", "{ Utilize paramentros validos }\n\nExemplo:\n1 - Ex: 192.168.0.0 -k en-us\n\n2-No utlilize a geomatria o sistema ja detecta automaticamente\n\nPS: -k en-us, especifica o layout do teclado ex: -k pt-br"+(" "*200) )
