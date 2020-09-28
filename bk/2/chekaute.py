#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import ctypes
import os
from conectar import *	
from menufiscal import *
from decimal import *
import wx.lib.agw.pybusyinfo as PBI
from wx.lib.buttons import GenBitmapTextButton

class PainelPrincipal(wx.Panel):
	
	cor   = "#47665B" #"#6A1E1E" #"#575757"
	quant = Decimal('1.000')
	TotalGeral = Decimal('0.000')
	TotalSubTo = Decimal('0.000')
	LivreCaixa = True
	ConsultaCd = ''
	libEcfs    = ''
	
	acessCons  = ''

	documento = ''
	NomeClien = ''
	EndeClien = ''
	arquivoCF = ''
	
	def __init__(self,parent,id):

		self.bancos     = ecfPrincipal._basedd
		self.cursor     = ecfPrincipal._cursor
		self.gPath		= os.getcwd()
		pasTasSis 	    = syspastas()
		self.parente    = parent

		pasTasSis.pastas(self.gPath) #-->[ Cria as pasta do sistema para o ecf ]

		##self.ecfLib = ctypes.cdll.LoadLibrary('lib/64/libDarumaFramework.so')
		##self.ecfLib = ctypes.CDLL(self.gPath+'/lib/32/libDarumaFramework.so')  

		#self.fEcfs	        	= funcoesEcfs(parent,self.ecfLib)
		#PainelPrincipal.libEcfs = self.ecfLib
		#self.erroStatus         = statusErro(parent,self.ecfLib)

		wx.Panel.__init__(self, parent, -1,size=(wx.DisplaySize()[0],wx.DisplaySize()[1]),style=0) # wx.WANTS_CHARS|wx.SUNKEN_BORDER)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_KEY_UP, self.Teclas)

		wx.StaticBox(self, -1, 'Produto', pos=(25,55),  size=(975, 55),style=wx.SUNKEN_BORDER).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.LIGHT))
		wx.StaticBox(self, -1, '{F9}-Funções Gerais', pos=(25,170), size=(400, 70),style=wx.SUNKEN_BORDER).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.LIGHT))
		wx.StaticBox(self, -1, 'Alterar Quantidade', pos=(25,320), size=(400, 70),style=wx.SUNKEN_BORDER).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.LIGHT))
		wx.StaticBox(self, -1, 'Procurar Item', pos=(25,470), size=(400, 70),style=wx.SUNKEN_BORDER).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.LIGHT))

		Tgeral = wx.StaticBox(self, -1, 'Total Geral', pos=(25,555), size=(400, 70),style=wx.SUNKEN_BORDER|wx.ALIGN_RIGHT)
		Tgeral.SetFont(wx.Font(20, wx.MODERN, wx.ITALIC,wx.LIGHT));	Tgeral.SetForegroundColour('#FFFFFF')
		
		self.Descricao = wx.StaticText(self, wx.ID_STATIC,pos=(35,65))
		self.Descricao.SetForegroundColour('#4E8BC7');	self.Descricao.SetFont(wx.Font(22, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.pUnitario = wx.StaticText(self, wx.ID_STATIC,label="",pos=(35,195))
		self.pUnitario.SetForegroundColour('#FFFFFF');	self.pUnitario.SetFont(wx.Font(22, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.Quantidad = wx.StaticText(self, wx.ID_STATIC,label="",pos=(35,340),size=(400,-1),style=wx.ALIGN_RIGHT)
		self.Quantidad.SetForegroundColour('#FFFFFF');	self.Quantidad.SetFont(wx.Font(22, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.TotalItem = wx.StaticText(self, wx.ID_STATIC,label="",pos=(35,490))
		self.TotalItem.SetForegroundColour('#FFFFFF');	self.TotalItem.SetFont(wx.Font(22, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.TotaGeral = wx.StaticText(self, wx.ID_STATIC,label="",pos=(35,585))
		self.TotaGeral.SetForegroundColour('#4E8BC7');	self.TotaGeral.SetFont(wx.Font(22, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.Tcoo = wx.StaticText(self, wx.ID_STATIC,label="",pos=(wx.DisplaySize()[0]-(1024-760),22))
		self.Tcoo.SetForegroundColour('#E6E6FA');	self.Tcoo.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.Tccf = wx.StaticText(self, wx.ID_STATIC,label="",pos=(wx.DisplaySize()[0]-(1024-760),37))
		self.Tccf.SetForegroundColour('#E6E6FA');	self.Tccf.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.TMod = wx.StaticText(self, wx.ID_STATIC,label="",pos=(wx.DisplaySize()[0]-(1024-855),22))
		self.TMod.SetForegroundColour('#E6E6FA');	self.TMod.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.TFab = wx.StaticText(self, wx.ID_STATIC,label="",pos=(wx.DisplaySize()[0]-(1024-855),37))
		self.TFab.SetForegroundColour('#E6E6FA');	self.TFab.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.relogio, self.timer)
		self.timer.Start(1000)
		
		self.DataHora = wx.StaticText(self,wx.ID_ANY, label='',pos=(wx.DisplaySize()[0]-(1024-780),10))		
		self.DataHora.SetForegroundColour('#FFFFFF');	self.DataHora.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.bUnitario = GenBitmapTextButton(self, 100, wx.Bitmap('imagens/opcao.png'), (" "*8)+"Valor Unitario", (25,120),(400,50),style=wx.BU_LEFT)
		self.bUnitario.SetBackgroundColour(self.cor);	self.bUnitario.SetForegroundColour("#FFFFFF")
		self.bUnitario.SetFont(wx.Font(20, wx.MODERN, wx.ITALIC,wx.BOLD));	self.bUnitario.SetBezelWidth(5)

		self.bQuantida = GenBitmapTextButton(self, 101, wx.Bitmap('imagens/opcao.png'), (" "*12)+"Quantidade", (25,270),(400,50),style=wx.BU_LEFT)
		self.bQuantida.SetBackgroundColour(self.cor);	self.bQuantida.SetForegroundColour("#FFFFFF")
		self.bQuantida.SetFont(wx.Font(20, wx.MODERN, wx.ITALIC,wx.BOLD));	self.bQuantida.SetBezelWidth(5)

		self.dadosAssicia=wx.StaticText(self,wx.ID_ANY, label='',pos=(470,110))		
		self.dadosAssicia.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD));	self.dadosAssicia.SetForegroundColour("#FFFFFF")

		self.bTotaItem = GenBitmapTextButton(self, 102, wx.Bitmap('imagens/opcao.png'), (" "*9)+"Total do Item", (25,420),(400,50),style=wx.BU_LEFT)
		self.bTotaItem.SetBackgroundColour(self.cor);	self.bTotaItem.SetForegroundColour("#FFFFFF")
		self.bTotaItem.SetFont(wx.Font(20, wx.MODERN, wx.ITALIC,wx.BOLD));	self.bTotaItem.SetBezelWidth(5)

		self.bPAgamento = GenBitmapTextButton(self, 1, wx.Bitmap('imagens/pagamento.png'), "{F1}\nPagamento", (wx.DisplaySize()[0]-(1024-470),wx.DisplaySize()[1]-(768-635)),(125,60),style=wx.BU_LEFT)
		self.bPAgamento.SetForegroundColour('#E6E6FA');	self.bPAgamento.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bPAgamento.SetBezelWidth(5);	self.bPAgamento.SetBackgroundColour(self.cor)		

		self.bConsulta = GenBitmapTextButton(self, 1, wx.Bitmap('imagens/consulta.png'), "{F2}\nConsultar", (wx.DisplaySize()[0]-(1024-605),wx.DisplaySize()[1]-(768-635)),(125,60),style=wx.BU_LEFT)
		self.bConsulta.SetForegroundColour('#E6E6FA');	self.bConsulta.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bConsulta.SetBezelWidth(5);	self.bConsulta.SetBackgroundColour(self.cor)		

		self.bCancela = GenBitmapTextButton(self, 1, wx.Bitmap('imagens/cancelar.png'), "{F3}\nCancelar\nItemCupom", (wx.DisplaySize()[0]-(1024-742),wx.DisplaySize()[1]-(768-635)),(125,60),style=wx.BU_LEFT)
		self.bCancela.SetForegroundColour('#E6E6FA');	self.bCancela.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bCancela.SetBezelWidth(5);	self.bCancela.SetBackgroundColour(self.cor)		

		self.bFechar = GenBitmapTextButton(self, 1, wx.Bitmap('imagens/sair.png'), "{F12}\nSair", (wx.DisplaySize()[0]-(1024-878),wx.DisplaySize()[1]-(768-635)),(125,60),style=wx.BU_LEFT)
		self.bFechar.SetForegroundColour('#E6E6FA');	self.bFechar.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bFechar.SetBezelWidth(5);	self.bFechar.SetBackgroundColour(self.cor)		

		self.bOrcame = GenBitmapTextButton(self, 1, wx.Bitmap('imagens/orcfiscal.png'), "  {F4}\n  Recuperar Orcamento", (25,wx.DisplaySize()[1]-(768-635)),(195,60),style=wx.BU_LEFT)
		self.bOrcame.SetForegroundColour('#E6E6FA');	self.bOrcame.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bOrcame.SetBezelWidth(5);	self.bOrcame.SetBackgroundColour(self.cor)		

		self.bMFisca = GenBitmapTextButton(self, 1, wx.Bitmap('imagens/orcfiscal.png'), "  {F5}\n  Menu Fiscal"+(" "*8), (232,wx.DisplaySize()[1]-(768-635)),(195,60),style=wx.BU_LEFT)
		self.bMFisca.SetForegroundColour('#E6E6FA');	self.bMFisca.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bMFisca.SetBezelWidth(5);	self.bMFisca.SetBackgroundColour(self.cor)		

		self.bCancela.SetBackgroundColour(self.cor)
		self.bCancela.SetForegroundColour("#FFFFFF")
		self.bCancela.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD))

		self.bFechar.SetBackgroundColour(self.cor)
		self.bFechar.SetForegroundColour("#FFFFFF")
		self.bFechar.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD))

		self.Bind(wx.EVT_PAINT, self.OnPaint)

		self.ListaPro = wx.ListBox(self, -1,choices='',pos=(wx.DisplaySize()[0]-(1024-470), 120), size=(530, wx.DisplaySize()[1]-(768-495)), style=wx.LB_SINGLE|wx.RAISED_BORDER)
		self.consultar = wx.TextCtrl(self, -1,'', pos=(wx.DisplaySize()[0]-(1024-470),wx.DisplaySize()[1]-(768-617)),size=(530, 15),style=wx.TE_PROCESS_ENTER|wx.NO_BORDER)
		self.consultar.SetBackgroundColour("#302E2E");	self.consultar.SetForegroundColour("#4B4949")

		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.venderItem)
	
		self.bPAgamento.Bind(wx.EVT_BUTTON, self.pagamentos)
		self.bConsulta.Bind(wx.EVT_BUTTON,self.consultarProd)
		self.bCancela.Bind(wx.EVT_BUTTON,self.cancelar)
		self.bFechar.Bind(wx.EVT_BUTTON, self.fechar)

		self.bUnitario.Bind(wx.EVT_BUTTON,self.fGerais)
		self.bQuantida.Bind(wx.EVT_BUTTON,self.bBotoes)
		self.bTotaItem.Bind(wx.EVT_BUTTON,self.bBotoes)
		self.bMFisca.Bind(wx.EVT_BUTTON,self.fMenuFiscal)

		#self.caixalivre()

		#self.consultar.SetToolTipString(u'')
		#self.consultar.SetFocus()

	def GravaTexto(self,TexTo1,TexTo2,TexTo3):

		__arquivo = open(self.gPath+"/users/ecf/vendas/root_cupom"+self.arquivoCF+".txt","a")
		if len(TexTo1) !=0:	__arquivo.writelines("\n"+TexTo1)
		if len(TexTo2) !=0:	__arquivo.writelines("\n"+TexTo2)
		if len(TexTo3) !=0:	__arquivo.writelines("\n"+TexTo3)

		__arquivo.close()
		
	def atualizaAssocia(self,_doc,_nom,_end):

		self.documento = _doc
		self.NomeClien = _nom
		self.EndeClien = _end
		if len(_doc.strip()) !=0:
			self.dadosAssicia.SetLabel("CPF-CNPJ: "+self.documento)
		else:	self.dadosAssicia.SetLabel('')
		
	def Teclas(self,event):

		keycode=event.GetKeyCode()
		if keycode == wx.WXK_F1:	self.pagamentos(self)
		if keycode == wx.WXK_F2:	self.consultarProd(self)
		if keycode == wx.WXK_F3:	self.cancelar(self)
		if keycode == wx.WXK_F5:	self.fMenuFiscal(self)
		if keycode == wx.WXK_F9:	self.fGerais(self)
		if keycode == wx.WXK_F12:	self.fechar(self)
	
		event.Skip()		

	def bBotoes(self,event):

		iDentifica = event.GetId()
		
		if iDentifica == 101 or iDentifica == 102:

			TecladoBotoes.Receptor = iDentifica

			PainelPrincipal.acessCons=TecladoBotoes(parent=self.parente,id=-1)
			PainelPrincipal.acessCons.Center()
			PainelPrincipal.acessCons.Show()					
	
		self.consultar.SetFocus()

	def fGerais(self,event):

		funcoesGerais.acessCons=funcoesGerais(parent=self.parente,id=-1)
		funcoesGerais.acessCons.Center()
		funcoesGerais.acessCons.Show()					

		self.consultar.SetFocus()

	def fMenuFiscal(self,event):

		ecfPrinter = ecfSel()
		ecfPrinter.accessoMenu("daruma",self.ecfLib,self.cor,self.parente)
		self.consultar.SetFocus()
		
	def relogio(self,event):
	
		self.DataHora.SetLabel(' %s ' % datetime.datetime.now().strftime("{ %b %a} %d/%m/%Y %T"))

	def limpaVendas(self):

		self.ListaPro.Clear()
		
		self.Descricao.SetLabel("")
		self.pUnitario.SetLabel("")
		self.Quantidad.SetLabel("")
		self.TotalItem.SetLabel("")
		self.TotaGeral.SetLabel("")

		self.quant = Decimal('1.000')
		self.TotalGeral = Decimal('0.000')
		self.TotalSubTo = Decimal('0.000')
		self.LivreCaixa = True

	def caixalivre(self):

		DocAberto = self.erroStatus.statusDaruma(12,False)
		ReducaoPD = self.erroStatus.statusDaruma(6,False)
		ECFOffLin = self.fEcfs.ecfLigado('off') 

		
		if DocAberto == False:
			self.Descricao.SetLabel((" "*( ( 52 - len("DOCUMENTO ABERTO".strip()) ) / 2 ))+"DOCUMENTO ABERTO")	
			self.LivreCaixa = False
	
			Tapagar = self.fEcfs.saldoApagar()
			TsubToT = self.fEcfs.subTotal()
			
			if int(TsubToT) > 0:
				
				self.TotalGeral = Decimal( ('%.3f' % Decimal(TsubToT[:10]+"."+TsubToT[10:])) )
				self.TotalSubTo = Decimal( ('%.3f' % Decimal(Tapagar[:10]+"."+Tapagar[10:])) )				

				TotalGeralf     = ('%.2f' % self.TotalGeral).replace('.',',')
				self.TotaGeral.SetLabel((" "*( 21 - len(TotalGeralf) ))+TotalGeralf)	

		if ReducaoPD == False:
			self.Descricao.SetLabel((" "*( ( 52 - len("REDUÇÃO PENDENTE".strip()) ) / 2 ))+"REDUÇÃO PENDENTE")	
			self.LivreCaixa = False

		if ECFOffLin != 1:
			self.Descricao.SetLabel((" "*( ( 52 - len("ECF OFF-LINE".strip()) ) / 2 ))+"ECF OFF-LINE")	
			self.LivreCaixa = False

		if DocAberto == True and ReducaoPD == True and ECFOffLin==1:	
			self.Descricao.SetLabel((" "*( ( 52 - len("CAIXA LIVRE".strip()) ) / 2 ))+"CAIXA LIVRE")
			self.LivreCaixa = True
		
		_fabricante = self.fEcfs.rInformacoes("78",21)
		_modelo		= self.fEcfs.rInformacoes("81",20)
		_ccf        = self.fEcfs.rInformacoes("30",6)
		_coo        = self.fEcfs.rInformacoes("26",6)

		self.Tcoo.SetLabel("COO:"+_coo)											
		self.Tccf.SetLabel("CCF:"+_ccf)											
		
		self.TMod.SetLabel(_modelo)
		self.TFab.SetLabel(_fabricante)
		
		if DocAberto == False:

			self.arquivoCF = _coo
			if os.path.exists(self.gPath+"/users/ecf/vendas/root_cupom"+_coo+".txt") == True:
				
				__arquivo = open(self.gPath+"/users/ecf/vendas/root_cupom"+_coo+".txt","r")
				for i in __arquivo:
					if len(i.strip()) !=0:	self.ListaPro.Append(i.rstrip())
				__arquivo.close()
				
			else:

				NoFile = wx.MessageDialog(self,"Arquivo não recuperado!!\n"+(" "*130),"Recuperado ECF",wx.OK)
				if NoFile.ShowModal() ==  wx.OK:	pass
				NoFile.Destroy()

	def Interceptar(self,__codigo):
		
		self.adiciona(__codigo)

	def venderItem(self,event):

		__codigo = self.consultar.GetValue().upper().strip()
		self.adiciona(__codigo)
		self.consultar.Clear()

	def cancelarItem(self,item,valorCan):

		self.atualizaSaldo()
		vCancela = Decimal( ('%.3f' % Decimal(valorCan[:9]+"."+valorCan[9:])) )
		vCancela =  ('%.2f' % vCancela).replace('.',',')

		self.ListaPro.Append('Cancelamento de ITEM: '+item)		
		self.ListaPro.Append('Cancelamento de ITEM Valor: '+vCancela)		

		itemsControle = self.ListaPro.GetCount()
		self.ListaPro.SetSelection((itemsControle-1))
		self.GravaTexto('Cancelamento de ITEM: '+item,'Cancelamento de ITEM Valor: '+vCancela,"")

	def finalizaCupom(self,Texto):

		self.ListaPro.Append(Texto)
		itemsControle = self.ListaPro.GetCount()
		self.ListaPro.SetSelection((itemsControle-1))
		self.GravaTexto(Texto,"","")

#---------------[ Abertura do Cupom, Emissao de ITEMS]		
	def adiciona(self,ocorrencia):

		if self.fEcfs.ecfLigado("on") !=1:	return
		if( self.fEcfs.ecfinforme() == False ):

			self.consultar.Clear()
			self.consultar.SetFocus()
			return
	
		if self.TotalSubTo > 0:

			semValor = wx.MessageDialog(self,"Documento em aberto, Ecf Totalizado...\nSelecione a opção de Pagamento para fazer o fechamento do cupom\n"+(" "*130),"Ecf Totalizado",wx.OK)
			if semValor.ShowModal() ==  wx.OK:	pass
			semValor.Destroy()
			self.consultar.Clear()
			self.consultar.SetFocus()
						
			return

		NovaQT1 = ocorrencia[:1]         #-->[Retorna o primeiro caracter]
		NovaQT2 = ocorrencia[1:2]        #-->[Retorna o segundo  caracter]
		NovaQT3 = ocorrencia[1:].strip() #-->[Retorna todos o caracter apos o primeiro]
		
		if NovaQT1 == "X" and NovaQT2.isdigit() == True:

			QuanTidade1 = NovaQT3.replace(',', '.')
			QuanTidade2 = Decimal( ('%.3f' % Decimal(QuanTidade1)) )

			localiza = "Quantidade Alterada: ["+str(QuanTidade2)+"]"
			self.Descricao.SetLabel((" "*( ( 52 - len(localiza.strip()) ) / 2 ))+localiza)
			
			self.quant = QuanTidade2

			if Decimal(self.quant) == 0:

				localiza = "Quantidade [0.000], Mantendo Quantidade em [1.000]"
				self.Descricao.SetLabel((" "*( ( 52 - len(localiza.strip()) ) / 2 ))+localiza)
				self.quant = Decimal('1.000')
							
			return

		if ocorrencia !=0:	_retorno = self.cursor.execute("SELECT pd_barr,pd_nome,pd_unid,pd_tpr1,pd_codi FROM produtos where pd_barr='"+ocorrencia+"' ")
		if ocorrencia !=0 and _retorno == 0:	_retorno = self.cursor.execute("SELECT pd_barr,pd_nome,pd_unid,pd_tpr1,pd_codi FROM produtos where pd_codi='"+ocorrencia+"' ")
	
		if ocorrencia != '' and _retorno != 0:

			_result   = self.cursor.fetchall()
			if _result[0][3] == 0:

				semPreco = wx.MessageDialog(self,_result[0][0]+' '+_result[0][1]+u"\n\nSem Preço de venda...\n"+(" "*130),u"Emissão do Cupom, Produto sem Preço de Venda",wx.OK)
				if semPreco.ShowModal() ==  wx.OK:	pass
				semPreco.Destroy()
				return
		
			if self.fEcfs.ecfLigado("on") == 1 and self.fEcfs.liberado() == True: 

				if self.fEcfs.docAberto() == True and self.fEcfs.abrirCupom(self.documento,self.NomeClien,self.EndeClien) == 1:

					_ccf = self.fEcfs.rInformacoes("30",6)
					_coo = self.fEcfs.rInformacoes("26",6)
								
					self.arquivoCF = _coo
					self.ListaPro.Append("A b e r t u r a do E C F")		
					self.ListaPro.Append("COO: "+str(_coo))
					self.ListaPro.Append("CCF: "+str(_ccf))

					self.GravaTexto("A b e r t u r a do E C F","COO: "+str(_coo),"CCF: "+_ccf)

					if len(self.documento.strip()) !=0:
									
						self.ListaPro.Append("CPF-CNPJ: "+str(self.documento))
						self.ListaPro.Append("CLIENTE.: "+str(self.NomeClien))
						self.ListaPro.Append("ENDERECO: "+str(self.EndeClien))
						self.GravaTexto("CPF-CNPJ: "+str(self.documento),"CLIENTE.: "+str(self.NomeClien),"\nENDERECO: "+str(self.EndeClien))
							
					self.ListaPro.Append("-"*125)
					self.Tcoo.SetLabel("COO:"+_coo)											
					self.Tccf.SetLabel("CCF:"+_ccf)											
					self.GravaTexto(("-"*125),"","")
						
				if  self.erroStatus.statusDaruma(6,False) == True:	self.LivreCaixa = False

				if( self.LivreCaixa == False and self.erroStatus.statusDaruma(6,True) == True ):

					_codigos = _result[0][0]
					_produto = _result[0][1]
					_unidade = _result[0][2]
					_precovd = _result[0][3]
					_codigop = _result[0][4]
							
					_precovd = self.truncar(_precovd)
					TotalIte = ( _precovd * self.quant )

					TotalIte = Decimal( format(TotalIte,'.2f') )

					_qunatidf = ('%.3f' % self.quant).replace('.', ',')
					_precovdf = self.truncarFormatar(_precovd)
					TotalItef = ('%.2f' % TotalIte).replace('.',',')
					if _codigos.strip() == "":	_codigos = _codigop
					
					if self.fEcfs.vender("II",_qunatidf,_precovdf,"D%","0,00",_codigos,"UN",_produto) == 1:
						
						nItem = self.fEcfs.rInformacoes("58",3)
						Texto_1 = nItem+' '+_codigos+' '+_produto
						Texto_2 = (' '*20)+_qunatidf+' '+_unidade+' X '+_precovdf+' '+TotalItef

						self.ListaPro.Append(Texto_1)		
						self.ListaPro.Append(Texto_2)		
							
						itemsControle = self.ListaPro.GetCount()
						self.ListaPro.SetSelection((itemsControle-1))

						self.Descricao.SetLabel((" "*( ( 52 - len(_produto.strip()) ) / 2 ))+_produto)
						self.pUnitario.SetLabel((" "*( 21 - len(_precovdf) ))+_precovdf)	
						self.Quantidad.SetLabel((" "*( 21 - len(_qunatidf) ))+_qunatidf)
						self.TotalItem.SetLabel((" "*( 21 - len(TotalItef) ))+TotalItef)	

						self.atualizaSaldo()											
						self.erroStatus.statusDaruma(13,True) #-->[ Papel ]					
						self.erroStatus.statusDaruma(8,True) #--->[ Papel ]					
						self.GravaTexto(Texto_1,Texto_2,"")
						
		else:
			
			if len(ocorrencia) != 0:	localiza = ocorrencia+u", Não Localizado!!"
			if len(ocorrencia) == 0:	localiza = "Codigo,Descrição Vazio!!"

			self.Descricao.SetLabel((" "*( ( 52 - len(localiza.strip()) ) / 2 ))+localiza)
		
		self.quant = Decimal('1.000')
#-------------------[ Fechamento do ECF]
					
	def fechar(self,event):

		_reTorno = self.erroStatus.statusDaruma(12,False)
		if _reTorno == False:

			semValor = wx.MessageDialog(self,"Documento fiscal em aberto...\n"+(" "*130),"Emitindo do Cupom",wx.OK)
			if semValor.ShowModal() ==  wx.OK:	pass
			semValor.Destroy()
			self.consultar.SetFocus()		
			return

		self.parente.Destroy()

	def atualizaSaldo(self):
		
		Tapagar = self.fEcfs.saldoApagar()
		TsubToT = self.fEcfs.subTotal()

		self.TotalGeral = Decimal( ('%.3f' % Decimal(TsubToT[:10]+"."+TsubToT[10:])) )
		self.TotalSubTo = Decimal( ('%.3f' % Decimal(Tapagar[:10]+"."+Tapagar[10:])) )				
		TotalGeralf     = ('%.2f' % self.TotalGeral).replace('.',',')
		self.TotaGeral.SetLabel((" "*( 21 - len(TotalGeralf) ))+TotalGeralf)	
		
	def OnPaint(self, event):

		dc = wx.PaintDC(self)
		dc.GradientFillLinear((0, 0, wx.DisplaySize()[0],wx.DisplaySize()[1]),  '#ECE5E5', '#000000', wx.SOUTH)
		dc.GradientFillLinear((25, 0, wx.DisplaySize()[0]-(1024-1000), 50),  self.cor , 'black', wx.EAST)
		dc.GradientFillLinear((0, 0, 23, 50),     self.cor , 'black', wx.SOUTH)
		dc.GradientFillLinear((0, wx.DisplaySize()[1]-(768-700), wx.DisplaySize()[0], 68), self.cor , 'black', wx.EAST)
		dc.SetTextForeground("#FFFFFF")
		dc.SetFont(wx.Font(15, wx.SWISS,  wx.NORMAL, wx.BOLD))
		dc.DrawText("Fluzão Construção", 40, 5)
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD))		
		dc.DrawText("Lykos PAF-ECF Versão 1.0\nLinux-Windows-MAC", 5, wx.DisplaySize()[1]-(768-725))
		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD))		
		dc.DrawText("F9-Funções Gerais\nF5-Menu Fiscal", wx.DisplaySize()[0]-(1024-880), wx.DisplaySize()[1]-(768-725))
		dc.SetTextForeground("#FFFFFF") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD))		
		dc.DrawRotatedText("Littus Sistemas Integrados", 5, wx.DisplaySize()[1]-(768-695), 90)

	def truncarFormatar(self,_valor):
		
		_Formatando = format(_valor,'.3f') #-->Recebe Decimal e Formata
		TruncadoVlr = Decimal( _Formatando[:( len(_Formatando) - 1)] ) #-->Trunca 
		TruncadoVlr = ('%.2f' % TruncadoVlr).replace('.',',') #->Formata com 2 com <,>

		return TruncadoVlr

	def truncar(self,_valor):
		
		_Formatando = format(_valor,'.3f') #-->Recebe Decimal e Formata
		TruncadoVlr = Decimal( _Formatando[:( len(_Formatando) - 1)] ) #-->Trunca 

		return TruncadoVlr

	def pagamentos(self,event):

		if self.TotalGeral >  0:

			valorApagar = self.TotalGeral
			if self.TotalSubTo > 0:	valorApagar = self.TotalSubTo
			
			formaPagamentos.ValorCompra = self.TotalGeral
			formaPagamentos.SubTotal    = valorApagar
			formaPagamentos.libPrinter  = self.ecfLib

			paga_frame=formaPagamentos(parent=self.parente,id=-1)
			paga_frame.Center()
			paga_frame.Show()	
				
			self.consultar.SetFocus()		
		else:

			semValor = wx.MessageDialog(self,"Nenhum valor registrado para recebimento...\n"+(" "*130),"Abertura do Cupom",wx.OK)
			if semValor.ShowModal() ==  wx.OK:	pass
			semValor.Destroy()

			self.consultar.SetFocus()		
			return

	def consultarProd(self,event):

		PainelPrincipal.acessCons=ProdConsulta(parent=self.parente,id=-1)
		PainelPrincipal.acessCons.Center()
		PainelPrincipal.acessCons.Show()					

		self.consultar.SetFocus()
				
	def cancelar(self,event):	

		if self.TotalGeral >  0:

			canc_frame=cancelamentos(parent=self.parente,id=-1)
			canc_frame.Center()
			canc_frame.Show()					
			self.consultar.SetFocus()
		else:

			semValor = wx.MessageDialog(self,"Nenhum valor registrado para cancelamento...\n"+(" "*130),"Abertura do Cupom",wx.OK)
			if semValor.ShowModal() ==  wx.OK:	pass
			semValor.Destroy()

			self.consultar.SetFocus()		
			return


