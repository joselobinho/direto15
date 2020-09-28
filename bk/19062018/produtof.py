#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import datetime
import glob

import commands
import os

from decimal import *
from conectar import sqldb,AbrirArquivos,dialogos,cores,login,numeracao,sbarra,formasPagamentos,CodigoMunicipio,TelNumeric,truncagem,diretorios,menssagem,acesso
from plcontas  import PlanoContas
from relatorio import relcompra,relatorioSistema
from produtom  import rTabelas,CalcularConversao
from cadfretes import blqadmsystem
from cdavs import impressao
from bdavs import CalcularTributos
from wx.lib.buttons import GenBitmapTextButton

alertas = dialogos()
sb      = sbarra()
nF      = numeracao()
Trunca  = truncagem()
mens    = menssagem()
rls     = relatorioSistema()
acs     = acesso()
rcTribu = CalcularTributos()
embmetros = CalcularConversao()

class fornecedores(wx.Frame):

	fornece  = {}
	registro = 0
	pesquisa = False

	nmFornecedor = ''
	NomeFilial   = ''
	unidademane  = False
	transportar  = False

	registro_expedicao = ''

	def __init__(self, parent,id):
		
		self.p = parent
		self.p.Disable()
		self.lsT = []
		
		self.cFcFilial = self.NomeFilial
		
		wx.Frame.__init__(self, parent, id, 'Fornecedores: Cadastro de fornecedores e serviços', size=(900,565), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.fornecedor = FRListCtrl(self.painel, 300 ,pos=(10,40), size=(885,405),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.fornecedor.SetBackgroundColour('#DCE9F5')
		self.fornecedor.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.editarfr)
		self.fornecedor.Bind(wx.EVT_LIST_ITEM_SELECTED, self.passagem)

		wx.StaticText(self.painel,-1,"Pesquisar: Descrição,CPF-CNPJ, R:Registro, P:Expressão",  pos=(20, 452)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tipos de Fornecedores",  pos=(423, 452)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Filiais/Empresa:", pos=(0,   8) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Filial:",          pos=(420, 8) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tranportador",     pos=(20, 500)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Período",          pos=(733,500)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		
		self.oco = wx.StaticText(self.painel,-1,"",  pos=(297, 452))
		self.oco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.oco.SetForegroundColour('#4B7CA9')

		apiint= wx.BitmapButton(self.painel, 111, wx.Bitmap("imagens/api24.png",        wx.BITMAP_TYPE_ANY), pos=(590,459), size=(30,30))	
		pjbank = wx.BitmapButton(self.painel, 110, wx.Bitmap("imagens/bank24.png",       wx.BITMAP_TYPE_ANY), pos=(625,459), size=(30,30))	
		atuali = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/importp.png",      wx.BITMAP_TYPE_ANY), pos=(663,459), size=(30,30))	
		instru = wx.BitmapButton(self.painel, 112, wx.Bitmap("imagens/referencia16.png", wx.BITMAP_TYPE_ANY), pos=(697,459), size=(30,30))	
		unidad = wx.BitmapButton(self.painel, 132, wx.Bitmap("imagens/tree16.png",       wx.BITMAP_TYPE_ANY), pos=(730,459), size=(30,30))	

		procur = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/procurap.png",      wx.BITMAP_TYPE_ANY), pos=(550,453), size=(36,36))				
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltam.png",        wx.BITMAP_TYPE_ANY), pos=(772,453), size=(36,36))				
		inclui = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/incluip.png",       wx.BITMAP_TYPE_ANY), pos=(814,453), size=(36,36))				
		altera = wx.BitmapButton(self.painel, 300, wx.Bitmap("imagens/alterarm.png",      wx.BITMAP_TYPE_ANY), pos=(856,453), size=(36,36))
		
		self.relato = wx.BitmapButton(self.painel, 301, wx.Bitmap("imagens/produtos.png", wx.BITMAP_TYPE_ANY), pos=(855,507), size=(36,36))

		""" Empresas Filiais """
		relaFil = [""]+login.ciaRelac
		self.rfilia = wx.ComboBox(self.painel, -1, '',  pos=(93, 4), size=(300,28), choices = relaFil,style=wx.NO_BORDER|wx.CB_READONLY)

		self.filialc = wx.TextCtrl(self.painel,-1,"", pos=(455,4),size=(441,25), style=wx.TE_READONLY)
		self.filialc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.filialc.SetBackgroundColour('#E5E5E5')
		self.filialc.SetForegroundColour("#7F7F7F")

		self.consultar = wx.TextCtrl(self.painel, -1, "",              pos=(15,463),  size = (400,27), style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.fornecedo = wx.ComboBox(self.painel, -1, login.TForne[0], pos=(420,463), size = (120,27), choices = login.TForne,style=wx.NO_BORDER|wx.CB_READONLY)
		if self.unidademane:	self.fornecedo.SetValue( login.TForne[6] )

		self.Transporta = wx.TextCtrl(self.painel, -1, "", pos=(15,517),  size = (400,25), style=wx.TE_READONLY)
		self.Transporta.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.Transporta.SetBackgroundColour('#BFBFBF')

		self.TrIndividu = wx.CheckBox(self.painel, -1,  "- Marcar p/Relatório por Transportador\n- Desmarcar relatório p/todos os transportadores\n  com entrega no periódo", pos=(423,500))
		self.TrIndividu.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(730,510), size=(115,22), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(730,533), size=(115,22))

		atuali.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		instru.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		inclui.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		altera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		procur.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		pjbank.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		apiint.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.relato.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		atuali.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		instru.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		inclui.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		altera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		procur.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		pjbank.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		apiint.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.relato.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		self.fornecedo.Bind(wx.EVT_COMBOBOX, self.SeleCombo)
		
		self.rfilia.Bind(wx.EVT_COMBOBOX, self.FornecedorFilial)
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		inclui.Bind(wx.EVT_BUTTON, self.editarfr)
		altera.Bind(wx.EVT_BUTTON, self.editarfr)
		atuali.Bind(wx.EVT_BUTTON, self.exporta)
		procur.Bind(wx.EVT_BUTTON, self.selecionar)
		instru.Bind(wx.EVT_BUTTON, self.instrucao)
		unidad.Bind(wx.EVT_BUTTON, self.unidadeManejoFlorestal)
		apiint.Bind(wx.EVT_BUTTON, self.apiInformacao)
		
		self.relato.Bind(wx.EVT_BUTTON, self.relatoriofc)
		if self.transportar:

			self.fornecedo.SetValue( login.TForne[4] )
			self.fornecedo.Enable( False )
		
		self.FornecedorFilial(wx.EVT_BUTTON)
		
		if self.NomeFilial !="":	self.rfilia.Enable(False)
		if self.nmFornecedor !='':	self.consultar.SetValue(self.nmFornecedor)
		self.selecionar(wx.EVT_BUTTON)
		if self.pesquisa == False:	atuali.Disable()
		if self.transportar:	atuali.Enable()

		self.TrIndividu.Enable( False )
		self.relato.Enable( False )
		self.dindicial.Enable( False )
		self.datafinal.Enable( False )

		inclui.Enable( acs.acsm("901",True) )
		altera.Enable( acs.acsm("901",True) )
		unidad.Enable( acs.acsm("903",True) )

		self.consultar.SetFocus()

	def FornecedorFilial(self,event):
		
		fila = self.rfilia.GetValue().split("-")[0]
		if self.rfilia.GetValue() == "":	fila = login.identifi
		if self.NomeFilial !="":	fila = self.NomeFilial
		self.cFcFilial = fila
		FRListCtrl.FRCFilial = fila
		
		if self.NomeFilial !="":	self.rfilia.SetValue( fila + "-"+  login.filialLT[ fila ][14].upper().decode('utf-8') )
		self.filialc.SetValue( login.filialLT[ fila ][1].upper() )
		self.filialc.SetBackgroundColour('#E5E5E5')
		self.filialc.SetForegroundColour('#4D4D4D')	

		if nF.rF( cdFilial = fila ) == "T":

			self.filialc.SetBackgroundColour('#711717')
			self.filialc.SetForegroundColour('#FF2800')	

		elif nF.rF( cdFilial = fila ) !="T" and login.identifi != fila:

			self.filialc.SetBackgroundColour('#0E60B1')
			self.filialc.SetForegroundColour('#E0E0FB')	

	def passagem(self,event):
		
		indice = self.fornecedor.GetFocusedItem()
		Valor  = True

		if self.fornecedor.GetItem(indice, 8).GetText() == "4":

			self.Transporta.SetValue( self.fornecedor.GetItem(indice, 4).GetText() )
			self.TrIndividu.SetValue( True )

		else:

			self.Transporta.SetValue( '' )
			self.TrIndividu.SetValue( False )
			Valor = False

		self.TrIndividu.Enable( Valor )
		self.relato.Enable( Valor )
		self.dindicial.Enable( Valor )
		self.datafinal.Enable( Valor )

	def exporta(self,event):

		if self.fornecedor.GetItemCount() !=0:
			
			indice = self.fornecedor.GetFocusedItem()
			__id = self.fornecedor.GetItem(indice,0).GetText()
			__dc = self.fornecedor.GetItem(indice,2).GetText()
			__ft = self.fornecedor.GetItem(indice,3).GetText()
			__nm = self.fornecedor.GetItem(indice,4).GetText()
			__ie = self.fornecedor.GetItem(indice,5).GetText()
			__im = self.fornecedor.GetItem(indice,6).GetText()
			__cn = self.fornecedor.GetItem(indice,7).GetText()
			__rp = self.fornecedor.GetItem(indice,15).GetText()
			__pc = self.fornecedor.GetItem(indice,16).GetText()
			__ru = self.fornecedor.GetItem(indice,17).GetText()
			__up = self.fornecedor.GetItem(indice,18).GetText()

			__cg = self.fornecedor.GetItem(indice,19).GetText()
			__cm = self.fornecedor.GetItem(indice,20).GetText()

			if self.transportar:	self.p.retornoFornecedor( __id, __dc, __nm, __cg, __cm ) #-: usado p/expedicao
			else:
				
				if self.unidademane:	self.p.ajustarManejo( __dc, __ft, __nm, __ie, __im, __cn, __id, __rp, __pc, __ru, __up )
				else:	self.p.ajustafrn( __dc, __ft, __nm, __ie, __im, __cn, __id, __rp, __pc )
				
			self.sair(wx.EVT_BUTTON)
			
	def SeleCombo(self,event):
		
		self.consultar.SetValue('')
		self.selecionar(wx.EVT_BUTTON)
		
	def editarfr(self,event):

		indice = self.fornecedor.GetFocusedItem()
		codigo = self.fornecedor.GetItem(indice, 0).GetText()

		if acs.acsm("901",True) == False:	alertas.dia(self,"Opção indisponível p/usuário atual...\n"+(" "*100),"Alteração do Fornecedor")
		else:
			
			edicaofr.cadastro = event.GetId()
			edicaofr.codigofr = codigo 
			efr_frame=edicaofr(parent=self,id=-1)
			efr_frame.Centre()
			efr_frame.Show()

	def instrucao(self,event):
		
		InstrucaoBoleto.CodigId = self.fornecedor.GetItem(self.fornecedor.GetFocusedItem(), 0).GetText()

		efr_frame=InstrucaoBoleto(parent=self,id=-1)
		efr_frame.Centre()
		efr_frame.Show()

	def unidadeManejoFlorestal(self,event):

		efr_frame=UnidadeManejo(parent=self,id=-1)
		efr_frame.Centre()
		efr_frame.Show()

	def apiInformacao(self,event):

		if self.fornecedor.GetItem( self.fornecedor.GetFocusedItem(), 8 ).GetText() == "3":

			api_frame=InformacoesAPI(parent=self,id=-1)
			api_frame.Centre()
			api_frame.Show()

		else:	alertas.dia(self, "Apenas para bancos cadastrados...\n"+(" "*150),"Dados de conexão para API")
		
	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()

	def selecionar(self,event):
			
		conn = sqldb()
		sql  = conn.dbc("Fornecedor: cadastro", fil = self.cFcFilial, janela = self.painel )

		pesq = self.consultar.GetValue().upper().split(":")
		
		if sql[0] == True:

			pf = "SELECT * FROM fornecedor WHERE fr_regist!=0 ORDER BY fr_nomefo"
			if self.consultar.GetValue() == '' and self.fornecedo.GetValue()[:1] != "1":	pf = pf.replace("ORDER","and fr_tipofi='"+str( int(self.fornecedo.GetValue()[:1]) - 1 )+"' ORDER")
			if self.consultar.GetValue() != '' and self.consultar.GetValue().isdigit() == False and len( pesq ) == 1:	pf = pf.replace("ORDER","and fr_nomefo like '"+ pesq[0] +"%' ORDER")
			if self.consultar.GetValue() != '' and self.consultar.GetValue().isdigit() == False and len( pesq ) == 2 and pesq[0] == "P":	pf = pf.replace("ORDER","and fr_nomefo like '%"+ pesq[1] +"%' ORDER")
			if self.consultar.GetValue() != '' and self.consultar.GetValue().isdigit() == False and len( pesq ) == 2 and pesq[0] == "R":	pf = pf.replace("ORDER","and fr_regist='"+str( pesq[1] )+"' ORDER")

			if self.consultar.GetValue() != '' and self.consultar.GetValue().isdigit() == True:	pf = pf.replace("ORDER","and fr_docume like '"+str( pesq[0] )+"%' ORDER")
			if self.transportar and self.registro_expedicao:	 pf = pf.replace("ORDER","and fr_regist='"+str( self.registro_expedicao )+"' ORDER")

			pLista = sql[2].execute( pf )
			
			result = sql[2].fetchall()
			conn.cls(sql[1])

			if pLista !=0:
				
				fornecedores.fornece  = {} 
				fornecedores.registro = 0   

				_registros = 0
				relacao = {}

				for i in result:
					
					relacao[_registros] = str(i[0]),str(i[23]),str(i[1]),i[7],i[6],i[2],i[3],i[4],i[24],i[25],i[26],i[27],i[28],i[29],i[30],i[34],i[33],i[38] if i[38] else "",i[39],str( i[40] ), str( i[41] )
					_registros +=1

				if pLista:	self.oco.SetLabel("Ocorrencias: { "+str(pLista).zfill(5)+" }")
				else:	self.oco.SetLabel("")
				
				fornecedores.fornece    = relacao 
				FRListCtrl.itemDataMap  = relacao
				FRListCtrl.itemIndexMap = relacao.keys()   

			#--: Numero de ocorrencias
			self.fornecedor.SetBackgroundColour('#DCE9F5')
			if nF.rF( cdFilial = self.cFcFilial ) == "T":	self.fornecedor.SetBackgroundColour('#BE8F8F')

			self.fornecedor.SetItemCount(pLista)

#--:Relatorio
	def relatoriofc( self, event ):
		
		indice = self.fornecedor.GetFocusedItem()
		docume = self.fornecedor.GetItem(indice, 2).GetText()

		if self.TrIndividu.GetValue() == True and docume == '':	alertas.dia(self.painel,u"CPF-CNPJ, estar vazio !!\n"+(' '*80),"Forncedores: Relatório")
		else:
			
			lsT = []
			Id = self.dindicial.GetValue()
			Fd = self.datafinal.GetValue()
			
			dI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			dF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

			conn = sqldb()
			sql  = conn.dbc("Fornecedor", fil = self.cFcFilial, janela = self.painel )
			
			if sql[0] == True:

				self.lsT = []
				
#-------------: Individual
				if self.TrIndividu.GetValue() == True:

					acha = "SELECT * FROM romaneio WHERE rm_fecdt>='"+str( dI )+"' and rm_fecdt<='"+str( dF )+"' and rm_canus='' and rm_cpfcn='"+str( docume )+"' ORDER BY rm_roman"
					_fsf = sql[2].execute( acha )
					fors = sql[2].fetchall()
					
					if _fsf !=0:
						
						for i in fors:
							
							self.lsT.append( i[1]+"<p>"+format( i[2], "%d/%m/%Y" )+"<p>"+format( i[6], "%d/%m/%Y" )+"<p>"+str( i[15] )+"<p>"+format( i[22],"%d/%m/%Y" )+"<p>"+str( i[23] ) )

#-------------: Todos
				elif self.TrIndividu.GetValue() == False:

					lsTf = sql[2].execute("SELECT fr_docume,fr_nomefo FROM fornecedor WHERE fr_tipofi='4' ORDER BY fr_nomefo")
					
					if lsTf !=0:

						relaf = sql[2].fetchall()
						
						for rf in relaf:
							
							acha = "SELECT * FROM romaneio WHERE rm_fecdt>='"+str( dI )+"' and rm_fecdt<='"+str( dF )+"' and rm_canus='' and rm_cpfcn='"+str( rf[0] )+"' ORDER BY rm_roman"
							_fsf = sql[2].execute( acha )
							fsfo = sql[2].fetchall()

							if _fsf !=0:
								
								for i in fsfo:
									
									self.lsT.append( i[1]+"<p>"+format( i[2], "%d/%m/%Y" )+"<p>"+format( i[6], "%d/%m/%Y" )+"<p>"+str( i[15] )+"<p>"+format( i[22],"%d/%m/%Y" )+"<p>"+str( i[23] ) )
					
				conn.cls( sql[1] )
				if self.lsT != []:	rls.RomaneioFrete( Id, Fd, self, self.cFcFilial )

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Incluir um Novo Fornecedor { Produtos, Serviços, Bancos e Transportador }",0)
		elif event.GetId() == 300:	sb.mstatus(u"  Alterar Editar Fornecedor Selecionado { Click Duplo para Editar e Alterar }",0)
		elif event.GetId() == 301:	sb.mstatus(u"  Relatório de Entregas por Transportador",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Pesquisa Procurar Fornecedor",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Exporta para Modulo Chamador",0)
		elif event.GetId() == 112:	sb.mstatus(u"  Instruções do Boleto Bancario",0)
		elif event.GetId() == 110:	sb.mstatus(u"  Conta digital do PJBANK, emissão de boletos, recebimentos em cartão de credito",0)
		elif event.GetId() == 111:	sb.mstatus(u"  Dados para a API de integração { TOKEN, USUARIO, SENHA, URLs } - Emissão de boletos, recebimentos em cartão TED,DOC ",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Cadastro de Fornecedores: { Produtos, Serviços, Bancos, Tranportador }",0)
		event.Skip()

	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2F809B") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Relatório     CADASTRO DE FORNECEDORES", 0, 555, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,  448,882, 45,   3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12,  496,882, 62,   3) #-->[ Lykos ]

class FRListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}
	FRCFilial = ''
	
	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		_fornece = fornecedores.fornece
		FRListCtrl.itemDataMap  = _fornece
		FRListCtrl.itemIndexMap = _fornece.keys()  
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr4 = wx.ListItemAttr()
		self.attr5 = wx.ListItemAttr()
		self.attr6 = wx.ListItemAttr()

		self.attr1.SetBackgroundColour("#E0EFFB")
		self.attr2.SetBackgroundColour("#EEFFEE")
		self.attr3.SetBackgroundColour("#FFBEBE")
		self.attr4.SetBackgroundColour("#F6F6AE")
		self.attr5.SetBackgroundColour("#EB9494")
		self.attr6.SetBackgroundColour("#B07C7C")

		self.InsertColumn(0, 'Código ID', format=wx.LIST_ALIGN_LEFT,width=70)
		self.InsertColumn(1, 'Filial',   width=70)
		self.InsertColumn(2, 'CPF-CNPJ', format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(3, 'Fantasia',                  width=200)
		self.InsertColumn(4, 'Descrição do Fornecedores', width=600)

		self.InsertColumn(5, 'I.Estadual',  width=110)
		self.InsertColumn(6, 'I.Municipal', width=110)
		self.InsertColumn(7, 'CNAE',        width=110)
		self.InsertColumn(8, 'Tipo',        width=50)

		self.InsertColumn(9, 'Banco',    format=wx.LIST_ALIGN_LEFT,width=70)
		self.InsertColumn(10,'Agência',  format=wx.LIST_ALIGN_LEFT,width=70)
		self.InsertColumn(11,'Nº Conta', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(12,'Convênio', format=wx.LIST_ALIGN_LEFT,width=70)
		self.InsertColumn(13,'Especie',  format=wx.LIST_ALIGN_LEFT,width=70)
		self.InsertColumn(14,'Carteira', format=wx.LIST_ALIGN_LEFT,width=70)
		self.InsertColumn(15,'Descrição do Representante', width=500)
		self.InsertColumn(16,'Plano de Contas', width=200)
		self.InsertColumn(17,'Unidades de manejo', width=200)
		self.InsertColumn(18,'Unidades de manejo padrao', width=200)

		self.InsertColumn(19,'Carga KG', width=100)
		self.InsertColumn(20,'Comprimento MT', width=100)
					
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index=self.itemIndexMap[item]

		if item % 2:

			if nF.rF( cdFilial = self.FRCFilial ) == "T":	return self.attr6

			return self.attr1
		
	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][8] == "1":	return self.sim
		if self.itemDataMap[index][8] == "2":	return self.sim1
		if self.itemDataMap[index][8] == "3":	return self.sim2
		if self.itemDataMap[index][8] == "4":	return self.sim3
		if self.itemDataMap[index][8] == "5":	return self.sim4
		return self.sim

	def GetListCtrl(self):	return self

class InformacoesAPI(wx.Frame):

	def __init__(self, parent,id):
		
		self.p = parent
		wx.Frame.__init__(self, parent, id, '{ Fornecedor } Credencias para API', size=(708,242), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		__i = self.p.fornecedor.GetFocusedItem()
		__t = self.p.fornecedor.GetItem( __i, 8 ).GetText()
		__d = self.p.fornecedor.GetItem( __i, 0 ).GetText()+'-'+self.p.fornecedor.GetItem( __i, 4 ).GetText()
		self.idf = self.p.fornecedor.GetItem( __i, 0 ).GetText()

		wx.StaticText(self.painel,-1,"Tipo de fornecedor: ",  pos=(17,3)  ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descriçao do fornecedor: ", pos=(127,3)  ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Servidor de web-service ",  pos=(20,50)  ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"URL-Envio { para o envio da solicitação da API para conexão } ",  pos=(20,100) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"URL-Copia { para o envio da solicitação da API para 2a via } ",  pos=(20,150) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"TOKEN-Login { para conexão do serviço do web-service } ",  pos=(20,200) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.tp_fornecedor = wx.TextCtrl(self.painel,-1, __t ,pos=(15,15),size=(100,25), style = wx.TE_READONLY)
		self.tp_fornecedor.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.tp_fornecedor.SetBackgroundColour('#E5E5E5')

		self.id_fornecedor = wx.TextCtrl(self.painel,-1, __d, pos=(125,15),size=(373,25), style = wx.TE_READONLY)
		self.id_fornecedor.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.id_fornecedor.SetBackgroundColour('#E5E5E5')

		api_gravar = GenBitmapTextButton(self.painel,-1,label='   Gravar os dados para a API\n   do servço web-service',  pos=(502,5),size=(203,33), bitmap=wx.Bitmap("imagens/api24.png", wx.BITMAP_TYPE_ANY))
		api_gravar.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.fornecedor_servico = ["","1 - Boleto cloud { emissão de boletos com painel, arquivos CNAB [ Emissão free e pago ] }","2 - PJBANK Conta digital { emissão de boletos, recebimentos em cartão, TED, DOC, [Mais] }"]
		self.servidor_web = wx.ComboBox(self.painel, 700, '', pos=(18,63), size=(688,27), choices = self.fornecedor_servico, style = wx.CB_READONLY)

		self.url_solicitacao = wx.TextCtrl(self.painel,-1, __d, pos=(18,113),size=(688,25))
		self.url_solicitacao.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.url_solicitacao.SetBackgroundColour('#E5E5E5')

		self.url_segundavia = wx.TextCtrl(self.painel,-1, __d, pos=(18,163),size=(688,25))
		self.url_segundavia.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.url_segundavia.SetBackgroundColour('#E5E5E5')

		self.token_login = wx.TextCtrl(self.painel,-1, __d, pos=(18,213),size=(688,25))
		self.token_login.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.token_login.SetBackgroundColour('#E5E5E5')

		self.tp_fornecedor.SetValue( login.TForne[int(__t)] )
		api_gravar.Bind(wx.EVT_BUTTON, self.gravarDadosAPI)
		
		self.servidor_web.Bind(wx.EVT_COMBOBOX, self.servidorServico)

		self.consultaDadosAPI()
	
	def servidorServico(self,event):
		
		en = True
		if self.servidor_web.GetValue().split('-')[0].strip() and self.servidor_web.GetValue().split('-')[0].strip() == "2":
			
			self.url_solicitacao.SetValue("")
			self.url_segundavia.SetValue("")
			self.token_login.SetValue("")
			en = False

		self.url_solicitacao.Enable( en )
		self.url_segundavia.Enable( en )
		self.token_login.Enable( en )

	def consultaDadosAPI( self ):
		
		conn = sqldb()
		sql  = conn.dbc("Fornecedor: cadastro", fil = self.p.cFcFilial, janela = self.painel )
		if sql[0]:
			
			acha = "SELECT fr_parame FROM fornecedor WHERE fr_regist='" +self.idf+ "'"
			if sql[2].execute( acha ):
				
				srv = urc =	urv = tok = ""
				
				__d = sql[2].fetchone()[0]

				if __d:	srv, urc , urv ,tok = __d.split('|')
				self.servidor_web.SetValue( self.fornecedor_servico[ int( srv ) ] if __d and srv else '' )
				self.url_solicitacao.SetValue( urc )
				self.url_segundavia.SetValue( urv )
				self.token_login.SetValue( tok )

			conn.cls( sql[1] )

	def gravarDadosAPI(self,event):
		
		if self.idf:

			__add = wx.MessageDialog(self,u"Confirme para gravar os dados de conexão...\n"+(" "*150),u"API de conexão",wx.YES_NO)
			if __add.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Fornecedor: cadastro", fil = self.p.cFcFilial, janela = self.painel )
				grv  = False
				erro = ""
				if sql[0]:

					_sv = self.servidor_web.GetValue().split('-')[0].strip()
					_us = self.url_solicitacao.GetValue().strip()
					_uv = self.url_segundavia.GetValue().strip()
					_tl = self.token_login.GetValue().strip()
					_dd = _sv +'|'+ _us +'|'+ _uv +'|'+ _tl

					try:

						g = "UPDATE fornecedor SET fr_parame='" +_dd+ "' WHERE fr_regist='" +self.idf+ "'"
						sql[2].execute( g )
						sql[1].commit()
						grv = True
						
					except Exception as erro:

						if type( erro ) !=unicode:	erro = str( erro )
						grv = False
					
					conn.cls( sql[1] )
					if   grv:	self.Destroy()
					elif not grv and erro:	alertas.dia(self,"{ Sistema não gravou os dados }\n\n"+ erro + "\n"+ (" "*150),"API de conexão")
				
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#5C84AC") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Dados para conexão com a API do serviço", 2, 240, 90)

			
class edicaofr(wx.Frame):

	cadastro = ''
	codigofr = ''
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.f = formasPagamentos()
		self.c = numeracao()
		self.r = []
		self.p.Disable()
		self.cFeFilial = self.p.cFcFilial
		self.l = [""]
		
		self.T  = False
		self.ir = ""
		mkn = wx.lib.masked.NumCtrl
		
		wx.Frame.__init__(self, parent, id, '{ Fornecedor } Alterção-Inclusão', size=(708,560), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		self.Bind(wx.EVT_KEY_UP, self.teclas)

		#-----------------: Buscar dados do fornecedor
		conn = sqldb()
		sql  = conn.dbc("Cadastro de fornecedores", fil = self.cFeFilial, janela = self.painel )

		sb.mstatus("Cadatro de Fornecedores",0)
		if self.cadastro != '':
	
			if sql[0] == False:	self.voltar(wx.EVT_BUTTON)
			if sql[0] == True:

				"""  Relacao das unidades de manejo florestal  """
				self.relacao_unidades = [] if not sql[2].execute("SELECT fg_prin FROM grupofab WHERE fg_cdpd='A'") else [ str(i[0]) for i in sql[2].fetchall()]
				
				if sql[2].execute("DESC fornecedor") != 0:

					_ordem  = 0
					_campos = sql[2].fetchall()

					#-------: Alteracao
					if self.cadastro == 300:

						_reTorn = "SELECT * FROM fornecedor WHERE fr_regist='"+str(self.codigofr)+"'"
						reTorno = sql[2].execute(_reTorn)
						_result = sql[2].fetchall()
					
						for _field in _result:pass
					
					else:	reTorno = 1

					for i in _campos:
						
						#-----: Alteração
						if self.cadastro == 300:	_conteudo = _field[_ordem]
						
						#-----: Inclusão
						else:

							__variavel1 = i[1]
							__variavel2 = __variavel1[0:7]
									
							if   __variavel2 == 'varchar' or __variavel2 == 'text':	_conteudo = ''
							elif __variavel2 == 'date':	_conteudo = '0000-00-00'
							else:	_conteudo = 0

						exec "%s=_conteudo" % ('self.'+i[0])
						_ordem+=1

				""" Relacionar Representantes """
				prepres = "SELECT fr_regist,fr_nomefo FROM fornecedor WHERE fr_tipofi='5'"
				if sql[2].execute( prepres ) !=0:

					rrepres = sql[2].fetchall()
					indicer = 0
					for r in rrepres:
						
						self.r.append( str( r[0] ).zfill(8)+"-"+str( r[1] ) )

						""" Pega a Referencia do Representante """
						if self.fr_repres !=None and self.fr_repres !="" and self.fr_repres.split("-")[0] == str( r[0] ).zfill(8):	self.ir = indicer
							
						indicer +=1
			
				conn.cls(sql[1])
				
				if self.fr_tipofi == "5":	self.T = True
				
		#----------------: Fim de Busca
		EmiTirBoleto = self.fr_boleto
		self.Tipof   = login.SForne
		self.docForn = self.fr_docume

		wx.StaticText(self.painel,-1,"Código",         pos=(18, 5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CPF-CNPJ",       pos=(113,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Insc.Estadual",  pos=(228,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Insc.Municipal", pos=(345,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CNAE",           pos=(463,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CRT",            pos=(580,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Cadastramento",  pos=(615,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Fantasia",                pos=(18, 55)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição do fornecedor", pos=(228,55)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Endereço",      pos=(20, 115)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Numero",        pos=(410,115)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Complemento",   pos=(488,115)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"C E P",         pos=(625,115)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Duplo Click",   pos=(655,120)).SetFont(wx.Font(6, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Pesquisa\nCEP", pos=(660,163)).SetFont(wx.Font(6, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Bairro",      pos=(20, 160)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Cidade",      pos=(215,160)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"U F",         pos=(410,160)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Código do Municipio", pos=(488,160)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Telefone {1}",        pos=(20, 205)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Telefone {2}",        pos=(20, 245)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome e Informações dos Contatos", pos=(212, 203)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Representante",       pos=(212,260)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Web-Service",         pos=(18, 315)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tipo de Fornecedor",  pos=(18, 360)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Emails ( Clientes, Contatos )", pos=(283, 315)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Nº Banco", pos=(18, 420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Agência",  pos=(83, 420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Conta Corrente",  pos=(168, 420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Convenio", pos=(280, 420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Especie",  pos=(393, 420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Carteira", pos=(458, 420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Plano de Contas",   pos=(512,420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Placa Veículo",  pos=(20, 468)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tipo de Veículo",   pos=(115,468)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome do Motorista", pos=(273,468)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Carga KG", pos=(539,468)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Comprimento MT", pos=(623,468)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Unidade(s) de manejo do fornecedor", pos=(18,512)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Relação das unidades de manejo", pos=(368,512)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Informacoes da consulta do CPF-CNPJ """
		self.vi = wx.StaticText(self.painel,-1,"", pos=(113,43))
		self.vi.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vi.SetForegroundColour('#B64949')

		""" Formatar data de cadastramento """
		dTc = "0000-00-00"
		if self.fr_dtcada !="0000-00-00" and self.fr_dtcada:	dTc = format(self.fr_dtcada,'%d-%m-%Y')
		self.documento_anterior = self.fr_docume
		
		self.fr_regist = wx.TextCtrl(self.painel, -1, value=str(self.fr_regist), pos=(15, 20), size=(90, 22),style = wx.TE_READONLY)
		self.fr_docume = wx.TextCtrl(self.painel,101, value=str(self.fr_docume), pos=(110,20), size=(110,22))
		self.fr_insces = wx.TextCtrl(self.painel, -1, value=str(self.fr_insces), pos=(225,20), size=(110,22))
		self.fr_inscmu = wx.TextCtrl(self.painel, -1, value=str(self.fr_inscmu), pos=(342,20), size=(110,22))
		self.fr_incnae = wx.TextCtrl(self.painel, -1, value=str(self.fr_incnae), pos=(460,20), size=(110,22))
		self.fr_inscrt = wx.TextCtrl(self.painel, -1, value=str(self.fr_inscrt), pos=(577,20), size=(30,22))
		self.fr_dtcada = wx.TextCtrl(self.painel, -1, value=str(dTc),            pos=(613,20), size=(90,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.fr_fantas = wx.TextCtrl(self.painel, -1, value=str(self.fr_fantas), pos=(15, 70), size=(202,22))
		self.fr_nomefo = wx.TextCtrl(self.painel, -1, value=str(self.fr_nomefo), pos=(225,70), size=(478,22))

		self.fr_endere = wx.TextCtrl(self.painel, -1,  value=str(self.fr_endere), pos=(15, 130), size=(380,22))
		self.fr_numero = wx.TextCtrl(self.painel, -1,  value=str(self.fr_numero), pos=(405,130), size=(70,22))
		self.fr_comple = wx.TextCtrl(self.painel, -1,  value=str(self.fr_comple), pos=(485,130), size=(127,22))
		self.fr_cepfor = wx.TextCtrl(self.painel, -1,  value=str(self.fr_cepfor), pos=(622,130), size=(81,22))
		self.fr_bairro = wx.TextCtrl(self.painel, -1,  value=str(self.fr_bairro), pos=(15, 175), size=(185,22))
		self.fr_cidade = wx.TextCtrl(self.painel, -1,  value=str(self.fr_cidade), pos=(210,175), size=(185,22))
		self.fr_estado = wx.TextCtrl(self.painel, -1,  value=str(self.fr_estado), pos=(405,175), size=(40,22))
		self.fr_cmunuc = wx.TextCtrl(self.painel, 600, value=str(self.fr_cmunuc), pos=(485,175), size=(127,22))
		self.fr_telef1 = wx.TextCtrl(self.painel, -1,  value=str(self.fr_telef1), pos=(15, 220), size=(185,22))
		self.fr_telef2 = wx.TextCtrl(self.painel, -1,  value=str(self.fr_telef2), pos=(15, 260), size=(185,22))
		
		self.fr_contas = wx.TextCtrl(self.painel, -1,  value=str(self.fr_contas), pos=(210,215), size=(490,43), style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.fr_contas.SetBackgroundColour('#7F7F7F')
		self.fr_contas.SetForegroundColour('#EFEF8A')
		self.fr_contas.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.fr_repres = wx.ComboBox(self.painel, -1,'', pos=(208,271),size=(495,30), choices = self.r, style=wx.CB_READONLY)
		if  self.T == True:	self.fr_repres.Enable( False )
		if self.ir !="":	self.fr_repres.SetValue( self.r[ self.ir ] )

		self.fr_emails = wx.TextCtrl(self.painel, -1,  value=str(self.fr_emails), pos=(280,327), size=(422,71), style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.fr_emails.SetBackgroundColour('#E5E5E5')

		self.webservic = wx.ComboBox(self.painel, -1,login.webServL[login.padrscep], pos=(15,327),size=(255,27), choices = login.webServL,style=wx.CB_READONLY)
		self.webservic.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.TipoForne = wx.ComboBox(self.painel, -1,self.Tipof[0], pos=(15,372),size=(255,27), choices = self.Tipof,style=wx.CB_READONLY)
		self.TipoForne.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.fr_bancof = wx.TextCtrl(self.painel, -1, value=str(self.fr_bancof), pos=(15, 432), size=(50 ,22))
		self.fr_agenci = wx.TextCtrl(self.painel, -1, value=str(self.fr_agenci), pos=(80, 432), size=(70, 22))
		self.fr_contac = wx.TextCtrl(self.painel, -1, value=str(self.fr_contac), pos=(165,432), size=(100,22))
		self.fr_conven = wx.TextCtrl(self.painel, -1, value=str(self.fr_conven), pos=(277,432), size=(100,22))
		self.fr_especi = wx.TextCtrl(self.painel, -1, value=str(self.fr_especi), pos=(390,432), size=(50, 22))
		self.fr_cartei = wx.TextCtrl(self.painel, -1, value=str(self.fr_cartei), pos=(455,432), size=(50, 22))
		self.fr_planoc = wx.TextCtrl(self.painel, -1, value=str(self.fr_planoc), pos=(512,432), size=(90, 22), style = wx.TE_READONLY)
		self.fr_boleto = wx.CheckBox(self.painel, -1, "Emitir Boleto", pos=(613,438))
		if EmiTirBoleto == "T":	self.fr_boleto.SetValue(True)
		else:	self.fr_boleto.SetValue(False)

		self.fr_vplaca = wx.TextCtrl(self.painel, -1, value=str(self.fr_vplaca), pos=(15, 480), size=(90, 20))
		self.fr_vtipov = wx.TextCtrl(self.painel, -1, value=str(self.fr_vtipov), pos=(112,480), size=(150,20))
		self.fr_motori = wx.TextCtrl(self.painel, -1, value=str(self.fr_motori), pos=(270,480), size=(260,20))

		self.fr_cargac = mkn(self.painel, id = 303, value = str( self.fr_cargac ), pos=(536,480),style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 4, fractionWidth = 3, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.fr_compri = mkn(self.painel, id = 303, value = str( self.fr_compri ), pos=(620,480),style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 4, fractionWidth = 3, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.fr_cargac.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_compri.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		if self.fr_manejo:

			for i in self.fr_manejo.split('|'):

				if i:	self.l.append( i )

		self.unidademj = wx.ComboBox(self.painel, -1, self.fr_unpadr,  pos=(15, 524),size=(300,27), choices = self.l,style=wx.CB_READONLY)
		self.relacaouf = wx.ComboBox(self.painel, -1,'', pos=(365,524),size=(300,27), choices = self.relacao_unidades, style=wx.CB_READONLY)

		self.fr_regist.Disable()
		self.fr_docume.SetMaxLength(14)
		self.fr_insces.SetMaxLength(14)
		self.fr_inscmu.SetMaxLength(15)
		self.fr_incnae.SetMaxLength(7)
		self.fr_inscrt.SetMaxLength(1)
		self.fr_fantas.SetMaxLength(60)
		self.fr_nomefo.SetMaxLength(120)
		self.fr_endere.SetMaxLength(60)
		self.fr_numero.SetMaxLength(10)
		self.fr_comple.SetMaxLength(20)
		self.fr_cepfor.SetMaxLength(8)
		self.fr_bairro.SetMaxLength(20)
		self.fr_cidade.SetMaxLength(20)
		self.fr_estado.SetMaxLength(2)
		self.fr_cmunuc.SetMaxLength(7)
		self.fr_bancof.SetMaxLength(3)	
		self.fr_agenci.SetMaxLength(6)
		self.fr_contac.SetMaxLength(11)
		self.fr_telef1.SetMaxLength(20)
		self.fr_telef2.SetMaxLength(20)
		self.fr_conven.SetMaxLength(10)
		self.fr_especi.SetMaxLength(5)
		self.fr_cartei.SetMaxLength(5)
		self.fr_planoc.SetMaxLength(20)

		self.fr_vplaca.SetMaxLength(10)
		self.fr_vtipov.SetMaxLength(60)
		self.fr_motori.SetMaxLength(60)

		self.fr_regist.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_regist.SetBackgroundColour('#E5E5E5')
		
		self.fr_docume.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_docume.SetBackgroundColour('#E5E5E5')
		
		self.fr_insces.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_insces.SetBackgroundColour('#E5E5E5')

		self.fr_inscmu.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_inscmu.SetBackgroundColour('#E5E5E5')

		self.fr_incnae.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_incnae.SetBackgroundColour('#E5E5E5')

		self.fr_inscrt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_inscrt.SetBackgroundColour('#E5E5E5')

		self.fr_dtcada.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_dtcada.SetBackgroundColour('#E5E5E5')

		self.fr_fantas.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_fantas.SetBackgroundColour('#E5E5E5')

		self.fr_nomefo.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_nomefo.SetBackgroundColour('#E5E5E5')

		self.fr_endere.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_endere.SetBackgroundColour('#E5E5E5')

		self.fr_numero.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_numero.SetBackgroundColour('#E5E5E5')

		self.fr_comple.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_comple.SetBackgroundColour('#E5E5E5')

		self.fr_cepfor.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_cepfor.SetBackgroundColour('#E5E5E5')

		self.fr_bairro.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_bairro.SetBackgroundColour('#E5E5E5')

		self.fr_cidade.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_cidade.SetBackgroundColour('#E5E5E5')

		self.fr_estado.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_estado.SetBackgroundColour('#E5E5E5')

		self.fr_cmunuc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_cmunuc.SetBackgroundColour('#E5E5E5')

		self.fr_bancof.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_bancof.SetBackgroundColour('#E5E5E5')

		self.fr_agenci.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_agenci.SetBackgroundColour('#E5E5E5')

		self.fr_contac.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_contac.SetBackgroundColour('#E5E5E5')

		self.fr_telef1.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_telef1.SetBackgroundColour('#E5E5E5')

		self.fr_telef2.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_telef2.SetBackgroundColour('#E5E5E5')

		self.fr_conven.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_conven.SetBackgroundColour('#E5E5E5')

		self.fr_especi.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_especi.SetBackgroundColour('#E5E5E5')

		self.fr_cartei.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_cartei.SetBackgroundColour('#E5E5E5')

		self.fr_planoc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_planoc.SetBackgroundColour('#E5E5E5')

		self.fr_vplaca.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_vplaca.SetBackgroundColour('#BFBFBF')

		self.fr_vtipov.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_vtipov.SetBackgroundColour('#BFBFBF')

		self.fr_motori.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fr_motori.SetBackgroundColour('#BFBFBF')

		self.fr_boleto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		pescep = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/web.png",    wx.BITMAP_TYPE_ANY),  pos=(622,160), size=(32,26))				
		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/volta16.png", wx.BITMAP_TYPE_ANY), pos=(613,410), size=(40,27))				
		gravar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/save16.png",  wx.BITMAP_TYPE_ANY), pos=(663,410), size=(40,27))

		""" Unidades de manejo """
		un_apagar = wx.BitmapButton(self.painel, 600, wx.Bitmap("imagens/simapaga16.png", wx.BITMAP_TYPE_ANY), pos=(320,523), size=(34,27))
		un_inclui = wx.BitmapButton(self.painel, 601, wx.Bitmap("imagens/simadd20.png",   wx.BITMAP_TYPE_ANY), pos=(669,523), size=(34,27))

		if   self.cadastro == 300:	self.fr_insces.SetFocus()
		elif self.cadastro != 300:	self.fr_docume.SetFocus()
		
		"""  Habilita Alteracao do CNPJ se Estiver Vazio   """
		if self.fr_docume.GetValue().strip() == '':	self.fr_docume.Enable( True )
		if self.fr_docume.GetValue().strip() == '':	self.fr_docume.SetFocus()
			
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		pescep.Bind(wx.EVT_BUTTON, self.pesqcep)
		gravar.Bind(wx.EVT_BUTTON, self.gravarforncedor)
		un_apagar.Bind(wx.EVT_BUTTON, self.adicionarApagarManejo)
		un_inclui.Bind(wx.EVT_BUTTON, self.adicionarApagarManejo)

		self.fr_cepfor.Bind(wx.EVT_LEFT_DCLICK, self.pesqcep)
		self.fr_cmunuc.Bind(wx.EVT_LEFT_DCLICK, self.cmunicipio)
		self.TipoForne.Bind(wx.EVT_COMBOBOX, self.evenToCombo)
		self.fr_planoc.Bind(wx.EVT_LEFT_DCLICK, self.plnContas)

		if self.fr_tipofi == '1':	self.TipoForne.SetValue( self.Tipof[0] )
		if self.fr_tipofi == '2':	self.TipoForne.SetValue( self.Tipof[1] )
		if self.fr_tipofi == '3':	self.TipoForne.SetValue( self.Tipof[2] )
		if self.fr_tipofi == '4':	self.TipoForne.SetValue( self.Tipof[3] )
		if self.fr_tipofi == '5':	self.TipoForne.SetValue( self.Tipof[4] )
		if self.fr_tipofi == '6':	self.TipoForne.SetValue( self.Tipof[5] )
		
		self.evenToCombo(wx.EVT_BUTTON)

		if self.cadastro ==300 and self.fr_tipofi !='4':
			
			self.fr_vplaca.Enable( False )
			self.fr_vtipov.Enable( False )
			self.fr_motori.Enable( False )

			self.fr_cargac.Enable( False )
			self.fr_compri.Enable( False )

	def adicionarApagarManejo(self,event):

		if self.l:

			existir = False
			for e in self.l:
				
				if e == self.relacaouf.GetValue() and event.GetId() == 601:	existir = True

			if existir:	alertas.dia(self,"Ja consta na relação...\n"+(" "*100),"Fornecedor: Unidade de manejo")
			if not existir:
				
				listar = self.l
				self.l = [""]
				if event.GetId() == 601:	self.l.append( self.relacaouf.GetValue() )

				for i in listar:

					if i and event.GetId() == 600 and i != self.unidademj.GetValue():	self.l.append( i ) 
					if i and event.GetId() == 601:	self.l.append( i )

		else:
			if event.GetId() == 601:	lista.append( self.relacaouf.GetValue() )
		self.unidademj.SetItems( self.l )
		self.unidademj.SetValue( self.l[1] if len( self.l ) >= 2 else self.l[0] )

	def evenToCombo(self,event):

		ena = False
		if self.TipoForne.GetValue()[:1] == "3":	ena = True

		self.fr_bancof.Enable(ena)
		self.fr_agenci.Enable(ena)
		self.fr_contac.Enable(ena)

	def cmunicipio(self,event):

		mun_frame=CodigoMunicipio(parent=self,id=event.GetId())
		mun_frame.Centre()
		mun_frame.Show()

	def MunicipioCodigo(self,_codigo,_id):	self.fr_cmunuc.SetValue(_codigo)
	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()

	def pesqcep(self,event):

		cep = self.fr_cepfor.GetValue()
		if cep == '':
			alertas.dia(self.painel,u"Campo do CEP, estar vazio !!\n"+(' '*80),"Forncedores: Pesquisa do cep")
			return

		conn = sqldb()
		sql  = conn.dbc("Fornecedores, Forncedores CEPs", fil = self.cFeFilial, janela = self.painel )

		if sql[0] == True:

			SeuCep = self.c.cep(cep,self.webservic.GetValue(),self.painel)
			if SeuCep !=None:

				self.fr_endere.SetValue(SeuCep[0])
				self.fr_bairro.SetValue(SeuCep[1])
				self.fr_cidade.SetValue(SeuCep[2])
				self.fr_estado.SetValue(SeuCep[3])
				self.fr_cmunuc.SetValue(SeuCep[4])
					
			conn.cls(sql[1])

	def gravarforncedor(self,event):

		_docu = self.fr_docume.GetValue()
		_nome = self.fr_nomefo.GetValue()
		if _nome == '':
			alertas.dia(self.painel,u"Nome do forncedor vazio!!\n"+(' '*80),"Fornecedores: Alterar-Incluir")
			return
		
		elif len(_nome) < 5:
			alertas.dia(self.painel,u"Nome do forncedor minimo 5 caracteres!!\n"+(' '*80),"Fornecedores: Alterar-Incluir")
			return

		conTinuar = False
		if _docu == '':	conTinuar = True
		if acs.acsm("902",False) == True:	conTinuar = False
		
		if conTinuar == True:
			
			alertas.dia(self.painel,u"CPF-CNPJ do forncedor vazio!!\n"+(' '*80),"Fornecedores: Alterar-Incluir")
			return

		if _docu != '' and self.c.cpfcnpj( str(self.fr_docume.GetValue() ) )[0] == False:

			alertas.dia(self.painel,u"CPF-CNPJ do forncedor Invalido!!\n"+(' '*80),"Fornecedores: Alterar-Incluir")
			return

		#---------: Gravacao
		conn = sqldb()
		sql  = conn.dbc("Fornecedores, Gravando", fil = self.cFeFilial, janela = self.painel )

		if sql[0] == True:
			
			#------------: Inclusão
			_doc = str(self.fr_docume.GetValue())
			_ies = str(self.fr_insces.GetValue())
			_imu = str(self.fr_inscmu.GetValue())
			_cna = str(self.fr_incnae.GetValue())
			_crt = str(self.fr_inscrt.GetValue())
			_fan = self.fr_fantas.GetValue().upper()
			_nom = self.fr_nomefo.GetValue().upper()
			_end = self.fr_endere.GetValue().upper()
			_num = self.fr_numero.GetValue().upper()
			_cmp = self.fr_comple.GetValue().upper()
			_cep = str(self.fr_cepfor.GetValue())
			_bai = self.fr_bairro.GetValue().upper()
			_cid = self.fr_cidade.GetValue().upper()
			_est = self.fr_estado.GetValue().upper()
			_ibg = str(self.fr_cmunuc.GetValue())
			_ema = self.fr_emails.GetValue()
			_bnd = str(self.fr_bancof.GetValue())
			_age = str(self.fr_agenci.GetValue())
			_ncc = str(self.fr_contac.GetValue())
			_nT1 = str(self.fr_telef1.GetValue())
			_nT2 = str(self.fr_telef2.GetValue())
			_con = self.fr_contas.GetValue()
			_cnv = str(self.fr_conven.GetValue())
			_esp = str(self.fr_especi.GetValue())
			_car = str(self.fr_cartei.GetValue())
			_pla = str(self.fr_planoc.GetValue())
			_rep = str(self.fr_repres.GetValue())
			_vpl = self.fr_vplaca.GetValue()
			_vTp = self.fr_vtipov.GetValue()
			_moT = self.fr_motori.GetValue()
			_cag = str(self.fr_cargac.GetValue())
			_com = str(self.fr_compri.GetValue())
			
			_dta = datetime.datetime.now().strftime("%Y/%m/%d")
			_grv = False
			mane = ""
			
			if _doc and self.documento_anterior != _doc:

				achar_documento = sql[2].execute("SELECT fr_docume, fr_nomefo FROM fornecedor WHERE fr_docume='"+str( _doc )+"'")
				if achar_documento:

					relacao_docs = ""
					resulta_docs = sql[2].fetchall()
					for rdoc in resulta_docs:

						relacao_docs +=rdoc[0]+' '+rdoc[1]+'\n'

					if self.TipoForne.GetValue().split('-')[0] == "3":	permitir = "\n\nAutorizado a inclusão em duplicidade epanas p/instituição bancaria!!"
					else:	permitir = ''
					alertas.dia( self, "Documento: "+str( _doc )+'\n\n'+relacao_docs+permitir+'\n'+(' '*140),"Cadastro de fornecedors")
					if not permitir:

						conn.cls( sql[1] )
						return
			
			if self.l:
				
				for x in self.l:
					
					if type( x ) == str:	x = x.decode("UTF-8")
					if x:	mane +=x +'|'
			
			try:
				
				_TPF = self.TipoForne.GetValue()[:1]
				_BOL = str(self.fr_boleto.GetValue())[:1]
				if _TPF != "3":	_bnd = _age = _ncc = ''
				
				if self.cadastro != 300:
					
					gravar = "INSERT INTO fornecedor (fr_docume,fr_insces,fr_inscmu,fr_incnae,fr_inscrt,fr_nomefo,\
							fr_fantas,fr_endere,fr_numero,fr_comple,fr_bairro,fr_cidade,\
							fr_cepfor,fr_estado,fr_cmunuc,fr_telef1,fr_telef2,fr_telef3,\
							fr_fosite,fr_emails,fr_contas,fr_dtcada,fr_idfila,fr_tipofi,\
							fr_bancof,fr_agenci,fr_contac,fr_conven,fr_especi,fr_cartei,\
							fr_boleto,fr_planoc,fr_repres,fr_vplaca,fr_vtipov,fr_motori,fr_manejo,fr_unpadr,\
							fr_cargac,fr_compri)\
							VALUES(%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,%s,%s,\
							%s,%s)"
							
					sql[2].execute(gravar,(_doc,_ies,_imu,_cna,_crt,_nom,_fan,_end,_num,_cmp,_bai,_cid,_cep,_est,_ibg,\
					_nT1,_nT2,'','',_ema,_con,_dta,self.cFeFilial,_TPF,_bnd,_age,_ncc,_cnv,_esp,_car,_BOL,_pla,_rep,_vpl,_vTp,_moT,mane,self.unidademj.GetValue(),\
					_cag, _com ) )
					
					sql[1].commit()
					_grv = True
							
				elif self.cadastro == 300:

					gravar = "UPDATE fornecedor SET fr_insces=%s,fr_inscmu=%s,\
							fr_incnae=%s,fr_inscrt=%s,\
							fr_nomefo=%s,fr_fantas=%s,\
							fr_endere=%s,fr_numero=%s,\
							fr_comple=%s,fr_bairro=%s,\
							fr_cidade=%s,fr_cepfor=%s,\
							fr_estado=%s,fr_cmunuc=%s,\
							fr_telef1=%s,fr_telef2=%s,\
							fr_telef3=%s,fr_fosite=%s,\
							fr_emails=%s,fr_contas=%s,\
							fr_tipofi=%s,fr_bancof=%s,\
							fr_agenci=%s,fr_contac=%s,\
							fr_conven=%s,fr_especi=%s,\
							fr_cartei=%s,fr_boleto=%s,\
							fr_planoc=%s,fr_repres=%s,\
							fr_vplaca=%s,fr_vtipov=%s,\
							fr_motori=%s,fr_manejo=%s,fr_unpadr=%s,fr_cargac=%s,fr_compri=%s WHERE fr_regist=%s"

					"""   Altera o CPF-CNPJ se Estiver vazio   """
					gravas = "UPDATE fornecedor SET fr_docume=%s,fr_insces=%s,fr_inscmu=%s,\
							fr_incnae=%s,fr_inscrt=%s,\
							fr_nomefo=%s,fr_fantas=%s,\
							fr_endere=%s,fr_numero=%s,\
							fr_comple=%s,fr_bairro=%s,\
							fr_cidade=%s,fr_cepfor=%s,\
							fr_estado=%s,fr_cmunuc=%s,\
							fr_telef1=%s,fr_telef2=%s,\
							fr_telef3=%s,fr_fosite=%s,\
							fr_emails=%s,fr_contas=%s,\
							fr_tipofi=%s,fr_bancof=%s,\
							fr_agenci=%s,fr_contac=%s,\
							fr_conven=%s,fr_especi=%s,\
							fr_cartei=%s,fr_boleto=%s,\
							fr_planoc=%s,fr_repres=%s,\
							fr_vplaca=%s,fr_vtipov=%s,\
							fr_motori=%s,fr_manejo=%s,fr_unpadr=%s,fr_cargac=%s,fr_compri=%s WHERE fr_regist=%s"

					"""   Altera o CPF-CNPJ se Estiver vazio   """
					alterar_docs = False
					if _doc !="" and self.docForn == "":	alterar_docs = True
					if _doc !="" and self.docForn !="" and _doc != self.docForn:	alterar_docs = True 

					if alterar_docs:

						sql[2].execute(gravas,(_doc,_ies,_imu,_cna,_crt,_nom,_fan,_end,_num,_cmp,_bai,_cid,_cep,_est,_ibg,\
						_nT1,_nT2,'','',_ema,_con,_TPF,_bnd,_age,_ncc,_cnv,_esp,_car,_BOL,_pla,_rep,_vpl,_vTp,_moT,mane,self.unidademj.GetValue(), _cag, _com, self.codigofr))

					else:
						sql[2].execute(gravar,(_ies,_imu,_cna,_crt,_nom,_fan,_end,_num,_cmp,_bai,_cid,_cep,_est,_ibg,\
						_nT1,_nT2,'','',_ema,_con,_TPF,_bnd,_age,_ncc,_cnv,_esp,_car,_BOL,_pla,_rep,_vpl,_vTp,_moT,mane,self.unidademj.GetValue(), _cag, _com, self.codigofr))

					sql[1].commit()
					_grv = True

			except Exception, _reTornos:
					
				sql[1].rollback()
				alertas.dia(self.painel,u"ERRO!! Forncedores Inclusão !!\n \nRetorno: "+str(_reTornos),"Retorno")	

			conn.cls(sql[1])

		if   _grv == True and self.cadastro != 300:	alertas.dia(self.painel,u"Fornecedores: inclusão ok!!\n"+(' '*80),"Fornecedores")
		elif _grv == True and self.cadastro == 300:	alertas.dia(self.painel,u"Fornecedores: alteração ok!!\n"+(' '*80),"Fornecedores")
		if   _grv == True:
			
			self.p.selecionar(wx.EVT_BUTTON)
			self.sair(wx.EVT_BUTTON)
			
	def teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()

		if keycode == wx.WXK_ESCAPE:	self.sair(wx.EVT_BUTTON)
		if controle !=None and controle.GetId() == 101:

			if len(self.fr_docume.GetValue()) !=0 and self.fr_docume.GetValue().isdigit() == False:

				self.vi.SetLabel("Digito Invalido")
				event.Skip()
				return

			elif self.fr_docume.GetValue() == "":	self.vi.SetLabel("")
				
			if len(self.fr_docume.GetValue()) == 11 or len(self.fr_docume.GetValue()) == 14:

				conn = sqldb()
				sql  = conn.dbc("Fornecedores->Procura CPF-CNPJ", fil = self.cFeFilial, janela = self.painel )

				if sql[0] == True:

					_achei = "SELECT fr_docume FROM fornecedor WHERE fr_docume='"+str(self.fr_docume.GetValue())+"'"
					achei1 = sql[2].execute(_achei)

					if achei1 !=0:
						
						self.vi.SetLabel("{ Cadastrado }")
						if self.TipoForne.GetValue().split('-')[0] == "3":	self.vi.SetLabel("{ Duplicidade }")
						if self.TipoForne.GetValue().split('-')[0] != "3":
							
							if   self.TipoForne.GetValue()[:1] !="3":	self.fr_docume.SetValue('')
							elif self.TipoForne.GetValue()[:1] =="3":	self.fr_docume.SetValue("")

					elif achei1 == 0:

						_valida = self.c.cpfcnpj(str(self.fr_docume.GetValue()))
						self.vi.SetLabel("")

						if _valida[0] == False:	self.vi.SetLabel("CPF-CNPJ Invalido")

					conn.cls(sql[1])

	def plnContas(self,event):
		
		PlanoContas.TipoAcesso = "consulta"
		forn_frame=PlanoContas(parent=self,id=-1)
		forn_frame.Centre()
		forn_frame.Show()

	def AtualizaPlContas(self,_nconta):	self.fr_planoc.SetValue(_nconta)	
	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#906619") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("FORNECEDORES - Incluir Alterar", 0, 297, 90)

		dc.SetTextForeground("#FFA500") 	
		if self.cadastro ==  300:	dc.DrawRotatedText("{ Alteração }", 0, 100, 90)
		else:	dc.DrawRotatedText("{ Inclusão }", 0, 100, 90)

		dc.SetTextForeground("#1764AF") 	
		dc.DrawRotatedText("Bancos", 0, 361, 90)

		dc.SetTextForeground("#638663") 	
		dc.DrawRotatedText("Extração", 0, 553, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,  1,  693, 99,  3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12,  104,693, 202, 3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12,  310,693, 91,  3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12,  408,693, 55,  3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12,  465,693, 40,  3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12,  509,693, 46,  3) #-->[ Lykos ]


class edicaonf(wx.Frame):
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.p.Disable()

		wx.Frame.__init__(self, parent, id, '{ Compras } Dados da NFe', size=(407,97), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		wx.StaticText(self.painel,-1,"Nº NFe",        pos=(15, 10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Emissão",       pos=(93, 10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Entrada/Saida", pos=(218,10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Serie",         pos=(340,10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Chave",      pos=(15, 50)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nfenume = wx.TextCtrl(self.painel,-1,str(self.p.nfenume.GetValue()), pos=(12,25), size=(60,22),style = wx.ALIGN_RIGHT)
		self.nfenume.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nfenume.SetBackgroundColour('#E5E5E5')

		self.emissao = wx.DatePickerCtrl(self.painel,-1, pos=(90, 25), size=(110,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.entrada = wx.DatePickerCtrl(self.painel,-1, pos=(215,25), size=(110,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

		self.nrserie = wx.TextCtrl(self.painel,-1, str(self.p.nrserie.GetValue()), pos=(335,25), size=(35,22),style = wx.ALIGN_RIGHT)
		self.nrserie.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nrserie.SetBackgroundColour('#E5E5E5')

		self.chaveac = wx.TextCtrl(self.painel,-1,str(self.p.chaveac.GetValue()), pos=(12,65), size=(358,22))
		self.chaveac.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.chaveac.SetBackgroundColour('#E5E5E5')

		self.nfenume.SetMaxLength(9)
		self.chaveac.SetMaxLength(44)
		self.nrserie.SetMaxLength(3)

		importa = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/importp.png", wx.BITMAP_TYPE_ANY), pos=(376,16), size=(28,30))
		voltar  = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/volta16.png", wx.BITMAP_TYPE_ANY), pos=(376,50), size=(28,30))
		voltar. Bind(wx.EVT_BUTTON, self.sair)
		importa.Bind(wx.EVT_BUTTON, self.exportar)

	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()
		
	def exportar(self,event):

		dTe = str( datetime.datetime.strptime(self.emissao.GetValue().FormatDate(),'%d-%m-%Y').date() )
		dTs = str( datetime.datetime.strptime(self.entrada.GetValue().FormatDate(),'%d-%m-%Y').date() )
		
		self.p.nfenume.SetValue(self.nfenume.GetValue())
		self.p.nrserie.SetValue(self.nrserie.GetValue())
		self.p.chaveac.SetValue(self.chaveac.GetValue())
		self.p.emissao.SetValue(dTe)
		self.p.entrasa.SetValue(dTs)
		
		self.sair(wx.EVT_BUTTON)

	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#906619") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Dados da NFE", 0, 92, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(10,  2,363, 90,   3) #-->[ Lykos ]


#---: Vincular codigo do produto ao produto do xml		
class vinculacdxml(wx.Frame):

	produtos = {}
	registro = 0
	rlFilial = ""
	modulo_chamador = 1

	def __init__(self, parent,id):
		
		self.p = parent
		self.v = VincularProdutos()
		self.r = 0
		self.q = "0.0000"
		
		wx.Frame.__init__(self, parent, id, '{ Produto } Vincular código ['+str( self.rlFilial )+']', size=(700,332), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.cadProdutos = PRListCtrl(self.painel, 300 ,pos=(10,60), size=(685,203),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.cadProdutos.SetBackgroundColour('#BDD1D9')
		self.cadProdutos.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		
		self.Bind(wx.EVT_ENTER_WINDOW,self.AtualizaProduto)
		self.Bind(wx.EVT_LEAVE_WINDOW,self.AtualizaProduto)
		self.Bind(wx.EVT_KEY_UP, self.Teclas)
		self.cadProdutos.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passar)

		wx.StaticText(self.painel,-1,"Descrição do Produto: ",  pos=(2, 4)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Referência", pos=(3, 25)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Código Controle Interno",  pos=(163,25)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Referência do Fabricante", pos=(323,25)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Fabricante", pos=(533,25)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Descrição,P:Expressão,F:Fabricante,R:Referência,D:Referencia[*]-Encadeada,I-CdInterno",  pos=(13, 290)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
  
		wx.StaticText(self.painel,-1,"{+}-Vincular",   pos=(380,267)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Estoque Fisico", pos=(450,267)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Estoque de Reserva",  pos=(550,267)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,self.rlFilial,  pos=(648, 295)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.ocorrencias = wx.StaticText(self.painel,-1,"{LISTA}",  pos=(645, 310))
		self.ocorrencias.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial")) 
		self.ocorrencias.SetForegroundColour('#15518B')

		self.coo = wx.TextCtrl(self.painel,302,"",pos=(130,2),size=(567,18))
		self.coo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.coo.SetForegroundColour('#174776')
		self.coo.SetBackgroundColour('#E5E5E5')

		self.ref = wx.TextCtrl(self.painel,-1,"",pos=(0,38),size=(150,20),style=wx.TE_RIGHT)
		self.ref.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.ref.SetForegroundColour('#174776')
		self.ref.SetBackgroundColour('#E5E5E5')

		self.cin = wx.TextCtrl(self.painel,-1,"",pos=(160,38),size=(150,20),style=wx.TE_RIGHT)
		self.cin.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.cin.SetForegroundColour('#174776')
		self.cin.SetBackgroundColour('#E5E5E5')

		self.rfb = wx.TextCtrl(self.painel,-1,"",pos=(320,38),size=(200,20),style=wx.TE_RIGHT)
		self.rfb.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.rfb.SetForegroundColour('#174776')
		self.rfb.SetBackgroundColour('#E5E5E5')

		self.fab = wx.TextCtrl(self.painel,-1,"",pos=(530,38),size=(167,20),style=wx.TE_RIGHT)
		self.fab.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.fab.SetForegroundColour('#174776')
		self.fab.SetBackgroundColour('#E5E5E5')

		self.ffilia = wx.CheckBox(self.painel, 501, "Filtrar Produtos da Filial: { "+str( self.rlFilial ) +" }", pos=(10,265 ))
		self.ffilia.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ffilia.SetForegroundColour('#2865A1')
		
		procura = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(450,295), size=(32,30))
		relerls = wx.BitmapButton(self.painel, 322, wx.Bitmap("imagens/relerpp.png",   wx.BITMAP_TYPE_ANY), pos=(485,295), size=(32,30))
		alterar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/alterarp.png",  wx.BITMAP_TYPE_ANY), pos=(520,295), size=(32,30))				
		exporta = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/importp.png",   wx.BITMAP_TYPE_ANY), pos=(555,295), size=(32,30))
		voltar  = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/volta16.png",   wx.BITMAP_TYPE_ANY), pos=(595,295), size=(32,30))

		self.consultar = wx.TextCtrl(self.painel, 301,   pos=(11,301), size=(420,23),style=wx.TE_PROCESS_ENTER)
		self.consultar.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)

		exporta.Bind(wx.EVT_BUTTON, self.exporTariTem)
		procura.Bind(wx.EVT_BUTTON, self.selecionar)
		relerls.Bind(wx.EVT_BUTTON, self.selecionar)
		alterar.Bind(wx.EVT_BUTTON, self.alTerarProdutos)
		voltar. Bind(wx.EVT_BUTTON, self.sair)
		self.ffilia.Bind(wx.EVT_CHECKBOX, self.selecionar)
	
		self.consultar.SetFocus()

		if self.modulo_chamador == 2 and self.p.descricao.GetValue():	self.consultar.SetValue( self.p.descricao.GetValue() )

	def alTerarProdutos(self,event):

		indice = self.cadProdutos.GetFocusedItem()
		if self.cadProdutos.GetItem(indice,21).GetText() !='':	self.p.editaProdutos( self.cadProdutos.GetItem(indice,21).GetText() )
		
	def AtualizaProduto(self,event):

		if self.modulo_chamador == 1:
			
			indice = self.p.PosicaoAtuale
			self.coo.SetValue(self.p.ListaCMP.GetItem(indice,1).GetText()+"-"+self.p.ListaCMP.GetItem(indice,3).GetText())
			self.q = self.p.ListaCMP.GetItem(indice,4).GetText()

	def sair(self,event):	self.Destroy()

	def selecionar(self,event):

		if self.consultar.GetValue() == '':	return
		
		conn = sqldb()
		sql  = conn.dbc("Produtos: vincular codigo", fil = self.rlFilial, janela = self.painel )

		if sql[0] == True:

			_ds = str( self.consultar.GetValue().upper().split(":")[1] ) if len( self.consultar.GetValue().upper().split(":") ) == 2 else str( self.consultar.GetValue().upper() )
			_lt = str( self.consultar.GetValue().upper().split(":")[0] ) if len( self.consultar.GetValue().upper().split(":") ) == 2 else ""

			_ps = "SELECT * FROM produtos WHERE pd_canc!='4' ORDER BY pd_nome"
			_pb = "SELECT * FROM produtos WHERE pd_canc!='4' ORDER BY pd_nome"

			if   _lt == 'P':	_ps = "SELECT * FROM produtos WHERE pd_nome like '%"+_ds+"%' and pd_canc!='4' ORDER BY pd_nome"
			elif _lt == 'F':	_ps = "SELECT * FROM produtos WHERE pd_fabr like '%"+_ds+"%' and pd_canc!='4' ORDER BY pd_nome"
			elif _lt == 'R':	_ps = "SELECT * FROM produtos WHERE pd_refe like '%"+_ds+"%' and pd_canc!='4' ORDER BY pd_nome"
			elif _lt == 'B':	_ps = "SELECT * FROM produtos WHERE pd_barr like '%"+_ds+"%' and pd_canc!='4' ORDER BY pd_nome"
			elif _lt == 'I':	_ps = "SELECT * FROM produtos WHERE pd_intc like '%"+_ds+"%' and pd_canc!='4' ORDER BY pd_nome"
			elif _lt == 'C':	_ps = "SELECT * FROM produtos WHERE pd_codi like '%"+_ds+"%' and pd_canc!='4' ORDER BY pd_nome"
			elif not _lt and _ds.isdigit():	_ps = "SELECT * FROM produtos WHERE ( pd_codi like '%"+_ds+"%' or pd_intc like '%"+_ds+"%' or pd_refe like '%"+_ds+"%' or pd_barr like '%"+_ds+"%' ) and pd_canc!='4' ORDER BY pd_nome"
			else:

				if not len( self.consultar.GetValue().split("*") ) > 1:	_ps = "SELECT * FROM produtos WHERE pd_nome like '"+_ds+"%' and pd_canc!='4' ORDER BY pd_nome"

			""" Consulta encadeada """
			if len( self.consultar.GetValue().split("*") ) > 1:
				
				_ps = _pb
				for fpq in self.consultar.GetValue().split("*"):
					
					if fpq !='':	_ps = _ps.replace("WHERE","WHERE pd_nome like '%"+str( fpq )+"%' and")

			pLista = sql[2].execute(_ps)
			result = sql[2].fetchall()
				
			vinculacdxml.produtos = {} 
			vinculacdxml.registro = 0   

			_registros = 0
			relacao = {}

			for i in result:

				_psa = True
				_vin = "False"
				_est = _vir = "0.0000"
				_pcf = ""

				""" Verifica se o produto estar vinculao a filial atual """

				if nF.fu( self.rlFilial ) == "T":	esFV = sql[2].execute("SELECT * FROM estoque WHERE ef_codigo='"+str( i[2] )+"'")
				else:	esFV = sql[2].execute("SELECT * FROM estoque WHERE ef_idfili='"+str( self.rlFilial )+"' and ef_codigo='"+str( i[2] )+"'")
				
				if esFV !=0:	
					
					rEsT = sql[2].fetchall()
					_vin = 'True'
					_est = str( rEsT[0][4] )
					_vir = str( rEsT[0][5] )
				
				else:
					
					if self.ffilia.GetValue() == True:	_psa = False

				if _psa == True:
					
					"""  Elimina se for Kit-Conjunto   """

					if i[79] !="T":

						
						if i[90] !=None and i[90] !="":	_pcf = i[90] 
						
						relacao[_registros] = i[2],i[6],i[5],i[3],i[9],i[0],i[21],i[35],i[36],i[37],i[38],i[39],i[29],i[30],i[31],i[32],i[33],i[20],i[28],i[70],i[0],i[5],i[10],i[60]+" - "+i[71],str(i[74]),str(i[75]),str(i[16]),str( _est ),str( _vir ),_vin,_pcf, str( i[68] ),i[93], i[89]
						_registros +=1

			conn.cls(sql[1])

			self.cadProdutos.SetItemCount( _registros )
			vinculacdxml.registro   = _registros
			vinculacdxml.produtos   = relacao 
			PRListCtrl.itemDataMap  = relacao
			PRListCtrl.itemIndexMap = relacao.keys()
			
			self.ocorrencias.SetLabel("{"+str( _registros )+"}")

			if pLista == 0 or event.GetId() != 322:	self.r = 0	

	def Teclas(self,event):
		
		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		if keycode == wx.WXK_ESCAPE:	self.sair(wx.EVT_BUTTON)
		
		if controle !=None:

			if keycode == 9 and controle.GetId() == 300:	self.consultar.SetFocus()
			if keycode == 9 and controle.GetId() == 302:	self.consultar.SetFocus()
			if keycode == 9 and controle.GetId() == 301:	self.cadProdutos.SetFocus()

			#--------: Tecla { + } 
			if keycode == 388:

				if controle.GetId() == 209 or controle.GetId() == 300:	self.exporTariTem(wx.EVT_BUTTON)

			#--------: Tecla { - } 
			if keycode == 390:

				if controle.GetId() == 209 or controle.GetId() == 300:	self.incremenTar()

	def incremenTar(self):

		self.p.incremenTa()
				
		self.p.ListaCMP.Select(self.p.PosicaoAtuale)
		self.p.ListaCMP.SetFocus()
		
		self.AtualizaProduto(wx.EVT_BUTTON)
		
	def exporTariTem(self,event):

		nRegis = self.cadProdutos.GetItemCount()
		indice = self.cadProdutos.GetFocusedItem()

		if   self.cadProdutos.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista de produtos estar vazio!!\n"+(" "*100),"Compras: Vincular produtos ao XML")
		elif self.cadProdutos.GetItem(indice, 29 ).GetText().upper() == "FALSE":	alertas.dia(self.painel,"Filial: { "+str( self.rlFilial )+" }\n\nEsse produto não estar vinculado a filial atual!!\n"+(' '*110),"Compras XML: Vincular Produtos") 
			
		else:

			Posind = self.p.PosicaoAtuale
			
			liProdu = []
			coluna = self.cadProdutos.GetColumnCount()
			for i in range( coluna ):

				liProdu.append( self.cadProdutos.GetItem(indice,i).GetText() )

			if self.modulo_chamador == 2:	self.p.gravarTemporario( self.cadProdutos.GetItem( self.cadProdutos.GetFocusedItem(), 0 ).GetText() )
			if self.modulo_chamador == 1:

				self.v.vinculaProduto( self.p, liProdu, Posind, 2, self, self.rlFilial )
				self.p.gravarTemporario()

	def passar(self,event):

		self.r  = self.cadProdutos.GetFocusedItem()
		self.ref.SetValue( self.cadProdutos.GetItem( self.cadProdutos.GetFocusedItem(),21 ).GetText() )
		self.cin.SetValue( self.cadProdutos.GetItem( self.cadProdutos.GetFocusedItem(),22 ).GetText() )
		self.rfb.SetValue( self.cadProdutos.GetItem( self.cadProdutos.GetFocusedItem(),23 ).GetText() )
		self.fab.SetValue( self.cadProdutos.GetItem( self.cadProdutos.GetFocusedItem(), 4 ).GetText() )

	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#123B63") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Vincular produto ao XML", 0, 325, 90)
		dc.SetTextForeground("#498CA2") 	
		dc.DrawRotatedText("Lista de Produtos", 0, 162, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(638,  292,55, 32,   3) #-->[ Lykos ]


class PRListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#C5DCE4")

		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr4 = wx.ListItemAttr()
		self.attr2.SetBackgroundColour("#E3C3C9")
		self.attr3.SetBackgroundColour("#CC7787")
		self.attr4.SetBackgroundColour("#E5E593")

		self.InsertColumn(0, 'Código',        format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(1, 'Código Barras', format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(2, 'Referencia', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(3, 'Descriçao dos Produtos',width=300)
		self.InsertColumn(4, 'Fabricante',            width=200)
		self.InsertColumn(5, 'ID-Registro',           width=80)
		self.InsertColumn(6, 'Margem de Segurança',   format=wx.LIST_ALIGN_LEFT,width=130)

		self.InsertColumn(7, '{%}Acréscim-Desconto-2',   format=wx.LIST_ALIGN_LEFT,width=160)
		self.InsertColumn(8, '{%}Acréscim-Desconto-3',   format=wx.LIST_ALIGN_LEFT,width=160)
		self.InsertColumn(9, '{%}Acréscim-Desconto-4',   format=wx.LIST_ALIGN_LEFT,width=160)
		self.InsertColumn(10, '{%}Acréscim-Desconto-5',   format=wx.LIST_ALIGN_LEFT,width=160)
		self.InsertColumn(11,'{%}Acréscim-Desconto-6',   format=wx.LIST_ALIGN_LEFT,width=160)

		self.InsertColumn(12,'{$}Acréscim-Desconto-2',   format=wx.LIST_ALIGN_LEFT,width=160)
		self.InsertColumn(13,'{$}Acréscim-Desconto-3',   format=wx.LIST_ALIGN_LEFT,width=160)
		self.InsertColumn(14,'{$}Acréscim-Desconto-4',   format=wx.LIST_ALIGN_LEFT,width=160)
		self.InsertColumn(15,'{$}Acréscim-Desconto-5',   format=wx.LIST_ALIGN_LEFT,width=160)
		self.InsertColumn(16,'{$}Acréscim-Desconto-6',   format=wx.LIST_ALIGN_LEFT,width=160)

		self.InsertColumn(17,'Margem de Lucro',          format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(18,'Preço de Venda',           format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(19,'A-Acréscimo D-Desconto',   format=wx.LIST_ALIGN_LEFT,width=170)
		self.InsertColumn(20,'Numero do ID-Registro',    format=wx.LIST_ALIGN_LEFT,width=170)

		self.InsertColumn(21,'Referência',     format=wx.LIST_ALIGN_LEFT,width=200)
		self.InsertColumn(22,'Código Interno', format=wx.LIST_ALIGN_LEFT,width=200)
		self.InsertColumn(23,'Referência do Fabricante', width=300)
		self.InsertColumn(24,'Media ST',format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(25,'QT Embalagem',format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(26,'Estoque Minimo',format=wx.LIST_ALIGN_LEFT, width=120)
		self.InsertColumn(27,'Estoque Fisico',  format=wx.LIST_ALIGN_LEFT, width=120)
		self.InsertColumn(28,'Estoque Reserva', format=wx.LIST_ALIGN_LEFT, width=150)
		self.InsertColumn(29,'Produto Vinculado', width=150)
		self.InsertColumn(30,'Precos p/Filial', width=800)
		self.InsertColumn(31,'Marcação/valor', width=200)
		self.InsertColumn(32,'Controle p/numero de serie', width=200)
		self.InsertColumn(33,'Metragem p/Calculo automatico de unidades', width=200)
			
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
			
			index = self.itemIndexMap[item]
			minim = Decimal( self.itemDataMap[index][26] )
			fisic = Decimal( self.itemDataMap[index][27] )
			
			if self.itemDataMap[index][29] == 'False':	return self.attr4

			if minim !=0 and minim == fisic:	return self.attr2
			if minim !=0 and minim  > fisic:	return self.attr3
			
			if   item % 2:	return self.attr1
		
	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][29] == 'False':	return self.i_idx
		return self.w_idx

	def GetListCtrl(self):	return self


class VincularProdutos:
	
	def vinculaProduto(self,_p,lProdu,indPos, TP, parent, Filial ):

		""" Parametros p/Calculo automatico da quantidade p/Embalagens """
		qTC = _p.ListaCMP.GetItem(indPos, 4 ).GetText() #-: Quantidade de Compra
		vUC = _p.ListaCMP.GetItem(indPos, 6 ).GetText() #-: Valor Unitario de Compra
		vTP = _p.ListaCMP.GetItem(indPos, 7 ).GetText() #-: Valor Total do Produto

		qTM = _p.ListaCMP.GetItem(indPos,69).GetText() #-: Quantidade Manual
		vUM = _p.ListaCMP.GetItem(indPos,77).GetText() #-: Valor Unitario Manual
		
		""" Se o produto não tiver sT e o produtos cadastrado tiver ele busca do cadastro """
		xsT = _p.ListaCMP.GetItem(indPos,78).GetText()
		if lProdu[24] !='' and Decimal( lProdu[24] ) > 0:	psT = str( lProdu[24] )
		else:	psT = ''
		
		_custo = _venda = _nmarge = margem = _npreco = Decimal('0.000')
		if _p.ListaCMP.GetItem(indPos,42).GetText()  != '':	_custo = Decimal( _p.ListaCMP.GetItem(indPos,42).GetText() )

		if lProdu[18] != '':	_venda = Decimal( lProdu[18] )
		if lProdu[17] != '':	margem = Decimal( lProdu[17] )
		
		if _custo != 0 and _venda != 0:	_nmarge = _p.T.trunca( 1, ( ( ( Decimal(_venda) / _custo ) -1 ) * 100 ) ) #-: Margem de lucro novo
		if margem != 0 and _custo != 0:	_npreco = _p.T.trunca( 1, ( _custo + ( _custo * margem / 100 ) ) ) #----------: Novo Preco de venda

		_p.ListaCMP.SetStringItem(indPos,40, "2")  #------------------------------------------: codigo vinculado
		_p.ListaCMP.SetStringItem(indPos,41, lProdu[0] )  #-: codigo do produto

		_p.ListaCMP.SetStringItem(indPos, 8, str( lProdu[18] ) ) #-: Preço  de Venda

		_p.ListaCMP.SetStringItem(indPos,53, str( lProdu[17] ) ) #-: Margem de Lucro
		_p.ListaCMP.SetStringItem(indPos,54, str( _npreco )) #----------------------------------: Novo preco de venda
		_p.ListaCMP.SetStringItem(indPos,58, str( _nmarge )) #----------------------------------: Nova Maregem de Lucro

		_ajuste = "2"
		if _nmarge <= 0:	_ajuste = "1"
		_p.ListaCMP.SetStringItem(indPos,59, _ajuste) #---------------------------------------: Margem 1-2

		p2 = p3 = p4 = p5 = p6 =''
		if lProdu[7] and Decimal( lProdu[7] ):	p2 = str( lProdu[7] )
		if lProdu[8] and Decimal( lProdu[8] ):	p3 = str( lProdu[8] )
		if lProdu[9] and Decimal( lProdu[9] ):	p4 = str( lProdu[9] )
		if lProdu[10] and Decimal( lProdu[10] ):	p5 = str( lProdu[10] )
		if lProdu[11] and Decimal( lProdu[11] ):	p6 = str( lProdu[11])

		v2 = str( lProdu[12] ) if lProdu[12] and Decimal( lProdu[12] ) else ''
		v3 = str( lProdu[13] ) if lProdu[13] and Decimal( lProdu[13] ) else ''
		v4 = str( lProdu[14] ) if lProdu[14] and Decimal( lProdu[14] ) else ''
		v5 = str( lProdu[15] ) if lProdu[15] and Decimal( lProdu[15] ) else ''
		v6 = str( lProdu[16] ) if lProdu[16] and Decimal( lProdu[16] ) else ''

		_p.ListaCMP.SetStringItem(indPos,62, p2) #-:% Acrescimo-Desconto 2
		_p.ListaCMP.SetStringItem(indPos,63, p3) #-:% Acrescimo-Desconto 3
		_p.ListaCMP.SetStringItem(indPos,64, p4) #-:% Acrescimo-Desconto 4
		_p.ListaCMP.SetStringItem(indPos,65, p5) #-:% Acrescimo-Desconto 5
		_p.ListaCMP.SetStringItem(indPos,66, p6) #-:% Acrescimo-Desconto 6
		_p.ListaCMP.SetStringItem(indPos,67, str( lProdu[17] ) ) #-:% Backup Margem de Lucro

		_p.ListaCMP.SetStringItem(indPos,79, str( lProdu[5] )) #---: ID-Produto
		_p.ListaCMP.SetStringItem(indPos,82, v2) #-:$ Acrescimo-Desconto 2
		_p.ListaCMP.SetStringItem(indPos,83, v3) #-:$ Acrescimo-Desconto 3
		_p.ListaCMP.SetStringItem(indPos,84, v4) #-:$ Acrescimo-Desconto 4
		_p.ListaCMP.SetStringItem(indPos,85, v5) #-:$ Acrescimo-Desconto 5
		_p.ListaCMP.SetStringItem(indPos,86, v6) #-:$ Acrescimo-Desconto 6
		_p.ListaCMP.SetStringItem(indPos,114, lProdu[31]) #-: Marcacao/vaolor

		"""   Precos separado por filial   """
		_pfl = _lsF = ""
		if lProdu[30] !=None and lProdu[30] !="" and rcTribu.retornaPrecos( Filial, lProdu[30], Tipo = 1 )[0] == True:

			_pfl,_lsF = rcTribu.retornaPrecos( Filial, lProdu[30], Tipo=2 )

		_p.ListaCMP.SetStringItem(indPos,107, _pfl ) #-: Informacoes da filial selecionada
		_p.ListaCMP.SetStringItem(indPos,108, _lsF ) #-: Inforamcoes das filiais nao selecionadas

		""" Calculo automatico da quantidade p/Embalagens """
		#if calcular and _p.embala.GetValue():	embmetros.calcularEmbalagensAutomatico( _p, ( Decimal( lProdu[24] ), Decimal( vUC ), Decimal( qTC ), indPos ) )
		if lProdu[25]:	embmetros.calcularEmbalagensAutomatico( _p, ( Decimal( lProdu[25] ), Decimal( vUC ), Decimal( qTC ), indPos ), True )

		"""  Calculo automatico para metros transformando em unidades { Conversao para unidade, preco unitario manual }  """
		if lProdu[33] and len( lProdu[33].split('|') ) >=6:

			com, lar, exp = Decimal( lProdu[33].split('|')[3] ), Decimal( lProdu[33].split('|')[4] ), Decimal( lProdu[33].split('|')[5] )
			if ( com + lar + exp ):	embmetros.calcularMetragens( _p, ( com, lar, exp, qTC, vTP, lProdu[33], indPos ), True )
		
		if xsT == '' and psT != '':	_p.ListaCMP.SetStringItem(indPos,78, str( psT ) )
		if xsT != '' and Decimal( xsT ) == 0 and psT !='':	_p.ListaCMP.SetStringItem(indPos,78, str( psT ) )

		_p.ListaCMP.SetStringItem(indPos,70, lProdu[3] ) #--------:[ Descricao do produto ]
		_p.ListaCMP.SetStringItem(indPos,80, str( lProdu[6] ) ) #-:[ Margem de seguranca ]
		_p.ListaCMP.SetStringItem(indPos,87, lProdu[19]) #--------:$ A-Acrescimo D-Desconto
		
		_p.relerLista(wx.EVT_BUTTON)
		if TP == 2:	_p.recalculaST()

		_p.codigovin.SetLabel("Código: {"+str( lProdu[0] )+"}")
		_p.vinculado.SetValue( lProdu[3] )
		
		if TP == 2:
			
			try:
			
				_p.passagem(wx.EVT_BUTTON)
	
			except Exception as error:
				
				pass

	def desvincular(self,_p,indPos):

		_p.ListaCMP.SetStringItem(indPos,40, "" ) #------------------------------------------: codigo vinculado
		_p.ListaCMP.SetStringItem(indPos,41, "" ) #-: codigo do produto
		_p.ListaCMP.SetStringItem(indPos, 8, "" ) #-: Preço  de Venda
		_p.ListaCMP.SetStringItem(indPos,53, "" ) #-: Margem de Lucro
		_p.ListaCMP.SetStringItem(indPos,54, "" ) #----------------------------------: Novo preco de venda
		_p.ListaCMP.SetStringItem(indPos,58, "" ) #----------------------------------: Nova Maregem de Lucro
		_p.ListaCMP.SetStringItem(indPos,59, "" ) #---------------------------------------: Margem 1-2
		_p.ListaCMP.SetStringItem(indPos,62, "" ) #-:% Acrescimo-Desconto 2
		_p.ListaCMP.SetStringItem(indPos,63, "" ) #-:% Acrescimo-Desconto 3
		_p.ListaCMP.SetStringItem(indPos,64, "" ) #-:% Acrescimo-Desconto 4
		_p.ListaCMP.SetStringItem(indPos,65, "" ) #-:% Acrescimo-Desconto 5
		_p.ListaCMP.SetStringItem(indPos,66, "" ) #-:% Acrescimo-Desconto 6
		_p.ListaCMP.SetStringItem(indPos,67, "" ) #-:% Backup Margem de Lucro
		_p.ListaCMP.SetStringItem(indPos,69, "" ) #-: Valor Unitario Manual
		_p.ListaCMP.SetStringItem(indPos,70, "" ) #-:[ Descricao o produto ]
		_p.ListaCMP.SetStringItem(indPos,77, "" ) #-: Quantidade Manual
		_p.ListaCMP.SetStringItem(indPos,78, "" )
		_p.ListaCMP.SetStringItem(indPos,79, "" ) #-:[ Numero do Registro ID-Produto ]
		_p.ListaCMP.SetStringItem(indPos,80, "" ) #-:[ Margem de seguranca ]
		_p.ListaCMP.SetStringItem(indPos,87, "" ) #-:$ A-Acrescimo D-Desconto
		
		_p.relerLista(wx.EVT_BUTTON)
		_p.recalculaST()
		_p.codigovin.SetLabel("")
		_p.vinculado.SetValue("")
		_p.passagem(wx.EVT_BUTTON)
		
		
class InformarPrecos(wx.Frame):
	
	npedido = ''
	modulos = ''
	TipoPed = ''
	filialP = ''
	
	def __init__(self,parent,id):

		self.p = parent
		self.n = numeracao()
		mkn    = wx.lib.masked.NumCtrl

		if   self.modulos == "COMPRA":	self.r = parent.r
		elif self.modulos == "PRODUTO":	self.r = parent
		elif self.modulos == "CANCELA":	self.r = parent.r
		elif self.modulos == "AJUSTES":	self.r = parent

		self._pes = ""
		self.lcal = []
		self.lsTa = {}
		self.rsTa = ""
		self.prma = '' #-: Verifica se o pedido de RMA Foi Emitido nfe e nao permiti cancelamento
		
		if self.r.ajfabri.GetValue() == True:	self._pes = self.r.precos.GetValue()
		if self.r.ajgrupo.GetValue() == True:	self._pes = self.r.precos.GetValue()
		if self.r.ajsubg1.GetValue() == True:	self._pes = self.r.precos.GetValue()
		if self.r.ajsubg2.GetValue() == True:	self._pes = self.r.precos.GetValue()
		
		AJListCtrl.TipoFilialRL = nF.rF( cdFilial = self.filialP )
		
		mkn = wx.lib.masked.NumCtrl

		wx.Frame.__init__(self, parent, 400, 'Compras produtos: ajuste de preços  [ Conferência ]  {'+str( self.filialP )+'}', size=(900,595), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		self.Conferencia = AJListCtrl(self.painel, 401,pos=(12,0), size=(885,225),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

		self.Conferencia.SetBackgroundColour('#D5F0D5')
		self.Conferencia.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.Conferencia.Bind(wx.EVT_LIST_ITEM_SELECTED, self.passagem)
		if self.modulos != "CANCELA":	self.Conferencia.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.alterarDados)
		self.Bind(wx.EVT_KEY_UP,self.Teclas)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		if self.modulos == "CANCELA":

			self.SetTitle('Compras Produtos: Cancelamento  {'+str( self.filialP )+'}')
			self.Conferencia.SetBackgroundColour('#D0AAAA')

		self._aT = wx.StaticText(self.painel,-1,u"Nº Itens", pos=(110,235))
		self._aT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._aT.SetForegroundColour('#10467B')

		wx.StaticText(self.painel,-1,u"Nº Chave NFe", pos=(173,232)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº NFe",       pos=(553,232)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Protocolo", pos=(633,232)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Descrição do Fornecedor:", pos=(15, 280)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Lançamento:",              pos=(553,280)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 
		wx.StaticText(self.painel,-1,u"Total dos Produtos", pos=(18, 308)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"SB.Triburaria",      pos=(130,308)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Total I P I",        pos=(242,308)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Total Frete",        pos=(354,308)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Outras Despesas", pos=(18, 348)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Seguro",          pos=(130,348)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Desconto",        pos=(242,348)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Total Nota",      pos=(354,348)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Código do Fornecedor",     pos=(468,308)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Referência do Fornecedor", pos=(688,308)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Descrição do produdo no Fornecedor",  pos=(468,348)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Preço {1}", pos=(18, 410)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Preço {2}", pos=(128,410)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Preço {3}", pos=(238,410)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Preço {4}", pos=(18, 450)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Preço {5}", pos=(128,450)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Preço {6}", pos=(238,450)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		wx.StaticText(self.painel,-1,u"Margem\nReal", pos=(348,400)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Margem p/Acréscimo-Desconto:", pos=(183,520)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Atalhos p/Ajuste de Preços: [ + ]-Seleciona Margens  [ - ]-Seleciona Preços_1-6  [ / ]-Seleciona Acréscimo-Desconto  [ * ]-Selecionar Todos", pos=(5,550)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		"""  Codigos fiscais  """
		self.cprimario = wx.StaticText(self.painel,-1,u"Codigos", pos=(5,  570))
		self.cprimario.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.csecundar = wx.StaticText(self.painel,-1,u"Codigos", pos=(320,570))
		self.csecundar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.cfmens = wx.StaticText(self.painel,-1,u"{ Codigos fiscais }", pos=(790,570))
		self.cfmens.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cfmens.SetForegroundColour('#7F7F7F')
		
		self.T2 = wx.StaticText(self.painel,-1,u"Desconto {2}", pos=(415,410))
		self.T2.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.T3 = wx.StaticText(self.painel,-1,u"Desconto {3}", pos=(482,410))
		self.T3.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.T4 = wx.StaticText(self.painel,-1,u"Desconto {4}", pos=(345,450))
		self.T4.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.T5 = wx.StaticText(self.painel,-1,u"Desconto {5}", pos=(415,450))
		self.T5.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.T6 = wx.StaticText(self.painel,-1,u"Desconto {6}", pos=(482,450))
		self.T6.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.T7 = wx.StaticText(self.painel,-1,u"{ Ajuste de Preços }\nGeral, Fabricante\nGrupo,Sub-Grupos", pos=(17,495))
		self.T7.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.T7.SetForegroundColour("#1E5890")

		self.pd = wx.StaticText(self.painel,-1,u"", pos=(18, 390))
		self.pd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pd.SetForegroundColour('#21476D')
 
 		wx.StaticText(self.painel,-1,u"Marcação",    pos=(549,410)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,u"Compra",      pos=(639,410)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,u"Custo",       pos=(736,410)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

 		wx.StaticText(self.painel,-1,u"Custo Médio", pos=(549,450)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,u"Comissão",    pos=(639,450)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,u"Segurança",   pos=(736,450)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 
		self.chave = wx.TextCtrl(self.painel,-1,'',pos=(170,245),size=(370,23),style = wx.TE_READONLY)
		self.chave.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.chave.SetBackgroundColour('#BFBFBF')
		if self.modulos == "CANCELA":	self.chave.SetForegroundColour('#E30404')

		self.nuNfe = wx.TextCtrl(self.painel,-1,'',pos=(550,245),size=(70,23),style = wx.TE_READONLY)
		self.nuNfe.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nuNfe.SetBackgroundColour('#BFBFBF')
		if self.modulos == "CANCELA":	self.nuNfe.SetForegroundColour('#E30404')

		self.nProT = wx.TextCtrl(self.painel,-1,'',pos=(630,245),size=(268,23),style = wx.TE_READONLY)
		self.nProT.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nProT.SetBackgroundColour('#BFBFBF')
		if self.modulos == "CANCELA":	self.nProT.SetForegroundColour('#E30404')

		self.Forne = wx.TextCtrl(self.painel,-1,'',pos=(170,275),size=(370,23),style = wx.TE_READONLY)
		self.Forne.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.Forne.SetBackgroundColour('#BFBFBF')		
		if self.modulos == "CANCELA":	self.Forne.SetForegroundColour('#E30404')

		self.lanca = wx.TextCtrl(self.painel,-1,'',pos=(630,275),size=(268,23),style = wx.TE_READONLY)
		self.lanca.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.lanca.SetBackgroundColour('#BFBFBF')
		if self.modulos == "CANCELA":	self.lanca.SetForegroundColour('#E30404')

		self.TTPro = wx.TextCtrl(self.painel,-1,'',pos=(15,320),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTPro.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TTPro.SetBackgroundColour('#E5E5E5')

		self.TTSbT = wx.TextCtrl(self.painel,-1,'',pos=(127,320),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTSbT.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TTSbT.SetBackgroundColour('#E5E5E5')

		self.TTipi = wx.TextCtrl(self.painel,-1,'',pos=(239,320),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTipi.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TTipi.SetBackgroundColour('#E5E5E5')

		self.TTfrt = wx.TextCtrl(self.painel,-1,'',pos=(351,320),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTfrt.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TTfrt.SetBackgroundColour('#E5E5E5')

		self.TTOut = wx.TextCtrl(self.painel,-1,'',pos=(15,360),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTOut.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TTOut.SetBackgroundColour('#E5E5E5')

		self.TTSeg = wx.TextCtrl(self.painel,-1,'',pos=(127,360),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTSeg.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TTSeg.SetBackgroundColour('#E5E5E5')

		self.TTdes = wx.TextCtrl(self.painel,-1,'',pos=(239,360),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTdes.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TTdes.SetBackgroundColour('#E5E5E5')

		self.TTnot = wx.TextCtrl(self.painel,-1,'',pos=(351,360),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTnot.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TTnot.SetBackgroundColour('#E5E5E5')

		self.TTcfr = wx.TextCtrl(self.painel,-1,'',pos=(465,320),size=(210,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTcfr.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTcfr.SetBackgroundColour('#E5E5E5')
		if self.modulos == "CANCELA":	self.TTcfr.SetForegroundColour('#E30404')
		else:	self.TTcfr.SetForegroundColour('#111182')

		self.TTref = wx.TextCtrl(self.painel,-1,'',pos=(685,320),size=(210,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTref.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTref.SetBackgroundColour('#E5E5E5')
		if self.modulos == "CANCELA":	self.TTref.SetForegroundColour('#E30404')
		else:	self.TTref.SetForegroundColour('#111182')

		self.TTdsf = wx.TextCtrl(self.painel,-1,'',pos=(465,360),size=(430,20),style = wx.TE_READONLY)
		self.TTdsf.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TTdsf.SetBackgroundColour('#E5E5E5')
		if self.modulos == "CANCELA":	self.TTdsf.SetForegroundColour('#E30404')
		else:	self.TTdsf.SetForegroundColour('#111182')
		
#-------: Desconto Acrescimo
		self.desconto = wx.RadioButton(self.painel,-1,"Desconto ",  pos=(543,388),style=wx.RB_GROUP)
		self.acrescim = wx.RadioButton(self.painel,-1,"Acréscimo",  pos=(630,388))
		self.pd_marc  = wx.CheckBox(self.painel, -1 , "Marcação-Valor",(730,388))

		self.desconto.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.acrescim.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_marc.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

#-------: Dados de precos

		self.pd_tpr1 = mkn(self.painel, id = 241, value = '0.000', pos = (15, 422), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_tpr2 = mkn(self.painel, id = 350, value = '0.000', pos = (125,422), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_tpr3 = mkn(self.painel, id = 351, value = '0.000', pos = (235,422), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_tpr4 = mkn(self.painel, id = 352, value = '0.000', pos = (15, 461), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_tpr5 = mkn(self.painel, id = 353, value = '0.000', pos = (125,461), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_tpr6 = mkn(self.painel, id = 354, value = '0.000', pos = (235,461), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

		self.pd_tpr1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pd_vdp1 = wx.TextCtrl(self.painel,-1, '0.000', pos=(345,422),size=(60,23),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pd_vdp1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pd_vdp1.SetBackgroundColour('#E5E5E5')
		self.pd_vdp1.SetForegroundColour('#1C4C1C')

		self.pd_vdp2 = mkn(self.painel, id = 231, value = '0.00', pos = (415,422), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_vdp3 = mkn(self.painel, id = 232, value = '0.00', pos = (482,422), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_vdp4 = mkn(self.painel, id = 233, value = '0.00', pos = (345,461), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_vdp5 = mkn(self.painel, id = 234, value = '0.00', pos = (415,461), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_vdp6 = mkn(self.painel, id = 235, value = '0.00', pos = (482,461), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

		self.pd_vdp2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pd_marg = mkn(self.painel, 240, value = '0.000',  pos = (546,422), style = wx.ALIGN_RIGHT|0, integerWidth = 4, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#BFBFBF", validBackgroundColour = "#BFBFBF", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_pcom = wx.TextCtrl(self.painel, -1,  '0.0000', pos = (636,422), size=(90,23), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pd_pcus = mkn(self.painel, 242, value = '0.0000', pos = (733,422), style = wx.ALIGN_RIGHT|0, integerWidth = 5, fractionWidth = 4, groupChar = ',', decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#BFBFBF", validBackgroundColour = "#BFBFBF", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_cusm = wx.TextCtrl(self.painel, -1,  '0.0000', pos = (546,461), size=(83,23), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pd_coms = mkn(self.painel, 243,  value = '0.000', pos = (636,461), style = wx.ALIGN_RIGHT|0, integerWidth = 3, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black",   signedForegroundColour = "Red", emptyBackgroundColour = "#BFBFBF", validBackgroundColour = "#BFBFBF", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_mrse = mkn(self.painel, 244,  value = '0.00',  pos = (733,461), style = wx.ALIGN_RIGHT|0, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#DC8E8E", signedForegroundColour = "Red", emptyBackgroundColour = "#BFBFBF", validBackgroundColour = "#BFBFBF", invalidBackgroundColour = "Yellow",allowNegative = False)

		self.pmargem = mkn(self.painel, id = 355, value = '0.000', pos = (350,513), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pmargem.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ajustar = wx.CheckBox(self.painel,   -1,"Marque p/Ajustar Preços { Geral, Fabricante, Grupos }",  pos=(180,492))
		self.ajustar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ajustar.SetForegroundColour("#00407E")
		if nF.rF( cdFilial = self.filialP ) == "T":	self.ajustar.SetLabel("Marque p/Ajustar Preços { REMOTO Não Permitido }")
		
		self.ajGrupos = wx.RadioButton(self.painel,-1,"Ajuste de Preços Fabricante,Grupos", pos=(510,491),style=wx.RB_GROUP)
		self.ajpGeral = wx.RadioButton(self.painel,-1,"Ajuste de Preços Geral", pos=(510,515))

		self.ajAcresc = wx.RadioButton(self.painel,-1,"Ajustar Custo",  pos=(730,491),style=wx.RB_GROUP)
		self.ajDescon = wx.RadioButton(self.painel,-1,"Ajustar Margem", pos=(730,515))

		self.ajGrupos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajpGeral.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajAcresc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajDescon.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pd_marg.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_pcus.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pd_coms.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_mrse.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pd_cusm.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pd_pcom.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pd_coms.SetForegroundColour('#1E65AC')
		self.pd_pcus.SetForegroundColour('#1E65AC')
		self.pd_mrse.SetForegroundColour('#B61C1C')
		self.pd_cusm.SetBackgroundColour('#BFBFBF')
		self.pd_pcom.SetBackgroundColour('#BFBFBF')
		self.pd_pcom.SetForegroundColour('#4D4D4D')

#-------: Icones
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltap.png",    wx.BITMAP_TYPE_ANY), pos=(15,233), size=(34,32))				

		self.cancla = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/cancela24.png", wx.BITMAP_TYPE_ANY), pos=(850,402), size=(43,38))				
		self.altera = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/alterarp.png",  wx.BITMAP_TYPE_ANY), pos=(55,233), size=(34,32))				
		self.gravar = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(850,442), size=(43,38))				
		self.ajuste = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/executa.png",wx.BITMAP_TYPE_ANY), pos=(850,495), size=(43,38))				

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.cancla.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gravar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.altera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.cancla.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.gravar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		self.altera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  

		self.altera.Bind(wx.EVT_BUTTON, self.AjustaPrecos)
		voltar.Bind(wx.EVT_BUTTON, self.sair)

		self.cancla.Bind(wx.EVT_BUTTON, self.cancelaCompra)
		self.desconto.Bind(wx.EVT_RADIOBUTTON, self.evTRadio)
		self.acrescim.Bind(wx.EVT_RADIOBUTTON, self.evTRadio)
		self.pd_marc.Bind(wx.EVT_CHECKBOX,  self.marcacao)
		self.gravar.Bind(wx.EVT_BUTTON, self.atualizaValores)
		self.ajustar.Bind(wx.EVT_CHECKBOX,  self.mAjuste)
		self.ajuste.Bind(wx.EVT_BUTTON, self.aTualizarPrecos)
		
		""" Teclado Numerico """
		self.pd_tpr1.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_tpr2.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_tpr3.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_tpr4.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_tpr5.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_tpr6.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_vdp2.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_vdp3.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_vdp4.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_vdp5.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_vdp6.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_marg.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_pcus.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_coms.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_mrse.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pmargem.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

		self.selecionar()
		if self.modulos != "AJUSTES":	self.ativaDesativa( False )

		if self.modulos != "CANCELA":	self.cancla.Enable( False )
		if self.modulos != "AJUSTES":	self.ajustar.Enable( False )

		self.ajGrupos.Disable()
		self.ajpGeral.Disable()
		self.ajAcresc.Disable()
		self.ajDescon.Disable()
		self.ajuste.Disable()
		self.pmargem.Enable( False )

		if nF.rF( cdFilial = self.filialP ) == "T":	self.ajustar.Enable( False )
		self.Conferencia.Select(0)
		self.Conferencia.SetFocus()

	def mAjuste(self,event):
		
		self.ajGrupos.Enable( self.ajustar.GetValue() )
		self.ajpGeral.Enable( self.ajustar.GetValue() )
		self.ajAcresc.Enable( self.ajustar.GetValue() )
		self.ajDescon.Enable( self.ajustar.GetValue() )
		self.pmargem.Enable( self.ajustar.GetValue() )
		self.ajuste.Enable( self.ajustar.GetValue() )
		self.pmargem.Enable( self.ajustar.GetValue() )

		if self.ajustar.GetValue() == True:	self.altera.Enable( False )
		else:	self.altera.Enable( True )

	def TlNum(self,event):

		dc = 2
		d3=[240,241,243,350,351,352,353,354,355]
		d4=[242]
		if event.GetId() in d3:	dc = 3
		if event.GetId() in d4:	dc = 4
		
		TelNumeric.decimais = dc
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def cancelaCompra(self,event):

		if self.prma.split("|")[0] == '1':
			
			info = ''
			if len( self.prma.split("|") ) >=3:	info += u"\nNº DANFE: "+self.prma.split("|")[2]
			if len( self.prma.split("|") ) >=2:	info += u"\nNº NFe....: "+self.prma.split("|")[1]
			if len( self.prma.split("|") ) >=4:	info += u"\nEmissão..: "+self.prma.split("|")[3]

			alertas.dia(self.painel,u"{ Pedido de Devolulção de RMA }\n\nAntes de cancelar o pedidos de RMA\nCancele a NFe no Gerênciador de Notas\n"+ info +"\n"+(" "*120),"Cancelamento de RMA com NFe")
			return

		compraCancela.ccFilial = self.filialP
		can_frame=compraCancela(parent=self,id=event.GetId())
		can_frame.Centre()
		can_frame.Show()

	def Tvalores(self,valor,idfy):

		if Decimal(valor) == 0:	valor = "0.00"

		if idfy == 241:	self.pd_tpr1.SetValue(valor)
		if idfy == 350:	self.pd_tpr2.SetValue(valor)
		if idfy == 351:	self.pd_tpr3.SetValue(valor)
		if idfy == 352:	self.pd_tpr4.SetValue(valor)
		if idfy == 353:	self.pd_tpr5.SetValue(valor)
		if idfy == 354:	self.pd_tpr6.SetValue(valor)
		if idfy == 355:	self.pmargem.SetValue(valor)

		if idfy == 231:	self.pd_vdp2.SetValue(valor)
		if idfy == 232:	self.pd_vdp3.SetValue(valor)
		if idfy == 233:	self.pd_vdp4.SetValue(valor)
		if idfy == 234:	self.pd_vdp5.SetValue(valor)
		if idfy == 235:	self.pd_vdp6.SetValue(valor)

		if idfy == 240:	self.pd_marg.SetValue(valor)
		if idfy == 242:	self.pd_pcus.SetValue(valor)
		if idfy == 243:	self.pd_coms.SetValue(valor)
		if idfy == 244:	self.pd_mrse.SetValue(valor)

		self.n.calcularProduto(idfy,self, Filial = self.filialP, mostrar = True, retornar_valor = False )

	def marcacao(self,event):
		
		self.pd_vdp2.Enable(self.pd_marc.GetValue())
		self.pd_vdp3.Enable(self.pd_marc.GetValue())
		self.pd_vdp4.Enable(self.pd_marc.GetValue())
		self.pd_vdp5.Enable(self.pd_marc.GetValue())
		self.pd_vdp6.Enable(self.pd_marc.GetValue())
		self.n.calcularProduto(event.GetId(),self, Filial = self.filialP, mostrar = True, retornar_valor = False )
		
	def evTRadio(self,event):

		TT = "Desconto"
		CO = "#000000"
		if self.acrescim.GetValue() == True:
			TT = "Acréscimo"
			CO = "#B61C1C"
			
		self.T2.SetLabel(str(TT)+" {2}")
		self.T3.SetLabel(str(TT)+" {3}")
		self.T4.SetLabel(str(TT)+" {4}")
		self.T5.SetLabel(str(TT)+" {5}")
		self.T6.SetLabel(str(TT)+" {6}")

		self.T2.SetForegroundColour(CO)
		self.T3.SetForegroundColour(CO)
		self.T4.SetForegroundColour(CO)
		self.T5.SetForegroundColour(CO)
		self.T6.SetForegroundColour(CO)

		self.n.calcularProduto(0,self, Filial = self.filialP, mostrar = True, retornar_valor = False )

	def Teclas(self,event):
		
		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		__id     = 0
		if controle !=None:	__id = controle.GetId()
		self.n.calcularProduto(__id,self, Filial = self.filialP, mostrar = True, retornar_valor = False )
		if keycode == 27:	self.reTornaIndice()
		
		__key = [388,390,392,387]
		if keycode in __key:

			self.alterarDados( wx.EVT_BUTTON )
			
			calcularMargem.cdTecla = keycode
			ajp_frame=calcularMargem(parent=self,id=event.GetId())
			ajp_frame.Centre()
			ajp_frame.Show()

	def reTornaIndice(self):
		
		self.Conferencia.Select( self.Conferencia.GetFocusedItem() )
		self.Conferencia.SetFocus()
		
	def ativaDesativa(self,op):

		self.desconto.Enable(op)
		self.acrescim.Enable(op)
		#self.gravar.Enable(op) #-: 05-10-2017 o eliardo pediu para desabilitar mais sabe o pq

	def alterarDados(self,event):
		
		indice = self.Conferencia.GetFocusedItem()
		if self.ajustar.GetValue() == True:
			
			alertas.dia(self.painel,u"Atulizalção de preços por fabricante,grupos...","Ajuste de Preços")
			return
			
		if self.Conferencia.GetItem(indice, 6).GetText() !='':

			codigo = self.Conferencia.GetItem(indice, 6).GetText()
			conn   = sqldb()
			sql    = conn.dbc("", fil = self.filialP, janela = self.painel )

			if sql[0] == True:

				compra  = "SELECT * FROM produtos WHERE pd_regi='"+str( codigo )+"'"
				compras = sql[2].execute(compra)
				result  = sql[2].fetchall()
				conn.cls(sql[1])

				if compras !=0:

					try:
						
						self.pd_tpr1.SetValue( str( result[0][28] ) )
						self.pd_tpr2.SetValue( str( result[0][29] ) )
						self.pd_tpr3.SetValue( str( result[0][30] ) )
						self.pd_tpr4.SetValue( str( result[0][31] ) )
						self.pd_tpr5.SetValue( str( result[0][32] ) )
						self.pd_tpr6.SetValue( str( result[0][33] ) )
						self.pd_vdp1.SetValue( str( result[0][34] ) )
						self.pd_vdp2.SetValue( str( result[0][35] ) )
						self.pd_vdp3.SetValue( str( result[0][36] ) )
						self.pd_vdp4.SetValue( str( result[0][37] ) )
						self.pd_vdp5.SetValue( str( result[0][38] ) )
						self.pd_vdp6.SetValue( str( result[0][39] ) )
						self.pd_marg.SetValue( str( result[0][20] ) )
						self.pd_pcom.SetValue( str( result[0][23] ) )
						self.pd_pcus.SetValue( str( result[0][24] ) )
						self.pd_cusm.SetValue( str( result[0][25] ) )
						self.pd_coms.SetValue( str( result[0][27] ) )
						self.pd_mrse.SetValue( str( result[0][21] ) )

						if result[0][70] == "D":	self.desconto.SetValue( True )
						if result[0][70] == "A":	self.acrescim.SetValue( True )
						if result[0][68] == "T":	self.pd_marc.SetValue( True )
						if result[0][68] != "T":	self.pd_marc.SetValue( False )
						
						self.pd.SetLabel("Produto: { "+str(result[0][0])+" }  "+str( result[0][2] )+" "+str( result[0][3] ) )

						if self.modulos != "AJUSTES":	self.ativaDesativa( False )
						self.evTRadio(wx.EVT_BUTTON)
						self.pd_marg.SetFocus()
						
					except Exception as _reTornos:
						
						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )	
						alertas.dia(self.painel,u"{ Retorno }\n"+ _reTornos ,"Atualizar valores do produto")			

				else:	alertas.dia(self.painel,u"Produto não localizado no cadastrado!!\n"+(" "*100),u"Compras: conferência de produtos")
			
		else:	alertas.dia(self.painel,u"Código do produto vazio { ID-Produto }\n"+(" "*130),u"Compras: conferência de produtos")
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus("  Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus("  Conferencia e ajuste de preços",0)
		elif event.GetId() == 102:	sb.mstatus("  Grava valores de preços e margens do produto seleiconado",0)
		elif event.GetId() == 103:	sb.mstatus("  Cancelamento do Pedido de Compra",0)
		elif event.GetId() == 401:	sb.mstatus("  Click duplo para conferencia e ajuste de preços",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Compras Produtos: Ajuste de Preços  [ Conferência ]",0)
		event.Skip()

	def AjustaPrecos(self,event):

		indice = self.Conferencia.GetFocusedItem()
		if self.Conferencia.GetItem(indice, 6).GetText() !='':	self.r.alterarProdCompra( self.Conferencia.GetItem(indice, 6).GetText() )

	def passagem(self,even):

		indice = self.Conferencia.GetFocusedItem()
		self.TTcfr.SetValue( self.Conferencia.GetItem(indice, 8).GetText() )
		self.TTref.SetValue( self.Conferencia.GetItem(indice, 7).GetText() )
		self.TTdsf.SetValue( self.Conferencia.GetItem(indice, 9).GetText() )
	
		dB = self.Conferencia.GetItem(indice, 22).GetText().split("|")
		cp = self.Conferencia.GetItem(indice, 26).GetText().strip()
		cs = self.Conferencia.GetItem(indice, 27).GetText().strip()
		
		if self.Conferencia.GetItem(indice, 21).GetText() != '':	self.TTdsf.SetForegroundColour('#D01A1A')
		else:	self.TTdsf.SetForegroundColour('#000000')

		if dB[0] !="":

			self.pd_tpr1.SetValue( str( dB[0].split(";")[0] ) )
			self.pd_tpr2.SetValue( str( dB[0].split(";")[1] ) )
			self.pd_tpr3.SetValue( str( dB[0].split(";")[2] ) )
			self.pd_tpr4.SetValue( str( dB[0].split(";")[3] ) )
			self.pd_tpr5.SetValue( str( dB[0].split(";")[4] ) )
			self.pd_tpr6.SetValue( str( dB[0].split(";")[5] ) )
			self.pd_vdp1.SetValue( str( dB[1].split(";")[0] ) )
			self.pd_vdp2.SetValue( str( dB[1].split(";")[1] ) )
			self.pd_vdp3.SetValue( str( dB[1].split(";")[2] ) )
			self.pd_vdp4.SetValue( str( dB[1].split(";")[3] ) )
			self.pd_vdp5.SetValue( str( dB[1].split(";")[4] ) )
			self.pd_vdp6.SetValue( str( dB[1].split(";")[5] ) )
			if "-" not in dB[2].split(";")[0]:	self.pd_marg.SetValue( str( dB[2].split(";")[0] ) )
			self.pd_mrse.SetValue( str( dB[2].split(";")[1] ) )
			self.pd_coms.SetValue( str( dB[2].split(";")[2] ) )
			self.pd_pcom.SetValue( str( dB[3].split(";")[0] ) )
			self.pd_pcus.SetValue( str( dB[3].split(";")[1] ) )
			self.pd_cusm.SetValue( str( dB[3].split(";")[2] ) )
		
		if self.modulos != "AJUSTES":	self.ativaDesativa( False )

		self.cprimario.SetLabel("{ Código fiscal primário }")
		self.csecundar.SetLabel("{ Código fiscal secundário }")
		self.cprimario.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.csecundar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.csecundar.SetForegroundColour('#0B569F')
		self.cprimario.SetForegroundColour('#0B569F')

		if cp:
			self.cprimario.SetLabel("Codigo fiscal primario: ["+str( cp )+"]")
			if len( cp.split('.') ) >= 3 and cp.split('.')[2].isdigit():

				if int( cp.split('.')[2] ) == 500 or int( cp.split('.')[2] ) == 60:

					self.cprimario.SetForegroundColour('#A52A2A')
					self.cprimario.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
					 			
		if cs:
			self.csecundar.SetLabel("Codigo fiscal secundario: ["+str( cs )+"]")
			if int( cs.split('.')[2] ) == 500 or int( cs.split('.')[2] ) == 60:

				self.csecundar.SetForegroundColour('#A52A2A')
				self.csecundar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

	def sair(self,event):	self.Destroy()
	def selecionar(self):

		conn = sqldb()
		sql  = conn.dbc("Compras: Selecionar produtos de compras para ajuste de preços", fil = self.filialP, janela = self.painel )

		if sql[0] == True:

			if self.modulos == "AJUSTES":

				Ordem = 1
				
				produtos = "SELECT * FROM produtos WHERE pd_canc!= '4' ORDER BY pd_nome"  if nF.fu( self.filialP ) == "T" else "SELECT t1.*,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( self.filialP )+"' ) WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"
				
				_grp = True
				if self.ajustar.GetValue() and self.ajpGeral.GetValue():	_grp = False

				if _grp == True:					
					
					if self.r.ajfabri.GetValue():	produtos = produtos.replace('WHERE',"WHERE pd_fabr='"+str( self._pes )+"' and") if nF.fu( self.filialP ) == "T" else produtos.replace('WHERE',"WHERE t1.pd_fabr='"+str( self._pes )+"' and")
					if self.r.ajgrupo.GetValue():	produtos = produtos.replace('WHERE',"WHERE pd_nmgr='"+str( self._pes )+"' and") if nF.fu( self.filialP ) == "T" else produtos.replace('WHERE',"WHERE t1.pd_nmgr='"+str( self._pes )+"' and")
					if self.r.ajsubg1.GetValue():	produtos = produtos.replace('WHERE',"WHERE pd_sug1='"+str( self._pes )+"' and") if nF.fu( self.filialP ) == "T" else produtos.replace('WHERE',"WHERE t1.pd_sug1='"+str( self._pes )+"' and")
					if self.r.ajsubg2.GetValue():	produtos = produtos.replace('WHERE',"WHERE pd_sug2='"+str( self._pes )+"' and") if nF.fu( self.filialP ) == "T" else produtos.replace('WHERE',"WHERE t1.pd_sug2='"+str( self._pes )+"' and")

				aPro = sql[2].execute(produtos)
				rPro = sql[2].fetchall()
				conn.cls(sql[1])
				
			else:
				
				Ordem = 2
				
				compra  = "SELECT * FROM ccmp WHERE cc_contro='"+str(self.npedido)+"'"
				compras = sql[2].execute(compra)
				self.rsTa = sql[2].fetchall()
				
				"""   Bloqueios   """
				if compras !=0 and self.modulos == "CANCELA":
					
					if self.rsTa[0][27] == "1":	self.cancla.Enable( acs.acsm("207",True) ) #-:Compra
					if self.rsTa[0][27] == "2":	self.cancla.Enable( acs.acsm("209",True) ) #-:Acerto de Estoque
					if self.rsTa[0][27] == "3":	self.cancla.Enable( acs.acsm("210",True) ) #-:RMA
					if self.rsTa[0][27] == "4":	self.cancla.Enable( acs.acsm("209",True) ) #-:Transferencia origem
					if self.rsTa[0][27] == "5":	self.cancla.Enable( acs.acsm("208",True) ) #-:Orcamento
					if self.rsTa[0][27] == "7":	self.cancla.Enable( acs.acsm("209",True) ) #-:Transferencia Destino
				
				aPro = 0

				"""  Bloqueia a o Cancelamento do pedido de RMA   """
				if self.rsTa[0][27] == "3" and self.rsTa[0][5] !="" and self.rsTa[0][6] and self.rsTa[0][37] !="":	self.prma = '1|'+str(self.rsTa[0][5])+'|'+str( self.rsTa[0][6] )+'|'+str( self.rsTa[0][37] )

				if compras == 0:

					conn.cls(sql[1])
					self.chave.SetValue("Numero de controle: ["+self.npedido+"], não localizado!!")
					self.chave.SetForegroundColour('#C34848')
					self.chave.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
					
				else:

					buscar  = "SELECT * FROM iccmp WHERE ic_contro='"+str( self.npedido )+"'"
					aPro = sql[2].execute( buscar )
					rPro = sql[2].fetchall()

				conn.cls(sql[1])

			self.Conferencia.SetBackgroundColour('#D5F0D5')
			if nF.rF( cdFilial = self.filialP ) == "T":	self.Conferencia.SetBackgroundColour('#BE8F8F')

			""" Monta a Lista Virtual """
			self.lsTa  = rPro

			if aPro !=0:	self.ListarSel( Ordem )
					
	def ListarSel(self, ordem ):

		indice = 0
		ordems = 1
		
		_registros = 0
		relacao    = {}
		conn = sqldb()

		sql  = conn.dbc("Compras: Selecionar produtos de compras para ajuste de preços", fil = self.filialP, janela = self.painel )

		if sql[0] == True:

			for i in self.lsTa:

				if ordem == 1:	codigo = i[2]
				else:	codigo = i[59]
				
				dDa  = ""
				_pfl = _lsF = _lsG = _cfp = _cfs = ""

				if sql[2].execute("SELECT * FROM produtos WHERE pd_codi='"+str( codigo )+"' ORDER BY pd_nome") !=0:

					r = sql[2].fetchall()[0]
					
					PRC = str( r[28] )+";"+str( r[29] )+";"+str( r[30] )+";"+str( r[31] )+";"+str( r[32] )+";"+str( r[33] ) #-: Precos
					PCT = str( r[34] )+";"+str( r[35] )+";"+str( r[36] )+";"+str( r[37] )+";"+str( r[38] )+";"+str( r[39] ) #-: Percentuais
					MRG = str( r[20] )+";"+str( r[21] )+";"+str( r[27] ) #-: Margem-Segurancao-Comissao
					CUS = str( r[23] )+";"+str( r[24] )+";"+str( r[25] ) #-: Compra-Custo-Customedio
					dDa = PRC+"|"+PCT+"|"+MRG+"|"+CUS

					_cfp, _cfs = str(r[47]),str(r[82])

					"""   Precos separado por filial   """
					if r[90] and rcTribu.retornaPrecos( self.filialP, r[90], Tipo = 1 )[0]:	_pfl,_lsF = rcTribu.retornaPrecos( self.filialP, r[90], Tipo=2 )

				if self.modulos != "AJUSTES":

					QTX = i[10] #--: Quantidade do XML
					VUX = i[11] #--: Valor Unitario do XML
					STX = i[12] #--: SubToTal do XML
					QTE = i[49] #--: Quantidade Unitario { Lancamento Manual }
					VUE = i[57] #--: Valor Unitario { Lancamento Manual }
					STE = i[60] #--: SubToTal do Valor unitario
					DSC = i[50]

					if Decimal( QTE ) == 0:	QTE = QTX
					if Decimal( VUE ) == 0:	VUE = VUX
					if Decimal( STE ) == 0:	STE = STX
					if DSC == '':	DSC = i[6]
							
				if self.modulos == "AJUSTES":

					if indice in self.lcal:	ajs = "AJUSTE"
					else:	ajs = ""

					relacao[_registros] = str(ordems).zfill(5),i[2],i[3],format(i[15],','),format(i[24],','),format(i[28],','),str(i[0]),str(self.r.precos.GetValue()),"","",\
					"","","","","","","","","","","",ajs,dDa,_pfl,_lsF,_lsG,_cfp, _cfs
				else:

					if indice in self.lcal:	ajs = "AJUSTE"
					else:	ajs = ""

					relacao[_registros] = str(ordems).zfill(5),i[59],DSC,str(QTE),format(Decimal(VUE),','),format(Decimal(STE),','),\
					i[58],i[4],i[5],i[6],str(i[10]),format(Decimal(i[11]),','),format(Decimal(i[12]),','),str(i[27]),str(i[61]),str(i[33]),str(i[51]),\
					str(i[53]),str(i[55]),str(i[0]),str(i[66]),ajs,dDa,_pfl,_lsF,_lsG,_cfp, _cfs

				_registros +=1

				ordems +=1
				indice +=1

			conn.cls(sql[1])

			self._aT.SetLabel("Nº Itens\n{ "+str( len(self.lsTa) )+" }")
						
			self.chave.SetValue('Ajuste de Preços { '+str(self.r.precos.GetValue())+' }')
			self.Forne.SetValue('AJUSTE DE PREÇOS { NORMAL }')
						
			self.Conferencia.SetItemCount( len(self.lsTa) )
			AJListCtrl.itemDataMap  = relacao
			AJListCtrl.itemIndexMap = relacao.keys()

	def atualizaValores(self,event):

		indice = self.Conferencia.GetFocusedItem()
		codigo = self.Conferencia.GetItem(indice, 6).GetText()
		sepFil = self.Conferencia.GetItem(indice,23).GetText()
		sepnFl = self.Conferencia.GetItem(indice,24).GetText()
		
		conn = sqldb()
		sql  = conn.dbc("Compras: Atualização de Preços", fil = self.filialP, janela = self.painel )
		grv  = False

		if sql[0] == True:

			pc1 = self.pd_tpr1.GetValue()
			pc2 = self.pd_tpr2.GetValue()
			pc3 = self.pd_tpr3.GetValue()
			pc4 = self.pd_tpr4.GetValue()
			pc5 = self.pd_tpr5.GetValue()
			pc6 = self.pd_tpr6.GetValue()
			pe1 = self.pd_vdp1.GetValue().replace(',','')
			pe2 = self.pd_vdp2.GetValue()
			pe3 = self.pd_vdp3.GetValue()
			pe4 = self.pd_vdp4.GetValue()
			pe5 = self.pd_vdp5.GetValue()
			pe6 = self.pd_vdp6.GetValue()
			mar = self.pd_marg.GetValue()
			pco = self.pd_pcom.GetValue().replace(',','')
			pcu = self.pd_pcus.GetValue()
			cmd = self.pd_cusm.GetValue().replace(',','')
			com = self.pd_coms.GetValue()
			seg = self.pd_mrse.GetValue()

			mac = "F"
			des = "D"
			flf = ""
			if self.pd_marc.GetValue() == True:	mac = "T"
			if self.acrescim.GetValue() == True:	des = "A"

			"""   Precos separados p/Filial   """
			if sepFil !="":
			
				rcFilial = rTabelas()

				gpv = rcFilial.calculaPrecoFilial( sepFil, Decimal( pcu ), mar )
				flf = sepnFl+gpv

			try:
	
				""" Guardar os 10 ultimos Precos e Margens """
				__i = sql[2].execute("SELECT * FROM produtos WHERE pd_regi='"+str( codigo )+"'")
				_i  = sql[2].fetchall()[0]

				_pcs = str( _i[28] )+";"+str( _i[20] )+"|"+str( _i[29] )+";"+str( _i[35] )+"|"+str( _i[30] )+";"+str( _i[36] )+"|"+str( _i[31] )+";"+str( _i[37] )+"|"+str( _i[32] )+";"+str( _i[38] )+"|"+str( _i[33] )+";"+str( _i[39] )
				pcs  = str(self.pd_tpr1.GetValue())+";"+str(self.pd_marg.GetValue())+"|"+str(self.pd_tpr2.GetValue())+";"+str(self.pd_vdp2.GetValue())+"|"+str(self.pd_tpr3.GetValue())+";"+str(self.pd_vdp3.GetValue())+"|"+\
					   str(self.pd_tpr4.GetValue())+";"+str(self.pd_vdp4.GetValue())+"|"+str(self.pd_tpr5.GetValue())+";"+str(self.pd_vdp5.GetValue())+"|"+str(self.pd_tpr6.GetValue())+";"+str(self.pd_vdp6.GetValue())

				""" Grava as Ultimas Alteracoes de precos """
				ajP = nF.alteracaoPrecos( _pcs, pcs, _i[76], "", "", "AM", "" )
		
				gravar = "UPDATE produtos SET pd_tpr1=%s,pd_tpr2=%s,pd_tpr3=%s,pd_tpr4=%s,pd_tpr5=%s,pd_tpr6=%s,pd_vdp1=%s,pd_vdp2=%s,pd_vdp3=%s,\
						pd_vdp4=%s,pd_vdp5=%s,pd_vdp6=%s,pd_marg=%s,pd_pcom=%s,pd_pcus=%s,pd_cusm=%s,pd_coms=%s,pd_mrse=%s,pd_marc=%s,pd_acds=%s, pd_pcfl=%s, pd_altp=%s WHERE pd_regi=%s"

				grva = sql[2].execute( gravar, ( pc1, pc2, pc3, pc4, pc5, pc6, pe1, pe2, pe3, pe4, pe5, pe6, mar, pco, pcu, cmd, com, seg, mac, des, flf, ajP, codigo))
				sql[1].commit()
				
				if grva !=0:	grv = True
				_reTornos = u"Produto não sofreu ajuste pelo usuario"

			except Exception as _reTornos:
				
				if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
				sql[1].rollback()
				
			conn.cls(sql[1])
	
			if grv == False:	alertas.dia(self.painel,u"Produto não atualizado!!\n\nRetorno: "+_reTornos+"\n"+(" "*120),u"Ajuste de preços conferencia")

			if grv == True:

				""" Adiciona na lista os registro dos produtos q foram ajustados """
				self.lcal.append(indice)

				if self.modulos != "AJUSTES":

					self.ativaDesativa( False )
					self.ListarSel(2)

				else:	self.ListarSel(1)
				
	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#1A461A")
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Dados para conferência de compras", 0, 485, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(12, 230,145, 40,  3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12, 305,885, 80,  3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12, 387,885, 100, 3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12, 490,885, 50, 3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(1,  543,896, 47, 3) #-->[ Lykos ]

#---: Ajuste de Precos, Margem, Compra, Custo
	def aTualizarPrecos(self,event):
		
		if self.pmargem.GetValue() == 0:
			
			alertas.dia(self.painel,"Margem de ajuste estar zerado...\n"+(" "*100),"Ajustar: Preços e Custos")
			return
		
		ET  = datetime.datetime.now().strftime("%d%m%Y_%T")+"_"+login.usalogin.lower()
		_mensagem = mens.showmsg("Selecionando dados da TABELA de Produtos!!\n\nAguarde...")
		shost,suser,spass,sqlbd,sqlpo = login.spadrao.split(";") #-: Servidor padrao { spadrao.cmd }
		
		if not spass.strip():

			alertas.dia(self.painel,u"Os dados do servidor padrão para o banco de dados, estar faltando informações...\n"+(" "*160),u"Ajustar: Preços e Custos")
			return
		
		FileBack = "mysqldump -u%s -p%s sei produtos > %s" %( suser,spass,diretorios.auPreco+"produtos_"+str( ET )+".sql" )
		
		#backu = "echo 151407|su lykos|"+FileBack
		#abrir = commands.getstatusoutput( backu )

		abrir = commands.getstatusoutput( FileBack )
		del _mensagem
		
		if abrir[0] !=0:
			
			alertas.dia(self.painel,"O sistema não conseguiu fazer o backup do cadastro de produtos...\n\n%s" %(abrir[1])+"\n"+(" "*160),"Ajustar: Preços e Custos")
			return

		Tipo = "Fabricante: "+str( self._pes )
		if self.r.ajgrupo.GetValue() == True:	Tipo = "Grupo: "+str( self._pes )
		if self.r.ajsubg1.GetValue() == True:	Tipo = "Sub-Grupo_1: "+str( self._pes )
		if self.r.ajsubg2.GetValue() == True:	Tipo = "Sub-Grupo_2: "+str( self._pes )
		if self.ajpGeral.GetValue()  == True:	Tipo = "Ajuste Geral { Todos os Produtos }"
		
		conn = sqldb()
		sql  = conn.dbc("Compras: Selecionar produtos de compras para ajuste de preços\n\n"+Tipo, fil = self.filialP, janela = self.painel )

		if sql[0] == True:
			
			if nF.rF( cdFilial = self.filialP ) == "T":	produtos = "SELECT * FROM produtos WHERE pd_idfi='"+str( self.filialP )+"' ORDER BY pd_nome"
			else:	produtos = "SELECT * FROM produtos WHERE pd_codi!='' ORDER BY pd_nome"
				
			_grp = True
			if self.ajustar.GetValue() == True and self.ajpGeral.GetValue() == True:	_grp = False

			if _grp == True:					
					
				if self.r.ajfabri.GetValue() == True:	produtos = produtos.replace('WHERE',"WHERE pd_fabr='"+str( self._pes )+"' and")
				if self.r.ajgrupo.GetValue() == True:	produtos = produtos.replace('WHERE',"WHERE pd_nmgr='"+str( self._pes )+"' and")
				if self.r.ajsubg1.GetValue() == True:	produtos = produtos.replace('WHERE',"WHERE pd_sug1='"+str( self._pes )+"' and")
				if self.r.ajsubg2.GetValue() == True:	produtos = produtos.replace('WHERE',"WHERE pd_sug2='"+str( self._pes )+"' and")

			aPro = sql[2].execute(produtos)
			rPro = sql[2].fetchall()
			semC = 0
			Csem = 0
			grav = True

			for ic in rPro:
						
				__pcus = ic[24]
				if Decimal( __pcus ) == 0:	Csem +=1

			if aPro !=0:

				try:
				
					for i in rPro:

						self._pcus = i[24]
						self._marg = i[20]
						self._vdp2 = i[35]
						self._vdp3 = i[36]
						self._vdp4 = i[37]
						self._vdp5 = i[38]
						self._vdp6 = i[39]

						self._tpr1 = i[28]
						self._tpr2 = i[29]
						self._tpr3 = i[30]
						self._tpr4 = i[31]
						self._tpr5 = i[32]
						self._tpr6 = i[33]
						
						self._acds = i[70]
						
						if Decimal( self._pcus ) > 0:

							self.pd_marg.SetValue( str( i[20] ) )
							self.pd_pcus.SetValue( str( i[24] ) )
												  
							self.pd_tpr1.SetValue( str( i[28] ) )
							self.pd_tpr2.SetValue( str( i[29] ) )
							self.pd_tpr3.SetValue( str( i[30] ) )
							self.pd_tpr4.SetValue( str( i[31] ) )
							self.pd_tpr5.SetValue( str( i[32] ) )
							self.pd_tpr6.SetValue( str( i[33] ) )
												  
							self.pd_vdp2.SetValue( str( i[35] ) )
							self.pd_vdp3.SetValue( str( i[36] ) )
							self.pd_vdp4.SetValue( str( i[37] ) )
							self.pd_vdp5.SetValue( str( i[38] ) )
							self.pd_vdp6.SetValue( str( i[39] ) )
																
							margem,mreal,custo = self.CalculaPrecos()
							if custo:	self.pd_pcus.SetValue( str( custo ) )
							if margem:	self.pd_marg.SetValue( str( margem ) )

							mr, pco1, pco2, pco3, pco4, pco5, pco6 = self.n.calcularProduto( 240, self, Filial = self.filialP, mostrar = False, retornar_valor = True )

							if self.r.ajfabri.GetValue() == True:	FG = "FA"
							if self.r.ajgrupo.GetValue() == True:	FG = "GR"
							if self.r.ajsubg1.GetValue() == True:	FG = "G1"
							if self.r.ajsubg2.GetValue() == True:	FG = "G2"

							if self.ajpGeral.GetValue() == True:	TP = "GL"
							else:	TP = "GU"
					
							""" Ajuste pelo Custo pela Margem """
							ajCusMar = "Ajustar p/ Custo"
							if self.ajDescon.GetValue() == True:	ajCusMar = "Ajustar p/Margem"

							_pcs = str( i[28] )+";"+str( i[20] )+"|"+str( i[29] )+";"+str( i[35] )+"|"+str( i[30] )+";"+str( i[36] )+"|"+str( i[31] )+";"+str( i[37] )+"|"+str( i[32] )+";"+str( i[38] )+"|"+str( i[33] )+";"+str( i[39] )
							pcs  = str(self.pd_tpr1.GetValue())+";"+str(self.pd_marg.GetValue())+"|"+str(self.pd_tpr2.GetValue())+";"+str(self.pd_vdp2.GetValue())+"|"+str(self.pd_tpr3.GetValue())+";"+str(self.pd_vdp3.GetValue())+"|"+\
								   str(self.pd_tpr4.GetValue())+";"+str(self.pd_vdp4.GetValue())+"|"+str(self.pd_tpr5.GetValue())+";"+str(self.pd_vdp5.GetValue())+"|"+str(self.pd_tpr6.GetValue())+";"+str(self.pd_vdp6.GetValue())

							""" Grava as Ultimas Alteracoes de precos """
							ajP = nF.alteracaoPrecos( _pcs, pcs, i[76], FG, self._pes, TP, "[p]"+str( self.pmargem.GetValue() )+"|"+str(ajCusMar) )

							"""   Precos separado por filial   """
							flf = ""
							if i[90] !=None and i[90] !="" and rcTribu.retornaPrecos( self.filialP, i[90], Tipo = 1 )[0] == True:

								_pfl,_lsF = rcTribu.retornaPrecos( self.filialP, i[90], Tipo=2 )

								rcFilial = rTabelas()
								gpv = rcFilial.calculaPrecoFilial( _pfl, custo, margem )
								flf = _lsF+gpv

							acrescimo_desconto = "D" if self.desconto.GetValue() else "A"
							marcacao_precos = "T" if self.pd_marc.GetValue() else "F" 

							aTualizaProduto = "UPDATE produtos SET pd_marg='"+str( margem )+"',pd_vdp1='"+str( mreal )+"',pd_pcus='"+str( custo )+"',\
							pd_tpr1='"+str( pco1 )+"',pd_tpr2='"+str( pco2 )+"',pd_tpr3='"+str( pco3 )+"',pd_tpr4='"+str( pco4 )+"',\
							pd_tpr5='"+str( pco5 )+"',pd_tpr6='"+str( pco6 )+"',pd_altp='"+str( ajP )+"',pd_pcfl='"+str( flf )+"',pd_marc='"+str( marcacao_precos )+"',pd_acds='"+str( acrescimo_desconto )+"' WHERE pd_regi='"+str( i[0] )+"'"

							sql[2].execute( aTualizaProduto )
							
						else:	semC +=1
					
					sql[1].commit()
				
				except Exception as _reTornos:

					sql[1].rollback()
					grav = False

				conn.cls(sql[1])
				self.ajustar.SetValue( False )
				self.mAjuste(wx.EVT_BUTTON)
				
				if semC !=0:	sc = u"A T E N Ç Ã O: Produtos não atualizados { "+ semC +" }, sem valor de custo"
				else:	sc = ""

				if grav == False:	alertas.dia(self.painel,"Processo não finalizado...\n\n"+str( _reTornos )+"\n"+(" "*160),"Erro: Atualizando preços e custos")
				if grav == True:	alertas.dia(self.painel,"Preços e custos atualizado...\n\n"+sc+"\n"+(" "*160),"Atualizando preços e custos")
					
	def CalculaPrecos(self):
		
		valorp = Trunca.trunca(1, Decimal( self._pcus ) )
		precop = Trunca.trunca(1, Decimal( self._pcus ) )
			
		margem = Trunca.trunca(1, Decimal( self._marg ) )
		ajuste = Trunca.trunca(1, Decimal( self.pmargem.GetValue() ) )

		if self.ajDescon.GetValue() == True:	margem = ( margem + ajuste ) #-: Ajustar Margem

		if self.ajAcresc.GetValue() == True and login.filialLT[login.identifi][19]!="2":	precop = Trunca.trunca(1, ( valorp + ( valorp * ajuste / 100 ) ) ) #-: Ajuste de Custo
		if self.ajAcresc.GetValue() == True and login.filialLT[login.identifi][19]=="2":	precop = Trunca.trunca(3, ( valorp + ( valorp * ajuste / 100 ) ) ) #-: Ajuste de Custo
		if login.filialLT[login.identifi][19]!="2":	self._tpr1 = Trunca.trunca(1, ( precop + ( precop * margem / 100 ) ) ) #-: Ajuste de Custo
		if login.filialLT[login.identifi][19]=="2":	self._tpr1 = Trunca.trunca(3, ( precop + ( precop * margem / 100 ) ) ) #-: Ajuste de Custo

		mg1 = margem
		pc1 = Trunca.trunca(1, Decimal(self._tpr1) )

		if precop > 0 and pc1 > 0:	real = Trunca.trunca(1, ( ( pc1 - precop ) / pc1 * 100 ) )
		else:	real = '0.000'

		return margem, real, precop
		

class AJListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}
	TipoFilialRL = ""
	
	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr4 = wx.ListItemAttr()
		self.attr5 = wx.ListItemAttr()

		self.attr2.SetBackgroundColour("#E3C3C9")
		self.attr3.SetBackgroundColour("#CC7787")
		self.attr4.SetBackgroundColour("#B07C7C")
		self.attr5.SetBackgroundColour("#608E9D")

		if InformarPrecos.modulos.strip() == "AJUSTES":

			self.InsertColumn(0,  u'ORDEM',  format=wx.LIST_ALIGN_LEFT,width=70)
			self.InsertColumn(1,  u'Código', format=wx.LIST_ALIGN_LEFT,width=115)
			self.InsertColumn(2,  u'Descrição dos Produtos', width=390)
			self.InsertColumn(3,  u'Estoque Fisico',format=wx.LIST_ALIGN_LEFT,width=90)
			self.InsertColumn(4,  u'Preço de Custo',format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(5,  u'Preço de Venda',format=wx.LIST_ALIGN_LEFT,width=100)

			self.InsertColumn(6,  u'Nº Registro do Produto',  format=wx.LIST_ALIGN_LEFT,width=150)
			self.InsertColumn(7,  u'Referência Fabricante',   format=wx.LIST_ALIGN_LEFT,width=200)
			self.InsertColumn(8,  u'Código Barras',           format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(9,  u'Descrição do Fabricante', width=500)
			self.InsertColumn(10,  u'Quantidade',              format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(11, u'Valor Unitario',          format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(12, u'Sub-ToTal',               format=wx.LIST_ALIGN_LEFT,width=100)

			self.InsertColumn(13, u'{%} ST-MVA',              format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(14, u'{%} Média ST',            format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(15, u'{%} I P I',               format=wx.LIST_ALIGN_LEFT,width=100)

			self.InsertColumn(16, u'{%} ST-PorFora',          format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(17, u'{%} Frete',               format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(18, u'{%} Desconto',            format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(19, u'ID-do Registro',          format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(20, u'Entrada-Saida',           format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(21, u'Ajuste',                  width=100)
			self.InsertColumn(22, u'Dados de Preços-Valores', width=500)
			self.InsertColumn(23, u'Preços separados p/Filial', width=500)
			self.InsertColumn(24, u'Preços separados p/Filial { Filias q faz parte }', width=500)
			self.InsertColumn(25, u'Preços separados p/Filial { Pronto p/Gravacao }', width=500)
			self.InsertColumn(26, u'Codigo fiscal primario', width=200)
			self.InsertColumn(27, u'Codigo fiscal secundario', width=200)

		else:

			self.InsertColumn(0,  u'ORDEM',  format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(1,  u'Código', format=wx.LIST_ALIGN_LEFT,width=115)
			self.InsertColumn(2,  u'Descrição dos Produtos', width=390)
			
			self.InsertColumn(3,  u'Quantidade',    format=wx.LIST_ALIGN_LEFT,width=90)
			self.InsertColumn(4,  u'Valor Unitario',format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(5,  u'Sub-ToTal',     format=wx.LIST_ALIGN_LEFT,width=100)

			self.InsertColumn(6,  u'Nº Registro do Produto',  format=wx.LIST_ALIGN_LEFT,width=150)
			self.InsertColumn(7,  u'Referência Fabricante',   format=wx.LIST_ALIGN_LEFT,width=200)
			self.InsertColumn(8,  u'Código Barras',           format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(9,  u'Descrição do Fabricante', width=500)
			self.InsertColumn(10,  u'Quantidade',              format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(11, u'Valor Unitario',          format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(12, u'Sub-ToTal',               format=wx.LIST_ALIGN_LEFT,width=100)

			self.InsertColumn(13, u'{%} ST-MVA',              format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(14, u'{%} Média ST',            format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(15, u'{%} I P I',               format=wx.LIST_ALIGN_LEFT,width=100)

			self.InsertColumn(16, u'{%} ST-PorFora',          format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(17, u'{%} Frete',               format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(18, u'{%} Desconto',            format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(19, u'ID-do Registro',          format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(20, u'Entrada-Saida',           format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(21, u'Ajuste',                  width=100)
			self.InsertColumn(22, u'Dados de Preços-Valores', width=500)
			self.InsertColumn(23, u'Preços separados p/Filial', width=500)
			self.InsertColumn(24, u'Preços separados p/Filial { Filias q faz parte }', width=500)
			self.InsertColumn(25, u'Preços separados p/Filial { Pronto p/Gravacao }', width=500)
			self.InsertColumn(26, u'Codigo fiscal primario', width=200)
			self.InsertColumn(27, u'Codigo fiscal secundario', width=200)
		
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
			
			index = self.itemIndexMap[item]

			cst = False
			if self.itemDataMap[index][26] and len( self.itemDataMap[index][26].split(".") ) == 4:
				if int( self.itemDataMap[index][26].split(".")[2] ) == 500 or int( self.itemDataMap[index][26].split(".")[2] ) == 60:	cst = True

			if self.itemDataMap[index][27] and len( self.itemDataMap[index][27].split(".") ) == 4:
				if int( self.itemDataMap[index][27].split(".")[2] ) == 500 or int( self.itemDataMap[index][27].split(".")[2] ) == 60:	cst = True
				
			if cst and InformarPrecos.modulos.strip() == "AJUSTES":	return self.attr4
			
			if self.itemDataMap[index][23]:	return self.attr5
			if self.itemDataMap[index][21] == "AJUSTE":	return self.attr2

			if item % 2 and self.TipoFilialRL == "T":	return self.attr4
			if item % 2:	return self.attr1
		
	def OnGetItemImage(self, item):

		index = self.itemIndexMap[item]
		if self.itemDataMap[index][23]:	return self.i_orc
		if self.itemDataMap[index][21] == "AJUSTE":	return self.sm_up
		return self.w_idx

	def GetListCtrl(self):	return self


class calcularMargem(wx.Frame):
	
	cdTecla = 0
	
	def __init__(self,parent,id):

		self.p = parent
		mkn    = wx.lib.masked.NumCtrl

		self.p.Disable()
		wx.Frame.__init__(self, parent, 400, 'Produtos: Ajuste de preços {'+str( self.p.filialP )+'}', size=(497,250), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		wx.StaticText(self.painel,-1,"Marcação: ", pos=(15, 10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Comissão: ", pos=(15,30)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Segurança:", pos=(15,50)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Preço_1:", pos=(15, 75)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_2:", pos=(15, 95)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_3:", pos=(15,115)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_4:", pos=(15,135)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_5:", pos=(15,155)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_6:", pos=(15,175)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Real %:", pos=(295, 75)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"AcDc%2:", pos=(295, 95)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"AcDc%3:", pos=(295,115)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"AcDc%4:", pos=(295,135)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"AcDc%5:", pos=(295,155)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"AcDc%6:", pos=(295,175)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Esc-Sair-Voltar\n[ + ]-Restaura valor do campo selecionado\n[ * / F10 ]-Salvar", pos=(5,200)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cfis = wx.StaticText(self.painel,-1,"{ Códigos fiscais }", pos=(363,257))
		self.cfis.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cfis.SetForegroundColour('#7F7F7F')

		indice = self.p.Conferencia.GetFocusedItem()
		cp = self.p.Conferencia.GetItem(indice, 26).GetText().strip()
		cs = self.p.Conferencia.GetItem(indice, 27).GetText().strip()

		cfsp = wx.StaticText(self.painel,-1,"Código fiscal primário:", pos=(5,252))
		cfsp.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		cfss = wx.StaticText(self.painel,-1,"Código fiscal secundário:", pos=(5,267))
		cfss.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		cofp = wx.StaticText(self.painel,-1,"["+str( cp )+"]", pos=(160,252))
		cofs = wx.StaticText(self.painel,-1,"["+str( cs )+"]", pos=(160,267))
		cofp.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		cofs.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		cfsp.SetForegroundColour('#0B569F')
		cfss.SetForegroundColour('#0B569F')
		cofp.SetForegroundColour('#0B569F')
		cofs.SetForegroundColour('#0B569F')

		if cp and len( cp.split('.') ) >= 3 and cp.split('.')[2].isdigit():

			if int( cp.split('.')[2] ) == 500 or int( cp.split('.')[2] ) == 60:

				cfsp.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				cofp.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

				cfsp.SetForegroundColour('#A52A2A')
				cofp.SetForegroundColour('#A52A2A')

		if cs and len( cs.split('.') ) >= 3 and cs.split('.')[2].isdigit():

			if int( cs.split('.')[2] ) == 500 or int( cs.split('.')[2] ) == 60:

				cfss.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				cofs.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

				cfss.SetForegroundColour('#A52A2A')
				cofs.SetForegroundColour('#A52A2A')

		"""   Margens  """
		self.__marg1 = wx.TextCtrl(self.painel, -1,  format( self.p.pd_marg.GetValue(), ',' )+ " %", pos = (70,8), size=(80,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__marg1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__marg2 = wx.TextCtrl(self.painel, -1,  format( self.p.pd_coms.GetValue(), ',' )+ " %", pos = (70,28), size=(80,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__marg2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__marg3 = wx.TextCtrl(self.painel, -1,  format( self.p.pd_mrse.GetValue(), ',' )+ " %", pos = (70,48), size=(80,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__marg3.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__marg1.Enable( False )
		self.__marg2.Enable( False )
		self.__marg3.Enable( False )

		self._marg = mkn(self.painel, 240, value = str( self.p.pd_marg.GetValue() ),  pos = (160 ,5), style = wx.ALIGN_RIGHT|0, integerWidth = 3, fractionWidth = 3, decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self._coms = mkn(self.painel, 243, value = str( self.p.pd_coms.GetValue() ),  pos = (160,25), style = wx.ALIGN_RIGHT|0, integerWidth = 3, fractionWidth = 3, decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self._mrse = mkn(self.painel, 244, value = str( self.p.pd_mrse.GetValue() ),  pos = (160,45), style = wx.ALIGN_RIGHT|0, integerWidth = 3, fractionWidth = 3, decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)

		self._marg.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self._coms.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self._mrse.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		"""   Precos Valores   """

		self.__pr1 = wx.TextCtrl(self.painel, -1,  format( self.p.pd_tpr1.GetValue(), ',' )+" $", pos = (70, 73), size=(80,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__pr1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__pr2 = wx.TextCtrl(self.painel, -1,  format( self.p.pd_tpr2.GetValue(), ',' )+" $", pos = (70, 93), size=(80,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__pr2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__pr3 = wx.TextCtrl(self.painel, -1,  format( self.p.pd_tpr3.GetValue(), ',' )+" $", pos = (70,113), size=(80,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__pr3.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__pr4 = wx.TextCtrl(self.painel, -1,  format( self.p.pd_tpr4.GetValue(), ',' )+" $", pos = (70,133), size=(80,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__pr4.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__pr5 = wx.TextCtrl(self.painel, -1,  format( self.p.pd_tpr5.GetValue(), ',' )+" $", pos = (70,153), size=(80,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__pr5.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__pr6 = wx.TextCtrl(self.painel, -1,  format( self.p.pd_tpr6.GetValue(), ',' )+" $", pos = (70,173), size=(80,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__pr6.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__pr1.Enable( False )
		self.__pr2.Enable( False )
		self.__pr3.Enable( False )
		self.__pr4.Enable( False )
		self.__pr5.Enable( False )
		self.__pr6.Enable( False )

		self._tpr1 = mkn(self.painel, id = 241, value = str( self.p.pd_tpr1.GetValue() ), pos = (160, 70), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self._tpr2 = mkn(self.painel, id = 350, value = str( self.p.pd_tpr2.GetValue() ), pos = (160, 90), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self._tpr3 = mkn(self.painel, id = 351, value = str( self.p.pd_tpr3.GetValue() ), pos = (160,110), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self._tpr4 = mkn(self.painel, id = 352, value = str( self.p.pd_tpr4.GetValue() ), pos = (160,130), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self._tpr5 = mkn(self.painel, id = 353, value = str( self.p.pd_tpr5.GetValue() ), pos = (160,150), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self._tpr6 = mkn(self.painel, id = 354, value = str( self.p.pd_tpr6.GetValue() ), pos = (160,170), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

		self._tpr1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._tpr2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._tpr3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._tpr4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._tpr5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._tpr6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		"""   Precos Margens  """

		self.__dp1 = wx.TextCtrl(self.painel, -1,  self.p.pd_vdp1.GetValue()+" %", pos = (340, 73), size=(78,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__dp1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__dp2 = wx.TextCtrl(self.painel, -1,  str( self.p.pd_vdp2.GetValue() )+" %", pos = (340, 93), size=(78,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__dp2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__dp3 = wx.TextCtrl(self.painel, -1,  str( self.p.pd_vdp3.GetValue() )+" %", pos = (340,113), size=(78,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__dp3.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__dp4 = wx.TextCtrl(self.painel, -1,  str( self.p.pd_vdp4.GetValue() )+" %", pos = (340,133), size=(78,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__dp4.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__dp5 = wx.TextCtrl(self.painel, -1,  str( self.p.pd_vdp5.GetValue() )+" %", pos = (340,153), size=(78,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__dp5.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__dp6 = wx.TextCtrl(self.painel, -1,  str( self.p.pd_vdp6.GetValue() )+" %", pos = (340,173), size=(78,15), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.__dp6.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self._vdp1 = mkn(self.painel, id = -1,  value = str( self.p.pd_vdp1.GetValue() ), pos = (420, 70), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self._vdp2 = mkn(self.painel, id = 231, value = str( self.p.pd_vdp2.GetValue() ), pos = (420, 90), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self._vdp3 = mkn(self.painel, id = 232, value = str( self.p.pd_vdp3.GetValue() ), pos = (420,110), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self._vdp4 = mkn(self.painel, id = 233, value = str( self.p.pd_vdp4.GetValue() ), pos = (420,130), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self._vdp5 = mkn(self.painel, id = 234, value = str( self.p.pd_vdp5.GetValue() ), pos = (420,150), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self._vdp6 = mkn(self.painel, id = 235, value = str( self.p.pd_vdp6.GetValue() ), pos = (420,170), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

		self._vdp1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._vdp2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._vdp3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._vdp4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._vdp5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._vdp6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.__dp1.Enable( False )
		self.__dp2.Enable( False )
		self.__dp3.Enable( False )
		self.__dp4.Enable( False )
		self.__dp5.Enable( False )
		self.__dp6.Enable( False )
		self._vdp1.Enable( False )

		self.acresci = wx.RadioButton(self.painel,-1,"Acréscimo", pos=(248,10),style=wx.RB_GROUP)
		self.descont = wx.RadioButton(self.painel,-1,"Desconto",  pos=(348,10))
		self.marcaca = wx.CheckBox(self.painel, -1,  "Marcação-Valor", pos=(248,36))

		self.marcaca.SetValue( self.p.pd_marc.GetValue()  )
		self.acresci.SetValue( self.p.acrescim.GetValue() )
		self.descont.SetValue( self.p.desconto.GetValue() )

		self.sMargem = wx.RadioButton(self.painel,-1,"Seleciona Margens", pos=(230,197),style=wx.RB_GROUP)
		self.sPrecos = wx.RadioButton(self.painel,-1,"Selecicnao Preços", pos=(230,220))
		self.sAcDesc = wx.RadioButton(self.painel,-1,"AcréscomoDesconto", pos=(355,197))
		self.slTodos = wx.RadioButton(self.painel,-1,"Todos", pos=(355, 220))

		self.sMargem.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.sPrecos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.sAcDesc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.slTodos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.marcaca.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.acresci.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.descont.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.voltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(415,32), size=(34,31))			
		self.gravar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/save20.png", wx.BITMAP_TYPE_ANY), pos=(453,32), size=(34,31))			

		self.voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.gravar.Bind(wx.EVT_BUTTON, self.gravacaoValores)
		self.sMargem.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.sPrecos.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.sAcDesc.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.slTodos.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		
		self.marcaca.Bind(wx.EVT_CHECKBOX, self.evradio)
		self.acresci.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.descont.Bind(wx.EVT_RADIOBUTTON, self.evradio)

		self.Bind(wx.EVT_KEY_UP,self.Teclas)
		self._marg.SetFocus()
		
		if self.cdTecla == 388:	self.sMargem.SetValue( True )
		if self.cdTecla == 390:	self.sPrecos.SetValue( True )
		if self.cdTecla == 392:	self.sAcDesc.SetValue( True )
		if self.cdTecla == 387:	self.slTodos.SetValue( True )

		self.evradio( wx.EVT_RADIOBUTTON )

	def gravacaoValores(self,event):

		self.p.atualizaValores(wx.EVT_BUTTON)
		self.sair(wx.EVT_BUTTON)
		
	def Teclas(self,event):
		
		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		__id     = 0
		if controle !=None:	__id = controle.GetId()

		try:
			
			if __id == 240 and keycode == 388:	self._marg.SetValue( str( self.__marg1.GetValue().split(" %" )[0] ) )
			if __id == 243 and keycode == 388:	self._coms.SetValue( str( self.__marg2.GetValue().split(" %" )[0] ) )
			if __id == 244 and keycode == 388:	self._mrse.SetValue( str( self.__marg3.GetValue().split(" %" )[0] ) )

			if __id == 241 and keycode == 388:	self._tpr1.SetValue( str( self.__pr1.GetValue().split(" $" )[0] ) )
			if __id == 350 and keycode == 388:	self._tpr2.SetValue( str( self.__pr2.GetValue().split(" $" )[0] ) )
			if __id == 351 and keycode == 388:	self._tpr3.SetValue( str( self.__pr3.GetValue().split(" $" )[0] ) )
			if __id == 352 and keycode == 388:	self._tpr4.SetValue( str( self.__pr4.GetValue().split(" $" )[0] ) )
			if __id == 353 and keycode == 388:	self._tpr5.SetValue( str( self.__pr5.GetValue().split(" $" )[0] ) )
			if __id == 354 and keycode == 388:	self._tpr6.SetValue( str( self.__pr6.GetValue().split(" $" )[0] ) )

			if __id == 231 and keycode == 388:	self._vdp2.SetValue( str( self.__dp2.GetValue().split(" %" )[0] ) )
			if __id == 232 and keycode == 388:	self._vdp3.SetValue( str( self.__dp3.GetValue().split(" %" )[0] ) )
			if __id == 233 and keycode == 388:	self._vdp4.SetValue( str( self.__dp4.GetValue().split(" %" )[0] ) )
			if __id == 234 and keycode == 388:	self._vdp5.SetValue( str( self.__dp5.GetValue().split(" %" )[0] ) )
			if __id == 235 and keycode == 388:	self._vdp6.SetValue( str( self.__dp6.GetValue().split(" %" )[0] ) )

			if __id == 240:	self.p.pd_marg.SetValue( str( self._marg.GetValue() ) )
			if __id == 243:	self.p.pd_coms.SetValue( str( self._coms.GetValue() ) )
			if __id == 244:	self.p.pd_mrse.SetValue( str( self._mrse.GetValue() ) )

			if __id == 241:	self.p.pd_tpr1.SetValue( str( self._tpr1.GetValue() ) )
			if __id == 350:	self.p.pd_tpr2.SetValue( str( self._tpr2.GetValue() ) )
			if __id == 351:	self.p.pd_tpr3.SetValue( str( self._tpr3.GetValue() ) )
			if __id == 352:	self.p.pd_tpr4.SetValue( str( self._tpr4.GetValue() ) )
			if __id == 353:	self.p.pd_tpr5.SetValue( str( self._tpr5.GetValue() ) )
			if __id == 354:	self.p.pd_tpr6.SetValue( str( self._tpr6.GetValue() ) )

			if __id == 231:	self.p.pd_vdp2.SetValue( str( self._vdp2.GetValue() ) )
			if __id == 232:	self.p.pd_vdp3.SetValue( str( self._vdp3.GetValue() ) )
			if __id == 233:	self.p.pd_vdp4.SetValue( str( self._vdp4.GetValue() ) )
			if __id == 234:	self.p.pd_vdp5.SetValue( str( self._vdp5.GetValue() ) )
			if __id == 235:	self.p.pd_vdp6.SetValue( str( self._vdp6.GetValue() ) )
			
			"""   Recalcula os valores precos,margens,acrescimos-descontos  """
			rca1,rca2 = self.p.n.calcularProduto(__id,self.p, Filial = self.p.filialP, mostrar = False, retornar_valor = False )
			if rca1 or rca2:
				self.cfis.SetLabel("{ Sem preço custo }")
				self.cfis.SetForegroundColour('#A52A2A')

			if __id != 240:	self._marg.SetValue( str( self.p.pd_marg.GetValue() ) )
			if __id != 243:	self._coms.SetValue( str( self.p.pd_coms.GetValue() ) )
			if __id != 244:	self._mrse.SetValue( str( self.p.pd_mrse.GetValue() ) )
										   
			if __id != 241:	self._tpr1.SetValue( str( self.p.pd_tpr1.GetValue() ) )
			if __id != 350:	self._tpr2.SetValue( str( self.p.pd_tpr2.GetValue() ) )
			if __id != 351:	self._tpr3.SetValue( str( self.p.pd_tpr3.GetValue() ) )
			if __id != 352:	self._tpr4.SetValue( str( self.p.pd_tpr4.GetValue() ) )
			if __id != 353:	self._tpr5.SetValue( str( self.p.pd_tpr5.GetValue() ) )
			if __id != 354:	self._tpr6.SetValue( str( self.p.pd_tpr6.GetValue() ) )
										   
			if __id != 231:	self._vdp2.SetValue( str( self.p.pd_vdp2.GetValue() ) )
			if __id != 232:	self._vdp3.SetValue( str( self.p.pd_vdp3.GetValue() ) )
			if __id != 233:	self._vdp4.SetValue( str( self.p.pd_vdp4.GetValue() ) )
			if __id != 234:	self._vdp5.SetValue( str( self.p.pd_vdp5.GetValue() ) )
			if __id != 235:	self._vdp6.SetValue( str( self.p.pd_vdp6.GetValue() ) )

		except Exception as erros:

			alertas.dia( self, "{ Erro: Alteraçao de valores }\n\n"+str( erros )+"\n"+(" "*140),"Calculo de preços")
			
		"""   Grava se Volta  """
		if keycode == wx.WXK_F10 or keycode == 387: #{ F10 ou * }

			self.p.atualizaValores(wx.EVT_BUTTON)
			self.sair(wx.EVT_BUTTON)
			
		if keycode == 27:	self.sair(wx.EVT_BUTTON)
			
	def evradio(self,event):

		if self.sMargem.GetValue() == True:	m,t,v = True, False,False
		if self.sPrecos.GetValue() == True:	m,t,v = False, True,False
		if self.sAcDesc.GetValue() == True:	m,t,v = True,False,True
		if self.slTodos.GetValue() == True:	m,t,v = True,True,True

		self.p.desconto.SetValue( self.descont.GetValue() )
		self.p.acrescim.SetValue( self.acresci.GetValue() )
		self.p.pd_marc.SetValue( self.marcaca.GetValue() ) 

		self._marg.Enable( m )
		self._coms.Enable( m )
		self._mrse.Enable( m )

		self._tpr1.Enable( t ) 
		self._tpr2.Enable( t )
		self._tpr3.Enable( t )
		self._tpr4.Enable( t )
		self._tpr5.Enable( t )
		self._tpr6.Enable( t )

		self._vdp2.Enable( v )
		self._vdp3.Enable( v )
		self._vdp4.Enable( v )
		self._vdp5.Enable( v )
		self._vdp6.Enable( v )

		if self.sMargem.GetValue() == True:	self._marg.SetFocus()
		if self.sPrecos.GetValue() == True:	self._tpr1.SetFocus()
		if self.sAcDesc.GetValue() == True:	self._vdp2.SetFocus()
		if self.slTodos.GetValue() == True:	self._marg.SetFocus()

	def sair(self,event):
		
		self.p.Enable()

		self.p.reTornaIndice()
		self.Destroy()

	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#327A91")
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Conferência e Ajustes de Preços", 0, 190, 90)

		dc.SetTextForeground("#256275")
		dc.DrawRotatedText("Margens", 150, 60, 90)
		dc.DrawRotatedText("Preços 1-6", 150, 187,90)
		dc.DrawRotatedText("AcréscimoDesconto", 285, 187,90)

		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(11,  1,485, 192,3)
		dc.DrawRoundedRectangle(245, 5,245, 62, 3)
		dc.DrawRoundedRectangle(1,  195,495,50, 3)
		#dc.DrawRoundedRectangle(1,  247,494, 40, 3)


class compraCancela(wx.Frame):
	
	ccFilial = ''
	def __init__(self,parent,id):

		self.p = parent
		self.h = ''

		wx.Frame.__init__(self, parent, 400, 'Produtos: Cancelamento de Compras {'+str( self.ccFilial )+'}', size=(450,250), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaContas = wx.ListCtrl(self.painel, 320,pos=(15,1), size=(434,99),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaContas.SetBackgroundColour('#C4D8EB')
		self.ListaContas.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		self.ListaContas.InsertColumn(0, 'Nº Lançamento', format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListaContas.InsertColumn(1, 'Nº Duplicata',  format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListaContas.InsertColumn(2, 'Nº NF',         format=wx.LIST_ALIGN_LEFT,width=60)
		self.ListaContas.InsertColumn(3, 'Vencimento',    format=wx.LIST_ALIGN_LEFT,width=75)
		self.ListaContas.InsertColumn(4, 'Valor',         format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaContas.InsertColumn(5, 'Fornecedor',    width=400)

		self.hs = wx.StaticText(self.painel,-1,"Historico",   pos=(15,100))
		self.hs.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		_c = wx.StaticText(self.painel,-1,"Cancelamento Compras\nControle: { "+self.p.npedido+" }",  pos=(310,215))
		_c.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_c.SetForegroundColour('#732525')
		
		if self.p.TipoPed == "2":	_c.SetLabel("Cancelamento Acerto\nControle: {"+self.p.npedido+"}")
		
		self.motivo = wx.TextCtrl(self.painel, value='', pos=(15,112), size=(433,98),style=wx.TE_MULTILINE)
		self.motivo.SetBackgroundColour("#7F7F7F")
		self.motivo.SetForegroundColour('#E1E11E')

		voltar      = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(15,212), size=(36,32))
		self.gravar = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(60,212), size=(36,32))

		self.cancelar = wx.CheckBox(self.painel, -1, "Cancelar Parcelas\nContas Apagar", pos=(110,210))
		self.cancelar.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cancelar.SetForegroundColour('#A52A2A')
		self.cancelar.SetValue(True)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.gravar.Bind(wx.EVT_BUTTON, self.cancelarCompra)
		
		self.contasApagar(wx.EVT_BUTTON)
		
	def sair(self,event):	self.Destroy()
	def contasApagar(self,event):

		conn = sqldb()
		sql  = conn.dbc("Produstos: Giro de Produtos, Curva ABC", fil = self.ccFilial, janela = self.painel )
		 
		if sql[0] == True:

			_acha = "SELECT * FROM apagar WHERE ap_ctrlcm='"+str( self.p.npedido )+"' ORDER BY ap_dtvenc"
			achar = sql[2].execute(_acha)
			lista = sql[2].fetchall()

			""" Verifica se ja foi cancelado """
			cance = "SELECT cc_status,cc_cancel FROM ccmp WHERE cc_contro='"+str(self.p.npedido)+"' and cc_status='1' and cc_filial='"+str( self.ccFilial )+"'"
			ccmac = "SELECT cc_status,cc_cancel FROM ccmp WHERE cc_contro='"+str(self.p.npedido)+"' and cc_filial='"+str( self.ccFilial )+"'"
			
			if sql[2].execute( cance ) !=0:

				self.motivo.SetValue('\n  Compra Cancelada!!')
				if self.p.TipoPed == "2":	self.motivo.SetValue('\n  Acerto Cancelado!!')
				if self.p.TipoPed == "4":	self.motivo.SetValue('\nTransferência Cancelado!!')
				self.motivo.SetForegroundColour('#E8E815')
				self.motivo.SetFont(wx.Font(30,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
				self.gravar.Enable(False)
				
			if sql[2].execute( ccmac ) !=0:	self.h = sql[2].fetchall()[0][1]
					
			conn.cls(sql[1])

			if achar == 0:
				self.cancelar.SetValue(False)
				self.cancelar.Enable(False)

			indice = 0
			
			if achar != 0:

				for i in lista:
					
					self.ListaContas.InsertStringItem(indice,i[4]+'-'+i[11])
					self.ListaContas.SetStringItem(indice,1, i[10])
					self.ListaContas.SetStringItem(indice,2, i[5])
					self.ListaContas.SetStringItem(indice,3, format(i[9],"%d/%m/%Y"))
					self.ListaContas.SetStringItem(indice,4, format(i[12],","))
					self.ListaContas.SetStringItem(indice,5, i[2])
					indice +=1
	
	def cancelarCompra(self,event):

		dFi = self.p.rsTa[0][51] #-: Data,Hora,Usuario da Transferencia do pedido para o destino
		cDe = self.p.rsTa[0][53] #-: Nº do Pedido de Controle - Destinos

		if self.p.rsTa[0][27] == "4" and dFi != "" and cDe != "":	self.cancelaTransferencia()
		else:
			
			if self.p.rsTa[0][27] == "4":	Trans = u"- A V I S O -\n1 - Pedido de Transferência com pendencias\n2 - Pedido não enviado ao destino\n3 - Pedido de envio não confeccionado\n\n"
			else:	Trans = ""

			_cancela = wx.MessageDialog(self, Trans +"Confirme para cancelar...\n"+(" "*140),"Compras: Cancelamento",wx.YES_NO|wx.NO_DEFAULT)
			if _cancela.ShowModal() ==  wx.ID_YES:
				
				nRegis = self.p.Conferencia.GetItemCount()
				histor = self.motivo.GetValue()
				indice = 0

				grva = False
				conn = sqldb()
				sql  = conn.dbc("Compras: Cancelamento", fil = self.ccFilial, janela = self.painel )

				if sql[0] == True:

					try:
						
						for i in range( nRegis ):
							
							qT = Decimal( self.p.Conferencia.GetItem(indice,3).GetText() )
							nR = self.p.Conferencia.GetItem( indice,  6).GetText() #-: ID do Produto no cadastro de produtos
							cD = self.p.Conferencia.GetItem( indice,  1).GetText() #-: Codigo Produto
							iP = self.p.Conferencia.GetItem( indice, 19).GetText() #-: ID do Lancamento do Produto
							ES = self.p.Conferencia.GetItem( indice, 20).GetText() #-: Pedido de Acerto de Estoque { E-Entrada - S-Saida }

							DTA = datetime.datetime.now().strftime("%Y/%m/%d")
							HOR = datetime.datetime.now().strftime("%T")
							CAN = datetime.datetime.now().strftime("%Y/%m/%d %T")+' '+login.usalogin
							CCM = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin

							indice +=1

							"""  Atualiza as ultimas compras  """
							if sql[2].execute("SELECT pd_ulcm FROM produtos WHERE pd_regi='"+ nR +"'"):
								
								ultimas_compras = sql[2].fetchone()[0]
								update_compras = u""
								
								if ultimas_compras:
									
									for uc in ultimas_compras.split("\n"):
										
										if uc:

											if str( self.p.npedido ) in uc:	update_compras +=uc.decode("UTF-8") + '|'+ CCM + '\n'
											else:	update_compras +=uc.decode("UTF-8") + '\n'

								if update_compras:	sql[2].execute("UPDATE produtos SET pd_ulcm='"+ update_compras +"' WHERE pd_regi='"+ nR +"'")							
											
							if nF.fu( self.ccFilial ) == "T":	ajuste = "SELECT ef_fisico,ef_esloja FROM estoque WHERE ef_codigo='"+str( cD )+"'"
							else:	ajuste = "SELECT ef_fisico,ef_esloja FROM estoque WHERE ef_idfili='"+str( self.ccFilial )+"' and ef_codigo='"+str( cD )+"'"
							
							if sql[2].execute( ajuste ) != 0:

								#-------: Ajustar estoque no cadastro de produtos
								__esf = sql[2].fetchall()[0]
								esTFisico = __esf[0]
								estolocal = __esf[1]

								if self.p.rsTa[0][27] == "8": #//Estoque local { para lojas com estoque centralizado no galpao }

									if ES == "S":	e_saldo = ( estolocal + qT )
									else:	e_saldo   = ( estolocal - qT )
									
									if nF.fu( self.ccFilial ) == "T":	esToque = "UPDATE estoque SET ef_esloja=( %s ) WHERE ef_codigo=%s"
									else:	esToque = "UPDATE estoque SET ef_esloja=( %s ) WHERE  ef_idfili=%s and ef_codigo=%s"

									if nF.fu( self.ccFilial ) == "T":	sql[2].execute( esToque, ( e_saldo, cD ) )
									else:	sql[2].execute( esToque, ( e_saldo, self.ccFilial, cD ) )

								else:

									if ES == "S":	e_saldo = ( esTFisico + qT )
									else:	e_saldo   = ( esTFisico - qT )

									if nF.fu( self.ccFilial ) == "T":	esToque = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_codigo=%s"
									else:	esToque = "UPDATE estoque SET ef_fisico=( %s ) WHERE  ef_idfili=%s and ef_codigo=%s"

									if nF.fu( self.ccFilial ) == "T":	sql[2].execute( esToque, ( e_saldo, cD ) )
									else:	sql[2].execute( esToque, ( e_saldo, self.ccFilial, cD ) )
									
								#-------: Cancelar no cadastro de ITEMS de compra
								
								canCompra = "UPDATE iccmp SET ic_dtcanc=%s,ic_hocanc=%s,ic_uscanc=%s,ic_cdusca=%s,ic_cancel=%s,\
								ic_qtanca=%s WHERE cc_regist=%s and ic_contro=%s and ic_nregis=%s"
								
								sql[2].execute( canCompra, ( DTA, HOR, login.usalogin, login.uscodigo, '1', esTFisico, iP, self.p.npedido, nR ) )

						#-------: Cancelar no cadastro de Controle de Pedidos de compras
						_DTA = datetime.datetime.now().strftime("%Y/%m/%d")
						_HOR = datetime.datetime.now().strftime("%T")

						histor +="\n\nCancelamento do pedido de Entrada/Saida e RMA: "+str( _DTA )+" "+str( _HOR )+" "+str( login.usalogin )
						if self.h !=None:	histor +="\n\n"+ self.h
						
						canControle = "UPDATE ccmp SET cc_ndanfe=%s,cc_cancel=%s,cc_dtcanc=%s,cc_hrcanc=%s,cc_uscanc=%s,\
						cc_uccanc=%s,cc_status=%s WHERE cc_contro=%s and cc_filial='"+str( self.ccFilial )+"'"
						
						""" Cancela no gerenciado de NFs, de pedidos de compras  """
						cancela_compras = "UPDATE comprasxml SET nc_cancel='"+ CCM +"' WHERE nc_contro='"+ self.p.npedido +"'"
						
						sql[2].execute( canControle, ('',histor,DTA,HOR,login.usalogin,login.uscodigo,'1',self.p.npedido) )
						sql[2].execute( cancela_compras )

						#-------: Cancelar no contas Apagar
						if self.cancelar.GetValue() == True:

							_sa = "SELECT * FROM apagar WHERE ap_ctrlcm='"+str( self.p.npedido )+"'"
							if sql[2].execute(_sa) !=0:
								
								_sar = sql[2].fetchall()
								for i in _sar:
									
									_nl = i[4] #--: Numero Lancamento
									_np = i[11] #-: Numero Parcela
									_hs = ''
									if i[31] != None:	_hs = i[31] if type( i[31] ) == unicode else i[31].decode("UTF-8")
									his = u"Cancelamento atraves do cancelamento da compra\nEmissão: "+str( DTA )+" "+str( HOR )+" {"+login.usalogin+"}\nMotivo: "+histor+"\n\nProximo...\n\n"+_hs
									
									_ca = "UPDATE apagar SET ap_dtcanc=%s,ap_hocanc=%s,ap_usacan=%s,ap_status=%s,ap_cdusca=%s,ap_histor=%s WHERE ap_ctrlcm=%s and ap_parcel=%s"
									sql[2].execute(_ca,(DTA,HOR,login.usalogin,"2",login.uscodigo,his,_nl,_np))

						sql[1].commit()
						grva = True

					except Exception as _reTornos:
								
						sql[1].rollback()
						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
						
					conn.cls(sql[1])

					if grva == False:	alertas.dia(self.painel,u"Processo interrompido, cancelamento de compras!!\n\nRetorno: "+ _reTornos ,"Compras: Cancelamento")			
					if grva == True:

						self.p.p.selecionar()
						alertas.dia(self.painel,u"Compras: Cancelamento concluido...\n"+(" "*90),"Compras: Cancelamento")
						self.sair(wx.EVT_BUTTON)

	def desenho(self,event):
			
		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#6A92B9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Cancelamentos compras e ajustes", 0, 247, 90)

	def cancelaTransferencia(self):
		
		nPc = self.p.rsTa[0][30] #-: Numero do Pedido de Controle na origem
		Tpd = self.p.rsTa[0][27] #-: Tipo de Pedido
		flo = self.p.rsTa[0][48] #-: Filial de Origem
		fld = self.p.rsTa[0][49] #-: Filial de Destino
		dTr = self.p.rsTa[0][50] #-: Data,Hora,Usuario do pedido de Transferencia
		dFi = self.p.rsTa[0][51] #-: Data,Hora,Usuario da Transferencia do pedido para o destino
		cOr = self.p.rsTa[0][52] #-: Nº do Pedido de Controle - Origem
		cDe = self.p.rsTa[0][53] #-: Nº do Pedido de Controle - Destino

		cTrans = wx.MessageDialog(self,"Cancelamento de Transferência entre Filiais\n\nFilial Origem.: "+str( flo )+" Controle: "+str( cOr )+"\nFilial Destino: "+str( fld )+" Controle: "+str( cDe )+"\n\nConfirme para cancelar !!\n"+(" "*140),"Compras: Cancelamento",wx.YES_NO|wx.NO_DEFAULT)
		if cTrans.ShowModal() !=  wx.ID_YES:	return

		pen = penden = reTorno = ""

		if Tpd != "4":	pen +="1-Tipo de pedido incompativel { "+str( Tpd )+" }\n"
		if flo == "":	pen +="2-Filial origem, vazia\n"
		if fld == "":	pen +="3-Filial destino, vazia\n"
		if dTr == "":	pen +="4-Informações do pedido de transferência vazio\n"
		if dFi == "":	pen +="5-Informações de pedido transferido vazio\n"
		if cOr == "":	pen +="6-Pedido de Controle da origem vazio\n"
		if cDe == "":	pen +="7-Pedido de Controle do destino vazio\n"

		if pen != "":	alertas.dia(self.painel,u"{ Pendências p/Cancelamento }\n\n"+str( pen )+(" "*120),"Compras: Cancelamento")
		else:
			
			nRegis = self.p.Conferencia.GetItemCount()
			histor = self.motivo.GetValue()
			
			nachor = 0 #-: Nao localizado na origem
			nachds = 0 #-: Nao localizado no destino
			
			indice = 0
			Locais = False

			if nF.rF( cdFilial = flo ) == nF.rF( cdFilial = fld ):	Locais = True
				
			conn = sqldb()
			sql1  = conn.dbc("1-Produtos-Transferência-Cancelamento\nFilial Origem.: "+str( flo )+"\nFilial Destino: "+str( fld ), fil = flo, janela = self.painel ) #-: Origem
			if Locais == True:	sql2 = sql1
			else:	sql2  = conn.dbc("2-Produtos-Transferência-Cancelamento\nFilial Origem.: "+str( flo )+"\nFilial Destino: "+str( fld ), fil = fld, janela = self.painel ) #-: Destino

			if sql1[0] !=True:	penden += "1 - Inacessível filial de origem { "+str( flo )+" }\n"
			if sql2[0] !=True:	penden += "2 - Inacessível filial de destino { "+str( fld )+" }\n"

			if sql1[0] == True and sql2[0] == True:

				_roll = False
				#try:
				
				"""   Pesquisa os ITEMS   """
				spo = sql1[2].execute("SELECT * FROM iccmp WHERE ic_contro='"+str( nPc )+"'")
				rso = sql1[2].fetchall()
				
				spd = sql2[2].execute("SELECT * FROM iccmp WHERE ic_contro='"+str( cDe )+"'")
				rsd = sql2[2].fetchall()

				if spo == 0:	penden += "3 - Não localizou items na origem\n"
				if spd == 0:	penden += "4 - Não localizou items no destino\n"
				
				if spo !=0 and spd !=0:

					DTA = datetime.datetime.now().strftime("%Y/%m/%d")
					HOR = datetime.datetime.now().strftime("%T")

					"""   Cancelamento Cadastro de Controle de Pedidos   """
					caC = "UPDATE ccmp  SET cc_ndanfe=%s,cc_cancel=%s,cc_dtcanc=%s,cc_hrcanc=%s,cc_uscanc=%s,cc_uccanc=%s,cc_status=%s WHERE cc_contro=%s and cc_filial=%s"
					cc1 = sql1[2].execute( caC, ( '',histor, DTA, HOR, login.usalogin, login.uscodigo, '1', nPc, flo ))
					cc2 = sql2[2].execute( caC, ( '',histor, DTA, HOR, login.usalogin, login.uscodigo, '1', cDe, fld ))

					if cc1 == 0:	penden += u"5 - Não foi cancelado no controle da origem\n"
					if cc2 == 0:	penden += u"6 - Não foi cancelado no controle do destino\n"

					can = "UPDATE iccmp SET ic_dtcanc=%s,ic_hocanc=%s,ic_uscanc=%s,ic_cdusca=%s,ic_cancel=%s,ic_qtanca=%s WHERE cc_regist=%s and ic_contro=%s and ic_nregis=%s and ic_cdprod=%s"
					aTD = "UPDATE estoque SET ef_fisico=( %s ) WHERE  ef_idfili=%s and ef_codigo=%s"
					
					if nF.fu( flo ) == "T":	aTE = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_codigo=%s"
					else:	aTE = "UPDATE estoque SET ef_fisico=( %s ) WHERE  ef_idfili=%s and ef_codigo=%s"

					"""   Cancelamento na Origem    """
					for io in rso:

						qT1 = io[10] #-: Quantidade
						nR1 = io[58] #-: ID do Produto no cadastro de produtos
						cD1 = io[59] #-: Codigo Produto
						iP1 = io[0] #--: ID do Lancamento do Produto
						ES1 = io[66] #-: Pedido de Acerto de Estoque { E-Entrada - S-Saida }

						DTA1 = datetime.datetime.now().strftime("%Y/%m/%d")
						HOR1 = datetime.datetime.now().strftime("%T")

						"""    Apura o Estoque fisico atual p/Gravar no Estoque fisico anterior ao cancelamento    """
						if nF.fu( flo ) == "T":	efo = sql1[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_codigo='"+str( cD1 )+"'" ) #-: Apura estoque fisico na origem
						else:	efo = sql1[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( flo )+"' and ef_codigo='"+str( cD1 )+"'" ) #-: Apura estoque fisico na origem

						if efo !=0:	FSo = sql1[2].fetchall()[0][0]
						else:	FSo = Decimal("0.0000")
						
						if efo == 0:	nachor +=1
						if efo == 0:	penden += u"7 - Não foi Apurado o estoque fisico na origem\n"

						o_saldo = ( FSo + qT1 )

						if nF.fu( flo ) == "T":	es1 = sql1[2].execute( aTE, ( o_saldo, cD1 ) ) #-------------------------------------: Atualiza Estoque Fisico
						else:	es1 = sql1[2].execute( aTE, ( o_saldo, flo, cD1 ) ) #------------------------------------------------: Atualiza Estoque Fisico
						ei1 = sql1[2].execute( can, ( DTA1, HOR1, login.usalogin, login.uscodigo, '1', FSo, iP1, nPc, nR1, cD1 ) ) #-: Cancela em items

						if es1 == 0:	penden += u"8 - Não foi Atualizado estoque fisico na origem\n"
						if ei1 == 0:	penden += u"9 - Não foi Cancelado items na origem\n"

					"""   Cancelamento no Destino    """
					for de in rsd:

						qT2 = de[10] #-: Quantidade
						nR2 = de[58] #-: ID do Produto no cadastro de produtos
						cD2 = de[59] #-: Codigo Produto
						iP2 = de[0] #--: ID do Lancamento do Produto
						ES2 = de[66] #-: Pedido de Acerto de Estoque { E-Entrada - S-Saida }

						DTA2 = datetime.datetime.now().strftime("%Y/%m/%d")
						HOR2 = datetime.datetime.now().strftime("%T")

						""" Apura o Estoque fisico atual p/Gravar no Estoque fisico anterior ao cancelamento """
						efd = sql2[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( fld )+"' and ef_codigo='"+str( cD2 )+"'" ) #-: Apura estoque fisico no destino

						if efd !=0:	FSd = sql2[2].fetchall()[0][0]
						else:	FSd = Decimal("0.0000")
						if efd == 0:	nachds +=1
						if efd == 0:	penden += u"10- Não foi Apurado o estoque fisico no destino\n"

						d_saldo = ( FSd - qT2 )

						es2 = sql2[2].execute( aTD, ( d_saldo, fld, cD2 ) ) #---------------------------------------------------: Atualiza Estoque Fisico
						ei2 = sql2[2].execute( can, ( DTA2, HOR2, login.usalogin, login.uscodigo, '1', FSd, iP2, cDe, nR2, cD2 ) ) #-: Cancela em items

						if es2 == 0:	penden += u"11- Não foi Atualizado estoque fisico no destino\n"
						if ei2 == 0:	penden += u"12- Não foi Cancelado items no destino\n"

					grv1 = False
					grv2 = False
					if penden == "":
						
						sql2[1].commit()
						grv1 = True
						
					if penden == "" and grv1 == True:
						
						sql1[1].commit()
						grv2 = True

					if penden !="":
						
						sql1[1].rollback()
						if Locais == False:	sql2[1].rollback()
						_roll = True
						
					if grv2 != True:	penden += u"13- Problema na finalizao na origem\n"
					if grv1 != True:	penden += u"\n14- Problema na finalização no destino\n"

			if sql1[0] == True:	conn.cls( sql1[1] )	
			if sql2[0] == True and Locais == False:	conn.cls( sql2[1] )
			
			if penden == "":	penden = u"Cancelamento de Transferência Finalizada com sucesso !!"
			alertas.dia(self.painel,"{ Cancelamento de Transferência entre Filiais }\n\n"+str( penden )+"\n"+(" "*160),"Cancelamento de Transferência entre Filiais")
			self.sair(wx.EVT_BUTTON)


class InstrucaoBoleto(wx.Frame):
	
	CodigId = ''
	
	def __init__(self,parent,id):

		self.p = parent
		
		if id == 444:	self.ibFFilial = self.p.filrc #-: Acesso pelo contas areceber
		else:	self.ibFFilial = self.p.cFcFilial

		wx.Frame.__init__(self, parent, 400, 'Fornecedor Bancos: Instrução do boleto bancario {'+str( self.ibFFilial )+'}', size=(700,140), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.Instrucao = wx.TextCtrl(self.painel,-1,value="", pos=(40,0), size=(655,137),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.Instrucao.SetBackgroundColour('#4D4D4D')
		self.Instrucao.SetForegroundColour('#EFEFAD')
		self.Instrucao.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	
		gravar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(1,62),  size=(36,34))				
		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(1,102), size=(36,34))				
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		gravar.Bind(wx.EVT_BUTTON, self.aTualizar)
		self.buscarInstrucao()
	
	def sair(self,event):	self.Destroy()
	def buscarInstrucao(self):

		conn = sqldb()
		sql  = conn.dbc("Fornecedor Bancos: Instrução do Boleto Bancario", fil = self.ibFFilial, janela = self.painel )
				
		if sql[0] == True:

			_ins = "SELECT fr_insbol FROM fornecedor WHERE fr_regist='"+str( self.CodigId )+"'"
			_ach = sql[2].execute(_ins)
			if _ach !=0:
				
				rs = sql[2].fetchall()[0][0]
				if rs !=None:	self.Instrucao.SetValue(rs)
				
			conn.cls(sql[1])
		
	def aTualizar(self,event):		

		conn = sqldb()
		sql  = conn.dbc("Fornecedor Bancos: Instrução do Boleto Bancario", fil = self.ibFFilial, janela = self.painel )
		grv  = False
				
		if sql[0] == True:

			try:
				
				grava = "UPDATE fornecedor SET fr_insbol=%s WHERE fr_regist=%s"
				sql[2].execute( grava, ( self.Instrucao.GetValue(), self.CodigId ) )
				sql[1].commit()
				grv = True

			except Exception, _reTornos:	sql[1].rollback()
	
			conn.cls(sql[1])
	
			if grv == False:	alertas.dia(self.painel,u"Atualização não concluida !!\n \nRetorno: "+str(_reTornos),"Retorno")	
			if grv == True:
				
				alertas.dia(self.painel,u"Atualização da Instrução do Boleto [ OK ] !!\n"+(" "*100),"Fornecedor Bancos: Instrução do Boleto Bancario")	
				self.sair(wx.EVT_BUTTON)

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#A52A2A") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Instrução\ndo boleto", 5, 58, 90)

""" Relatorios """
class ProdutosRelacionar(wx.Frame):

	def __init__(self, parent,id):
		
		self.p = parent
		self.i = impressao()
		self.c = relcompra()
		
		self.pRpFilial = self.p.pRFilial

		self.p.Disable()
		
		indice = self.p.RLTprodutos.GetFocusedItem()
		self.codigo = self.p.RLTprodutos.GetItem(indice, 0).GetText()
		self.descri = self.p.RLTprodutos.GetItem(indice, 1).GetText()
		
		wx.Frame.__init__(self, parent, id, 'Produtos: Relação-Relatorios', size=(880,400), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.RLCprodutos = RLCListCtrl(self.painel, 300 ,pos=(15,50), size=(865,350),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)
		
		self.RLCprodutos.SetBackgroundColour('#A8C2DB')
		self.RLCprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.RLCprodutos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.impresDav)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,u"Período Inicial", pos=(2,  5)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Período Final",   pos=(125,5)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Código/Descrição do Produto", pos=(250,5)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		oco = wx.StaticText(self.painel,-1,u"Ocorrências", pos=(800,5))
		oco.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		oco.SetForegroundColour('#1C72C6')

		self.oc = wx.StaticText(self.painel,-1,u"", pos=(800,20))
		self.oc.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.oc.SetForegroundColour('#1C72C6')

		"""  Determina datas """
		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(0,  18), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(123,18), size=(120,25))

		#d,m,y = str( self.p.dp ).split('/')
		#self.dindicial.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))
		self.dindicial.SetValue(self.p.dindicial.GetValue())
		self.datafinal.SetValue(self.p.datafinal.GetValue())

		self.produto = wx.TextCtrl(self.painel, -1, '['+str(self.codigo)+'] '+str(self.descri), pos=(247,18),   size=(450,23),style=wx.TE_PROCESS_ENTER)
		self.produto.SetBackgroundColour('#E5E5E5')
		self.produto.SetForegroundColour('#406D99')
		self.produto.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		avanca = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/executa.png", wx.BITMAP_TYPE_ANY), pos=(710, 10), size=(36,34))				
		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltap.png",  wx.BITMAP_TYPE_ANY), pos=(750, 10), size=(36,34))				

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		avanca.Bind(wx.EVT_BUTTON, self.selecionar)
		
		self.selecionar(wx.EVT_BUTTON)

	def impresDav(self,event):
				
		indice    = self.RLCprodutos.GetFocusedItem()
		NumeroDav = self.RLCprodutos.GetItem(indice,1).GetText()

		if self.RLCprodutos.GetItem(indice,8).GetText() == "CMP":	self.c.compras( self, NumeroDav, "1", Filiais = self.pRpFilial, mostrar = True )
		else:

			Devolucao = ""
			if self.RLCprodutos.GetItem(indice,8).GetText() == "DEV":	Devolucao = "DEV"
			self.i.impressaoDav(NumeroDav,self,True,True,Devolucao,"",  servidor = self.pRpFilial, codigoModulo = "", enviarEmail = "" )
			self.i.impressaoDav(NumeroDav,self,True,False,Devolucao,"", servidor = self.pRpFilial, codigoModulo = "", enviarEmail = "")

	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()

	def selecionar(self,event):

		dI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		dF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Produtos...", fil = self.pRpFilial, janela = self.painel )
		
		if sql[0] == True:

			""" Eliminando dados do Temporario """
			eliminar = "DELETE FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' and tc_relat='MOVIM'"
			sql[2].execute(eliminar)
			sql[1].commit()

			Compra = "SELECT * FROM iccmp  WHERE ic_lancam>='"+str( dI )+"' and ic_lancam<='"+str( dF )+"' and ic_cdprod='"+str( self.codigo )+"' and ic_cancel='' and ic_tipoen='1'"
			Vendas = "SELECT * FROM idavs  WHERE it_lanc>='"+str( dI )+"' and it_lanc<='"+str( dF )+"' and it_codi='"+str( self.codigo )+"' and it_canc='' and it_futu!='T' and it_tped='1'"
			Devolu = "SELECT * FROM didavs WHERE it_lanc>='"+str( dI )+"' and it_lanc<='"+str( dF )+"' and it_codi='"+str( self.codigo )+"' and it_canc='' and it_futu!='T' and it_tped='1'"

			if self.p.rFilial.GetValue() == True:

				Compra = Compra.replace("WHERE","WHERE ic_filial='"+str( self.pRpFilial )+"' and")
				Vendas = Vendas.replace("WHERE","WHERE it_inde='"+str( self.pRpFilial )+"' and")
				Devolu = Devolu.replace("WHERE","WHERE it_inde='"+str( self.pRpFilial )+"' and")

			pCompra = sql[2].execute(Compra)
			rCompra = sql[2].fetchall()
	
			pVendas = sql[2].execute(Vendas)
			rVendas = sql[2].fetchall()

			pDevolu = sql[2].execute(Devolu)
			rDevolu = sql[2].fetchall()

			self.oc.SetLabel("{"+str( pCompra )+"}-{"+str( pVendas )+"}-{"+str( pDevolu )+"}")

			""" Adicionando Compra """
			if pCompra != 0:

				for c in rCompra:
					
					filial = c[75]
					numdav = c[1]
					emissa = c[43]
					horaem = c[44]
					qTcomp = c[10]
					vender = c[76]
					fornec = c[3]
					custo  = c[48]
					inCompra = "INSERT INTO tmpclientes (tc_usuari,tc_inndat,tc_nmvc,tc_codi,tc_barr,tc_relat,tc_quant1,tc_hora,tc_filial,tc_nome,tc_valor1,tc_valor3) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					sql[2].execute(inCompra,(login.usalogin,emissa,vender,numdav,"CMP","MOVIM",qTcomp,horaem,filial,fornec,custo,'0.000'))

			""" Adicionando Vendas """
			if pVendas != 0:

				for v in rVendas:
					
					filial = v[49]
					numdav = v[2]
					emissa = v[67]
					horaem = v[68]
					qTvend = v[12]
					vender = v[46]
					client = v[84]
					pcusto = v[77]
					pvenda = v[11]
					inVendas = "INSERT INTO tmpclientes (tc_usuari,tc_inndat,tc_nmvc,tc_codi,tc_barr,tc_relat,tc_quant2,tc_hora,tc_filial,tc_nome,tc_valor1,tc_valor3) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					sql[2].execute(inVendas,(login.usalogin,emissa,vender,numdav,"VND","MOVIM",qTvend,horaem,filial,client,pcusto,pvenda))

			""" Adicionando Devolucao """
			if pDevolu != 0:

				for d in rDevolu:
					
					filial = d[49]
					numdav = d[2]
					emissa = d[67]
					horaem = d[68]
					qTdevo = d[12]
					vender = d[46]
					client = d[84]
					pcusto = d[77]
					pvenda = d[11]
					
					inDevolu = "INSERT INTO tmpclientes (tc_usuari,tc_inndat,tc_nmvc,tc_codi,tc_barr,tc_relat,tc_quant3,tc_hora,tc_filial,tc_nome,tc_valor1,tc_valor3) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					sql[2].execute(inDevolu,(login.usalogin,emissa,vender,numdav,"DEV","MOVIM",qTdevo,horaem,filial,client,pcusto,pvenda))
					
			sql[1].commit()
			conn.cls(sql[1])

			self.leituraTemporario(wx.EVT_BUTTON)

	def leituraTemporario(self,event):
				
		conn = sqldb()
		sql  = conn.dbc("Produtos: Giro de Produtos, Curva ABC...", fil = self.pRpFilial, janela = self.painel )

		_registros = 0
		relacao = {}
		
		if sql[0] == True:

			""" Leitura dos dados """
			leitura = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"' and tc_relat='MOVIM' ORDER BY tc_inndat"
			_lei = sql[2].execute(leitura)
			_res = sql[2].fetchall()
			conn.cls(sql[1])

			if _lei > 0:
				
				for i in _res:
					
					emissao = ""
					compra  = vendas = devolu = custo = venda = ""
					_vnd = _dev = Decimal("0.0000")
					if i[10] !=None:	emissao = i[10].strftime("%d/%m/%Y")+" "+str(i[28])+"  "+str(i[9])
					if i[25] !=None and i[25] > 0:	compra = format(i[25],',') 
					if i[26] !=None and i[26] > 0:	vendas = format(i[26],',')
					if i[27] !=None and i[27] > 0:	devolu = format(i[27],',')
					if i[30] !=None and i[30] > 0:	custo  = format(i[30],',')
					if i[32] !=None and i[32] > 0:	venda  = format(i[32],',')

					if i[26] !=None:	_vnd = i[26]
					if i[27] !=None:	_dev = i[27]
					
					saldo = vendas
					if _vnd > _dev:	saldo = format( (_vnd-_dev), ',' )

					relacao[_registros] = str(i[29]),str(i[16]),emissao,str(i[18]),compra,vendas,devolu,saldo,i[17],custo,venda
					_registros +=1

		self.RLCprodutos.SetItemCount(_registros)
		RLCListCtrl.itemDataMap  = relacao
		RLCListCtrl.itemIndexMap = relacao.keys()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		
		dc.SetTextForeground("#1A528A")
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Produtos: Relatorios { Movimentação do Produto }", 0, 395, 90)
		
class RLCListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):

		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour('#A5C6E6')
		self.attr2.SetBackgroundColour('#849CB3')
		self.attr3.SetBackgroundColour('#9CB0C3')

		self.InsertColumn(0, 'Filial', width=70)
		self.InsertColumn(1, 'Nº DAV/Pedido', format=wx.LIST_ALIGN_LEFT,width=115)
		self.InsertColumn(2, 'Emissão', width=90)
		self.InsertColumn(3, 'Descrição Cliente/Fornecedor', width=270)
		self.InsertColumn(4, 'Compra', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(5, 'Venda', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(6, 'Devolução', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(7, 'Saldo de Venda', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(8, 'Tipo', width=50)
		self.InsertColumn(9, 'Preço de Custo', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(10,'Preço de Venda', format=wx.LIST_ALIGN_LEFT,width=100)
		
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
			
			index = self.itemIndexMap[item]
			if self.itemDataMap[index][8] == "VND":	return self.attr2
			if self.itemDataMap[index][8] == "CMP":	return self.attr3
			if item % 2:	return self.attr1
			
	def GetListCtrl(self):	return self			

	def OnGetItemImage(self, item):

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if self.itemDataMap[index][8] == "VND":	return self.i_orc
			if self.itemDataMap[index][8] == "CMP":	return self.e_rma
			return self.e_est

""" Etiquetas de Produtos """
class eTiqueTas:
	
	def eTiqueTa01(self,prd):

		""" 1 Carreira 107 x 25 """
		
		_prd = prd.split('|')
		GT01 = chr(2)+'o0000\n'
		GT02 = chr(2)+'M0300\n'
		GT03 = chr(2)+'c0000\n'
		GT04 = chr(2)+'f10\n'
		GT05 = chr(2)+'e\n'
		GT06 = chr(2)+'LC0000\n'

		GT07 = 'H10\n' #Intensidade da Impressao
		GT08 = 'D11\n' #Largura e altura do caracter desenhado
		GT09 = 'SF\n'
		GT10 = 'PF\n'
		GT11 = 'R0000\n'
		GT12 = 'z\n'
		GT13 = 'W\n'
		GT14 = '^01\n'

		#		GT15 = '131100300700015'+login.emfantas+"\n"
		GT15 = '131100300700015'+login.emfantas+"  R$"+format( Decimal( _prd[6].strip() ),'.2f')+"\n"
		GT16 = '121100300550015'+"Produto.: "+_prd[2]+"\n"
		GT17 = '121100400400015'+"Endereco: "+_prd[5]+"  { ["+_prd[3]+"] [ "+_prd[4]+"] }\n"
		GT18 = '121100300200015'+"Codigo..: "+_prd[0]+(" "*2)+"Barras: "+_prd[1]+"\n"
		GT19 = '1F2203500050015'+_prd[1]
		
		GT20 = 'Q0001\n' # +strzero(_quanti,4) // 0001'
		GT21 = 'E\n' #Ejetar

		return GT01+GT02+GT03+GT04+GT05+GT06+GT07+GT08+GT09+GT10+GT11+GT12+GT13+GT14+GT15+GT16+GT17+GT18+GT19+GT20+GT21

	def eTiqueTa02(self,prd):

		""" 1 Carreira 107 x 25 """
		
		_prd = prd.split('|')
		GT01 = chr(2)+'o0000\n'
		GT02 = chr(2)+'M0300\n'
		GT03 = chr(2)+'c0000\n'
		GT04 = chr(2)+'f10\n'
		GT05 = chr(2)+'e\n'
		GT06 = chr(2)+'LC0000\n'

		GT07 = 'H10\n' #Intensidade da Impressao
		GT08 = 'D11\n' #Largura e altura do caracter desenhado
		GT09 = 'SF\n'
		GT10 = 'PF\n'
		GT11 = 'R0000\n'
		GT12 = 'z\n'
		GT13 = 'W\n'
		GT14 = '^01\n'

		codigo = _prd[0].strip()
		if _prd[1]:	codigo = _prd[1].strip()
		GT15 = '131100300750010'+login.emfantas+"\n"
		GT24 = '121200100800165'+'CODIGO:'+str( int( _prd[0] ) )+"\n"
		GT16 = '121100300540010'+"Fabricante: "+_prd[4].strip()+"\n"
		GT17 = '121100300650010'+"Produto: "+_prd[2].strip()+"\n"
		GT18 = '1F2203500050015'+codigo+"\n"
		GT19 = '121200100200120['+_prd[5].strip()+"]\n" #-: Endereco
		GT20 = '121100100090120['+_prd[3].strip()+"]\n" #-: Grupo
		GT21 = '131200100200218R$'+format( Decimal( _prd[6].strip() ),'.2f')+"\n" #-: Preco
		
		GT22 = 'Q0001\n' # +strzero(_quanti,4) // 0001'
		GT23 = 'E\n' #Ejetar

		return GT01+GT02+GT03+GT04+GT05+GT06+GT07+GT08+GT09+GT10+GT11+GT12+GT13+GT14+GT15+ GT24 +GT16+GT17+GT18+GT19+GT20+GT21+GT22+GT23

	def eTiqueTa04(self,prd):
		
		GT01 = chr(2)+'o0220\n'
		GT02 = chr(2)+'M0000\n'
		GT03 = chr(2)+'c0000\n'
		GT04 = chr(2)+'f10\n' #-: Alinhamento esquerdo
		GT05 = chr(2)+'e\n'
		GT06 = chr(2)+'LC0000\n'
		GT07 = 'H10\n' #--------: Intensidade da Impressao
		GT08 = 'D11\n' #--------: Largura e altura do caracter desenhado
		GT09 = 'SF\n'
		GT10 = 'PF\n'
		GT11 = 'R0000\n'
		GT12 = 'z\n'
		GT13 = 'W\n'
		GT14 = '^01\n'
		
		col = 0
		PT01 = PT02 = PT03 = PT04 = ''
		for i in prd.split('\n'):
			
			_prd = i.split('|')
			if _prd[0] !='':
				
				PT01 += '111100700420'+str((col+9)).zfill(3)+login.emfantas+"\n"
				PT02 += '111100700350'+str((col+9)).zfill(3)+_prd[2]+"\n" 
				PT03 += '121100300350'+str(col).zfill(3)+"R$ "+format( Decimal( _prd[6].strip() ),'.2f')+"\n"
				PT04 += "1F1202000050"+str(col).zfill(3)+_prd[1]+"\n"
				col +=99
				
				
		GT15 = 'Q0004\n'			
		GT16 = 'E\n'

		return GT01+GT02+GT03+GT04+GT05+GT06+GT07+GT08+GT09+GT10+GT11+GT12+GT13+GT14+ PT01+PT02+PT03+PT04 +GT15+GT16

	def eTiqueTa05(self,prd):
		
		GT01 = chr(2)+'o0220\n'
		GT02 = chr(2)+'M0000\n'
		GT03 = chr(2)+'c0000\n'
		GT04 = chr(2)+'f10\n' #-: Alinhamento esquerdo
		GT05 = chr(2)+'e\n'
		GT06 = chr(2)+'LC0000\n'
		GT07 = 'H10\n' #--------: Intensidade da Impressao
		GT08 = 'D15\n' #--------: Largura e altura do caracter desenhado
		GT09 = 'SF\n'
		GT10 = 'PF\n'
		GT11 = 'R0000\n'
		GT12 = 'z\n'
		GT13 = 'W\n'
		GT14 = '^01\n'
		
		col = 0
		PT01 = PT02 = PT03 = PT04 = ''
		for i in prd.split('\n'):
			
			_prd = i.split('|')
			if _prd[0] !='':
				print _prd
				PT01 += '111100700420'+str((col+9)).zfill(3)+login.emfantas+"\n"
				PT02 += '111100700350'+str((col+9)).zfill(3)+_prd[2]+"\n" 
				PT03 += '121100300350'+str(col).zfill(3)+"R$ "+format( Decimal( _prd[6].strip() ),'.2f')+"\n"
				PT04 += "1F1202000050"+str(col).zfill(3)+_prd[1]+"\n"
				col +=44
				
				
		GT15 = 'Q0004\n'			
		GT16 = 'E\n'

		return GT01+GT02+GT03+GT04+GT05+GT06+GT07+GT08+GT09+GT10+GT11+GT12+GT13+GT14+ PT01+PT02+PT03+PT04 + GT15+ GT16
		#return GT01+GT02+GT03+GT04+GT05+GT06+GT07+GT08+GT09+GT10+GT11+GT12+GT13+GT14+ PT01 + GT15+ GT16

#-: Ultimos ajuste de preços
	def ultimosAjustesPrecos(self, lisTap ):

		ulTimaPrc = ""
		indice = 0
		for x in lisTap.split("\n"):
			
			if x !="":
					
				cm = ""
				x1 = x.split("[p]")
				p1 = x1[0].split("|")
				p2 = x1[1].split("|")
				
				if len( x1 ) == 3:	cm = x1[2]

				if indice <= 1:	ulTimaPrc +=p2[3]+"   "
				
				indice +=1
		
		return ulTimaPrc	

	def cfreteadm(self,para):
		
		if login.usalogin.upper() == "LYKOS" and login.administrador.upper() == "ADMINISTRACAO" or login.administrador.upper() == "ADMINISTRACAO-APAGAR":

			adm_frame=blqadmsystem(parent=para,id=-1)
			adm_frame.Centre()
			adm_frame.Show()

		else:	alertas.dia( para, "{ Informações do sistema }\n\n- None"+(" "*120),"Informa system")
		

from cadfretes import blqadmsystem		

""" Ajuste de Preços """
class ProdutosAjustarPreco(wx.Frame):

	lisTap = ""
	dsProd = ""
	
	def __init__(self, parent,id):
		
		self.p = parent

		wx.Frame.__init__(self, parent, id, 'Produtos: Ajuste de preços', size=(860,405), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)

		self.AjusTePrecos = wx.ListCtrl(self.painel, -1,pos=(15,0), size=(841,227),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.AjusTePrecos.SetBackgroundColour('#3A697A')
		self.AjusTePrecos.SetForegroundColour('#33ADD5')
		self.AjusTePrecos.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.AjusTePrecos.Bind(wx.EVT_LIST_ITEM_SELECTED, self.passagem)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		self.AjusTePrecos.InsertColumn(0, 'Preço_1 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(1, 'Preço_2 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(2, 'Preço_3 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(3, 'Preço_4 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(4, 'Preço_5 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(5, 'Preço_6 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(6, 'Tipo Ajuste', width=120)
		self.AjusTePrecos.InsertColumn(7, 'Modo Ajuste', width=120)
		self.AjusTePrecos.InsertColumn(8, 'Descrição',   width=120)
		self.AjusTePrecos.InsertColumn(9, 'Data Ajuste', width=220)
        
		self.AjusTePrecos.InsertColumn(10,'Ajuste_1 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(11,'Ajuste_2 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(12,'Ajuste_3 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(13,'Ajuste_4 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(14,'Ajuste_5 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(15,'Ajuste_6 - Margem', format=wx.LIST_ALIGN_LEFT, width=130)
		self.AjusTePrecos.InsertColumn(16,'Ajuste p/Custo-Margem', width=230)
        
		wx.StaticText(self.painel,-1,"Preço_1 - Margem: ",pos=(20,255)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_2 - Margem: ",pos=(20,280)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_3 - Margem: ",pos=(20,305)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_4 - Margem: ",pos=(20,330)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_5 - Margem: ",pos=(20,355)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_6 - Margem: ",pos=(20,380)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Data e Hora da Alteração",pos=(527,240)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tipo de Ajuste",          pos=(527,280)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Modo de Ajuste",          pos=(707,280)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição { Fabricante, Grupo, Sub-Grupos }Modo de Ajuste", pos=(527,327)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		an = wx.StaticText(self.painel,-1,"{ "+self.dsProd+" }",pos=(20,232))
		an.SetForegroundColour('#4D4D4D')
		an.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.an1 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(120,250), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.an1.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.an1.SetBackgroundColour("#E5E5E5")

		self.an2 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(120,275), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.an2.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.an2.SetBackgroundColour("#E5E5E5")

		self.an3 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(120,300), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.an3.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.an3.SetBackgroundColour("#E5E5E5")

		self.an4 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(120,325), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.an4.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.an4.SetBackgroundColour("#E5E5E5")

		self.an5 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(120,350), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.an5.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.an5.SetBackgroundColour("#E5E5E5")

		self.an6 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(120,375), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.an6.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.an6.SetBackgroundColour("#E5E5E5")

		self.ap1 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(230,250), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ap1.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ap1.SetBackgroundColour("#E5E5E5")

		self.ap2 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(230,275), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ap2.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ap2.SetBackgroundColour("#E5E5E5")

		self.ap3 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(230,300), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ap3.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ap3.SetBackgroundColour("#E5E5E5")

		self.ap4 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(230,325), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ap4.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ap4.SetBackgroundColour("#E5E5E5")

		self.ap5 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(230,350), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ap5.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ap5.SetBackgroundColour("#E5E5E5")

		self.ap6 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(230,375), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ap6.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ap6.SetBackgroundColour("#E5E5E5")

		""" Ajustes """
		self.usA = wx.TextCtrl(self.painel,-1,value="",pos=(525,250), size=(332,20),style=wx.TE_READONLY)
		self.usA.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.usA.SetBackgroundColour("#BFBFBF")
		self.usA.SetForegroundColour("#174E82")

		self.Tpa = wx.TextCtrl(self.painel,-1,value="",pos=(525,290), size=(165,20),style=wx.TE_READONLY)
		self.Tpa.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tpa.SetBackgroundColour("#BFBFBF")
		self.Tpa.SetForegroundColour("#174E82")

		self.Mda = wx.TextCtrl(self.painel,-1,value="",pos=(705,290), size=(152,20),style=wx.TE_READONLY)
		self.Mda.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Mda.SetBackgroundColour("#BFBFBF")
		self.Mda.SetForegroundColour("#174E82")

		self.Dsa = wx.TextCtrl(self.painel,-1,value="",pos=(525,340), size=(330,55),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.Dsa.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Dsa.SetBackgroundColour("#BFBFBF")
		self.Dsa.SetForegroundColour("#174E82")

		self.aT1 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(320,250), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.aT1.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.aT1.SetBackgroundColour("#E5E5E5")
		self.aT1.SetForegroundColour("#174E82")

		self.aT2 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(320,275), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.aT2.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.aT2.SetBackgroundColour("#E5E5E5")
		self.aT2.SetForegroundColour("#174E82")

		self.aT3 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(320,300), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.aT3.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.aT3.SetBackgroundColour("#E5E5E5")
		self.aT3.SetForegroundColour("#174E82")

		self.aT4 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(320,325), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.aT4.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.aT4.SetBackgroundColour("#E5E5E5")
		self.aT4.SetForegroundColour("#174E82")

		self.aT5 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(320,350), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.aT5.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.aT5.SetBackgroundColour("#E5E5E5")
		self.aT5.SetForegroundColour("#174E82")

		self.aT6 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(320,375), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.aT6.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.aT6.SetBackgroundColour("#E5E5E5")
		self.aT6.SetForegroundColour("#174E82")

		self.Tp1 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(430,250), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.Tp1.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tp1.SetBackgroundColour("#E5E5E5")
		self.Tp1.SetForegroundColour("#174E82")
		
		self.Tp2 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(430,275), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.Tp2.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tp2.SetBackgroundColour("#E5E5E5")
		self.Tp2.SetForegroundColour("#174E82")

		self.Tp3 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(430,300), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.Tp3.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tp3.SetBackgroundColour("#E5E5E5")
		self.Tp3.SetForegroundColour("#174E82")

		self.Tp4 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(430,325), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.Tp4.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tp4.SetBackgroundColour("#E5E5E5")
		self.Tp4.SetForegroundColour("#174E82")

		self.Tp5 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(430,350), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.Tp5.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tp5.SetBackgroundColour("#E5E5E5")
		self.Tp5.SetForegroundColour("#174E82")

		self.Tp6 = wx.TextCtrl(self.painel,-1,value="0.00",pos=(430,375), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.Tp6.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tp6.SetBackgroundColour("#E5E5E5")
		self.Tp6.SetForegroundColour("#174E82")
		
		self.AlteracaoLista()

	def AlteracaoLista(self):

		indice = 0
		for x in self.lisTap.split("\n"):
			
			if x !="":
					
				cm = ""
				x1 = x.split("[p]")
				p1 = x1[0].split("|")
				p2 = x1[1].split("|")
				if len( x1 ) == 3:	cm = x1[2]

				Tipo = "Individual"
				FabG = ""
				
				if p2[0] == "GL":	Tipo = "Ajuste geral"
				if p2[0] == "GU":	Tipo = "Ajuste grupo"
				if p2[0] == "AD":	Tipo = "Ajuste p/acréscimo-desconto"
				if p2[0] == "AM":	Tipo = "Ajuste manual"
				if p2[0] == "CM":	Tipo = "Ajuste na compra"
				
				if p2[1] == "FA":	FabG = "Fabricante"
				if p2[1] == "GR":	FabG = "Grupo"
				if p2[1] == "G1":	FabG = "Sub-Grupo 1"
				if p2[1] == "G2":	FabG = "Sub-Grupo 2"

				self.AjusTePrecos.InsertStringItem( indice, str( p1[0].split(";")[0] )+" - "+str( p1[0].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 1, str( p1[1].split(";")[0] )+" - "+str( p1[1].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 2, str( p1[2].split(";")[0] )+" - "+str( p1[2].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 3, str( p1[3].split(";")[0] )+" - "+str( p1[3].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 4, str( p1[4].split(";")[0] )+" - "+str( p1[4].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 5, str( p1[5].split(";")[0] )+" - "+str( p1[5].split(";")[1] ) )
				
				self.AjusTePrecos.SetStringItem( indice, 6, Tipo )
				self.AjusTePrecos.SetStringItem( indice, 7, FabG )
				self.AjusTePrecos.SetStringItem( indice, 8, str( p2[2] ) )
				self.AjusTePrecos.SetStringItem( indice, 9, str( p2[3] ) )

				self.AjusTePrecos.SetStringItem( indice, 10, str( p2[4].split(";")[0] )+" - "+str( p2[4].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 11, str( p2[5].split(";")[0] )+" - "+str( p2[5].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 12, str( p2[6].split(";")[0] )+" - "+str( p2[6].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 13, str( p2[7].split(";")[0] )+" - "+str( p2[7].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 14, str( p2[8].split(";")[0] )+" - "+str( p2[8].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 15, str( p2[9].split(";")[0] )+" - "+str( p2[9].split(";")[1] ) )
				self.AjusTePrecos.SetStringItem( indice, 16, cm )
				
				if indice % 2:	self.AjusTePrecos.SetItemBackgroundColour(indice, "#177594")
				
				indice +=1

	def passagem(self,event):

		indice = self.AjusTePrecos.GetFocusedItem()

		if self.AjusTePrecos.GetItem(indice, 16).GetText().strip() !="":	mc = "Margem de Ajuste: [ "+str( self.AjusTePrecos.GetItem(indice, 16).GetText().split("|")[0] )+" %]  "+str( self.AjusTePrecos.GetItem(indice, 16).GetText().split("|")[1] )
		else:	mc = ""
		
		self.usA.SetValue( self.AjusTePrecos.GetItem(indice, 9).GetText() )
		
		self.an1.SetValue( self.AjusTePrecos.GetItem(indice, 0).GetText().split(' - ')[0] )
		self.an2.SetValue( self.AjusTePrecos.GetItem(indice, 1).GetText().split(' - ')[0] )
		self.an3.SetValue( self.AjusTePrecos.GetItem(indice, 2).GetText().split(' - ')[0] )
		self.an4.SetValue( self.AjusTePrecos.GetItem(indice, 3).GetText().split(' - ')[0] )
		self.an5.SetValue( self.AjusTePrecos.GetItem(indice, 4).GetText().split(' - ')[0] )
		self.an6.SetValue( self.AjusTePrecos.GetItem(indice, 5).GetText().split(' - ')[0] )

		self.ap1.SetValue( self.AjusTePrecos.GetItem(indice, 0).GetText().split(' - ')[1]+" %" )
		self.ap2.SetValue( self.AjusTePrecos.GetItem(indice, 1).GetText().split(' - ')[1]+" %" )
		self.ap3.SetValue( self.AjusTePrecos.GetItem(indice, 2).GetText().split(' - ')[1]+" %" )
		self.ap4.SetValue( self.AjusTePrecos.GetItem(indice, 3).GetText().split(' - ')[1]+" %" )
		self.ap5.SetValue( self.AjusTePrecos.GetItem(indice, 4).GetText().split(' - ')[1]+" %" )
		self.ap6.SetValue( self.AjusTePrecos.GetItem(indice, 5).GetText().split(' - ')[1]+" %" )

		""" Ajuste """
		self.aT1.SetValue( self.AjusTePrecos.GetItem(indice, 10).GetText().split(' - ')[0] )
		self.aT2.SetValue( self.AjusTePrecos.GetItem(indice, 11).GetText().split(' - ')[0] )
		self.aT3.SetValue( self.AjusTePrecos.GetItem(indice, 12).GetText().split(' - ')[0] )
		self.aT4.SetValue( self.AjusTePrecos.GetItem(indice, 13).GetText().split(' - ')[0] )
		self.aT5.SetValue( self.AjusTePrecos.GetItem(indice, 14).GetText().split(' - ')[0] )
		self.aT6.SetValue( self.AjusTePrecos.GetItem(indice, 15).GetText().split(' - ')[0] )

		self.Tp1.SetValue( self.AjusTePrecos.GetItem(indice, 10).GetText().split(' - ')[1]+" %" )
		self.Tp2.SetValue( self.AjusTePrecos.GetItem(indice, 11).GetText().split(' - ')[1]+" %" )
		self.Tp3.SetValue( self.AjusTePrecos.GetItem(indice, 12).GetText().split(' - ')[1]+" %" )
		self.Tp4.SetValue( self.AjusTePrecos.GetItem(indice, 13).GetText().split(' - ')[1]+" %" )
		self.Tp5.SetValue( self.AjusTePrecos.GetItem(indice, 14).GetText().split(' - ')[1]+" %" )
		self.Tp6.SetValue( self.AjusTePrecos.GetItem(indice, 15).GetText().split(' - ')[1]+" %" )

		self.Tpa.SetValue( self.AjusTePrecos.GetItem(indice, 6).GetText() )
		self.Mda.SetValue( self.AjusTePrecos.GetItem(indice, 7).GetText() )
		self.Dsa.SetValue( self.AjusTePrecos.GetItem(indice, 8).GetText()+"\n"+mc )

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#214E7B") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Ajuste de Preços e Margens { Valor Anterir, Ajustes }", 0, 397, 90)


class manuTencaoSisTema:
	
	def vamosManter(self,par):
		
		self.p = par
		self.conn = sqldb()
		self.sql  = self.conn.dbc("Manutencão do Sistema",1, login.identifi, janela = par)

		if self.sql[0] == True:

			os.system("clear")
			saida = input("1-Ajuste de Pedidos { Gravar Pedidos Dentro do ITEM, se Pedido,Orcamento, se Cancelado e Data do Cancelamento }\n2-Ajuste de Devolução { Gravar Pedidos Dentro do ITEM, se Pedido,Orcamento, se Cancelado e Data do Cancelamento }\n\nOpção: ")
	
			if saida == 1 or saida == 2:

				_pedido = "SELECT * FROM cdavs WHERE cr_tipo='1'"
				if saida == 2:	_pedido = _pedido.replace("cdavs","dcdavs")

				pedidos = self.sql[2].execute(_pedido)
				rpedido = self.sql[2].fetchall()

				if pedidos !=0:
					
					for i in rpedido:
						
						nDav = i[2]
						dCan = i[19]
						hCan = i[20]
						
						achar = "SELECT * FROM idavs WHERE it_ndav='"+str( nDav )+"'"
						if saida == 2:	achar = achar.replace("idavs","didavs")
						achei = self.sql[2].execute(achar)
						
						if achei !=0:

							up1 = "UPDATE idavs SET it_dcan='"+str( dCan )+"',it_hcan='"+str( hCan )+"',it_canc='1',it_tped='1' WHERE it_ndav='"+str( nDav )+"'"
							up2 = "UPDATE idavs SET it_tped='1' WHERE it_ndav='"+str( nDav )+"'"
							if saida == 2:	up1 = up1.replace("idavs","didavs")
							if saida == 2:	up2 = up2.replace("idavs","didavs")

							if dCan != None:

								self.sql[2].execute(up1)

							if dCan == None:

								self.sql[2].execute(up2)

					self.sql[1].commit()

		self.conn.cls(self.sql[1])
	
		os.system("exit")

class UnidadeManejo(wx.Frame):

	def __init__(self, parent,id):
		
		self.p = parent
		mkn    = wx.lib.masked.NumCtrl

		self.van = ""
		
		wx.Frame.__init__(self, parent, id, 'Fornecedor: Unidade de manejo florestal', size=(452,202), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)

		self.unidade_manejo= wx.ListCtrl(self.painel, -1,pos=(15,1), size=(398,155),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.unidade_manejo.SetBackgroundColour("#D2DBD2")
		self.unidade_manejo.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		
		self.unidade_manejo.InsertColumn(0, 'Unidade de manejo florestal', width=250)
		self.unidade_manejo.InsertColumn(1, 'Valor p/M3', format=wx.LIST_ALIGN_LEFT, width=130)
		self.unidade_manejo.InsertColumn(2, 'Observe', width=30)
	
		inclui = wx.BitmapButton(self.painel, 300, wx.Bitmap("imagens/incluip.png",  wx.BITMAP_TYPE_ANY), pos=(415, 1), size=(36,36))				
		altera = wx.BitmapButton(self.painel, 301, wx.Bitmap("imagens/alterarm.png", wx.BITMAP_TYPE_ANY), pos=(415, 41), size=(36,36))
		apagar = wx.BitmapButton(self.painel, 302, wx.Bitmap("imagens/apagar.png",   wx.BITMAP_TYPE_ANY), pos=(415, 81), size=(36,36))
		salvar = wx.BitmapButton(self.painel, 303, wx.Bitmap("imagens/savep.png",    wx.BITMAP_TYPE_ANY), pos=(415,121), size=(36,36))

		inform = wx.BitmapButton(self.painel, 304, wx.Bitmap("imagens/dadosfor.png",    wx.BITMAP_TYPE_ANY), pos=(415,162), size=(36,36))

		wx.StaticText(self.painel,-1,"Unidade de manejo {Endereço}", pos=(17,158)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor p/M3}", pos=(323,158)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.anterior = wx.StaticText(self.painel,-1,"", pos=(170,158))
		self.anterior.SetFont(wx.Font(5, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.unidade = wx.TextCtrl(self.painel,-1, "",pos=(13,172),size=(300,22))
		self.unidade.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.unidade.SetBackgroundColour('#E5E5E5')

		self.valormt = mkn(self.painel, -1, value = '0.00', pos=(320,172), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 5, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.valormt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.unidade.SetMaxLength(30)
		self.valormt.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		inclui.Bind(wx.EVT_BUTTON, self.incluirUnidade)
		altera.Bind(wx.EVT_BUTTON, self.alterarUnidade)
		apagar.Bind(wx.EVT_BUTTON, self.apagarUnidade)
		salvar.Bind(wx.EVT_BUTTON, self.alteracaoUnidade)

		inform.Bind(wx.EVT_BUTTON, self.unidadeAlteracoes )
		
		self.listarUnidades(wx.EVT_BUTTON)
		
	def passagem(self,event):

		self.unidade.SetValue('')
		self.valormt.SetValue('0.00')

	def unidadeAlteracoes( self, event ):
		
		efe_frame=UnidadeManejoAlteracoes(parent=self,id=-1)
		efe_frame.Centre()
		efe_frame.Show()

	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=-1)
		tel_frame.Centre()
		tel_frame.Show()

	def alterarUnidade(self,event):

		self.van = ""

		if self.unidade_manejo.GetItemCount():

			indice = self.unidade_manejo.GetFocusedItem()
			self.unidade.SetValue( self.unidade_manejo.GetItem( indice, 0 ).GetText() )
			self.valormt.SetValue( self.unidade_manejo.GetItem( indice, 1 ).GetText().replace(',','') )
			self.anterior.SetLabel( self.unidade_manejo.GetItem( indice, 0 ).GetText() )
			self.unidade.SetFocus()
			self.van = self.unidade_manejo.GetItem( indice, 0 ).GetText()+";"+self.unidade_manejo.GetItem( indice, 1 ).GetText()

		else:	alertas.dia(self,"Lista de unidades estar vazio...\n"+(" "*100),"Fornecedor: Unidade de manejo")

	def apagarUnidade(self,event):

		if self.unidade_manejo.GetItemCount():

			indice = self.unidade_manejo.GetFocusedItem()
			unidad = self.unidade_manejo.GetItem(indice, 0).GetText().strip()
			
			receb = wx.MessageDialog(self,"Confirme para apagar a unidade de manejo selecionada...\n"+(" "*110),"Fornecedor: Unidade de manejo",wx.YES_NO|wx.NO_DEFAULT)
			if receb.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Unidade de manejo", fil = login.identifi, janela = self )
				grva = True

				if sql[0]:

					try:
						
						sql[2].execute("DELETE FROM grupofab WHERE fg_cdpd='A' and fg_prin='"+ unidad +"'")
						sql[1].commit()

						atual = ""
						self.van = self.unidade_manejo.GetItem(indice, 0).GetText().strip()+";"+self.unidade_manejo.GetItem(indice, 1).GetText().strip()
						saida_gravacao = self.uidadesManejoGravar( "D", self.van, atual )
						self.van = ""

					except Exception as error:
						
						sql[1].rollback()
						grva = False
						
						if type( error ) !=unicode:	error = str( error )

					conn.cls( sql[1] )

					if not grva:	alertas.dia(self,u"Erro na eliminação da unidade...\n"+ error +"\n"+(" "*100),"Fornecedor: Unidade de manejo")
					if grva:

						self.listarUnidades(wx.EVT_BUTTON)
						try:
							
							self.unidade.SetValue('')
							self.valormt.SetValue('0.00')
							self.anterior.SetLabel('')

						except Exception as erro:

							self.unidade.SetValue('')
							self.anterior.SetLabel('')

	def listarUnidades(self,event):

		conn = sqldb()
		sql  = conn.dbc("Unidade de manejo", fil = login.identifi, janela = self )

		if sql[0]:

			achar = sql[2].execute("SELECT fg_desc,fg_prin FROM grupofab WHERE fg_cdpd='A' ORDER BY fg_prin")
			if achar:

				result = sql[2].fetchall()
				conn.cls( sql[1] )
				
				indice = 0
				self.unidade_manejo.DeleteAllItems()
				
				for i in result:

					self.unidade_manejo.InsertStringItem( indice, i[1] )
					self.unidade_manejo.SetStringItem(indice,1, format( Decimal( i[0] ), ',' ) )
	
					if indice % 2:	self.unidade_manejo.SetItemBackgroundColour(indice, "#CBD3CB")
					indice +=1

	def alteracaoUnidade(self,event):

		if not self.unidade.GetValue().strip() or not self.valormt.GetValue():

			alertas.dia(self,u"Descrição da unidade e/ou valor p/M3 vazio...\n"+(" "*100),"Fornecedor: Unidade de manejo")
			return

		if not self.anterior.GetLabel().strip():

			alertas.dia(self,u"Unidade anterior p/alteração estar vazio...\n"+(" "*100),"Fornecedor: Unidade de manejo")
			return
			
		conn = sqldb()
		sql  = conn.dbc("Unidade de manejo", fil = login.identifi, janela = self )
		grva = True

		saida_gravacao = ""
		
		if sql[0]:

			if self.unidade.GetValue().strip() != self.anterior.GetLabel().strip() and sql[2].execute("SELECT fg_cdpd FROM grupofab WHERE fg_cdpd='A' and fg_prin='"+ self.unidade.GetValue() +"'"):

				conn.cls( sql[1] )
				alertas.dia(self,"Unidade de manejo ja cadastrada...\n"+(" "*100),"Fornecedor: Unidade de manejo")

			else:

				try:
					
					sql[2].execute("UPDATE grupofab SET fg_desc='"+str( Trunca.trunca( 3, Decimal( self.valormt.GetValue() ) ) )+"', fg_prin='"+ self.unidade.GetValue() +"' WHERE fg_cdpd='A' and fg_prin='"+ self.anterior.GetLabel().strip() +"'")
					sql[1].commit()

					atual = self.unidade.GetValue()+";"+str( Trunca.trunca( 3, Decimal( self.valormt.GetValue() ) ) )
					saida_gravacao = self.uidadesManejoGravar( "A", self.van, atual )
					
				except Exception as error:
					sql[1].rollback()
					grva = False

				conn.cls( sql[1] )

				if grva:

					self.listarUnidades(wx.EVT_BUTTON)
					try:
						
						self.unidade.SetValue('')
						self.valormt.SetValue('0.00')
						self.anterior.SetLabel('')

					except Exception as erro:

						self.unidade.SetValue('')
						self.anterior.SetLabel('')

		if saida_gravacao:	alertas.dia( self, saida_gravacao+(" "*120),u"Alteração")

	def incluirUnidade(self,event):

		if not self.unidade.GetValue().strip() or not self.valormt.GetValue():

			alertas.dia(self,"Descrição da unidade e/ou valor p/M3 vazio...\n"+(" "*100),"Fornecedor: Unidade de manejo")
			return

		receb = wx.MessageDialog(self,"Confirme para incluir a unidade de manejo...\n"+(" "*110),"Fornecedor: Unidade de manejo",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() ==  wx.ID_YES:

			del receb
			conn = sqldb()
			sql  = conn.dbc("Unidade de manejo", fil = login.identifi, janela = self )
			grva = True
			if sql[0]:

				achar = sql[2].execute("SELECT fg_cdpd FROM grupofab WHERE fg_cdpd='A' and fg_prin='"+ self.unidade.GetValue() +"'")
				if achar:	grva = False  
				if not achar:

					try:
						
						grv = "INSERT INTO grupofab (fg_cdpd,fg_desc,fg_prin) VALUE(%s,%s,%s)"
						sql[2].execute( grv, ( 'A', Trunca.trunca( 3, Decimal( self.valormt.GetValue() ) ), self.unidade.GetValue().upper() ) )
						sql[1].commit()

						atual = self.unidade.GetValue().upper()+";"+str( Trunca.trunca( 3, Decimal( self.valormt.GetValue() ) ) )
						saida_gravacao = self.uidadesManejoGravar( "I", self.van, atual )

					except Exception as error:
						sql[1].rollback()
						grva = False
						
				conn.cls( sql[1] )

				if achar:	alertas.dia(self,"Unidade ja cadastrada...\n"+(" "*100),"Fornecedor: Unidade de manejo")

			if grva:

				self.listarUnidades(wx.EVT_BUTTON)
				try:
					
					self.unidade.SetValue('')
					self.valormt.SetValue('0.00')
					self.anterior.SetLabel('')

				except Exception as erro:

					self.unidade.SetValue('')
					self.anterior.SetLabel('')
					
	def Tvalores(self,valor,idfy):

		if valor == '':	valor = self.valormt.GetValue()

		if Decimal(valor) > Decimal('99999.99') or Decimal(valor) == 0:

			valor = self.valormt.GetValue()
			alertas.dia(self.painel,u"Valor enviado é incompatível!!","Fornecedor")
			
		self.valormt.SetValue(valor)
		
	def uidadesManejoGravar( self, tipo, _anterior, _atual ):

		error = ""
		__arquivo = ""
		
		try:

			entrada = {"A": "Alterando dados", "D": "Apagando dados", "I": "Incluindo dados"}

			_nomeArq = "/home/"+diretorios.usPrinci+"/direto/manejo/unidadesmanejo.csv"
			if os.path.exists( _nomeArq ):

				abrir, __arquivo = True, open( _nomeArq,"r" ).read()
				if __arquivo and type( __arquivo ) == str:	__arquivo = __arquivo.decode("UTF-8")	

			else:	abrir = False

			lista_dados = ""
			quantidade  = 0
			if abrir and __arquivo:

				for i in __arquivo.split('\n'):

					if i and quantidade < 50:	lista_dados +=i+'\n'
					quantidade +=1

			dados_gravar = entrada[tipo]+"|"+ login.usalogin +" "+ datetime.datetime.now().strftime("%d/%m/%Y %T") +"|"+_anterior+"|"+_atual+"\n"+lista_dados
			gravar_dados = open( _nomeArq ,"w" ).write( dados_gravar.encode("UTF-8") )
			self.van = ""
		
		except Exception as _erro:
			
			if type( _erro ) !=unicode:	_erro = str( _erro )
			error = "{ Gravando dados do usuario }\n\nErro: "+ _erro +"\n"

		return error

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#2D6F2D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Unidade de Manejo-Extração", 0, 192, 90)


class UnidadeManejoAlteracoes(wx.Frame):

	def __init__(self, parent,id):
		
		self.p = parent
	
		wx.Frame.__init__(self, parent, id, 'Fornecedor: Unidade de manejo florestal', size=(850,160), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)

		self.unidade_manejo= wx.ListCtrl(self.painel, -1,pos=(15,0), size=(833,157),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.unidade_manejo.SetBackgroundColour("#5989B3")
		self.unidade_manejo.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.unidade_manejo.InsertColumn(0, 'Tipo de lançamento', width=130)
		self.unidade_manejo.InsertColumn(1, 'Usuario', width=200)
		self.unidade_manejo.InsertColumn(2, 'Antes { Unidade }', width=135)
		self.unidade_manejo.InsertColumn(3, 'Antes { Valor }', format=wx.LIST_ALIGN_LEFT,width=110)
		self.unidade_manejo.InsertColumn(4, 'Depois { Unidade }', width=135)
		self.unidade_manejo.InsertColumn(5, 'Depois { Valor }', format=wx.LIST_ALIGN_LEFT,width=110)

		indice = 0
		for lu in glob.glob("/home/*"):

			if os.path.exists( lu + "/direto/manejo" ) and os.path.exists( lu + "/direto/manejo/unidadesmanejo.csv" ):

				__arquivo = open( lu + "/direto/manejo/unidadesmanejo.csv", "r" ).read()
				
				for i in __arquivo.split('\n'):

					if i:

						saida = i.split('|')

						self.unidade_manejo.InsertStringItem( indice, saida[0] )
						self.unidade_manejo.SetStringItem(indice,1, saida[1])
						if 	saida[2]:
							
							self.unidade_manejo.SetStringItem(indice,2, saida[2].split(";")[0] )
							self.unidade_manejo.SetStringItem(indice,3, saida[2].split(";")[1] )

						if 	saida[3]:
							
							self.unidade_manejo.SetStringItem(indice,4, saida[3].split(";")[0] )
							self.unidade_manejo.SetStringItem(indice,5, saida[3].split(";")[1] )

						if indice % 2:	self.unidade_manejo.SetItemBackgroundColour(indice, "#6D93B5")

						indice +=1

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#2D6F2D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Status das unidades", 0, 155, 90)
