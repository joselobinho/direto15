#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os
import datetime
from wx.lib.buttons import GenBitmapTextButton
import wx.lib.agw.pybusyinfo as PBI

class FiscalMenu(wx.Frame):

	MyNumData = ""
	cdInterva = ""
	PainelCor = ""
	FocusSele = ""
	pathAtual = os.getcwd()
	
	def __init__(self,parent,id):
		
		self.ecfLib            = ecfSel.driveEcf
		corPainel              = self.PainelCor
		self.erroStatus        = statusErro(parent,self.ecfLib)
		self.erroStatus.ecfLib = ecfSel.driveEcf
		self.ECFs              = ExecutarCmd(parent,self.ecfLib)
				
		wx.Frame.__init__(self, parent, id, 'Menu Fiscal',pos=(30,80),size=(710,615), style=wx.NO_BORDER|wx.FRAME_FLOAT_ON_PARENT)
		
		self.painel = wx.Panel(self)
		self.painel.SetBackgroundColour(corPainel)

		mFiscal = wx.StaticBox(self.painel, -1, 'Menu Fiscal', pos=(5,5), size=(695,320),  style=wx.RB_GROUP|wx.SUNKEN_BORDER|wx.ALIGN_CENTER)
		mFiscal.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD));	mFiscal.SetForegroundColour('#FFFFFF')

		mNumero = wx.StaticBox(self.painel, -1, 'Menu Fiscal', pos=(440,330), size=(260,250),  style=wx.SUNKEN_BORDER)
		mNumero.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD));	mNumero.SetForegroundColour('#FFFFFF')

		Interva = wx.StaticBox(self.painel, -1, 'Intervalo', pos=(5,390), size=(430,190),  style=wx.SUNKEN_BORDER)
		Interva.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD));	Interva.SetForegroundColour('#FFFFFF')

		TSaidaR = wx.StaticBox(self.painel, -1, 'Saida', pos=(5,330), size=(430,50),  style=wx.SUNKEN_BORDER)
		TSaidaR.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD));	TSaidaR.SetForegroundColour('#FFFFFF')

		fiscal_LLLX = GenBitmapTextButton(self.painel, 600, wx.Bitmap('imagens/relecf.png'), " {F1}-LX"+(" "*25), (15, 25), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_LLLX.SetForegroundColour('#E6E6FA');	fiscal_LLLX.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_LLLX.SetBezelWidth(5);	fiscal_LLLX.SetBackgroundColour(corPainel)		

		fiscal_LMFC = GenBitmapTextButton(self.painel, 601, wx.Bitmap('imagens/relecf.png'), " {F2}-LMFC"+(" "*23), (240, 25), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_LMFC.SetForegroundColour('#E6E6FA');	fiscal_LMFC.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_LMFC.SetBezelWidth(5);	fiscal_LMFC.SetBackgroundColour(corPainel)		

		fiscal_LMFS = GenBitmapTextButton(self.painel, 602, wx.Bitmap('imagens/relecf.png'), " {F3}-LMFS"+(" "*23), (470, 25), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_LMFS.SetForegroundColour('#E6E6FA');	fiscal_LMFS.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_LMFS.SetBezelWidth(5);	fiscal_LMFS.SetBackgroundColour(corPainel)		

		fiscal_EMDF = GenBitmapTextButton(self.painel, 603, wx.Bitmap('imagens/relecf.png'), " {F4}-Espelho MFD"+(" "*16), (15, 85), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_EMDF.SetForegroundColour('#E6E6FA');	fiscal_EMDF.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_EMDF.SetBezelWidth(5);	fiscal_EMDF.SetBackgroundColour(corPainel)		

		fiscal_AMDF = GenBitmapTextButton(self.painel, 604, wx.Bitmap('imagens/relecf.png'), " {F5}-Arq. MFD"+(" "*19), (240, 85), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_AMDF.SetForegroundColour('#E6E6FA');	fiscal_AMDF.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_AMDF.SetBezelWidth(5);	fiscal_AMDF.SetBackgroundColour(corPainel)		

		fiscal_TABP = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/relecf.png'), " {F6}-Tab PROD."+(" "*19), (470, 85), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_TABP.SetForegroundColour('#E6E6FA');	fiscal_TABP.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_TABP.SetBezelWidth(5);	fiscal_TABP.SetBackgroundColour(corPainel)		
		
		fiscal_ESTO = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/relecf.png'), " {F7}-Estoque"+(" "*20), (15, 145), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_ESTO.SetForegroundColour('#E6E6FA');	fiscal_ESTO.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_ESTO.SetBezelWidth(5);	fiscal_ESTO.SetBackgroundColour(corPainel)		

		fiscal_MOVE = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/relecf.png'), " {F8}-Movimento por ECF"+(" "*10), (240, 145), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_MOVE.SetForegroundColour('#E6E6FA');	fiscal_MOVE.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_MOVE.SetBezelWidth(5);	fiscal_MOVE.SetBackgroundColour(corPainel)		
		
		fiscal_MPAG = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/relecf.png'), " {F9}-Meios de Pgto."+(" "*14), (470, 145), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_MPAG.SetForegroundColour('#E6E6FA');	fiscal_MPAG.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_MPAG.SetBezelWidth(5);	fiscal_MPAG.SetBackgroundColour(corPainel)		
		
		fiscal_DAVE = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/relecf.png'), " {F10}-Davs Emitidos"+(" "*13), (15, 205), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_DAVE.SetForegroundColour('#E6E6FA');	fiscal_DAVE.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_DAVE.SetBezelWidth(5);	fiscal_DAVE.SetBackgroundColour(corPainel)		

		fiscal_IPAF = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/relecf.png'), " {F11}-Identificação do PAF-ECF"+(" "*2), (240, 205), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_IPAF.SetForegroundColour('#E6E6FA');	fiscal_IPAF.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_IPAF.SetBezelWidth(5);	fiscal_IPAF.SetBackgroundColour(corPainel)		

		fiscal_TIND = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/relecf.png'), " {F12}-Tab.Indice Técnico Produção", (470, 205), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_TIND.SetForegroundColour('#E6E6FA');	fiscal_TIND.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_TIND.SetBezelWidth(5);	fiscal_TIND.SetBackgroundColour(corPainel)		
		
		fiscal_VDPR = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/relecf.png'), " {Shift-F1}\n Vendas por Periodo"+(" "*14), (15, 265), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_VDPR.SetForegroundColour('#E6E6FA');	fiscal_VDPR.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_VDPR.SetBezelWidth(5);	fiscal_VDPR.SetBackgroundColour(corPainel)		

		fiscal_PARA = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/relecf.png'), " {Shift-F2}\n Parametros de Configuração"+(" "*6), (240, 265), (220, 50),style=wx.ALIGN_RIGHT)
		fiscal_PARA.SetForegroundColour('#E6E6FA');	fiscal_PARA.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		fiscal_PARA.SetBezelWidth(5);	fiscal_PARA.SetBackgroundColour(corPainel)		

		self.focuP = wx.StaticText(self.painel,-1,"", pos=(470, 265))
		self.focuP.SetForegroundColour('#FFFFFF');	self.focuP.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))
		
		dIf = wx.StaticText(self.painel,-1,"  Data Inicial:",pos=(10,425))
		dIf.SetForegroundColour('#E6E6FA');	dIf.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))

		dFf = wx.StaticText(self.painel,11,"    Data Final:",pos=(10,465))
		dFf.SetForegroundColour('#E6E6FA');	dFf.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))

		cIf = wx.StaticText(self.painel,-1,"COOCRZ Inicial:",pos=(10,515))
		cIf.SetForegroundColour('#E6E6FA');	cIf.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))

		cFf = wx.StaticText(self.painel,-1,"  COOCRZ Final:",pos=(10,545))
		cFf.SetForegroundColour('#E6E6FA');	cFf.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))

		aDf = wx.StaticText(self.painel,-1,"{Shift-F3}",pos=(130,400))
		aDf.SetForegroundColour('#E6E6FA');	aDf.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))

		aCf = wx.StaticText(self.painel,-1,"{Shift-F4}",pos=(130,495))
		aCf.SetForegroundColour('#E6E6FA');	aCf.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))

		arq = wx.StaticText(self.painel,-1,"Arquivo:",pos=(5,585))
		arq.SetForegroundColour('#E6E6FA');	arq.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))

		self.ImprInt = wx.RadioButton(self.painel,-1,"{Shift-I}\nImpressão  ", pos=(10,340),style=wx.RB_GROUP)
		self.ImprInt.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD)); self.ImprInt.SetForegroundColour('#E6E6FA')
		
		self.ImprArq = wx.RadioButton(self.painel,-1,"{Shift-A}\nArquivo    ", pos=(120,340))
		self.ImprArq.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD)); self.ImprArq.SetForegroundColour('#E6E6FA')

		self.dI = wx.DatePickerCtrl(self.painel,300, pos=(130,410),size=(120,-1),style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.dF = wx.DatePickerCtrl(self.painel,301, pos=(130,460),size=(120,-1),style=wx.DP_DEFAULT)

		self.cI = wx.TextCtrl(self.painel,302,pos=(130,510),size=(65,18))
		self.cF = wx.TextCtrl(self.painel,303,pos=(130,540),size=(65,18))
		self.cI.SetMaxLength(6);	self.cF.SetMaxLength(6)

		self.Ar = wx.TextCtrl(self.painel,304,pos=(70,585),size=(630,18))
		self.Ar.Disable()
			
		Numero7 = wx.Button(self.painel,200,"7",(445,340),(80,50))
		Numero7.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Numero8 = wx.Button(self.painel,201,"8",(530,340),(80,50))
		Numero8.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Numero9 = wx.Button(self.painel,202,"9",(615,340),(80,50))
		Numero9.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Numero4 = wx.Button(self.painel,203,"4",(445,400),(80,50))
		Numero4.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Numero5 = wx.Button(self.painel,204,"5",(530,400),(80,50))
		Numero5.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Numero6 = wx.Button(self.painel,205,"6",(615,400),(80,50))
		Numero6.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Numero1 = wx.Button(self.painel,206,"1",(445,460),(80,50))
		Numero1.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Numero2 = wx.Button(self.painel,207,"2",(530,460),(80,50))
		Numero2.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Numero3 = wx.Button(self.painel,208,"3",(615,460),(80,50))
		Numero3.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Numero0 = wx.Button(self.painel,209,"0",(445,520),(80,50))
		Numero0.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		bLimpar = wx.Button(self.painel,210,"Limpar",(530,520),(80,50))
		bLimpar.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))		

		NumeroE = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/voltarp.png'), "{F12}\nVoltar", (615,520),(80,50),style=wx.ALIGN_RIGHT)
		NumeroE.SetForegroundColour('#E6E6FA');	NumeroE.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD))
		NumeroE.SetBezelWidth(5);	NumeroE.SetBackgroundColour(corPainel)		

		Numero1.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		Numero2.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		Numero3.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		Numero4.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		Numero5.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		Numero6.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		Numero7.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		Numero8.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		Numero9.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		Numero0.Bind(wx.EVT_BUTTON,self.TeclarNumeros)

		bLimpar.Bind(wx.EVT_BUTTON,self.TeclarNumeros)

		self.cI.Bind(wx.EVT_SET_FOCUS,self.intervalos)
		self.cF.Bind(wx.EVT_SET_FOCUS,self.intervalos)
		
		fiscal_LLLX.Bind(wx.EVT_BUTTON,self.relatoriosFiscais)
		fiscal_LMFC.Bind(wx.EVT_BUTTON,self.relatoriosFiscais)
		fiscal_LMFS.Bind(wx.EVT_BUTTON,self.relatoriosFiscais)
		fiscal_EMDF.Bind(wx.EVT_BUTTON,self.relatoriosFiscais)
		fiscal_AMDF.Bind(wx.EVT_BUTTON,self.relatoriosFiscais)
				
		NumeroE.Bind(wx.EVT_BUTTON,self.voltar)

	def intervalos(self,event):

		cdIntervalo = event.GetId()
		if cdIntervalo == 302:
			
			self.FocusSele = "302"
			self.focuP.SetLabel("COOCRZ: Inicial")
			self.MyNumData = ""
				
		elif cdIntervalo == 303:
			self.FocusSele = "303"
			self.focuP.SetLabel("COOCRZ: Final")
			self.MyNumData = ""
		print "jose: ",cdIntervalo
		
	def TeclarNumeros(self,event):

		idNumero = event.GetId()
		if idNumero == 200:	_Numero = "7" 
		if idNumero == 201:	_Numero = "8" 
		if idNumero == 202:	_Numero = "9" 

		if idNumero == 203:	_Numero = "4" 
		if idNumero == 204:	_Numero = "5" 
		if idNumero == 205:	_Numero = "6" 

		if idNumero == 206:	_Numero = "1" 
		if idNumero == 207:	_Numero = "2"
		if idNumero == 208:	_Numero = "3" 
		if idNumero == 209:	_Numero = "0" 

		print idNumero
		if idNumero != 210:	self.MyNumData +=_Numero
		if idNumero == 210:	self.MyNumData = ""

		if self.FocusSele == "302":	self.cI.SetValue(self.MyNumData)
		if self.FocusSele == "303":	self.cF.SetValue(self.MyNumData)
			
	def voltar(self,event):	self.Destroy()

	def relatoriosFiscais(self,event):

		_mensagem = PBI.PyBusyInfo("Gerando Relatórios Fiscais!!\n\nAguarde...", title="Relatórios Fiscais",icon=wx.Bitmap("imagens/aguarde.png"))

		idRelatorio = event.GetId() 
		print "ID-Relatorios: ",idRelatorio

		_dIni = self.dI.GetValue().FormatDate().replace("-","")
		_dFim = self.dF.GetValue().FormatDate().replace("-","")
		_cooI = self.cI.GetValue().strip().zfill(6)
		_cooF = self.cF.GetValue().strip().zfill(6)
		_daTa = False
		_cooR = False
		_impr = self.ImprInt.GetValue()
		_arqu = self.ImprArq.GetValue()
		_saida= 1
		
		arqData = datetime.datetime.now().strftime("%d/%m/%Y").replace("/","")+datetime.datetime.now().strftime("%T").replace(":","")
		gRela = "Sem Relatório..."
			
		print "Data/COO Inicial: ",_dIni," >--> ",_cooI
		print "Data/COO Final..: ",_dFim," >--> ",_cooF
		print "Date/Time.......: ",datetime.datetime.now().strftime("{ %b %a} %d/%m/%Y %T")
		print "Arquivo.........: ",arqData


		if len(_cooI) == 6 and len(_cooF) == 6 and int(_cooI) !=0 and int(_cooF) !=0:	_cooR = True
		if _cooR == False:	_daTa = True
		if idRelatorio == 601 or idRelatorio == 604:	self.ajusteReg("daruma","1") #->[LMFC]	
		if idRelatorio == 602:	self.ajusteReg("daruma","0") #->[LMFS]
		
		if idRelatorio == 600: #>---------[ Leitura X ]

			if _impr == True:	self.ECFs.enviarCMD("LX","I","","","","","Relatório { LX }-Impressão",self.focuP,"","")
			if _arqu == True:	self.ECFs.enviarCMD("LX","A","","","lx_"+arqData+".txt","retorno.txt","Relatório { LX }-Arquivo",self.focuP,self.Ar,"")
								
		elif idRelatorio == 601 or idRelatorio == 602: #--------[ LMFC/LMFS ]

			Tipo = "Data"
			if _cooR == True:

				_dIni = _cooI;	_dFim = _cooF
				Tipo  = "COO"
			
			if idRelatorio == 601 and _impr == True:	self.ECFs.enviarCMD("LMFC","I",str(_dIni),str(_dFim),"","","Relatório {LMFC->"+Tipo+"}-Impressão",self.focuP,"","")
			if idRelatorio == 602 and _impr == True:	self.ECFs.enviarCMD("LMFS","I",str(_dIni),str(_dFim),"","","Relatório {LMFS->"+Tipo+"}-Impressão",self.focuP,"","")
				
			if idRelatorio == 601 and _arqu == True:	self.ECFs.enviarCMD("LMFC","A",str(_dIni),str(_dFim),"lmfc_"+arqData+".txt","retorno.txt","Relatório {LMFC->"+Tipo+"}-Impressão",self.focuP,self.Ar,"")
			if idRelatorio == 602 and _arqu == True:	self.ECFs.enviarCMD("LMFS","A",str(_dIni),str(_dFim),"lmfs_"+arqData+".txt","retorno.txt","Relatório {LMFS->"+Tipo+"}-Impressão",self.focuP,self.Ar,"")

		elif idRelatorio == 603: #>---------[ Espelho MFD ]

			_dIni = _dIni[0:4]+_dIni[6:8]
			_dFim = _dFim[0:4]+_dFim[6:8]
			Tipo  = "Data";	_coDT = "1"
			if _cooR == True:
				_dIni = _cooI;	_dFim = _cooF
				Tipo  = "COO";	_coDT = "2"

			self.ECFs.enviarCMD("EMFD","A",str(_dIni),str(_dFim),"espelho_"+arqData+".txt","Espelho_MFD.txt","Relatório {Espelho MFD-"+Tipo+"}",self.focuP,self.Ar,_coDT)

		elif idRelatorio == 604: #>---------[ Arq.MFD ]

			Tipo = "DATA";	RelatorioT = "DATAM"
			AtoA = "ATO_MFD_DATA.TXT"
			if _cooR == True:
				_dIni = _cooI;	_dFim = _cooF;	Tipo = "COO";	RelatorioT = "COO"
				AtoA = "ATO_MFD_COO.TXT"
				
			self.ECFs.enviarCMD("AMFD","A",str(_dIni),str(_dFim),"arqmfd_"+arqData+".txt",AtoA,"Relatório {Arq. MFD-"+Tipo+"}",self.focuP,self.Ar,RelatorioT)

		self.cI.SetValue("")		
		self.cF.SetValue("")

		del _mensagem

	def ajusteReg(self,pEcf,Tipo):
		
		if pEcf == "daruma":

			self.ecfLib.regAlterarValor_Daruma ("START\LocalArquivos", ""+self.pathAtual+"/users/ecf/tmp/" )
			self.ecfLib.regAlterarValor_Daruma ("START\LocalArquivosRelatorios", ""+self.pathAtual+"/users/ecf/tmp/" )
			self.ecfLib.regAlterarValor_Daruma ("ECF\LMFCompleta", Tipo  )
			self.ecfLib.regAlterarValor_Daruma ("ECF\ArquivoLeituraX", "retorno.txt")

			