class funcoesGerais(wx.Frame):

	acessCons  = ''
	ValorPagar = ''
	SangSuprim = ''
	
	def __init__(self,parent,id):

		corPainel   = PainelPrincipal.cor		
		self.ecfs   = ecfPrincipal.ecfs		
		self.mkn    = wx.lib.masked.NumCtrl
		self.ecfLib = PainelPrincipal.libEcfs
		self.fEcfs	= funcoesEcfs(parent,self.ecfLib)
		self._coo   = self.fEcfs.rInformacoes("26",6)
		self.docT   = self.fEcfs.TipoDocumento().strip().upper()

		wx.Frame.__init__(self, parent, id, 'Cancelamento de Cupom', size=(640,430), style=wx.NO_BORDER|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)
		self.painel.SetBackgroundColour(corPainel)
		self.painel.Bind(wx.EVT_KEY_UP, self.Teclas)

		self.pa1 = wx.StaticBox(self.painel, -1, 'Valor da Sangria', pos=(0,0), size=(360,50),  style=wx.SUNKEN_BORDER)
		self.pa1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD));	self.pa1.SetForegroundColour('#FFFFFF')
		
		self.pa2 = wx.StaticBox(self.painel, -1, 'Sangria', pos=(0,60), size=(360,245),  style=wx.SUNKEN_BORDER)
		self.pa2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD));	self.pa2.SetForegroundColour('#FFFFFF')

		self.ulTimoC = wx.StaticText(self.painel,-1,"Ultimo COO: "+self._coo+" Impresso: "+self.docT, pos=(380,240))
		self.ulTimoC.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD));	self.ulTimoC.SetForegroundColour('#7F7F7F')

		assDocu = wx.StaticBox(self.painel, -1, 'Documento CPF-CNPJ', pos=(2,305), size=(143,33),  style=wx.SUNKEN_BORDER)
		assDocu.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD));	assDocu.SetForegroundColour('#FFFFFF')
		self.DocuAss = wx.TextCtrl(self.painel,-1,'',pos=(5,317),size=(135,18),style = wx.NO_BORDER)
		self.DocuAss.SetMaxLength(18) #--> [ Limita o numero de caracter ]

		assNome = wx.StaticBox(self.painel, -1, 'Nome do Cliente', pos=(2,345), size=(367,33),  style=wx.SUNKEN_BORDER)
		assNome.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD));	assNome.SetForegroundColour('#FFFFFF')
		self.NomeAss = wx.TextCtrl(self.painel,-1,'',pos=(5,355),size=(360,18),style = wx.NO_BORDER)
		self.NomeAss.SetMaxLength(45) #--> [ Limita o numero de caracter ]

		assEnde = wx.StaticBox(self.painel, -1, 'Endereço', pos=(2,385), size=(367,33),  style=wx.SUNKEN_BORDER)
		assEnde.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD));	assEnde.SetForegroundColour('#FFFFFF')
		self.EndeAss = wx.TextCtrl(self.painel,-1,'',pos=(5,397),size=(360,18),style = wx.NO_BORDER)
		self.EndeAss.SetMaxLength(45) #--> [ Limita o numero de caracter ]

		self.vSangria = self.mkn(self.painel, id = -1, value = "0.00", pos=(130,10),style = wx.NO_BORDER|wx.ALIGN_RIGHT, integerWidth = 7, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#FFFFFF", signedForegroundColour = "Red", emptyBackgroundColour = corPainel, validBackgroundColour = corPainel, invalidBackgroundColour = "Yellow")
		self.vSangria.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL,wx.BOLD))	
		self.vSangria.SetBackgroundColour(corPainel)
		self.vSangria.SetForegroundColour('#FFFFFF')

		self.Entrar= wx.Button(self.painel,-1,"{F11}\nEnter",(275,190),(80,110))
		self.Entrar.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))		
			
		sangria = GenBitmapTextButton(self.painel, 500, wx.Bitmap('imagens/executar.png'), "{F1}-Sangria"+(" "*9), (380, 5), (250, 50),style=wx.ALIGN_RIGHT)
		sangria.SetForegroundColour('#E6E6FA');	sangria.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))
		sangria.SetBezelWidth(5);	sangria.SetBackgroundColour(corPainel)		

		suprime = GenBitmapTextButton(self.painel, 501, wx.Bitmap('imagens/executar.png'), "{F2}-Suprimentos"+(" "*5), (380, 70), (250, 50),style=wx.ALIGN_RIGHT)
		suprime.SetForegroundColour('#E6E6FA');	suprime.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))
		suprime.SetBezelWidth(5);	suprime.SetBackgroundColour(corPainel)		

		leiturx = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/executar.png'), "{F3}-Leitura X"+(" "*7), (380, 130), (250, 50),style=wx.BU_LEFT)
		leiturx.SetForegroundColour('#E6E6FA');	leiturx.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))
		leiturx.SetBezelWidth(5);	leiturx.SetBackgroundColour(corPainel)		

		leiturz = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/executar.png'), "{F4}-Leitura Z"+(" "*7), (380, 190), (250, 50),style=wx.BU_LEFT)
		leiturz.SetForegroundColour('#E6E6FA');	leiturz.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))
		leiturz.SetBezelWidth(5);	leiturz.SetBackgroundColour(corPainel)		

		cacupom = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/executar.png'), "{F5}-Cancelar Cupom"+(" "*2), (380, 255), (250, 50),style=wx.BU_LEFT)
		cacupom.SetForegroundColour('#E6E6FA');	cacupom.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))
		cacupom.SetBezelWidth(5);	cacupom.SetBackgroundColour(corPainel)		

		associa = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/executar.png'), "{F6}-Associar Cliente", (380, 315), (250, 50),style=wx.BU_LEFT)
		associa.SetForegroundColour('#E6E6FA');	associa.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))
		associa.SetBezelWidth(5);	associa.SetBackgroundColour(corPainel)		

		opvolta = GenBitmapTextButton(self.painel, -1, wx.Bitmap('imagens/voltar.png'), "{F12}-Voltar",pos=(380,370), size=(250,50),style=wx.BU_LEFT)
		opvolta.SetForegroundColour('#E6E6FA');	opvolta.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))
		opvolta.SetBezelWidth(5);	opvolta.SetBackgroundColour(corPainel)		

		TDocu = GenBitmapTextButton(self.painel, 400, wx.Bitmap('imagens/teclado.png'), "CpfCnpj",pos=(150,315),size=(70,20),style=wx.BU_LEFT)
		TDocu.SetForegroundColour('#E6E6FA');	TDocu.SetFont(wx.Font(5,wx.MODERN,wx.NORMAL, wx.BOLD))
		TDocu.SetBezelWidth(1);	TDocu.SetBackgroundColour(corPainel)		

		TNome = GenBitmapTextButton(self.painel, 401, wx.Bitmap('imagens/teclado.png'), "Nome",pos=(230,315),size=(65,20),style=wx.BU_LEFT)
		TNome.SetForegroundColour('#E6E6FA');	TNome.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL, wx.BOLD))
		TNome.SetBezelWidth(1);	TNome.SetBackgroundColour(corPainel)		

		TEnde = GenBitmapTextButton(self.painel, 402, wx.Bitmap('imagens/teclado.png'), "Endereço",pos=(300,315),size=(70,20),style=wx.BU_LEFT)
		TEnde.SetForegroundColour('#E6E6FA');	TEnde.SetFont(wx.Font(4,wx.MODERN,wx.NORMAL, wx.BOLD))
		TEnde.SetBezelWidth(1);	TEnde.SetBackgroundColour(corPainel)		

		self.b7 = wx.Button(self.painel,200,"7",(5,70),(80,50))
		self.b7.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		self.b8 = wx.Button(self.painel,201,"8",(95,70),(80,50))
		self.b8.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		self.b9 = wx.Button(self.painel,202,"9",(185,70),(80,50))
		self.b9.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		self.b4 = wx.Button(self.painel,203,"4",(5,130),(80,50))
		self.b4.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		self.b5 = wx.Button(self.painel,204,"5",(95,130),(80,50))
		self.b5.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD))		

		self.b6 = wx.Button(self.painel,205,"6",(185,130),(80,50))
		self.b6.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		
		
		self.b1 = wx.Button(self.painel,206,"1",(5,190),(80,50))
		self.b1.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		self.b2 = wx.Button(self.painel,207,"2",(95,190),(80,50))
		self.b2.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		self.b3 = wx.Button(self.painel,208,"3",(185,190),(80,50))
		self.b3.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		
		
		self.b0 = wx.Button(self.painel,209,"0",(5,250),(170,50))
		self.b0.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		self.bp = wx.Button(self.painel,210,".",(275,130),(80,50))
		self.bp.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		self.ba = wx.Button(self.painel,300,"Apagar",(185,250),(80,50))
		self.ba.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))		

		self.bl = wx.Button(self.painel,301,"{F9}\nLimpar",(275,70),(80,50))
		self.bl.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD))		
		
		opvolta.Bind(wx.EVT_BUTTON,self.voltar)
		associa.Bind(wx.EVT_BUTTON,self.associar)

		TDocu.Bind(wx.EVT_BUTTON,self.acTeclado)
		TNome.Bind(wx.EVT_BUTTON,self.acTeclado)
		TEnde.Bind(wx.EVT_BUTTON,self.acTeclado)
		sangria.Bind(wx.EVT_BUTTON,self.acSangria)
		suprime.Bind(wx.EVT_BUTTON,self.acSangria)
		leiturx.Bind(wx.EVT_BUTTON,self.Sangleiturx)
		leiturz.Bind(wx.EVT_BUTTON,self.acLeituraz)
		cacupom.Bind(wx.EVT_BUTTON,self.ultimoCupom)
		
		self.Entrar.Bind(wx.EVT_BUTTON,self.EntraSangria)	
		self.b0.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.b1.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.b2.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.b3.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.b4.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.b5.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.b6.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.b7.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.b8.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.b9.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.bp.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		self.bl.Bind(wx.EVT_BUTTON,self.limpar)
				
		self.setarOpcoes(1,1)
		self.vSangria.Disable()
		self.DocuAss.SetFocus()

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
		if idNumero == 210:	_Numero = "." 

		self.ValorPagar +=_Numero
		try:

			if len(self.ValorPagar) == 1 and  self.ValorPagar == ".":	self.ValorPagar = "0."

			NovoValor1 = format(Decimal(self.ValorPagar),'.5f')
			NovoValor2 = NovoValor1[:( len(NovoValor1) - 3 )]
			self.vSangria.SetValue(NovoValor2)
				
		except Exception, _reTornos:
			
			self.vSangria.SetValue('0.00')
			self.ValorPagar = ''


	def limpar(self,event):

		self.vSangria.SetValue('0.00')
		self.ValorPagar = ''
		self.vSangria.SetFocus()

	def EntraSangria(self,event):
	
		if Decimal( self.vSangria.GetValue() ) > 0:

			NovoValor1 = format(Decimal( self.vSangria.GetValue()),'.5f').replace(".",",")

			if self.fEcfs.saicaCaixa(self.SangSuprim,NovoValor1[:( len(NovoValor1) - 3 )]) ==  0:

				SangriaInvalido = wx.MessageDialog(self,"Erro de comunicação, não foi possível enviar o método\nSangria: "+NovoValor1[:( len(NovoValor1) - 3 )].replace('.',',')+(" "*120),"Sangria Caixa",wx.OK)
				if SangriaInvalido.ShowModal() ==  wx.ID_OK:	pass
				SangriaInvalido.Destroy()

				SangriaInvalido.Destroy()				
				self.vSangria.SetFocus()

			else:
				self.setarOpcoes(1,1)
				self.vSangria.Disable()
				self.limpar(self)
				self.DocuAss.SetFocus()

	def Sangleiturx(self,event):
		self.ecfLib.iLeituraX_ECF_Daruma()

	def ultimoCupom(self,event):
		
		self._coo = self.fEcfs.rInformacoes("26",6)
		self.docT = self.fEcfs.TipoDocumento().strip().upper()

		self.ulTimoC.SetLabel("Ultimo COO: "+self._coo+" Impresso: "+self.docT)

		if len(self._coo.strip()) !=0 and int(self._coo) == 0:
			
			cancelarCupom = wx.MessageDialog(self,"Sem cupom fiscal para ser cancelado\n"+(" "*120),"Sangria Caixa",wx.OK)
			if cancelarCupom.ShowModal() ==  wx.ID_OK:	pass
			cancelarCupom.Destroy()

		elif len(self._coo.strip()) !=0 and int(self._coo) != 0:
			
			confirmaCupom = wx.MessageDialog(self,"{"+self._coo+"} Confirme para cancelar!!\n"+(" "*120),"Cancelamento do cupom",wx.YES_NO|wx.NO_DEFAULT)
			if confirmaCupom.ShowModal() ==  wx.ID_YES and self.fEcfs.cancelaCupom() == 1:
				self.ecfs.limpaVendas()
				self.ecfs.caixalivre()
				
			confirmaCupom.Destroy()

	def acLeituraz(self,event):	self.fEcfs.reducaoz()

	def acSangria(self,event):

		idSanSup = event.GetId()
		if idSanSup == 500: #[Sangria]

			self.SangSuprim = 1
			self.pa1.SetLabel("Valor da Sangria")
			self.pa2.SetLabel("Sangria")

		if idSanSup == 501: #[Suprimento]

			self.SangSuprim = 2 
			self.pa1.SetLabel("Valor do Suprimentos")
			self.pa2.SetLabel("Suprimentos")
		
		self.setarOpcoes(1,2)
		self.vSangria.Enable()
		self.vSangria.SetFocus()
		
	def acTeclado(self,event):
		
		idControle = event.GetId()
		
		if idControle == 400:
			Teclado.moduloaces = '2'
			Teclado.saidadados = self.DocuAss.GetValue()			
			
		if idControle == 401:
			Teclado.moduloaces = '3'
			Teclado.saidadados = self.NomeAss.GetValue()			

		if idControle == 402:
			Teclado.moduloaces = '4'
			Teclado.saidadados = self.EndeAss.GetValue()			

		tecl_frame=Teclado(parent=self,id=-1)
		tecl_frame.Center()
		tecl_frame.Show()					

	def aTualizaCliente(self,dados,opcao):

		if opcao == '2':	self.DocuAss.SetValue(dados)		
		if opcao == '3':	self.NomeAss.SetValue(dados)
		if opcao == '4':	self.EndeAss.SetValue(dados)
			
	def voltar(self,event):
		
		__documento = self.DocuAss.GetValue()
		__nomeClien = self.NomeAss.GetValue()
		__endeClien = self.EndeAss.GetValue()
		self.ecfs.atualizaAssocia(__documento,__nomeClien,__endeClien)
		self.Destroy()		
		
	def associar(self,event):	self.DocuAss.SetFocus()
		
	def setarOpcoes(self,opcao,_op):

		if opcao == 1 and _op == 1:
			self.b7.Disable();	self.b8.Disable();	self.b9.Disable()
			self.b4.Disable();	self.b5.Disable();	self.b6.Disable()
			self.b1.Disable();	self.b2.Disable();	self.b3.Disable()
			self.b0.Disable();	self.bp.Disable();	self.ba.Disable()
			self.bl.Disable();	self.Entrar.Disable()

		elif opcao ==1 and _op == 2:
			self.b7.Enable();	self.b8.Enable();	self.b9.Enable()
			self.b4.Enable();	self.b5.Enable();	self.b6.Enable()
			self.b1.Enable();	self.b2.Enable();	self.b3.Enable()
			self.b0.Enable();	self.bp.Enable()
			self.bl.Enable();	self.Entrar.Enable()


		elif opcao == 2 and _op == 1:
			self.DocuAss.Disable(); self.NomeAss.Disable();	self.EndeAss.Disable()

		elif opcao == 2 and _op == 2:
			self.DocuAss.Enable(); self.NomeAss.Enable();	self.EndeAss.Enable()

	def Teclas(self,event):
		
		keycode=event.GetKeyCode()

		if keycode == wx.WXK_F1:
			self.SangSuprim = 1
			self.pa1.SetLabel("Valor da Sangria")
			self.pa2.SetLabel("Sangria")

			self.acSangria(self) #->Sangria
			
		if keycode == wx.WXK_F2: #---------------------------->Suprimentos
			self.SangSuprim = 2
			self.pa1.SetLabel("Valor do Suprimentos")
			self.pa2.SetLabel("Suprimentos")

			self.acSangria(self) #->Sangria
			
		if keycode == wx.WXK_F3:	self.Sangleiturx(self) #-->Leitura X
		if keycode == wx.WXK_F4:	self.acLeituraz(self) #--->Leitura Z
		if keycode == wx.WXK_F5:	self.ultimoCupom(self) #-->Cancelar Ultimo Cupom
		if keycode == wx.WXK_F6:	self.associar(self) #----->Associar Clientes
		if keycode == wx.WXK_F9:	self.limpar(self) #------->Limpar Sangria
		if keycode == wx.WXK_F11:	self.EntraSangria(self) #->Improimir Sangria
		
		if keycode == wx.WXK_F12:	self.voltar(self)
			
		event.Skip()		
	
