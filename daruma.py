#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Jose de Almeida Lobinho
# 26-06-2015 12:30
# Daruma FrameWork p/NFCE 310

#from ctypes import cdll
import datetime
import commands
import time
import os
import re
import wx
import shutil
import xml.dom.minidom
import unicodedata
import zipfile
import subprocess

from wx.lib.buttons import GenBitmapTextButton
from conectar  import login,diretorios,dialogos,sqldb,cores,configuraistema,menssagem,numeracao,formasPagamentos,truncagem,MostrarHistorico,gerenciador,AbrirArquivos
from decimal   import *
#from prndireta import Termicas
from relatorio import sangrias
from danfepdf  import danfeGerar
from acbrnfs   import acbrNFCe,acbRetornos

psT  = diretorios()
cnS  = configuraistema()
mens = menssagem()
#dire = Termicas()
fpgT = formasPagamentos()
nF   = numeracao()
npdf = sangrias()
Trun = truncagem()

geraPDF = danfeGerar()
alertas = dialogos()

acbrNCe = acbrNFCe()

class darumaNfce310(wx.Frame):

	Filial = ""
	cdClie = ""
	nuDavs = ""
	TPEmis = 0
	dReceb = ""
	vincul = ""

	def __init__(self, parent,id):
		
		self.p = parent

		self.a = "" #-------: Arquivo de recuperacao
		self.d = "" #-------: Lista de dados do pedido
		self.c = "" #-------: Lista de dados do cliente
		self.i = "" #-------: Lista de dados dos items
		self.r = "" #-------: Lista c/Formas de Recebimento
		self.n = "" #-------: Lista do Gerenciador de NFs
		self.e = "" #-------: Dados de Procon, Informacoes promocionais e etc
		self.dcia = "" #----: Dados de nfce p/emissao da nfce
		self.acbr = "" #----: Dados de nfce p/emissao da nfce
		
		self.cOff = False #-: Contigencia OFF-Line
		self.r105 = False #-: NFCe em precessamento
		self.qrco = "" #----: QRCode p/Contigencia OFF-Line
		self.TpcT = "" #----: Tipo de contigencia
		
		self.mnd = "" #-: dados do  pedidos para meia nf
		self.mni = "" #-: dados dos items para meia nf

		self.nfe_windo = False #-: XML localizado na pasta windows

		"""   Pasta onde se emcontram os XMLs, Local,LocalTemporario, Windows   """
		self.pLocal = ""
		self.pTempo = ""
		self.pWindo = ""
		
		""" self.sw
			Servidor de WEB-SERVER
			1-Daruma Migrate
			2-PySped
			3-ACBrMonitro PLUS
			
		"""
		self.sw = ""
		self.ac = login.filialLT[ self.Filial ][38].split("|")[0].split(";")
		self.TM = "\n\nO Sistema Aguardara "+str( login.filialLT[ self.Filial ][38].split("|")[0].split(";")[14] )+" Segundos"

#-----// Definicao do recebimento em meia nota
		self.forma_pagamentos = []
		self.valor_pagamentos_saldos = Decimal("0.00")
		self.valor_pagamentos_cartao = Decimal("0.00")