class syspastas:
	
	def pastas(self,Apath):

		dUsers = os.path.isdir(Apath+"/users")
		dLibs  = os.path.isdir(Apath+"/lib")

		dEcfs  = os.path.isdir(Apath+"/users/ecf")
		dRela  = os.path.isdir(Apath+"/users/ecf/fiscal")
		dVenda = os.path.isdir(Apath+"/users/ecf/vendas")
		dTmpec = os.path.isdir(Apath+"/users/ecf/tmp")

		if dUsers==False:	os.mkdir(Apath+"/users") 
		if dLibs ==False:	os.mkdir(Apath+"/lib")

		if dEcfs ==False:	os.mkdir(Apath+"/users/ecf") 
		if dRela ==False:	os.mkdir(Apath+"/users/ecf/fiscal")
		if dVenda==False:	os.mkdir(Apath+"/users/ecf/vendas")
		if dTmpec==False:	os.mkdir(Apath+"/users/ecf/tmp")

class  ExecutarCmd:

	"""_cmd=Comando,ai=Arquivo/Impressao,_dcI=DataCooInicial,_dcF=DataCooFinal
	   _gr=Nome do Arquivo para Gravar, _rt=Nome do Arquivo de Retorno
	   _informe=Informacoes p/SetLabel,_setL=SetarLabel,_setV=SetarValue,cooData=Relatorio COO DATA
	"""

	def __init__(self,parente,libEcfs):

		self.seEcf  = statusErro(parente,libEcfs)		
		self.LibEcf = libEcfs

	def enviarCMD(self,_cmd,_ai,_dcI,_dcF,_gr,_rt,_informe,_setL,_setV,CooData):

		self.pathAtual  = os.getcwd()
		#self.erroStatus = statusErro(self.parent,self.LibEcf)
		_saida          = 1
			
		if _cmd == "LX":
			if   _ai == "I":	_saida = self.LibEcf.iLeituraX_ECF_Daruma()
			elif _ai == "A":	_saida = self.LibEcf.rLeituraX_ECF_Daruma()
				
		if _cmd == "LMFC":
			if   _ai == "I":	_saida = self.LibEcf.iMFLer_ECF_Daruma(_dcI,_dcF)	
			if   _ai == "A":	_saida = self.LibEcf.iMFLerSerial_ECF_Daruma(_dcI,_dcF)	

		if _cmd == "LMFS":
			if   _ai == "I":	_saida = self.LibEcf.iMFLer_ECF_Daruma(_dcI,_dcF)	
			if   _ai == "A":	_saida = self.LibEcf.iMFLerSerial_ECF_Daruma(_dcI,_dcF)	

		if _cmd == "EMFD":
			_saida = self.LibEcf.rGerarEspelhoMFD_ECF_Daruma(CooData,_dcI,_dcF)

		if _cmd == "AMFD":
			print "Tipo............: ",CooData
			print "DataCooIDataCooF: ",_dcI," >--> ",_dcF
			_saida = self.LibEcf.rGerarMFD_ECF_Daruma(CooData,_dcI,_dcF)
			
		if len(_informe) !=0 and _setL !="":	_setL.SetLabel(_informe)	
		if _saida == 1 and _ai == "A" :	self.gravarArquivo(_gr,_rt,_setV)
		if _saida != 1:	self.seEcf.erroDaruma(_saida)
		
				
	def gravarArquivo(self,NomeArquivo,ArquivoRetorno,__set):

		if os.path.exists(self.pathAtual+"/users/ecf/tmp/"+ArquivoRetorno) == True:

			os.rename(self.pathAtual+"/users/ecf/tmp/"+ArquivoRetorno,self.pathAtual+"/users/ecf/fiscal/"+NomeArquivo)
			if __set !="":	__set.SetValue(self.pathAtual+"/users/ecf/fiscal/"+NomeArquivo)

