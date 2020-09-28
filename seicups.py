#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  seicups.py
#  
#  Copyright 2017 lykos users <lykos@linux-714r.site>
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

import wx
import cups
import os
import commands
import datetime
from conectar import login,dialogos,diretorios,AbrirArquivos,MostrarHistorico,sbarra

alertas = dialogos()
sb      = sbarra()

class CupsSei(wx.Frame):

	def __init__(self, parent,id):

		self.conp = cups.Connection()
		self.a = "" #-: Pegar o nome da pasta de restauracao do cups
		
		wx.Frame.__init__(self, parent, id, u'Lista de Impressoras { CUPS }', size=(800,600), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,id,style=wx.BORDER_SUNKEN)

		self.lista_printers= wx.ListCtrl(self, -1,pos=(10,0), size=(788,198),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.lista_printers.SetBackgroundColour('#7F7F7F')
		self.lista_printers.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.lista_printers.InsertColumn(0, 'Impressora fila de impressão',  width=200)
		self.lista_printers.InsertColumn(1, 'Uri-Device', width=270)
		self.lista_printers.InsertColumn(2, 'Status do serviço', width=270)
		self.lista_printers.InsertColumn(3, 'Reação do cups', width=280)

		self.listar_jobs = wx.ListCtrl(self, -1,pos=(10,235), size=(788,157),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.listar_jobs.SetBackgroundColour('#6D7F91')
		self.listar_jobs.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.listar_jobs.InsertColumn(0, 'ID-Job',  width=100)
		self.listar_jobs.InsertColumn(1, 'Job-Uri { Endereço do job }',  width=800)

		self.numero_jobs = wx.StaticText(self,-1,"Numero de impressões presa na lista",     pos=(15,210))
		self.numero_jobs.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self,-1,"Conteudo do arquivo printers.conf", pos=(15,397)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.referenci = wx.TextCtrl(self,203,value="", pos=(10, 410), size=(788,180),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.referenci.SetBackgroundColour('#4D4D4D')
		self.referenci.SetForegroundColour('#17C317')
		self.referenci.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.resta = wx.BitmapButton(self,  95,  wx.Bitmap("imagens/finaliza16.png",wx.BITMAP_TYPE_ANY), pos=(260,200), size=(40,33))
		self.backu = wx.BitmapButton(self,  96,  wx.Bitmap("imagens/romaneio16.png",wx.BITMAP_TYPE_ANY), pos=(302,200), size=(40,33))
		self.saida = wx.BitmapButton(self,  97,  wx.Bitmap("imagens/volta16.png",   wx.BITMAP_TYPE_ANY), pos=(400,200), size=(40,33))
		self.impre = wx.BitmapButton(self,  98,  wx.Bitmap("imagens/cima20.png",    wx.BITMAP_TYPE_ANY), pos=(450,200), size=(40,33))
		self.jobss = wx.BitmapButton(self,  99,  wx.Bitmap("imagens/restaurar.png", wx.BITMAP_TYPE_ANY), pos=(500,200), size=(40,33))
		self.apaga = wx.BitmapButton(self, 100, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY),  pos=(710,200), size=(40,33))
		self.apall = wx.BitmapButton(self, 101, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY),  pos=(759,200), size=(40,33))

		self.maximizar = wx.BitmapButton(self, 404, wx.Bitmap("imagens/maximize32.png",  wx.BITMAP_TYPE_ANY), pos=(695,550), size=(40,33))
		self.finalizar = wx.BitmapButton(self, 405, wx.Bitmap("imagens/finaliza24.png",  wx.BITMAP_TYPE_ANY), pos=(743,550), size=(40,33))

		self.saida.Bind(wx.EVT_BUTTON, self.sair)
		self.impre.Bind(wx.EVT_BUTTON, self.levantarPrinters)
		self.jobss.Bind(wx.EVT_BUTTON, self.listaJobs)
		self.apaga.Bind(wx.EVT_BUTTON, self.apagarJobs)
		self.apall.Bind(wx.EVT_BUTTON, self.apagarJobs)
		self.backu.Bind(wx.EVT_BUTTON, self.backupPrintersConf)
		self.resta.Bind(wx.EVT_BUTTON, self.restaurarCupsConf )
		self.finalizar.Bind(wx.EVT_BUTTON, self.cupsRestart )
		self.maximizar.Bind(wx.EVT_BUTTON, self.maximizarHistorico )

		self.resta.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.backu.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.saida.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.impre.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.jobss.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.apaga.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.apall.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.maximizar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.finalizar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.resta.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.backu.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.saida.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.impre.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.jobss.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.apaga.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.apall.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.maximizar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.finalizar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.levantarPrinters( wx.EVT_BUTTON )


	def sair( self,event ):	self.Destroy()
	def backupPrintersConf(self,event):

		if login.usalogin.upper() == "LYKOS":
			
			hoje = datetime.datetime.now().strftime("%d%m%Y")
			if not os.path.exists(diretorios.pasHome+'relatorios/cups'):	os.makedirs(diretorios.pasHome+'relatorios/cups')
			if os.path.exists(diretorios.pasHome+'relatorios/cups') and os.path.exists('/etc/cups/printers.conf'):
				
				origem = "/etc/cups/printers.conf"
				destin = diretorios.pasHome+'relatorios/cups/printers_'+str( hoje )+'.conf'
				saida = commands.getstatusoutput("sudo cp -r "+str( origem )+" "+str( destin ))

				if not saida[0]:	alertas.dia( self, "Backup realizado com sucessso!!\n"+(" "*130),"Backup cups, printers.conf")
				else:	alertas.dia( self, "Erro no backup do arquivo printers.conf na relatorios/cups do lykos!!\n\n "+str( aa[1] )+"\n"+(" "*150),"Backup cups, printers.conf")
					
			else:	alertas.dia( self, "O arquivo printers.conf de cups ou a pasta relatorios/cups do lykos, não foi localizado!!\n "+(" "*150),"Backup cups, printers.conf")

		else:	alertas.dia( self, "Usuario incompativel p/o procedimento de backup!!\n "+(" "*120),"Backup cups, printers.conf")
		
	def restaurarCupsConf( self, event ):

		AbrirArquivos.pastas = diretorios.pasHome+'relatorios/cups/'
		AbrirArquivos.arquiv = "Arquivos CUPS (*.conf)|*.conf|"
			
		arq_frame=AbrirArquivos(parent=self,id=702)
		arq_frame.Centre()
		arq_frame.Show()

	def restartarCups( self ):

		saida1 = commands.getstatusoutput("sudo chmod 0444 "+str( self.a ))
		__arquivo = open( self.a, "r" ).read()
		self.referenci.SetValue( __arquivo )

		self.referenci.SetBackgroundColour('#4D4D4D')
		self.referenci.SetForegroundColour('#17C317')

		if "STOP-PRINTER" in __arquivo.upper():
			self.referenci.SetBackgroundColour("#CBB4B4")
			self.referenci.SetForegroundColour("#F7F7F7")
		

	def cupsRestart(self,event):
		
		destino = "/etc/cups/printers.conf"
		saida1 = commands.getstatusoutput("sudo cp -r "+str( self.a )+" "+str( destino ))
		saida2 = commands.getstatusoutput("sudo /etc/rc.d/cups restart")

		erro1 = "\n{ Erro na execução do procedimento }\n" if saida1[0] else "Procedimento realizado com sucesso!!"
		erro2 = "\n{ Erro na execução do procedimento }\n" if saida2[0] else "Procedimento realizado com sucesso!!"

		sai1 = "1 - copia printers.conf\n\n"+ str( saida1[1] )+str( erro1 ) if saida1[1] else "1 - copia printers.conf, "+str( erro1 )
		sai2 = "\n\n2 - restauração printers.conf, restart cups\n\n"+ str( saida2[1] )+"\n"+str( erro2 ) if saida2[1] else "\n\n2 - restauração printers.conf, restart cups, "+str( erro2 )

		if sai1 or sai2:	alertas.dia( self, "{ Saida do cups }\n\n"+str( sai1 )+str( sai2 )+"\n"+(" "*150),"Restauração e restart do cups")

	def maximizarHistorico( self, event ):

		MostrarHistorico.TP = ""
		MostrarHistorico.hs = str( self.referenci.GetValue() )
		MostrarHistorico.TT = "Conteudo do printers.conf"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = login.identifi

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
		
	def levantarPrinters( self, event ):

		self.lista_printers.DeleteAllItems()
		self.lista_printers.Refresh()

		printers = self.conp.getPrinters()
		indices  = 0

		for i in printers:

			self.lista_printers.InsertStringItem( indices, i )
			self.lista_printers.SetStringItem(indices,1, printers[i]['device-uri'])
			self.lista_printers.SetStringItem(indices,2, printers[i]['printer-state-message'])
			if str( printers[i]['printer-state-reasons'][0] ).upper() !="NONE":	self.lista_printers.SetStringItem(indices,3, printers[i]['printer-state-reasons'][0])
			
			indices +=1

		self.listaJobs( wx.EVT_BUTTON )
		
	def listaJobs(self,event):

		self.listar_jobs.DeleteAllItems()
		self.listar_jobs.Refresh()

		printers = self.conp.getPrinters()
		
		lista_jobs = self.conp.getJobs()
		self.numero_jobs.SetLabel( "Numero de impressões presa na lista: { "+str( len( lista_jobs ) )+" }")

		indices = 0
		if lista_jobs:

			for i in lista_jobs:
				
				self.listar_jobs.InsertStringItem( indices, str( i ) )
				self.listar_jobs.SetStringItem(indices,1, lista_jobs[i]["job-uri"])

				indices +=1

	def apagarJobs(self,event):

		if self.listar_jobs.GetItemCount():

			_id = self.listar_jobs.GetItem( self.listar_jobs.GetFocusedItem(), 0 ).GetText()
			
			_ap = "Apagar todas as impressões presa!!"
			if event.GetId() == 100:	_ap = "Apagar impressão presa com ID: { "+str( _id )+" }"
			if event.GetId() == 102:	_ap = "Restartar impressão com ID: { "+str( _id )+" }"
			__add = wx.MessageDialog(self, _ap + "\n\nConfirme p/Continuar\n"+(" "*120),"Apagar Item da Lista",wx.YES_NO)
			if __add.ShowModal() !=  wx.ID_YES:	return

			finalizado = True

			try:
				
				if event.GetId() == 100:	self.conp.cancelJob ( int( _id ), purge_job = True )
				if event.GetId() == 102:	self.conp.restartJob( int( _id ), job_hold_until='weekend' )
				
				if event.GetId() == 101:

					for i in range( self.listar_jobs.GetItemCount() ):

						_id = self.listar_jobs.GetItem( i, 0 ).GetText()
						self.conp.cancelJob ( int( _id ), purge_job = True )

				self.levantarPrinters( wx.EVT_BUTTON )

			except Exception as retorno:
				finalizado = False

			if not finalizado:	alertas.dia( self, "Cups error: "+str( retorno ),"Retorno cups")
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 95:	sb.mstatus("  Restaura printers.conf",0)
		elif event.GetId() == 96:	sb.mstatus("  Copia de segurança do printers.conf",0)
		elif event.GetId() == 97:	sb.mstatus("  Sair do gerenciador do cups",0)
		elif event.GetId() == 98:	sb.mstatus("  Lista impressoras cadastradas no cups",0)
		elif event.GetId() == 99:	sb.mstatus("  Lista de impressões { lista dos jobs de impressão do cups }",0)
		elif event.GetId() == 100:	sb.mstatus("  Apaga o job selecionado",0)
		elif event.GetId() == 101:	sb.mstatus("  Apaga todos os jobs da lista",0)
		elif event.GetId() == 404:	sb.mstatus(u"  Maximizar o conteudo do printers.conf",0)
		elif event.GetId() == 405:	sb.mstatus(u"  Restaurar o printers.conf e restartar o cups",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Gerenciador de impressao do cups",0)
		event.Skip()
					
	def desenho(self,event):

		dc = wx.PaintDC(self)
      
		dc.SetTextForeground("#3D78B2") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Informações do cups { Lista de impressoras e Jobs }", 0, 395, 90)
		dc.DrawRotatedText("Conteudo do printers.conf", 0, 590, 90)