class TecladoBotoes(wx.Frame):

	NumerosTeclados = ''
	Receptor        = ''
	def __init__(self,parent,id):

		corPainel    = PainelPrincipal.cor		
		self.ecfs    = ecfPrincipal.ecfs		

		itemQuantidade = (" "*11)+"Quantidade"
		if self.Receptor == 102:	itemQuantidade = (" "*4)+"Código,Codigo de Barras"

		wx.Frame.__init__(self, parent, id, 'Cancelamento de Cupom', size=(265,420), style=wx.NO_BORDER|wx.FRAME_FLOAT_ON_PARENT)
		painel = wx.Panel(self)
		painel.SetBackgroundColour(corPainel)

		b7 = wx.Button(painel,200,"7",(0,50),(80,50))
		b7.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b8 = wx.Button(painel,201,"8",(90,50),(80,50))
		b8.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b9 = wx.Button(painel,202,"9",(180,50),(80,50))
		b9.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b4 = wx.Button(painel,203,"4",(0,110),(80,50))
		b4.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b5 = wx.Button(painel,204,"5",(90,110),(80,50))
		b5.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b6 = wx.Button(painel,205,"6",(180,110),(80,50))
		b6.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b1 = wx.Button(painel,206,"1",(0,170),(80,50))
		b1.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b2 = wx.Button(painel,207,"2",(90,170),(80,50))
		b2.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b3 = wx.Button(painel,208,"3",(180,170),(80,50))
		b3.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b0 = wx.Button(painel,209,"0",(0,230),(170,50))
		b0.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		bp = wx.Button(painel,210,".",(180,230),(80,50))
		bp.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		
		if self.Receptor == 102:	bp.Disable()

		opcao = wx.StaticText(painel,-1,itemQuantidade,pos=(2,340))
		opcao.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD));	opcao.SetForegroundColour('#7F7F7F')
		
		self.EntraNumero = wx.TextCtrl(painel, -1, "" , pos=(2,2),size=(255, 40),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB|wx.NO_BORDER)
		self.EntraNumero.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))


		apaga = GenBitmapTextButton(painel, 300, wx.Bitmap('imagens/voltarcan.png'), "Apagar", (2, 290), (165, 50),style=wx.BU_LEFT)
		apaga.SetForegroundColour('#E6E6FA');	apaga.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD))
		apaga.SetBezelWidth(5);	apaga.SetBackgroundColour(corPainel)		

		limpa = GenBitmapTextButton(painel, 301, wx.Bitmap('imagens/eraser.png'), "Limpar", (180, 290), (80, 50),style=wx.BU_LEFT)
		limpa.SetForegroundColour('#E6E6FA');	limpa.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL, wx.BOLD))
		limpa.SetBezelWidth(5);	limpa.SetBackgroundColour(corPainel)		

		entra = GenBitmapTextButton(painel, 1, wx.Bitmap('imagens/return.png'), "Entrar", (2, 360), (255, 50),style=wx.BU_LEFT)
		entra.SetForegroundColour('#E6E6FA');	entra.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))
		entra.SetBezelWidth(5);	entra.SetBackgroundColour(corPainel)		
		
		entra.Bind(wx.EVT_BUTTON,self.SairEntrar)

		b1.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b2.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b3.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b4.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b5.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b6.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b7.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b8.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b9.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b0.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		bp.Bind(wx.EVT_BUTTON,self.TeclarNumeros)

		limpa.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		apaga.Bind(wx.EVT_BUTTON,self.TeclarNumeros)

		
	def SairEntrar(self,event):
		
		TexToNumero = self.EntraNumero.GetValue()
		if len(TexToNumero) and self.Receptor == 101:
			self.ecfs.Interceptar("X"+TexToNumero)

		elif len(TexToNumero) and self.Receptor == 102:
			self.ecfs.Interceptar(TexToNumero)
			
		self.Destroy()

	def TeclarNumeros(self,event):
	
		iDentifica = event.GetId()

		try:
	
			if iDentifica == 200:	self.NumerosTeclados +="7"
			if iDentifica == 201:	self.NumerosTeclados +="8"
			if iDentifica == 202:	self.NumerosTeclados +="9"
			
			if iDentifica == 203:	self.NumerosTeclados +="4"
			if iDentifica == 204:	self.NumerosTeclados +="5"
			if iDentifica == 205:	self.NumerosTeclados +="6"

			if iDentifica == 206:	self.NumerosTeclados +="1"
			if iDentifica == 207:	self.NumerosTeclados +="2"
			if iDentifica == 208:	self.NumerosTeclados +="3"

			if iDentifica == 209:	self.NumerosTeclados +="0"
			if iDentifica == 210:	self.NumerosTeclados +="."

			if iDentifica == 300:	self.NumerosTeclados = self.NumerosTeclados[:( len(self.NumerosTeclados) - 1)]
			if iDentifica == 301:	self.NumerosTeclados = ''
			erroProvoca = Decimal(self.NumerosTeclados)
			self.EntraNumero.SetValue(self.NumerosTeclados)

		except Exception, _reTornos:
			self.NumerosTeclados = ''
			self.EntraNumero.SetValue(self.NumerosTeclados)
		
		
