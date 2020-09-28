#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  apagar1.py
#  
#  Copyright 2019 lykos users <lykos@linux-mw9m>
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
# Jose de almeida lobinho
# Controle de cheques independentes [ 04-02-2019 Monfardini ]
import wx
import datetime

class GerenciadorCheques(wx.Frame):
    
	def __init__(self, parent,id):
		
		self.p = parent

		wx.Frame.__init__(self, parent, id, 'Gerênciador de nota fiscal de compras', size=(950,490), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
#		self.Bind(wx.EVT_CLOSE, self.sair)

#		self.gerenciaNfeCompras = NFeCompras(self.painel, 50 ,pos=(30,30), size=(922,350),
#							style=wx.LC_REPORT
#							|wx.LC_VIRTUAL
#							|wx.BORDER_SUNKEN
#							|wx.LC_HRULES
#							|wx.LC_VRULES
#							|wx.LC_SINGLE_SEL
#							)

#		self.gerenciaNfeCompras.SetBackgroundColour('#557E8C')
#		self.gerenciaNfeCompras.SetForegroundColour("#000000")
#		self.gerenciaNfeCompras.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
#		self.painel.Bind(wx.EVT_PAINT,self.desenho)
#		self.gerenciaNfeCompras.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
#		self.gerenciaNfeCompras.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.geracaoPdf)
    