class funcoesEcfs:

	def __init__(self,parente,libEcfs):

		self.seEcf  = statusErro(parente,libEcfs)		
		self.LibEcf = libEcfs
		self.parent = parente
		
	def ecfLigado(self,onoff):

		Ligado = self.LibEcf.rVerificarImpressoraLigada_ECF_Daruma()
		if Ligado !=1 and onoff == "on":	self.seEcf.erroDaruma(Ligado)
		return Ligado

	def saldoApagar(self):

		Tapagar = (" "*12)
		self.LibEcf.rCFSaldoAPagar_ECF_Daruma(Tapagar)
		return Tapagar
		
	def subTotal(self):

		TsubToT = (" "*12)
		self.LibEcf.rCFSubTotal_ECF_Daruma(TsubToT)
		return TsubToT

	def rInformacoes(self,Indice,Tamanho):

		__var = (" "*Tamanho)
		self.LibEcf.rRetornarInformacao_ECF_Daruma(Indice,__var)
		return __var

	def abrirCupom(self,documento,cliente,endereco):
		
		aberto = self.LibEcf.iCFAbrir_ECF_Daruma(documento,cliente,endereco)					
		if aberto !=1:	self.seEcf.erroDaruma(aberto)
		return aberto

	def ecfinforme(self):

		rToPag = self.rInformacoes("57",30)
		if rToPag.strip() !="":

			if int(rToPag) == 2 or int(rToPag) == 3 or int(rToPag) == 4:

				ecfToTPag = wx.MessageDialog(parente,"ECF Totalizado e/ou Pagamento...\n"+(" "*130),"Ecf em Fechamento",wx.OK|wx.ICON_EXCLAMATION)
				if ecfToTPag.ShowModal() ==  wx.OK:	pass
				ecfToTPag.Destroy()
				return False
		return True

	def liberado(self):

		_reTorno = True
		if self.seEcf.statusDaruma(6,True)   !=True:	_reTorno = False
		if self.seEcf.statusDaruma(8,True)   !=True:	_reTorno = False
		if self.seEcf.statusDaruma(11,True)  !=True:	_reTorno = False
		if self.seEcf.statusDaruma(17,True)  !=True:	_reTorno = False
		 		
		return _reTorno
	def docAberto(self):
		
		return self.seEcf.statusDaruma(12,False)		
		
	def vender(self,_imp,_qTd,_pvd,_pda,_vda,_cod,_und,_prd):
		"""_imp=Imposto, _qTd=Quantidade, _pvd=Preco de Venda, _pda=DescontoAcrescimo %
		   _vda=DescontoAcrescimo $, _cod=Codigo do Produto, _und=Unidade, _prd=Descricao do produto
		"""   
		Item = self.LibEcf.iCFVender_ECF_Daruma(_imp,_qTd,_pvd,_pda,_vda,_cod,_und,_prd)
		if Item !=1:	self.seEcf.erroDaruma(Item)
		return Item
		
	def saicaCaixa(self,ss,valor):

		if ss == 1:	SangS = self.LibEcf.iSangria_ECF_Daruma(valor,"Sangria de Caixa")
		if ss == 2:	SangS = self.LibEcf.iSuprimento_ECF_Daruma(valor,"Suprimentos de Caixa")
		return SangS

	def cancelaCupom(self):

		saida = self.LibEcf.iCFCancelar_ECF_Daruma()#-->[Fiscal CF]
		#saida = self.LibEcf.iCNFCancelar_ECF_Daruma #-->[Nao Fiscal CNF]	
		return saida

	def cancelaItem(self,ITEM):

		saida = self.LibEcf.iCFCancelarItem_ECF_Daruma(ITEM)		
		return saida
		
	def reducaoz(self):
		
		_desicao = self.seEcf.statusDaruma(6,False)
		_mensage = "Não há RZ pendente...\n"
		if _desicao == False:	_mensage = "Redução Z do dia anterior pendente!!\n"

		rzp = wx.MessageDialog(self.parent,_mensage+(" "*120),"Reducão Z",wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
		if rzp.ShowModal() ==  wx.ID_YES:
			self.LibEcf.iReducaoZ_ECF_Daruma()			

		rzp.Destroy()
		
	def estendido(self,indice,Tamanho):
		
		var = (" "*Tamanho)
		self.LibEcf.rInfoEstendida_ECF_Daruma(indice,var)
		return var

	def totalizaecf(self,desAcr,vlrDA):

		self.LibEcf.iCFTotalizarCupom_ECF_Daruma(desAcr,vlrDA)
		
	def fazpagamento(self,forma,valor):

		saida = self.LibEcf.iCFEfetuarPagamento_ECF_Daruma(forma,valor)			
		if saida !=1:	self.seEcf.erroDaruma(saida)
		return saida

	def encerramento(self,adicional,informes):
		saida = self.LibEcf.iCFEncerrar_ECF_Daruma(adicional,informes)	
		if saida !=1:	self.seEcf.erroDaruma(saida)
		return saida

	def TipoDocumento(self):
		var = (" "*3)
		self.LibEcf.rTipoUltimoDocumentoStr_ECF_Daruma(var)
		return var
		
		
class statusErro:

	def __init__(self,parente,libEcfs):

		self.LibEcf = libEcfs
		self.parent = parente

	def statusDaruma(self,indice,mostrar):

		_resulta = (" "*18)
		_num = 0
		_reTorno = self.LibEcf.rStatusImpressoraBinario_ECF_Daruma(_resulta)

		for i in _resulta:
			_num = _num + 1
			if _num==1 and i=="0": _r01="{01} [0] Modo Fiscal"; _s01 = True
			if _num==1 and i=="1": _r01="{01} [1] Em MIT (Ligado com o jumper aberto)"; _s01 = False

			if _num==2 and i=="0": _r02="{02} [0] MF Disponível"; _s02 = True
			if _num==2 and i=="1": _r02="{02} [1] MF esgotada ou em erro irrecuperável"; _s02 = False

			if _num==3 and i=="0": _r03="{03} [0] MFDE Disponível"; _s03 = True
			if _num==3 and i=="1": _r03="{03} [1] MFDE esgotada ou em erro irrecuperável"; _s03 = False

			if _num==4 and i=="0": _r04="{04} [0] Dia fiscal não aberto"; _s04 = False
			if _num==4 and i=="1": _r04="{04} [1] Em jornada fiscal"; _s04 = True

			if _num==5 and i=="0": _r05="{05} [0] Ainda não emitiu RZ hoje (com dia fiscal aberto)"; _s05 = True
			if _num==5 and i=="1": _r05="{05} [1] Já emitiu RZ não pendente hoje"; _s05 = False

			if _num==6 and i=="0": _r06="{06} [0] Não há RZ pendente"; _s06 = True
			if _num==6 and i=="1": _r06="{06} [1] RZ do dia anterior pendente"; _s06 = False

			if _num==7 and i=="0": _r07="{07} [0] Near End não detectado"; _s07 = True
			if _num==7 and i=="1": _r07="{07} [1] Near End detectado"; _s07 = False

			if _num==8 and i=="0": _r08="{08} [0] Bobina de papel presente"; _s08 = True
			if _num==8 and i=="1": _r08="{08} [1] Bobina de papel ausente"; _s08 = False

			if _num==9 and i=="0": _r09="{09} [0] Gaveta fechada"; _s09 = True
			if _num==9 and i=="1": _r09="{09} [1] Gaveta aberta"; _s09 = False

			if _num==10 and i=="0": _r10="{10} [0] Cheque presente"; _s10= True
			if _num==10 and i=="1": _r10="{10} [1] Não há cheque posicionado"; _s10 = False

			if _num==11 and i=="0": _r11="{11} [0] ECF On Line"; _s11 = True
			if _num==11 and i=="1": _r11="{11} [1] ECF Off Line"; _s11 = False

			if _num==12 and i=="0": _r12="{12} [0] Nenhum documento aberto"; _s12 = True
			if _num==12 and i=="1": _r12="{12} [1] Algum documento aberto"; _s12 = False

			if _num==13 and i=="0": _r13="{13} [0] Papel carregado (bobina)"; _s13 = True
			if _num==13 and i=="1": _r13="{13} [1] Aguardando papel"; _s13 = False

			if _num==14 and i=="0": _r14="{14} [0] Documento posicionado"; _s14 = True
			if _num==14 and i=="1": _r14="{14} [1] Aguardando posicionamento do documento"; _s14 = False

			if _num==15 and i=="0": _r15="{15} [0] Cheque posicionado"; _s15 = True
			if _num==15 and i=="1": _r15="{15} [1] Aguardando posicionamento do cheque"; _s15 = False

			if _num==16 and i=="0": _r16="{16} [0] Não há cheque/documento obstruindo"; _s16 = True
			if _num==16 and i=="1": _r16="{16} [1] Aguardando remoção do cheque/documento"; _s16 = False

			if _num==17 and i=="0": _r17="{17} [0] Tampa fechada"; _s17 = True
			if _num==17 and i=="1": _r17="{17} [1] Tampa aberta"; _s17 = False

			if _num==18 and i=="0": _r18="{18} [0] Tampa de cabeça térmica fechada"; _s18 = True
			if _num==18 and i=="1": _r18="{18} [1] Tampa de cabeça térmica aberta"; _s18 = False

		if indice==20: wx.MessageBox("Status do ECF-Retorno"+(" "*90)+" \n\n"+_r01+
			"\n"+_r02+
			"\n"+_r03+
			"\n"+_r04+
			"\n"+_r05+
			"\n"+_r06+
			"\n"+_r07+
			"\n"+_r08+
			"\n"+_r09+
			"\n"+_r10+
			"\n"+_r11+
			"\n"+_r12+
			"\n"+_r13+
			"\n"+_r14+
			"\n"+_r15+
			"\n"+_r16+
			"\n"+_r17+
			"\n"+_r18,"Status do ECF",wx.OK)	       

		elif not indice==20:
			
			if indice==1: __saida = _r01; __voltar = _s01
			if indice==2: __saida = _r02; __voltar = _s02
			if indice==3: __saida = _r03; __voltar = _s03
			if indice==4: __saida = _r04; __voltar = _s04
			if indice==5: __saida = _r05; __voltar = _s05
			if indice==6: __saida = _r06; __voltar = _s06
			if indice==7: __saida = _r07; __voltar = _s07
			if indice==8: __saida = _r08; __voltar = _s08
			if indice==9: __saida = _r09; __voltar = _s09
			if indice==10: __saida = _r10; __voltar = _s10
			if indice==11: __saida = _r11; __voltar = _s11
			if indice==12: __saida = _r12; __voltar = _s12
			if indice==13: __saida = _r13; __voltar = _s13
			if indice==14: __saida = _r14; __voltar = _s14
			if indice==15: __saida = _r15; __voltar = _s15
			if indice==16: __saida = _r16; __voltar = _s16
			if indice==17: __saida = _r17; __voltar = _s17
			if indice==18: __saida = _r18; __voltar = _s18

			if mostrar == True and __voltar == False:
				__exclui = wx.MessageDialog(self.parent,str(__saida)+"\n"+(" "*120),"ECFs->Retornos Status",wx.OK|wx.ICON_INFORMATION)
				if __exclui.ShowModal() ==  wx.OK:	pass
				__exclui.Destroy()
				return __voltar

			return __voltar

	def erroDaruma(self,erro):
		
		if erro == 0:	__saida = "{"+str(erro)+"}"+" Erro durante a execução."
		if erro == -1:	__saida = "{"+str(erro)+"}"+" Erro do Método."
		if erro == -2:	__saida = "{"+str(erro)+"}"+" Parâmetro incorreto."
		if erro == -3:	__saida = "{"+str(erro)+"}"+" Alíquota (Situação tributária) não programada."
		if erro == -4:	__saida = "{"+str(erro)+"}"+" Chave do Registry não encontrada."
		if erro == -5:	__saida = "{"+str(erro)+"}"+" Erro ao Abrir a porta de Comunicação."
		if erro == -6:	__saida = "{"+str(erro)+"}"+" Impressora Desligada."
		if erro == -7: __saida = "{"+str(erro)+"}"+"Erro no Número do Banco."
		if erro == -8: __saida = "{"+str(erro)+"}"+"Erro ao Gravar as informações no arquivo de Status ou de Retorno de Info."
		if erro == -9: __saida = "{"+str(erro)+"}"+"Erro ao Fechar a porta de Comunicação."
		if erro == -10: __saida = "{"+str(erro)+"}"+"O ECF não tem a forma de pagamento e não permite cadastrar esta forma."
		if erro == -12: __saida = "{"+str(erro)+"}"+"A função executou o comando porém o ECF sinalizou Erro, chame a rStatusUltimoCmdInt_ECF_Daruma para identificar o Erro."
		if erro == -24: __saida = "{"+str(erro)+"}"+"Forma de Pagamento não Programada."
		if erro == -25: __saida = "{"+str(erro)+"}"+"Totalizador nao ECF Não Vinculado não Programado."
		if erro == -27: __saida = "{"+str(erro)+"}"+"Foi Detectado Erro ou Warning na Impressora."
		if erro == -28: __saida = "{"+str(erro)+"}"+"Time-Out."
		if erro == -40: __saida = "{"+str(erro)+"}"+"Tag XML Inválida."
		if erro == -50: __saida = "{"+str(erro)+"}"+"Problemas ao Criar Chave no Registry."
		if erro == -51: __saida = "{"+str(erro)+"}"+"Erro ao Gravar LOG."
		if erro == -52: __saida = "{"+str(erro)+"}"+"Erro ao abrir arquivo."
		if erro == -53: __saida = "{"+str(erro)+"}"+"Fim de arquivo."
		if erro == -60: __saida = "{"+str(erro)+"}"+"Erro na tag de formatação DHTML."
		if erro == -90: __saida = "{"+str(erro)+"}"+"Erro Configurar a Porta de Comunicação."
		if erro == -99: __saida = "{"+str(erro)+"}"+"Parâmetro inválido ou ponteiro nulo de parâmetro."
		if erro == -101: __saida = "{"+str(erro)+"}"+"Erro ao LER ou ESCREVER arquivo"
		if erro == -102: __saida = "{"+str(erro)+"}"+"Erro arquivo corrompido"
		if erro == -103: __saida = "{"+str(erro)+"}"+"Não foram encontradas as DLLs auxiliares (lebin.dll e LeituraMFDBin.dll)"
		if erro == -104: __saida = "{"+str(erro)+"}"+"Data informada é inferior ao primeiro documento emitido"
		if erro == -105: __saida = "{"+str(erro)+"}"+"Data informada é maior que a ultima redução Z impressa"
		if erro == -106: __saida = "{"+str(erro)+"}"+"Nao possui movimento fiscal"
		if erro == -107: __saida = "{"+str(erro)+"}"+"Porta de comunicação ocupada"
		if erro == -110: __saida = "{"+str(erro)+"}"+"Indica que o GT foi atualizado no arquivo de registro do PAF"
		if erro == -112: __saida = "{"+str(erro)+"}"+"O numero de serie ja existe no arquivo do PAF"
		if erro == -113: __saida = "{"+str(erro)+"}"+"ECF conectado nao cadastrado no arquivo do PAF"
		if erro == -114: __saida = "{"+str(erro)+"}"+"MFD Danificada"
		if erro == -115: __saida = "{"+str(erro)+"}"+"Erro ao abrir arquivos .idx/.dat/.mf"
		if erro == -116: __saida = "{"+str(erro)+"}"+"Intervalo solicitado não é válido"
		if erro == -117: __saida = "{"+str(erro)+"}"+"Impressora não identificada durante download dos binários"
		if erro == -118: __saida = "{"+str(erro)+"}"+"Erro ao abrir porta serial"
		if erro == -119: __saida = "{"+str(erro)+"}"+"Leitura dos binários abortada"

		__exclui = wx.MessageDialog(self.parent,str(__saida)+"\n"+(" "*120),"ECFs->Retornos Status",wx.OK|wx.ICON_INFORMATION)
		if __exclui.ShowModal() ==  wx.OK:	pass
		__exclui.Destroy()
		return
			
class ecfSel:

	driveEcf = ''
	mnFiscal = ''
	
	def accessoMenu(self,pEcf,pDriver,corPainel,parente):

		ecfSel.driveEcf = pDriver
		FiscalMenu.PainelCor = corPainel

		ecfSel.mnFiscal= FiscalMenu(parent=parente,id=-1)
		ecfSel.mnFiscal.Center()
		ecfSel.mnFiscal.Show()					