class cancelamentos(wx.Frame):
	
	def __init__(self,parent,id):

		corPainel   = PainelPrincipal.cor		
		self.ecfs   = ecfPrincipal.ecfs		
		self.ecfLib = PainelPrincipal.libEcfs
		self.fEcfs 	= funcoesEcfs(parent,self.ecfLib)		

		self._ite = self.fEcfs.rInformacoes("58",3)
		self._coo = self.fEcfs.rInformacoes("26",6)

		nItems = []
		vItems = 1
		for i in range(int(self._ite)):

			nItems.append(""+str(vItems).zfill(3)+"")
			vItems +=1

		wx.Frame.__init__(self, parent, id, 'Cancelamento de Cupom', size=(165,230), style=wx.NO_BORDER|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)
		self.painel.SetBackgroundColour(corPainel)
		self.painel.Bind(wx.EVT_KEY_UP, self.Teclas)

		TiTems = wx.StaticBox(self.painel, -1, 'Selecionar ITEM', pos=(5,150), size=(150,65),  style=wx.SUNKEN_BORDER)
		TiTems.SetForegroundColour('#FFFFFF');	TiTems.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))

		self.bItems = GenBitmapTextButton(self.painel, 1, wx.Bitmap('imagens/itemcan.png'), "{F1}-Cancelar\n Item: "+self._ite, (0, 0), (160, 80),style=wx.BU_LEFT)
		self.bSairr = GenBitmapTextButton(self.painel, 1, wx.Bitmap('imagens/voltar.png'), "{F12}-Voltar", (0, 90), (160, 50),style=wx.BU_LEFT)
		self.IteCan = wx.ComboBox(self.painel, -1, self._ite, pos=(10,165), size=(140,45), choices = nItems,style=wx.NO_BORDER|wx.CB_READONLY)
		
		self.bItems.SetForegroundColour('#E6E6FA');	self.bItems.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bItems.SetBezelWidth(5);	self.bItems.SetBackgroundColour(corPainel)		

		self.bSairr.SetForegroundColour('#FFFFFF');	self.bSairr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bSairr.SetBezelWidth(5);	self.bSairr.SetBackgroundColour("#5A5A2D")		
    
		self.IteCan.Bind(wx.EVT_COMBOBOX,self.aTualizaCan)

		self.bItems.Bind(wx.EVT_BUTTON,self.cancelaItem)
		self.bSairr.Bind(wx.EVT_BUTTON,self.fechar)
		self.IteCan.SetFocus()

	def aTualizaCan(self,event):

		ItemCancelar = self.IteCan.GetValue()
		if ItemCancelar.isdigit()==True and len(ItemCancelar) >= 1 and len(ItemCancelar) <=3:
			self.bItems.SetLabel("{F1}-Cancelar\n Item: "+ItemCancelar)
			self.Refresh()
		
	def Teclas(self,event):
		
		keycode=event.GetKeyCode()
		if keycode == wx.WXK_F1:	self.cancelaItem(self)
		if keycode == wx.WXK_F2:	self.cancelaCupom(self)
		if keycode == wx.WXK_F12:	self.fechar(self)
			
		event.Skip()		
	def cancelaItem(self,event):

		if( self.fEcfs.ecfinforme() == True ):

			ItemCancelar = self.IteCan.GetValue()
			if ItemCancelar.isdigit()==True and len(ItemCancelar) >=1 and len(ItemCancelar) <=3 and int(ItemCancelar) !=0 and int(ItemCancelar) <= int(self._ite):

				self.fEcfs.cancelaItem(str(ItemCancelar))

				rItemCan = self.fEcfs.estendido(1,3)
				rValoCan = self.fEcfs.estendido(2,11)
								
				if len(rItemCan.strip()) !=1:
					self.ecfs.cancelarItem(rItemCan,rValoCan)
					self.Destroy()
									
			self.IteCan.SetFocus()
		
	def fechar(self,event):	self.Destroy()
	
	
