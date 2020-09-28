#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import os
import datetime
import calendar
import shutil
from extenso import NumeroPorExtenso
import davs as dav

from cdavs import *
from retaguarda import *
from nfe2 import *
from receber import *

from gerentenf import GerenteNfe,CancelaDavEcf
from conectar  import socorrencia,TelNumeric,cores,dadosCheque,regBandeira,srateio,listaemails,acesso,numeracao,AbrirArquivos,configuraistema,autorizacoes
from relatorio import extrato,recibo
from clientes  import referencias,alTeraInclui,ClientesRelatorios
from caixar  import Devolucoes,infomacoesNFes,ReferenciasDav
from daruma  import darumaNfce310
from acbrnfs import acbrNFCe
from contacorrente import ControlerConta

from nfcepysped import editadanfenfce

alertas = dialogos()
mens = menssagem()
sb   = sbarra()
acs  = acesso()
numero = numeracao()
nF     = numeracao()
infNFs = infomacoesNFes()
confSi = configuraistema()
expedicao_departamento = ExpedicaoDepartamentos()

acbrNC = acbrNFCe()

class recebimentos(wx.Frame):

	clientes = {}
	registro = 0
    
	def __init__(self, parent,id):
		
		self.parente = parent
		self.impress = impressao()
		self.extcli  = extrato()
		
		self.davCance = "F" #-: Inibir davs cancelados no relatorio
		self.ambACBRP = True
		self.acbrPlus = ['']

		self.ndav = ''
		self.ne   = NumeroPorExtenso()
		self.a    = '' #-: Retornar com arquivo TXT ECF TDM,MFD
		self.uFil = '' #-: Ultima filial q emitiu a nfce
		self.uEsT = '' #-: Ultima Estacao ACBR-PLUS
		self.fdbl = False
		
		"""  Bloqueio do Icone do Caixa   """
		self.parente.ToolBarra.EnableTool(503,False)
		
		self.fl = login.identifi

		self.sw = login.filialLT[ self.fl ][35].split(";")[23]
		self.TM = "\n\nO Sistema Aguardara p/"+str( login.filialLT[ self.fl ][38].split("|")[0].split(";")[14] )+" Segundos" if login.filialLT[ self.fl ][38] else "Sem informacoes para configuracao do tempo de conexao NFe-NFce"
		if login.filialLT[ self.fl ][38] and len( login.filialLT[ self.fl ][38].split("|")[0].split(";") ) >= 17 and login.filialLT[ self.fl ][38].split("|")[0].split(";")[16] == "T":	self.TM = "\n\nO Sistema Aguardara o Retorno da SEFAZ no Tempo do ACBr-PLUS\n\nAguarde..."

		wx.Frame.__init__(self, parent, id, 'Caixa: Recebimentos de DAV(s)', size=(970,632), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		
		self.ListaRec = RcListCtrl(self.painel, 300,pos=(0,120), size=(965,238),
								style=wx.LC_REPORT
								|wx.LC_VIRTUAL
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.ListaRec.SetBackgroundColour('#BFBFBF')
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.voltar)
		
		self.ListaRec.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.impresDav)
		self.ListaRec.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		"""
			Lista de Estações ACBR-Plus
		"""
		if os.path.exists(diretorios.aTualPsT+"/srv/impressoras.cmd") == True:
			
			ardp = open(diretorios.aTualPsT+"/srv/impressoras.cmd","r").read()
			for i in ardp.split("\n"):
				
				if len( i.split("|") ) >=8 and i.split("|")[7] == "S":
					
					NomeAcbr = i.split("|")[1].replace(":",'')
					Estacao  = i.split("|")[3].replace(":",'')
					self.acbrPlus.append(NomeAcbr+": "+Estacao)

		"""Busca Empresas"""
		self.filial = wx.StaticText(self.painel,-1,"{ Informações do DAV: Filial, Cliente }",pos=(510,61))
		self.filial.SetForegroundColour('#1A761A')
		self.filial.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.tipopd = wx.StaticText(self.painel,-1,"Tipo de DAV: {}",pos=(517,410))
		self.tipopd.SetForegroundColour('#896016')
		self.tipopd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
				
		""" ECF ON OFF """
		self.ecfof = wx.StaticText(self.painel,-1, '', pos=(510,104))
		self.ecfof.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		wx.StaticText(self.painel,-1, "Nº NFE:",      pos=(5,15)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Nº Chave:",    pos=(200,15)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Emissão:",     pos=(5,40)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Protocolo:",   pos=(200,40)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Usuário:",     pos=(370,40)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, "Emissão:",        pos=(565,40)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Controle:", pos=(760,15)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"DAV\nVinculado:",  pos=(760,30)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, "Total de NFs p/Inutilizar:",     pos=(200,362)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"NFs Usuário p/Inutilizar:",      pos=(200,377)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"NFs Filial       p/Inutilizar:", pos=(200,392)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, "Total de NFs em Contigência:",  pos=(400,362)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"NFs Usuário em Contigência:",   pos=(400,377)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"NFs Filial       em Contigência:", pos=(400,392)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		_filial = wx.StaticText(self.painel,-1,u"Relação de Filiais/Empresa", pos=(3,60))
		_filial.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_filial.SetForegroundColour('#12589D')

		self.vinnfe = wx.StaticText(self.painel,-1, "Redução\nOrçamento\nvinculado-NFe:", pos=(545,0))
		self.vinnfe.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		if self.sw == "3":	_menufs = wx.StaticText(self.painel,-1,u"Estações NFCe-ACBR-Plus", pos=(248,60))
		else:	_menufs = wx.StaticText(self.painel,-1,u"Opções do ECF { Menu Fiscal }", pos=(248,60))
		_menufs.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_menufs.SetForegroundColour('#12589D')

		"""   Mostrar informacoes de contigencias e inutilizacao   """
		self.cTperi = wx.StaticText(self.painel,-1,"", pos=(2,362))
		self.cTperi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cTperi.SetForegroundColour("#215A92")

		#--: Inutilizar
		self.cTInuT = wx.TextCtrl(self.painel,-1,'',pos=(325,359),size=(60,18),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cTfInT = wx.TextCtrl(self.painel,-1,'',pos=(325,374),size=(60,18),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cTuInT = wx.TextCtrl(self.painel,-1,'',pos=(325,388),size=(60,18),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cTInuT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cTfInT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cTuInT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cTInuT.SetBackgroundColour("#BB8686")
		self.cTfInT.SetBackgroundColour("#BB8686")		
		self.cTuInT.SetBackgroundColour("#BB8686")
		self.cTInuT.SetForegroundColour("#FFFFFF")
		self.cTfInT.SetForegroundColour("#FFFFFF")
		self.cTuInT.SetForegroundColour("#FFFFFF")

		self.cTconT = wx.TextCtrl(self.painel,-1,'',pos=(550,359),size=(60,18),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cTfcoT = wx.TextCtrl(self.painel,-1,'',pos=(550,374),size=(60,18),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cTucoT = wx.TextCtrl(self.painel,-1,'',pos=(550,388),size=(60,18),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cTconT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cTfcoT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cTucoT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cTconT.SetBackgroundColour("#266C83")
		self.cTfcoT.SetBackgroundColour("#266C83")		
		self.cTucoT.SetBackgroundColour("#266C83")
		self.cTconT.SetForegroundColour("#FFFFFF")
		self.cTfcoT.SetForegroundColour("#FFFFFF")
		self.cTucoT.SetForegroundColour("#FFFFFF")

		"""   Partilha do ICMS  """
		wx.StaticText(self.painel,-1,u"InterEstadual", pos=(620,367)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"( FPC )",       pos=(708,367)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"ICMS-Destino",  pos=(798,367)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"ICMS-Origem",   pos=(885,367)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.paInte = wx.TextCtrl(self.painel,-1,'',pos=(617,380),size=(83,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.paFund = wx.TextCtrl(self.painel,-1,'',pos=(705,380),size=(83,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.paDesT = wx.TextCtrl(self.painel,-1,'',pos=(795,380),size=(83,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.paOrig = wx.TextCtrl(self.painel,-1,'',pos=(882,380),size=(81,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.paInte.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.paFund.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.paDesT.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.paOrig.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.paInte.SetBackgroundColour("#BFBFBF")
		self.paFund.SetBackgroundColour("#BFBFBF")
		self.paDesT.SetBackgroundColour("#BFBFBF")		
		self.paOrig.SetBackgroundColour("#BFBFBF")

		"""  Certificado  """
		self.cerTIF = wx.StaticText(self.painel,-1,"Certificado:", pos=(2,392))
		self.cerTIF.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
		self.porCom = wx.StaticText(self.painel,-1,"", pos=(620,408))
		self.porCom.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.porCom.SetForegroundColour('#356A7B')

		self.nfecan = wx.StaticText(self.painel,-1,"{ Informações ECF, NFe, NFCe }", pos=(510,82))
		self.nfecan.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nfecan.SetForegroundColour('#EE0000')

		pesquisa = wx.StaticText(self.painel,-1,"Nome,Nº.DAV, P:Expressão, F:Fantasia, N:NºNoTaFiscal, C:NºCPF-CNPJ, O:NºCOO\n$-Valor, pesquisar-Controle Temporario use letra 'p/P' no final do numero", pos=(17,575))
		pesquisa.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	
		_oc = wx.StaticText(self.painel,-1,"Ocorrências:", pos=(365,439))
		_oc.SetForegroundColour('#1E90FF');	_oc.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ocorre = wx.StaticText(self.painel,-1,"", pos=(420,439))
		self.ocorre.SetForegroundColour('#0000FF')
		self.ocorre.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Periódo",   pos=(168,435)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Usuário:",  pos=(520,445)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Vendedor:", pos=(520,465)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pgTo = wx.StaticText(self.painel,-1,"Pagamento:", pos=(520,485))
		self.pgTo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.rcb = wx.StaticText(self.painel,-1,"Recebimento:",  pos=(520,505))
		self.rcb.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.vda = wx.StaticText(self.painel,-1,"",  pos=(210,433))
		self.vda.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.vda.SetForegroundColour('#DC2323')

		wx.StaticText(self.painel,-1,"Total Produtos:",        pos=(750,445)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Frete:",                 pos=(750,465)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Acréscimo:",             pos=(750,485)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Desconto:",              pos=(750,505)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tributos:",              pos=(750,525)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Total DAV:",             pos=(750,545)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Rateio Troco:",          pos=(524,558)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Rateio Conta Corrente:", pos=(524,575)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Pagamento com Crédito:", pos=(524,595)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,'Valor Recebido:',        pos=(750,575)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,'Troco:',                 pos=(800,595)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Dados da Filial """
		self.dFilial = wx.TextCtrl(self.painel,-1,'',pos=(0,98),size=(500,22),style = wx.TE_READONLY)
		self.dFilial.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Filiais """
		self.relFiliais = [""]+login.ciaRelac
		self.rfilial = wx.ComboBox(self.painel, 900, self.relFiliais[0],  pos=(0,71), size=(236,27), choices = self.relFiliais,style=wx.NO_BORDER|wx.CB_READONLY)
		
		"""  Libera Combobox de Estacoes ACBr  """
		self.esTAcbr = wx.ComboBox(self.painel, -1, self.acbrPlus[0],  pos=(245,71), size=(256,27), choices = self.acbrPlus,style=wx.NO_BORDER|wx.CB_READONLY)
		self.esTAcbr.Bind(wx.EVT_COMBOBOX, self.seTarEstarcaoAcbr)

		""""  Estacao acbr vinculada ao usuario   """
		if len( login.usaparam.split(";") ) >=2 and login.usaparam.split(";")[1]:

			self.esTAcbr.SetValue( login.usaparam.split(";")[1] )
			self.seTarEstarcaoAcbr(wx.EVT_COMBOBOX)

		if len( login.usaparam.split(";") ) >= 6 and login.usaparam.split(";")[5] == "T":

			self.rfilial.SetValue( login.usafilia+'-'+login.filialLT[ login.usafilia ][14] )
			self.rfilial.Enable( False ) 
			
		""" F I M """
		
		self.nfn = wx.TextCtrl(self.painel,-1,'',pos=(55,12),size=(120,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nfn.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.nfn.SetBackgroundColour('#E5E5E5')

		self.nfe = wx.TextCtrl(self.painel,-1,'',pos=(55,35),size=(120,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nfe.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.nfe.SetBackgroundColour('#E5E5E5')

		self.nfc = wx.TextCtrl(self.painel,-1,'',pos=(255,12),size=(285,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nfc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.nfc.SetBackgroundColour('#E5E5E5')

		self.nfp = wx.TextCtrl(self.painel,-1,'',pos=(255,35),size=(110,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nfp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.nfp.SetBackgroundColour('#E5E5E5')

		self.ecn = wx.TextCtrl(self.painel,-1,'',pos=(620,14),size=(115,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.ecn.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.ecn.SetBackgroundColour('#BFBFBF')

		self.ece = wx.TextCtrl(self.painel,-1,'',pos=(620,35),size=(115,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.ece.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.ece.SetBackgroundColour('#E5E5E5')

		"""  Dav Temporario de Controle  """
		self.uec = wx.TextCtrl(self.painel,263,'',pos=(830,12),size=(120,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.uec.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.uec.SetBackgroundColour('#BFBFBF')

		self.vin = wx.TextCtrl(self.painel,260,'',pos=(830,35),size=(120,20),style = wx.TE_READONLY)
		self.vin.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vin.SetBackgroundColour('#BFBFBF')
		self.vin.SetForegroundColour('#BE5656')

		self.unf = wx.TextCtrl(self.painel,-1,'',pos=(420,35),size=(120,20),style = wx.TE_READONLY)
		self.unf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.unf.SetBackgroundColour('#E5E5E5')

		self._us = wx.TextCtrl(self.painel,-1,'', pos=(590,440),size=(150,20), style=wx.TE_READONLY)
		self._us.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._us.SetBackgroundColour('#E5E5E5')

		self._vd = wx.TextCtrl(self.painel,-1,'',  pos=(590,460),size=(150,20), style=wx.TE_READONLY)
		self._vd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._vd.SetBackgroundColour('#E5E5E5')

		self._pg = wx.TextCtrl(self.painel,-1,'',  pos=(590,480),size=(150,20), style=wx.TE_READONLY)
		self._pg.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._pg.SetBackgroundColour('#E5E5E5')

		self._rc = wx.TextCtrl(self.painel,229,'',  pos=(590,500),size=(150,20), style=wx.TE_READONLY)
		self._rc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._rc.SetBackgroundColour('#E5E5E5')

		self._tp = wx.TextCtrl(self.painel,-1,'',       pos=(840,440),size=(120,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self._tp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._tp.SetBackgroundColour('#E5E5E5')

		self._fr = wx.TextCtrl(self.painel,-1,'',       pos=(840,460),size=(120,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self._fr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._fr.SetBackgroundColour('#E5E5E5')

		self._ac = wx.TextCtrl(self.painel,-1,'',       pos=(840,480),size=(120,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self._ac.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._ac.SetBackgroundColour('#E5E5E5')

		self._dc = wx.TextCtrl(self.painel,-1,'',       pos=(840,500),size=(120,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self._dc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._dc.SetBackgroundColour('#E5E5E5')

		self._tb = wx.TextCtrl(self.painel,-1,'',      pos=(840,520),size=(120,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self._tb.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._tb.SetBackgroundColour('#E5E5E5')

		self._td = wx.TextCtrl(self.painel,-1,'',       pos=(840,540),size=(120,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self._td.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._td.SetBackgroundColour('#E5E5E5')
		
		self._cx = wx.StaticText(self.painel,-1, pos=(524,540) )
		self._cx.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._cx.SetForegroundColour('#264663')

		#-->[ Rateio ]
		self._tr = wx.TextCtrl(self.painel,-1, pos=(640,555), size=(80,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self._tr.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._tr.SetBackgroundColour('#E5E5E5')
		self._tr.SetForegroundColour('#264663')

		self._cr = wx.TextCtrl(self.painel,-1, pos=(640,573), size=(80,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self._cr.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._cr.SetBackgroundColour('#E5E5E5')
		self._cr.SetForegroundColour('#264663')

		self._pc = wx.TextCtrl(self.painel,-1, pos=(640,592), size=(80,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self._pc.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self._pc.SetBackgroundColour('#E5E5E5')
		self._pc.SetForegroundColour('#264663')
		#-->[ F I M ]

		self._vr = wx.TextCtrl(self.painel,-1,'',       pos=(840,570),size=(120,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self._vr.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._vr.SetBackgroundColour('#E5E5E5');	self._vr.SetForegroundColour('#456D91')

		self.tro = wx.TextCtrl(self.painel,-1,'',       pos=(840,590),size=(120,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.tro.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.tro.SetBackgroundColour('#E5E5E5');	self.tro.SetForegroundColour('#456D91')

		vinculo  = wx.BitmapButton(self.painel, 321, wx.Bitmap("imagens/confere.png",       wx.BITMAP_TYPE_ANY), pos=(790,  26), size=(18,18))				
		Voltar   = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/voltam.png",        wx.BITMAP_TYPE_ANY), pos=(320, 449), size=(36,35))				
		Procurar = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/procurap.png",      wx.BITMAP_TYPE_ANY), pos=(365, 449), size=(36,35))				
		Printar  = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/printp.png",        wx.BITMAP_TYPE_ANY), pos=(413, 449), size=(36,35))

		self.CupomFis = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/cupomi.png",   wx.BITMAP_TYPE_ANY), pos=(460, 449), size=(36,35))				
		self.emissnfe = wx.BitmapButton(self.painel, 225, wx.Bitmap("imagens/nfe.png",      wx.BITMAP_TYPE_ANY), pos=(320, 485), size=(36,35))				

		nfegeren = wx.BitmapButton(self.painel, 234, wx.Bitmap("imagens/gerenciador16.png", wx.BITMAP_TYPE_ANY), pos=(365, 485), size=(36,35))				
		ContaCor = wx.BitmapButton(self.painel, 227, wx.Bitmap("imagens/bank.png",          wx.BITMAP_TYPE_ANY), pos=(413, 485), size=(36,35))				

		self.CupomCan = wx.BitmapButton(self.painel, 228, wx.Bitmap("imagens/cupomc.png",   wx.BITMAP_TYPE_ANY), pos=(460, 485), size=(36,35))				
		self.NFCeEMiT = wx.BitmapButton(self.painel, 250, wx.Bitmap("imagens/nfce16.png",   wx.BITMAP_TYPE_ANY), pos=(320, 520), size=(36,35))				

		self.vincular = wx.BitmapButton(self.painel, 251, wx.Bitmap("imagens/vinculo.png",  wx.BITMAP_TYPE_ANY), pos=(365, 520), size=(36,35))				
		self.creceber = wx.BitmapButton(self.painel, 261, wx.Bitmap("imagens/pcreceber.png",wx.BITMAP_TYPE_ANY), pos=(413, 520), size=(36,35))				
		self.sangrias = wx.BitmapButton(self.painel, 262, wx.Bitmap("imagens/cash24.png",   wx.BITMAP_TYPE_ANY), pos=(460, 520), size=(36,35))				

		referenc = wx.BitmapButton(self.painel, 232, wx.Bitmap("imagens/referencia16.png",  wx.BITMAP_TYPE_ANY), pos=(130, 513), size=(28,28))				
		ocorrenc = wx.BitmapButton(self.painel, 231, wx.Bitmap("imagens/ocorrencia.png",    wx.BITMAP_TYPE_ANY), pos=(280, 449), size=(28,28))				
		extratoc = wx.BitmapButton(self.painel, 230, wx.Bitmap("imagens/cccl.png",          wx.BITMAP_TYPE_ANY), pos=(280, 482), size=(28,28))				
		#self.sms = wx.BitmapButton(self.painel, 251, wx.Bitmap("imagens/sms16.png",         wx.BITMAP_TYPE_ANY), pos=(907, 90), size=(28,28))				
		#self.waz = wx.BitmapButton(self.painel, 252, wx.Bitmap("imagens/whatsapp16.png",         wx.BITMAP_TYPE_ANY), pos=(937, 90), size=(28,28))				
		#self.sms = GenBitmapTextButton(self.painel,-1,label='',  pos=(907,90),size=(28,29), bitmap=wx.Bitmap("imagens/sms24.png", wx.BITMAP_TYPE_ANY))

		#self.sms.SetBackgroundColour('#5298DC')
		#self.waz.SetBackgroundColour('#317A31')

		self.Aberto = wx.RadioButton(self.painel,-1,"DAV(s) em Aberto ", pos=(15,430), style=wx.RB_GROUP)
		self.Davss  = wx.RadioButton(self.painel,-1,"DAV(s)", pos=(15,452))
		self.dcance = wx.RadioButton(self.painel,-1,"DAV(s) Cancelados", pos=(15,474))
		self.Orcam  = wx.RadioButton(self.painel,-1,"Orçamento", pos=(15,497))
		self.Todos  = wx.RadioButton(self.painel,-1,"Todos ", pos=(15,520))
		
		self.sfaTu  = wx.RadioButton(self.painel,-1, "Simples faturamento", pos=(15, 408))
		self.efuTu  = wx.RadioButton(self.painel,-1, "Entrega futura", pos=(145,408))
		self.lsTcg  = wx.RadioButton(self.painel,-1, "NFCe contigência", pos=(251,408))
		self.lsTin  = wx.RadioButton(self.painel,-1, "NFCe interrompida", pos=(369,408))

		self.cdevol = wx.CheckBox(self.painel, -1,  "Devolução", pos=(15,542))

		self.Todos. SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.Davss .SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.Orcam .SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.Aberto.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dcance.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cdevol.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.sfaTu. SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.efuTu. SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.lsTcg. SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.lsTin. SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	
		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(165,450), size=(110,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(165,485), size=(110,25))

		self.vendedor = wx.ComboBox(self.painel, -1, '',          pos=(164,515), size = (144,27), choices = login.uslis,style=wx.NO_BORDER|wx.CB_READONLY)
		self.rCaixass = wx.RadioButton(self.painel,-1,"Caixa   ", pos=(164,542), style = wx.RB_GROUP)
		self.rVendedo = wx.RadioButton(self.painel,-1,"Vendedor", pos=(225,542))

		self.rVendedo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.rCaixass.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.consultar = wx.TextCtrl(self.painel, -1,            pos=(14,597),   size=(400,23),style=wx.TE_PROCESS_ENTER)
		self.pesqperio = wx.CheckBox(self.painel, -1, "Pesquisar\ncliente\np/período", pos=(417,576))
		self.pesqperio.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	
		Voltar.Bind  (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Procurar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Printar.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		ContaCor.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		ocorrenc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		extratoc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		referenc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.vin.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		nfegeren.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		
		self.emissnfe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.CupomFis.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.CupomCan.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.vincular.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.creceber.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.sangrias.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.NFCeEMiT.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.uec.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
	
		Voltar.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Procurar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Printar.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		ContaCor.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		ocorrenc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		extratoc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		referenc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.vin.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		nfegeren.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.emissnfe.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.CupomFis.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.CupomCan.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.vincular.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.creceber.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.sangrias.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.NFCeEMiT.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.uec.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		
		self.Bind(wx.EVT_KEY_UP,self.Teclas)
		self.ListaRec.Bind(wx.EVT_LIST_ITEM_SELECTED, self.Teclas)	
			
		Procurar.Bind(wx.EVT_BUTTON, self.selecionar)
		Printar.Bind(wx.EVT_BUTTON,self.impresDav)
		Voltar.Bind(wx.EVT_BUTTON,self.voltar)

		self.CupomFis.Bind(wx.EVT_LEFT_DCLICK,self.OnClick)
		self.CupomFis.Bind(wx.EVT_BUTTON,self.ecfcaixa)

		ContaCor.Bind(wx.EVT_BUTTON,self.acessconta)
		self.CupomCan.Bind(wx.EVT_BUTTON,self.ecfcancela)
		extratoc.Bind(wx.EVT_BUTTON,self.extrato)
		ocorrenc.Bind(wx.EVT_BUTTON,self.frecebimento)
		nfegeren.Bind(wx.EVT_BUTTON,self.cnTGenrenteNf)
		referenc.Bind(wx.EVT_BUTTON,self.cxreferencia)
		vinculo.Bind(wx.EVT_BUTTON, self.vinculado)

		self.emissnfe.Bind(wx.EVT_BUTTON, self.nfeatalho)
		self.vincular.Bind(wx.EVT_BUTTON, self.vinculacl)
		self.creceber.Bind(wx.EVT_BUTTON, self.cnTReceber)
		self.sangrias.Bind(wx.EVT_BUTTON, self.retirada)
		#self.sms.Bind(wx.EVT_BUTTON, self.comunicacaoSMS)

		self.vendedor.Bind(wx.EVT_COMBOBOX, self.evradio)		
		self.rfilial.Bind(wx.EVT_COMBOBOX, self.SeleFilial)
		self.cdevol.Bind(wx.EVT_CHECKBOX, self.dvchekb)

		self.Todos. Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.Davss. Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.Aberto.Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.dcance.Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.Orcam. Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.sfaTu. Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.efuTu. Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.lsTcg. Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.lsTin. Bind(wx.EVT_RADIOBUTTON,self.evradio)
		
		self.vin.Bind(wx.EVT_LEFT_DCLICK, self.abrirdav)
		self.uec.Bind(wx.EVT_LEFT_DCLICK, self.pesquisaControle)
		self.ecn.Bind(wx.EVT_LEFT_DCLICK, self.pesquisaVinculo)
		#self.selecionar(wx.EVT_BUTTON)
		
		"""   Bloquei do Menu do caixa   """
		if acs.acsm("505",True) == True:	self.MenuPopUp()
		
		self.SelecaoFilial( 900 )

		self.NFCeEMiT.Bind(wx.EVT_BUTTON, self.TeteNfc )

		"""   Bloqueios   """
		self.vincular.Enable( acs.acsm("516",True) )
		self.creceber.Enable( acs.acsm("515",True) )
		self.CupomCan.Enable( acs.acsm("510",True) )
		self.CupomFis.Enable( acs.acsm("503",True) ) #-: Recebimento do DAV
		self.sangrias.Enable( acs.acsm("509",True) ) #-: Sangrias
		self.emissnfe.Enable( acs.acsm("504",True) ) #-: Emissao de NFE
		
		ocorrenc.Enable( acs.acsm("511",True) ) #-: Ocorrencias
		extratoc.Enable( acs.acsm("512",True) ) #-: Extrato do Cliente
		ContaCor.Enable( acs.acsm("513",True) ) #-: Conta Corrente
		ContaCor.Enable( acs.acsm("513",True) ) #-: Conta Corrente
		nfegeren.Enable( acs.acsm("517",True) ) #-: Gerenciador de NFe-NFCe

	def OnClick(self,event):	self.fdbl = True #-: Click duplo no recebimento
	def EstacaoAcbr(self,event):	self.acbrEstacao( self.fl )
	def pesquisaControle(self,event):
		
		if self.uec.GetValue():
			
			self.consultar.SetValue( self.uec.GetValue() )
			self.selecionar(wx.EVT_BUTTON)

	#def comunicacaoSMS(self,event):

	#	if not self.ListaRec.GetItemCount():	alertas.dia( self, "Selecione um dav para o sistema registrar a filial...\n"+(" "*140),"Envio de SMS")
	#	else:	

	#		id_filial = self.ListaRec.GetItem( self.ListaRec.GetFocusedItem(), 29 ).GetText()
	#		voi_frame=GerenciadorSMS(parent=self,id=-1, filial = id_filial, dados = ("CPF-CNPJ","CodigoCliente") )
	#		voi_frame.Centre()
	#		voi_frame.Show()
		
	def pesquisaVinculo(self,event):
		
		if self.ecn.GetValue():
			
			if self.Orcam.GetValue():	self.Davss.SetValue( True )
			elif self.Davss.GetValue():	self.Orcam.SetValue( True )
			self.consultar.SetValue( self.ecn.GetValue() )
			self.selecionar(wx.EVT_BUTTON)
	
	def seTarEstarcaoAcbr(self,event):	

		if len( self.esTAcbr.GetValue().split(":") ) == 2:	login.acbrEsta = self.esTAcbr.GetValue().split(":")[1].strip()
		else:	login.acbrEsta = ""
				
	def acbrEstacao(self,Filial):
		
		rTTcp  = False
		esTaca = ''

		if Filial == "":
			
			alertas.dia(self,"Sem filial p/Continuar\n\nSelecione uma filial e/ou um DAV...\n"+(" "*120),"Estação ACBr-PLUS")
			return 

		if login.usaenfce != 'T':	alertas.dia(self,"Usuario desmarcado p/emissão de nfce...\n"+(" "*120),"Caixa: Emissão de NFCe")
		if login.usaenfce == 'T' and login.filialLT[ Filial ][21] == '2' and self.sw == "3" and login.acbrEsta !="":
			
			rTTcp = self.ambACBRP = acbrNC.configuraNFCe( self, Filial )
			self.uFil = Filial
			self.uEsT = esTaca
		
		if rTTcp == False:

			self.esTAcbr.SetValue("")
			login.acbrEsta = ""
			self.uFil = ""
			self.uEsT = ""
			
	def auTorizarDevolucao(self,event):
		
		indice = self.ListaRec.GetFocusedItem()
		nDavs  = self.ListaRec.GetItem(indice,  0).GetText()

		if self.ListaRec.GetItemCount() == 0:	alertas.dia(self, "Lista de Recebimento estar Vazia!!\n"+(" "*100),"Autorização de Devolução");	return
		if self.cdevol.GetValue() == False:	alertas.dia(self, "Marque Devolução antes de Continuar!!\n"+(" "*100),"Autorização de Devolução");	return
		
		conn = sqldb()
		sql  = conn.dbc("Caixa: Consulta de DAVs, Autorizar Devolução", fil =  self.fl, janela = self.painel )
		rcbc = ""
		grv  = ""
	
		if sql[0] == True:
	
			if sql[2].execute("SELECT cr_urec,cr_reca,cr_audv FROM dcdavs WHERE cr_ndav='"+str( nDavs )+"'") !=0:
				
				rcb,can,auT = sql[2].fetchone()
				if rcb != "":	rcbc +="1-Devolução Recebida\n"
				if can == "3":	rcbc +="2-Devolução Cancelada\n"
				if auT != "":	rcbc +="3-Devolução ja foi Autorizada "+str( auT )+"\n"
			
			if rcbc == "":

				receb = wx.MessageDialog(self,"Confirme para Autorizar o Recebimento da Devolução...\n"+(" "*140),"Autorização de Devolução",wx.YES_NO|wx.NO_DEFAULT)
				if receb.ShowModal() ==  wx.ID_YES:
					
					try:
						
						ET = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
						auToriza = sql[2].execute("UPDATE dcdavs SET cr_audv='"+str( ET )+"' WHERE  cr_ndav='"+str( nDavs )+"'")
						
						sql[1].commit()
						grv = True
						
					except Exception, _reTornos:
						
						sql[1].rollback()
						grv = False
			
			conn.cls( sql[1] )

		if rcbc != "":	alertas.dia(self,"{ Retorno da Devolução Selecionada }\n\n"+rcbc+"\n"+(" "*110),"Autorização de Devolução")
		if rcbc == "" and grv == False:	alertas.dia(self,"Devolução não Autorizada\n\nRetorno: "+str( _reTornos )+"\n"+(" "*130),"Autorização de Devolução")
		if rcbc == "" and grv == True:	alertas.dia(self,"Devolução Autorizada com Sucesso!!\n"+(" "*110),"Autorização de Devolução")
		
	def vinculado(self,event):
		
		if self.vin.GetValue().strip() == "":	alertas.dia(self,"Sem numero de dav em dav-vinculado...\n"+(" "*100),"Caixa: Consulta de DAV Vinculado")
		else:
			
			conn = sqldb()
			sql  = conn.dbc("Caixa: Consulta de DAVs", fil =  self.fl, janela = self.painel )
			sV   = ""

			if sql[0] == True:
				
				_ps1 = "SELECT cr_cupo,cr_ccan,cr_ecem,cr_ecca,cr_nota,cr_nfem,cr_nfca,cr_chnf FROM cdavs  WHERE cr_ndav='"+str( self.vin.GetValue() )+"'"
				_ps2 = "SELECT cr_cupo,cr_ccan,cr_ecem,cr_ecca,cr_nota,cr_nfem,cr_nfca,cr_chnf FROM dcdavs WHERE cr_ndav='"+str( self.vin.GetValue() )+"'"
				if sql[2].execute( _ps1 ) !=0:	sV = sql[2].fetchall()[0]
				if sV == "" and sql[2].execute( _ps2 ) !=0:	sV = sql[2].fetchall()[0]
				conn.cls(sql[1])
				
			if sV !="":	alertas.dia(self, "{ Dados de Emissão de Documenos Fiscais }\n\nNº NFe..................: "+str( sV[4] )+"\nEmissão NFe.........: "+str( sV[5] )+"\nCancelamento NFe: "+str( sV[6] )+\
			"\nNFe Nº Chave........: "+str( sV[7] )+"\n"+(" "*160),"DAVs: Informações")

			else:	alertas.dia(self,"Dav não localizado...\n"+(" "*100),"DAVs: Informações")
			
	def TeteNfc(self,event):

		if str( self._tp.GetValue() ) == '':

			alertas.dia(self,"Selecione um dav para emissão da NFCe...\n"+(" "*100),"Caixa: Emissão de NFCe")	
			return

		indice = self.ListaRec.GetFocusedItem()
		nDavs  = self.ListaRec.GetItem(indice,  0).GetText()
		cdCli  = self.ListaRec.GetItem(indice, 32).GetText()
		receb  = self.ListaRec.GetItem(indice, 23).GetText()
		if self.sw == "3":
				
			"""
				Envia automaticamente os dados da filial selecionada para o acbr, se os ultimos dados da filial
				enviado for diferente da atual
			"""
			if self.esTAcbr.GetValue().strip() == "":
						
				alertas.dia(self,"Selecione uma Estação ACBR-Plus p/Continuar...\n"+(" "*120),"ACBr-Plus")
				return
			
			if len( login.filialLT[ self.fl ][38].split("|")[0].split(";") ) >= 17 and login.filialLT[ self.fl ][38].split("|")[0].split(";")[16] == "T":	self.TM = "\n\nAguardando Retorno da SEFAZ no Tempo do ACBr-PLUS\n\nAguarde..."

			if self.selecionarFilial() == False:	return
			if self.fl != self.uFil or self.uEsT != self.esTAcbr.GetValue().split(":")[1].strip():	self.acbrEstacao( self.fl )

			darumaNfce310.Filial = self.fl
			darumaNfce310.cdClie = cdCli
			darumaNfce310.nuDavs = nDavs
			darumaNfce310.TPEmis = 1
			darumaNfce310.dReceb = receb
			darumaNfce310.vincul = self.ListaRec.GetItem(indice, 54).GetText()
			
			fwd_frame=darumaNfce310(parent=self,id=-1)
			fwd_frame.Centre()
			fwd_frame.Show()

		elif self.sw == "2":

			if self.cdevol.GetValue():	alertas.dia( self, "NFCe não permitido para devolução...\n"+(" "*100),"NFCe, Devoluçao")
			else:
				
				"""  Verica se a frem ja foi aberta se aberto nao permiti abrir novamente  """
				if editadanfenfce.instancia > 0:	return

				filial_dav = self.ListaRec.GetItem( self.ListaRec.GetFocusedItem() ,29 ).GetText()
				#_dados = self.fl, nDavs, 2
				_dados = filial_dav, nDavs, 2

				editadanfenfce.instancia = 1
				nfc_frame=editadanfenfce(parent=self,id=-1, dados = _dados )
				nfc_frame.Centre()
				nfc_frame.Show(True)
			
	def SeleFilial(self,event):	self.SelecaoFilial( event.GetId() )
	def SelecaoFilial(self,_id):

		self.fl = self.rfilial.GetValue().split("-")[0]
		if self.rfilial.GetValue() !="":	self.configuracaoFiliais()
		
		self.ListaRec.DeleteAllItems()
		self.ListaRec.SetItemCount( 0 )
		self.ListaRec.Refresh()
		if _id == 900:	self.selecionar(wx.EVT_BUTTON)

	def configuracaoFiliais(self):
		
		""" Servico de WEB-SERVICE, self.sw 1-Migrete-Daruma 2-PySped 3-ACBrMonitorPlus """
		self.sw = ""
		if len( login.filialLT[ self.fl ][35].split(";") ) >=24:	self.sw = login.filialLT[ self.fl ][35].split(";")[23]
		
		self.dFilial.SetValue( str( login.filialLT[  self.fl ][1].upper() ) )
		self.dFilial.SetBackgroundColour('#E5E5E5')
		self.dFilial.SetForegroundColour('#4D4D4D')	

		if len( login.filialLT[ self.fl ][35].split(";") ) >=11:	self.davCance = login.filialLT[ self.fl ][35].split(";")[10]
		if login.filialLT[ self.fl ][38] and len( login.filialLT[ self.fl ][38].split("|")[0].split(";") ) >= 17 and login.filialLT[ self.fl ][38].split("|")[0].split(";")[16] == "T":	self.TM = "\n\nAguardando Retorno da SEFAZ no Tempo do ACBr-PLUS\n\nAguarde..."

		if nF.rF( cdFilial = self.fl ) == "T":

			self.dFilial.SetBackgroundColour('#711717')
			self.dFilial.SetForegroundColour('#FF2800')	

		elif nF.rF( cdFilial = self.fl ) !="T" and login.identifi != self.fl:

			self.dFilial.SetBackgroundColour('#0E60B1')
			self.dFilial.SetForegroundColour('#E0E0FB')	

		"""   CERTIFICADO    """
		alls = login.filialLT[ self.fl ][30].split(";")
		aldv = diretorios.esCerti+alls[6] 
		alsh = alls[5]

		crTificado = "Certificado: "
		rTCer = confSi.validadeCertificado(aldv,alsh)

		self.cerTIF.SetForegroundColour("#1A1A1A")
		
		if rTCer[0] == True and len( rTCer[1].split("\n") ) >= 6:

			_dTa  = str( rTCer[1].split("\n")[3][23:] )
			_dTd  = str( rTCer[1].split("\n")[3][23:33] ).strip()
			_dias = 0

			crTificado +=_dTa
			
			if _dTa !="":
				
				_dVal = datetime.datetime.strptime(_dTd, "%d/%m/%Y").date()
				_dHoj = datetime.datetime.now().date()
				_dias = ( _dVal - _dHoj ).days
			
			if _dias <= 30:	self.cerTIF.SetForegroundColour("#BC4F4F")
			if _dias <= 15:	self.cerTIF.SetForegroundColour("#DB2C2C")
			
		if rTCer[0] == False:	crTificado +="{ Vazio }"

		self.cerTIF.SetLabel(crTificado)
		
	def MenuPopUp(self):

		self.popupmenu  = wx.Menu(style=wx.NO_BORDER)
		self.Relatorios = wx.Menu(style=wx.NO_BORDER)
		self.comissao   = wx.Menu(style=wx.NO_BORDER)

		self.popupmenu.Append(wx.ID_APPLY, "Gerênciador de relatórios do caixa")
		#self.popupmenu.AppendSeparator()
		self.popupmenu.Append(wx.ID_PASTE, "Analisar Custo e &Margens do DAV Selecionado")
		self.popupmenu.Append(wx.ID_PREFERENCES, "Listar &Quantidade de Impressões do DAV Selecionado")
		#self.popupmenu.AppendSeparator()

		self.popupmenu.Append(1013, "Autorizar o Recebimento da Devolução")
		self.popupmenu.Append(1015, "Alteração da Referência de Entrega do Dav Selecionado")
		self.popupmenu.Append(1016, "Recalcular DAV { Frete, Acrescimo, Desconto, Codigo Fiscal }")
		#self.popupmenu.AppendSeparator()
		self.popupmenu.Append(wx.ID_PRINT,"&Conciliar compras do cliente selecionado { compras,devolução,cancelamentos}")
		self.popupmenu.Append(wx.ID_SELECTALL,  "Controle do conta corrente")


		self.Bind(wx.EVT_MENU, self.OnPopupItemSelected)
		self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

		self.popupmenu.Enable( id = wx.ID_PASTE, enable = acs.acsm("507",True) )
		self.popupmenu.Enable( id = 1013, enable = acs.acsm("518",False) )

	def OnShowPopup(self, event):

		pos = event.GetPosition()
		pos = self.ScreenToClient(pos)
		self.PopupMenu(self.popupmenu, pos)

	def OnPopupItemSelected(self, event):

		indice = self.ListaRec.GetFocusedItem()
		even   = event.GetId()

		if even == 5033:	self.cusTosDav(wx.EVT_BUTTON)
		if even == 5022:	self.rImpressoes(wx.EVT_BUTTON)

		if even == 5102: #in rl:
			
			Devolucoes.id_ = '' #even
			Devolucoes.md_ = ''
			Devolucoes.fla = self.fl
			
			dev_frame=Devolucoes(parent=self,id=even)
			dev_frame.Centre()
			dev_frame.Show()

		elif even == 5010:
			
			if not self.ListaRec.GetItem( self.ListaRec.GetFocusedItem(), 32 ).GetText():
				alertas.dia( self, "Cliente sem código de cadastro...\n"+(" "*120),"Conciliar compras do cliente")
			else:
					
				ClientesRelatorios.Filial = self.fl
				ClientesRelatorios._id    = ""
				ClientesRelatorios.caixa  = True
				clie_frame=ClientesRelatorios(parent=self,id=-1)
				clie_frame.Centre()
				clie_frame.Show()

		elif even == 1013:	self.auTorizarDevolucao(wx.EVT_BUTTON)

		elif even == 1015 or even == 1016:

			if self.ListaRec.GetItemCount() == 0:	alertas.dia( self,"Lista estar vazia...\n"+(" "*100),"Caixa: Ponto de Referência")
			else:
			
				if even == 1015:
					
					arq_frame=ReferenciasDav(parent=self,id=even)
					arq_frame.Centre()
					arq_frame.Show()

				if even == 1016:	self.recalcularDavPedido()

		if even ==  5037:

			ControlerConta.modulo = "3-Caixa recebimentos"

			ccct_frame=ControlerConta(parent=self,id=even)
			ccct_frame.Centre()
			ccct_frame.Show()

	def recalcularDavPedido(self):
	
		indice = self.ListaRec.GetFocusedItem()

		conn = sqldb()
		sql  = conn.dbc("Caixa: Consulta de DAVs", fil =  self.fl, janela = self.painel )

		if sql[0] == True:

			ach = "SELECT cr_tipo,cr_reca FROM cdavs WHERE cr_ndav='"+str( self.ListaRec.GetItem(indice, 0).GetText() )+"'"
			okc = sql[2].execute( ach )
			rT  = sql[2].fetchone()

			conn.cls( sql[1] )
			
			if okc !=0:
					
				if rT[0] == "1":

					if rT[1] == "" or rT[1] == "2":
							
						dav.dav.caixaDavNumeroRec = self.ListaRec.GetItem(indice, 0).GetText()
						dav.dav.caixaDavRecalculo = True
						dav.dav.caixaDavFilial = self.ListaRec.GetItem(indice, 29).GetText()

						dav_frame=dav.davControles(parent=self,id=-1)
						dav_frame.Centre()
						dav_frame.Show()
				
					else:	alertas.dia( self,"{ Ajustar-Recalcular DAV }\n\nPermitido apenas para davs: Aberto, Estornado...\n"+(" "*100),"Caixa: Ajustar-Recalcular DAV")
		
				else:	alertas.dia( self,"{ Ajustar-Recalcular DAV }\n\nNão e dav valido...\n"+(" "*100),"Caixa: Ajustar-Recalcular DAV")
					
			else:	alertas.dia( self,"{ Ajustar-Recalcular DAV }\n\nDAV "+str( self.ListaRec.GetItem(indice, 0).GetText() ) +", não localizado...\n"+(" "*100),"Caixa: Ajustar-Recalcular DAV")
		
		
	#def abrirDanfe(self,event):

	#	gerenciador.Anexar = self.a
	#	gerenciador.imprimir = False
	#	gerenciador.TIPORL   = "ECF"
	#	gerenciador.Filial   = self.fl
					
	#	ger_frame=gerenciador(parent=self,id=-1)
	#	ger_frame.Centre()
	#	ger_frame.Show()
		

	def rImpressoes(self,event):

		indice = self.ListaRec.GetFocusedItem()

		if self.ListaRec.GetItem(indice, 45).GetText() !="None" and self.ListaRec.GetItem(indice, 45).GetText() !='':
			
			historico = u'Impressões do Dav Selecionado\n\n'
			for _i in self.ListaRec.GetItem(indice, 45).GetText().split("\n"):
				
				if _i !='':
					
					_d = _i.split('|')

					historico +=_d[0]
					if _d[1].strip() == "" or _d[1].strip() == "F":	historico +=u" Impressão Normal"
					if _d[1].strip() == "T":	historico +=u" Impressão pela Expedição"
					historico +="\n"
			
		else:	historico = "DAV Sem Impressões..."
	
		MostrarHistorico.hs = historico
		MostrarHistorico.TP = ""
		MostrarHistorico.TT = "Caixa { Impressões }"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.fl
		MostrarHistorico.GD = ""

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
		
	def cxreferencia(self,event):

		indice = self.ListaRec.GetFocusedItem()
		self.codigocliente = self.ListaRec.GetItem(indice, 32).GetText()

		if self.ListaRec.GetItem(indice, 32).GetText() != '':

			referencias.rfFilial = self.fl
			addEdit = referencias(parent=self,id=-1)
			addEdit.Centre()
			addEdit.Show()	

	def retirada(self,event):

		if self.selecionarFilial() == False:	return
		
		san_frame=sangria(parent=self,id=-1)
		san_frame.Centre()
		san_frame.Show()
		
		
	def cnTReceber(self,event):
		
		login.rcmodulo = 'CAIXA'
		rcb_frame=contasReceber(parent=self,id=-1)
		rcb_frame.Centre()
		rcb_frame.Show()

	def cnTGenrenteNf(self,event):

		gnf_frame=GerenteNfe(parent=self,id=-1)
		gnf_frame.Centre()
		gnf_frame.Show()

	def abrirdav(self,event):
		
		if   self.cdevol.GetValue() != True:	alertas.dia(self.painel,u"Função exclusiva do modulo de devolução!!","Caixa: Recebimentos")
		elif self.cdevol.GetValue() == True and self.vin.GetValue() != '':

			if   self.vin.GetValue() == '':	alertas.dia(self.painel,"DAV-Vinculado, estar vazio!!","Caixa: Recebimentos")
			elif self.vin.GetValue() != '':
				
				indice    = self.ListaRec.GetFocusedItem()
				filialDav = self.ListaRec.GetItem(indice,47).GetText()
				TipoDav   = self.ListaRec.GetItem(indice,17).GetText()

				cdDav = cdEma = ""
				if TipoDav == "1":	cdDav,cdEma = "605", "607"
				if TipoDav == "2":	cdDav,cdEma = "606", "608"
			
				NumeroDav = self.vin.GetValue()

				self.impress.impressaoDav( NumeroDav, self, True, True,  "", "", servidor = filialDav, codigoModulo=cdDav, enviarEmail = cdEma )
				#self.impress.impressaoDav( NumeroDav, self, True, False, "", "", servidor = filialDav, codigoModulo=cdDav, enviarEmail = cdEma )

				#self.impress.impressaoDav( NumeroDav, self, True, True,  "", "", servidor =  self.fl, codigoModulo=cdDav, enviarEmail = cdEma )
				#self.impress.impressaoDav( NumeroDav, self, True, False, "", "", servidor =  self.fl, codigoModulo=cdDav, enviarEmail = cdEma )

	def evradio(self,event):	self.selecionar(wx.EVT_BUTTON)
	def aTualizaLista(self):	self.selecionar(wx.EVT_BUTTON)	
	def dvchekb(self,event):
		
		if self.cdevol.GetValue() == True:

			self.Todos.SetValue(True)
			self.Todos.Disable()
			self.Davss.Disable() 
			self.Aberto.Disable()
			self.dcance.Disable()
			self.Orcam.Disable()

			self.ListaRec.SetBackgroundColour('#F5E5E9')			
			self.ListaRec.attr1.SetBackgroundColour('#F8EDF0')

			header = self.ListaRec.GetColumn ( 0 )
			header.SetText ( u'Nº Devolução' )
			self.ListaRec.SetColumn ( 0, header )
			
			self.ListaRec.DeleteAllItems()
			self.ListaRec.Refresh()
			
			self.SetTitle(u"Caixa: Recebimentos e Controle de Devoluções")
			self.CupomFis.SetBitmapLabel(wx.Bitmap('imagens/trocap.png'))
			self.CupomCan.SetBitmapLabel(wx.Bitmap('imagens/ctrocap.png'))

			self.selecionar(wx.EVT_BUTTON)
			
		else:

			self.Todos.Enable()
			self.Davss.Enable() 
			self.Aberto.Enable()
			self.dcance.Enable()
			self.Orcam.Enable()
			self.vincular.Enable()

			self.ListaRec.SetBackgroundColour('#BFBFBF')
			self.ListaRec.attr1.SetBackgroundColour('#CCCCCC')

			header = self.ListaRec.GetColumn ( 0 )
			header.SetText ( 'Nº D A V' )
			self.ListaRec.SetColumn ( 0, header )

			self.ListaRec.DeleteAllItems()
			self.ListaRec.Refresh()

			self.SetTitle("Caixa: Recebimentos de DAV(s)")
			self.CupomFis.SetBitmapLabel (wx.Bitmap("imagens/cupomi.png"))
			self.CupomCan.SetBitmapLabel (wx.Bitmap("imagens/cupomc.png"))

			self.selecionar(wx.EVT_BUTTON)

			self.vincular.Enable(acs.acsm("0516",True))
			
	def iconizar(self,event): self.Destroy()
		
	def extrato(self,event):

		indice = self.ListaRec.GetFocusedItem()
		if self.ListaRec.GetItem(indice, 31).GetText().strip() != '':
			
			self.extcli.extratocliente( self.ListaRec.GetItem(indice, 31).GetText(), self, Filial = self.fl, NomeCliente = self.ListaRec.GetItem(indice, 4).GetText(), fpagamento = '' )

		else:	alertas.dia(self,"CNPJ-CPF, Vazio...\n"+(" "*100),"Extrato do Cliente")

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 221:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 222:	sb.mstatus(u"  Procurar/Pesquisar DAV(s)",0)
		elif event.GetId() == 223:	sb.mstatus(u"  Consultar DAV,Visualizar, Enviar Email, Reimprimir",0)
		elif event.GetId() == 225:	sb.mstatus(u"  Emissão Posterior do DANFE",0)
		elif event.GetId() == 226:	sb.mstatus(u"  Acesso ao Menu de Caixa",0)
		elif event.GetId() == 227:	sb.mstatus(u"  Acesso ao Conta Corrente do Cliente",0)
		elif event.GetId() == 230:	sb.mstatus(u"  Extrato do cliente",0)
		elif event.GetId() == 231:	sb.mstatus(u"  Ocorrências de DAV/Comanda",0)
		elif event.GetId() == 232:	sb.mstatus(u"  Referências comerciais do cliente",0)
		elif event.GetId() == 234:	sb.mstatus(u"  Gerênciador de NFe,NFCe { Nota Fiscal Eletrônica e Nota Fiscal de Venda ao Consumidor }",0)
		elif event.GetId() == 235:	sb.mstatus(u"  Levantamento do Custo da Comanda",0)
		elif event.GetId() == 250:	sb.mstatus(u"  DANFE: Reenviar e Reimprimir",0)
		elif event.GetId() == 251:	sb.mstatus(u"  Vincular um cliente ao pedido [ apenas para pedidos com cliente não cadastrado ]",0)
		elif event.GetId() == 260:	sb.mstatus(u"  DAV-Vinculado a devolução [ Duplo click para abrir o dav ]",0)
		elif event.GetId() == 261:	sb.mstatus(u"  Acesso ao contas areceber [ Baixa de Títulos ]",0)
		elif event.GetId() == 262:	sb.mstatus(u"  Sangria: Retirada do caixa [ Dinheiro,Cheque,Cartão ]",0)
		elif event.GetId() == 263:	sb.mstatus(u"  Agrupar davs emitido em conjunto com outras filiais",0)

		if   self.cdevol.GetValue() == True and event.GetId() == 224:
			sb.mstatus(u"  Receber Devolução e emitir recibo",0)
			
		elif self.cdevol.GetValue() != True and event.GetId() == 224:
			
			sb.mstatus(u"  Receber DAV, Emitir Cupom Fiscal e/ou Nota Fiscal Eletrônica",0)

		if   self.cdevol.GetValue() == True and event.GetId() == 228:
			sb.mstatus(u"  Cancelamento da Devolução Recebida",0)
			
		elif self.cdevol.GetValue() != True and event.GetId() == 228:
			
			sb.mstatus(u"  Cancelamento do Ultimo Cupom Emitido",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Caixa: Recebimentos de DAVs",0)
		self.rcb.SetLabel("Recebimento")

		self._rc.SetForegroundColour('#000000')
		self.rcb.SetForegroundColour('#000000')

		event.Skip()

	def ecfcancela(self,event):

		if self.selecionarFilial() == False:	return
		
		indice = self.ListaRec.GetFocusedItem()
		NuDav  = self.ListaRec.GetItem(indice, 0).GetText()
		impres = self.ListaRec.GetItem(indice,45).GetText()

		rimpr = impres.split('|')
		vimpr = False
		for ri in rimpr:
			
			if ri[:1] == "T":	vimpr = True

	
		if self.ListaRec.GetItem(indice,17).GetText() == "2": # or self.ListaRec.GetItem(indice,48).GetText() == "2":

			if self.ListaRec.GetItem(indice,17).GetText() == "2":	alertas.dia(self.painel,u"Orçamento Nº: "+str(NuDav)+u"\n\nProcedimento não suportado\n"+(' '*70),"Caixa: Cancelamentos")
			return
			
		CancelaDavEcf.expedica = vimpr	
		cdc_frame=CancelaDavEcf(parent=self,id=-1)
		cdc_frame.Centre()
		cdc_frame.Show()
		
	def nfeatalho(self,event):

		indice = self.ListaRec.GetFocusedItem()
		NuDav  = self.ListaRec.GetItem(indice,0).GetText()

		if self.ListaRec.GetItem(indice,17).GetText() == "2":

			alertas.dia(self.painel,u"Orçamento: "+str(NuDav)+u"\n\nProcedimento não suportado\n"+(' '*70),"Caixa: Recebimento")
			return
	
		valorD = str(self._tp.GetValue())

		if valorD == '':

			alertas.dia(self,u"Selecione um dav para emissão da NFE...\n"+(" "*100),u"Caixa: Emissão de NFE")	
			_recebimento = False

		elif self.selecionarFilial() == False:	return

		else:
	
			passar = True
			if self.ListaRec.GetItem(indice,43).GetText() != 'S':
				alertas.dia(self,u"Cliente não cadastrado !!\n"+(" "*80),u"Caixa: Emissão de NFE")	
				passar = False
				
			if self.ListaRec.GetItem(indice,31).GetText() == '':
				alertas.dia(self,u"CPF-CNPJ do Cliente não cadastrado !!\n"+(" "*80),u"Caixa: Emissão de NFE")	
				passar = False

			if os.path.exists('srv/rnfe.cnf') !=True:
				alertas.dia(self,u"[rnfe.cnf] Arquivo de códigos de rejeição, não localizado\n"+(" "*90),u"DANFE Emissão")
				passar = False

			if passar == True:

				editadanfe.davNumero = self.ListaRec.GetItem(indice,0).GetText()
				editadanfe.dccliente = self.ListaRec.GetItem(indice,31).GetText()
				editadanfe.cdcliente = self.ListaRec.GetItem(indice,32).GetText()
				editadanfe.vinculado = self.ListaRec.GetItem(indice,54).GetText()
				
				editadanfe.identifca = 'POS'
				editadanfe.listaRece = ''
				editadanfe.listaQuan = ''
				editadanfe.idefilial = self.ListaRec.GetItem(indice,29).GetText()
				editadanfe.tiponfrma = ""
				editadanfe.dadostran = ''

				nfe_frame=editadanfe(parent=self,id=-1)
				nfe_frame.Centre()
				nfe_frame.Show()


	def acessconta(self,event):

		indice = self.ListaRec.GetFocusedItem()
		contacorrente.consulta = str(self.ListaRec.GetItem(indice,31).GetText())
		contacorrente.ccFilial = self.fl
		contacorrente.modulo   = "CX"
		
		ban_frame=contacorrente(parent=self,id=-1)
		ban_frame.Centre()
		ban_frame.Show()

	def vinculacl(self,event):

		""" Compartilhando funcao retaguarda.py"""
		
		if self.selecionarFilial() == False:	return
		if self.nfn.GetValue().strip():

			alertas.dia( self, "Cliente c/numero de nota fiscal preenchido...\n"+(" "*100),"Vincular cliente")
			return

		
		indice = self.ListaRec.GetFocusedItem()
		self.ndav = str(self.ListaRec.GetItem(indice,0).GetText())
		adiciona.TipoConsulta = '3'		
		adiciona.adFilial     = self.fl
		
		vnc_frame=adiciona(parent=self,id=-1)
		vnc_frame.Centre()
		vnc_frame.Show()
	
	def frecebimento(self,event):

		indice = self.ListaRec.GetFocusedItem()
		
		if str( self.ListaRec.GetItem(indice,0).GetText() ) == '':
			alertas.dia(self.painel,"Numero de DAV, Vazio...\n"+(' '*100),"Caixa: Listar Ocorrências de Recebimentos")
		
		else:

			formarecebimentos.dav = str( self.ListaRec.GetItem(indice,0).GetText() )
			formarecebimentos.mod = ""
			formarecebimentos.dev = self.cdevol.GetValue()
			formarecebimentos.ffl =  self.fl
			
			frcb_frame=formarecebimentos(parent=self,id=-1)
			frcb_frame.Centre()
			frcb_frame.Show()

	def impresDav(self,event):

		if self.cdevol.GetValue() == True:	__Dev = "DEV"
		else:	__Dev = ""
		
		indice    = self.ListaRec.GetFocusedItem()
		NumeroDav = self.ListaRec.GetItem(indice, 0).GetText()
		TipoDav   = self.ListaRec.GetItem(indice,17).GetText()

		cdDav = cdEma = ""
		if TipoDav == "1":	cdDav,cdEma = "605", "607"
		if TipoDav == "2":	cdDav,cdEma = "606", "608"

		if cdDav == "":	cdDav = "501"

		self.impress.impressaoDav( NumeroDav, self, True, True,  __Dev, "", servidor =  self.fl, codigoModulo = cdDav, enviarEmail = cdEma )
		#self.impress.impressaoDav( NumeroDav, self, True, False, __Dev, "", servidor =  self.fl, codigoModulo = cdDav, enviarEmail = cdEma )

	def cusTosDav(self,event):
		
		if self.ListaRec.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista vazia, sem registros para prosseguir!!\n","Caixa: Custo do DAV")
		else:
			
			if self.cdevol.GetValue() == True:	__Dev = "DEV"
			else:	__Dev = ""
			
			indice    = self.ListaRec.GetFocusedItem()
			NumeroDav = self.ListaRec.GetItem(indice, 0).GetText()
			TipoDav   = self.ListaRec.GetItem(indice,17).GetText()

			cdDav = cdEma = ""
			if TipoDav == "1":	cdDav,cdEma = "605", "607"
			if TipoDav == "2":	cdDav,cdEma = "606", "608"

			if cdDav == "":	cdDav = "501"

			self.impress.impressaoDav( NumeroDav, self, True, True, __Dev, "CUS", servidor =  self.fl, codigoModulo = cdDav, enviarEmail = cdEma )
			#self.impress.impressaoDav( NumeroDav, self, True, False,__Dev, "CUS", servidor =  self.fl, codigoModulo = cdDav, enviarEmail = cdEma )
		
	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		indi = self.ListaRec.GetFocusedItem()
		if indi >=0:

			daTa = datetime.datetime.strptime(str(self.ListaRec.GetItem(indi,2).GetText()), "%d/%m/%Y").date()
			hoje = datetime.datetime.now().date()
		
			""" Controla icone do vincular cliente """
			if hoje > daTa:	self.vincular.Disable()
			else:	self.vincular.Enable()
				
		if keycode == wx.WXK_ESCAPE:	self.voltar(wx.EVT_BUTTON)
		if controle !=None and controle.GetId() == 300:

			indice  = self.ListaRec.GetFocusedItem()
			daTaN = ''
			daTaE = ''
			ProTo = ''
			usarN = ''
			usarE = ''
			caixa = ''
			vincu = ''
			Tipop = "DAV-Pedido"
			if self.ListaRec.GetItem(indice,17).GetText() == '2':	Tipop = "DAV-Orçamento"
			if self.cdevol.GetValue() == True:	Tipop = u"DAV-Devolução"
			
			if self.ListaRec.GetItem(indice,48).GetText() == "1":	Tipop = "DAV-Pedido [ Simples Faturamento-Entrega Ftutura ]"
			if self.ListaRec.GetItem(indice,48).GetText() == "2":	Tipop = "DAV-Pedido [ Entrega Futura ]"
			self.tipopd.SetLabel("{ "+ Tipop +" }")
			
			if self.ListaRec.GetItem(indice,50).GetText() !='':	self.porCom.SetLabel("Parceiro-Comprador/Portador\n"+str( self.ListaRec.GetItem(indice,50).GetText() ))
			else:	self.porCom.SetLabel("")

			if self.ListaRec.GetItem(indice,19).GetText() !='' and self.ListaRec.GetItem(indice,10).GetText() !='':
				caixa = self.ListaRec.GetItem(indice,19).GetText()+" "+self.ListaRec.GetItem(indice,10).GetText()+" "+self.ListaRec.GetItem(indice,11).GetText()+" "+self.ListaRec.GetItem(indice,12).GetText()

			self.nfn.SetValue(self.ListaRec.GetItem(indice,33).GetText())
			if self.ListaRec.GetItem(indice,35).GetText() !='':

				_emi  = self.ListaRec.GetItem(indice,35).GetText().split(' ')

				daTaN = format(datetime.datetime.strptime(_emi[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+_emi[1]
				if len( _emi ) >=3:	ProTo = _emi[2]
				if len( _emi ) >=4:	usarN = _emi[3]

			if self.ListaRec.GetItem(indice,37).GetText() !='':

				_emi = self.ListaRec.GetItem(indice,37).GetText().split(' ')
				daTaE = format(datetime.datetime.strptime(_emi[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+_emi[1]
				usarE = _emi[2]

			self._cx.SetLabel(caixa)
			self.nfe.SetValue(daTaN)
			self.nfp.SetValue(ProTo)
			self.unf.SetValue(usarN)			

			self.ece.SetValue(daTaE)

			self.nfc.SetValue(self.ListaRec.GetItem(indice,34).GetText()) #->[ Chave NFE ]
			self.ecn.SetValue(self.ListaRec.GetItem(indice,54).GetText()) #->[ Orcamento vinculado p/emissao da nfe ]
			self.vin.SetValue(self.ListaRec.GetItem(indice,42).GetText())
			self.uec.SetValue(self.ListaRec.GetItem(indice,46).GetText())
			self._us.SetValue(self.ListaRec.GetItem(indice,21).GetText())
			self._vd.SetValue(self.ListaRec.GetItem(indice,16).GetText())
			self._pg.SetValue(self.ListaRec.GetItem(indice,22).GetText())
			self._rc.SetValue(self.ListaRec.GetItem(indice,23).GetText())

			self._tp.SetValue(self.ListaRec.GetItem(indice, 6).GetText())
			self._fr.SetValue(self.ListaRec.GetItem(indice, 7).GetText())
			self._ac.SetValue(self.ListaRec.GetItem(indice, 8).GetText())
			self._dc.SetValue(self.ListaRec.GetItem(indice, 9).GetText())
			self._tb.SetValue(self.ListaRec.GetItem(indice,20).GetText())
			self._td.SetValue(self.ListaRec.GetItem(indice, 5).GetText())
			self._vr.SetValue(self.ListaRec.GetItem(indice,24).GetText())
			self.tro.SetValue(self.ListaRec.GetItem(indice,25).GetText())
			self._tr.SetValue(self.ListaRec.GetItem(indice,26).GetText())
			self._cr.SetValue(self.ListaRec.GetItem(indice,27).GetText())
			self._pc.SetValue(self.ListaRec.GetItem(indice,28).GetText())

			self.vinnfe.SetLabel( u"Redução "+str( self.ListaRec.GetItem(indice,55).GetText() )+u"%\nOrçamento\nvinculado-NFe:" )

			if self.ListaRec.GetItem(indice,22).GetText()[:2] == "12":

				self.pgTo.SetLabel("Receber\nLocal")
				self.pgTo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
				self.pgTo.SetForegroundColour('#C13A3A')
				self.pgTo.SetPosition((520, 478)) 
				
				self._pg.SetForegroundColour('#C13A3A')
				self._pg.SetValue(self.ListaRec.GetItem(indice,41).GetText())
				
				fpg = self.ListaRec.GetItem(indice,49).GetText().split("|")
				if len( fpg ) == 2 and fpg[0].split(";")[0].split("-")[0] == "12":	self._pg.SetValue(fpg[0].split(";")[3])
					

			else:
				self.pgTo.SetLabel("Pagamento:")
				self.pgTo.SetPosition((520, 485)) 
				self.pgTo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
				self.pgTo.SetForegroundColour('#000000')

				self._pg.SetForegroundColour('#000000')

			
			if self.ListaRec.GetItem(indice,38).GetText() !='':
				
				nfec = self.ListaRec.GetItem(indice,38).GetText().split(' ')
				nfec = format(datetime.datetime.strptime(nfec[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+nfec[1]+' '+nfec[3]
				self.nfecan.SetLabel("NFe-Cancelado: "+nfec)

			elif self.ListaRec.GetItem(indice,40).GetText() !='':

				nfec = self.ListaRec.GetItem(indice,40).GetText().split(' ')
				if nfec[2] == 'NORMAL':	nfec = u"[ Normal ] Modo: "+format(datetime.datetime.strptime(nfec[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+nfec[1]+' '+nfec[3]
				else:
					
					if self.cdevol.GetValue() == True:	nfec = u"Devolução: "+format(datetime.datetime.strptime(nfec[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+nfec[1]+' '+nfec[2]
					else:	nfec = "ECF-Cupom: "+format(datetime.datetime.strptime(nfec[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+nfec[1]+' '+nfec[2]+' '+nfec[3]+' '+nfec[4]

				if self.ListaRec.GetItem(indice,39).GetText() == '2':	nfec = ( "[ Estorno ] "+ nfec)
				else:	nfec = ( "[ Cancelado ] "+ nfec)
				
				self.nfecan.SetLabel(nfec)	

			else:	self.nfecan.SetLabel("{ Informações ECF, NFe, NFCe }")

			if self.ListaRec.GetItem(indice,44).GetText() != '':
				self.vda.SetLabel('[Autorizada]')
			else:	self.vda.SetLabel('')

			_idFil = "DAV: {"+self.ListaRec.GetItem(indice,29).GetText()+"} Cliente: { "+self.ListaRec.GetItem(indice,32).GetText()+"-"+self.ListaRec.GetItem(indice,31).GetText()+" }"
			self.filial.SetLabel(_idFil)

		self.nfn.SetBackgroundColour('#E5E5E5')	
		self.nfe.SetBackgroundColour('#E5E5E5')	
		self.nfc.SetBackgroundColour('#E5E5E5')	
		self.nfp.SetBackgroundColour('#E5E5E5')	
		
		if self.ListaRec.GetItem(indi,51).GetText().split('-')[0] == "1":

			self.nfn.SetBackgroundColour("#D39393")
			self.nfe.SetBackgroundColour("#D39393")
			self.nfc.SetBackgroundColour("#D39393")
			self.nfp.SetBackgroundColour("#D39393")

		"""  Partilha  """
		icI = icF = icD = icO = Decimal("0.00")
		if self.ListaRec.GetItem(indi,52).GetText() != "":

			vlr = self.ListaRec.GetItem(indi,52).GetText().split(";")
			icF,icD,icO = Decimal(vlr[0]),Decimal(vlr[2]),Decimal(vlr[1])
			if icD !=0:	icI = Decimal( self.ListaRec.GetItem(indi,53).GetText() )
			
		self.paInte.SetValue(format(icI,','))
		self.paFund.SetValue(format(icF,','))
		self.paDesT.SetValue(format(icD,','))
		self.paOrig.SetValue(format(icO,','))

		if self.rfilial.GetValue().strip() == "" and self.ListaRec.GetItem(indi,29).GetText() != "":

			self.fl = self.ListaRec.GetItem(indi,29).GetText().strip()
			self.configuracaoFiliais()

	def voltar(self,event):
		
		login.acbrEsta = ""
		self.parente.ToolBarra.EnableTool(503,True)
		self.Destroy()
		
	def selecionar(self,event):

		conn = sqldb()
		sql  = conn.dbc("Caixa: Consulta de DAVs", fil =  self.fl, janela = self.painel )

		if sql[0] == True:
			
				
			rTQ,per = infNFs.informeNFes( sql, self.fl )
			self.cTperi.SetLabel(u"Contigência-Inutilização\nPeriodo: "+per)

			self.cTInuT.SetValue(str( rTQ[0] ))
			self.cTfInT.SetValue(str( rTQ[4] ))
			self.cTuInT.SetValue(str( rTQ[2] ))

			self.cTconT.SetValue(str( rTQ[1] ))
			self.cTfcoT.SetValue(str( rTQ[5] ))
			self.cTucoT.SetValue(str( rTQ[3] ))

			self.cTperi.SetForegroundColour("#215A92")
				
			_mensagem = mens.showmsg("Consultando DAVs!!\nAguarde...", filial =  self.fl )

			inicial = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			final   = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
#			numero.cdata( self.dindicial.GetValue().FormatDate() , 1, vr = 0 )

			#inicial = numero.cdata( self.dindicial.GetValue().FormatDate(), 1 )
			#final   = numero.cdata( self.datafinal.GetValue().FormatDate(), 1 )
			consul  = self.consultar.GetValue()

			_cmp = self.consultar.GetValue().upper().split(':')
			_leT = ''
			_pes = self.consultar.GetValue().upper()
			_ven = self.vendedor.GetValue().upper()

			if len(_cmp) == 2:	_leT, _pes = _cmp[0].upper(), _cmp[1]
	
			_pes = "DEV"+_pes.zfill(10) if self.cdevol.GetValue() and _pes !="" and _pes.isdigit() else _pes
			if _pes[:3] == "DEV":	_leT = ''

			pesqui  = consul[:2].upper()
			hoje    = datetime.datetime.now().strftime("%Y/%m/%d")
			caixa = "SELECT * FROM cdavs WHERE cr_edav >='"+str( inicial )+"' and cr_edav <='"+str( final )+"' ORDER BY cr_ndav,cr_edav"
			
			if self.pesqperio.GetValue() == False and _pes!='':	caixa = "SELECT * FROM cdavs WHERE cr_regi!=0 ORDER BY cr_ndav,cr_edav"
			
			if self.Davss.GetValue() == True:	caixa = caixa.replace("ORDER BY","and cr_tipo='1' ORDER BY")
			if self.Aberto.GetValue() == True:	caixa = caixa.replace("ORDER BY","and cr_tipo='1' and ( cr_reca='2' or cr_reca='' ) ORDER BY")
			if self.Orcam.GetValue() == True:	caixa = caixa.replace("ORDER BY","and cr_tipo='2' ORDER BY")
			if self.dcance.GetValue() == True:	caixa = caixa.replace("ORDER BY","and cr_tipo='1' and cr_reca='3' ORDER BY")
			if self.dcance.GetValue() == True:	caixa = caixa.replace("cr_edav","cr_ecan")

			if self.rVendedo.GetValue() == True and _ven!='':	caixa = caixa.replace("ORDER BY","and cr_nmvd='"+_ven+"' ORDER BY")
			if self.rCaixass.GetValue() == True and _ven!='':	caixa = caixa.replace("ORDER BY","and cr_urec='"+_ven+"' ORDER BY")

			if _pes!='' and _leT=='' and _pes.isdigit()==True:	caixa = caixa.replace("ORDER BY","and cr_ndav like '"+_pes.zfill(13)+"%' ORDER BY")
			if _pes!='' and _leT=='' and _pes[:3] == "DEV":	caixa = caixa.replace("ORDER BY","and cr_ndav like '"+_pes.zfill(13)+"%' ORDER BY")
			
			"""   So verifica se o numero nao tem p/P para pesquisa no nome   """
			if len( consul.upper().split('P') ) != 2 or consul.upper().split('P')[0].isdigit() != True:

				if _pes!='' and _leT=='' and _pes.isdigit()==False and _pes[:3] !="DEV":	caixa = caixa.replace("ORDER BY","and cr_nmcl like '"+_pes+"%' ORDER BY")

			if _pes!='' and _leT=='P':	caixa = caixa.replace("ORDER BY","and cr_nmcl like '%"+_pes+"%' ORDER BY")
			if _pes!='' and _leT=='F':	caixa = caixa.replace("ORDER BY","and cr_facl like '"+ _pes+"%' ORDER BY")
			if _pes!='' and _leT=='N':	caixa = caixa.replace("ORDER BY","and cr_nota like '"+ _pes+"%' ORDER BY")
			if _pes!='' and _leT=='C':	caixa = caixa.replace("ORDER BY","and cr_docu like '"+ _pes+"%' ORDER BY")
			if _pes!='' and _leT=='O':	caixa = caixa.replace("ORDER BY","and cr_cupo like '%"+_pes+"%' ORDER BY")

			if self.sfaTu.GetValue() == True:	caixa = caixa.replace("WHERE","WHERE cr_tfat='1' and")
			if self.efuTu.GetValue() == True:	caixa = caixa.replace("WHERE","WHERE cr_tfat='2' and")
			if self.lsTcg.GetValue() == True:	caixa = caixa.replace("WHERE","WHERE cr_cont like '1-%' and")
			if self.lsTin.GetValue() == True:	caixa = caixa.replace("WHERE","WHERE cr_nota!='' and cr_tnfs='2' and ( cr_nfem='' or cr_chnf='' ) and")

			""" Pesquisa pelo valor """
			if _pes[:1] == "$" and _pes[1:].split('.')[0].isdigit() == True:	caixa = "SELECT * FROM cdavs WHERE cr_tnot like '"+str(_pes[1:])+"%' ORDER BY cr_edav"
			if len( consul.upper().split('P') ) == 2 and consul.upper().split('P')[0].isdigit() == True:	caixa = caixa.replace("ORDER BY","and cr_ecfb='"+str( consul.upper().split('P')[0].zfill(12)+"P" )+"' ORDER BY")
				
			if self.rfilial.GetValue() !="":	caixa = caixa.replace("ORDER BY","and cr_inde='"+str(  self.fl )+"' ORDER BY")
			if self.cdevol.GetValue() == True:	caixa = caixa.replace("cdavs","dcdavs")

			procura = sql[2].execute(caixa)
			_result = sql[2].fetchall()
			
			_vinculad = u"{ davs vinculados de devolucão'}\n" if self.cdevol.GetValue() else ""
			_mensagem = mens.showmsg(_vinculad+"Consultando DAVs!!\nNumero de registros: "+str( procura )+"\n\nAguarde...", filial =  self.fl )
			_registros = 0
			relacao    = {}

			indice = 0
			for i in _result:

				""" Busca a Filial do Vinculado """
				devId = ""
				if i[78] !=None and i[78] !="" and self.cdevol.GetValue():

					pDev = "SELECT cr_inde FROM cdavs WHERE cr_ndav='"+str( i[78] )+"'"
					if sql[2].execute( pDev ) !=0:	devId = sql[2].fetchall()[0][0]
					
				_DTRec = ''
				_DTEmi = ''
				_DTEnt = ''
				_ECFem = ''
				_Impre = str( i[54] )
				_PreRe = ''
				_ComPo = ''
				_conTg = ''
				_parTi = ''
				_icmsv = '0.00'

				if i[11]  !=None:	_DTEmi = i[11].strftime("%d/%m/%Y")
				if i[13]  !=None:	_DTRec = i[13].strftime("%d/%m/%Y")
				if i[21]  !=None:	_DTEnt = i[21].strftime("%d/%m/%Y")
				if i[85]  !=None and i[85] !='':	_Impre = 'I-'+str( i[54] )
				if i[95]  !=None:	_PreRe = i[95]
				if i[100] !=None:	_conTg = i[100]
				if i[110] !=None:	_parTi = i[110]
				if i[26]  !=None:	_icmsv = i[26]

				if i[102] !=None:	_ComPo = str( i[103] )+'-'+str( i[102] )
				Tributos  = format( ( i[28] +i[29] + i[30] ),',')

				relacao[_registros] = str(i[2]),\
				_Impre,\
				_DTEmi,\
				i[12],\
				i[4],\
				format(i[37],','),\
				format(i[36],','),\
				format(i[23],','),\
				format(i[24],','),\
				format(i[25],','),\
				i[10],\
				_DTRec,\
				i[14],\
				_DTEnt,\
				i[22],\
				i[1],\
				i[43]+'-'+i[44],\
				i[41],\
				i[45],\
				i[46],\
				Tributos,\
				i[9],\
				i[40],\
				i[47],\
				format(i[48],','),\
				format(i[49],','),\
				format(i[53],','),\
				format(i[50],','),\
				format(i[51],','),\
				i[54],\
				i[55],\
				i[39],\
				i[3],\
				i[8],\
				i[73],\
				i[15],\
				i[6]+'-'+i[67],\
				i[17],\
				i[16],\
				i[74],\
				i[18],\
				i[83],\
				i[78],\
				i[75],\
				i[81],\
				i[85],\
				i[92],\
				devId,\
				i[98],\
				_PreRe,\
				_ComPo,\
				_conTg,\
				_parTi,\
				_icmsv,\
				i[112],\
				str( i[113] )
				
				_registros +=1
				indice +=1

			conn.cls(sql[1])

			if self.cdevol.GetValue() !=True:	self.ListaRec.SetBackgroundColour('#BFBFBF')
		
			RcListCtrl.itemDataMap  = relacao
			RcListCtrl.itemIndexMap = relacao.keys()
			RcListCtrl.TipoFilialRL = nF.rF( cdFilial = self.fl )
	
			self.ListaRec.SetItemCount(procura)
			self.ocorre.SetLabel("{"+str(procura)+"}")
			
			self.vendedor.SetValue('')

			del _mensagem
	
	def ecfcaixa(self,event):

		"""  Click Duplo """
		if self.fdbl:

			alertas.dia(self.painel,u"Não utilize duplo-click p/recebimento!!\n"+(' '*80),"Caixa: Recebimentos")
			return

		if self.ListaRec.GetItemCount() == 0:
			
			alertas.dia(self.painel,"Sem registros para recebimento!!\n"+(' '*80),"Caixa: Recebimentos")
			return
			
		indice = self.ListaRec.GetFocusedItem()
		NuDav  = self.ListaRec.GetItem(indice, 0).GetText()
		NuDav  = self.ListaRec.GetItem(indice, 0).GetText()
		clresu = ''  
		
		self.ndav = self.ListaRec.GetItem(indice,0).GetText()
		if self.selecionarFilial() == False:	return
		
		""" Recebimento de DAVS """
		if self.ListaRec.GetItem(indice,48).GetText() == "2":

			alertas.dia(self.painel,u"DAV Nº: "+str( NuDav )+u"\n\nProcedimento não suportado\n\n{ Pedido com marca de entrega futura de simples faturamento }\n"+(' '*120),"Caixa: Recebimento")
			return

		if self.cdevol.GetValue() == False:
		
			if self.ListaRec.GetItem(indice,17).GetText() == "2":
				alertas.dia(self.painel,u"Orçamento: "+str(NuDav)+u"\n\nProcedimento não suportado\n"+(' '*70),"Caixa: Recebimento")
				return

			LanDav = str(self.ListaRec.GetItem(indice,2).GetText())
			valorD = str(self._tp.GetValue())
			dTHoje = datetime.datetime.now().strftime("%d/%m/%Y")

			ld = datetime.datetime.strptime(LanDav, "%d/%m/%Y").date()
			hj = datetime.datetime.now().date()
			_recebimento = True

			if NuDav  == '':	_recebimento = False

			if valorD == '' and _recebimento == True:

				alertas.dia(self,"Selecione um dav para receber...\n"+(" "*100),"Caixa: Recebimentos de Dav(s)")
				_recebimento = False

			if ld < hj and _recebimento == True:

				ndias = ( hj - ld ).days
				if ndias == 1:	alertas.dia(self,"Recebimento com data retroagido {  D + 1 }...\n"+(" "*100),"Caixa: Recebimentos de Dav(s)")

				if ndias  > 1:
					alertas.dia(self,"Recebimento com data retroagido { Acima do limite }...\n"+(" "*100),"Caixa: Recebimentos de Dav(s)")
					_recebimento = True
				
			if _recebimento == True:
				
				valor_vinculado = ''

				conn = sqldb()
				sql  = conn.dbc("Caixa: Recebimento", fil = self.fl, janela = self.painel )

				if sql[0]:

					"""  DAV-Vinculado meia nota  """
					if self.ecn.GetValue() and sql[2].execute("SELECT cr_tnot FROM cdavs WHERE cr_ndav='"+ self.ecn.GetValue() +"'"):	valor_vinculado = str( int( self.ecn.GetValue() ) )+' { '+format( sql[2].fetchone()[0],',')+' }'

					_rT = sql[2].execute("SELECT * FROM cdavs WHERE cr_ndav='"+str( NuDav )+"'")
					listaDav = sql[2].fetchall()

					if listaDav[0][75] == "S" and listaDav[0][3] !='': #-: Cliente cadastrado

						cl = "SELECT cl_pgfutu,cl_endere,cl_bairro,cl_cidade,cl_pgtofu,cl_blcred, cl_docume FROM clientes WHERE cl_codigo='"+str( listaDav[0][3] )+"'"
						if sql[2].execute(cl) !=0:	clresu = sql[2].fetchall()
						
					conn.cls(sql[1])

					""" Verica se Ja foi emitido o DANFE"""
					if listaDav[0][73] != '' or listaDav[0][6] !='' or listaDav[0][74] == '1' or listaDav[0][74] == '3':

						cooEmissao = ''
						nfeEmissao = ''
						dvrecebido = ''

						if listaDav[0][74] == '1' and listaDav[0][13] !=None:	dvrecebido  = "Recebimento: "+     format(listaDav[0][13],"%d/%m/%Y")+' '+str(listaDav[0][14])+'\nCaixa: '+str(listaDav[0][10])
						if listaDav[0][74] == '3' and listaDav[0][13] !=None:	dvrecebido  = "Recebimento: "+     format(listaDav[0][13],"%d/%m/%Y")+' '+str(listaDav[0][14])+'\nCaixa: '+str(listaDav[0][10])
						if listaDav[0][74] == '3' and listaDav[0][19] !=None:	dvrecebido += "\n\nCancelamento: "+format(listaDav[0][19],"%d/%m/%Y")+' '+str(listaDav[0][20])+'\nUsuario: '+str(listaDav[0][45])
						
						if listaDav[0][17] !='':

							cooemi     = listaDav[0][17].split(' ')
							cooEmissao = format(datetime.datetime.strptime(cooemi[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+cooemi[1]+' '+cooemi[2]

						if listaDav[0][15] !='':

							nfeemi     = listaDav[0][15].split(' ')
							nfeEmissao = format(datetime.datetime.strptime(nfeemi[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+nfeemi[1]+'\nProtocolo: '+nfeemi[2]

						alertas.dia(self.painel,u"DAV-Pedido Recebido\n\n"+dvrecebido+"\n\nCOO...: "+str(listaDav[0][6])+u"\nEmissão: "+str(cooEmissao)+\
						"\nECF Cancelado: "+str(listaDav[0][18])+"\n\nNFe: "+str(listaDav[0][8])+u"\nEmissão: "+nfeEmissao+"\nCHAVE: "+str(listaDav[0][73])+\
						"\nNFE Cancelado: "+str(listaDav[0][16])+'\n'+(' '*100),u"Caixa: Recebimento { NFE-COO Emitida }")
		
					if listaDav[0][74] == "2" or listaDav[0][74] == "":	_rcb = True
					if listaDav[0][74] == '1' or listaDav[0][74] == '3':	_rcb = False
						
					if _rT != 0 and _rcb == True:

						pagamento.result  = listaDav
						pagamento.clresul = clresu
						pagamento.valor_vinculado = valor_vinculado

						self.CupomFis.Enable( False )
						pag_frame=pagamento(parent=self,id=-1)
						pag_frame.Centre()
						pag_frame.Show()

						self.CupomFis.Enable( True )

		elif self.cdevol.GetValue() == True: #->[ Recebimento de Devolucao ]

			LanDav = str(self.ListaRec.GetItem(indice,2).GetText())
			valorD = str(self._tp.GetValue())
			dTHoje = datetime.datetime.now().strftime("%d/%m/%Y")

			if valorD == '' and NuDav != '':

				alertas.dia(self,u"Selecione devolução para receber...\n"+(" "*100),u"Caixa: Recebimentos de Devoluções")	
				return
			
			elif valorD != '' and NuDav != '':
				
				conn = sqldb()
				sql  = conn.dbc("Devolução", fil = self.fl, janela = self.painel )

				if sql[0] == True: 
				
					_dev = sql[2].execute("SELECT * FROM dcdavs WHERE  cr_ndav='"+str(self.ndav)+"'")
					if _dev == 0:

						conn.cls(sql[1])
						alertas.dia(self.painel,u"Devolução: "+str(self.ndav)+u", não localizada...\n"+(' '*70),u"Caixa: Recebimento de Devolução")
						self.Destroy()

					else:

						self.resul = sql[2].fetchall()
						conn.cls(sql[1])

						if self.resul[0][10] !='':
							
							_edv= str(format(self.resul[0][11],'%d/%m/%Y'))+' '+str(self.resul[0][12])
							_emi= "\nCaixa............: "+str(self.resul[0][10].upper())+u"\nEmissão.......: "+_edv+"\nRecebimento: "+str(format(self.resul[0][13],'%d/%m/%Y'))+' '+str(self.resul[0][14])
								
							alertas.dia(self.painel,u"Devolução recebida!!\n\n"+_emi+'\n'+(' '*80),u'Caixa: Recebimento de Devolução')

						elif self.resul[0][74] == '3':

							rc = str(self.resul[0][18]).split(' ')
							rc = format(datetime.datetime.strptime(rc[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+rc[1]+' '+rc[2]
							alertas.dia(self.painel,u"Devolução cancelada!!\n\nCancelamento: "+rc+'\n'+(' '*90),u'Caixa: Recebimento de Devolução')

						else:
							
							dev_frame=pgdevolucao(parent=self,id=-1)
							dev_frame.Centre()
							dev_frame.Show()
				
	def selecionarFilial(self):

		indice = self.ListaRec.GetFocusedItem()

		if self.fl.strip() == "":

			alertas.dia(self.painel,"Selecione uma filial ou um DAV p/Continuar!!\n"+(' '*120),"Caixa: Recebimento")
			return False

		if self.rfilial.GetValue().strip() == "" and self.ListaRec.GetItem(indice,29).GetText() != "":
			
			self.fl = self.ListaRec.GetItem(indice,29).GetText().strip()
			self.configuracaoFiliais()
		
		return True
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"CAIXA Recebimentos e Controles", 0, 625, 90)

		""" Boxes """
		""" Dados da NFE-ECF"""
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(0,    0,  965,  60, 3) #-: Dados da NFE
		dc.DrawRoundedRectangle(12,  407, 495, 163, 3) #-: Consulta
		dc.DrawRoundedRectangle(12,  570, 495,  55, 3) #-: Pesuisar
		dc.DrawRoundedRectangle(515, 430, 450, 195, 3) #-: Informacoes
		dc.DrawRoundedRectangle(518, 525, 221,  95, 3) #-: Recebimento no Caixa
		dc.DrawRoundedRectangle(312, 436, 192, 122, 3) #-: Atalhos
		#dc.DrawRoundedRectangle(0,   406, 965,  22, 3) #-: Filtro Simples Faturamento Etc...
		dc.DrawRoundedRectangle(615, 362, 350,  42, 3) #-: Atalhos
		
		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText( "Dados da NFE-ECF", 2,2, 0)
		dc.DrawRotatedText(u"Informações", 517,432, 0)
		dc.DrawRotatedText( "Recebimento no Caixa", 520,527, 0)
		dc.DrawRotatedText( "Atalhos", 315,439, 0)
		
class RcListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}
	TipoFilialRL = ""

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		_clientes = recebimentos.clientes
		RcListCtrl.itemDataMap  = _clientes
		RcListCtrl.itemIndexMap = _clientes.keys()  
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self._frame = parent

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		
		self.attr1.SetBackgroundColour("#CCCCCC")
		self.attr2.SetBackgroundColour("#F4F4E7")
		self.attr3.SetBackgroundColour("#DFC5C9")

		self.InsertColumn(0, u'Nº D A V',   format=wx.LIST_ALIGN_LEFT,width=145)
		self.InsertColumn(1, u'P-Filial  ', format=wx.LIST_ALIGN_LEFT,width=65)
		self.InsertColumn(2, u'Emissão',    format=wx.LIST_ALIGN_LEFT,width=85)
		self.InsertColumn(3, u'Horario',               width=65)
		self.InsertColumn(4, u'Descrição dos Clientes', width=460)
		self.InsertColumn(5, u'Valor',     format=wx.LIST_ALIGN_LEFT,width=130)

		self.InsertColumn(6, u'SubTotal',       format=wx.LIST_ALIGN_LEFT,width=113)
		self.InsertColumn(7, u'Frete',          format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(8, u'Acrescimo',      format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(9, u'Desconto',       format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(10,u'Caixa',             width=160)
		self.InsertColumn(11,u'DATA',              width=80)
		self.InsertColumn(12,u'Horario',           width=65)
		self.InsertColumn(13,u'Entrega',           width=80)
		self.InsertColumn(14,u'Horario',           width=80)
		self.InsertColumn(15,u'Filial',            width=50)
		self.InsertColumn(16,u'Vendedor',          width=160)
		self.InsertColumn(17,u'Tipo',              width=40)
		self.InsertColumn(18,u'Cancelamento',      width=120)
		self.InsertColumn(19,u'CódigoCaixa',      width=90)
		self.InsertColumn(20,u'Tributos',          width=160)
		self.InsertColumn(21,u'Usuário',           width=160)
		self.InsertColumn(22,u'Pagamento',         width=160)
		self.InsertColumn(23,u'Recebimento',       width=160)
		self.InsertColumn(24,u'ValorRecebido',     width=160)
		self.InsertColumn(25,u'Troco',             width=100)
		self.InsertColumn(26,u'Rateio Troco',      width=100)
		self.InsertColumn(27,u'Rateio C/C',        width=100)
		self.InsertColumn(28,u'PGTo Credito',      width=100)
		self.InsertColumn(29,u'ID-Filial DAV',     width=120)
		self.InsertColumn(30,u'ID-Filial Cliente', width=160)
		self.InsertColumn(31,u'CPF-CNPJ',          width=160)
		self.InsertColumn(32,u'Código Cliente',   width=160)
		self.InsertColumn(33,u'NFE-Numero',        width=100)
		self.InsertColumn(34,u'NFE-Chave',         width=400)
		self.InsertColumn(35,u'NFE-Emissão',       width=350)
		self.InsertColumn(36,u'COO-CCF',           width=100)
		self.InsertColumn(37,u'ECF-Emissão',       width=350)
		self.InsertColumn(38,u'NFE-Cancelado',     width=350)
		self.InsertColumn(39,u'1-Recebido 2-Estornado 3-Cancelado',     width=350)
		self.InsertColumn(40,u'ECF-Cancelado',     width=350)
		self.InsertColumn(41,u'Receber Local',     width=200)
		self.InsertColumn(42,u'Vinculo',           width=110)
		self.InsertColumn(43,u'Cadastrado',        width=110)
		self.InsertColumn(44,u'Autorizações',      width=200)
		self.InsertColumn(45,u'Impressões',        width=200)
		self.InsertColumn(46,u'ECF Fabricante',    width=200)
		self.InsertColumn(47,u'Filial Vinculado ao DAV-Devolução', width=200)
		self.InsertColumn(48,u'Simples Faturamento-Entrega', width=200)
		self.InsertColumn(49,u'Pre-Recebimento',   width=200)
		self.InsertColumn(50,u'Comprador/Portador',width=200)
		self.InsertColumn(51,u'Contigencia',width=200)
		self.InsertColumn(52,u'Partilha',width=200)
		self.InsertColumn(53,u'Partilha-ICMS',width=200)
		self.InsertColumn(54,u'Orçamento vinculado p/emissao da nfe',width=300)
		self.InsertColumn(55,u'Percentual de redução',width=300)
			
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			estor=self.itemDataMap[index][39]

			if   estor.strip() == "2":	return self.attr2 # Estorno
			elif estor.strip() == "3":	return self.attr3 # Cancelado

			if   item % 2:
				#if self.TipoFilialRL == "T":	return self.attr4
				return self.attr1
			else:
				return None

		else:	return None
		
	def OnGetItemImage(self, item):

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			
			genre = self.itemDataMap[index][0]
			orcam = self.itemDataMap[index][17] #->[ Orcamento - Pedido ]
			caixa = self.itemDataMap[index][10] #-->[ Caixa Recebeu ]
			cance = self.itemDataMap[index][18] #->[ Cancelamento ]
			estor = self.itemDataMap[index][39] #->[ Estarnado ]
			fuTur = self.itemDataMap[index][48] #->[ Simples Faturamento-Entrega Futura ]

			if fuTur.strip() !='' and fuTur.strip() == '2':	return self.e_tra
			if estor.strip() !='' and estor.strip() == '2':	return self.e_est
			if orcam == "1" and cance !='':	return self.i_idx
			if fuTur.strip() !='' and fuTur.strip() == '1':	return self.e_sim
			
			if   orcam == "1" and caixa !='':	return self.w_idx
			elif orcam == "1" and caixa =='':	return self.e_idx
			elif orcam == "2":	return self.i_orc
			else:	return self.w_idx
		
		else:	return self.w_idx
		
	def GetListCtrl(self):	return self


class pagamento(wx.Frame):

	result  = ''
	clresul = ''
	valor_vinculado = ''

	def __init__(self, parent,id):

		#self.pgFil = parent.fl

		"""  Filial do dav selecioando  """
		self.pgFil = parent.ListaRec.GetItem( parent.ListaRec.GetFocusedItem() ,29 ).GetText()
		
		self.valorSDav = self.result[0][37]
		self.valorDav  = format( self.result[0][37],',' )
		self.davn      = self.result[0][2]
		mkn            = wx.lib.masked.NumCtrl
		self.Trunca    = truncagem()
		self.parente   = parent
		self.documento = self.result[0][39]
		vlCreditoConta = Decimal('0.00')
		vlDebitoRecebe = Decimal('0.00')
		self.valcnpj   = numeracao()
		self.cdevol    = self.parente.cdevol
		self.relpag    = formasPagamentos()
		self.md        = "2" #--: Usado para edicao do cadastro do cliente [1-Acesso pelo modulo do cliente 2-acesso pelo recebimento de caixa ]
		self.fPagamec  = "" #---: Formas de Pagamentos Vinculadas ao ECF
		self._cnpj_cpf = False
		self.grVencime = "" #---: Utilizado p/Gravar a da de vencimento da parcela

		self.cResgaTe = False
		if len( login.filialLT[ self.pgFil ][35].split(";") ) >= 23 and login.filialLT[ self.pgFil ][35].split(";")[22] == "T":	self.cResgaTe = True

		self.vda       = self.result[0][82].strip() #-:Historico das Autorizações
		if self.result[0][95] !=None and self.result[0][95] !="" and ( len( self.result[0][95].split('|') ) -1 ) > 1:	self.pre = self.result[0][95] #-:Pre-Recebimentos
		else:	self.pre = ""

		self.autorizacao_muda_pagamento = ""

		TamanhoQuadro  = 624
	
		if self.documento !='':

			creditoDebitoCl= self.creditoDebito()
			vlCreditoConta = creditoDebitoCl[0]
			vlDebitoRecebe = creditoDebitoCl[1]
			self._cnpj_cpf = self.valcnpj.cpfcnpj(self.documento)[0]

		wx.Frame.__init__(self, parent, id, 'Caixa: Recebimento de DAV(s)', size=(750,TamanhoQuadro), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

		self.listaPagamento = wx.ListCtrl(self.painel, -1,pos=(10,63), size=(507,202),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.Bind(wx.EVT_CLOSE, self.voltar)
		self.listaPagamento.SetBackgroundColour('#E8EEF3')
		self.listaPagamento.SetForegroundColour('#7F7F7F')
		self.listaPagamento.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.listaPagamento.InsertColumn(0, u'Parcela',     width=50)
		self.listaPagamento.InsertColumn(1, u'Vencimento',  width=90)
		self.listaPagamento.InsertColumn(2, u'Forma de Pagamento', width=260)
		self.listaPagamento.InsertColumn(3, u'Valor Recebido',format=wx.LIST_ALIGN_LEFT, width=100)
		self.listaPagamento.InsertColumn(4, u'Valor Parcela', format=wx.LIST_ALIGN_LEFT, width=110)
		self.listaPagamento.InsertColumn(5, u'Troco',format=wx.LIST_ALIGN_LEFT, width=100)
		self.listaPagamento.InsertColumn(6, u'PGTo Crédito',format=wx.LIST_ALIGN_LEFT, width=110)
		self.listaPagamento.InsertColumn(7, u'CPF-CNPJ',    width=110)
		self.listaPagamento.InsertColumn(8, u'Correntista', width=110)
		self.listaPagamento.InsertColumn(9, u'Nº Banco',    width=110)
		self.listaPagamento.InsertColumn(10,u'Nº Agência',  width=110)
		self.listaPagamento.InsertColumn(11,u'Nº Cheque',   width=110)
		self.listaPagamento.InsertColumn(12,u'Nº ContaCorrente', width=130)
		self.listaPagamento.InsertColumn(13,u'Dados do Cheque',  width=130)
		self.listaPagamento.InsertColumn(14,u'Bandeira',         width=200)
		self.listaPagamento.InsertColumn(15,u'Descricao ECF',    width=200)
		self.listaPagamento.InsertColumn(16,u'Nº Autorização',   width=200)
		self.listaPagamento.InsertColumn(17,u'{COMP}Compensação',width=200)
		self.listaPagamento.InsertColumn(18,u'Autorizacao mudaca pagamento',width=300)

		""" Dados do Cheque """
		self.chdocum = self.chcorre = self.chbanco = self.chagenc = ''
		self.chconta = self.chnumer = self.chinfor = self.compens = ''

		""" Desabilita Tela Anterior """
		self.parente.Disable()
	
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.listaPagamento.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.alterar)
		self.listaPagamento.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)

		""" Cabecalho """
		scli = u"{ Cliente Cadastrado }"
		if self.result[0][75] != "S":	scli = u"{ Cliente Não Cadastrado }"

		clie = wx.StaticText(self.painel,-1,scli,pos=(527,160))
		clie.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		clie.SetForegroundColour('#A52A2A')

		ndav = wx.StaticText(self.painel,-1,u"Nº DAV-Documento:",pos=(2,10))
		ndav.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		vdav = wx.StaticText(self.painel,-1,u"Valor do DAV:",pos=(240,4))
		vdav.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		flid = wx.StaticText(self.painel,-1,u"ID-Filial DAV",pos=(455,4))
		flid.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		flid.SetForegroundColour("#4D4D4D")

		self.dav_vinculado = wx.StaticText( self.painel, -1, '[ '+ self.valor_vinculado +' ]', pos=(2,28))
		self.dav_vinculado.SetForegroundColour('#0C0C9D')
		self.dav_vinculado.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		self.fiddav = wx.TextCtrl(self.painel,-1,value =self.result[0][54], pos=(452,18),size=(66,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.fiddav.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		self.fiddav.SetForegroundColour('#EFEF7D')
		self.fiddav.SetBackgroundColour('#7F7F7F')

		vdes = wx.StaticText(self.painel,-1,"Valor do Desconto:",pos=(240,24))
		vdes.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		nmcl = wx.StaticText(self.painel,-1,"Nome do Cliente:", pos=(2,45))
		nmcl.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		vdav = wx.StaticText(self.painel,-1,"Receber",pos=(527,12))
		vdav.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		
		sldv = wx.StaticText(self.painel,-1,"S a l d o",pos=(642,12))
		sldv.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		vcco = wx.StaticText(self.painel,-1,"Conta Corrente",pos=(527,60))
		vcco.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		vcco.SetForegroundColour('#1E90FF')

		vdeb = wx.StaticText(self.painel,-1,"Débitos",pos=(642,60))
		vdeb.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		vdeb.SetForegroundColour('#FF0000')

		vrec = wx.StaticText(self.painel,-1,"Entre com o Valor",pos=(527,115))
		vrec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		vrec.SetForegroundColour('#4D4D4D')

		vrec = wx.StaticText(self.painel,-1,"Nº Dias",pos=(662,115))
		vrec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		vrec.SetForegroundColour('#4D4D4D')

		vnci = wx.StaticText(self.painel,-1,"Vencimento",pos=(527,173))
		vnci.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		vnci.SetForegroundColour('#4D4D4D')

		parc = wx.StaticText(self.painel,-1,"Parçelas",pos=(662,173))
		parc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		parc.SetForegroundColour('#4D4D4D')

		troc = wx.StaticText(self.painel,-1,"Troco-Rateio",  pos=(527,280))
		troc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		troc.SetForegroundColour('#005C00')

		conc = wx.StaticText(self.painel,-1,"Conta-Corrente",pos=(527,315))
		conc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		conc.SetForegroundColour('#005C00')

		TCnr = wx.StaticText(self.painel,-1, "Resgate de crédito\navulso NºTickete:", pos=(15,313))
		TCnr.SetForegroundColour('#3E8298')
		TCnr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		TCnc = wx.StaticText(self.painel,-1, "Pagamento com Crédito:", pos=(255,320))
		TCnc.SetForegroundColour('#7F7F7F')
		TCnc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		Trec = wx.StaticText(self.painel,-1, "Valor Total Recebito:", pos=(280,350))
		Trec.SetForegroundColour('#7F7F7F')
		Trec.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		vTro = wx.StaticText(self.painel,-1, "Registro do Troco: ", pos=(12,355))
		vTro.SetForegroundColour('#7F7F7F')
		vTro.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Valor Parcela", 		 pos=(15, 275)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Nº Cheque",     		 pos=(132,275)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Alterar\nVencimento:", pos=(278,280)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Estações NFCe-ACBr-Plus", pos=(430,554)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))

		self.bandeira = wx.StaticText(self.painel,-1, '', pos=(12,335),style = wx.ALIGN_RIGHT)
		self.bandeira.SetForegroundColour('#BC7B04')
		self.bandeira.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.autoriza = wx.StaticText(self.painel,-1, '', pos=(12,345),style = wx.ALIGN_RIGHT)
		self.autoriza.SetForegroundColour('#A7710E')
		self.autoriza.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		#-------------------: Receber no Local
		if self.result[0][83] !='':

			rcbLocal = wx.StaticText(self.painel,-1, '{ '+self.result[0][83]+' }', pos=(527,212),style = wx.ALIGN_RIGHT)
			rcbLocal.SetForegroundColour('#1C521C')
			rcbLocal.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.formapg = wx.StaticText(self.painel,-1, '{ '+self.result[0][40]+' }', pos=(527,222),style = wx.ALIGN_RIGHT)
		self.formapg.SetForegroundColour('#4D4D4D')
		self.formapg.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
				
		""" Saida de Dados """
		""" Cabecalho Numero do DAV """ 
		sdav = wx.TextCtrl(self.painel,-1,value =str(self.result[0][2]),pos=(120,5),size=(110,22))
		sdav.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		sdav.SetForegroundColour('#7F7F7F')
		sdav.SetBackgroundColour('#E5E5E5')

		""" Valor do DAV - Desconto """
		vlrd = wx.TextCtrl(self.painel,-1,value =format(self.result[0][36],','),pos=(340,0),size=(110,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vlrd.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		vlrd.SetForegroundColour('#125290')
		vlrd.SetBackgroundColour('#E5E5E5')

		desco = wx.TextCtrl(self.painel,-1,value =format(self.result[0][25],','),pos=(340,20),size=(110,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		desco.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		desco.SetForegroundColour('#C64646')
		desco.SetBackgroundColour('#E5E5E5')

		snmc = wx.TextCtrl(self.painel,-1,value = str(self.result[0][4]),pos=(120,40),size=(398,22))
		snmc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		snmc.SetForegroundColour('#7F7F7F')
		snmc.SetBackgroundColour('#E5E5E5')
		
		self.vDav = wx.TextCtrl(self.painel,-1,format( self.result[0][37],','), pos=(525,27),size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.vDav.SetForegroundColour('#7F7F7F')
		self.vDav.SetBackgroundColour('#E5E5E5')
		self.vDav.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	
		self.slDav = wx.TextCtrl(self.painel,-1,format(self.result[0][37],','), pos=(640,27),size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.slDav.SetForegroundColour('#789ABA')
		self.slDav.SetBackgroundColour('#E5E5E5')
		self.slDav.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ccDav = wx.TextCtrl(self.painel,-1,format(vlCreditoConta,','), pos=(525,75),size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.ccDav.SetForegroundColour('#0000FF')
		self.ccDav.SetBackgroundColour('#E5E5E5')
		self.ccDav.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.crDav = wx.TextCtrl(self.painel,-1,format(vlDebitoRecebe,','), pos=(640,75),size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.crDav.SetForegroundColour('#F56969')
		self.crDav.SetBackgroundColour('#E5E5E5')
		self.crDav.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		wx.StaticLine(self.painel, -1, (520,55),   (224,4)).SetForegroundColour('#E6E6FA')
		
		pagCli = ""
		if self.clresul !="" and self.clresul[0][4] !=None:	pagCli = self.clresul[0][4]
		self.formaspgt = self.relpag.fpg(pagCli,2)
			
		""" Entrar com o valor """
		self.valorapaga = mkn(self.painel, 130,  value = str(self.valorSDav), pos=(525,126), size=(100,22),  style = wx.ALIGN_RIGHT, integerWidth = 7, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.valorapaga.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Vencimento-parcelas """
		self.vencimento = wx.DatePickerCtrl(self.painel,-1, pos=(525,185), size=(114,26), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.VencPadrao = self.vencimento.GetValue() 
		self.nuparcelas = wx.ComboBox(self.painel, -1, '1', pos=(660,185), size=(65,26),  choices = login.parcelas, style=wx.CB_READONLY)
		self.numeroDias = wx.ComboBox(self.painel, -1, '',  pos=(660,125), size=(65,26),  choices = ['']+login.interval)
		self.acbrEsTaca = wx.ComboBox(self.painel, -1, self.parente.esTAcbr.GetValue(),  pos=(427,567), size=(320,27), choices = self.parente.acbrPlus,style=wx.NO_BORDER|wx.CB_READONLY)

		self.emdinamica = wx.CheckBox(self.painel, 328 , u"Emissão dinámica da nfce",  pos=(427,594))
		self.emdinamica.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		if len( login.filialLT[ self.pgFil ][35].split(";") ) >= 63 and login.filialLT[ self.pgFil ][35].split(";")[62] == "T":

			self.emdinamica.Enable( True )
			self.emdinamica.SetValue( True )
		else:	self.emdinamica.Enable( False )

		""" Forma de pagamento """
		self.fpagamento = wx.ComboBox(self.painel, 201, '', pos=(525,235), size=(218,26), choices = self.formaspgt,style=wx.CB_READONLY)

		""" Troco-Rateio """
		self.Valor_Troco = wx.TextCtrl(self.painel,-1,'0.00', pos=(525,290),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Valor_Troco.SetForegroundColour('#6D95BC')
		self.Valor_Troco.SetBackgroundColour('#E5E5E5')
		self.Valor_Troco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.Valor_Rateio = wx.TextCtrl(self.painel,-1,'0.00', pos=(525,325),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Valor_Rateio.SetForegroundColour('#6D95BC')
		self.Valor_Rateio.SetBackgroundColour('#E5E5E5')
		self.Valor_Rateio.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.numer_TicheT = wx.TextCtrl(self.painel,555,'', pos=(130,315),size=(97,22),style =wx.TE_PROCESS_ENTER|wx.ALIGN_RIGHT)
		self.numer_TicheT.SetForegroundColour('#6D95BC')
		self.numer_TicheT.SetBackgroundColour('#BFBFBF')
		self.numer_TicheT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		if self.result[0][75] != "S" and self.cResgaTe == True:	self.numer_TicheT.Enable( True )
		else:	self.numer_TicheT.Enable( False )
	
		self.TConCo = wx.TextCtrl(self.painel,-1,'0.00', pos=(403,315),size=(110,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TConCo.SetForegroundColour('#FFADBC')
		self.TConCo.SetBackgroundColour('#E5E5E5')
		self.TConCo.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.TReceb = wx.TextCtrl(self.painel,-1,'0.00', pos=(403,345),size=(110,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TReceb.SetForegroundColour('#7F7F7F')
		self.TReceb.SetBackgroundColour('#E5E5E5')
		self.TReceb.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.Trocos = wx.TextCtrl(self.painel,-1, "0.00", pos=(100,350),size=(70,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Trocos.SetForegroundColour('#7F7F7F')
		self.Trocos.SetBackgroundColour('#E5E5E5')
		self.Trocos.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Altera valor da parcela,numero do cheque e vencimento """
		self.alparc = mkn(self.painel, 120,        value = '0.00', pos=(13,286), size=(90, 22), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.alparc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		
		self.alcheq = wx.TextCtrl(self.painel,123, value='', pos=(130,288), size=(97, 22), style = wx.ALIGN_RIGHT)
		self.alvenc = wx.DatePickerCtrl(self.painel,-1,      pos=(345,285), size=(115,26), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.alcheq.SetBackgroundColour('#E5E5E5')

		self.fixadia = wx.CheckBox(self.painel, 228 , "Dias Fixo",  pos=(661,150))
		self.fixadia.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		
		""" Botoes """
		rateio = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/rateiop.png",   wx.BITMAP_TYPE_ANY), pos=(525,345), size=(26,27))				
		client = wx.BitmapButton(self.painel, 161, wx.Bitmap("imagens/cliente16.png", wx.BITMAP_TYPE_ANY), pos=(556,345), size=(26,27))				

		inclu1 = wx.BitmapButton(self.painel, 151, wx.Bitmap("imagens/adicionam.png", wx.BITMAP_TYPE_ANY), pos=(615,270), size=(40,38))				
		apagar = wx.BitmapButton(self.painel, 152, wx.Bitmap("imagens/apagar.png",    wx.BITMAP_TYPE_ANY), pos=(659,270), size=(40,38))				
		cancel = wx.BitmapButton(self.painel, 153, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(702,270), size=(40,38))				

		Voltar = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(615,308), size=(40,38))				
		nfeemi = wx.BitmapButton(self.painel, 160, wx.Bitmap("imagens/nfe.png",       wx.BITMAP_TYPE_ANY), pos=(659,308), size=(40,38))				
		self.ecfemi = wx.BitmapButton(self.painel, 225, wx.Bitmap("imagens/cupomi.png",    wx.BITMAP_TYPE_ANY), pos=(702,308), size=(40,38))				
		recebn = GenBitmapTextButton(self.painel,229,label='Recebimento Normal', pos=(618,350),size=(123,22), bitmap=wx.Bitmap("imagens/liquidar.png", wx.BITMAP_TYPE_ANY))
		recebn.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.altera = wx.BitmapButton(self.painel, 108, wx.Bitmap("imagens/alterarp.png",  wx.BITMAP_TYPE_ANY), pos=(474,280), size=(40,30))				

		""" Telas de Hisotrico das Autorizacoes e Pre-Recebimento do Vendedor """
		wx.StaticText(self.painel,-1,"Histórico das autorizacções",  pos=(12, 378)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"Pre-Recebimentos de Vendas  ", pos=(428,378)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))

		self.historico = wx.TextCtrl(self.painel,900,value=self.result[0][82], pos=(10,390), size=(414,115),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetBackgroundColour('#4D4D4D')
		self.historico.SetForegroundColour('#90EE90')
		self.historico.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL))
		
		if self.result[0][82] == None or self.result[0][82].strip() == "":
			
			self.historico.SetValue( "Historico de Autorizaçoes!!")
			self.historico.SetForegroundColour('#7F7F7F')

		""" Pre-Recebimentos """
		self.misTu = wx.TextCtrl(self.painel, 901, value="", pos=(10,510), size=(414,105),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.misTu.SetBackgroundColour("#7F7F7F")
		self.misTu.SetForegroundColour("#F1F1B0")
		self.misTu.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD))

		if self.result[0][111] !=None and self.result[0][111] !="":

			lisTaPag = "{  DAV com Separacao automatica  }\n\n"
			for pr in self.result[0][111].split('|'):
					
				if pr !='':
						
					_fp = pr.split(';')
					_tT = _fla = ""
					if "{ Formas de Pagamento do Grupo }\n" in pr:
						
						_tT = "\n\n{ Formas de Pagamento do Grupo }\n"
						_fp = pr.replace("{ Formas de Pagamento do Grupo }\n","").split(";")
						
					if len( _fp ) >=6 and _fp[5] !="":	_fla = _fp[5]+" "
					else:	_fla = ""
					
					lisTaPag +=_tT+_fla+_fp[0]+"  "+_fp[2]+" "+_fp[1]+" "+_fp[3]+"\n"

			self.misTu.SetValue( lisTaPag )

		else:
			
			self.misTu.SetValue( "{ Lista de Pagamento }\nPara DAVs c/Produtos de Filiais Diferentes!!" )
			self.misTu.SetForegroundColour('#BFBFBF')
				
		self.ListaPrer = wx.ListCtrl(self.painel, 770,pos=(428,390), size=(318,160),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaPrer.SetBackgroundColour('#7CA8B6')
		self.ListaPrer.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ListaPrer.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.recPreRec)
			
		self.ListaPrer.InsertColumn(0, 'Forma de Pagamento', width=155)
		self.ListaPrer.InsertColumn(1, 'Valor',      format=wx.LIST_ALIGN_LEFT,width=75)
		self.ListaPrer.InsertColumn(2, 'Vencimento', format=wx.LIST_ALIGN_LEFT,width=75)
		self.ListaPrer.InsertColumn(3, 'Desconto',   format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaPrer.InsertColumn(4, 'Receber no Local', width=200)

		if self.result[0][95] !=None and self.result[0][95] !="":

			indice = 0
			for pr in self.result[0][95].split('|'):
					
				if pr !='':
						
					_fp = pr.split(';')
					self.ListaPrer.InsertStringItem(indice,_fp[0])
					self.ListaPrer.SetStringItem(indice,1, _fp[2])	
					self.ListaPrer.SetStringItem(indice,2, _fp[1])	
					self.ListaPrer.SetStringItem(indice,3, _fp[4])	
					self.ListaPrer.SetStringItem(indice,4, _fp[3])	

					if indice % 2:	self.ListaPrer.SetItemBackgroundColour(indice, "#79AFC0")

					indice +=1

		rateio.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		inclu1.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		apagar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cancel.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		nfeemi.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ecfemi.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		client.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		recebn.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.historico.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.misTu.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		
		self.altera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.alparc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.alcheq.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.fixadia.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		rateio.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		inclu1.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		apagar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cancel.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		nfeemi.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ecfemi.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		client.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		recebn.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.misTu.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.historico.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.altera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.alparc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.alcheq.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.fixadia.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		rateio.Bind(wx.EVT_BUTTON,self.acsrateio)
		client.Bind(wx.EVT_BUTTON,self.alteraCliente)
		
		inclu1.Bind(wx.EVT_BUTTON,self.pagamentos)
		apagar.Bind(wx.EVT_BUTTON,self.apagaritems)
		cancel.Bind(wx.EVT_BUTTON,self.apagaritems)
		Voltar.Bind(wx.EVT_BUTTON,self.voltar)
		nfeemi.Bind(wx.EVT_BUTTON,self.fechanfe)
		self.ecfemi.Bind(wx.EVT_BUTTON,self.fechaecf)
		recebn.Bind(wx.EVT_BUTTON,self.fechaecf)
		
		self.historico.Bind(wx.EVT_LEFT_DCLICK, self.hisToricoAUT)
		self.misTu.Bind(wx.EVT_LEFT_DCLICK, self.hisToricoAUT)
		
		self.valorapaga.Bind(wx.EVT_LEFT_DCLICK, self.tecladon)
		self.alparc.Bind(wx.EVT_LEFT_DCLICK, self.tecladon)
		self.alcheq.Bind(wx.EVT_LEFT_DCLICK, self.tecladon)
		
		self.altera.Bind(wx.EVT_BUTTON,self.alterarValores)
		self.numer_TicheT.Bind(wx.EVT_TEXT_ENTER,  self.resgate)			
		self.acbrEsTaca.Bind(wx.EVT_COMBOBOX, self.TrocarEstacaoAcbr)
		self.fixadia.Bind(wx.EVT_CHECKBOX, self.evchBox)
		self.numeroDias.Bind(wx.EVT_COMBOBOX, self.evchBox)

		""" Evento Combo Box"""
		self.fpagamento.Bind(wx.EVT_COMBOBOX,self.evcombo)
		
		self.valorapaga.SetFocus()

		if self.clresul == '':	self._cnpj_cpf = False

		self.altera.Enable(False)
		self.alparc.Enable(False)
		self.alcheq.Enable(False)
		self.alvenc.Enable(False)
		rateio.Enable(self._cnpj_cpf)

		if self.result[0][75] != "S":	client.Enable(False)	

		self.daTaORiginal = self.alvenc.GetValue()

		if login.filialLT[ self.pgFil ][21] == "1":	recebn.Disable()
		
		"""  Permitir Emissao de NFCe, Cadastro da Empresa 2-Normal NFe,NFCe  """
		if login.filialLT[ self.pgFil ][21] == "2" and login.usaenfce == "T":	self.ecfemi.SetBitmapLabel (wx.Bitmap('imagens/download16.png'))
		else:	self.ecfemi.Enable( False )
		
		if self.result[0][73] !="":	nfeemi.Disable() #-: NFe Emitida
		
		"""   Ambiente de Emissao da NFCe ACBR-PLUS   """
		if len( login.filialLT[ self.pgFil ][35].split(";") ) >= 25 and login.filialLT[ self.pgFil ][35].split(";")[24] == "T":	self.fpagamento.Enable( False )

		if self.parente.fdbl:

			self.historico.SetValue(u"\n\nNão use click duplo  no recebimento")
			self.historico.SetForegroundColour("#FFFFFF")
			self.historico.SetBackgroundColour("#000000")
			self.historico.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

			self.misTu.SetValue(u"\n\nNão use click duplo  no recebimento")
			self.misTu.SetForegroundColour("#FFFFFF")
			self.misTu.SetBackgroundColour("#000000")
			self.misTu.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

			nfeemi.Enable( False )
			self.ecfemi.Enable( False )
			recebn.Enable( False )
			recebn.Enable( False )

			rateio.Enable( False )
			client.Enable( False )
			inclu1.Enable( False )
			apagar.Enable( False )
			cancel.Enable( False )

			self.parente.fdbl = False
		
		"""  Bloqueio emissa NFCe para clientes com CNPJ  """	
		if len( login.filialLT[ self.pgFil ][35].split(';') ) >= 115 and login.filialLT[ self.pgFil ][35].split(';')[114] == 'T' and self.clresul and len( self.clresul[0][6] ) == 14:	self.ecfemi.Enable( False )

	def voltar(self,event):
		
		self.parente.Enable()
		self.Destroy()
	
	def evchBox(self,event):

		if self.fixadia.GetValue():	self.numeroDias.SetValue('')
		
	def TrocarEstacaoAcbr(self,event):
		
		self.parente.esTAcbr.SetValue( self.acbrEsTaca.GetValue() )
		self.parente.seTarEstarcaoAcbr(wx.EVT_BUTTON)
	
	def resgate( self, event ):

		if self.numer_TicheT.GetValue().strip() !="":
			
			_doc = self.numer_TicheT.GetValue().strip()
			if len( _doc ) <= 10:	pass
			else:
				
				self.numer_TicheT.SetValue('')
				alertas.dia( self.painel,"Número de digitos, incompativel com o número do tickete...\n"+(" "*100),"Resgate de Créditos Avulso")
				return
			
			_doc = "DEV"+str( _doc ).zfill(10)
			self.numer_TicheT.SetValue(_doc)
			
			sald = formasPagamentos()
			conn = sqldb()
			sql  = conn.dbc("Caixa: Recebimento { coleta do créditos e débitos }", fil = self.pgFil, janela = self )
					
			if sql[0] == True:

				_ccc,_deb = sald.saldoCC( sql[2], _doc )
				_sal = ( _ccc - _deb )

				conn.cls(sql[1])

			if _sal > 0:
				
				confima = wx.MessageDialog(self.painel,"{ Resgate do crédito avulso }\n\nvalor do cŕedito: "+format( _sal,',' )+"\nConfirme p/Continuar\n"+(" "*100),"Caixa: Resgate do crédito avulso",wx.YES_NO|wx.NO_DEFAULT)
				if confima.ShowModal() ==  wx.ID_YES:
			
					self.ccDav.SetValue( format( _sal,',' ) )
					self.numer_TicheT.Enable( False )
					self.numer_TicheT.SetBackgroundColour("#F9F9F9")
					self.numer_TicheT.SetForegroundColour("#000000")
			
			if _sal == 0:	self.numer_TicheT.SetValue('')
		
	def hisToricoAUT(self,event):
			
		_his = "Historico vazio..."
		if event.GetId() == 900:	_his = self.historico.GetValue()
		if event.GetId() == 901:	_his = self.misTu.GetValue()
			
		MostrarHistorico.hs = _his
		MostrarHistorico.TT = "{ Caixa }"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.pgFil
		MostrarHistorico.GD = ""

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()

	""" Recebimento pelo pre-recebimento """
	def recPreRec(self,event):

		self.grVencime = "" #-: Utilizado p/Gravar a da de vencimento da parcela
		nRegis = self.ListaPrer.GetItemCount()
		indice = self.ListaPrer.GetFocusedItem()

		_saldo = self.Trunca.trunca( 3, Decimal( self.slDav.GetValue().replace(',','') ) )
		_receb = self.Trunca.trunca( 3, Decimal( self.ListaPrer.GetItem(indice,1).GetText().replace(',','') ) )
		
		if _receb > _saldo:

			alertas.dia(self.painel,"Valor é superior ao saldo...\n"+(" "*80),"Caixa: Pre-Recebimento")
			return
			
		lsPg = ["02","03","04","05","08","09","11"]

		if self.valorapaga.GetValue() == 0:	alertas.dia(self.painel,"Valor enviado imcompativel...\n{ Sem valor para pagamentos }\n"+(" "*80),"Caixa: Pre-Recebimento")
		else:
			
			rLocal = True
			for pfg in range(nRegis):
				
				if self.ListaPrer.GetItem(pfg,0).GetText()[:2] !="12":	rLocal = False

			""" Adicionar Pagamentos """
			__fp = self.ListaPrer.GetItem(indice,0).GetText()
			__vp = Decimal( self.ListaPrer.GetItem(indice,1).GetText().replace(',','') )
			__vc = self.ListaPrer.GetItem(indice,2).GetText()

			parcela_incluida = False
			for lanpag in range( self.listaPagamento.GetItemCount() ):

				___fp = self.listaPagamento.GetItem( lanpag, 2 ).GetText()
				___vp = Decimal( self.listaPagamento.GetItem( lanpag, 3 ).GetText().replace(',','') )
				___vc = self.listaPagamento.GetItem( lanpag, 1 ).GetText()

				if ___fp == __fp and ___vp == __vp and ___vc == __vc:	parcela_incluida = True

			if parcela_incluida:	alertas.dia( self, "Parcela ja incluida na lista de pagamentos...\n"+(" "*100),"Caixa: Pagamentos")
			if not parcela_incluida:

				iP = 0
				for lP in self.formaspgt:
						
					if lP !='':
						
						if lP.split(' ')[1][:2] == __fp[:2]:	self.fpagamento.SetValue( self.formaspgt[iP] )	
							
					iP += 1
			
				if rLocal == False:	self.valorapaga.SetValue(str( __vp ))

				if __fp[:2] in lsPg:

					self.vencimento.SetValue( wx.DateTimeFromDMY( int( __vc.split('/')[0] ), ( int( __vc.split('/')[1] ) - 1 ), int( __vc.split('/')[2] )))
					self.grVencime = __vc
					self.evcombo(wx.EVT_COMBOBOX)

				else:

					self.vencimento.SetValue( wx.DateTimeFromDMY( int( __vc.split('/')[0] ), ( int( __vc.split('/')[1] ) - 1 ), int( __vc.split('/')[2] )))
					self.incluirPagamento(151, vcPre = __vc )

	""" Provocar o Retorno da DANFE"""
	def sair(self,event):
		
		self.parente.Enable()
		self.Destroy()	

	def alteraCliente(self,event):

		self.idInc  = 500
		self.codigo = self.result[0][3]

		alTeraInclui.clFilial = self.pgFil
		acl_frame=alTeraInclui(parent=self,id=-1)
		acl_frame.Centre()
		acl_frame.Show()

	def alterarValores(self,event):

		indice = self.listaPagamento.GetFocusedItem()
		if self.listaPagamento.GetItemCount() > 0 :

			dTVenc = datetime.datetime.strptime(self.alvenc.GetValue().FormatDate(),'%d-%m-%Y').date()
			dTHoje = datetime.datetime.now().date()
			valorA = Decimal( self.listaPagamento.GetItem(indice, 3).GetText().replace(",","") )
			valorE = Decimal( str( self.valorapaga.GetValue() ) )
			valorP = Decimal( str( self.alparc.GetValue() ) )
			
			valorS = ( valorA + valorE )
			if valorP > valorS:

				alertas.dia(self.painel,"Valor superior ao saldo...\n"+(" "*60),"Caixa-Pagamento")
				return

			_pa = ["02","03"]
			_fp = self.listaPagamento.GetItem(indice, 2).GetText()[:2]

			sdT = False
			snD = False
			if _fp in _pa:	sdT = True
			if _fp not in _pa:	snD = True
				
			if _fp == "06" and acs.acsm("522",False) == True:	snD, sdT = False, True
			if _fp == "07" and acs.acsm("523",False) == True:	snD, sdT = False, True
			
			if snD == True:	alertas.dia(self,u"Forma de pagamento não permite alterar vencimento...\n"+(" "*120),"Caixa: Pagamento")

			fpT = self.listaPagamento.GetItem(indice, 2).GetText()[:2]
			autorizaca_data = True if fpT in ["02","03"] and len( login.filialLT[ self.pgFil ][35].split(";") ) >= 61 and login.filialLT[ self.pgFil ][35].split(";")[60] == "T" else False
			data_autorizada = u"\n{ Autorização p/retroagir }\n" if fpT in ["02","03"] and autorizaca_data else "\n"

			saida = False
			if dTVenc < dTHoje:

				if not autorizaca_data:	sdT = False
				saida = True

			if sdT == True:
				
				regist = self.listaPagamento.GetItemCount()
				daTaor = self.listaPagamento.GetItem(indice, 1).GetText()
				vlrori = self.listaPagamento.GetItem(indice, 3).GetText()
				pagame = self.listaPagamento.GetItem(indice, 2).GetText()[:2]

				valor = format( self.alparc.GetValue(),'.2f' )
				ncheq = self.alcheq.GetValue()
				venci =	datetime.datetime.strptime(self.alvenc.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

				self.listaPagamento.SetStringItem(indice,1,  str(venci) )	
				self.listaPagamento.SetStringItem(indice,3,  format( Decimal(valor),',' ) )
				self.listaPagamento.SetStringItem(indice,4,  format( Decimal(valor),',' ) )
				self.listaPagamento.SetStringItem(indice,11, str(ncheq) )
				
				self.passagem(wx.EVT_BUTTON)
				self.ajustaParcela(vlrori,pagame,daTaor,valor)
				self.valoresRecebidos()

		self.altera.Enable(False)
		self.alparc.Enable(False)
		self.alcheq.Enable(False)
		self.alvenc.Enable(False)

		if saida:	alertas.dia(self.painel,"[ Data Incompatível ]\n\nVencimento: "+str(dTVenc.strftime("%d/%m/%Y"))+"\n  Data Atual: "+str(dTHoje.strftime("%d/%m/%Y"))+"\n\nCom Pagamento em CHEQUE!!\n"+data_autorizada+(" "*120),"Caixa-Pagamento")

	def ajustaParcela(self,_Valor,_Forma,_DaTa,vParcela):

		formas = "06-07-10-11"
		nregis = self.listaPagamento.GetItemCount()
		indlan = self.listaPagamento.GetFocusedItem()
		vlToTa = Troco = Decimal('0.00')

		indice = 0

		for i in range(self.listaPagamento.GetItemCount()):

			vlToTa += Decimal( self.listaPagamento.GetItem(indice, 3).GetText().replace(',','') )
			indice +=1

		if vlToTa >  Decimal( self.result[0][37] ) and _Forma not in formas:

			Troco = ( vlToTa - Decimal( self.result[0][37] ) )
			self.listaPagamento.SetStringItem(indlan,5, format( Troco ,',' ) )
			self.listaPagamento.Refresh()

		elif vlToTa >  Decimal( self.result[0][37] ) and _Forma in formas:

			self.listaPagamento.SetStringItem(indlan,1, _DaTa )
			self.listaPagamento.SetStringItem(indlan,3, _Valor )
			self.listaPagamento.Refresh()

			alertas.dia(self.painel,u"1-Valor maior que o saldo, não permitido para esta modalidade...\n"+(" "*120),u"Recebimento de Caixa")	

		elif vlToTa <= Decimal( self.result[0][37] ) and _Forma in formas:

			self.listaPagamento.SetStringItem(indlan,4, vParcela )
			self.listaPagamento.Refresh()
		
	def passagem(self,event):

		self.altera.Enable(False)
		self.alparc.Enable(False)
		self.alvenc.Enable(False)

		self.alvenc.SetValue(self.daTaORiginal)
		self.alparc.SetValue('0.00')
		self.alcheq.SetValue('')
		
	def alterar(self,event):

		indice = self.listaPagamento.GetFocusedItem()
		vlparc = self.listaPagamento.GetItem(indice,3).GetText()
		dTvenc = self.listaPagamento.GetItem(indice,1).GetText()
		nucheq = self.listaPagamento.GetItem(indice,11).GetText()

		if dTvenc !='':
			
			d,m,y = dTvenc.split('/')
			self.alvenc.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))
			self.alparc.SetValue(vlparc)
			self.alcheq.SetValue(nucheq)

			self.altera.Enable(True)
			self.alparc.Enable(True)
			self.alcheq.Enable(True)
			self.alvenc.Enable(True)

	def validaPagamentosFuturos(self):

		"""  validacao para formas de pagamentos futuros sem cpf-cnpj  """

		formas_pagamentos = ""
		formas_bloqueio = False
		retornar = True
		
		cliente_documento = self.clresul[0][6] if self.clresul else ""
		vendas_documento  = self.result[0][39]
		
		sem_documento =""
		if not cliente_documento:	sem_documento  = "1 - Cliente sem cpf-cnpj no cadastro de clientes"
		if not vendas_documento:	sem_documento += "\n2 - Cliente sem cpf-cnpj no dav"
		
		if self.listaPagamento.GetItemCount():
			
			for i in range( self.listaPagamento.GetItemCount() ):
				
				if self.listaPagamento.GetItem( i, 2 ).GetText().split('-')[0] in ['02','03','06','07','08','11','12'] and sem_documento:
					
					formas_pagamentos +=self.listaPagamento.GetItem( i, 2 ).GetText()+'\n'
					formas_bloqueio = True
			
			if formas_bloqueio:
				
				alertas.dia( self, u"{ Formas de pagamentos com lançamento no contas areceber }\n\n"+sem_documento+u"\n\nAjuste os dados do cliente e refaça o processo\n"+(" "*150),"Bloquei com formas de pagamentos futuras")
				retornar = False
				
		return retornar
		
	def fechaecf(self,event):

		""" Verifica a filial da empresa """
		if not self.validaPagamentosFuturos():	return
		if login.filialLT[ self.pgFil ][21] == "2" and login.usaenfce == "T" and event.GetId() == 225:
			
			if self.fechaTeste( "255" ) == True:

				if   self.parente.sw == "2":

					"""  Verica se a frema ja foi aberta se aberto nao permiti abrir novamente  """
					if editadanfenfce.instancia > 0:	return

					editadanfenfce.instancia = 1
					_dados = self.pgFil,self.davn, 1
					nfc_frame=editadanfenfce(parent=self,id=-1, dados = _dados )
					nfc_frame.Centre()
					nfc_frame.Show()
					
				elif self.parente.sw == "3":

					"""
						Envia automaticamente os dados da filial selecionada para o acbr, se os ultimos dados da filial
						enviado for diferente da atual
					"""
					self.ecfemi.Enable( False )
					if self.parente.esTAcbr.GetValue().strip() == "":

						self.ecfemi.Enable( True )
						alertas.dia(self,u"Selecione uma Estação ACBR-Plus p/Continuar...\n"+(" "*120),u"ACBr-Plus")
						return
						
					if self.pgFil != self.parente.uFil or self.parente.uEsT != self.parente.esTAcbr.GetValue().split(":")[1].strip():	self.parente.acbrEstacao( self.pgFil )

					if Decimal( self.slDav.GetValue().replace(',','') ) !=0:	alertas.dia(self.painel,u"3-Consta um saldo de caixa:\n\nSaldo: "+str(self.slDav.GetValue())+"\n"+(" "*100),u"Caixa: Fechamento")
					else:

						darumaNfce310.Filial = self.pgFil
						darumaNfce310.cdClie = self.result[0][3]
						darumaNfce310.nuDavs = self.result[0][2]
						darumaNfce310.TPEmis = 2
						darumaNfce310.dReceb = ""
						darumaNfce310.vincul = self.result[0][112]

						fwd_frame=darumaNfce310(parent=self,id=-1)
						fwd_frame.Centre()
						fwd_frame.Show()

		else: #-: Emissao por ECF

			if not self.validaPagamentosFuturos():	return
			if   self.validaRcNormal() == False:	alertas.dia(self,u"{ DAV em processo de inutilização de NOTA }\n\n1 - Voçê pode Reenviar ao SEFAZ p/continuar o recebimento\n2 - Inutilize a NF no gerenciador de notas e refaça o recebimento\n"+(" "*130),u"Caixa: Recebimento Normal")
			elif Decimal(self.slDav.GetValue().replace(',','')) !=0:	alertas.dia(self.painel,u"4-Consta um saldo de caixa:\n\nSaldo: "+str(self.slDav.GetValue())+"\n"+(" "*100),u"Caixa: Fechamento")

			else:

				_emis = u"{ Recebimento com Emissão de ECF }"
				if event.GetId()==229:	_emis = u"{ Recebimento Normal }"
				receb = wx.MessageDialog(self.painel,_emis+u"\n\nConfirme para finalizar o recebimento...\n"+(" "*100),u"Caixa: Recebimento",wx.YES_NO|wx.NO_DEFAULT)
				
				if receb.ShowModal() ==  wx.ID_YES:
					
					if event.GetId()==229:	self.fechamento("229",'', filial = self.pgFil )	

	def validaRcNormal(self):

		conn = sqldb()
		sql  = conn.dbc("Caixa: Recebimento { Verificando NF em processo de inutilização }", fil = self.pgFil, janela = self )
		avan = True
		
		if sql[0] == True:
			
			if sql[2].execute("SELECT cr_nota FROM cdavs WHERE cr_ndav='"+str( self.davn )+"'") !=0:
				
				nnoTa = sql[2].fetchone()[0]
				if nnoTa !=None and nnoTa !="" and sql[2].execute("SELECT nf_numdav FROM nfes WHERE nf_numdav='"+str( self.davn )+"' and nf_nnotaf='"+str( nnoTa )+"' and nf_tipola='2'") !=0:	avan = False
					
			conn.cls( sql[1] )

		return avan
				
	def acsrateio(self,event):

		srateio.sobra = Decimal(self.Trocos.GetValue().replace(',',''))
		srateio.docum = self._cnpj_cpf

		raT_frame=srateio(parent=self,id=-1)
		raT_frame.Centre()
		raT_frame.Show()
		
	def evcombo(self,event):

		""" Dados do Cheque """
		self.listaCheque = []
		self.chdocum = self.chcorre = self.chbanco = self.chagenc = ''
		self.chconta = self.chnumer = self.chinfor = self.compens = ''
		self.autorizacao_muda_pagamento = ""

		self.bandeira.SetLabel('')
		self.autoriza.SetLabel('')
		
		if self.fpagamento.GetValue()[3:5] == "02" or self.fpagamento.GetValue()[3:5] == "03":

			dadosCheque.Filial = self.pgFil
			dadosCheque.vencim = self.vencimento.GetValue()
			doc_frame=dadosCheque(parent=self,id=-1)
			doc_frame.Centre()
			doc_frame.Show()

		elif self.fpagamento.GetValue()[3:5] == "04" or self.fpagamento.GetValue()[3:5] == "05" or self.fpagamento.GetValue()[3:5] == "08" or self.fpagamento.GetValue()[3:5] == "09" or self.fpagamento.GetValue()[3:5] == "11":

			regBandeira.pagamento = self.fpagamento.GetValue()
			regBandeira.moduloCha = "RCX"

			ban_frame=regBandeira(parent=self,id=-1)
			ban_frame.Centre()
			ban_frame.Show()

	def RetornaCheque( self, _dc, _cm, _co, _nb, _ag, _cc, _nc, _ic, _vc, _alterada_data ):
				
		self.chdocum = _dc
		self.compens = _cm
		self.chcorre = _co
		self.chbanco = _nb
		self.chagenc = _ag
		self.chconta = _cc
		self.chnumer = _nc
		self.chinfor = _ic
		if _vc:	self.vencimento.SetValue( wx.DateTimeFromDMY( int( _vc.split('/')[0] ), ( int( _vc.split('/')[1] ) - 1 ), int( _vc.split('/')[2] ) ) )
		
	def tecladon(self,event):

		if event.GetId() == 123:	TelNumeric.decimais = 5
		else:	TelNumeric.decimais = 2
		
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def OnEnterWindow(self, event):

		if   event.GetId() == 224:	sb.mstatus(u"  Acesso ao Teclado Numérico",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Rateio da Sobra de Caixa",0)
		elif event.GetId() == 108:	sb.mstatus(u"  Alterar valor da parcela e vencimento",0)
		elif event.GetId() == 120:	sb.mstatus(u"  Click duplo para acionar o teclado numerico virtual",0)
		elif event.GetId() == 123:	sb.mstatus(u"  Click duplo para acionar o teclado numerico virtual",0)
		elif event.GetId() == 151:	sb.mstatus(u"  Incluir Pagamento",0)
		elif event.GetId() == 152:	sb.mstatus(u"  Apagar o Lançamento Selecionado",0)
		elif event.GetId() == 153:	sb.mstatus(u"  Apagar Todos os Lançamentos",0)
		elif event.GetId() == 223:	sb.mstatus(u"  Sair do Recebimento de DAV(s)",0)
		elif event.GetId() == 160:	sb.mstatus(u"  Emitir Nota Fiscal Eletrônica",0)
		elif event.GetId() == 161:	sb.mstatus(u"  Acesso ao cadastro do cliente { Altera dados }",0)
		elif event.GetId() == 229:	sb.mstatus(u"  Recebimento sem Emissão do Cupom e sem Emissão de NFe",0)
		elif event.GetId() == 225:	sb.mstatus(u"  Emitir Cupom Fiscal",0)
		elif event.GetId() == 226:	sb.mstatus(u"  Marque esta opcao para quando na finalização do recebimento o sistema direcionar para o ECFs",0)
		elif event.GetId() == 228:	sb.mstatus(u"  Marque esta opcao para quando no parcelamento o dia de vencimento repetir",0)
		elif event.GetId() == 900:	sb.mstatus(u"  Click duplo para ampliar histórico",0)
		elif event.GetId() == 901:	sb.mstatus(u"  Click duplo para ampliar lista de formas de pagamentos",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus(u"  Caixa: Recebimentos de DAV(s)",0)
		event.Skip()

	def acessconta(self,event):
			
		contacorrente.consulta = self.result[0][39]
		contacorrente.ccFilial = self.pgFil
		contacorrente.modulo   = u"CX"
		
		ban_frame=contacorrente(parent=self,id=-1)
		ban_frame.Centre()
		ban_frame.Show()
		
	def	creditoDebito(self):

		sald = formasPagamentos()
		conn = sqldb()
		sql  = conn.dbc("Caixa: Recebimento { Coleta do Créditos e Débitos }", fil = self.pgFil, janela = self )

		_sal = Decimal('0.00')
		_cad = Decimal('0.00')
		_dAT = datetime.datetime.now().strftime("%Y/%m/%d")
				
		if sql[0] == True:

			if self.documento !='':

				_ccc,_deb = sald.saldoCC( sql[2], self.documento )

				_sal = ( _ccc - _deb )
				_cad,_atraso = sald.saldoRC( sql[2], self.documento, _dAT, self.pgFil )
		
			conn.cls(sql[1])

		return _sal,_cad
	
	def pagamentos(self,event):
		
		if self.fpagamento.GetValue() != '':	self.incluirPagamento( event.GetId() )
		else:	alertas.dia(self.painel,"Forma de pagamento estar vazia...\n"+(' '*100),"Caixa: Recebimento de DAV(s)")
	
	def incluirPagamento(self,_op, vcPre = "" ):

		fpT = self.fpagamento.GetValue()[3:5]
		vcr = Decimal( self.ccDav.GetValue().replace(",","") )
		vdb = Decimal( self.crDav.GetValue().replace(",","") )

		inf01 = inf02 = inf03 = inf04 = False
		inf05 = False,""
		inf06 = inf07 = inf08 = False
		
		if self.grVencime !="":	vcPre = self.grVencime
		
		if len( login.filialLT[ self.pgFil ][35].split(";") ) >=16:	Tcc = login.filialLT[ self.pgFil ][35].split(";")[15]
		else:	Tcc = "F"

		if len( login.usaparam.split(";") ) >=8 and login.usaparam.split(";")[7] == "T" and self.ListaPrer.GetItemCount() and not self.autorizacao_muda_pagamento and not self.validarFormasPagamentos():	return
		autorizar_mudanca = self.autorizacao_muda_pagamento
		self.autorizacao_muda_pagamento = ""
		
		if Decimal( self.valorapaga.GetValue() ) > 0:

			_receber   = True
			_pagCred   = False
			_valorPago = self.recalculo(1)

			if vcPre:	dTVenc = _venci = datetime.datetime.strptime( str( vcPre ),'%d/%m/%Y').date() #-: Altera vencimento p/Pre-Recebimento
			else:	dTVenc = _venci = datetime.datetime.strptime(self.vencimento.GetValue().FormatDate(),'%d-%m-%Y').date()
			dTHoje = datetime.datetime.now().date()
			
			if _valorPago == self.result[0][37]:	_receber = False

			if _receber !=True:

				alertas.dia(self.painel,u"   Valor do DAV: "+str(self.result[0][37])+\
							  u"\n              Saldo: "+str(self.slDav.GetValue())+"\n"+(" "*100)+\
							  u"\nSem saldo para recebimentos\nFinalize com a emissão do cupom e/ou NFE",u"Recebimento de Caixa")	

			""" Bloqueio com valor a maior que o saldo """
			if fpT == "06" or fpT == "07" or fpT == "10" or fpT == "11":
			
				_vs = self.Trunca.trunca(3,Decimal(self.slDav.GetValue().replace(',','')))
				_vp = self.Trunca.trunca(3,Decimal(self.valorapaga.GetValue()))

				if Tcc == "F" and _vp > _vs:

					inf04, _receber = True, False
					if fpT == "11" and len( login.filialLT[ self.pgFil ][35].split(";") ) >= 50 and login.filialLT[ self.pgFil ][35].split(";")[49] == "T":	_receber, inf04 = True, False
					
			""" Pagamento com crédito """
			if _receber == True and self.fpagamento.GetValue()[3:5] == "10":

				valorLan = self.Trunca.trunca(3,Decimal(self.valorapaga.GetValue()))
				valorCre = self.Trunca.trunca(3,Decimal(self.ccDav.GetValue().replace(',','')))
				_vPagoCr = self.Trunca.trunca(3,Decimal(self.TConCo.GetValue()))

				if _vPagoCr !=0:	inf08, _receber = True, False
				if valorLan > valorCre and _receber !=False:	inf06, _receber = True, False

			if _receber == True and self.fpagamento.GetValue()[3:5] == "10" and self.clresul !=None and self.clresul !='' and self.clresul[0][5] !=None and self.clresul[0][5] !='' and self.clresul[0][5].split('\n')[0].split('|')[0].upper() == "TRUE":	inf07, _receber = True, False

			if dTVenc < dTHoje:

				_pa = "02.03"
				_fp = self.fpagamento.GetValue()[3:5]

				sdT = False
				snD = False
				if _fp in _pa:	sdT = True
				if _fp not in _pa:	snD = True
					
				if _fp == "06" and acs.acsm("522",False) == True:	snD, sdT = False, True
				if _fp == "07" and acs.acsm("523",False) == True:	snD, sdT = False, True

				if sdT == True:	inf01 = True
				if snD == True:	_receber, inf02 = False, True

			""" Ajuste do Vencimento - Atualização da Bandeira """
			autorizaca_data = True if fpT in ["02","03"] and len( login.filialLT[ self.pgFil ][35].split(";") ) >= 61 and login.filialLT[ self.pgFil ][35].split(";")[60] == "T" else False
			data_autorizada = u"\n\n{ Autorização p/retroagir }" if fpT in ["02","03"] and autorizaca_data else ""
		
			if dTVenc < dTHoje and not autorizaca_data:	_receber = False
			altera_data = True if dTVenc != dTHoje else False

			""" Pagamentos com Boletos-Parcelados """
			if _receber == True:

				parcelado = False
				formaspgT = "01-02-07-09-10-11"
				if fpT in formaspgT:	parcelado = True

				"""  Permitir Parcelamento para o Carteira   """
				if fpT == "07" and len( login.filialLT[ self.pgFil ][35].split(";") ) >=37 and login.filialLT[ self.pgFil ][35].split(";")[36] == "T":	parcelado = False	

				if parcelado == True and int( self.nuparcelas.GetValue() ) > 1:
				
					self.vencimento.SetValue(self.VencPadrao)
					alertas.dia(self.painel,u"Não é permitido parcelamento para a forma de pagamento selecionado\n"+(" "*120)+u"Forma de Pagamento: "+self.fpagamento.GetValue()[6:],u"Contas AReceber: Desmenbramento de Títulos")
					return

				""" Vencimentos predefinidos """
				vcpredefinido = True
				if fpT == "01" or fpT == "02" or fpT == "04" or fpT == "05" or fpT == "09" or fpT == "10":	vcpredefinido = False

				if dTVenc < dTHoje and vcpredefinido == False:

					_pa = "02.03"
					_fp = self.fpagamento.GetValue()[3:5]

					sdT = False
					snD = False

					if _fp in _pa:	sdT = True
					if _fp not in _pa:	snD = True

					if sdT == True:	inf03 = True
					if snD == True:

						alertas.dia(self.painel,u"Vencimento incompatível com a forma de pagamento\n"+(" "*120)+u"Forma de Pagamento: "+self.fpagamento.GetValue()[6:],u"Caixa: Recebimentos")
						return

				ValorToTal = self.Trunca.trunca( 3, Decimal( self.valorapaga.GetValue() ) )
				NuParcelas = int( self.nuparcelas.GetValue() )
				ValorParce = self.Trunca.trunca( 3, ( ValorToTal / NuParcelas ) )
				SomaParcel = ( ValorParce * NuParcelas )
				RestoSoma  = ( ValorToTal - SomaParcel )

				VlParcela  = ValorParce
				if RestoSoma !=0:	VlParcela = ( ValorParce + RestoSoma )
				
				_vdias = _ndias = int( self.fpagamento.GetValue()[:2] )
				if self.numeroDias.GetValue():	_vdias = _ndias = int( self.numeroDias.GetValue() )
				b_dia  = datetime.datetime.strptime(self.vencimento.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y").split("/")[0]

				self.numeroDias.SetValue('')
	
				for i in range( NuParcelas ):

					""" Se Datas Diferentes Mantem data Selecionada na primeira parcela """
					if i == 0 and altera_data:	_vdias = int(0) #--: a primeira parcela com data selecionada

					self.venc = ( _venci + datetime.timedelta( days = _vdias ) ).strftime("%d/%m/%Y")
					if self.fixadia.GetValue(): #-: Verifica a quantidade de dias do mes p/incrementa { Quando for dia fixo }

						dia, mes, ano = self.venc.split('/')
						_ndias = calendar.monthrange( int( ano ), int( mes ) )[1]
						if b_dia in ["29","30","31"] and mes == "01":	_ndias = calendar.monthrange( int( ano ), int( 2 ) )[1]

						self.venc = b_dia+"/"+self.venc.split('/')[1]+'/'+self.venc.split('/')[2]
						dia, mes, ano = self.venc.split('/')

						"""  altera o dia do mes se o dia no existir no mes atual, ex: 29/02 fica 28/02  """
						if int( dia ) > int( calendar.monthrange( int( ano ), int( mes ) )[1] ):

							self.venc = str( calendar.monthrange( int( ano ), int( mes ) )[1] ).zfill(2)+"/"+self.venc.split('/')[1]+'/'+self.venc.split('/')[2]
								
					__vlr   = ValorParce
					_vdias += _ndias

					if i == 0:	__vlr = VlParcela
					self.valorapaga.SetValue(format(__vlr,','))

					inf05 = self.inluiRecebimento( _op, autorizar_mudanca )

				_receber = False

			""" Atualiza Valores Padrao """
			self.vencimento.SetValue(self.VencPadrao)
			self.nuparcelas.SetValue('1')
			self.fpagamento.SetValue('')
			self.bandeira.SetLabel('')
			self.autoriza.SetLabel('')

			self.valorapaga.SetFocus()
			self.valoresRecebidos()

			if inf01:	alertas.dia(self.painel,u"[ 1-Data Incompatível ]\n\nVencimento: "+str(dTVenc.strftime("%d/%m/%Y"))+"\nData Atual..: "+str(dTHoje.strftime("%d/%m/%Y"))+u"\n\nForma de pagamento: CHEQUE!!"+data_autorizada+"\n"+(" "*120),"Caixa-Pagamento")
			if inf02:	alertas.dia(self.painel,u"[ 2-Data Incompatível ]\n\nVencimento: "+str(dTVenc.strftime("%d/%m/%Y"))+"\nData Atual..: "+str(dTHoje.strftime("%d/%m/%Y"))+u"\n"+(" "*120),"Caixa-Pagamento")
			if inf03:	alertas.dia(self.painel,u"3-Vencimento incompatível com a forma de pagamento\nForma de Pagamento: "+self.fpagamento.GetValue()[6:]+u" CHEQUE!!"+data_autorizada+"\n"+(" "*120),u"Caixa: Recebimentos")
			if inf04:	alertas.dia(self.painel,u"2-Valor maior que o saldo, não permitido para esta modalidade...\n"+(" "*120),u"Recebimento de Caixa")	
			if inf06:	alertas.dia(self.painel,u"[ Caixa ] Recebimento com Crédito:\n\nLançamento é maior que o crédioto...\n"+(" "*80),u"Caixa - Recebimento com Crédito!!")
			if inf07:	alertas.dia(self.painel,u"Cliente com crédito bloqueado no conta corrente...\n"+(" "*100),u"Caixa - Recebimento com Crédito!!")
			if inf08:	alertas.dia(self.painel,u"Já Houve pagamento com crédito!!\n\nPara um novo pagamento apague o pagamento anterior...\n"+(" "*100),u"Caixa - Recebimento com Crédito!!")

			if inf05[0]:	alertas.dia(self.painel, inf05[1]+"\n"+(" "*120),u"Recebimento de Caixa")

		else:	alertas.dia(self.painel,u"Valor enviado incompatível","CAIXA: Recebimento")		
		self.grVencime = "" #-: Utilizado p/gravar a da de vencimento da parcela

	""" 30-05-2015 Ajuste Valores do Recebimento """
	def valoresRecebidos( self ):

		""" 
			Ajusta as variaveis de valores
			Saldo,Troco-Rateio
		"""
		vlOriginal = self.Trunca.trunca( 3, Decimal( self.vDav.GetValue().replace(',','') ) )
			
		sReg = self.listaPagamento.GetItemCount()
		sVal = 0 #-: Valores lancados
		spCr = 0 #-: Valores c/pgTo credido

		""" Soma Valores de parcelas da lista de recebimento """
		for i in range( sReg ):
							
			sVal += Decimal( self.listaPagamento.GetItem(i, 3).GetText().replace(',','') )
			spCr += Decimal( self.listaPagamento.GetItem(i, 6).GetText().replace(',','') )

		if sVal >0:	self.TReceb.SetValue( format(sVal, ',' ) ) #-: Valor Total Recebido
		else:	self.TReceb.SetValue( "0.00" )

		if spCr >0:	self.TConCo.SetValue( format(spCr, ',' ) ) #-: Valor Total do Pagamento com Credito
		else:	self.TConCo.SetValue( "0.00" )

		"""  Ajusta Valores para Zero """
		self.slDav.SetValue("0.00")
		self.Valor_Troco.SetValue("0.00")
		self.Trocos.SetValue("0.00")
		self.valorapaga.SetValue("0.00")

		if vlOriginal > sVal: #--: Valor de Parcelas Menor, Fica Saldo """
				
			sSaldo = ( vlOriginal - sVal )
			self.slDav.SetValue(format(sSaldo,','))
			self.valorapaga.SetValue(str(sSaldo))				
	
		elif vlOriginal < sVal: #--: Valor de Parcelas Maior Sobra Troco-Rateito """
				
			sSobra = ( sVal - vlOriginal )

			self.Valor_Troco.SetValue( format( sSobra, ',' ) )
			self.Trocos.SetValue( format( sSobra, ',' ) )

	def validarFormasPagamentos( self ):

		fpag = self.fpagamento.GetValue().split(' ')[1].split('-')[0]
		passar = False
		if fpag in ['06','11']:

			pre_pagamentos = ""
			for i in range( self.ListaPrer.GetItemCount() ):

				if fpag == self.ListaPrer.GetItem( i, 0 ).GetText().split('-')[0]:	passar = True
				pre_pagamentos +=self.ListaPrer.GetItem( i, 2 ).GetText()+' '+self.ListaPrer.GetItem( i, 0 ).GetText()+' '+self.ListaPrer.GetItem( i, 1 ).GetText()+'\n'
				
			if not passar:

				mcl = u"\nRelação do pre-recebimento\n"+str( pre_pagamentos )+u'\nMudança para '+self.fpagamento.GetValue()[3:]
				mcr = u"\n1"

				autorizacoes._inform = u"{  Mudança na forma de pagamento [ Financeiro ] }\n" #-: Informacoes sobre a venda
				autorizacoes._autori = mcl #-------: Relacao das autorizacoes
				autorizacoes.auTAnTe = ''
				autorizacoes._cabeca = '' #--------: Dados do Recebimento
				autorizacoes._Tmpcmd = self.davn #-: Numero da comanda temporario 
				autorizacoes.moduloP = 23
							
				autorizacoes.filiala = self.pgFil
				auto_frame = autorizacoes(parent=self,id=-1)
				auto_frame.Centre()
				auto_frame.Show()	
			
		else:	passar = True #	return True	
		
		return passar
		
	def autorizarMudancaPagamento( self, autorizacao ):

		self.autorizacao_muda_pagamento = autorizacao
		alertas.dia( self, u"{ Recebimento autorizado }\n\n"+str( autorizacao )+u"\n\n1 - Click no botão p/incluir o pagamento\n"+(" "*130),u"Autorização")
		
	def receberPagamento(self,__bandeira,_autoriza):

		""" Utilizado atraves da classe regBandeira conectar.py  """
		self.bandeira.SetLabel(__bandeira)
		self.autoriza.SetLabel(_autoriza)
		self.incluirPagamento(151)
	
	def inluiRecebimento(self,opcao, mudanca_forma_pagamento ):
		
		""" Pagamento com cheque """
		chq = True
		if self.chdocum =='':	chq = False
		if self.compens =='':	chq = False
		if self.chcorre =='':   chq = False
		if self.chbanco =='':   chq = False
		if self.chagenc =='':   chq = False
		if self.chnumer =='':   chq = False
		if self.chconta =='':   chq = False

		if not chq and self.fpagamento.GetValue()[3:5] in ["02","03"]:

			informacao = u"Pagamento em cheque: Dados incompletos\n\n\
			\n\nCFP-CNPJ: "+str(self.chdocum)+u"\nNome correntista: "+str(self.chcorre)+u"\nCOMP: "+str(self.compens)+u"\nNº Banco: "+str(self.chbanco)+u"\nAgencia: "+str(self.chagenc)+u"\nNº Cheque: "+str(self.chnumer)+u"\nNº Conta: "+str(self.chconta)

			return True,informacao
		
		_valorPago = self.recalculo(1)

		if opcao == 151: #-->[ Inclusao ]

			indice = self.listaPagamento.GetItemCount()
			ordem  = ( indice + 1 )
			self.listaPagamento.InsertStringItem(indice,str(ordem).zfill(3))

		else:	indice = self.listaPagamento.GetFocusedItem()

		_vencim = datetime.datetime.strptime(self.vencimento.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		if chq:	self.venc = _vencim
			
		_vlDavs = self.result[0][37]
		_vlLanc = self.Trunca.trunca(2,Decimal(self.valorapaga.GetValue()))
		_vlLand = Decimal( _vlLanc.replace(',','.') )

		_vlrece = _vlLand
		_vlPago = ( _vlLand + _valorPago )
		_Trocos = 0
				
		if( _vlPago > self.result[0][37] ):
				
			_vlLand = ( self.result[0][37] - _valorPago )
			_Trocos = ( _vlPago - self.result[0][37] )

		self.listaPagamento.SetStringItem(indice,1, self.venc)	
		self.listaPagamento.SetStringItem(indice,2, self.fpagamento.GetValue()[3:])	
		self.listaPagamento.SetStringItem(indice,3, format(_vlrece,','))	
		self.listaPagamento.SetStringItem(indice,4, format(_vlLand,','))	
		self.listaPagamento.SetStringItem(indice,5, format(_Trocos,','))
		self.listaPagamento.SetStringItem(indice,6,'0.00')

		if 	self.fpagamento.GetValue()[3:5] == "10":
			self.listaPagamento.SetStringItem(indice,6, format(_vlLand,','))

		self.listaPagamento.SetStringItem(indice,7, self.chdocum )
		self.listaPagamento.SetStringItem(indice,8, self.chcorre )
		self.listaPagamento.SetStringItem(indice,9, self.chbanco )
		self.listaPagamento.SetStringItem(indice,10,self.chagenc )
		self.listaPagamento.SetStringItem(indice,11,self.chnumer )
		self.listaPagamento.SetStringItem(indice,12,self.chconta )
		self.listaPagamento.SetStringItem(indice,13,self.chinfor )
		self.listaPagamento.SetStringItem(indice,14,self.bandeira.GetLabel())
		self.listaPagamento.SetStringItem(indice,16,self.autoriza.GetLabel())
		self.listaPagamento.SetStringItem(indice,17,self.compens )
		self.listaPagamento.SetStringItem(indice,18,mudanca_forma_pagamento)
		
		self.listaPagamento.SetItemTextColour(indice,'#7F7F7F')
		if indice % 2:	self.listaPagamento.SetItemBackgroundColour(indice, "#EFF3F7")

		if 	self.fpagamento.GetValue()[3:5] == "10":	self.listaPagamento.SetItemTextColour(indice,'#A52A2A')
		if 	self.fpagamento.GetValue()[3:5] == "11":	self.listaPagamento.SetItemTextColour(indice,'#3B6A99')

		return False,""
		
	def recalculo(self,_Tp):

		_registro = self.listaPagamento.GetItemCount()
		_valor    = 0

		if _registro > 0 or _Tp == 3:
				
			_indice = 0
			_valor  = Decimal('0.00')
			_receb  = Decimal('0.00')
			_troco  = Decimal('0.00')
			_pgTCr  = Decimal('0.00')
				
			_ordem  = 1
			for i in range(_registro):
						
				_vlt1 = Decimal( self.listaPagamento.GetItem(_indice, 3).GetText().replace(',','') )
				_vlt2 = Decimal( self.listaPagamento.GetItem(_indice, 4).GetText().replace(',','') )
				_vlt3 = Decimal( self.listaPagamento.GetItem(_indice, 5).GetText().replace(',','') )
				_vlt4 = Decimal( self.listaPagamento.GetItem(_indice, 6).GetText().replace(',','') )
				self.listaPagamento.SetStringItem(_indice,0,str(_ordem).zfill(3))

				if _Tp == 3 and _vlt3 != 0:

					self.listaPagamento.SetStringItem(_indice,4,str(_vlt1))
					self.listaPagamento.SetStringItem(_indice,5,"0")

					_vlt1 = _vlt2
					_vlt3 = Decimal('0.00')
					
				#-------------:
				_valor += _vlt1 
				_receb += _vlt2
				_troco += _vlt3
				_pgTCr += _vlt4

				_indice +=1
				_ordem  +=1

		self.valorapaga.SetFocus()
		
		return _valor
			
	def apagaritems(self,event):

		_id = event.GetId()
		_in = self.listaPagamento.GetFocusedItem()
		_QT = self.listaPagamento.GetItemCount()
		if _QT != 0:
			
			if event.GetId() == 152 or event.GetId() == 153:

				_regis = u"Todos os Lançamentos"
				if event.GetId() == 152:	_regis = u"Registro: "+str(_in+1)

				if event.GetId() == 152:	self.listaPagamento.DeleteItem(_in)
				if event.GetId() == 153:	self.listaPagamento.DeleteAllItems()
			
				self.valoresRecebidos()

	def desenho(self,event):
			
		dc = wx.PaintDC(self.painel)     

		dc.SetTextForeground("#6A92B9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"CAIXA - Recebimento de DAV(s)", 0, 370, 90)

		dc.SetTextForeground("#357489")
		dc.DrawRotatedText(u"Histórico e Autorizações de DAVs", 0, 615, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.SetTextForeground("#0B8FBA")
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Filial-{"+str( self.pgFil )+"}", 730, 210, 90)
		#dc.DrawRotatedText(u"Filial-Pagamento\n{"+str( self.pgFil )+"}", 716, 210, 90)

		dc.DrawRoundedRectangle(520, 2,   225,  100, 3) #-->[ Caixa ]
		dc.DrawRoundedRectangle(520, 110, 225,  155, 3) #-->[ Atalhos ]
		dc.DrawRoundedRectangle(520, 268, 90,   108, 3) #-->[ Formas de Pagamento ]
		dc.DrawRoundedRectangle(613, 268, 132,  108, 3) #-->[ Formas de Pagamento ]
		dc.DrawRoundedRectangle(10,  268, 507,  72,  3) #-->[ Formas de Pagamento ]
		dc.DrawRoundedRectangle(10,  312, 507,  64,  3) #-->[ Formas de Pagamento ]

		dc.SetFont(wx.Font(6, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText( u"Valor Total do DAV - Saldo", 523,3, 0)
		
	def fechanfe(self,event):

		if not self.validaPagamentosFuturos():	return
		ic = self.parente.ListaRec.GetFocusedItem()

		rT = False
		if event.GetId() == 160:	rT = self.fechaTeste('160')

		if self.parente.ListaRec.GetItem(ic,43).GetText() != 'S':
			alertas.dia(self.painel,u"Cliente não cadastrado !!\n"+(" "*80),u"Caixa: Emissão de NFE")	
			rT = False
				
		elif self.parente.ListaRec.GetItem(ic,31).GetText() == '':
			
			alertas.dia(self.painel,u"CPF-CNPJ do Cliente não cadastrado !!\n"+(" "*80),u"Caixa: Emissão de NFE")	
			rT = False

		if os.path.exists('srv/rnfe.cnf') !=True:
			
			alertas.dia(self.painel,u"[rnfe.cnf] Arquivo de códigos de rejeição, não localizado\n"+(" "*90),u"DANFE Emissão")
			rT = False
	
		if rT == True:
				
			editadanfe.davNumero = self.result[0][2]
			editadanfe.dccliente = self.result[0][39]
			editadanfe.cdcliente = self.result[0][3]
			editadanfe.idefilial = self.result[0][54]
			editadanfe.vinculado = self.result[0][112]
			
			editadanfe.identifca = '160'
			editadanfe.listaRece = self.listaPagamento
			editadanfe.listaQuan = self.listaPagamento.GetItemCount()
			editadanfe.tiponfrma = ""
					
			ecfnfe_frame=editadanfe(parent=self,id=-1)
			ecfnfe_frame.Centre()
			ecfnfe_frame.Show()

	def aTualizaLista(self):	self.parente.selecionar(wx.EVT_BUTTON)
	def fechaTeste(self,idSaida):

		_finaliza = True
		_rateiocx = True
		
		""" Sobra no Caixa [ Abilita Rateio ] """
		if Decimal(self.Trocos.GetValue().replace(',','')) != 0 and Decimal(self.Valor_Rateio.GetValue().replace(',','')) == 0:

			Finaliza = wx.MessageDialog(self,u"1-Consta uma sobra de caixa:\n\nTroco: "+self.Trocos.GetValue()+u"\n\nGostaria de fazer rateio?\n"+(" "*100),u"DAV-Fechamento",wx.YES_NO)
			if Finaliza.ShowModal() ==  wx.ID_YES:
				
				self.Valor_Rateio.SetFocus()
				_finaliza = False
				_rateiocx = False
				
			del Finaliza
		
		if Decimal(self.slDav.GetValue().replace(',','')) !=0:

			alertas.dia(self.painel,u"2-Consta um saldo de caixa:\n\nSaldo: "+str(self.slDav.GetValue())+"\n"+(" "*100),u"Caixa: Fechamento")
			_finaliza = False

		""" Envia para Rateio """
		if _rateiocx == False:

			srateio.sobra = Decimal( self.Trocos.GetValue().replace(',','') )
			srateio.docum = self._cnpj_cpf
			raT_frame=srateio(parent=self,id=-1)
			raT_frame.Centre()
			raT_frame.Show()

		return _finaliza

	def fechamento( self, idNF, nfe, filial = '' ):

		soco = socorrencia()
		
		Nregistro = self.listaPagamento.GetItemCount()

		Nindice = 0
		_relaca = 0
		relacao = {}
		NomeCl  = self.result[0][4]
		DocuCl  = self.result[0][39]
		vFrete  = self.result[0][23]
		vAcres  = self.result[0][24]
		vDesco  = self.result[0][25]
		vProdu  = self.result[0][36]
		ibptec  = self.result[0][72]
		baixar  = True
		LanFin  = False

		finRINI = finRFIM = ""
		fina = finf = faTu = False

		for i in range( Nregistro ):

			Rvalo = str( self.listaPagamento.GetItem(Nindice, 3).GetText() )	
			Rvlrc = str( self.listaPagamento.GetItem(Nindice, 4).GetText() )
			Rfecf = str( self.listaPagamento.GetItem(Nindice,15).GetText() )
			fpagT = str( self.listaPagamento.GetItem(Nindice, 2).GetText() )

			""" Relaciona paga impressao ECF """
			relacao[_relaca] = Rfecf,Rvalo,Rvlrc
			_relaca +=1
			Nindice +=1

		nucoo = nuccf = nufab = ecfseq = ''

		""" Emissao do Cuporm Fiscal """
		if baixar == True:

			sald = formasPagamentos()
			conn = sqldb()
			sql  = conn.dbc("Caixa: Recebimento", fil = filial, janela = self.painel )

			if sql[0] == True:

				"""   Validando o recebimento da DAv { Alguns clientes estar deixa duas sessoes abertas e recebendo o dav duas vezes  }   """
				if sql[2].execute("SELECT cr_urec,cr_erec,cr_hrec FROM cdavs WHERE cr_urec!='' and cr_ndav='"+self.davn+"'"):
					
					recebido = sql[2].fetchone()
					conn.cls( sql[1] )
					
					alertas.dia( self, u"{ DAV Nº "+self.davn+u" Recebido !! }\n\nRecebimento :"+recebido[0]+' '+format( recebido[1],'%d/%m/%Y' )+' '+str( recebido[2] )+"\n"+(" "*140),u"Dav Recebido")
					return
				
				"""  Relacionar produtos para expedicao por departamento  """
				relacao_items_expedicao = []
				if sql[2].execute("SELECT it_codi,it_nome,it_unid,it_fabr,it_ende,it_quan,it_grup,it_estf FROM idavs WHERE it_ndav='"+ self.davn +"'"):

					for ri in sql[2].fetchall():
						
						relacao_items_expedicao.append( ri[0] +'|' + ri[2]+'|'+ str( ri[5] ) +'|'+ ri[6] +'|'+ ri[1] +'|'+ ri[3] +'|'+ ri[4] +'|'+ str( ri[7] ) )
					
				"""  Baixa do credito avulso  """
				nDocu = self.result[0][39]
				if self.numer_TicheT.GetValue().strip() !="":	nDocu = self.numer_TicheT.GetValue().strip()
				
				_cccr,_ccdb = sald.saldoCC( sql[2], nDocu )

				IFR = datetime.datetime.now().strftime("%d-%m-%Y") #---------->[ Data de Marcacao de finalizacao de Recebimento no  contas a receber local ]
				
				EMD = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
				DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
				CXN = str( login.usalogin.strip() ) #------------------------->[ Nome do Caixa ]
				CXC = login.uscodigo #---------------------------------------->[ Codigo do Caixa ]
				CXF = login.emcodigo #---------------------------------------->[ Filial do Caixa ]
				VRC = self.TReceb.GetValue().replace(',','') #---------------->[ Valor Recebido ]
				TRO = self.Trunca.trunca(3,Decimal(self.Trocos.GetValue().replace(',',''))) #->[ Troco ]
				CCR = self.Trunca.trunca(3,Decimal(self.Valor_Rateio.GetValue().replace(',',''))) #->[ Lancamento do Credito no CC Rateio do Troco ]
				CDB = self.Trunca.trunca(3,Decimal(self.TConCo.GetValue().replace(',',''))) #->[ Lancamento do Debito no CC (Pagamento com credito)]
				RTR = self.Trunca.trunca(3,Decimal(self.Valor_Troco.GetValue().replace(',',''))) #->[ Sobra de Troco do Rateio ]
				emi = EMD+' '+DHO+' '+login.usalogin
				
				"""  Guarda o Numero da devolucao para pagamento avulso do credito  """
				if self.numer_TicheT.GetValue().strip() !="" and Decimal( CDB ) !=0:	avu = self.numer_TicheT.GetValue().strip()
				else:	avu = ""
				
				if LanFin == True:	finRINI = "T|"+str( filial )+"|"+str( filial )+"|"+str( IFR )+"|"+str( DHO )+"|"+str( login.usalogin )

				_cdcl = self.result[0][3]
				_nmcl = self.result[0][4] if type( self.result[0][4] ) == unicode else self.result[0][4].decode("UTF-8")
				_fant =	self.result[0][5]
				_docu = self.result[0][39]
				_cdvd = self.result[0][43]
				_vend = self.result[0][44]
				_idfc = self.result[0][55]
				
				if Nregistro > 1:	FRC = u"20-Diversos"
				else:	FRC = str( self.listaPagamento.GetItem(0, 2).GetText() )

				#--->[  Contabiliza Formas de Pagamentos ]
				Indi = 0

				vDinh = Decimal('0.00')
				vChAv = Decimal('0.00')
				vChPr = Decimal('0.00')
				vCTcr = Decimal('0.00')
				vCTdb = Decimal('0.00')
				vFTbl = Decimal('0.00')
				vFTca = Decimal('0.00')
				vFina = Decimal('0.00')
				vTick = Decimal('0.00')
				vPgCr = Decimal('0.00')
				vDeCo = Decimal('0.00')
				vRcLo = Decimal('0.00')
				vFinR = Decimal('0.00')
				
				""" Guarda as Fomras de Pagamento em campo TEXTO """
				mudanca_pagamentos = ""
				guardar = ""
				parcela = ""
				for i in range( Nregistro ):

					FpgTo = self.listaPagamento.GetItem(Indi,2).GetText().split("-")[0]
					valor = Decimal( str(self.listaPagamento.GetItem(Indi,3).GetText()).replace(',','') )
					vparc = Decimal( str(self.listaPagamento.GetItem(Indi,4).GetText()).replace(',','') )
					if self.listaPagamento.GetItem(Indi,18).GetText():	mudanca_pagamentos +=self.listaPagamento.GetItem(Indi,18).GetText()+'\n'

					gParc = self.davn+"-"+str( self.listaPagamento.GetItem(Indi,0).GetText() )
					gVenc = str( self.listaPagamento.GetItem(Indi,1).GetText() )
					gForm = str( self.listaPagamento.GetItem(Indi,2).GetText() )
					gValo = str( self.listaPagamento.GetItem(Indi,3).GetText() )
					guardar += gParc+";"+gVenc+";"+gForm+";"+gValo+"|"
					parcela += FpgTo+";"+str( vparc )+"|"

					if FpgTo == "01":	vDinh +=valor
					if FpgTo == "02":	vChAv +=valor
					if FpgTo == "03":	vChPr +=valor
					if FpgTo == "04":	vCTcr +=valor
					if FpgTo == "05":	vCTdb +=valor
					if FpgTo == "06":	vFTbl +=valor
					if FpgTo == "07":	vFTca +=valor
					if FpgTo == "08":	vFina +=valor
					if FpgTo == "09":	vTick +=valor
					if FpgTo == "10":	vPgCr +=valor
					if FpgTo == "11":	vDeCo +=valor
					if FpgTo == "12":	vRcLo +=valor
					
					Indi +=1

				if mudanca_pagamentos:	mudanca_pagamentos = u"{ Mudanca no recebimento }\n"+mudanca_pagamentos
				if idNF == '160':

					""" Atualiza Recebimento com Emissao do DANFE """

					_gravar = "UPDATE cdavs SET cr_nfca='',\
					cr_urec='"+CXN+"',cr_erec='"+EMD+"',cr_hrec='"+DHO+"',cr_cxcd='"+CXC+"',cr_usac='',\
					cr_rece='"+FRC+"',cr_vlrc='"+str(VRC)+"',cr_vltr='"+str(TRO)+"',\
					cr_ccre='"+str(CCR)+"',cr_cdeb='"+str(CDB)+"',cr_ficx='"+CXF+"',\
					cr_tror='"+str(RTR)+"',cr_dinh='"+str(vDinh)+"', cr_chav='"+str(vChAv)+"',\
					cr_chpr='"+str(vChPr)+"',cr_ctcr='"+str(vCTcr)+"',cr_ctde='"+str(vCTdb)+"',\
					cr_fatb='"+str(vFTbl)+"',cr_fatc='"+str(vFTca)+"',cr_fina='"+str(vFina)+"',\
					cr_tike='"+str(vTick)+"',cr_pgcr='"+str(vPgCr)+"',cr_depc='"+str(vDeCo)+"',\
					cr_reca='1',cr_rcbl='"+str(vRcLo)+"',cr_guap='"+str( guardar )+"',cr_vpar='"+str( parcela )+"',cr_cavu='"+str( avu )+"' WHERE cr_ndav='"+self.davn+"'"

				else:

					""" Atualiza Recebimento com emissao do cupom """

					_gravar = "UPDATE cdavs SET \
					cr_cupo='"+str(nucoo)+"',cr_ecem='"+str(emi)+"',cr_ecca='',\
					cr_urec='"+CXN+"',cr_erec='"+EMD+"',cr_hrec='"+DHO+"',cr_cxcd='"+CXC+"',cr_usac='',\
					cr_rece='"+FRC+"',cr_vlrc='"+str(VRC)+"',cr_vltr='"+str(TRO)+"',\
					cr_ccre='"+str(CCR)+"',cr_cdeb='"+str(CDB)+"',cr_ficx='"+CXF+"',\
					cr_tror='"+str(RTR)+"',cr_dinh='"+str(vDinh)+"', cr_chav='"+str(vChAv)+"',\
					cr_chpr='"+str(vChPr)+"',cr_ctcr='"+str(vCTcr)+"',cr_ctde='"+str(vCTdb)+"',\
					cr_fatb='"+str(vFTbl)+"',cr_fatc='"+str(vFTca)+"',cr_fina='"+str(vFina)+"',\
					cr_tike='"+str(vTick)+"',cr_pgcr='"+str(vPgCr)+"',cr_depc='"+str(vDeCo)+"',\
					cr_ccfe='"+str(nuccf)+"',cr_reca='1',cr_rcbl='"+str(vRcLo)+"',cr_ecfb='"+str(nufab.strip())+"',\
					cr_ecfs='"+str(ecfseq)+"',cr_guap='"+str( guardar )+"',cr_vpar='"+str( parcela )+"',cr_cavu='"+str( avu )+"' WHERE cr_ndav='"+self.davn+"'"

				_retorno = 0

				try:

					""" Grava o Recebimento no cadastro de Controle de DAV """
					_retorno = sql[2].execute(_gravar)
					
					""" Grava o Contas areceber e o conta corrente """
					_indice   = 0

					"""   Liquidacao Atuomatica de Recebimentos no ContasAreceber p/CCredito, CDebito, CH.Avista, Cheque Predatado, Deposito em conta  """
					lqcD = "F"
					lqcC = "F"
					lqcH = "F"
					lqcP = "F"
					lqDC = "F"

					if len( login.filialLT[ filial ][35].split(";") ) >=34:	lqcD = login.filialLT[ filial ][35].split(";")[33] #-: Cartão Debito
					if len( login.filialLT[ filial ][35].split(";") ) >=35:	lqcC = login.filialLT[ filial ][35].split(";")[34] #-: Cartão Credito
					if len( login.filialLT[ filial ][35].split(";") ) >=36:	lqcH = login.filialLT[ filial ][35].split(";")[35] #-: Ch.Avista
					if len( login.filialLT[ filial ][35].split(";") ) >=38:	lqDC = login.filialLT[ filial ][35].split(";")[37] #-: Deposito em Conta
					if len( login.filialLT[ filial ][35].split(";") ) >=42:	lqcP = login.filialLT[ filial ][35].split(";")[41] #-: Cheque Predatado

					for i in range( Nregistro ):

						_parc = str(self.listaPagamento.GetItem(_indice,0).GetText()[1:])

						_venc = str(self.listaPagamento.GetItem(_indice,1).GetText())	
						_venc = format(datetime.datetime.strptime(_venc, "%d/%m/%Y"),"%Y/%m/%d") 				
						_fpag = self.listaPagamento.GetItem(_indice,2).GetText()

						_vlrc = str(self.listaPagamento.GetItem(_indice,3).GetText().replace(',',''))				
						_valo = str(self.listaPagamento.GetItem(_indice,4).GetText().replace(',',''))
						
						_docc = str(self.listaPagamento.GetItem(_indice,7).GetText())
						_corr = self.listaPagamento.GetItem(_indice,8).GetText() 
						_banc = self.listaPagamento.GetItem(_indice,9).GetText() 
						_agen = self.listaPagamento.GetItem(_indice,10).GetText()
						_cheq = self.listaPagamento.GetItem(_indice,11).GetText()
						_cont = self.listaPagamento.GetItem(_indice,12).GetText()
						_dadc = self.listaPagamento.GetItem(_indice,13).GetText()
						_band = self.listaPagamento.GetItem(_indice,14).GetText()					
						_fecf = self.listaPagamento.GetItem(_indice,15).GetText()					
						_ccar = self.listaPagamento.GetItem(_indice,16).GetText() #--:[ Comprovante-Autorizacao de Cartao de Credito ]
						_comp = self.listaPagamento.GetItem(_indice,17).GetText() #--:[ COMP-Compensacao do cheque ]

						Faturado = False
						if _fpag[:2]=="02" or _fpag[:2]=="03" or _fpag[:2]=="04":	Faturado = True
						if _fpag[:2]=="05" or _fpag[:2]=="06" or _fpag[:2]=="07":	Faturado = True
						if _fpag[:2]=="08" or _fpag[:2]=="09" or _fpag[:2]=="11":	Faturado = True
						if _fpag[:2]=="12":	Faturado = True

					
						"""  Liquidacao Automatica de Titulos  """
						LiqBaixa = False
						if _fpag[:2]=="02" and lqcH == "T":	LiqBaixa = True #-: Ch.Avista
						if _fpag[:2]=="03" and lqcP == "T":	LiqBaixa = True #-: Ch.Predado
						if _fpag[:2]=="04" and lqcC == "T":	LiqBaixa = True #-: Cartão Credito
						if _fpag[:2]=="05" and lqcD == "T":	LiqBaixa = True #-: Cartão Debito
						if _fpag[:2]=="11" and lqDC == "T":	LiqBaixa = True #-: Deposito em contalqDC

						if Faturado == True:
							
							finRFIM = ""
							
							_grec = "INSERT INTO receber (rc_ndocum,rc_origem,rc_nparce,rc_vlorin,rc_apagar,rc_formap,rc_dtlanc,rc_hslanc,rc_cdcaix,rc_loginc,\
														  rc_clcodi,rc_clnome,rc_clfant,rc_cpfcnp,rc_clfili,rc_indefi,rc_idfcli,rc_vencim,rc_bandei,rc_chdocu,\
														  rc_chcorr,rc_chbanc,rc_chagen,rc_chcont,rc_chnume,rc_chdado,rc_clcada,rc_vended,rc_chcomp,rc_autori,\
														  rc_notafi,rc_numcoo,rc_cdvend,rc_fimtra,rc_envfil)\
														  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																 %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																 %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																 %s,%s,%s,%s,%s)"

							_liqd = "INSERT INTO receber (rc_ndocum,rc_origem,rc_nparce,rc_vlorin,rc_apagar,rc_formap,rc_dtlanc,rc_hslanc,rc_cdcaix,rc_loginc,\
														  rc_clcodi,rc_clnome,rc_clfant,rc_cpfcnp,rc_clfili,rc_indefi,rc_idfcli,rc_vencim,rc_bandei,rc_chdocu,\
														  rc_chcorr,rc_chbanc,rc_chagen,rc_chcont,rc_chnume,rc_chdado,rc_clcada,rc_vended,rc_chcomp,rc_autori,\
														  rc_notafi,rc_numcoo,rc_cdvend,rc_fimtra,rc_envfil,\
														  rc_bxcaix,rc_bxlogi,rc_vlbaix,rc_dtbaix,rc_hsbaix,rc_formar,rc_status,rc_canest,rc_recebi,rc_baixat,rc_modulo )\
														  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																 %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																 %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																 %s,%s,%s,%s,%s,\
																 %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

							"""
							   Inserir no Contas Areceber Local 
							"""
								
							if LiqBaixa == False:

								sql[2].execute( _grec, ( self.davn, 'V', _parc, _valo, _vlrc, _fpag, EMD, DHO, CXC, CXN,\
										_cdcl, _nmcl, _fant, _docu, login.emcodigo, filial, _idfc, _venc, _band, _docc,\
										_corr, _banc, _agen, _cont, _cheq, _dadc, self.result[0][75], _vend, _comp, _ccar,\
										nfe, str(nucoo), str(_cdvd), str( finRINI ), str( finRFIM ) ) )
							
							"""
							   Inserir no Contas Areceber Local com liquidacao automatica
							"""
							if LiqBaixa == True:

								hisB = u'Liquidacao Automatica no recebimento do caixa'
								sql[2].execute( _liqd, ( self.davn, 'V', _parc, _valo, _vlrc, _fpag, EMD, DHO, CXC, CXN,\
										_cdcl, _nmcl, _fant, _docu, login.emcodigo, filial, _idfc, _venc, _band, _docc,\
										_corr, _banc, _agen, _cont, _cheq, _dadc, self.result[0][75], _vend, _comp, _ccar,\
										nfe, str(nucoo), str(_cdvd), str( finRINI ), str( finRFIM ), CXC, CXN, _vlrc, EMD, DHO, _fpag, '2', hisB, '2', '2', 'CAIXA' ) )
										
								_ocorr = "insert into ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde)\
										  values (%s,%s,%s,%s,%s)"			

								_lan  = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
								_tip  = u"Caixa"
								_oco  = u"Recebimento no Caixa c/Liquidacao Automatica\n"

								sql[2].execute( _ocorr, ( self.davn, _lan, _oco, _tip, filial ) )
					
						_indice +=1

					if Decimal( CCR ) !=0:

						_ccsaldo = ( ( _cccr - _ccdb ) +  CCR )
						_hist = u'Recebimento no Caixa Lançamento de Crédito'
						_gcon = "INSERT INTO conta (cc_lancam,cc_horala,\
								cc_usuari,cc_usnome,\
								cc_cdfili,cc_idfila,\
								cc_davlan,cc_cdclie,\
								cc_nmclie,cc_docume,\
								cc_idfcli,cc_origem,\
								cc_histor,cc_credit,\
								cc_saldos) values('"+EMD+"','"+DHO+"',\
								'"+CXC+"','"+CXN+"',\
								'"+login.emcodigo+"','"+ filial +"',\
								'"+self.davn+"','"+_cdcl+"',\
								'"+_nmcl+"','"+_docu+"',\
								'"+_idfc+"','RC',\
								'"+_hist+"','"+str(CCR)+"','"+str(_ccsaldo)+"')"
								
						sql[2].execute(_gcon)

					if Decimal( CDB ) !=0:

						_ccsaldo = ( _cccr - _ccdb - CDB )
						"""  Baixa do credito avulso  """
						_his = u"Recebimento no Caixa PGTO c/Crédito"
						if self.numer_TicheT.GetValue().strip() !="":

							_docu = self.numer_TicheT.GetValue().strip()
							_his =u"Recbimento Avulso PGTO p/Dav: "+str( self.davn )

						_gdeb = "INSERT INTO conta (cc_lancam,cc_horala,\
								cc_usuari,cc_usnome,\
								cc_cdfili,cc_idfila,\
								cc_davlan,cc_cdclie,\
								cc_nmclie,cc_docume,\
								cc_idfcli,cc_origem,\
								cc_histor,cc_debito,\
								cc_saldos) values('"+EMD+"','"+DHO+"',\
								'"+CXC+"','"+CXN+"',\
								'"+login.emcodigo+"','"+ filial +"',\
								'"+self.davn+"','"+_cdcl+"',\
								'"+_nmcl+"','"+_docu+"',\
								'"+_idfc+"','RD',\
								'"+_his+"','"+str(CDB)+"','"+str(_ccsaldo)+"')"
								
						sql[2].execute(_gdeb)

					sql[1].commit()
					fina = True 
				
				except Exception as _reTornos:

					sql[1].rollback()
					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
				
				""" Fechamento das Tabelas """
				conn.cls(sql[1])
				if fina:

					relacao_items_expedicao and len( login.filialLT[filial][35].split(";") ) >= 98 and login.filialLT[filial][35].split(";")[97]
						
					_nc = str( nucoo )
					
					if idNF == '160':	_nc +="[ Emissao de NFE ]"

					historico_soco = u"Recebimento de DAVs "+_nc
					if mudanca_pagamentos:	historico_soco += '\n\n'+mudanca_pagamentos
						
					soco.gravadados(self.davn,historico_soco,u"CAIXA", Filial = filial )

					"""  Enviar para as expedicos por departamento se nao tiver data de entrega programada """
					if not self.result[0][21] and relacao_items_expedicao and len( login.filialLT[filial][35].split(";") ) >= 99 and login.filialLT[filial][35].split(";")[98] == "T":

						expedicao_departamento.expedicionarProdutos( self.davn, filial, relacao_items_expedicao, self.result[0][4], self.result[0][44], self )
					
				if fina == False:	alertas.dia(self.painel,u"1-Recebimento não finalizado!!\n \nRetorno: "+ _reTornos +'\n'+(" "*140),u"Retorno")	

				if fina == True:	self.parente.selecionar(wx.EVT_BUTTON)
				if fina == True and idNF != '160' and nfe != u'nfce':	self.voltar(wx.EVT_BUTTON)

	def Tvalores(self,valor,idfy):

		if idfy == 130:
			
			if valor == '':	valor = self.slDav.GetValue()

			if Decimal(valor) > Decimal('99999.99') or Decimal(valor) == 0:
				valor = self.slDav.GetValue()
				alertas.dia(self.painel,u"Valor enviado é incompatível!!",u"Caixa: Recebimento")

			self.valorapaga.SetValue(str(valor))
		
		elif idfy == 120:

			if valor == '':	valor = "0.00"

			if Decimal(valor) > Decimal('99999.99') or Decimal(valor) == 0:
				valor = "0.00"
				alertas.dia(self.painel,u"Valor enviado é incompatível!!",u"Caixa: Recebimento")

			self.alparc.SetValue(str(valor))

		elif idfy == 123:
			
				cheque = str(valor).replace('.','')
				cheque = cheque.replace(',','')
				self.alcheq.SetValue(cheque)

class pgdevolucao(wx.Frame):
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.r = recibo()
		self.e = listaemails()
		self.f = self.p.fl
		
		mkn    = wx.lib.masked.NumCtrl
		
		wx.Frame.__init__(self, parent, id, u'Caixa: Recebimento de Devoluções', size=(593,306), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sairDev)

		self.p.Disable()
		
		if len( login.filialLT[ self.p.fl ][35].split(";") ) >=21:	self.DesBlock = login.filialLT[ self.p.fl ][35].split(";")[20].split(',')
		else:	self.DesBlock = [""]
		
		wx.StaticText(self.painel,-1,u"Nº Devolução", pos=(15, 10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Emissão",      pos=(125,10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Código",       pos=(15, 55)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"CPF-CPNJ",     pos=(125,55)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Descrição do Cliente",            pos=(15, 100)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Saldo\nDevolução",      pos=(18, 150)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Devolução\nem dinheiro", pos=(18, 200)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Transferir\nconta corrente", pos=(133,200)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Motivo da Devolução", pos=(235,55)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Dinheiro:",         pos=(393, 7)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Cartão Débito:",    pos=(393, 32)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Cartão Crédito:",   pos=(393, 57)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Cheque Avista:",    pos=(393, 82)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Cheque Predatado:", pos=(393,107)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Financeira:",       pos=(393,132)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Boleto:",           pos=(393,157)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Carteira-Loja:",    pos=(393,182)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"PgTo Crédito:",     pos=(393,207)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Deposito em Conta:",pos=(393,232)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Receber no Local:", pos=(392,257)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"QT de Devoluções", pos=(3,  262)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"DevoluçãoDinheiro",pos=(103,262)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Transferências",   pos=(203,262)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Total",            pos=(303,262)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.auT = wx.StaticText(self.painel,-1,u"", pos=(3,252))
		self.auT.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.auT.SetForegroundColour('#A52A2A')

		self.inf = wx.StaticText(self.painel,-1,u"", pos=(3,250))
		self.inf.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.inf.SetForegroundColour('#A52A2A')

		rate = wx.StaticText(self.painel,-1,u"Rateio\nDevolução", pos=(133,150))
		rate.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		rate.SetForegroundColour('#1E5F1E')

		vinc = wx.StaticText(self.painel,-1,u"Devolução vinculado\npedido nº: "+str(self.p.resul[0][78]), pos=(240,150))
		vinc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		vinc.SetForegroundColour('#1E5F1E')

		self.sDisp = wx.StaticText(self.painel,-1,u"Saldo Disponivel", pos=(133,175))
		self.sDisp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.sDisp.SetForegroundColour('#1E5F1E')

		if self.p.resul[0][74] == '2':

			esto = wx.StaticText(self.painel,-1,u"[ <Estornado> ]", pos=(240,250))
			esto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			esto.SetForegroundColour('#A52A2A')

		if self.p.resul[0][75] == '':

			cnao = wx.StaticText(self.painel,-1,u"Cliente não cadastrado", pos=(252,100))
			cnao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			cnao.SetForegroundColour('#A52A2A')

		emiss = format( self.p.resul[0][11],'%d/%m/%Y' )+' '+str( self.p.resul[0][12] )+' '+str( self.p.resul[0][9] )

		nDev = wx.TextCtrl(self.painel,-1,self.p.resul[0][2], pos=(12,22), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		nDev.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		nDev.SetBackgroundColour('#E5E5E5')

		nemi = wx.TextCtrl(self.painel,-1,emiss, pos=(122,22), size=(260,22), style=wx.TE_READONLY)
		nemi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		nemi.SetBackgroundColour('#E5E5E5')
				
		ncod = wx.TextCtrl(self.painel,-1,str(self.p.resul[0][0]), pos=(12,67), size=(100,22), style=wx.TE_READONLY)
		ncod.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		ncod.SetBackgroundColour('#E5E5E5')

		ndoc = wx.TextCtrl(self.painel,-1,str(self.p.resul[0][39]), pos=(122,67), size=(100,22), style=wx.TE_READONLY)
		ndoc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		ndoc.SetBackgroundColour('#E5E5E5')

		"""  Formas de Recebimentos  """
		self.rcbDin = wx.TextCtrl(self.painel,-1,'', pos=(490,  2), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcbcTd = wx.TextCtrl(self.painel,-1,'', pos=(490, 27), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcbcTc = wx.TextCtrl(self.painel,-1,'', pos=(490, 52), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcbCAv = wx.TextCtrl(self.painel,-1,'', pos=(490, 77), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcbCPr = wx.TextCtrl(self.painel,-1,'', pos=(490,102), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcbFin = wx.TextCtrl(self.painel,-1,'', pos=(490,127), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcbBol = wx.TextCtrl(self.painel,-1,'', pos=(490,152), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcbCLj = wx.TextCtrl(self.painel,-1,'', pos=(490,177), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcbpCr = wx.TextCtrl(self.painel,-1,'', pos=(490,202), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcbDcT = wx.TextCtrl(self.painel,-1,'', pos=(490,227), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcbRlo = wx.TextCtrl(self.painel,-1,'', pos=(490,252), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)

		self.dvQTD = wx.TextCtrl(self.painel,-1,'', pos=(0,  278), size=(95,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vlDev = wx.TextCtrl(self.painel,-1,'', pos=(100,278), size=(95,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vlTrf = wx.TextCtrl(self.painel,-1,'', pos=(200,278), size=(95,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vTsal = wx.TextCtrl(self.painel,-1,'', pos=(300,278), size=(88,22), style=wx.TE_READONLY|wx.TE_RIGHT)


		self.dvQTD.SetBackgroundColour('#E5E5E5')
		self.vlDev.SetBackgroundColour('#E5E5E5')
		self.vlTrf.SetBackgroundColour('#E5E5E5')

		self.vTsal.SetBackgroundColour('#7F7F7F')
		self.vTsal.SetForegroundColour('#FFFFFF')
		self.vTsal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.rcbDin.SetBackgroundColour('#BFBFBF')
		self.rcbcTd.SetBackgroundColour('#BFBFBF')
		self.rcbcTc.SetBackgroundColour('#BFBFBF')
		self.rcbCAv.SetBackgroundColour('#BFBFBF')
		self.rcbCPr.SetBackgroundColour('#BFBFBF')
		self.rcbFin.SetBackgroundColour('#BFBFBF')
		self.rcbBol.SetBackgroundColour('#E5E5E5')
		self.rcbCLj.SetBackgroundColour('#E5E5E5')
		self.rcbpCr.SetBackgroundColour('#E5E5E5')
		self.rcbDcT.SetBackgroundColour('#BFBFBF')
		self.rcbRlo.SetBackgroundColour('#E5E5E5')

		if self.DesBlock !="" and "1" in self.DesBlock:	self.rcbBol.SetBackgroundColour('#BFBFBF')
		if self.DesBlock !="" and "2" in self.DesBlock:	self.rcbCLj.SetBackgroundColour('#BFBFBF')
		if self.DesBlock !="" and "3" in self.DesBlock:	self.rcbpCr.SetBackgroundColour('#BFBFBF')
		if self.DesBlock !="" and "4" in self.DesBlock:	self.rcbRlo.SetBackgroundColour('#BFBFBF')
		
		""" CPF-CNPJ Nao Cadastrado """
		if self.p.resul[0][39] == '':
			
			ndoc.SetValue(u"Não Cadastrado")
			ndoc.SetForegroundColour('#A52A2A')

		nmot = wx.TextCtrl(self.painel,-1,str(self.p.resul[0][79]), pos=(232,67), size=(150,22), style=wx.TE_READONLY)
		nmot.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		nmot.SetBackgroundColour('#E5E5E5')
		nmot.SetForegroundColour('#2D562D')

		nome = wx.TextCtrl(self.painel,-1,str(self.p.resul[0][4]), pos=(12,112), size=(370,22), style=wx.TE_READONLY)
		nome.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		nome.SetBackgroundColour('#E5E5E5')
		nome.SetForegroundColour('#4D4D4D')

		self.valord   = mkn(self.painel, id = 110, value = str(self.p.resul[0][37]), pos=(15,172),  size=(100,22), style = wx.ALIGN_RIGHT|wx.TE_READONLY, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#FFA500", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)

		self.dinheiro = mkn(self.painel, id = 100, value = '0.00', pos=(15, 218), size=(100,20), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.contacor = mkn(self.painel, id = 101, value = '0.00', pos=(130,218), size=(100,20), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.dinheiro.SetValue( str( self.p.resul[0][37] ) )

		self.valord.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dinheiro.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.contacor.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.TikeTe = wx.CheckBox(self.painel, -1,u"Tickete de Crédito \np/Devolução",  pos=(240,172))
		self.copiar = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/copia.png",   wx.BITMAP_TYPE_ANY), pos=(240,206), size=(36,34))				
		self.salvar = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/savep.png",   wx.BITMAP_TYPE_ANY), pos=(343,206), size=(34,34))				
		self.TikeTe.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TikeTe.SetForegroundColour('#0000FF')
		
		self.TikeTe.Enable( False )
		if self.p.resul[0][75] == "" and self.p.resul[0][37] !=0:	self.TikeTe.Enable( True )
		
		voltar = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/voltam.png",  wx.BITMAP_TYPE_ANY), pos=(303,206), size=(36,34))				
		self.baixar = GenBitmapTextButton(self.painel,-1,label=(' '*5)+u'Liquidar Devolução'+(" "*10),  pos=(392,277),size=(196,23), bitmap=wx.Bitmap("imagens/liquidar.png", wx.BITMAP_TYPE_ANY))
		self.baixar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.copiar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.salvar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.dinheiro .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.contacor .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.copiar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.salvar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.baixar.Bind(wx.EVT_BUTTON, self.receberDevolucao)
				
		self.dinheiro.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.contacor.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
				
		voltar.Bind(wx.EVT_BUTTON, self.sairDev)

		self.copiar.Bind(wx.EVT_BUTTON, self.copiaCredito)
		self.salvar.Bind(wx.EVT_BUTTON, self.receberDevolucao)
				
		self.dinheiro.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.contacor.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		
		self.TikeTe.Bind(wx.EVT_CHECKBOX, self.marcaTk)
				
		self.Bind(wx.EVT_KEY_UP, self.Teclas)
			
		self.contacor.SetFocus()

		if self.p.resul[0][75] == '' or self.p.resul[0][39] == '':
			
			self.dinheiro.Disable()
			self.contacor.Disable()
			self.copiar.Disable()
	
		self.ajusTeValores()
	
	def marcaTk(self,event):
		
		self.copiar.Enable( self.TikeTe.GetValue() )
		self.contacor.Enable( self.TikeTe.GetValue() )

		if self.TikeTe.GetValue() == False:

			self.contacor.SetValue('0.00')
			vd  = Decimal(str(self.valord.GetValue()).replace(",",""))
			self.aTualizaValor( vd, Decimal('0.00'), 101 )

		
	def ajusTeValores(self):


		conn  = sqldb()
		sql   = conn.dbc("Caixa: Recebimento de Devolução", fil = self.f, janela = self.painel )
	
		if sql[0] == True:


			"""  Seleciona o recebimento do pedido vinculado   """
			
			vDisp = Decimal("0.00")
			vRece = Decimal("0.00")
			vTran = Decimal("0.00")
			vTDin = Decimal("0.00")
			vDevo = Decimal("0.00")
			saldo = Decimal("0.00")
			vAuTo = ""

			"""  Apura Como Foi o Recebimento do DAVs   """
			VDV = sql[2].execute("SELECT cr_tnot,cr_audv FROM dcdavs WHERE cr_ndav='"+str( self.p.resul[0][2] )+"'")
			if VDV !=0:	vDevo,vAuTo = sql[2].fetchone()

			if vAuTo !="":	self.auT.SetLabel(u"Autorização: { "+str( vAuTo )+" }")
			
			if sql[2].execute("SELECT cr_dinh,cr_chav,cr_chpr,cr_ctcr,cr_ctde,cr_fatb,cr_fatc,cr_fina,cr_tike,cr_pgcr,cr_depc,cr_rcbl FROM cdavs WHERE cr_ndav='"+str( self.p.resul[0][78] )+"'") !=0:
				
				valores = sql[2].fetchall()

				vDisp = ( valores[0][0] + valores[0][1] + valores[0][2] + valores[0][3] + valores[0][4] + valores[0][7] + valores[0][10] )
				
				"""  Autorizacao de Recebimento da Devolucao  """
				if vAuTo != "":	self.DesBlock = ['1','2','3','4']
				
				if self.DesBlock !="" and "1" in self.DesBlock:	vDisp +=valores[0][5]
				if self.DesBlock !="" and "2" in self.DesBlock:	vDisp +=valores[0][6]
				if self.DesBlock !="" and "3" in self.DesBlock:	vDisp +=valores[0][9]
				if self.DesBlock !="" and "4" in self.DesBlock:	vDisp +=valores[0][11]

				if valores[0][0]  !=0:	self.rcbDin.SetValue( format( valores[0][0] ,',' ) )
				if valores[0][4]  !=0:	self.rcbcTd.SetValue( format( valores[0][4] ,',' ) )
				if valores[0][3]  !=0:	self.rcbcTc.SetValue( format( valores[0][3] ,',' ) )
				if valores[0][1]  !=0:	self.rcbCAv.SetValue( format( valores[0][1] ,',' ) )
				if valores[0][2]  !=0:	self.rcbCPr.SetValue( format( valores[0][2] ,',' ) )
				if valores[0][7]  !=0:	self.rcbFin.SetValue( format( valores[0][7] ,',' ) )
				if valores[0][5]  !=0:	self.rcbBol.SetValue( format( valores[0][5] ,',' ) )
				if valores[0][6]  !=0:	self.rcbCLj.SetValue( format( valores[0][6] ,',' ) )
				if valores[0][9]  !=0:	self.rcbpCr.SetValue( format( valores[0][9] ,',' ) )
				if valores[0][10] !=0:	self.rcbDcT.SetValue( format( valores[0][10],',' ) )
				if valores[0][11] !=0:	self.rcbRlo.SetValue( format( valores[0][11],',' ) )

			"""  Resgata o valor original da devolucao  """

			QTD = sql[2].execute("SELECT cr_ccre,cr_cdeb,cr_tror,cr_reca FROM dcdavs WHERE cr_cdev='"+str( self.p.vin.GetValue() )+"'")

			if VDV !=0 and QTD !=0:

				QTdev = sql[2].fetchall()
				
				for i in QTdev:
					
					if i[3] == '1':
						
						vRece +=( i[0] + i[2] )

						vTran +=i[0] #-: Transferencias
						vTDin +=i[2] #-: Devolução em dinheiro

				self.dvQTD.SetValue( str( QTD ) )
				self.vlDev.SetValue( format( vTDin,',') ) #-: Valor da devolucao em dinheiro
				self.vlTrf.SetValue( format( vTran,',') ) #-: valor da transferencia cc
				self.vTsal.SetValue( format( vRece,',') ) #-: valor total ja recebido
			
			saldo = ( vDisp - vRece )
			
			vlDev = Decimal( self.valord.GetValue() )
			self.baixar.Enable( True )
			if saldo >= vDevo:	self.baixar.Enable( False )

			self.sDisp.SetLabel(u"Saldo Disponivel\n"+format( saldo,','))
			if vDevo > saldo:	self.inf.SetLabel(u"{ Valor de devolução superior ao dav }")
			
			""" Foi colocado o int p/q quando tem desconto no dav da uma pequena diferenca na dizima referente ao desconto na hora da devolucao  """
			if int( saldo ) < int( vDevo ):

				self.salvar.Enable( False )
				self.copiar.Enable( False )

				self.dinheiro.Enable( False )
				self.contacor.Enable( False )

				self.dinheiro.SetValue("0.00")
				self.contacor.SetValue("0.00")

			conn.cls( sql[1] )
		
	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		
		_dh = str(self.dinheiro.GetValue()).replace(',','')
		_cc = str(self.contacor.GetValue()).replace(',','')
 		vd  = Decimal(str(self.valord.GetValue()).replace(",",""))

		""" Calculo do Desconto """
		if controle != None and controle.GetId() == 100:	self.aTualizaValor(vd,Decimal(_dh),controle.GetId())
		if controle != None and controle.GetId() == 101:	self.aTualizaValor(vd,Decimal(_cc),controle.GetId())

		event.Skip()
		
	def aTualizaValor(self,vde,vlr,idf):

			rs = vde
			if vlr > 0 and vlr <= vde:	rs = ( vde - vlr)
			if idf == 100:	self.contacor.SetValue(str(rs))
			if idf == 101:	self.dinheiro.SetValue(str(rs))

			if vlr > vde:
							
				self.dinheiro.SetValue(str(vde))
				self.contacor.SetValue('0.00')
				
	def copiaCredito(self,event):

		if Decimal( self.contacor.GetValue() ) == 0:
			
			vd  = Decimal(str(self.valord.GetValue()).replace(",",""))
			self.dinheiro.SetValue('0.00')
			self.contacor.SetValue(str(vd))

		elif Decimal( self.contacor.GetValue() ) != 0:

			self.contacor.SetValue('0.00')
			vd  = Decimal(str(self.valord.GetValue()).replace(",",""))
			self.aTualizaValor( vd, Decimal('0.00'), 101 )
			

	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

 		vd  = Decimal(str(self.valord.GetValue()).replace(",",""))
		if valor == '':	valor = '0.00'
		
		if idfy == 100:	self.dinheiro.SetValue(str(valor))			
		if idfy == 101:	self.contacor.SetValue(str(valor))		

		self.aTualizaValor(vd,Decimal(valor),idfy)		
			
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 200:	sb.mstatus(u"  Voltar-Sair do recebimento de devolução",0)
		elif event.GetId() == 201:	sb.mstatus(u"  Gravar recebimento de devoluçao",0)
		elif event.GetId() == 202:	sb.mstatus(u"  Copiar valor da devolução para conta corrente",0)
		elif event.GetId() == 100:	sb.mstatus(u"  Entre com o valor para devolulçao em especie",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Entre com o valor para transferência para conta corrente",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus(u"  Caixa: Recebimento de Devolulções",0)
		event.Skip()

	def sairDev(self,event):
		
		self.p.Enable()
		self.Destroy()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#255F25") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Recebimento de Devoluções", 0, 250, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10,   0,  375, 250, 3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12, 145,  220, 100, 3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(235,145,  145, 100, 3) #-->[ Lykos ]

	def receberDevolucao(self,event):

		receber = wx.MessageDialog(self.painel,u"Confirme para o recebimento da devoluçao...\n"+(" "*100),u"Caixa: Recebimento de Devolução",wx.YES_NO|wx.NO_DEFAULT)
		grave   = False

		if receber.ShowModal() ==  wx.ID_YES:
			
			sald  = formasPagamentos()
			conn  = sqldb()
			sql   = conn.dbc("Caixa: Recebimento de Devolução", fil = self.f, janela = self.painel )
			
			self.salvar.Enable( False )

			if sql[0] == True:

				numeroDocu = self.p.resul[0][39]
				if self.TikeTe.GetValue() == True:	numeroDocu = str( self.p.ndav )
				
				_cccr,_ccdb = sald.saldoCC( sql[2], numeroDocu )
				emailsc     = self.e.listar( 1, self.p.resul[0][3], sql[2] )
						 
				EMD = datetime.datetime.now().strftime("%Y-%m-%d") #-: Data de Recebimento
				DHO = datetime.datetime.now().strftime("%T") #-------: Hora do Recebimento
				CXN = str( login.usalogin.strip() ) #----------------: Nome do Caixa
				CXC = login.uscodigo #-------------------------------: Codigo do Caixa
				CXF = login.emcodigo #-------------------------------: Filial do Caixa
				emi = EMD+' '+DHO+' '+login.usalogin

				VRC = str( self.valord.GetValue() ).replace(',','') #---: Valor Recebido
				TRO = str( self.valord.GetValue() ).replace(',','') #---: Troco
				RTR = str( self.dinheiro.GetValue() ).replace(',','') #-: Sobra de Troco do Rateio
				CCR = str( self.contacor.GetValue() ).replace(',','') #-: Lancamento do Credito no CC Rateio do Troco

				_cdcl = self.p.resul[0][3]
				_nmcl = self.p.resul[0][4].decode("UTF-8") if type( self.p.resul[0][4] ) == str else self.p.resul[0][4]
				_fant =	self.p.resul[0][5].decode("UTF-8") if type( self.p.resul[0][5] ) == str else self.p.resul[0][5]
				_docu = self.p.resul[0][39]
				_idfc = self.p.resul[0][55]

				if self.TikeTe.GetValue() == True:	_docu = str( self.p.ndav )
						
				""" Atualiza Recebimento da Devolucao """
				try:

					_gravar = "UPDATE dcdavs SET \
					cr_urec='"+CXN+"',cr_erec='"+EMD+"',cr_hrec='"+DHO+"',cr_cxcd='"+CXC+"',\
					cr_ecca='',cr_usac='',cr_vlrc='"+str(VRC)+"',cr_vltr='"+str(TRO)+"',\
					cr_ccre='"+str(CCR)+"',cr_ficx='"+CXF+"',\
					cr_tror='"+str(RTR)+"',cr_dinh='"+VRC+"',\
					cr_reca='1' WHERE cr_ndav='"+str(self.p.ndav)+"'"

					_retorno = sql[2].execute(_gravar)

					""" Entrada no Conta Corrente """
					if Decimal(CCR) !=0:
						
						_ccsaldo = ( ( _cccr - _ccdb ) +  Decimal(CCR) )
						__histor = u'Recebimento no Caixa da Devolução'
						
						_gcon = "INSERT INTO conta (cc_lancam,cc_horala,\
						cc_usuari,cc_usnome,\
						cc_cdfili,cc_idfila,\
						cc_davlan,cc_cdclie,\
						cc_nmclie,cc_docume,\
						cc_idfcli,cc_origem,\
						cc_histor,cc_credit,\
						cc_saldos) values('"+EMD+"','"+DHO+"',\
						'"+CXC+"','"+CXN+"',\
						'"+login.emcodigo+"','"+self.f +"',\
						'"+str(self.p.ndav)+"','"+_cdcl+"',\
						'"+_nmcl+"','"+_docu+"',\
						'"+_idfc+"','RC',\
						'"+__histor+"','"+str( CCR )+"','"+str( _ccsaldo )+"')"
											
						sql[2].execute(_gcon)

					""" Grava no Banco """
					sql[1].commit()
					grave =  True
				
				except Exception, _reTornos:

					sql[1].rollback()
					alertas.dia(self.painel,u"Inclusão não concluida !!\n \nRetorno: "+str(_reTornos),u"Retorno")	

				""" Fechamento do Banco """
				conn.cls(sql[1])

				if grave == True:

					soco.gravadados(str(self.p.ndav),u"Recebimento de Devolução","CAIXA")
					alertas.dia(self.painel,u"Recebimento da Devolução, [< OK >]\n"+(' '*60),u"Caixa: Recebimento de Devolução")
							
					vlExtenso = NumeroPorExtenso(RTR).extenso_unidade
					cliente   = _nmcl
					valor     = self.dinheiro.GetValue()

					vd = self.valord.GetValue()  #---:[ Valor Total da devolucao ]
					vc = self.contacor.GetValue() #--:[ Transferencia para conta corrente ]
							
					self.r.recibocliente(cliente,valor,vlExtenso,u"Devolução: "+str(self.p.resul[0][2]),emailsc,self.p,vd,vc, Filial = self.f )

		if grave == True:

			self.p.selecionar(wx.EVT_BUTTON)
			self.sairDev(wx.EVT_BUTTON)

class sangria(wx.Frame):
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.f = self.p.fl
		mkn    = wx.lib.masked.NumCtrl
		
		self.p.Disable()

		self.dados_fornecedor = ""
		
		wx.Frame.__init__(self, parent, id, u'Caixa: Sangria-Suprimentos', size=(575,490), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		_s1 = wx.StaticText(self.painel,-1,u"Recebimentos", pos=(183, 100))
		_s1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		_s1.SetForegroundColour('#174A7C')

		_s2 = wx.StaticText(self.painel,-1,u"(-) Sangria", pos=(283, 100))
		_s2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		_s2.SetForegroundColour('#B90C0C')

		_s3 = wx.StaticText(self.painel,-1,u"(+) Sangria", pos=(383, 100))
		_s3.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		_s3.SetForegroundColour('#1E90FF')

		_s4 = wx.StaticText(self.painel,-1,u"Sal", pos=(483, 100))
		_s4.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		_s4.SetForegroundColour('#346799')

		_s5 = wx.StaticText(self.painel,-1,u"do", pos=(500, 100))
		_s5.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		_s5.SetForegroundColour('#B90C0C')
		
		wx.StaticText(self.painel,-1,u"Dinheiro",          pos=(18,100)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Cartão de débito",  pos=(18,140)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Cartão de crédito", pos=(18,180)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Cheque avista",     pos=(18,220)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Cheque predatado",  pos=(18,260)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cx = wx.StaticText(self.painel,-1,u"Caixa: "+login.usalogin.upper(), pos=(18,5) )
		self.cx.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Devolução em Dinheiro / Pagamento do Credito Conta Corrente """
		self.dvdin = wx.StaticText(self.painel,-1,u"DAV-Devoluçao em Dinheiro: {  }",  pos=(18,305))
		self.dvdin.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.dvdin.SetForegroundColour("#A52A2A")

		self.pgccc = wx.StaticText(self.painel,-1,u"CC-Pagamento do Crédito..: {  }",  pos=(18,325))
		self.pgccc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.pgccc.SetForegroundColour("#B21313")

		self.Troco = wx.StaticText(self.painel,-1,u"Trocos...........: {  }",  pos=(320,305))
		self.Troco.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.Troco.SetForegroundColour("#A52A2A")

		self.Troca = wx.StaticText(self.painel,-1,u"Trocos Anteriores: {  }",  pos=(320,325))
		self.Troca.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.Troca.SetForegroundColour("#B21313")

		wx.StaticText(self.painel,-1,u"Histórico { Minimo 10 letras }",  pos=(18,355)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Login",      pos=(273, 5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Senha",      pos=(273,48)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Plano de contas:", pos=(18,437)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Fornecedor/Serviço:", pos=(18,462)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.lansaida = wx.RadioButton(self.painel,-1,u"Saida-Retirada",        pos=(15, 44),style=wx.RB_GROUP)
		self.lentrada = wx.RadioButton(self.painel,-1,u"Entrada-Suprimentos ",  pos=(15, 66))
		self.suprimen = wx.CheckBox(self.painel, -1,  u"Suprimentos",           pos=(165,44))
		self.transpor = wx.CheckBox(self.painel, -1,  u"Transportar saida p/contas apagar", pos=(330,430))

		self.lansaida.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.lentrada.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.suprimen.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.transpor.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dinheiro = mkn(self.painel, 700,  value = '0.00', pos=(15,115), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.dinheiro.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cartaodb = mkn(self.painel, 701,  value = '0.00', pos=(15,155), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.cartaodb.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
		self.cartaocr = mkn(self.painel, 702,  value = '0.00', pos=(15,195), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.cartaocr.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.chequeav = mkn(self.painel, 703,  value = '0.00', pos=(15,235), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.chequeav.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.chequepr = mkn(self.painel, 704,  value = '0.00', pos=(15,275), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.chequepr.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Totalizacao de Recebimentos do Caixa """
		
		self.dinh = wx.TextCtrl(self.painel,-1,value="", pos=(180, 115), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.dinh.SetBackgroundColour('#BFBFBF')
		self.dinh.SetForegroundColour('#153E67')
		self.dinh.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.cdeb = wx.TextCtrl(self.painel,-1,value="", pos=(180, 155), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.cdeb.SetBackgroundColour('#BFBFBF')
		self.cdeb.SetForegroundColour('#153E67')
		self.cdeb.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ccre = wx.TextCtrl(self.painel,-1,value="", pos=(180, 195), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ccre.SetBackgroundColour('#BFBFBF')
		self.ccre.SetForegroundColour('#153E67')
		self.ccre.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cavi = wx.TextCtrl(self.painel,-1,value="", pos=(180, 235), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.cavi.SetBackgroundColour('#BFBFBF')
		self.cavi.SetForegroundColour('#153E67')
		self.cavi.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cpre = wx.TextCtrl(self.painel,-1,value="", pos=(180, 275), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.cpre.SetBackgroundColour('#BFBFBF')
		self.cpre.SetForegroundColour('#153E67')
		self.cpre.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Totalizacao das Sangrias do Caixa """

		self.sdinh = wx.TextCtrl(self.painel,-1,value="", pos=(280, 115), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.sdinh.SetBackgroundColour('#BFBFBF')
		self.sdinh.SetForegroundColour('#DA0404')
		self.sdinh.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.scdeb = wx.TextCtrl(self.painel,-1,value="", pos=(280, 155), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.scdeb.SetBackgroundColour('#BFBFBF')
		self.scdeb.SetForegroundColour('#DA0404')
		self.scdeb.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.sccre = wx.TextCtrl(self.painel,-1,value="", pos=(280, 195), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.sccre.SetBackgroundColour('#BFBFBF')
		self.sccre.SetForegroundColour('#DA0404')
		self.sccre.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.scavi = wx.TextCtrl(self.painel,-1,value="", pos=(280, 235), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.scavi.SetBackgroundColour('#BFBFBF')
		self.scavi.SetForegroundColour('#DA0404')
		self.scavi.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.scpre = wx.TextCtrl(self.painel,-1,value="", pos=(280, 275), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.scpre.SetBackgroundColour('#BFBFBF')
		self.scpre.SetForegroundColour('#DA0404')
		self.scpre.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Sangria de Entrada """
		self.edinh = wx.TextCtrl(self.painel,-1,value="", pos=(380, 115), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.edinh.SetBackgroundColour('#BFBFBF')
		self.edinh.SetForegroundColour('#1E90FF')
		self.edinh.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.ecdeb = wx.TextCtrl(self.painel,-1,value="", pos=(380, 155), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ecdeb.SetBackgroundColour('#BFBFBF')
		self.ecdeb.SetForegroundColour('#1E90FF')
		self.ecdeb.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.eccre = wx.TextCtrl(self.painel,-1,value="", pos=(380, 195), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.eccre.SetBackgroundColour('#BFBFBF')
		self.eccre.SetForegroundColour('#1E90FF')
		self.eccre.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ecavi = wx.TextCtrl(self.painel,-1,value="", pos=(380, 235), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ecavi.SetBackgroundColour('#BFBFBF')
		self.ecavi.SetForegroundColour('#1E90FF')
		self.ecavi.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ecpre = wx.TextCtrl(self.painel,-1,value="", pos=(380, 275), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ecpre.SetBackgroundColour('#BFBFBF')
		self.ecpre.SetForegroundColour('#1E90FF')
		self.ecpre.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		""" Saldo do Caixa """

		self.vdinh = wx.TextCtrl(self.painel,600,value="", pos=(480, 115), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vdinh.SetBackgroundColour('#BFBFBF')
		self.vdinh.SetForegroundColour('#2D76BE')
		self.vdinh.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.vcdeb = wx.TextCtrl(self.painel,601,value="", pos=(480, 155), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vcdeb.SetBackgroundColour('#BFBFBF')
		self.vcdeb.SetForegroundColour('#2D76BE')
		self.vcdeb.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.vccre = wx.TextCtrl(self.painel,602,value="", pos=(480, 195), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vccre.SetBackgroundColour('#BFBFBF')
		self.vccre.SetForegroundColour('#2D76BE')
		self.vccre.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.vcavi = wx.TextCtrl(self.painel,603,value="", pos=(480, 235), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vcavi.SetBackgroundColour('#BFBFBF')
		self.vcavi.SetForegroundColour('#2D76BE')
		self.vcavi.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.vcpre = wx.TextCtrl(self.painel,604,value="", pos=(480, 275), size=(90,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vcpre.SetBackgroundColour('#BFBFBF')
		self.vcpre.SetForegroundColour('#2D76BE')
		self.vcpre.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Historico """
		self.histo = wx.TextCtrl(self.painel,203,value=u"saida-retirada do caixa", pos=(15, 368), size=(555,47),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.histo.SetBackgroundColour('#E5E5E5')
		self.histo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Logon do Caixa """
		self.caixa = wx.ComboBox(self.painel, -1, value=login.usalogin, pos=(15, 18), size = (240,27), choices = login.uslis,style=wx.NO_BORDER|wx.CB_READONLY)
		self.logon = wx.ComboBox(self.painel, -1, value=login.usalogin, pos=(270,18), size = (235,27), choices = login.uslis,style=wx.NO_BORDER|wx.CB_READONLY)
		self.senha = wx.TextCtrl(self.painel, -1, value= '',            pos=(270,63), size = (234,22), style = wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)

		self.gravar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/save16.png",   wx.BITMAP_TYPE_ANY), pos=(535,12), size=(33,32))			
		self.voltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltap.png",  wx.BITMAP_TYPE_ANY), pos=(535,53), size=(33,32))			

		""" Transportar p/contas apagar """
		self.planoc = wx.TextCtrl(self.painel,303,value="", pos=(135, 432), size=(180,20),style=wx.TE_READONLY)
		self.planoc.SetBackgroundColour('#E5E5E5')
		self.planoc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.fornec = wx.TextCtrl(self.painel,304,value="", pos=(134, 457), size=(436,20),style=wx.TE_READONLY)
		self.fornec.SetBackgroundColour('#E5E5E5')
		self.fornec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dinheiro.Disable()
		self.cartaodb.Disable()
		self.cartaocr.Disable()
		self.chequeav.Disable()
		self.chequepr.Disable()
		self.lansaida.Disable()
		self.lentrada.Disable()
		self.suprimen.Disable()
		self.histo.Disable()
		self.caixa.Disable()
		self.gravar.Disable()
		
		self.voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.gravar.Bind(wx.EVT_BUTTON, self.gravars)
		self.senha.Bind(wx.EVT_TEXT_ENTER, self.executar)

		self.lansaida.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.lentrada.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.suprimen.Bind(wx.EVT_CHECKBOX, self.evchekb)
		
		self.vdinh.Bind(wx.EVT_LEFT_DCLICK, self.vlrPassar)
		self.vcdeb.Bind(wx.EVT_LEFT_DCLICK, self.vlrPassar)
		self.vccre.Bind(wx.EVT_LEFT_DCLICK, self.vlrPassar)
		self.vcavi.Bind(wx.EVT_LEFT_DCLICK, self.vlrPassar)
		self.vcpre.Bind(wx.EVT_LEFT_DCLICK, self.vlrPassar)

		self.dinheiro.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.cartaodb.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.cartaocr.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.chequeav.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.chequepr.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

		self.fornec.Bind(wx.EVT_TEXT_ENTER,  self.pesquisaFornecedor)
		self.fornec.Bind(wx.EVT_LEFT_DCLICK, self.pesquisaFornecedor)

		self.caixa.Bind(wx.EVT_COMBOBOX, self.chbcaixa)
		
		self.senha.SetFocus()

	def pesquisaFornecedor(self,event):

		fornecedores.NomeFilial   = self.f
		fornecedores.pesquisa     = True
		fornecedores.nmFornecedor = self.fornec.GetValue()
		fornecedores.unidademane  = False
		fornecedores.transportar  = False

		frp_frame=fornecedores(parent=self,id=event.GetId())
		frp_frame.Centre()
		frp_frame.Show()

	def ajustafrn(self,_dc,_ft,_nm,_ie,_im,_cn,_id,_rp, _pc ):

		self.dados_fornecedor = str( _id )+"|"+str( _dc )+"|"+str( _ft )+"|"+str( _nm )+"|"+str( _pc )
		self.planoc.SetValue( _pc )
		self.fornec.SetValue( str( _id )+" "+str( _nm ) )
		
	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor == '':	valor = "0.00"
		if idfy == 700:	self.dinheiro.SetValue(valor)
		if idfy == 701:	self.cartaodb.SetValue(valor)
		if idfy == 702:	self.cartaocr.SetValue(valor)
		if idfy == 703:	self.chequeav.SetValue(valor)
		if idfy == 704:	self.chequepr.SetValue(valor)

	def vlrPassar(self,event):

		if event.GetId() == 600 and self.vdinh.GetValue() !='' and Decimal( self.vdinh.GetValue().replace(',','') ) > 0:	self.dinheiro.SetValue(self.vdinh.GetValue())
		if event.GetId() == 601 and self.vcdeb.GetValue() !='' and Decimal( self.vcdeb.GetValue().replace(',','') ) > 0:	self.cartaodb.SetValue(self.vcdeb.GetValue())
		if event.GetId() == 602 and self.vccre.GetValue() !='' and Decimal( self.vccre.GetValue().replace(',','') ) > 0:	self.cartaocr.SetValue(self.vccre.GetValue())
		if event.GetId() == 603 and self.vcavi.GetValue() !='' and Decimal( self.vcavi.GetValue().replace(',','') ) > 0:	self.chequeav.SetValue(self.vcavi.GetValue())
		if event.GetId() == 604 and self.vcpre.GetValue() !='' and Decimal( self.vcpre.GetValue().replace(',','') ) > 0:	self.chequepr.SetValue(self.vcpre.GetValue())
		
	def evchekb(self,event):

		if self.suprimen.GetValue() == True:
			
			self.cartaodb.Disable()
			self.cartaocr.Disable()
			self.chequeav.Disable()
			self.chequepr.Disable()
			self.lansaida.Disable()
			self.lentrada.Disable()

			self.cartaodb.SetValue('0.00')
			self.cartaocr.SetValue('0.00')
			self.chequeav.SetValue('0.00')
			self.chequepr.SetValue('0.00')
			
			self.lansaida.SetValue(True)
			self.histo.SetValue(u"suprimentos de caixa")

		else:
			
			self.cartaodb.Enable()
			self.cartaocr.Enable()
			self.chequeav.Enable()
			self.chequepr.Enable()
			self.lansaida.Enable()
			self.lentrada.Enable()

	def evradio(self,event):
		
		if self.lansaida.GetValue() == True:	self.histo.SetValue(u"saida-retirada do caixa")
		if self.lentrada.GetValue() == True:	self.histo.SetValue(u"entrada-suprimentos")
		
	def gravars(self,event):

		if self.transpor.GetValue():
			
			if not self.planoc.GetValue() or not self.fornec.GetValue():
				alertas.dia(self.painel,u"Transporte para contas apagar c/plano de contas ou fornecedor/serviço vazio...\n"+(' '*150),u"Caixa:  Sangria-Suprimentos")
				return

			if not Decimal( self.dinheiro.GetValue() ):

				alertas.dia(self.painel,u"Transporte para contas apagar c/valor em dinheiro zerado...\n"+(' '*140),u"Caixa:  Sangria-Suprimentos")
				return
		
		valor = ( Decimal(self.dinheiro.GetValue()) + Decimal(self.cartaodb.GetValue()) + Decimal(self.cartaocr.GetValue()) + Decimal(self.chequeav.GetValue()) + Decimal(self.chequepr.GetValue()) )
		if valor == 0:	alertas.dia(self.painel,u"Entre com valor para sagria/suprimentos...\n"+(' '*100),u"Caixa:  Sangria-Suprimentos")
		
		if len(self.histo.GetValue()) < 10:	alertas.dia(self.painel,u"Hostórico minimo de 10 letras...\n"+(' '*80),u"Caixa: Sangria-Suprimentos")
		if len(self.histo.GetValue()) > 9 and valor !=0:

			capaga = u"\nSangria com lançamento em dinheiro p/contas apagar\n" if self.transpor.GetValue() else ""
			addsan = wx.MessageDialog(self,u"Confirme para gravar sangria-suprimentos!!\n"+capaga+(" "*140),u"Caixa: Sangria-Suprimentos",wx.YES_NO)
			
			if addsan.ShowModal() ==  wx.ID_YES:
					
				conn = sqldb()
				sql  = conn.dbc(u"Caixa: Sangria-Suprimentos", fil = self.f, janela = self.painel )

				if sql[0] == True:

					historico = self.histo.GetValue()

					if self.transpor.GetValue():

						__id, __dc, __ft, __nm, __pc = self.dados_fornecedor.split('|')

						nControle = numeracao()
						controle_apagar = nControle.numero(u"8",u"Controle de compras", self.painel, self.f )
			
						if not controle_apagar:

							alertas.dia(self.painel,u"Nào foi possivel criar o numero de controle do contas apagar...\n"+(' '*140),u"Caixa:  Sangria-Suprimentos")

							conn.cls( sql[1] )
							return

						historico +=u"\n\nSangria com lancamento em dinheiro para o contas apagar\nValor: "+str( self.dinheiro.GetValue() ).replace(",","")+u"\nControle: "+str( controle_apagar ).zfill(10)+"\n"+str( __nm )
						
					if self.lansaida.GetValue() == True:	ES = "S"
					if self.lentrada.GetValue() == True:	ES = "E"
					if self.suprimen.GetValue() == True:	ES = "C"

					EMI = datetime.datetime.now().strftime("%Y/%m/%d")
					HEM = datetime.datetime.now().strftime("%T")

					grava = "INSERT INTO sansu (ss_lancam,ss_horala,\
					                            ss_usnome,ss_usreti,\
					                            ss_idfila,\
					                            ss_dinhei,ss_chavis,\
					                            ss_chpred,ss_credit,\
					                            ss_debito,ss_ensaid,\
					                            ss_histor)\
					                            values('"+EMI+"','"+HEM+"',\
					                            '"+ self.logon.GetValue() +"','"+ self.caixa.GetValue() +"',\
					                            '"+str( self.f )+"',\
												'"+str(self.dinheiro.GetValue()).replace(",","")+"','"+str(self.chequeav.GetValue()).replace(",","")+"',\
												'"+str(self.chequepr.GetValue()).replace(",","")+"','"+str(self.cartaocr.GetValue()).replace(",","")+"',\
												'"+str(self.cartaodb.GetValue()).replace(",","")+"','"+ES+"',\
												'"+ historico +"')"

					if self.transpor.GetValue():

						__id, __dc, __ft, __nm, __pc = self.dados_fornecedor.split('|')

						apagar = "INSERT INTO apagar ( ap_docume, ap_nomefo, ap_fantas, ap_ctrlcm, ap_dtlanc, ap_hrlanc, ap_usalan,\
								ap_dtvenc, ap_duplic, ap_parcel, ap_valord, ap_dtbaix, ap_horabx, ap_valorb, ap_usabix, ap_filial, ap_pagame, ap_hiscon, ap_rgforn, ap_contas, ap_vlorig, ap_status )\
								VALUES( %s, %s, %s, %s, %s, %s, %s,\
								%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"

					try:

						sql[2].execute(grava)

						if self.transpor.GetValue():

							pg_dinheiro = str( self.dinheiro.GetValue() ).replace(",","")
							sql[2].execute( apagar, ( __dc, __nm, __ft, str( controle_apagar ), EMI, HEM, login.usalogin,\
												EMI, str( controle_apagar ).zfill(10), "01", pg_dinheiro, EMI, HEM, pg_dinheiro, login.usalogin, self.f, "1", "Sangria de caixa\n\n"+str( historico ), __id, __pc, pg_dinheiro, "1" ) )

						sql[1].commit()

						self.sair(wx.EVT_BUTTON)
						
					except Exception, _reTornos:
							
						sql[1].rollback()
						alertas.dia(self,u"Pocesso Interrompido, Gravando sangria-suprimentos!!\n\nRetorno: "+str(_reTornos),u"Gravando sangria-suprimentos")			
					
					conn.cls(sql[1])
			
	def executar(self,event):

		if self.senha.GetValue() !='':
						
			conn = sqldb()
			sql  = conn.dbc(u"Sangria, Suprimentos", fil = self.f, janela = self.painel )
			
			if sql[0] == True:

				ach = sql[2].execute("SELECT us_logi,us_senh FROM usuario WHERE us_logi='"+str(self.logon.GetValue())+"'")
				snh =	sql[2].fetchall()[0][1]
				conn.cls(sql[1])
				
				if ach !=0:

					if snh == self.senha.GetValue():

						self.dinheiro.Enable()
						self.cartaodb.Enable()
						self.cartaocr.Enable()
						self.chequeav.Enable()
						self.chequepr.Enable()
						self.lansaida.Enable()
						self.lentrada.Enable()
						self.suprimen.Enable()
						
						self.histo.Enable()
						self.caixa.Enable()
						self.gravar.Enable()

						self.logon.Disable()
						self.senha.Disable()
						self.dinheiro.SetFocus()

						self.ToTalizacao()
						
					else:	alertas.dia(self.painel,u"Senha não confere...\n"+(' '*80),u"Caixa: Sangria-Suprimentos")
				else:	alertas.dia(self.painel,u"Usuário não localizado...\n"+(' '*80),u"Caixa: Sangria-Suprimentos")
		
	def chbcaixa(self,event):
		
		self.cx.SetLabel("Caixa:  "+str(self.caixa.GetValue()).upper())
		self.ToTalizacao()
		
	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()

	def ToTalizacao(self):
		
		conn = sqldb()
		sql  = conn.dbc("Caixa, Totalização do caixa", fil = self.f, janela = self.painel )
		if sql[0] == True:

			""" Dia Atual """
			dIni = dFim = hoje = datetime.datetime.now().strftime("%Y/%m/%d")
			din  = cha  = chp  = crc = crd = dvd = Tro = Tra = Decimal('0.00')

			self.dinheiro.SetValue('0.00')
			self.cartaodb.SetValue('0.00')
			self.cartaocr.SetValue('0.00')
			self.chequeav.SetValue('0.00')
			self.chequepr.SetValue('0.00')

			diaatual = "SELECT SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde), SUM(cr_vltr) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca='1' and cr_urec='"+str(self.caixa.GetValue())+"'"
			anterior = "SELECT SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde), SUM(cr_vltr) FROM cdavs WHERE cr_erec >='"+dIni+"' and cr_erec <='"+dFim+"' and cr_edav < '"+hoje+"' and cr_reca='1' and cr_urec='"+str(self.caixa.GetValue())+"'"
			creceber = "SELECT * FROM receber WHERE rc_dtlanc >='"+dIni+"' and rc_dtlanc <='"+dFim+"' and rc_modulo ='CAIXA' and rc_loginc = '"+str(self.logon.GetValue())+"' and rc_status != '2' and rc_status != '4' and rc_status != '5'"

			devoluca = "SELECT SUM(cr_tror) FROM dcdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca='1' and cr_urec='"+str(self.caixa.GetValue())+"'"

			sangrias = "SELECT * FROM sansu   WHERE ss_lancam='"+str(dIni)+"' and ss_usnome='"+str(self.caixa.GetValue())+"'"
			creditoc = "SELECT SUM(cc_debito) FROM conta WHERE cc_lancam='"+str(dIni)+"' and cc_origem='PC' and cc_usnome='"+str(self.caixa.GetValue())+"'"

			""" Dia Atual """
			if sql[2].execute(diaatual) !=0:

				_da = sql[2].fetchall()
				if _da[0][0] !=None:	din += _da[0][0]
				if _da[0][1] !=None:	cha += _da[0][1]
				if _da[0][2] !=None:	chp += _da[0][2]
				if _da[0][3] !=None:	crc += _da[0][3]
				if _da[0][4] !=None:	crd += _da[0][4]
				if _da[0][5] !=None:	Tro += _da[0][5]
			
			""" Dias Anteriores """
			if sql[2].execute(anterior) !=0:
				
				_an = sql[2].fetchall()
				if _an[0][0] !=None:	din += _an[0][0]
				if _an[0][1] !=None:	cha += _an[0][1]
				if _an[0][2] !=None:	chp += _an[0][2]
				if _an[0][3] !=None:	crc += _an[0][3]
				if _an[0][4] !=None:	crd += _an[0][4]
				if _an[0][5] !=None:	Tra += _an[0][5]
				
			if sql[2].execute(devoluca) !=0:

				_dv = sql[2].fetchall()
				if _dv[0][0] !=None:	dvd += _dv[0][0]
				
			""" Contas AReceber """
			if sql[2].execute(creceber) !=0:

				_rc = sql[2].fetchall()
				for rc in _rc:

					if rc[21][:2] == "01":	din += rc[05]
					if rc[21][:2] == "02":	cha += rc[05]
					if rc[21][:2] == "03":	chp += rc[05]
					if rc[21][:2] == "04":	crc += rc[05]
					if rc[21][:2] == "05":	crd += rc[05]

			""" Sangrias """
			saDin = saCha = saChp = saCcr = saCdb = sasup = Decimal('0.00')
			seDin = seCha = seChp = seCcr = seCdb = Decimal('0.00')
			slDin = slCha = slChp = slCcr = slCdb = Decimal('0.00')
			
			if sql[2].execute(sangrias) !=0:

				sanBaix = sql[2].fetchall()
						
				for i in sanBaix:
						
					if i[11] == 'S':
							
						saDin += Decimal(i[6])
						saCha += Decimal(i[7])
						saChp += Decimal(i[8])
						saCcr += Decimal(i[9])
						saCdb += Decimal(i[10])
							
					if i[11] == 'E':

						seDin += Decimal(i[6])
						seCha += Decimal(i[7])
						seChp += Decimal(i[8])
						seCcr += Decimal(i[9])
						seCdb += Decimal(i[10])
						
					if i[11] == 'C':	sasup += Decimal(i[6])
	
			""" Pagamento de Credito do Conta Corrente ao Cliente """
			PgToCredito = Decimal('0.00')
			if sql[2].execute(creditoc) !=0:

				sanPagc = sql[2].fetchall()[0][0]

				if sanPagc !=None:	PgToCredito = sanPagc

			self.dinh.SetValue(str(din))
			self.cavi.SetValue(str(cha))
			self.cpre.SetValue(str(chp))
			self.cdeb.SetValue(str(crd))
			self.ccre.SetValue(str(crc))
			self.dvdin.SetLabel(u"DAV-Devoluçao em Dinheiro: { "+format(dvd,',')+" }")
			self.pgccc.SetLabel(u"CC-Pagaamento do Crédito.: { "+format(PgToCredito,',')+" }")
			self.Troco.SetLabel(u"Troco................: { "+format( Tro,',')+" }")
			self.Troca.SetLabel(u"Troco Dias-Anteriores: { "+format( Tra,',')+" }")

			""" Sangrias """
			saDin +=PgToCredito #-: Pagamento do Credito do Conta Corrente ao Cliente
			saDin +=dvd
			saDin +=Tro #---------: Troco
			saDin +=Tra #---------: Troco de dias anteriores
			
			slDin = ( ( din - saDin ) + seDin )
			slCha = ( ( cha - saCha ) + seCha )
			slChp = ( ( chp - saChp ) + seChp )
			slCcr = ( ( crc - saCcr ) + seCcr )
			slCdb = ( ( crd - saCdb ) + seCdb )

			self.sdinh.SetValue(format(saDin,','))
			self.scavi.SetValue(format(saCha,','))
			self.scpre.SetValue(format(saChp,','))
			self.sccre.SetValue(format(saCcr,','))
			self.scdeb.SetValue(format(saCdb,','))
	
			self.edinh.SetValue(format(seDin,','))
			self.ecavi.SetValue(format(seCha,','))
			self.ecpre.SetValue(format(seChp,','))
			self.eccre.SetValue(format(seCcr,','))
			self.ecdeb.SetValue(format(seCdb,','))

			self.vdinh.SetValue(format(slDin,','))
			self.vcavi.SetValue(format(slCha,','))
			self.vcpre.SetValue(format(slChp,','))
			self.vccre.SetValue(format(slCcr,','))
			self.vcdeb.SetValue(format(slCdb,','))
			
			if slDin < 0:	self.vdinh.SetForegroundColour('#A52A2A')
			if slCha < 0:	self.vcavi.SetForegroundColour('#A52A2A')
			if slChp < 0:	self.vcpre.SetForegroundColour('#A52A2A')
			if slCcr < 0:	self.vccre.SetForegroundColour('#A52A2A')
			if slCdb < 0:	self.vcdeb.SetForegroundColour('#A52A2A')
		
			conn.cls(sql[1])
	
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#ED1616") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Caixa: SANGRIA-SUPRIMENTOS", 0, 270, 90)

		dc.SetTextForeground("#6D6D40") 	
		dc.DrawRotatedText(u"Histórico", 0, 410, 90)

		dc.SetTextForeground("#126E12") 	
		dc.DrawRotatedText(u"Apagar", 0, 485, 90)

		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.SetTextForeground("#3C7587") 	
		dc.DrawRotatedText(u"Filial\n{ "+str(self.f)+" }", 505, 85, 90)

		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12, 1,  560, 344, 3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12, 350,560, 70, 3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12, 425,560, 60, 3) #-->[ Lykos ]

		dc.DrawLine (16,90, 567, 90)
		dc.DrawLine (150,90, 150, 300)