#-----// Definicao do recebimento em meia nota //
		
		if len( self.ac ) >= 17 and self.ac[16] == "T":	self.TM = "\n\nAguardando Retorno da SEFAZ no Tempo do ACBr-PLUS\n\nAguarde..."

		if len( login.filialLT[ self.Filial ][35].split(";") ) >=24:	self.sw = login.filialLT[ self.Filial ][35].split(";")[23]

		"""    Informacoes do Adicionais da NFCe do Estado     """
		if os.path.exists(diretorios.aTualPsT+"/srv/nferodape.cnf") == True:
			
			ardp = open(diretorios.aTualPsT+"/srv/nferodape.cnf","r").read()
			for rd in ardp.split('\n'):
				
				self.e += str( unicodedata.normalize('NFKD', rd.strip().decode('utf-8')).encode('ascii', 'ignore') )+" "

		self.p.Enable( False )
		
		self.Finalizacao = False #----------: Finalizacao do Recebimento da NFCe
			
		"""   Dados da impressora de NFCe  modelo,colunas,porta, ip-porta COM   """
		self.modelo = self.coluna = self.nporta = self.ipport = self.pfilas = self.forcar = self.impres = ''
		
		if self.TPEmis == 2:	self.r = self.p.listaPagamento

		"""  obj de configuraca Framework  """
		_us = str( login.usalogin ).lower()
		_fl = str( self.Filial ).lower()
		self._pT = diretorios.nfcedrf+"/"+_fl+"/"+_us+"/libDarumaFramework.so"
		self._dU = diretorios.nfcedrf+"/"+_fl+"/"+_us+"/"
	
		
		wx.Frame.__init__(self, parent, id, str( self.Filial ) +' Emissão NFCe', size=(700,505), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		if self.sw=="3":	self.SetTitle( "Emissão NFCe { ACBrMonitor Plus }" )

		wx.StaticText(self.painel,-1,'Nº DAV',     pos=(20, 10)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Emissão',    pos=(180,10)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Vendedor',   pos=(340,10)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Impressora', pos=(500,10)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'CPF/CNPJ',   pos=(20, 50)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Descrição do Cliente', pos=(180,50)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		if self.sw == "3":	wx.StaticText(self.painel,-1,'Retorno SEFAZ-ACBrMonitor Plus', pos=(15,97)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,'Localização do XML p/envio de contigência\ne/ou recuperação do XML p/csTat 105/204/539', pos=(15,442)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		wx.StaticText(self.painel,-1,'Nº NFCe',  pos=(20, 320)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Nº Serie', pos=(115,320)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Nº Protocolo', pos=(180,320)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Emissão { SEFAZ }', pos=(415,320)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,'Nº DANFE { Chave NFCe }', pos=(20, 357)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Digest Value', pos=(415,357)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Reimpressão',  pos=(498,402)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.emis = wx.StaticText(self.painel,-1,'', pos=(547,277))
		self.emis.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.emis.SetForegroundColour('#D98181')

		self.mnfe = wx.StaticText(self.painel, -1, "", pos=(200,490))
		self.mnfe.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.mnfe.SetForegroundColour("#9C3636")


		self.Tamb = wx.StaticText(self.painel,-1,'Tipo de Ambiente', pos=(547,292))
		self.Tamb.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tamb.SetForegroundColour('#7F7F7F')

		self.Temp = wx.StaticText(self.painel,-1,'Tempo Envio-Emissão', pos=(539,97))
		self.Temp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Temp.SetForegroundColour('#2F572F')
		
		if self.TPEmis == 1:	self.emis.SetLabel("{ Emissão Posterior }")
		if self.TPEmis == 2:	self.emis.SetLabel("{ Emissão c/Recebimento }")
		if self.TPEmis == 1:	self.emis.SetForegroundColour('#C81E1E')
		if self.TPEmis == 2:	self.emis.SetForegroundColour('#0E5192')

		if self.sw=="3" and self.ac[7] == "1":	self.Tamb.SetLabel('{ Plus-Produção }')
		if self.sw=="3" and self.ac[7] == "2":	self.Tamb.SetLabel('{ Plus-Homologação }')
		
        
		self.info = wx.StaticText(self.painel,-1,'', pos=(18,278))
		self.info.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.info.SetForegroundColour('#DC6161')

		self.inf1 = wx.StaticText(self.painel,-1,'', pos=(18,293))
		self.inf1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.inf1.SetForegroundColour('#DC6161')

		self.insT = wx.StaticText(self.painel,-1,'', pos=(18,293))
		self.insT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.insT.SetForegroundColour('#1E5D9B')

		self.nnfc = wx.TextCtrl(self.painel,-1, '', pos=(15, 333), size=(90, 20) , style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.seri = wx.TextCtrl(self.painel,-1, '', pos=(110,333), size=(60, 20) , style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.npro = wx.TextCtrl(self.painel,-1, '', pos=(175,333), size=(230,20) , style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.ndta = wx.TextCtrl(self.painel,-1, '', pos=(410,333), size=(285,20) , style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.chav = wx.TextCtrl(self.painel,-1, '', pos=(15, 370), size=(390,20) , style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.dfvl = wx.TextCtrl(self.painel,-1, '', pos=(410,370), size=(285,20) , style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.emai = wx.TextCtrl(self.painel,-1, '', pos=(15, 403), size=(478,35) , style = wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.CB_READONLY)

		self.nnfc.SetBackgroundColour('#E5E5E5')
		self.seri.SetBackgroundColour('#E5E5E5')
		self.npro.SetBackgroundColour('#E5E5E5')
		self.ndta.SetBackgroundColour('#E5E5E5')
		self.chav.SetBackgroundColour('#E5E5E5')
		self.dfvl.SetBackgroundColour('#E5E5E5')
		self.emai.SetBackgroundColour('#89A0B7')
		self.emai.SetForegroundColour('#EBEBEB')
		
		self.nnfc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.seri.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.npro.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ndta.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.chav.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.dfvl.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.emai.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		simm,impressoras, user = fpgT.listaprn(2)

		self.nDav = wx.TextCtrl(self.painel,-1, '', pos=(15,  23), size=(150,20), style = wx.TE_READONLY)
		self.emis = wx.TextCtrl(self.painel,-1, '', pos=(175, 23), size=(150,20), style = wx.TE_READONLY)
		self.vend = wx.TextCtrl(self.painel,-1, '', pos=(335, 23), size=(150,20), style = wx.TE_READONLY)
		
		self.prin = wx.ComboBox(self.painel,-1, '', pos=(495, 23), size=(200,27), choices = impressoras, style=wx.NO_BORDER|wx.CB_READONLY)
		self.reim = wx.ComboBox(self.painel,-1, '', pos=(495,412), size=(200,25), choices = impressoras, style=wx.NO_BORDER|wx.CB_READONLY)
		
		self.docl = wx.TextCtrl(self.painel,-1, '', pos=(15, 63), size=(150,20))
		self.nmcl = wx.TextCtrl(self.painel,-1, '', pos=(175,63), size=(310,20))
		self.docl.SetBackgroundColour('#E5E5E5')
		self.nmcl.SetBackgroundColour('#E5E5E5')
		self.docl.SetForegroundColour('#21588D')
		self.nmcl.SetForegroundColour('#21588D')
		self.docl.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nmcl.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nDav.SetValue( str( self.nuDavs ) )

		self.reTsD = wx.TextCtrl(self.painel,-1,value='', pos=(17,115), size=(658,152),style = wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.CB_READONLY)
		self.reTsD.SetBackgroundColour('#4D4D4D')
		self.reTsD.SetForegroundColour('#F3F3F3')
		self.reTsD.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.volta = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/volta16.png",   wx.BITMAP_TYPE_ANY), pos=(495, 55), size=(30,26))				
		self.statu = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/status.png",    wx.BITMAP_TYPE_ANY), pos=(530, 52), size=(34,32))				
		self.envio = GenBitmapTextButton(self.painel,-1,label='   NFCe - Enviar',  pos=(570,56),size=(121,26), bitmap=wx.Bitmap("imagens/download16.png", wx.BITMAP_TYPE_ANY))
		self.envio.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.rc539 = wx.BitmapButton(self.painel, 206, wx.Bitmap("imagens/fire24.png",      wx.BITMAP_TYPE_ANY), pos=(590,156), size=(34,32))				
		self.fl539 = wx.BitmapButton(self.painel, 205, wx.Bitmap("imagens/previewc124.png", wx.BITMAP_TYPE_ANY), pos=(590,188), size=(34,32))				
		self.flini = wx.BitmapButton(self.painel, 204, wx.Bitmap("imagens/fileini32.png",   wx.BITMAP_TYPE_ANY), pos=(590,220), size=(34,32))				
		self.maxim = wx.BitmapButton(self.painel, 203, wx.Bitmap("imagens/maximize32.png",  wx.BITMAP_TYPE_ANY), pos=(625,124), size=(34,32))				
		self.vrxml = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/xml20.png",       wx.BITMAP_TYPE_ANY), pos=(625,156), size=(34,32))				
		self.avnfe = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/qrcode16.png",    wx.BITMAP_TYPE_ANY), pos=(625,188), size=(34,32))				
		self.avuls = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/pdf1.png",        wx.BITMAP_TYPE_ANY), pos=(625,220), size=(34,32))				
		self.rc539.Enable( False )
		self.fl539.Enable( False )


		self.xmLoc = wx.RadioButton(self.painel,-1,"Pasta Local", pos=(300,440), style=wx.RB_GROUP)
		self.xmlTm = wx.RadioButton(self.painel,-1,"Pasta Temporario", pos=(410,440))
		self.xmlWm = wx.RadioButton(self.painel,-1,"Pasta da Estação Windows", pos=(535,440))
		self.xmLoc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.xmlTm.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.xmlWm.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.xmLoc.Enable( False )
		self.xmlTm.Enable( False )
		self.xmlWm.Enable( False )

		self.cnTgn = wx.CheckBox(self.painel, -1,  "Emissão em contigência", pos=(15,470))
		self.cnTgn.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cnTgn.SetForegroundColour("#A52A2A")

		self.meian = wx.CheckBox(self.painel, -1,  "Orçamento vinculado { "+str( self.vincul )+" }", pos=(175,466))
		self.meian.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.meian.SetForegroundColour("#106986")

		self.consu = wx.CheckBox(self.painel, -1,  "Cliente marcado p/emitir como consumidor", pos=(410,466))
		self.consu.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.consu.SetForegroundColour("#106986")

		self.avnfe.Enable( False )
		self.avuls.Enable( False )

		self.volta.Bind(wx.EVT_BUTTON, self.sair)
		self.statu.Bind(wx.EVT_BUTTON, self.sTaTus)
		self.envio.Bind(wx.EVT_BUTTON, self.emissaoNFCe)
		self.avnfe.Bind(wx.EVT_BUTTON, self.pDiretas)
		self.avuls.Bind(wx.EVT_BUTTON, self.pDiretas)
		self.maxim.Bind(wx.EVT_BUTTON, self.maximizeSefaz)
		self.flini.Bind(wx.EVT_BUTTON, self.maximizeSefaz)
		self.vrxml.Bind(wx.EVT_BUTTON, self.maximizeSefaz)
		self.fl539.Bind(wx.EVT_BUTTON, self.abrirXml539Recuperacao)
		self.rc539.Bind(wx.EVT_BUTTON, self.abrirFirox)
		
		self.prin.Bind(wx.EVT_COMBOBOX, self.selImpressora)
		
		if self.sw == "":

			self.statu.Enable(False)
			self.envio.Enable(False)
			self.avnfe.Enable(False)
			self.avuls.Enable(False)
			self.reTsD.SetValue("Servidor de serviço p/NFCe, não foi definido...")
		
		if self.sw == "3":
				
			self.prin.Enable( False )
			self.reim.Enable( False )


		self.levantar(wx.EVT_BUTTON)
		self.calcularMeiaNf()

		"""   Emissao dinamica da nfce  """
		if self.TPEmis !=1 and self.p.emdinamica.GetValue() and not self.nnfc.GetValue():	self.emissaoNFCe(wx.EVT_BUTTON)
			

	def calcularMeiaNf(self):

		self.forma_pagamentos = []
		self.valor_pagamentos_saldos = Decimal("0.00")
		self.valor_pagamentos_cartao = Decimal("0.00")
		
		#-----//Emissao pos recebimento		
		if self.meian.GetValue():
			
			if   self.TPEmis == 1:
			
				"""  Totaliza cartao-credito + debito  """
				self.valor_pagamentos_cartao = ( self.d[59] + self.d[60] )

				if self.mnd and self.valor_pagamentos_cartao > self.mnd[37]:
					
					self.meian.SetValue( False )
					self.meian.Enable( False )
					self.mnfe.SetLabel("Valor superior")
					self.mnfe.SetForegroundColour("#9C3636")

				else:
					"""  Subtrai os cartoes de total da nota, o saldo fica como dinheiro  """
					if self.mnd[37] > self.valor_pagamentos_cartao:	self.valor_pagamentos_saldos = ( self.mnd[37] - self.valor_pagamentos_cartao )
					self.mnfe.SetLabel( 'Valor: '+format( self.mnd[37],',')+" Saldo dinheiro: "+format( self.valor_pagamentos_saldos,',' ) +" Saldo cartão: "+format( self.valor_pagamentos_cartao,',') )
					self.mnfe.SetForegroundColour("#256FB7")

				self.forma_pagamentos = [str( self.valor_pagamentos_saldos ),'0.00', '0.00',str(self.d[59]), str(self.d[60]), '0.00','0.00','0.00','0.00','0.00','0.00','0.00']


			#---------//Emissao com recebimento
			elif self.TPEmis == 2:
			
				"""  Totaliza cartao-credito + debito  """
				for pgC in range( self.p.listaPagamento.GetItemCount() ):

					if self.p.listaPagamento.GetItem( pgC, 2 ).GetText().split('-')[0] in ["04","05"]:
						
						self.forma_pagamentos.append(self.p.listaPagamento.GetItem( pgC, 2 ).GetText()+";"+self.p.listaPagamento.GetItem( pgC, 3 ).GetText())
						self.valor_pagamentos_cartao +=Decimal( self.p.listaPagamento.GetItem( pgC, 3 ).GetText().replace(",","") )

				if self.mnd and self.valor_pagamentos_cartao > self.mnd[37]:
					
					self.meian.SetValue( False )
					self.meian.Enable( False )
					self.mnfe.SetLabel("Valor superior")
					self.mnfe.SetForegroundColour("#9C3636")
			
				else:
					"""  Subtrai os cartoes de total da nota, o saldo fica como dinheiro  """
					if self.mnd[37] > self.valor_pagamentos_cartao:	self.valor_pagamentos_saldos = ( self.mnd[37] - self.valor_pagamentos_cartao )
					if self.valor_pagamentos_saldos > 0:	self.forma_pagamentos.append("01-Dinheiro;"+str( self.valor_pagamentos_saldos ) )
					self.mnfe.SetLabel( 'Valor: '+format( self.mnd[37],',')+" Saldo dinheiro: "+format( self.valor_pagamentos_saldos,',' ) +" Saldo cartão: "+format( self.valor_pagamentos_cartao,',') )
					self.mnfe.SetForegroundColour("#256FB7")

		
		
	def emitirVinculado(self,event):	self.levantar(wx.EVT_BUTTON)
		
	def sair(self,event):

		self.p.Enable( True )
		if self.TPEmis == 2 and self.Finalizacao == True:

			self.p.voltar(wx.EVT_BUTTON)
			self.p.ecfemi.Enable( True )
			
		else:	self.Destroy()


	def emissaoNFCe(self,event):

		conn = sqldb()
		sql  = conn.dbc("Caixa: Consulta de DAVs", fil =  self.Filial, janela = self )
		
		if sql[0] == True:

			#------------------// Dados da empresa p/emissao da nfce //
			if self.nuDavs and sql[2].execute("SELECT cr_urec,cr_nota,cr_chnf FROM cdavs WHERE cr_ndav='"+str( self.nuDavs )+"'"):
				
				recebido_caixa = sql[2].fetchall()[0]
				if recebido_caixa[0] and recebido_caixa[1] and recebido_caixa[2] and not self.cOff:

					alertas.dia(self,"DAV-Recebido, usuario: "+str( recebido_caixa[0] )+"NF: "+str( recebido_caixa[1] )+"\nChave: "+str( recebido_caixa[2] )+"\n"+(" "*100),"Verifica recebimento de davs") 
					self.envio.Enable( False )
					return

		if self.cOff or self.r105:
			
			nDav = self.nDav.GetValue().strip()
			nnfe = self.nnfc.GetValue().strip()
			nSer = str( int(self.seri.GetValue().strip()) )
			nChv = self.chav.GetValue().strip()
			emis = self.ndta.GetValue()
			demi = self.emis.GetValue().replace("-","/")

			if self.r105: #-: NFCe com retorno 105 nota fiscal em processamento { Ajuste da data p/ano,mes,dia }

				de1, de2 = demi.split(" ")
				demi = de1.split("/")[2]+"/"+de1.split("/")[1]+"/"+de1.split("/")[0]+" "+de2
				
			#-: Historico p/notas com retorno 105 em processamento
			reen = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
			dant = "Numero dav..: "+str( nDav )+\
				   "\nNumero NF...: "+str( nnfe )+\
				   "\nNumero Serio: "+str( nSer )+\
				   "\nNumero Chave: "+str( nChv )+\
				   "\nEmissao.....: "+str( emis )
			hisT = "NFCe emitida anteriormente e o sefaz nao liberou o xml\nficando a mesma com retorno { csTaT 105/204/539 } em processamento para liberação posterior\nReenvio p/"+str( reen )+"\n\n{ Dados anterior }\n"+str( dant )

			lsTa = nDav,nnfe,nSer,nChv,self.qrco,emis
			lisT = demi,nChv,nnfe,nSer,nDav,hisT, "" if not self.n else self.n[39]

		if self.sw == "3" and self.cOff == False and self.r105 == False:
			
			if self.meian.GetValue():
				
				self.d = self.mnd
				self.i = self.mni

			self.envio.Enable( False )
			acbrNCe.acbrNFCeEmissao( self )
			
			
		if self.sw == "3":

			if self.cOff or self.r105:
				
				pasTap = "1",self.pWindo,self.pWindo
				
				if self.xmLoc.GetValue() == True:	pasTap = "2",self.pLocal,self.pWindo
				if self.xmlTm.GetValue() == True:	pasTap = "3",self.pTempo,self.pWindo

				self.envio.Enable( False )
				if self.cOff:	acbrNCe.enviaConTigencia( self, lsTa, pasTap ) #--------------------------------------------------------------------------: Enviar p/contigencia 
				if self.r105 and acbrNCe.acbrNFCeConsulta( self, self.Filial, lisT, self.pTempo, nChv, rtn105 = True, localizado = self.nfe_windo ): #----: Enviar p/recuperacao do xml no sefaz da nfce retorno 105

					self.p.voltar(wx.EVT_BUTTON)

				

	def impressoraPadrao(self,event):

		simm,impressoras, user = fpgT.listaprn(1)
		padr = ""
		
		if simm == True:
			
			for p in impressoras:
				
				if p[0] == login.usuanfce:

					padr = p[0]+'-'+p[1]
					self.pfilas = p[2]
					self.forcar = p[7]
					self.modelo = p[8]
					self.coluna = p[9]
					self.nporta = p[10]
					self.ipport = p[11]


		if padr !='':	self.prin.SetValue( padr )


	def selImpressora(self, event):

		simm,impressoras,user = fpgT.listaprn(1)
		if simm == True and self.prin.GetValue() !='':
			
			for p in impressoras:
				
				if p[0] == self.prin.GetValue().split("-")[0]:

					self.pfilas = p[2]
					self.forcar = p[7]
					self.modelo = p[8]
					self.coluna = p[9]
					self.nporta = p[10]
					self.ipport = p[11]

			self.GravarPrinter(wx.EVT_BUTTON)
			self.AjusteInicias()

			
	def pDiretas(self,event):
		
		if self.n == "":	alertas.dia(self,"Dav não localizado em controle de NFs...\n"+(' '*100),"Gerar pdf da nfce")
		else:


			if self.sw == "3" and event.GetId() == 200:
				
				lisT = self.ndta.GetValue(),self.chav.GetValue(),self.emis.GetValue()
				acbrNCe.acbrRePrinTer( self, self.d[54], lisT )

			elif event.GetId() == 201:

				di = df = datetime.datetime.now().strftime("%d/%m/%Y")
				npdf.ContaCorrente( di, df, self, Filial = self.Filial, Tp="2", iTems = self.i, Davs = self.d, ClienTe = self.c, nfes = self.n, conTigencia = self.TpcT )

		
	def sTaTus(self,event):


		"""  ACBrMonitor Plus  """
		if self.sw == "3":	acbrNCe.acbrNFCeStatus( self )

			
		
	def levantar(self,event):

		self.emai.SetValue( "Informações da NFe-NFCe" )
		self.info.SetLabel("")
		self.inf1.SetLabel("")
		_historico = ""
		

		self.insT.SetLabel("")
		rcbd = False,""
		cTgc = False
		c105 = False #-: NFce com retorno 105-Nota em processamento
		conn = sqldb()
		sql  = conn.dbc("Caixa: Consulta de DAVs", fil =  self.Filial, janela = self )
		
		if sql[0] == True:

			#------------------// Dados da empresa p/emissao da nfce //
			if sql[2].execute("SELECT ep_dnfe,ep_acbr FROM cia WHERE ep_inde='"+str( self.Filial )+"'"):
				
				saidaconfiguracao = sql[2].fetchone()

				self.dcia = "" if not saidaconfiguracao[0] else saidaconfiguracao[0].split(";")
				self.acbr = "" if not saidaconfiguracao[1] else saidaconfiguracao[1].split(";")
				
				if self.sw=="3" and self.acbr and self.acbr[7] == "1":	self.Tamb.SetLabel('{ 1-Plus-Produção }')
				if self.sw=="3" and self.acbr and self.acbr[7] == "2":	self.Tamb.SetLabel('{ 2-Plus-Homologação }')

				if self.acbr:	
					_historico = "\n\nAmbiente: "+ self.Tamb.GetLabel() +"\n"+\
									u"  Versão: "+ self.acbr[6] +"\n"+\
									"   Serie: "+ self.acbr[5]

			if self.nuDavs !="" and sql[2].execute("SELECT * FROM cdavs WHERE cr_ndav='"+str( self.nuDavs )+"'") !=0:
		
				"""    Bloqueio da Emissao se Ja Tiver Emitido    """
				self.d  = sql[2].fetchall()[0]

				"""    Atualiza campos   """
				self.nnfc.SetValue( str( self.d[8] ) )
				self.seri.SetValue( str( self.d[101] ) )
				self.chav.SetValue( str( self.d[73] ) )

				if self.d[10] and self.d[8] and self.d[73]:	rcbd = True, self.d[10]+"\nNF: "+str( self.d[8] )+"\nCahve: "+str( self.d[73 ] ) #-: Verifica se o dav ja foi recebido

				if self.d[15] !="" and len( self.d[15].split(" ") ) == 4:
					
					self.npro.SetValue( self.d[15].split(" ")[2] )
					self.ndta.SetValue( self.d[15].split(" ")[0]+" "+self.d[15].split(" ")[1] )

				if self.TPEmis == 1:

					if self.d[74] == "1" and self.d[15] == "":	self.envio.Enable( True )
					else:	self.envio.Enable( True if self.cOff else False  )
			
				if self.nuDavs !="" and sql[2].execute("SELECT * FROM idavs WHERE it_ndav='"+str( self.nuDavs )+"'") !=0:	self.i = sql[2].fetchall()
				if self.cdClie !="" and sql[2].execute("SELECT * FROM clientes WHERE cl_codigo='"+str( self.cdClie )+"'") !=0:	self.c = sql[2].fetchall()[0]
				if sql[2].execute("SELECT us_pnfc FROM usuario WHERE us_logi='"+str( login.usalogin )+"'") !=0:	login.usuanfce = sql[2].fetchall()[0][0]

				#-------------//  Dados para emissao da meia nota, orcamento vinculado p/impressao com meianota
				self.mnd = "" if self.vincul and not sql[2].execute("SELECT * FROM cdavs WHERE cr_ndav='"+str( self.vincul )+"'") else sql[2].fetchall()[0] if self.vincul else ""
				self.mni = "" if self.vincul and not sql[2].execute("SELECT * FROM idavs WHERE it_ndav='"+str( self.vincul )+"'") else sql[2].fetchall() if self.vincul else ""
				
				
				if not self.mnd or not self.mni:
					
					self.meian.SetValue( False )
					self.meian.Enable( False )
					
				if self.vincul and self.mnd and self.mni:	self.meian.SetValue( True )
				if self.c and self.c[50] !=None and self.c[50] and len( self.c[50].split(";") ) >=3 and self.c[50].split(";")[2] == "T":	self.consu.SetValue( True )
				if not self.c:
					
					self.consu.Enable( False )
					self.consu.SetValue( False )

				#-------------//  Dados para emissao da meia nota, orcamento vinculado p/impressao com meianota //
				if self.nuDavs !="" and self.d[8].strip() !="" and sql[2].execute("SELECT * FROM nfes  WHERE nf_numdav='"+str( self.nuDavs )+"' and nf_nnotaf='"+str( self.d[8].strip() )+"'") !=0:	self.n = sql[2].fetchall()[0]

				if self.c == "" and self.d !="":
					
					self.docl.SetValue( self.d[3] )
					self.nmcl.SetValue( self.d[4] )

				if self.c != "":	
					self.docl.SetValue( self.c[3] )
					self.nmcl.SetValue( self.c[1] )

				if self.d !="":
					
					self.emis.SetValue( str( self.d[11] ) +' '+ str( self.d[12] ) )
					self.vend.SetValue( self.d[9] )

				"""   Operação c/Frete   """
				if self.d[23] !=0:	
					
					self.info.SetLabel( "Operação com Frete, Utilize a Emissão de NFe" )
					self.info.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

					self.envio.Enable( False )
					
					
			if self.d == "":

				self.envio.Enable( False )
				self.insT.SetLabel("DAV,Vazio, não localizado!!")

			if self.d != "" and self.i == "":

				self.envio.Enable( False )
				self.insT.SetLabel("DAV,não localizado em items!!")
		
			conn.cls(sql[1])

		lgr = ""
		if self.vallogradouro( self.c )[0] == False:

			self.docl.SetBackgroundColour('#A52A2A')
			self.nmcl.SetBackgroundColour('#A52A2A')
			
			self.docl.SetForegroundColour('#F5F1F1')
			self.nmcl.SetForegroundColour('#F5F1F1')
			
			lgr = "\n{ Dados de Endereço incompletos [ "+str( self.vallogradouro( self.c )[1] )+" ] }" 

		"""   Verifica a existencia de Emissao de NFe, NFCe   """
		if self.d !="":
			
			if self.d[8] !="" or self.d[15] !="" or self.d[73] !="":

				nNf = Ser = nPr = emi = cha = Tip = dfV = ""

				if self.d[8]  !='':	nNf = self.d[8]
				if self.d[15] !='':	emi = self.d[15].split(" ")[0]+" "+self.d[15].split(" ")[1]
				if self.d[15] !='':	nPr = self.d[15].split(" ")[2]
				if self.d[73] !='':	cha = self.d[73]
				if self.d[73] !='':	Tip = self.d[73][20:22] #---: Modelo 55-NFe, 65-NFCe
				if self.d[73] !='':	Ser = self.d[73][22:25] #---: Numero de Serie
				if self.n !='':	dfV = self.n[35] #--------------: DigestValue

				self.nnfc.SetValue( nNf ) #-: Numero NFCe
				self.seri.SetValue( Ser ) #-: Numero da Serie
				self.npro.SetValue( nPr ) #-: Numero do Protocolo
				self.ndta.SetValue( emi ) #-: Data Emissao
				self.chav.SetValue( cha ) #-: Numero da DANFE CHAVE
				self.dfvl.SetValue( dfV ) #--: Digest Value

				if nPr !='' and cha !='':
					
					self.avnfe.Enable( True )
					self.avuls.Enable( True )


				if Tip !='':
					
					Tne = "NFCe - Modelo: "+str( Tip )
					if Tip == "55":

						Tne = "NFe - Modelo: "+str( Tip )
						self.envio.Enable( False )
						self.avuls.Enable( False )

				else:	Tne = "Provavelmente em modo de inutilização!!"
				
				if self.n !="" and cha !="" and self.n[37] == '1':

					hST = self.reTsD.GetValue()
					self.avnfe.Enable( True )
					self.avuls.Enable( True )
					self.TpcT = "1"

					if nPr == "":	self.envio.Enable( True )
					if Tip !='':

						Tne = "{ Emitida em contigência Off-Line }  NFCe - Modelo: "+str( Tip )
						self.envio.Enable( True )
					
					self.cnTgn.Enable( False )
					self.qrco= self.n[32]
					self.cOff= cTgc = True
					
				self.emai.SetValue( Tne )
				self.emai.SetBackgroundColour("#1A1A1A")
				self.emai.SetForegroundColour("#FF0000")
				self.emai.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
		"""  Nota fiscal com retorno 105/24-em processamento-Duplicidade  """
		if self.n and self.n[39] in ["105","204","539"]:

			if self.n[25].isdigit() and len( self.n[25] ) == 44:	

				self.info.SetLabel("DAV com emissão de NFCe com CSTAT 105/204/539 >-->Nota fiscal em processamento\nChave: "+self.n[25] )
				self.nnfc.SetValue( self.n[26] )
				self.chav.SetValue( self.n[25] )
				self.seri.SetValue( self.n[33] )
				c105 = True
				self.r105 = True

			
		self.verCertificado( cTgc )

		"""
			Verifica se estar em inutilizacao e se e NFCe
		"""		
		
		if self.n !="" and self.n[1] == "1" and self.n[3] == "2":

			self.envio.Enable( False )
			rTT = self.reTsD.GetValue()
			
			rTs = "{ NFe em processo de inutilização }\n\nInutilize a NFe antes de emitir uma NFCe"
			self.reTsD.SetValue( str( rTT )+"\n\n"+str( rTs ) )
			self.reTsD.SetForegroundColour('#E71818')

	
		"""   Localizacao do xml p/envio da contigencia   """
		if cTgc or c105:

			_menssag = mens.showmsg( "{ ACBrPlus - Verificando a existencia do XML }\n\nAguarde..." )

			acbRT = acbRetornos()
			chave = self.chav.GetValue().strip()+"-nfe.xml"
			
			chTem = "nfce_"+str( self.nnfc.GetValue().strip() )+'-65-'+str( int( self.seri.GetValue().strip() ) )+".xml"

			pasTa,Tmpas, pCan = acbRT.acbrCriaPasTa( self.Filial, True, str( self.emis.GetValue() ) )

			achDF = os.path.exists( pasTa+chave )
			achTM = os.path.exists( Tmpas+chTem )

			achWM = acbRT.acbrLocalizarWindows( self, self.Filial, "c:\\ACBrMonitorPlus\\Logs\\"+str( chave ))

			self.pLocal = pasTa+chave
			self.pTempo = Tmpas+chTem
			self.pWindo = "c:\\ACBrMonitorPlus\\Logs\\"+str( chave )

			self.nfe_windo = achWM #-: Localizado na pasta windows

			if c105 and achTM:

				origem  = Tmpas+chTem
				destino = pasTa+chave
				rT = shutil.copyfile( origem, destino )
				achDF = os.path.exists( pasTa+chave )

			if c105 and achDF:
				 
				self.emai.SetValue( "cStat 105/204/539-NFCe em processamento { XML Localizado }, download do xml\nChave: "+str( self.n[25] ) )
				self.emai.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				
				
			if achDF:	self.xmLoc.Enable( True )
			if achTM:	self.xmlTm.Enable( True )
			if achWM:	self.xmlWm.Enable( True )

			if achWM == True:	self.xmlWm.SetValue( True )
			if achWM != True and achDF == True:	self.xmLoc.SetValue( True )
			if achWM != True and achDF != True and achTM == True:	self.xmlTm.SetValue( True )

			if c105 and achDF and achTM:	self.xmlTm.Enable( False )
			if self.n and self.n[39] == "539":

				self.fl539.Enable( True ) #-: Habilita para procurar o xml, da nfce ja emitida p/recupara para o sistema
				self.rc539.Enable( True ) #-: Abri o firefox para recuperacao do xml

			_DF = _TM = _WM = "Não Loclizado"
			if achDF == True:	_DF = "Localizado"
			if achTM == True:	_TM = "Localizado"
			if achWM == True:	_WM = "Localizado"

			if achDF != True and achTM != True and achWM != True:	hs = self.reTsD.GetValue() + "\n{ XML NÃO LOCALIZADO !!! }"
			else:	hs = self.reTsD.GetValue() + "\n{ XML }  Local: "+_DF+"  Temporario: "+_TM+"  Windows: "+_WM
			self.reTsD.SetValue( hs )

			if c105 and not achDF:	self.reTsD.SetBackgroundColour("#B18C8C")	
			del _menssag

		if _historico:	self.reTsD.SetValue( self.reTsD.GetValue() + _historico )


		if rcbd[0]:
			
			self.reTsD.SetValue( "{ DAV-Recebido }\n\nUsuario: "+str( rcbd[1] ) )
			if not self.cOff:	self.envio.Enable( False )


	def abrirFirox(self,event):

		try:
			
			pagina = "file:///home/"+str( diretorios.usAtual ) if len( self.ac ) < 18 or not self.ac[17].strip() else self.ac[17]
			p = subprocess.Popen(['firefox',pagina],)
		
		except Exception as erro:
			alertas.dia( self,"{ Erro na abertura do firefox }\n\n"+str( erro )+"\n"+(" "*130),"Erro na abertura do firefox")

			
	def abrirXml539Recuperacao(self,event):

		AbrirArquivos.pastas = "/home/"+str( diretorios.usAtual )
		AbrirArquivos.arquiv = "All Files (*.*)|*.*|"
			
		arq_frame=AbrirArquivos(parent=self,id=700)
		arq_frame.Centre()
		arq_frame.Show()


	def aberturaTemporario( self ):

		if self.a and len( self.a.split('.') ) >= 2 and self.a.split('.')[1].upper() == "ZIP":

			alertas.dia( self,"O arquivo selecionado estar compactado, o sistema vai descompactar\ne copiar para pasta local!!\n"+(" "*120),"Recuperação do xml p/rejeição 539")
			pasta_atual  = "/"
			nome_arquivo = self.a.split("/")[ ( len( self.a.split("/") ) - 1 ) ].split('.')[0]+".xml"

			for i in range( len( self.a.split("/") ) - 1 ):

				if i:

					pasta_atual +=self.a.split("/")[i]+"/"

			"""  extrai arquivo zipado  """
			with zipfile.ZipFile( self.a, "r") as z:
				z.extractall( pasta_atual )

			self.recuperacaoXml539( pasta_atual + nome_arquivo )

		elif self.a and len( self.a.split('.') ) >= 2 and self.a.split('.')[1].upper() == "XML":	self.recuperacaoXml539( self.a )
		else:	alertas.dia(self,"O arquivo selecionado não e um arquivo xml ou zip...\n"+(" "*120),"Recuperação do xml p/rejeição 539")
		

	def recuperacaoXml539(self, arquivo_recuperar ):

		numero_chave_arquivo = ""
		acbr_criapastas = acbRetornos()

		"""  uso de expressoes regulares p/achar a chave no arquivo  """
		pasTa,Tmpas, pCan = acbr_criapastas.acbrCriaPasTa( self.Filial, True, str( self.emis.GetValue() ) )
		if arquivo_recuperar and len( re.search ("\d{44}" , arquivo_recuperar ).group() ) == 44:	numero_chave_arquivo = re.search ("\d{44}" , arquivo_recuperar ).group()

		chaves_iguais = True if numero_chave_arquivo.strip() and str( self.chav.GetValue().strip() ) and numero_chave_arquivo.strip() == str( self.chav.GetValue().strip() ) else False
		arquiv_locali = os.path.exists( arquivo_recuperar )


		if chaves_iguais and arquiv_locali:
	
			origem  = arquivo_recuperar
			destino = pasTa+numero_chave_arquivo+"-nfe.xml"

			copia_arquivo = shutil.copyfile( origem, destino )
			copia_verific = os.path.exists( destino )

			if copia_verific:

				self.xmLoc.Enable( True )
				self.xmlTm.Enable( False )
				self.xmlWm.Enable( False )				

				self.xmLoc.SetValue( True )
				self.xmlTm.SetValue( False )
				self.xmlWm.SetValue( False )				

				alertas.dia(self,"Arquivo de recuperação xml, ja foi atualizado na pasta pasta local...\n\n[ Click em NFCe - Enviar p/recuperação do xml pelo sistema ]\n"+(" "*140),"Recuperação do xml p/rejeição 539")


			else:	alertas.dia(self,"Arquivo de recuperação xml, não foi localizado na pasta local...\n"+(" "*100),"Recuperação do xml p/rejeição 539")

		else:

			alr = "Dados incompletos para recuperação do xml"+\
				  "\n\n[ Chave p/Recuperação ]\n"+str( self.chav.GetValue() )+\
				  "\n\n[ Chave do arquivo xml ]\n"+str( numero_chave_arquivo )+\
				  "\n\n[ Arquivo de recupera localizado ]\n"+str( arquiv_locali )+",  "+str( arquivo_recuperar )

			alertas.dia( self, alr+(" "*110),"Recuperação do xml p/rejeição 539")
			
		
	def maximizeSefaz(self,event):


		ddm = ddf = cha = ""
		
		if self.ndta.GetValue() !="":

			sdT = self.ndta.GetValue().split(' ')[0].split('-')
			ddm = str( sdT[1] )+str( sdT[0] )
			ddf = str( sdT[2] )+str( sdT[1] )+str( sdT[0] )
		
 		nfc = self.nnfc.GetValue().strip()
		if self.seri.GetValue() !="":	ser = str( int( self.seri.GetValue().strip() ) )
		else:	ser = ""

		arquivox = diretorios.nfceacb+self.Filial.lower()+"/"+ddm+"/tmp/"+ddf+"/nfce_"+str( nfc )+"-65-"+str( ser )+"_"+login.usalogin.lower()+".xml"
		arquivoi = diretorios.nfceacb+self.Filial.lower()+"/"+ddm+"/tmp/"+ddf+"/nfce_"+str( nfc )+"-65-"+str( ser )+"_"+login.usalogin.lower()+".ini"
		arquivoc = diretorios.nfceacb+self.Filial.lower()+"/"+ddm+"/danfe/"+ddf+"/"+( self.chav.GetValue().strip() )+"-nfe.xml"

		if self.chav.GetValue() !="" and os.path.exists( arquivoc ) == True:	arquivox = arquivoc
		

		MostrarHistorico.hs = self.reTsD.GetValue()
		arquivoxi = ""
		if event.GetId() == 202 and os.path.exists( arquivox ) == True:	arquivoxi = arquivox
		if event.GetId() == 204 and os.path.exists( arquivoi ) == True:	arquivoxi = arquivoi

		if arquivoxi !="" and self.sw == "3":
			
			gerenciador.Anexar = arquivoxi

			gerenciador.secund = '' 
			gerenciador.emails = ''
			gerenciador.TIPORL = ''
			gerenciador.imprimir = True
			gerenciador.Filial  = self.Filial
				
			ger_frame=gerenciador(parent=self,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

		
		if event.GetId() == 203:
								
			MostrarHistorico.TP = "Retorno NFCe"
			MostrarHistorico.TT = "Retorno de Emissão de NFCe"
								
			MostrarHistorico.AQ = ''
			MostrarHistorico.FL = self.Filial

			his_frame=MostrarHistorico(parent=self,id=-1)
			his_frame.Centre()
			his_frame.Show()

	

	def verCertificado(self,conTigencia):


		_ms = ""

		"""   Verifica Validade do Certificado  """
		_mensagem = mens.showmsg("Verificando Certificado\n\nAguarde...")

		al = login.filialLT[ self.Filial ][30].split(";")
		r  = login.filialLT[ self.Filial ][38].split("|")[0].split(";")
		
		arqCert  = diretorios.esCerti+al[6]
		senCert  = al[5]

		"""   ACBrMonitorPlus   """
		if self.sw == "3":

			arqCert = diretorios.esCerti+str( r[3] ) #-: nome do certificado
			senCert = str( r[4] ) #--------------------: senha do certificado

	
		if al[6] !="":	cerSer = cnS.validadeCertificado( arqCert, senCert )
		else:	cerSer = [False]
		
		if cerSer[0] == False:	self.envio.Enable( False )

		del _mensagem

		if cerSer[0] == False:
			
			self.reTsD.SetValue("Sem Informações do certificado" )
			self.reTsD.SetBackgroundColour('#DFCECE')
			self.reTsD.SetForegroundColour('#C41212')
			
		if cerSer[0] != False:
			
			if conTigencia == True:

				self.reTsD.SetValue( cerSer[2]+"\n\nEmitida em contigência Off-Line" )
				self.reTsD.SetBackgroundColour('#DFCECE')
				self.reTsD.SetForegroundColour('#C41212')

			else:
				
				self.reTsD.SetValue( cerSer[2] )
				self.reTsD.SetForegroundColour('#F3F3F3')
		


	def vallogradouro(self, c ):

		_lgr = _nro = _bai = _cmu = _mun = _ufd = _cep = ""
		if self.c !="":

			_lgr = str( self.c[8].strip() )
			_nro = str( self.c[3].strip() )
			_bai = str( self.c[13].strip() )
			_cmu = str( self.c[11].strip() )
			_mun = str( self.c[10].strip() )
			_ufd = str( self.c[15].strip() )
			_cep = str( self.c[12].strip() )

		logradouro = True
		relacao    = ""
		if _lgr == '':	logradouro = False
		if _lgr !='' and _nro == "":	logradouro = False
		if _lgr !='' and _bai == "":	logradouro = False
		if _lgr !='' and _cmu == "":	logradouro = False
		if _lgr !='' and _mun == "":	logradouro = False
		if _lgr !='' and _ufd == "":	logradouro = False
		if _lgr !='' and _cep == "":	logradouro = False

		if _lgr !='' and _nro == "":	relacao += "nro,"
		if _lgr !='' and _bai == "":	relacao += "bai,"
		if _lgr !='' and _cmu == "":	relacao += "cmu,"
		if _lgr !='' and _mun == "":	relacao += "mun,"
		if _lgr !='' and _ufd == "":	relacao += "ufd,"
		if _lgr !='' and _cep == "":	relacao += "cep,"

		return logradouro,relacao

		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#175417") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Emissão NFCe { Nota Eletrônica de Venda ao Consumidor }", 0, 462, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.SetTextForeground("#3E99B7") 	
		dc.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Filial: { "+str( self.Filial )+" }", 677, 252, 90)


		dc.DrawRoundedRectangle(13,  0,  683,  95, 3)
		dc.DrawRoundedRectangle(13,  110,683, 160, 3)
		dc.DrawRoundedRectangle(13,  275,683, 35, 3)
		dc.DrawRoundedRectangle(13,  313,683, 82, 3)
		dc.DrawRoundedRectangle(13,  400,683, 40, 3)
		dc.DrawRoundedRectangle(13,  467,683, 35, 3)