class ProdConsulta(wx.Frame):
	
	codigoConsulta = ''
	consultaTeclado= ''

	def __init__(self,parent,id):

		corPainel    = PainelPrincipal.cor		
		self.bancos  = ecfPrincipal._basedd
		self.cursor  = ecfPrincipal._cursor
		self.ecfs    = ecfPrincipal.ecfs		
		self.ecfLib  = PainelPrincipal.libEcfs
		self.fEcfs   = funcoesEcfs(parent,self.ecfLib)

		wx.Frame.__init__(self, parent, id, 'Fechamento do Cupom', size=(1000,520), style=wx.NO_BORDER|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)
		self.painel.SetBackgroundColour(corPainel)

		self.painel.Bind(wx.EVT_KEY_UP, self.Teclas)

		wx.StaticBox(self.painel, -1, '', pos=(5,2),  size=(985, 33),style=wx.SUNKEN_BORDER|wx.ALIGN_RIGHT)

		self.informa = wx.StaticText(self.painel,wx.ID_ANY, label='Consultar Produtos',pos=(380,10))		
		self.informa.SetForegroundColour('#FFFFFF');	self.informa.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.ListaPro = wx.ListCtrl(self.painel, pos=(0, 40), size=(995, 360), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
		self.ListaPro.SetForegroundColour('#000000');	self.ListaPro.SetFont(wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD))
	
		self.ListaPro.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)

		self.ListaPro.InsertColumn(0, 'Ordem',  format=wx.LIST_ALIGN_LEFT,width=60)
		self.ListaPro.InsertColumn(1, 'Barras', format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaPro.InsertColumn(2, 'Descricao dos Produtos', width=540)
		self.ListaPro.InsertColumn(3, 'Estoque', format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaPro.InsertColumn(4, 'UN', format=wx.LIST_ALIGN_TOP,width=30)
		self.ListaPro.InsertColumn(5, 'Preço',   format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaPro.InsertColumn(6, 'Codigo', format=wx.LIST_ALIGN_LEFT,width=150)

		self.bLista = GenBitmapTextButton(self.painel, 300, wx.Bitmap('imagens/lista.png'), "{F1}-Lista", (0,400),(160,60),style=wx.BU_LEFT)
		self.bLista.SetForegroundColour('#E6E6FA');	self.bLista.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bLista.SetBezelWidth(5);	self.bLista.SetBackgroundColour(corPainel)		

		self.bConsu = GenBitmapTextButton(self.painel, 301, wx.Bitmap('imagens/procurar.png'), "{F2}-Procurar", (180,400),(160,60),style=wx.BU_LEFT)
		self.bConsu.SetForegroundColour('#E6E6FA');	self.bConsu.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bConsu.SetBezelWidth(5);	self.bConsu.SetBackgroundColour(corPainel)		

		self.bLanca = GenBitmapTextButton(self.painel, 1, wx.Bitmap('imagens/comprar.png'), "{F3}-Comprar", (360,400),(160,60),style=wx.BU_LEFT)
		self.bLanca.SetForegroundColour('#E6E6FA');	self.bLanca.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bLanca.SetBezelWidth(5);	self.bLanca.SetBackgroundColour(corPainel)		

		self.bBaixo = GenBitmapTextButton(self.painel, 200, wx.Bitmap('imagens/pbaixo.png'), "{F4}-Para Baixo", (540,400),(160,60),style=wx.BU_LEFT)
		self.bBaixo.SetForegroundColour('#E6E6FA');	self.bBaixo.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bBaixo.SetBezelWidth(5);	self.bBaixo.SetBackgroundColour(corPainel)		

		self.bCimas = GenBitmapTextButton(self.painel, 201, wx.Bitmap('imagens/pcima.png'), "{F5}-Para Cima", (720,400),(160,60),style=wx.BU_LEFT)
		self.bCimas.SetForegroundColour('#E6E6FA');	self.bCimas.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.bCimas.SetBezelWidth(5);	self.bCimas.SetBackgroundColour(corPainel)		

		self.sairCons = GenBitmapTextButton(self.painel, 201, wx.Bitmap('imagens/voltar.png'), "{F12}\n\nVoltar", (895,400),(100,110),style=wx.BU_LEFT)
		self.sairCons.SetForegroundColour('#FFFFFF');	self.sairCons.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.sairCons.SetBezelWidth(5);	self.sairCons.SetBackgroundColour("#78783E")		

		self.Teclado = GenBitmapTextButton(self.painel, 201, wx.Bitmap('imagens/teclado.png'), "  Teclado", (720,470),(160,40),style=wx.BU_LEFT)
		self.Teclado.SetForegroundColour('#FFFFFF');	self.Teclado.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.Teclado.SetBezelWidth(5);	self.Teclado.SetBackgroundColour("#4B4B19")		

		BoxProcurar = wx.StaticBox(self.painel, -1, 'Procurar', pos=(5,465),  size=(690, 45),style=wx.SUNKEN_BORDER)
		BoxProcurar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD));	BoxProcurar.SetForegroundColour('#FFFFFF')

		self.Procurar = wx.TextCtrl(self.painel, -1, "", pos=(10,477),size=(680, 28),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB|wx.NO_BORDER)
		self.Procurar.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))
		
		self.Procurar.Bind(wx.EVT_TEXT_ENTER, self.pesquisar)
		self.Procurar.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
	
		self.bLista.Bind(wx.EVT_BUTTON,self.listaProcura)
		self.bConsu.Bind(wx.EVT_BUTTON,self.listaProcura)

		self.bLanca.Bind(wx.EVT_BUTTON,self.LancaCarro)
		self.bBaixo.Bind(wx.EVT_BUTTON,self.pBaixo)
		self.bCimas.Bind(wx.EVT_BUTTON,self.pBaixo)		

		self.Teclado.Bind(wx.EVT_BUTTON,self.Teclados)		
		self.sairCons.Bind(wx.EVT_BUTTON,self.fechar)
		
		self.Procurar.SetFocus()
		
	def Teclados(self,event):

		Teclado.moduloaces = '1'
		tecl_frame=Teclado(parent=self,id=-1)
		tecl_frame.Center()
		tecl_frame.Show()					

	def AtualizaCons(self,ProdutoProcurar,_opcao):
		if _opcao == 1:	self.Procurar.SetValue(ProdutoProcurar)
		if _opcao == 2:	self.pesquisar(wx.EVT_BUTTON)
			
	def Teclas(self,event):
		
		keycode=event.GetKeyCode()

		if keycode == wx.WXK_F1:	self.ListaPro.SetFocus()
		if keycode == wx.WXK_F2:	self.Procurar.SetFocus()
		if keycode == wx.WXK_F3:	self.LancaCarro(self)
		if keycode == wx.WXK_F4:	self.BaixoCima(200)
		if keycode == wx.WXK_F5:	self.BaixoCima(201)
		if keycode == wx.WXK_F12:	self.fechar(self)
			
		event.Skip()		

	def listaProcura(self,event):

		if event.GetId() == 300:	self.ListaPro.SetFocus()
		if event.GetId() == 301:	self.Procurar.SetFocus()
		
	def pBaixo(self,event):	self.BaixoCima(event.GetId())
	def BaixoCima(self,evento):

		_indice = int(self.ListaPro.GetFocusedItem())

		if evento == 200:	__iTem = ( _indice + 1 )
		if evento == 201:	__iTem = ( _indice - 1 )
		 
		self.ListaPro.SetItemState(_indice, 0, wx.LIST_STATE_SELECTED)
		self.ListaPro.Focus(__iTem)
		self.ListaPro.Select(__iTem)
		wx.CallAfter(self.ListaPro.SetFocus) #-->[Forca o curso voltar a lista]					
				
	def LancaCarro(self,event):

		if( self.fEcfs.ecfinforme() == True ):
			
			_indice = self.ListaPro.GetFocusedItem()
			Codigos = self.ListaPro.GetItem(_indice, 6).GetText() #->[Codigo do Produto]
			CodigoP = self.ListaPro.GetItem(_indice, 1).GetText() #->[Codigo de Barras]
			DescPro = self.ListaPro.GetItem(_indice, 2).GetText()
			PrecPro = self.ListaPro.GetItem(_indice, 5).GetText()
			
			if CodigoP == '' and Codigos !='':	CodigoP = Codigos
			if CodigoP == '':
				
				_descric = DescPro.strip()+u', Codigo de Barras Vazio...'

				self.informa.SetPosition((10,10))		
				self.informa.SetLabel((" "*( ( 80 - len(_descric) ) / 2 ))+_descric)

			elif Decimal(PrecPro) == 0:
				
				_descric = DescPro.strip()+u', Sem Preço de Venda...'

				self.informa.SetPosition((10,10))		
				self.informa.SetLabel((" "*( ( 80 - len(_descric) ) / 2 ))+_descric)
				
			else:	self.ecfs.Interceptar(CodigoP)

		self.ListaPro.SetFocus()
				
	def ListaCons(self,event):

		if event.GetId() == 100:	self.ListaPro.SetFocus()
		if event.GetId() == 101:	self.Procurar.SetFocus()
		
	def fechar(self,event):	self.Destroy()
	
	def passagem(self,event):

		_indice  = self.ListaPro.GetFocusedItem()
		pProduto = self.ListaPro.GetItem(_indice, 2).GetText()
		pPrecosp = self.ListaPro.GetItem(_indice, 5).GetText().replace('.',',')
		_descric = pProduto.strip()+u'  Preço: '+pPrecosp.strip()

		self.informa.SetPosition((10,10))		
		self.informa.SetLabel((" "*( ( 80 - len(_descric) ) / 2 ))+_descric)
		
	def pesquisar(self,event):
		
		TexToProcurar = self.Procurar.GetValue().upper()

		NovaQT1 = TexToProcurar[:1]         #-->[Retorna o primeiro caracter]
		NovaQT2 = TexToProcurar[1:2]        #-->[Retorna o segundo  caracter]
		NovaQT3 = TexToProcurar[1:].strip() #-->[Retorna todos o caracter apos o primeiro]
		
		if NovaQT1 == "X" and NovaQT2.isdigit() == True:

			self.ecfs.Interceptar(TexToProcurar)
			self.Procurar.Clear()
			return


		if TexToProcurar !='':

			_mensagem = PBI.PyBusyInfo(TexToProcurar+", Aguarde...", title="Buscando Produtos",icon=wx.Bitmap("imagens/aguarde.png"))
			_achamos  = False

			DigiCar   = TexToProcurar[:2]
			__reTorno = 0
			
			if DigiCar.isdigit() == True and len(TexToProcurar)==13:

				barras=TexToProcurar.strip()
				__reTorno = self.cursor.execute("SELECT pd_codi,pd_barr,pd_nome,pd_estf,pd_unid,pd_tpr1 FROM produtos where pd_barr='"+barras+"'")

				if __reTorno == 0:	__reTorno = self.cursor.execute("SELECT pd_codi,pd_barr,pd_nome,pd_estf,pd_unid,pd_tpr1 FROM produtos where pd_codi='"+barras+"'")
				if __reTorno != 0:	_achamos=True

			elif DigiCar.isdigit() == True and len(TexToProcurar)!=13:

				codigo=TexToProcurar.strip()
				__reTorno = self.cursor.execute("SELECT pd_codi,pd_barr,pd_nome,pd_estf,pd_unid,pd_tpr1 FROM produtos where pd_codi='"+codigo+"'")
				if __reTorno !=0:	_achamos=True

			else:

				pesquisa = TexToProcurar[:2]
				if pesquisa == "P:":
				
					TexToProcurar = TexToProcurar[2:]
					__reTorno = self.cursor.execute("SELECT pd_codi,pd_barr,pd_nome,pd_estf,pd_unid,pd_tpr1 FROM produtos where pd_nome like '%"+TexToProcurar+"%' ORDER BY pd_nome")

				else:
					__reTorno = self.cursor.execute("SELECT pd_codi,pd_barr,pd_nome,pd_estf,pd_unid,pd_tpr1 FROM produtos where pd_nome like '"+TexToProcurar+"%' ORDER BY pd_nome")
			
			if DigiCar.isdigit() == False and __reTorno !=0: 

				self.ListaPro.DeleteAllItems()
				_result   = self.cursor.fetchall()
				TextoSize = len(TexToProcurar)
				indice    = 0
				_achamos  = True
				for i in _result:

					self.ListaPro.InsertStringItem(indice,str(indice).zfill(5))	
					self.ListaPro.SetStringItem(indice,1, i[1])	
					self.ListaPro.SetStringItem(indice,2, i[2])	
					self.ListaPro.SetStringItem(indice,3, str(i[3]))	
					self.ListaPro.SetStringItem(indice,4, i[4])	
					self.ListaPro.SetStringItem(indice,5, str(i[5]))	
					self.ListaPro.SetStringItem(indice,6, i[0])	

					if indice % 2:	self.ListaPro.SetItemBackgroundColour(indice, "#F1F7FD")								

					indice +=1

				self.ListaPro.Select(0)
				self.ListaPro.Focus(0)
				wx.CallAfter(self.ListaPro.SetFocus) #-->[Forca o curso voltar a lista]					

			elif DigiCar.isdigit()==True and _achamos==True:

				_result     = self.cursor.fetchall()
				_produto = _result[0][2]
				_precosp = _result[0][5]
				_precosp = ('%.2f' % _precosp).replace('.', ',') 

				_descric = _produto.strip()+u'  Preço: '+_precosp.strip()

				self.informa.SetPosition((10,10))		
				self.informa.SetLabel((" "*( ( 80 - len(_descric) ) / 2 ))+_descric)
				self.Procurar.SetFocus()
						
			del _mensagem
			if _achamos == False:
				cLocalizado = wx.MessageDialog(self,TexToProcurar+u", Não Localizado!!\n"+(" "*130),"Procurar Produtos",wx.OK)
				if cLocalizado.ShowModal() ==  wx.OK:	pass
				cLocalizado.Destroy()
		self.Procurar.Clear()


class formaPagamentos(wx.Frame):

	ValorCompra = Decimal('0.00')
	SubTotal    = Decimal('0.00')
	libPrinter  = ''
	ValorPagar  = ''
	
	def __init__(self, parent, id):

		corPainel   = PainelPrincipal.cor
		self.mkn    = wx.lib.masked.NumCtrl
		self.ecf    = ecfPrincipal.ecfs
		self.ecfLib = PainelPrincipal.libEcfs
		self.fEcfs  = funcoesEcfs(parent,self.ecfLib)
		
		self.totalizaPagamento()

		wx.Frame.__init__(self, parent, id, 'Fechamento do Cupom', size=(775,420), style=wx.NO_BORDER|wx.FRAME_FLOAT_ON_PARENT)
		painel = wx.Panel(self,-1,style=wx.NO_BORDER)
		painel.SetBackgroundColour(corPainel)
		painel.Bind(wx.EVT_KEY_UP, self.Teclas)

		__Botoes = wx.StaticBox(painel, -1, 'Formas de Pagamentos', pos=(5,0),  size=(760, 170),style=wx.SUNKEN_BORDER|wx.ALIGN_CENTER)
		__Botoes.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL,wx.LIGHT));	__Botoes.SetForegroundColour('#FFFFFF')
	
		self.PgTo1 = GenBitmapTextButton(painel, -1, wx.Bitmap('imagens/dinheiro.png'), "{F1}Dinheiro", (10,25),(170,60),style=wx.BU_LEFT)
		self.PgTo1.SetForegroundColour('#E6E6FA');	self.PgTo1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.PgTo1.SetBezelWidth(5);	self.PgTo1.SetBackgroundColour(corPainel)		

		self.PgTo2 = GenBitmapTextButton(painel, -1, wx.Bitmap('imagens/cartao.png'), "{F2}CartãoCredito", (205,25),(170,60),style=wx.BU_LEFT)
		self.PgTo2.SetForegroundColour('#E6E6FA');	self.PgTo2.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.PgTo2.SetBezelWidth(5);	self.PgTo2.SetBackgroundColour(corPainel)		

		Pagamento3 = wx.Button(painel,102,"Cartão Débito",(395,25),(170,60))
		Pagamento4 = wx.Button(painel,103,"T E F",(590,25),(170,60))

		Pagamento5 = wx.Button(painel,100,"Pagamento5",(10,100),(170,60))
		Pagamento6 = wx.Button(painel,101,"Pagamento6",(205,100),(170,60))
		Pagamento7 = wx.Button(painel,102,"Pagamento7",(395,100),(170,60))
		Pagamento8 = wx.Button(painel,103,"Pagamento8",(590,100),(170,60))

		wx.StaticBox(painel, -1, 'Total/Saldo', pos=(270,180),  size=(490, 110),style=wx.SUNKEN_BORDER)
		wx.StaticLine(painel, -1, (270, 240), (490,9))

		GvalorTotal =wx.StaticText(painel, wx.ID_STATIC, 'Total: '+('%.2f' % self.ValorCompra).replace('.',','), pos=(280,200))
		GvalorTotal.SetForegroundColour('#FFFFFF');	GvalorTotal.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.SvalorTotal =wx.StaticText(painel, wx.ID_STATIC, 'Saldo:', pos=(280,250))
		self.SvalorTotal.SetForegroundColour('#FFFFFF');	self.SvalorTotal.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD))

		self._SvalorTotal =wx.StaticText(painel, wx.ID_STATIC, ('%.2f' % self.SubTotal).replace('.',','), pos=(390,250))
		self._SvalorTotal.SetForegroundColour('#FFFFFF');	self._SvalorTotal.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD))

		wx.StaticBox(painel, -1, 'Valor Apagar', pos=(270,300),  size=(490, 45),style=wx.SUNKEN_BORDER)
		vaPag = wx.StaticText(painel, wx.ID_STATIC, 'Valor Apagar: ', pos=(280,310))
		vaPag.SetForegroundColour('#FFFFFF');	vaPag.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD))
		
		self.vpg = self.mkn(painel, id = -1, value = str(self.SubTotal) , pos = (550,312),style = wx.NO_BORDER|wx.ALIGN_RIGHT, integerWidth = 7, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = "#FFFFFF", validBackgroundColour = "#FFFFFF", invalidBackgroundColour = "Yellow")
		self.vpg.SetFont(wx.Font(17, wx.MODERN, wx.NORMAL,wx.BOLD))	
			
		self.limpa = GenBitmapTextButton(painel, -1, wx.Bitmap('imagens/eraser.png'), "{F11}-Limpar Apagar", (270,360),(240,50),style=wx.BU_LEFT)
		self.limpa.SetForegroundColour('#FFFFFF');	self.limpa.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.limpa.SetBezelWidth(5);	self.limpa.SetBackgroundColour(corPainel)		

		self.sair = GenBitmapTextButton(painel, -1, wx.Bitmap('imagens/voltar.png'), "{F12}-Voltar", (530,360),(240,50),style=wx.BU_LEFT)
		self.sair.SetForegroundColour('#FFFFFF');	self.sair.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD))
		self.sair.SetBezelWidth(5);	self.sair.SetBackgroundColour(corPainel)		

		b7 = wx.Button(painel,200,"7",(10,180),(80,50))
		b7.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b8 = wx.Button(painel,201,"8",(90,180),(80,50))
		b8.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b9 = wx.Button(painel,202,"9",(170,180),(80,50))
		b9.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b4 = wx.Button(painel,203,"4",(10,240),(80,50))
		b4.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b5 = wx.Button(painel,204,"5",(90,240),(80,50))
		b5.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b6 = wx.Button(painel,205,"6",(170,240),(80,50))
		b6.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b1 = wx.Button(painel,206,"1",(10,300),(80,50))
		b1.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b2 = wx.Button(painel,207,"2",(90,300),(80,50))
		b2.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b3 = wx.Button(painel,208,"3",(170,300),(80,50))
		b3.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b0 = wx.Button(painel,209,"0",(10,360),(160,50))
		b0.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		bp = wx.Button(painel,210,".",(170,360),(80,50))
		bp.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		b1.Bind(wx.EVT_BUTTON,self.TNumerico)
		b2.Bind(wx.EVT_BUTTON,self.TNumerico)
		b3.Bind(wx.EVT_BUTTON,self.TNumerico)
		b4.Bind(wx.EVT_BUTTON,self.TNumerico)
		b5.Bind(wx.EVT_BUTTON,self.TNumerico)
		b6.Bind(wx.EVT_BUTTON,self.TNumerico)
		b7.Bind(wx.EVT_BUTTON,self.TNumerico)
		b8.Bind(wx.EVT_BUTTON,self.TNumerico)
		b9.Bind(wx.EVT_BUTTON,self.TNumerico)
		b0.Bind(wx.EVT_BUTTON,self.TNumerico)
		bp.Bind(wx.EVT_BUTTON,self.TNumerico)
		
		self.PgTo1.Bind(wx.EVT_BUTTON,self.registrar)
		self.limpa.Bind(wx.EVT_BUTTON,self.limpar)
		self.sair.Bind(wx.EVT_BUTTON,self.voltar)
		self.vpg.SetFocus()		

	def TNumerico(self,event):

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
		if idNumero == 210:	_Numero = "." 

		self.ValorPagar +=_Numero
		try:

			if len(self.ValorPagar) == 1 and  self.ValorPagar == ".":	self.ValorPagar = "0."

			NovoValor1 = format(Decimal(self.ValorPagar),'.5f')
			NovoValor2 = NovoValor1[:( len(NovoValor1) - 3 )]
			self.vpg.SetValue(NovoValor2)
				
		except Exception, _reTornos:
			
			self.vpg.SetValue(str(self.SubTotal))
			self.ValorPagar = ''

	def limpar(self,event):

		self.vpg.SetValue(str(self.SubTotal))
		self.ValorPagar = ''
		self.vpg.SetFocus()
								
	def Teclas(self,event):

		keycode=event.GetKeyCode()

		if keycode == wx.WXK_F1:	self.registrar(wx.EVT_BUTTON)
		if keycode == wx.WXK_F11:	self.limpar(wx.EVT_BUTTON)
		if keycode == wx.WXK_F12:	self.voltar(self)
	
		event.Skip()		
		
	def voltar(self,event):	self.Destroy()

		
	def registrar(self,event):


		if not self.SubTotal > 0:

			semValor = wx.MessageDialog(self,"1-Nenhum valor registrado para recebimento...\n"+(" "*130),"Encerramento do Cupom",wx.OK)
		
			if semValor.ShowModal() ==  wx.OK:	pass
			semValor.Destroy()
			self.vpg.SetFocus()
			return

		if Decimal(self.vpg.GetValue()) == 0:			

			semValor = wx.MessageDialog(self,"2-Nenhum valor registrado para recebimento...\n"+(" "*130),"Encerramento do Cupom",wx.OK)
		
			if semValor.ShowModal() ==  wx.OK:	pass
			semValor.Destroy()
			self.vpg.SetFocus()
			return

		rTroco = False
		emissaoItem = self.fEcfs.rInformacoes("57",30)
		print "Emissao: ",emissaoItem

		if emissaoItem.strip() == "1":

			self.fEcfs.totalizaecf("D$","0.00")
			print "Inicio!!"
			
			FinalTotal = self.fEcfs.estendido(1,12)
			print "FinalTotal: ",FinalTotal
			
			TotaTotaliza = ('%.2f' % Decimal(FinalTotal[:10]+"."+FinalTotal[10:])).replace('.',',')
			self.ecf.finalizaCupom(("-"*125))
			self.ecf.finalizaCupom("Total R$: "+TotaTotaliza)
			
		if self.SubTotal > 0:

			valor  = Decimal(self.vpg.GetValue())
			vlrPa  = Decimal( ('%.3f' % valor) )
			vlrPg  = ('%.2f' % valor).replace('.',',')
			RecPag = self.fEcfs.fazpagamento("Dinheiro",vlrPg)				

			if RecPag == 1:

				self.ecf.finalizaCupom("Dinheiro: "+vlrPg)

				if vlrPa > self.SubTotal:
					
					Troco = ( valor - self.SubTotal )
					self.SubTotal = Decimal("0.000")
					valor         = Decimal("0.000")
					self.SvalorTotal.SetLabel('Troco:')
					rTroco = True

				self.totalizaPagamento()				
				self._SvalorTotal.SetLabel(('%.2f' % self.SubTotal).replace('.',','))	
				self.vpg.SetValue(str(self.SubTotal).strip())		
				if rTroco == True:

					self._SvalorTotal.SetLabel(('%.2f' % Troco).replace('.',','))

					self.SvalorTotal.SetForegroundColour('#4E8BC7')
					self._SvalorTotal.SetForegroundColour('#4E8BC7')
					self.ecf.finalizaCupom("Troco...: "+('%.2f' % Troco).replace('.',','))
									
		self.vpg.SetValue(str(self.SubTotal))
		self.ValorPagar = ''
				
		if self.SubTotal == 0:

			_mensagem    = PBI.PyBusyInfo("Encerramento do Cupom, Aguarde...", title="Cupom Fiscal",icon=wx.Bitmap("imagens/aguarde.png"))
			Encerramento = self.fEcfs.encerramento("0","Informacoes Promocionais\nInformacoes Adicionais")
			if Encerramento == 1:

				self.ecf.finalizaCupom("Ecerramento do CUPOM...")
				self.ecf.limpaVendas()
				self.ecf.caixalivre()
				
			del _mensagem
			if rTroco == False:	self.Destroy()		
			
		self.vpg.SetFocus()
		

	def totalizaPagamento(self):
		
		Tapagar = self.fEcfs.saldoApagar()
		TsubToT = self.fEcfs.subTotal()
		Tvpagos = self.fEcfs.rInformacoes("48",13)
				
		TotalGeral = Decimal( ('%.3f' % Decimal(TsubToT[:10]+"."+TsubToT[10:])) )
		TotalSubTo = Decimal( ('%.3f' % Decimal(Tapagar[:10]+"."+Tapagar[10:])) )				
		ToTalPagos = Decimal( ('%.3f' % Decimal(Tvpagos[:11]+"."+Tvpagos[11:])) )

		self.ValorCompra = TotalGeral
		self.SubTotal    = ( TotalGeral - ToTalPagos )
		if self.SubTotal < 0:	self.SubTotal = TotalSubTo

class Teclado(wx.Frame):
	
	saidadados = ''
	moduloaces = ''
	
	def __init__(self,parent,id):
		
		self.pConsulta = PainelPrincipal.acessCons
		self.funGerais = funcoesGerais.acessCons

		wx.Frame.__init__(self, parent, id, 'Teclado Virtual', size=(885,250), style=wx.NO_BORDER|wx.FRAME_FLOAT_ON_PARENT)
		painel = wx.Panel(self)

		L1 = wx.Button(painel,200,"1",(0,0),(70,40))
		L1.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		
		
		L2 = wx.Button(painel,201,"2",(90,0),(70,40))
		L2.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		L3 = wx.Button(painel,202,"3",(180,0),(70,40))
		L3.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		L4 = wx.Button(painel,203,"4",(270,0),(70,40))
		L4.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		
		
		L5 = wx.Button(painel,204,"5",(360,0),(70,40))
		L5.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		L6 = wx.Button(painel,205,"6",(450,0),(70,40))
		L6.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		L7 = wx.Button(painel,206,"7",(540,0),(70,40))
		L7.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		L8 = wx.Button(painel,207,"8",(630,0),(70,40))
		L8.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		L9 = wx.Button(painel,208,"9",(720,0),(70,40))
		L9.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		L0 = wx.Button(painel,209,"0",(810,0),(70,40))
		L0.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lq = wx.Button(painel,100,"Q",(0,50),(70,40))
		Lq.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lw = wx.Button(painel,101,"W",(90,50),(70,40))
		Lw.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Le = wx.Button(painel,102,"E",(180,50),(70,40))
		Le.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lr = wx.Button(painel,103,"R",(270,50),(70,40))
		Lr.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lt = wx.Button(painel,104,"T",(360,50),(70,40))
		Lt.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Ly = wx.Button(painel,105,"Y",(450,50),(70,40))
		Ly.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lu = wx.Button(painel,106,"U",(540,50),(70,40))
		Lu.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Li = wx.Button(painel,107,"I",(630,50),(70,40))
		Li.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lo = wx.Button(painel,108,"O",(720,50),(70,40))
		Lo.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lp = wx.Button(painel,109,"P",(810,50),(70,40))
		Lp.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		La = wx.Button(painel,110,"A",(0,100),(70,40))
		La.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Ls = wx.Button(painel,111,"S",(90,100),(70,40))
		Ls.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		
		
		Ld = wx.Button(painel,112,"D",(180,100),(70,40))
		Ld.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lf = wx.Button(painel,113,"F",(270,100),(70,40))
		Lf.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lg = wx.Button(painel,114,"G",(360,100),(70,40))
		Lg.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lh = wx.Button(painel,115,"H",(450,100),(70,40))
		Lh.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lj = wx.Button(painel,116,"J",(540,100),(70,40))
		Lj.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lk = wx.Button(painel,117,"K",(630,100),(70,40))
		Lk.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Ll = wx.Button(painel,118,"L",(720,100),(70,40))
		Ll.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lz = wx.Button(painel,120,"Z",(0,150),(70,40))
		Lz.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lx = wx.Button(painel,121,"X",(90,150),(70,40))
		Lx.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lc = wx.Button(painel,122,"C",(180,150),(70,40))
		Lc.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lv = wx.Button(painel,123,"V",(270,150),(70,40))
		Lv.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lb = wx.Button(painel,124,"B",(360,150),(70,40))
		Lb.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Ln = wx.Button(painel,125,"N",(450,150),(70,40))
		Ln.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		Lm = wx.Button(painel,126,"M",(540,150),(70,40))
		Lm.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		dL = wx.Button(painel,127,":",(630,150),(70,40))
		dL.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		

		pL = wx.Button(painel,128,".",(720,150),(70,40))
		pL.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD))		
		
		Eraser = GenBitmapTextButton(painel, -1, wx.Bitmap('imagens/eraser.png'), "Limpar", (810,100),(70,40),style=wx.BU_LEFT)
		Eraser.SetForegroundColour('#FFFFFF');	Eraser.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL, wx.BOLD))
		Eraser.SetBezelWidth(5);	Eraser.SetBackgroundColour("#5A5A2D")		

		Apagar = GenBitmapTextButton(painel, -1, wx.Bitmap('imagens/voltarcan.png'), "Apagar", (810,150),(70,40),style=wx.BU_LEFT)
		Apagar.SetForegroundColour('#FFFFFF');	Apagar.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL, wx.BOLD))
		Apagar.SetBezelWidth(5);	Apagar.SetBackgroundColour("#5A5A2D")		

		Entrar = GenBitmapTextButton(painel, -1, wx.Bitmap('imagens/return.png'), "Enter", (770,200),(110,40),style=wx.BU_LEFT)
		Entrar.SetForegroundColour('#FFFFFF');	Entrar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		Entrar.SetBezelWidth(5);	Entrar.SetBackgroundColour("#787825")		

		Voltar = GenBitmapTextButton(painel, -1, wx.Bitmap('imagens/voltar.png'), "Voltar", (640,200),(110,40),style=wx.BU_LEFT)
		Voltar.SetForegroundColour('#FFFFFF');	Voltar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		Voltar.SetBezelWidth(5);	Voltar.SetBackgroundColour("#787825")		

		Espaco = GenBitmapTextButton(painel, 300, wx.Bitmap('imagens/espaco.png'), "", (0,200),(610,40),style=wx.BU_LEFT)
		Espaco.SetForegroundColour('#FFFFFF');	Espaco.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD))
		Espaco.SetBezelWidth(5);	Espaco.SetBackgroundColour("#787825")		

		Lq.Bind(wx.EVT_BUTTON, self.Teclas);	Lw.Bind(wx.EVT_BUTTON, self.Teclas)
		Le.Bind(wx.EVT_BUTTON, self.Teclas);	Lr.Bind(wx.EVT_BUTTON, self.Teclas)
		Lt.Bind(wx.EVT_BUTTON, self.Teclas);	Ly.Bind(wx.EVT_BUTTON, self.Teclas)
		Lu.Bind(wx.EVT_BUTTON, self.Teclas);	Li.Bind(wx.EVT_BUTTON, self.Teclas)
		Lo.Bind(wx.EVT_BUTTON, self.Teclas);	Lp.Bind(wx.EVT_BUTTON, self.Teclas)

		La.Bind(wx.EVT_BUTTON, self.Teclas);	Ls.Bind(wx.EVT_BUTTON, self.Teclas)
		Ld.Bind(wx.EVT_BUTTON, self.Teclas);	Lf.Bind(wx.EVT_BUTTON, self.Teclas)
		Lg.Bind(wx.EVT_BUTTON, self.Teclas);	Lh.Bind(wx.EVT_BUTTON, self.Teclas)
		Lj.Bind(wx.EVT_BUTTON, self.Teclas);	Lk.Bind(wx.EVT_BUTTON, self.Teclas)
		Ll.Bind(wx.EVT_BUTTON, self.Teclas)

		Lz.Bind(wx.EVT_BUTTON, self.Teclas);	Lx.Bind(wx.EVT_BUTTON, self.Teclas)
		Lc.Bind(wx.EVT_BUTTON, self.Teclas);	Lv.Bind(wx.EVT_BUTTON, self.Teclas)
		Lb.Bind(wx.EVT_BUTTON, self.Teclas);	Ln.Bind(wx.EVT_BUTTON, self.Teclas)
		Lm.Bind(wx.EVT_BUTTON, self.Teclas); 	dL.Bind(wx.EVT_BUTTON, self.Teclas)
		pL.Bind(wx.EVT_BUTTON, self.Teclas)

		L1.Bind(wx.EVT_BUTTON, self.Teclas);	L2.Bind(wx.EVT_BUTTON, self.Teclas)
		L3.Bind(wx.EVT_BUTTON, self.Teclas);	L4.Bind(wx.EVT_BUTTON, self.Teclas)
		L5.Bind(wx.EVT_BUTTON, self.Teclas);	L6.Bind(wx.EVT_BUTTON, self.Teclas)
		L7.Bind(wx.EVT_BUTTON, self.Teclas);	L8.Bind(wx.EVT_BUTTON, self.Teclas)
		L9.Bind(wx.EVT_BUTTON, self.Teclas);	L0.Bind(wx.EVT_BUTTON, self.Teclas)
		
		Apagar.Bind(wx.EVT_BUTTON, self.Apagar)
		Voltar.Bind(wx.EVT_BUTTON, self.Voltar)
		Entrar.Bind(wx.EVT_BUTTON, self.entrada)
		Espaco.Bind(wx.EVT_BUTTON, self.Teclas)
		Eraser.Bind(wx.EVT_BUTTON, self.Eraser)

	def Voltar(self,event):

		if self.moduloaces == '1':
			self.pConsulta.AtualizaCons('',1)

		self.Destroy()

	def Eraser(self,event):

		self.saidadados = ''
		if self.moduloaces == '1':
			self.pConsulta.AtualizaCons(self.saidadados,1)

		elif self.moduloaces == '2' or self.moduloaces == '3' or self.moduloaces == '4':
			self.funGerais.aTualizaCliente(self.saidadados,self.moduloaces)
		
	def Apagar(self,event):

		self.saidadados = self.saidadados[0:( len(self.saidadados) - 1 )]
		if self.moduloaces == '1':
			self.pConsulta.AtualizaCons(self.saidadados,1)

		elif self.moduloaces == '2' or self.moduloaces == '3' or self.moduloaces == '4':
			self.funGerais.aTualizaCliente(self.saidadados,self.moduloaces)
		
	def entrada(self,event):

		if self.moduloaces == '1':
			self.pConsulta.AtualizaCons(self.saidadados,2)		

		elif self.moduloaces == '2' or self.moduloaces == '3' or self.moduloaces == '4':
			self.funGerais.aTualizaCliente(self.saidadados,self.moduloaces)

		self.Destroy()
		
	def Teclas(self,event):

		if event.GetId() == 100:Letra="q"
		if event.GetId() == 101:Letra="w"
		if event.GetId() == 102:Letra="e"
		if event.GetId() == 103:Letra="r"
		if event.GetId() == 104:Letra="t"
		if event.GetId() == 105:Letra="y"
		if event.GetId() == 106:Letra="u"
		if event.GetId() == 107:Letra="i"
		if event.GetId() == 108:Letra="o"
		if event.GetId() == 109:Letra="p"
		
		if event.GetId() == 110:Letra="a"
		if event.GetId() == 111:Letra="s"
		if event.GetId() == 112:Letra="d"
		if event.GetId() == 113:Letra="f"
		if event.GetId() == 114:Letra="g"
		if event.GetId() == 115:Letra="h"
		if event.GetId() == 116:Letra="j"
		if event.GetId() == 117:Letra="k"
		if event.GetId() == 118:Letra="l"

		if event.GetId() == 120:Letra="z"
		if event.GetId() == 121:Letra="x"
		if event.GetId() == 122:Letra="c"
		if event.GetId() == 123:Letra="v"
		if event.GetId() == 124:Letra="b"
		if event.GetId() == 125:Letra="n"
		if event.GetId() == 126:Letra="m"
		if event.GetId() == 127:Letra=":"
		if event.GetId() == 128:Letra="."
		if event.GetId() == 300:Letra=" "

		if event.GetId() == 200:Letra="1"
		if event.GetId() == 201:Letra="2"
		if event.GetId() == 202:Letra="3"
		if event.GetId() == 203:Letra="4"
		if event.GetId() == 204:Letra="5"
		if event.GetId() == 205:Letra="6"
		if event.GetId() == 206:Letra="7"
		if event.GetId() == 207:Letra="8"
		if event.GetId() == 208:Letra="9"
		if event.GetId() == 209:Letra="0"
		
		self.saidadados +=Letra

		if self.moduloaces == '1':
			self.pConsulta.AtualizaCons(self.saidadados,1)

		elif self.moduloaces == '2' or self.moduloaces == '3' or self.moduloaces == '4':
			self.funGerais.aTualizaCliente(self.saidadados,self.moduloaces)
		
class ecfPrincipal(wx.Frame):

	_basedd = ''
	_cursor = ''
	ecfs    = ''

	def __init__(self,parent,id):

		gPath = os.getcwd()
		wx.Frame.__init__(self,parent,id,'{LITTUS} {Chekaute}')

		#_mensagem = PBI.PyBusyInfo("{LIB-DLL ECF}->Base, Acesso ao PDV\n\nAguarde...", title="Chekaute!!",icon=wx.Bitmap("imagens/aguarde.png"))
		#if os.path.exists('lib/64/libDarumaFramework.so') == True:

		try:

			conn = sqldb()
			sql  = conn.dbc("DAVs, Clientes CEPS",1,login.identifi)
			
			ecfPrincipal._basedd = sql[1]
			ecfPrincipal._cursor = sql[2]

			#del _mensagem
				
			parente=parent
			ecfPrincipal.ecfs = PainelPrincipal(self,parente)
				
		except Exception, _reTorno:

			wx.MessageBox("Retornos Base SQL, Chekaute...\nRetorno: "+str(_reTorno),"Cadastro de Produtos",wx.OK)	
			self.Destroy()
		#else:
			
		#	del _mensagem			
		#	wx.MessageBox("Biblioteca do ECF não localizado...\n\nPressione OK,p/voltar !!","Cadastro de Produtos",wx.OK)	
		#	self.Destroy()
