#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import datetime
import unicodedata
import calendar
import glob
import time

import commands
import os

from decimal   import *
from conectar  import sqldb,AbrirArquivos,dialogos,cores,login,numeracao,sbarra,formasPagamentos,CodigoMunicipio,TelNumeric,truncagem,diretorios,menssagem,MostrarHistorico,TTributos
from plcontas  import PlanoContas
from relatorio import relcompra

from cdavs import impressao

alertas = dialogos()
sb      = sbarra()
nF      = numeracao()
Trunca  = truncagem()
mens    = menssagem()

class ProdutosFiliais(wx.Frame):

	def __init__(self, parent,id):
		
		self.p = parent
		self.i = id
		
		self.pFFilial = self.p.ppFilial

		PFVListCtrl.TipoFilialRL = self.pFFilial
		_ffl = self.pFFilial
		
		wx.Frame.__init__(self, parent, id, 'Vincular produtos p/filial', size=(900,437), style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.vincularEstoque = PFVListCtrl(self.painel, 300 ,pos=(13,0), size=(883,315),
							   style=wx.LC_REPORT
							   |wx.LC_VIRTUAL
							   |wx.BORDER_SUNKEN
							   |wx.LC_HRULES
							   |wx.LC_VRULES
							   |wx.LC_SINGLE_SEL
							  )

		self.vincularEstoque.SetBackgroundColour("#DEE5DE")
		
		self.vincularEstoque.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.onPaint)

		wx.StaticText(self.painel,-1, u"Descrição,P:Expressão, C:Código,B:Barras, R:Referência, D:RefFabrica\nI:Código Interno, [ * ]-Encadeado",  pos=(15,330)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Filtrar Fabricante,Grupos",  pos=(213,388)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		_fl = wx.StaticText(self.painel,-1,"Filiais Locais { Vincular Estoque Físico }",  pos=(505,343))
		_fl.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_fl.SetForegroundColour('#C7E2FD')

		_fr = wx.StaticText(self.painel,-1,"Filiais Remotas { Incluir-Atualizar Produtos }", pos=(505,388))
		_fr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_fr.SetForegroundColour('#B78B93')

		self.TF = wx.StaticText(self.painel,-1,"{ Fabricante }", pos=(350,385))
		self.TF.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TF.SetForegroundColour("#2169B0")

		self.oco = wx.StaticText(self.painel,-1,"{ 0 }", pos=(300,343))
		self.oco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.oco.SetForegroundColour("#2169B0")

		self.consultar = wx.TextCtrl(self.painel, -1, "", pos=(12,357),size=(397, 25),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.consultar.SetBackgroundColour('#E5E5E5')
		self.consultar.SetForegroundColour('#4D4D4D')
		self.consultar.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.consultar.SetValue("x:a")

		"""   Marcar p/Transferir fisico do cadastro de produtos  """
		self.Tfisico = wx.CheckBox(self.painel, -1,  "Transferir estoque fisico", pos=(500,318))
		self.Tfisico.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.Tfisico.Enable( False )

		self.afisico = wx.CheckBox(self.painel, -1,  "Atualizar estoque p/produtos localizados", pos=(660,318))
		self.afisico.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.afisico.Enable( False )

		if login.usalogin.upper() == "LYKOS":
			self.Tfisico.Enable( True )
			self.afisico.Enable( True )

		self.ajfabri = wx.RadioButton(self.painel, 600 , "Fabricante",  pos=(12, 384) ,style=wx.RB_GROUP)
		self.ajgrupo = wx.RadioButton(self.painel, 601 , "Grupo",       pos=(12, 407))
		self.ajsubg1 = wx.RadioButton(self.painel, 602 , "Sub-Grupo 1", pos=(112,384))
		self.ajsubg2 = wx.RadioButton(self.painel, 603 , "Sub-Grupo 2", pos=(112,407))

		self.ajfabri.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajgrupo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajsubg1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajsubg2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.fgrupos = wx.ComboBox(self.painel, 604, '', pos=(210,400), size=(277,27), choices = '', style = wx.CB_READONLY)
		self.flLocal = wx.ComboBox(self.painel, 605, '', pos=(500,355), size=(300,27), choices = login.ciaLocal, style=wx.NO_BORDER|wx.CB_READONLY)
		self.flRemot = wx.ComboBox(self.painel, 606, '', pos=(500,400), size=(300,27), choices = login.ciaRemot, style=wx.NO_BORDER|wx.CB_READONLY)
		
		self.procura = wx.BitmapButton(self.painel, 400, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(413,352), size=(35,30))	
		self.voltars = wx.BitmapButton(self.painel, 410, wx.Bitmap("imagens/volta16.png",   wx.BITMAP_TYPE_ANY), pos=(451,352), size=(35,30))	
		self.anexaun = wx.BitmapButton(self.painel, 420, wx.Bitmap("imagens/importp.png",   wx.BITMAP_TYPE_ANY), pos=(815,348), size=(35,32))	
		self.anexall = wx.BitmapButton(self.painel, 430, wx.Bitmap("imagens/agrupar16.png", wx.BITMAP_TYPE_ANY), pos=(855,348), size=(35,32))	
		self.adicion = wx.BitmapButton(self.painel, 450, wx.Bitmap("imagens/nfecons16.png", wx.BITMAP_TYPE_ANY), pos=(815,391), size=(35,32))	
		self.adicall = wx.BitmapButton(self.painel, 451, wx.Bitmap("imagens/ngr.png",       wx.BITMAP_TYPE_ANY), pos=(855,391), size=(35,32))	
			
		self.anexaun.SetBackgroundColour('#C7E2FD')
		self.anexall.SetBackgroundColour('#C7E2FD')

		self.adicion.SetBackgroundColour('#B78B93')
		self.adicall.SetBackgroundColour('#B78B93')

		self.procura.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.voltars.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.anexaun.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.anexall.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.adicion.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.adicall.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.procura.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.voltars.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.anexaun.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.anexall.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.adicion.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.adicall.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.anexaun.Bind(wx.EVT_BUTTON, self.anexar)
		self.anexall.Bind(wx.EVT_BUTTON, self.anexar)

		self.ajfabri.Bind( wx.EVT_RADIOBUTTON, self.FabGrupos )
		self.ajgrupo.Bind( wx.EVT_RADIOBUTTON, self.FabGrupos )
		self.ajsubg1.Bind( wx.EVT_RADIOBUTTON, self.FabGrupos )
		self.ajsubg2.Bind( wx.EVT_RADIOBUTTON, self.FabGrupos )
		self.fgrupos.Bind( wx.EVT_COMBOBOX, self.selecionaFGrupos )
		self.procura.Bind( wx.EVT_BUTTON, self.selecionar )
		self.voltars.Bind( wx.EVT_BUTTON, self.sair )
		self.adicion.Bind( wx.EVT_BUTTON, self.adicionAltera )
		self.adicall.Bind( wx.EVT_BUTTON, self.adicionAltera )
		
		self.flLocal.Bind( wx.EVT_COMBOBOX, self.comEvT )
		self.flRemot.Bind( wx.EVT_COMBOBOX, self.comEvT )

		self.consultar.Bind( wx.EVT_TEXT_ENTER, self.selecionar )
		self.consultar.SetFocus()

		self.selecionar( wx.EVT_BUTTON )
		self.FabGrupos( wx.EVT_BUTTON )

		if nF.rF( cdFilial = _ffl ) == "T":

			self.adicion.Enable( False )
			self.adicall.Enable( False )
			self.flRemot.Enable( False )

		if nF.fu( _ffl ) == "T":

			self.anexaun.Enable( False )
			self.anexall.Enable( False )
			self.flLocal.Enable( False )
			
	def sair(self,event):	self.Destroy()
	def selecionaFGrupos(self,event):	self.selecionar(wx.EVT_BUTTON)
	def comEvT(self,event):
		
		if event.GetId() == 605 and self.flLocal.GetValue() !='':	self.flRemot.SetValue('')
		if event.GetId() == 606 and self.flRemot.GetValue() !='':	self.flLocal.SetValue('')

	def FabGrupos(self,event):
	
		self.fgrupos.SetValue('')
		if self.ajgrupo.GetValue() == True:

			self.fgrupos.SetItems(self.p.grupos)
			self.TF.SetLabel("{ Grupo }")

		if self.ajsubg1.GetValue() == True:

			self.fgrupos.SetItems(self.p.subgr1)
			self.TF.SetLabel("{ Sub-Grupo 1 }")

		if self.ajsubg2.GetValue() == True:

			self.fgrupos.SetItems(self.p.subgr2)
			self.TF.SetLabel("{ Sub-Grupo 2 }")

		if self.ajfabri.GetValue() == True:

			self.fgrupos.SetItems(self.p.fabric)
			self.TF.SetLabel("{ Fabricante }")

	def OnEnterWindow(self, event):

		if   event.GetId() == 400:	sb.mstatus("  Procurar-Pesquisar produtos",0)
		elif event.GetId() == 410:	sb.mstatus("  Sair - Voltar",0)
		elif event.GetId() == 420:	sb.mstatus("  Vincular produto selecionado ao cadastro do estoque fisico",0)
		elif event.GetId() == 430:	sb.mstatus("  Vincular produtos, grupos,fabricantes e/ou todos os produtos ao cadastro do estoque fisico",0)
		elif event.GetId() == 450:	sb.mstatus("  Incluir e/ou Atualizar produto selecionado no cadastro de produtos de uma filial remota",0)
		elif event.GetId() == 451:	sb.mstatus("  Incluir e/ou Atualizar produtos, grupos,fabricantes no cadastro de produtos de uma filial remota",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Vinculos de Produtos e Ajutes Remotos",0)
		event.Skip()

	def anexar(self,event):
		
		ind = self.vincularEstoque.GetFocusedItem()
		nrg = self.vincularEstoque.GetItemCount()
		idp = self.vincularEstoque.GetItem(ind, 0 ).GetText()
		cod = self.vincularEstoque.GetItem(ind, 1 ).GetText()
		des = self.vincularEstoque.GetItem(ind, 2 ).GetText()
		fis = str( self.vincularEstoque.GetItem(ind, 6 ).GetText() )
				
		if event.GetId() == 420:
			
			if self.vincularEstoque.GetItemCount() == 0 or self.flLocal.GetValue() == '' or cod == '' or idp == '':
		 
				if   self.vincularEstoque.GetItemCount() == 0:	alertas.dia(self.painel,"Lista de Produtos Vazia...\n"+(" "*100),"Vincular Produtos")
				elif self.flLocal.GetValue() == '':	alertas.dia(self.painel,"Selecione uma Filial...\n"+(" "*100),"Vincular Produtos")
				elif cod == '':	alertas.dia(self.painel,"Código do Produto Vazio...\n"+(" "*100),"Vincular Produtos")
				elif idp == '':	alertas.dia(self.painel,"ID do Produto Vazio...\n"+(" "*100),"Vincular Produtos")
				return

		elif event.GetId() == 430:

			if self.vincularEstoque.GetItemCount() == 0 or self.flLocal.GetValue() == '':
		 
				if   self.vincularEstoque.GetItemCount() == 0:	alertas.dia(self.painel,"Lista de Produtos Vazia...\n"+(" "*100),"Vincular Produtos em Grupo")
				elif self.flLocal.GetValue() == '':	alertas.dia(self.painel,"Selecione uma Filial...\n"+(" "*100),"Vincular Produtos em Grupos")
				return
				
		_filial = self.flLocal.GetValue().split('-')[0]
		_nomefl = self.flLocal.GetValue().split('-')[1]
		vincuni = False
		
		_ffl = self.pFFilial

#-------: Vincular por Produtos
		if event.GetId() == 420:

			vinculacao = wx.MessageDialog(self.painel,"Filial: "+str( _filial )+"\nID Produto: "+str( idp )+u"\nCódigo do Produto: "+str( cod )+u"\nDescrição do Produto: "+ des +"\n\nConfirme p/vincular produto a filial...\n"+(" "*140),"Vincular Produtos",wx.YES_NO|wx.NO_DEFAULT)
			if vinculacao.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Produtos: Vincular Produtos e Filias", fil = _ffl, janela = self.painel )
				grv  = True
				ngr  = False

				if sql[0] == True:

					ach = sql[2].execute("SELECT ef_idfili FROM estoque WHERE ef_idfili='"+str( _filial )+"' and ef_codigo='"+str( cod )+"'") 
						
					if ach:

						if self.Tfisico.GetValue() and self.afisico.GetValue():

							sql[2].execute("UPDATE estoque SET ef_fisico='"+str( fis )+"' WHERE ef_idfili='"+str( _filial )+"' and ef_codigo='"+str( cod )+"'")
							sql[1].commit()
						
					else:

						try:
							
							inserir = "INSERT INTO estoque ( ef_idfili, ef_codigo ) VALUES ( %s,%s)"

							sql[2].execute( inserir, ( _filial, cod ) )
							sql[1].commit()
							ngr = True
							
						except Exception as _reTornos:
							grv = False
							sql[1].rollback()

					conn.cls(sql[1])
					
					if vincuni:	alertas.dia(self.painel,"Produto ja vinculado...\n\nFilial: "+str( _filial )+"\nCodigo: "+str( cod )+"\nID Produto: "+str( idp )+"\n"+(" "*100),"Vincular Produtos")
					if grv == False:	alertas.dia(self.painel,u"Erro na Gravação...\n\nRetorno: "+ _reTornos +"\n"+(" "*140),"Vincular produtos")            
					if ngr == True:

						""" Atualiza Lista """
						_registros = 0
						relacao = {}

						for v in range( nrg ):

							idp = str( self.vincularEstoque.GetItem(v, 0 ).GetText() )
							cod = str( self.vincularEstoque.GetItem(v, 1 ).GetText() )
							des = self.vincularEstoque.GetItem(v, 2 ).GetText()
							fab = self.vincularEstoque.GetItem(v, 3 ).GetText()
							gru = self.vincularEstoque.GetItem(v, 4 ).GetText()
							vin = str( self.vincularEstoque.GetItem(v, 5 ).GetText() )
							sa1 = str( self.vincularEstoque.GetItem(v, 6 ).GetText() )
							sa2 = str( self.vincularEstoque.GetItem(v, 7 ).GetText() )

							if ind == v:	vinculo = "VINCULADO"
							else:	vinculo = vin
							
							relacao[_registros] = idp,cod,des,fab,gru,vinculo, sa1, sa2
							_registros +=1

						PFVListCtrl.itemDataMap  = relacao
						PFVListCtrl.itemIndexMap = relacao.keys()
						
						alertas.dia(self.painel,u"Produto Vinculado com Sucesso!!\n"+(" "*140),"Vincular Produtos")            

#-------: Vincular em Grupos
		elif event.GetId() == 430:
			
			if self.fgrupos.GetValue() !='':	vGrupos = self.fgrupos.GetValue()
			else:	vGrupos = u"[ A T E N Ç Ã O ] Vincular Todos os Produtos"
			informe = u"O sistema vai vincular apenas os produtos que não estjam vinculados..."

			vinculacao = wx.MessageDialog(self.painel,"{ Vincular em Grupo }\n\nFilial: "+_filial+" ["+_nomefl+"]\nGrupo/Fabricante: "+vGrupos+"\n\n"+informe+"\nConfirme p/vincular produtos a filial...\n"+(" "*140),"Vincular Produtos",wx.YES_NO|wx.NO_DEFAULT)
			if vinculacao.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Produtos: Vincular Produtos e Filias", fil = _ffl, janela = self.painel )
				grv  = True
				inv  = 0
				nvc  = 0 #-: Total de produtos vinculados
				nnv  = 0 #-: Total de produtos nao vinculados

				if sql[0] == True:

					_mensagem = mens.showmsg('Vincular')
					_registros = 0
					relacao = {}

					""" Atualiza Lista """
					for v in range( nrg ):

						idp = str( self.vincularEstoque.GetItem(v, 0 ).GetText() )
						cod = self.vincularEstoque.GetItem(v, 1 ).GetText()
						des = self.vincularEstoque.GetItem(v, 2 ).GetText()
						fab = self.vincularEstoque.GetItem(v, 3 ).GetText()
						gru = self.vincularEstoque.GetItem(v, 4 ).GetText()
						vin = str( self.vincularEstoque.GetItem(v, 5 ).GetText() )
						fis = str( self.vincularEstoque.GetItem(v, 6 ).GetText() )
						mar = str( self.vincularEstoque.GetItem(v, 7 ).GetText() )

						if not self.Tfisico.GetValue() and not self.afisico.GetValue():	fis = '0.0000'
						achf = sql[2].execute("SELECT ef_idfili FROM estoque WHERE ef_idfili='"+ _filial +"' and ef_codigo='"+ cod +"'")

						if achf:

							if self.Tfisico.GetValue() or self.afisico.GetValue():	sql[2].execute("UPDATE estoque SET ef_fisico='"+str( fis )+"' WHERE ef_idfili='"+ _filial +"' and ef_codigo='"+ cod +"'")

						if not achf:

							inserir = "INSERT INTO estoque ( ef_idfili, ef_codigo, ef_fisico ) VALUES ( %s,%s,%s )"
							sql[2].execute( inserir, ( _filial, cod, fis ) )

							relacao[_registros] = idp,cod,des,fab,gru,'VINCULADO'
							_registros +=1
							
							nvc +=1
							
						else:

							relacao[_registros] = idp,cod,des,fab,gru,vin,fis,mar
							_registros +=1

							nnv +=1

						_mensagem = mens.showmsg(str( v )+' [ '+idp+' '+cod+' ]\n'+des)

					del _mensagem

					PFVListCtrl.itemDataMap  = relacao
					PFVListCtrl.itemIndexMap = relacao.keys()
					
					try:
						sql[1].commit()
						
					except Exception, _reTornos:
						grv = False
						sql[1].rollback()

						if type( _reTornos ) != unicode:	_reTornos = str( _reTornos )
					conn.cls(sql[1])
					
					if grv == True:	alertas.dia(self.painel,str( _filial) +" - Processo Finalizado...\n\nTotal de Produtos: "+str( nrg )+"\n\nProdutos Vinculados: "+str( nvc )+"\nProdutos ja vinculados: "+str( nnv )+"\n"+(" "*100),"Vincular Produtos em Grupos")            
					if grv != True and nvc != 0:	alertas.dia(self.painel,str( _filial) +" Erro - Processo Interrompido...\n\nRetorno: "+ _reTornos +"\n"+(" "*100),"Vincular Produtos em Grupos")            
					if grv != True and nvc == 0:	alertas.dia(self.painel,str( _filial) +" - Processo Finalizado...\n\nTotal de Produtos: "+str( nrg )+"\n\nProdutos Vinculados: "+str( nvc )+"\nProdutos ja vinculados: "+str( nnv )+"\n"+(" "*100),"Vincular Produtos em Grupos")

	def adicionAltera(self,event):

		ind = self.vincularEstoque.GetFocusedItem()
		nrg = self.vincularEstoque.GetItemCount()
		cod = self.vincularEstoque.GetItem(ind, 1 ).GetText()
		
		if self.flRemot.GetValue() == '':
			
			alertas.dia( self.painel, "Selecione uma filial remota p/Continuar!!\n"+(" "*100),"Incluir/Alterar Produtos em Filial Remota")
			return 

		_vi = "Incluir-Atualizar produto selecionado para a filial: { "+str( self.flRemot.GetValue() )+" }"
		if event.GetId() == 451:	_vi = "Incluir-Atualizar grupos,fabricante de produtos para a filial: { "+str( self.flRemot.GetValue() )+" }"
		inAlT = wx.MessageDialog(self.painel,_vi+"\n\nConfirme p/Continuar\n"+(" "*140),"Incluir-Atualizar Produtos",wx.YES_NO|wx.NO_DEFAULT)

		if inAlT.ShowModal() ==  wx.ID_YES:

#---------: Incluir um unico produto
			if event.GetId() == 450:

				_ffl = self.pFFilial
				conn = sqldb()
				sql1  = conn.dbc("Produtos: vincular grupos", fil = _ffl, janela = self.painel )
				uPd   = 0
				grv   = ''

				if sql1[0] == True:
					
					uPd = sql1[2].execute("SELECT * FROM produtos WHERE pd_codi='"+str( cod )+"'")
					uRs = sql1[2].fetchall()

					if uPd !=0:

						sql1[2].execute("DESC produtos")

						_ordem  = 0
						_campos = sql1[2].fetchall()
						for _field in uRs:	pass
						for i in _campos:
								
							_conteudo = _field[_ordem]
							exec "%s=_conteudo" % ('self.'+i[0])
							_ordem+=1
					
					conn.cls( sql1[1] )

				if uPd !=0:

					_ffl = self.flRemot.GetValue().split('-')[0]

					self.sql2  = conn.dbc("Produtos: atualizando informações remota, Filial: { "+str( _ffl )+" }", fil = _ffl, janela = self.painel )
					aTualizei = 0
					acna = 0

					if self.sql2[0] == True:
						
						try:
							
							acna = self.sql2[2].execute("SELECT pd_nome FROM produtos WHERE pd_codi='"+str( cod )+"'")
							aTualizei,_TF = self.GravarProdutoRemoto( acna, _ffl, cod )
							
							self.sql2[1].commit()
							grv = True
							
						except Exception, _reTornos:
							grv = False	
							self.sql2[1].rollback()
						
						conn.cls( self.sql2[1] )
					
					if grv == True and acna !=0 and aTualizei == 0:	alertas.dia( self.painel, "Dados do produtos ja estava atualizado...\n"+(" "*100),"Atualizando Informações Remota")
					if grv == True and acna !=0 and aTualizei == 1:	alertas.dia( self.painel, "Dados do produtos A T U A L I Z A D O com Sucesso!!\n"+(" "*100),"Atualizando Informações Remota")

					if grv == True and acna == 0 and aTualizei == 0:	alertas.dia( self.painel, "Produto não foi I N C L U Í D O na Filial...\n"+(" "*100),"Incluindo Informações Remota")
					if grv == True and acna == 0 and aTualizei == 1:	alertas.dia( self.painel, "Dados do produtos INCLUÍDO com Sucesso!!\n"+(" "*100),"Incluindo Informações Remota")

					if grv == False:	alertas.dia( self.painel, "Processo não concluido...\n\nErro Retorno: "+str( _reTornos )+"\n"+(" "*100),"Incluindo Informações Remota")

#---------: Incluir um grupo de produtos
			if event.GetId() == 451:

				_ffl = self.pFFilial
				_ffr = self.flRemot.GetValue().split('-')[0]

				conn = sqldb()
				sql1 = conn.dbc("Produtos: incluiro grups", fil = _ffl, janela = self.painel )

				aTuaLiza = 0
				nATualiz = 0
				Incluido = 0
				nIncluid = 0

				ToTaIncl = 0
				ToTaATua = 0
				
				grv = ''
				
				if sql1[0] == True:

					sql1[2].execute("DESC produtos")
					_campos = sql1[2].fetchall()
					
					""" Abri o Banco Remoto p/Atualizacao """
					self.sql2 = conn.dbc("Cadastro de Produtos da Filial Remota\n\nIncluindo - Atualizando Produtos\n\nNº de Registros: { "+str( nrg )+" }", fil = _ffr, janela = self.painel )

					if self.sql2[0] == True:

						try:
							
							for nr in range( nrg ):

								cod = self.vincularEstoque.GetItem(nr, 1 ).GetText()
								uPd = sql1[2].execute("SELECT * FROM produtos WHERE pd_codi='"+str( cod )+"'")
								uRs = sql1[2].fetchall()

								if uPd !=0:
									
									_ordem  = 0
									for _field in uRs:	pass
									for i in _campos:
											
										_conteudo = _field[_ordem]
										exec "%s=_conteudo" % ('self.'+i[0])
										_ordem+=1
									
									""" Inclusao/Atualizacao da Filial Remota """
									acna = self.sql2[2].execute("SELECT pd_nome FROM produtos WHERE pd_codi='"+str( cod )+"'")
									aTlz,_TF = self.GravarProdutoRemoto( acna, _ffr, cod )

									if _TF == 0:	ToTaIncl +=1 
									if _TF != 0:	ToTaATua +=1

									if _TF == 0 and aTlz != 0:	Incluido +=1
									if _TF == 0 and aTlz == 0:	nIncluid +=1

									if _TF == 1 and aTlz != 0:	aTuaLiza +=1
									if _TF == 1 and aTlz == 0:	nATualiz +=1

							self.sql2[1].commit()
							grv = True

						except Exception, _reTornos:
							grv = False	
							self.sql2[1].rollback()

						conn.cls( self.sql2[1] )

					conn.cls( sql1[1] )

					informSaida = "Total de Produtos: { "+str( nrg ) +" }\nPara Incluir....: "+str( ToTaIncl )+"\nPara Atualizar: "+str( ToTaATua )+\
							  "\n\nProdutos incluídos.......: "+str( Incluido )+\
								"\nProdutos não incluídos: "+str( nIncluid )+\
							  "\n\nProdutos Atualizados....: "+str( aTuaLiza )+\
								"\nProdutos ja Atualizados: "+str( nATualiz )+"\n"
					
					if grv ==  True:	alertas.dia( self.painel,informSaida+(" "*100),"Dados da Inclusão - Atulização de Produtos")	
					if grv == False:	alertas.dia( self.painel, "Processo não concluido...\n\nErro Retorno: "+str( _reTornos )+"\n"+(" "*100),"Incluindo Informações Remota")
		
	def GravarProdutoRemoto(self, TF, _filial, _cod ):
		
		incp = "INSERT INTO produtos (pd_codi,pd_nome,pd_cara,pd_refe,pd_barr,pd_unid,pd_nmgr,pd_fabr,pd_intc,pd_ende,\
							pd_gara,pd_pesb,pd_pesl,pd_estm,pd_estx,pd_estt,pd_marg,pd_mrse,pd_mfin,pd_pcom,\
							pd_pcus,pd_cusm,pd_mdun,pd_coms,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,\
							pd_vdp1,pd_vdp2,pd_vdp3,pd_vdp4,pd_vdp5,pd_vdp6,pd_cont,pd_prom,pd_pdsc,pd_prod,\
							pd_bene,pd_cupf,pd_cfis,pd_cfir,pd_mark,pd_funa,pd_frac,pd_docf,pd_sug1,pd_sug2,\
							pd_simi,pd_agre,pd_marc,pd_cfor,pd_acds,pd_fbar,pd_pdof,pd_stcm,pd_qtem,\
							pd_alte,pd_kitc,pd_codk,pd_cokt,pd_cfsc,pd_imag,pd_cest,pd_para) VALUES(\
							%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,%s,%s)"

		aTua = "UPDATE produtos SET pd_nome=%s,pd_cara=%s,pd_refe=%s,pd_barr=%s,pd_unid=%s,pd_nmgr=%s,pd_fabr=%s,pd_intc=%s,pd_ende=%s,\
							pd_gara=%s,pd_pesb=%s,pd_pesl=%s,pd_estm=%s,pd_estx=%s,pd_estt=%s,pd_marg=%s,pd_mrse=%s,pd_mfin=%s,pd_pcom=%s,\
							pd_pcus=%s,pd_cusm=%s,pd_mdun=%s,pd_coms=%s,pd_tpr1=%s,pd_tpr2=%s,pd_tpr3=%s,pd_tpr4=%s,pd_tpr5=%s,pd_tpr6=%s,\
							pd_vdp1=%s,pd_vdp2=%s,pd_vdp3=%s,pd_vdp4=%s,pd_vdp5=%s,pd_vdp6=%s,pd_cont=%s,pd_prom=%s,pd_pdsc=%s,pd_prod=%s,\
							pd_bene=%s,pd_cupf=%s,pd_cfis=%s,pd_cfir=%s,pd_mark=%s,pd_funa=%s,pd_frac=%s,pd_docf=%s,pd_sug1=%s,pd_sug2=%s,\
							pd_simi=%s,pd_agre=%s,pd_marc=%s,pd_cfor=%s,pd_acds=%s,pd_fbar=%s,pd_pdof=%s,pd_stcm=%s,pd_qtem=%s,\
							pd_alte=%s,pd_kitc=%s,pd_codk=%s,pd_cokt=%s,pd_cfsc=%s,pd_imag=%s,pd_cest=%s,pd_para=%s WHERE pd_codi=%s"

		if TF == 0:
			
			dados = self.sql2[2].execute( incp,( self.pd_codi,self.pd_nome,self.pd_cara,self.pd_refe,self.pd_barr,self.pd_unid,self.pd_nmgr,self.pd_fabr,self.pd_intc,self.pd_ende,\
                                         self.pd_gara,self.pd_pesb,self.pd_pesl,self.pd_estm,self.pd_estx,self.pd_estt,self.pd_marg,self.pd_mrse,self.pd_mfin,self.pd_pcom,\
                                         self.pd_pcus,self.pd_cusm,self.pd_mdun,self.pd_coms,self.pd_tpr1,self.pd_tpr2,self.pd_tpr3,self.pd_tpr4,self.pd_tpr5,self.pd_tpr6,\
                                         self.pd_vdp1,self.pd_vdp2,self.pd_vdp3,self.pd_vdp4,self.pd_vdp5,self.pd_vdp6,self.pd_cont,self.pd_prom,self.pd_pdsc,self.pd_prod,\
                                         self.pd_bene,self.pd_cupf,self.pd_cfis,self.pd_cfir,self.pd_mark,self.pd_funa,self.pd_frac,self.pd_docf,self.pd_sug1,self.pd_sug2,\
                                         self.pd_simi,self.pd_agre,self.pd_marc,self.pd_cfor,self.pd_acds,self.pd_fbar,self.pd_pdof,self.pd_stcm,self.pd_qtem,\
                                         self.pd_alte,self.pd_kitc,self.pd_codk,self.pd_cokt,self.pd_cfsc,self.pd_imag,self.pd_cest,self.pd_para ) )

			""" Incluir no Estoque Fisico """
			if self.sql2[2].execute("SELECT ef_idfili FROM estoque WHERE ef_idfili='"+str( _filial )+"' and ef_codigo='"+str( _cod )+"'") == 0:

				inserir = "INSERT INTO estoque ( ef_idfili, ef_codigo ) VALUES ( %s,%s)"
				self.sql2[2].execute( inserir, ( _filial, _cod ) )

		""" Atualização de Produtos """
		if TF !=0:
			
			dados = self.sql2[2].execute( aTua, ( self.pd_nome,self.pd_cara,self.pd_refe,self.pd_barr,self.pd_unid,self.pd_nmgr,self.pd_fabr,self.pd_intc,self.pd_ende,\
                                         self.pd_gara,self.pd_pesb,self.pd_pesl,self.pd_estm,self.pd_estx,self.pd_estt,self.pd_marg,self.pd_mrse,self.pd_mfin,self.pd_pcom,\
                                         self.pd_pcus,self.pd_cusm,self.pd_mdun,self.pd_coms,self.pd_tpr1,self.pd_tpr2,self.pd_tpr3,self.pd_tpr4,self.pd_tpr5,self.pd_tpr6,\
                                         self.pd_vdp1,self.pd_vdp2,self.pd_vdp3,self.pd_vdp4,self.pd_vdp5,self.pd_vdp6,self.pd_cont,self.pd_prom,self.pd_pdsc,self.pd_prod,\
                                         self.pd_bene,self.pd_cupf,self.pd_cfis,self.pd_cfir,self.pd_mark,self.pd_funa,self.pd_frac,self.pd_docf,self.pd_sug1,self.pd_sug2,\
                                         self.pd_simi,self.pd_agre,self.pd_marc,self.pd_cfor,self.pd_acds,self.pd_fbar,self.pd_pdof,self.pd_stcm,self.pd_qtem,\
                                         self.pd_alte,self.pd_kitc,self.pd_codk,self.pd_cokt,self.pd_cfsc,self.pd_imag,self.pd_cest,self.pd_para, self.pd_codi ) )

			""" Incluir no Estoque Fisico """
			if self.sql2[2].execute("SELECT ef_idfili FROM estoque WHERE ef_idfili='"+str( _filial )+"' and ef_codigo='"+str( _cod )+"'") == 0:

				inserir = "INSERT INTO estoque ( ef_idfili, ef_codigo ) VALUES ( %s,%s)"
				self.sql2[2].execute( inserir, ( _filial, _cod ) )

		return dados,TF
		
	def selecionar(self,event):
		
		_ffl = self.pFFilial

		conn = sqldb()
		sql  = conn.dbc("Produtos: selecionando produtos filiais remota", fil = _ffl, janela = self.painel )
		fgr  = self.fgrupos.GetValue()
		cns  = self.consultar.GetValue()

		if sql[0] == True:

			""" Pesquisa filias em uma conexao remota """
			if nF.rF( cdFilial = _ffl ) == "T":

				rlF = sql[2].execute("SELECT * FROM cia ORDER BY ep_inde")
				rsF = sql[2].fetchall()
				
				fL,fR = nF.retornFiliais( rsF )
				
				self.flLocal.SetItems( fL )
				self.flRemot.SetItems( fR )

			rProdutos = "SELECT * FROM produtos WHERE pd_nome!=''"
			pProdutos = "SELECT * FROM produtos WHERE pd_nome!=''"

			if self.ajfabri.GetValue() == True and fgr !='':	rProdutos = rProdutos.replace("WHERE","WHERE pd_fabr='"+str( fgr )+"' and")
			if self.ajgrupo.GetValue() == True and fgr !='':	rProdutos = rProdutos.replace("WHERE","WHERE pd_nmgr='"+str( fgr )+"' and")
			if self.ajsubg1.GetValue() == True and fgr !='':	rProdutos = rProdutos.replace("WHERE","WHERE pd_sug1='"+str( fgr )+"' and")
			if self.ajsubg2.GetValue() == True and fgr !='':	rProdutos = rProdutos.replace("WHERE","WHERE pd_sug2='"+str( fgr )+"' and")
	
			if len( cns.split(":") ) > 1 and cns.split(":")[0].upper() == 'P':	rProdutos = pProdutos.replace("WHERE","WHERE pd_nome like '%"+str( cns.split(":")[1] )+"%' and")
			if len( cns.split(":") ) > 1 and cns.split(":")[0].upper() == 'C':	rProdutos = pProdutos.replace("WHERE","WHERE pd_codi like '%"+str( cns.split(":")[1] )+"%' and")
			if len( cns.split(":") ) > 1 and cns.split(":")[0].upper() == 'B':	rProdutos = pProdutos.replace("WHERE","WHERE pd_barr like '%"+str( cns.split(":")[1] )+"%' and")
			if len( cns.split(":") ) > 1 and cns.split(":")[0].upper() == 'R':	rProdutos = pProdutos.replace("WHERE","WHERE pd_refe like '%"+str( cns.split(":")[1] )+"%' and")
			if len( cns.split(":") ) > 1 and cns.split(":")[0].upper() == 'D':	rProdutos = pProdutos.replace("WHERE","WHERE pd_fbar like '%"+str( cns.split(":")[1] )+"%' and")
			if len( cns.split(":") ) > 1 and cns.split(":")[0].upper() == 'I':	rProdutos = pProdutos.replace("WHERE","WHERE pd_intc like '%"+str( cns.split(":")[1] )+"%' and")
			if len( cns.split(":") ) > 1 and cns.split(":")[0].upper() == 'X':	rProdutos = pProdutos.replace("WHERE","WHERE pd_nome like '"+str( cns.split(":")[1] )+"%' and")
			if len( cns.split(":") ) > 1 and cns.split(":")[0].upper() == 'X':	self.consultar.SetValue('')
			if len( cns.split(":") ) == 1:	rProdutos = rProdutos.replace("WHERE","WHERE pd_nome like '"+str( cns )+"%' and")

			""" Pesquisa encadeada """
			if len( self.consultar.GetValue().split("*") ) > 1:

				rProdutos = pProdutos
				for fpq in self.consultar.GetValue().split("*"):
					
					if fpq !='':	rProdutos = rProdutos.replace("WHERE","WHERE pd_nome like '%"+str( fpq )+"%' and")

			qProdutos = sql[2].execute( rProdutos )
			rProdutos = sql[2].fetchall()
			
			_registros = 0
			relacao = {}
	
			for i in rProdutos:

				relacao[_registros] = i[0],i[2],i[3],i[9],i[8],'',i[15],i[51]
				_registros +=1

			conn.cls(sql[1])

			self.vincularEstoque.SetItemCount( qProdutos )
			PFVListCtrl.itemDataMap  = relacao
			PFVListCtrl.itemIndexMap = relacao.keys()
			self.oco.SetLabel(u"Ocorrências {"+str( qProdutos )+"}")
			
			self.vincularEstoque.SetBackgroundColour("#DEE5DE")
			if nF.rF( cdFilial = _ffl ) == "T":	self.vincularEstoque.SetBackgroundColour('#BE8F8F')

	def onPaint(self,event):
		
		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#077D07") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Produtos: Vincular produtos ao Estoque Fisico", 0, 428, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(810, 345, 85, 82, 3)

class PFVListCtrl(wx.ListCtrl):

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
		self.attr6 = wx.ListItemAttr()
		self.attr7 = wx.ListItemAttr()

		self.attr1.SetBackgroundColour("#E0EFFB")
		self.attr2.SetBackgroundColour("#EEFFEE")
		self.attr3.SetBackgroundColour("#FFBEBE")
		self.attr4.SetBackgroundColour("#F6F6AE")
		self.attr5.SetBackgroundColour("#EB9494")
		self.attr6.SetBackgroundColour("#B07C7C")
		self.attr7.SetBackgroundColour("#DAE6DA")

		self.InsertColumn(0, 'Código ID', format=wx.LIST_ALIGN_LEFT,width=70)
		self.InsertColumn(1, 'Código',   format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(2, 'Descrição dos Produtos', width=600)
		self.InsertColumn(3, 'Fabricante', width=100)
		self.InsertColumn(4, 'Grupo', width=100)
		self.InsertColumn(5, 'Vinculado', width=100)
		self.InsertColumn(6, 'Estoque Antigo',format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(7, 'Marcados', width=70)
					
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		_ffl = self.TipoFilialRL
		index=self.itemIndexMap[item]

		if self.itemDataMap[index][7] == '4':	return self.attr6
		if self.itemDataMap[index][5] != '':	return self.attr2
		if item % 2 and nF.rF( cdFilial = _ffl ) == "T":	return self.attr6
		if item % 2:	return self.attr7
		
	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][5] != "":	return self.w_idx
		if self.itemDataMap[index][7] == "4":	return self.i_idx
		return self.w_idx

	def GetListCtrl(self):	return self


class Transferencias:
	
#---: Transferencia para o destino	
	def Transferir( self, nControle, Lista, fDestino, modulo, par, filialo='' ):
		""" 
			modulo 1-Transferencia atraves do pedido de transferencia
				   2-Transferencia posterior ao pedido de transferencia
		"""
		_ffl = fDestino
		
		if modulo == 1:	_ffa = par.fid
		if modulo == 2:	_ffa = filialo

		self.p = par

		CriarCTRL = numeracao()
		NumeroCTR = CriarCTRL.numero("8","Controle de compras", self.p.painel, _ffl )
		
		ItemsNLOC  = 0 #-----: Items Nao Localizados no destino
		reTornogv  = "" #----: Retorno da excessao
		gravaTrans = False #-: Transferencia gravada com sucesso 
		Informacao = "{ Informaçoes da Transferência }\n"
		Informargv = ""

		if NumeroCTR == 0:	Informargv +="1 - Numero do Controle não foi criado no destino { "+str( _ffl )+" }, [ Provavel: Servidor remoto Inacessivel !! ]\n"
		if NumeroCTR !=0:
			
			conn = sqldb()
			sql  = conn.dbc("Produtos: Transferência de Estoque { Destino }", fil = _ffl, janela = par )
			sql1 = conn.dbc("Produtos: Transferência Confirmação { Origem }", fil = _ffa, janela = par )

			if sql1[2] == False:	Informargv +="2 - Filial de Origem não Foi Aberta\n"
			if sql[2]  == False:	Informargv +="3 - Filial de Destino não Foi Aberta\n"

			nC = nP = 0
			lC = lP = ''
			
			if sql[0] == True and sql1[0] == True:
				
				nC = sql1[2].execute("SELECT * FROM ccmp  WHERE cc_contro='"+str( nControle )+"'")
				if nC !=0:	lC = sql1[2].fetchall()
			
				nP = sql1[2].execute("SELECT * FROM iccmp WHERE ic_contro='"+str( nControle )+"'")
				if nP !=0:	lP = sql1[2].fetchall()

				if nC == 0:	Informargv +="4 - Numero de Controle: "+str( nControle )+" em controle de pedido na origem, não foi localizado\n"
				if nP == 0:	Informargv +="5 - Numero de Controle: "+str( nControle )+" em controle de ITEMS na origem, não foi localizado\n"

				if nC !=0 and nP !=0:

					try:
						
						""" Numero de Controle, Filial """
						numeroControle = str( NumeroCTR ).zfill(10)
						idenTifcFilial = _ffl
						TipoPedidoTran = "7" #-: Pedidos de Transferencia de Destino
						ControleOrigem = nControle # -----: Pedido de Controle da origem
						ControleDestin = numeroControle #-: Pedido de Controle no Destino
						cTentradaSaida = "E" #------------: Controle de ITEMS Entrada-Estoque, Saida-Estoque
						
						sql1[2].execute("DESC ccmp")
						vPd = sql1[2].fetchall()

						sql1[2].execute("DESC iccmp")
						iPd = sql1[2].fetchall()
						
						""" Incluindo pedido """
						ordp = 0
						for _field in lC:pass

						for _p in vPd:
									
							_conteudo = _field[ordp]
							exec "%s=_conteudo" % ('self.'+_p[0])
							ordp +=1
						
						inPd = "INSERT INTO ccmp (cc_docume,cc_nomefo,cc_fantas,cc_crtfor,cc_ndanfe,cc_numenf,cc_dtlanc,cc_hrlanc,cc_uslanc,cc_nfemis,\
												  cc_nfdsai,cc_nfhesa,cc_tprodu,cc_baicms,cc_vlicms,cc_basest,cc_valost,cc_vfrete,cc_vsegur,cc_vdesco,\
												  cc_valoii,cc_valipi,cc_valpis,cc_vconfi,cc_vodesp,cc_vlrnfe,cc_tipoes,cc_filial,cc_duplic,cc_contro,\
												  cc_itemsp,cc_nserie,cc_stantv,cc_frantv,cc_dsantv,cc_emaile,cc_protoc,cc_fsegur,cc_fdesac,cc_tnffor,\
												  cc_cancel,cc_dtcanc,cc_hrcanc,cc_uscanc,cc_uccanc,cc_status,cc_icmfre,cc_forige,cc_fdesti,cc_fimtra,\
												  cc_envfil,cc_corige,cc_cdesti)\
								VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
									   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
									   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
									   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
									   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
									   %s,%s,%s)"

						sql[2].execute( inPd, ( self.cc_docume, self.cc_nomefo, self.cc_fantas, self.cc_crtfor, self.cc_ndanfe, self.cc_numenf, self.cc_dtlanc, self.cc_hrlanc, self.cc_uslanc, self.cc_nfemis,\
												self.cc_nfdsai, self.cc_nfhesa, self.cc_tprodu, self.cc_baicms, self.cc_vlicms, self.cc_basest, self.cc_valost, self.cc_vfrete, self.cc_vsegur, self.cc_vdesco,\
												self.cc_valoii, self.cc_valipi, self.cc_valpis, self.cc_vconfi, self.cc_vodesp, self.cc_vlrnfe, TipoPedidoTran, idenTifcFilial, self.cc_duplic, numeroControle,\
												self.cc_itemsp, self.cc_nserie, self.cc_stantv, self.cc_frantv, self.cc_dsantv, self.cc_emaile, self.cc_protoc, self.cc_fsegur, self.cc_fdesac, self.cc_tnffor,\
												self.cc_cancel, self.cc_dtcanc, self.cc_hrcanc, self.cc_uscanc, self.cc_uccanc, self.cc_status, self.cc_icmfre, self.cc_forige, self.cc_fdesti, self.cc_fimtra,\
												self.cc_envfil, ControleOrigem, ControleDestin ) )

						"""  Incluindo ITEMS """
						#if not _act: #-: True, Finalizacao apenas com aceite posterior c/aceite do gerente na filial destino { acessando a origem p/confirmacao }
							
						for ls in lP: #------: Lista de produtos a transferir
							
							ordi = 0
							for ii in iPd: #-: Lista de campos

								_conteudo = ls[ordi]
								exec "%s=_conteudo" % ('self.'+ii[0] ) #_i[0])
								ordi +=1
							
							"""  Apura Estoque Anterior  """
							eTa = "SELECT ef_fisico FROM estoque WHERE ef_idfili=%s and ef_codigo=%s"
							asT = sql[2].execute( eTa, ( _ffl, self.ic_cdprod ) )
							if asT != 0:	esToqueAnterio = sql[2].fetchall()[0][0]
							else:	esToqueAnterio = "0.0000"

							"""  Atualiza o Estoque Fisico  """
							aTu = "UPDATE estoque SET ef_fisico=( ef_fisico + %s ) WHERE ef_idfili=%s and ef_codigo=%s"
							Trf = sql[2].execute( aTu, ( self.ic_quanti, _ffl, self.ic_cdprod ) )
							if Trf == 0:	ItemsNLOC +=1

							iniT = "INSERT INTO iccmp ( ic_contro,ic_docume,ic_nomefo,ic_refere,ic_cbarra,ic_descri,ic_codncm,ic_cdcfop,ic_unidad,ic_quanti,\
														ic_quncom,ic_vlrpro,ic_untrib,ic_qtribu,ic_quatri,ic_pedido,ic_codcfi,ic_origem,ic_codcst,ic_ccsosn,\
														ic_modicm,ic_modcst,ic_enqipi,ic_bcicms,ic_pricms,ic_vlicms,ic_permva,ic_bascst,ic_prstic,ic_valrst,\
														ic_cstipi,ic_bscipi,ic_peripi,ic_vlripi,ic_cstpis,ic_vbcpis,ic_perpis,ic_vlrpis,ic_cstcof,ic_bccofi,\
														ic_prcofi,ic_vlrcof,ic_lancam,ic_horanl,ic_qtante,ic_fabric,ic_grupos,ic_vcusto,ic_qtunid,ic_prdvin,\
														ic_stantp,ic_stantv,ic_frantp,ic_frantv,ic_dsantp,ic_dsantv,ic_vlruni,ic_nregis,ic_cdprod,ic_subuni,\
														ic_medist,ic_pfsegu,ic_vfsegu,ic_pfdsac,ic_vfdsac,ic_esitem,ic_dtcanc,ic_hocanc,ic_uscanc,ic_cdusca,\
														ic_cancel,ic_qtanca,ic_icmfrm,ic_icmfrv,ic_filial,ic_uslanc,ic_cdusla,ic_tipoen,ic_fichae,ic_forige,\
														ic_fdesti)\
								   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
										  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
										  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
										  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
										  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
										  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
										  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
										  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
										  %s)"

							sql[2].execute( iniT, ( numeroControle, self.ic_docume, self.ic_nomefo, self.ic_refere, self.ic_cbarra, self.ic_descri, self.ic_codncm, self.ic_cdcfop, self.ic_unidad, self.ic_quanti,\
													self.ic_quncom, self.ic_vlrpro, self.ic_untrib, self.ic_qtribu, self.ic_quatri, self.ic_pedido, self.ic_codcfi, self.ic_origem, self.ic_codcst, self.ic_ccsosn,\
													self.ic_modicm, self.ic_modcst, self.ic_enqipi, self.ic_bcicms, self.ic_pricms, self.ic_vlicms, self.ic_permva, self.ic_bascst, self.ic_prstic, self.ic_valrst,\
													self.ic_cstipi, self.ic_bscipi, self.ic_peripi, self.ic_vlripi, self.ic_cstpis, self.ic_vbcpis, self.ic_perpis, self.ic_vlrpis, self.ic_cstcof, self.ic_bccofi,\
													self.ic_prcofi, self.ic_vlrcof, self.ic_lancam, self.ic_horanl, esToqueAnterio, self.ic_fabric, self.ic_grupos, self.ic_vcusto, self.ic_qtunid, self.ic_prdvin,\
													self.ic_stantp, self.ic_stantv, self.ic_frantp, self.ic_frantv, self.ic_dsantp, self.ic_dsantv, self.ic_vlruni, self.ic_nregis, self.ic_cdprod, self.ic_subuni,\
													self.ic_medist, self.ic_pfsegu, self.ic_vfsegu, self.ic_pfdsac, self.ic_vfdsac, cTentradaSaida, self.ic_dtcanc, self.ic_hocanc, self.ic_uscanc, self.ic_cdusca,\
													self.ic_cancel, self.ic_qtanca, self.ic_icmfrm, self.ic_icmfrv, idenTifcFilial, self.ic_uslanc, self.ic_cdusla, TipoPedidoTran, self.ic_fichae, self.ic_forige,\
													self.ic_fdesti ) )

						if ItemsNLOC != 0:	Informargv +="6 - "+str( ItemsNLOC )+", Produtos não localizado no destino e/ou não vinculado ao estoque fisico\n"
						if ItemsNLOC == 0:

							sql[1].commit()
							gravaTrans = True

						else:	sql[1].rollback()

					except Exception, reTornogv:

						sql[1].rollback()

				if gravaTrans == True and ItemsNLOC == 0 and sql1[0] == True:

					DTF = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
					env = "UPDATE ccmp SET cc_envfil=%s,cc_corige=%s,cc_cdesti=%s WHERE cc_contro=%s"
					sql1[2].execute( env, ( DTF, ControleOrigem, ControleDestin, nControle ) )

					sql1[1].commit()

			""" Fecha as Tabelas Abertas """
			if sql1[0] == True:conn.cls(sql1[1]) #-: Origem
			if sql[0]  == True:conn.cls(sql[1]) #--: Destino

		if Informargv == "":	Informacao +="Transferência Finalizada com sucesso!!"
		if Informargv != "":	Informacao +=Informargv
		
		return ( gravaTrans, fDestino, reTornogv, ItemsNLOC, Informacao, str( NumeroCTR ).zfill(10) )

#---: Adiciona ITEMS nos estoque de reserva e no TEMPORARIO
	def EsToqueVirtual( self, qTT, __ffl, item, ind, nControle, inAlT, qAnT, par ):

		""" Filial de Destino """
		flDesTino = par.p.flTrans.GetValue()
		idFlDesTi = par.p.flTrans.GetValue().split("-")[0]

		_ffl = __ffl
		_ffr = idFlDesTi

		_con = nControle #-------------------------------------------------: Numero do Controle
		_cdp = par.list_compra.GetItem( ind, 0 ).GetText() #---------------: Codigo do Produto
		_pro = par.list_compra.GetItem( ind, 1 ).GetText() #---------------: Descrição do Produto
		_uni = par.list_compra.GetItem( ind, 2 ).GetText().split('-')[0] #-: Unidade de Controle
		_idp = par.list_compra.GetItem( ind,16 ).GetText() #---------------: ID-Produto
		
		_log = login.usalogin #-: Usuario Atual

		dTaE = datetime.datetime.now().strftime("%Y/%m/%d")
		HraE = datetime.datetime.now().strftime("%T")

		conn = sqldb()
		sql  = conn.dbc("Produtos: Transferencia de Estoque", fil = _ffl, janela = par )
		rTn  = False
		qTd  = True
		flh  = True
		qTv  = 0
		dis  = 0

		if sql[0] == True:

			""" Verifica se produto estar vinculado no destino """
				
			""" Alteracao """
			if inAlT == 209:

				if nF.fu( __ffl ) == "T":	aTualiza = "UPDATE estoque SET ef_virtua=( ef_virtua - %s ) WHERE ef_codigo=%s"
				else:	aTualiza = "UPDATE estoque SET ef_virtua=( ef_virtua - %s ) WHERE ef_idfili=%s and ef_codigo=%s"

				if nF.fu( __ffl ) == "T":	sql[2].execute( aTualiza, ( qAnT, _cdp ) )
				else:	sql[2].execute( aTualiza, ( qAnT, __ffl, _cdp ) )

			if nF.fu( __ffl ) == "T":	achei = sql[2].execute( "SELECT ef_fisico,ef_virtua FROM estoque WHERE ef_codigo='"+str( _cdp )+"'" )
			else:	achei = sql[2].execute( "SELECT ef_fisico,ef_virtua FROM estoque WHERE ef_idfili='"+str( __ffl )+"' and ef_codigo='"+str( _cdp )+"'" )
			
			rache = sql[2].fetchall()

			qTv = rache[0][0]
			esv = rache[0][1]
			dis = ( qTv - esv )
			vir = ( esv + Decimal( qTT ) )

			if achei !=0 and ( qTv - esv ) >= Decimal( qTT ):
				
				try:
					
					Igrava = "INSERT INTO tdavs (tm_item,tm_cont,tm_codi,tm_nome,tm_quan,tm_unid,tm_logi,tm_lanc,tm_hora,tm_tipo,tm_fili,tm_idpd)\
							  VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

					if nF.fu( __ffl ) == "T":	Agrava = "UPDATE estoque SET ef_virtua=( ef_virtua + %s ) WHERE ef_codigo=%s"
					else:	Agrava = "UPDATE estoque SET ef_virtua=( ef_virtua + %s ) WHERE ef_idfili=%s and ef_codigo=%s"

					sql[2].execute( Igrava, ( item, _con, _cdp, _pro, qTT, _uni, _log, dTaE, HraE, 'T', _ffl, _idp ) )
					if nF.fu( __ffl ) == "T":	sql[2].execute( Agrava, ( qTT, _cdp ) )
					else:	sql[2].execute( Agrava, ( qTT, _ffl, _cdp ) )
					
					sql[1].commit()
					rTn = True

				except Exception, _reTornos:
					sql[1].rollback()
					flh = False

			else:	qTd = False
			
			conn.cls(sql[1])

			if flh == True and achei == 0:	alertas.dia(par,"Produto não localizado...\n"+(" "*100),"Produtos: 1-Transferência de Estoque")
			if flh == True and qTd == False:	alertas.dia(par,"Quantidade não disponivel!!\n\nEstoque Físico.........: "+str( qTv )+"\nEstoque de Reserva: "+str( esv )+"\n\nEstoque Disponível.........: "+str( dis )+"\nQuantidade selecionada: "+str( qTT )+"\n"+(" "*100),"Produtos: Tranferência de Estoque")
			if flh == False:	alertas.dia(par,"Processo não concluido!!\n\nErro Retorno: "+str( _reTornos )+"\n"+(" "*130),"Produtos: Tranferência de Estoque")
			
		return rTn
	
#---: Ajusta quantidades no virtual e apaga ITEMS no Temporario	
	def devTransf( self, LisTa, par, NumControle = "", individual = False ):

		_ffl = par.fid
		
		conn = sqldb()
		sql  = conn.dbc("Produtos: Cancela Transferência de Estoque", fil = _ffl, janela = par )
		
		if sql[0] == True:
			
			if individual == False:
				
				grv = True
				try:

					nRg = LisTa.GetItemCount()
				
					for i in range( nRg ):
						
						qTd = LisTa.GetItem( i,  4 ).GetText() #-: Quantidade
						cdp = LisTa.GetItem( i, 41 ).GetText() #-: Codigo do Produto
						idp = LisTa.GetItem( i, 79 ).GetText() #-: ID-Produto
						iTe = LisTa.GetItem( i, 97 ).GetText() #-: Numero do ITEM ID-do ITEM
						
						if nF.fu( _ffl ) == "T":	aTualiza = "UPDATE estoque SET ef_virtua=( ef_virtua - %s ) WHERE ef_codigo=%s"
						else:	aTualiza = "UPDATE estoque SET ef_virtua=( ef_virtua - %s ) WHERE ef_idfili=%s and ef_codigo=%s"

						TempATua = "DELETE FROM tdavs WHERE tm_cont=%s and tm_item=%s and tm_fili=%s and tm_codi=%s"
						
						if nF.fu( _ffl ) == "T":	sql[2].execute( aTualiza, ( qTd, cdp ) )
						else:	sql[2].execute( aTualiza, ( qTd, _ffl, cdp ) )
						
						sql[2].execute( TempATua, ( NumControle, iTe, _ffl, cdp ) )

					sql[1].commit()

				except Exception, _reTornos:
					sql[1].rollback()
					grv = False
				
			elif individual == True:
			
				grv = True
				try:
					
					i = LisTa.GetFocusedItem()
					qTd = LisTa.GetItem( i,  4 ).GetText() #-: Quantidade
					cdp = LisTa.GetItem( i, 41 ).GetText() #-: Codigo do Produto
					idp = LisTa.GetItem( i, 79 ).GetText() #-: ID-Produto
					iTe = LisTa.GetItem( i, 97 ).GetText() #-: Numero do ITEM ID-do ITEM

					if nF.fu( _ffl ) == "T":	aTualiza = "UPDATE estoque SET ef_virtua=( ef_virtua - %s ) WHERE ef_codigo=%s"
					else:	aTualiza = "UPDATE estoque SET ef_virtua=( ef_virtua - %s ) WHERE ef_idfili=%s and ef_codigo=%s"
					
					TempATua = "DELETE FROM tdavs WHERE tm_cont=%s and tm_item=%s and tm_fili=%s and tm_codi=%s"

					if nF.fu( _ffl ) == "T":	sql[2].execute( aTualiza, ( qTd, cdp ) )
					else:	sql[2].execute( aTualiza, ( qTd, _ffl, cdp ) )
					
					sql[2].execute( TempATua, ( NumControle, iTe, _ffl, cdp ) )
					
					sql[1].commit()

				except Exception, _reTornos:
					sql[1].rollback()
					grv = False
				
			conn.cls(sql[1])

			if individual == False and grv == False:	alertas.dia(par,"Apagando p/Item, processo não finalizado!!\n\nErro Retorno: "+str( _reTornos )+"\n"+(" "*120),"Produtos: Tranferência de Estoque")
			if individual == True  and grv == False:	alertas.dia(par,"Apagando Todos os Produtos, processo não finalizado!!\n\nErro Retorno: "+str( _reTornos )+"\n"+(" "*120),"Produtos: Tranferência de Estoque")

		return grv

class pendencias:
	
	def pendenciaRemota(self, parent, lisTa=[] ):

		_ffl = lisTa[2]
		_ffr = lisTa[1]
		self.painel = parent.painel
		
		if lisTa !='':

			reen = wx.MessageDialog(parent,"Verificar pendências do pedido de transferência }\n\nFilial de destino: "+str( lisTa[1] )+"\nNº do Controle: "+str( lisTa[0] )+"\n\nConfirme p/Continuar\n"+(" "*140),"Reenviar pedido de transferência",wx.YES_NO|wx.NO_DEFAULT)
			
			if reen.ShowModal() ==  wx.ID_YES: 
			
				cT = lisTa[0] #-: Numero do controle
				fr = lisTa[1] #-: Filial Remota Destino
				fl = lisTa[2] #-: Filial do Pedido de Transferencia-Origem
				rl = '' #-------: Relacao de Itens do Pedido
				lP = 'Filial Origem: '+str( fl )+" Filial Destino: "+str( fr )+"\n\n{ Lista de Produtos para Transferência }\n" #-: Lista das Pendencias
				nP = 0
				conn = sqldb()
				
				sql1  = conn.dbc("Produtos-Transferência: Filial Origem",  fil = _ffl, janela = self.painel )
				sql2  = conn.dbc("Produtos-Transferência: Filial Destino", fil = _ffr, janela = self.painel )

				if sql1[0] == True:

					if sql1[2].execute("SELECT * FROM iccmp WHERE ic_contro='"+str( cT )+"'") !=0:	rl = sql1[2].fetchall()
					conn.cls(sql1[1])
				
				if sql2[0] == True:
					
					if rl !="":
						
						for i in rl:
							
							esC = sql2[2].execute( "SELECT pd_nome FROM produtos WHERE pd_codi='"+str( i[59] )+"'" )
							esF = sql2[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( fr )+"' and ef_codigo='"+str( i[59] )+"'" )

							prod = "Código: "+str(i[59])+"  Produto: "+str(i[6])+"  Quantidade: "+str(i[10])

							if esC != 0:	prod += ",Cadastrado"
							if esF != 0:	prod += ",Vinculado"

							if esC == 0:	prod +=",Não Cadastrado"
							if esF == 0:	prod +=",Não Vinculado"

							if esC == 0 or esF == 0:	nP +=1

							lP += prod + '\n'

					conn.cls(sql2[1])
				
				if nP == 0:	lP +="\n\n{ Sem Pendências }"
				if nP != 0:	lP +="\n\n{ Número de Pendências -"+str( nP )+"- }"

				MostrarHistorico.hs = lP
				MostrarHistorico.TP = ""
				MostrarHistorico.TT = "Transferência de Estoque-Produtos"
				MostrarHistorico.AQ = ""
				MostrarHistorico.FL = _ffl

				his_frame=MostrarHistorico(parent=parent,id=-1)
				his_frame.Centre()
				his_frame.Show()

	def reenviarTransferencia(self, parent, lisTa=[] ):

		_ffl = lisTa[2]
		mTr = Transferencias()
		
		if lisTa !='':

			reen = wx.MessageDialog(parent,"-A V I S O-\n{ Reenviar pedido de transferência com pendência }\n\nFilial de destino: { "+str( lisTa[1] )+" }\nConfirme p/Continuar\n"+(" "*140),"Reenviar pedido de transferência",wx.YES_NO|wx.NO_DEFAULT)
			
			if reen.ShowModal() ==  wx.ID_YES: 

				cT = lisTa[0] #-: Numero do controle
				fr = lisTa[1] #-: Filial Remota Destino
				fl = lisTa[2] #-: Filial do Pedido de Transferencia-Origem
				rl = '' #-------: Relacao de Itens do Pedido
				nP = 0

				conn = sqldb()
				sql  = conn.dbc("Produtos-Transferência: Filial Origem", fil = _ffl, janela = parent )

				if sql[0] == True:

					if sql[2].execute("SELECT * FROM iccmp WHERE ic_contro='"+str( cT )+"'"):	rl = sql[2].fetchall()

					ver = sql[2].execute("SELECT cc_envfil FROM ccmp WHERE cc_contro='"+str( cT )+"'")
					vrs = sql[2].fetchall()

					conn.cls(sql[1])

					if vrs and not vrs[0][0] and rl:
						

						rTrans = mTr.Transferir( cT, rl, lisTa[1], 2, parent, filialo = lisTa[2] )
						rTr = "Transferência finalizada com sucesso, Filial de destino: { "+str( fr )+" }\nNº do Pedido de Controle no Destino: "+str( rTrans[5] )

						if rTrans[0] != True or rTrans[3] !=0:	rTr = "\n\n{  A V I S O  }  Filial de Destino: "+str( rTrans[1] )+"\n\n1 - Transferência de Estoque p/filial destino não foi concluída\n2 - O pedido ficará em aberto p/Transferência posterior\n\n"+str( rTrans[4] )+"\n\nRetorno SQL: "+str( rTrans[2] )

						alertas.dia(parent,"{ Dados da Transferência }\n\n"+rTr+"\n"+(' '*180),"Compras: Gravando Transferência")

					if ver !=0 and vrs[0][0] != '':	alertas.dia(parent,"Transferência ja finalizada: { "+str( vrs[0][0] )+" }\n"+(" "*140),"Compras: Gravando Transferência")


class consolidarEstoque:
	
	def consolidaFisico(self,par, ev, cd, ds ):

		_ffl = login.identifi
		conn = sqldb()
		sql  = conn.dbc("Consolidar Estoque Fisico-Locais", fil = _ffl, janela = par )
		lsT  = []
		TTe  = 0

		if sql[0] == True:
			
			for i in login.ciaLocal:
				
				if i !="":

					idf = i.split('-')[0]
					nfl = i.split('-')[1]
					
					esF = sql[2].execute( "SELECT ef_fisico,ef_virtua,ef_trocas,ef_esloja FROM estoque WHERE ef_idfili='"+str( idf )+"' and ef_codigo='"+str( cd )+"'" )

					if esF !=0:
					
						rsT = sql[2].fetchall()[0]
						lsT.append("Local|"+str(idf)+"|"+str(nfl)+"|"+str(rsT[0])+"|"+str(rsT[1])+"|"+str(rsT[1])+"|"+str(rsT[3]) )
						TTe += rsT[0]
						

			conn.cls(sql[1])

		if ev == 613 and login.ciaRemot !='':

			for i in login.ciaRemot:
				
				if i !="":
					
					idf  = i.split('-')[0]
					nfl  = i.split('-')[1]
					_frr = idf
					
					sql1 = conn.dbc("Consolidar Estoque Fisico-Remotas\nFilial: { "+str( i )+" }",  fil = _frr, sm=False, janela = par )

					if sql1[0] == True:
						
						try:
							
							esF = sql1[2].execute( "SELECT ef_fisico,ef_virtua,ef_trocas,ef_esloja FROM estoque WHERE ef_idfili='"+str( idf )+"' and ef_codigo='"+str( cd )+"'" )
							if esF !=0:
							
								rsT = sql1[2].fetchall()[0]
								lsT.append("Remota|"+str(idf)+"|"+str(nfl)+"|"+str(rsT[0])+"|"+str(rsT[1])+"|"+str(rsT[1])+"|"+str(rsT[3]) )
								TTe += rsT[0]
								
						except Exception, _reTornos:	pass

						conn.cls(sql1[1])

		mosTrarFisicoConsolidado.lisTar = lsT
		mosTrarFisicoConsolidado.TTFisc = TTe
		mosTrarFisicoConsolidado.produT = cd+'-'+ds
		cns_frame=mosTrarFisicoConsolidado(parent=par,id=-1)
		cns_frame.Centre()
		cns_frame.Show()
			

class mosTrarFisicoConsolidado(wx.Frame):

	lisTar = []
	TTFisc = 0
	produT = ''
	
	def __init__(self, parent,id):

		self.p = parent

		wx.Frame.__init__(self, parent, 209, 'Produtos: Estoque físico consolidado ', size=(730,232), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.fconsolida = wx.ListCtrl(self.painel, 209,pos=(15,0), size=(715,188),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.fconsolida.SetBackgroundColour('#9AADC0')
		self.fconsolida.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
	
		self.fconsolida.InsertColumn(0,  u'Tipo Filial',     width=90)
		self.fconsolida.InsertColumn(1,  u'ID-Filial',       width=80)
		self.fconsolida.InsertColumn(2,  u'Nome Filial',     width=100)
		self.fconsolida.InsertColumn(3,  u'Físico',  format=wx.LIST_ALIGN_LEFT,width=85)
		self.fconsolida.InsertColumn(4,  u'Reserva ', format=wx.LIST_ALIGN_LEFT,width=85)
		self.fconsolida.InsertColumn(5,  u'RMA',     format=wx.LIST_ALIGN_LEFT,width=85)
		self.fconsolida.InsertColumn(6,  u'Loja-local', format=wx.LIST_ALIGN_LEFT,width=85)
		self.fconsolida.InsertColumn(7,  u'Deposito', format=wx.LIST_ALIGN_LEFT,width=85)
		self.fconsolida.InsertColumn(8,  u'Observação',      width=100)

		wx.StaticText(self.painel, -1, "Total do Estoque Consolidado:",pos=(15,193)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, "Código-Descrição do Produto:", pos=(15,213)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		eF = wx.TextCtrl(self.painel,-1,value = str( self.TTFisc ), pos=(190,190), size=(100,18),style=wx.TE_READONLY|wx.TE_RIGHT)
		eF.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		eF.SetBackgroundColour('#BFBFBF')

		pD = wx.TextCtrl(self.painel,-1,value = str( self.produT ), pos=(190,210), size=(540,18),style=wx.TE_READONLY)
		pD.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		pD.SetBackgroundColour('#E5E5E5')
		pD.SetForegroundColour('#215689')
		
		saida = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/frente.png",    wx.BITMAP_TYPE_ANY), pos=(692,189), size=(36,20))

		ind = 0
		for f in self.lisTar:
			
			if f !='':

				ff = f.split("|")
				if Decimal( ff[3] ) !=0 and Decimal( ff[6] ) !=0:	estoque_deposito = ( Decimal( ff[3] ) - Decimal( ff[6] ) )
				else:	estoque_deposito = Decimal("0")

				self.fconsolida.InsertStringItem( ind, ff[0] )

				self.fconsolida.SetStringItem( ind, 1, ff[1] )
				self.fconsolida.SetStringItem( ind, 2, ff[2] )
				if Decimal( ff[3] ):	self.fconsolida.SetStringItem( ind, 3, ff[3] )
				if Decimal( ff[4] ):	self.fconsolida.SetStringItem( ind, 4, ff[4] )
				if Decimal( ff[5] ):	self.fconsolida.SetStringItem( ind, 5, ff[5] )
				if Decimal( ff[6] ):	self.fconsolida.SetStringItem( ind, 6, ff[6] )
				if Decimal( estoque_deposito ):	self.fconsolida.SetStringItem( ind, 7, str( estoque_deposito ) )

				if ff[0] == "Remota":	self.fconsolida.SetItemBackgroundColour(ind, "#BE9098")
				if Decimal( ff[3] ) < 0:	self.fconsolida.SetItemBackgroundColour(ind, "#CB6E7E")
				ind +=1

		saida.Bind(wx.EVT_BUTTON, self.sair)
		
	def sair(self,event):	self.Destroy()	

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Estoque Físico Consolidado", 0, 227, 90)

class kiTVendas(wx.Frame):

	def __init__(self, parent,id):

		self.p = parent
		self.f = self.p.ppFilial
		mkn    = wx.lib.masked.NumCtrl
		self.a = False
		self.o = [] #-: Guarda a lista original para ajustar produtos apagados da lista


		wx.Frame.__init__(self, parent, 209, 'Produtos: Composição do KiT', size=(730,230), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)

		self.mKit = wx.ListCtrl(self.painel, 209,pos=(30,0), size=(698,145),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.mKit.InsertColumn(0,  u'Codigo', format=wx.LIST_ALIGN_LEFT,width=100)
		self.mKit.InsertColumn(1,  u'Descrição do Produto', width=400)
		self.mKit.InsertColumn(2,  u'Quantidade', format=wx.LIST_ALIGN_LEFT,width=120)
		self.mKit.InsertColumn(3,  u'Codigo do KIT', format=wx.LIST_ALIGN_LEFT,width=120)
		self.mKit.InsertColumn(4,  u'Filial', width=80)

		self.mKit.SetBackgroundColour('#9AADC0')
		self.mKit.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.Bind(wx.EVT_ENTER_WINDOW,self.AtualizaProduto)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,u"Quantidade/Unidades", pos=(495,188)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		wx.StaticText(self.painel,-1,u"Descrição do Produto p/Incluir",        pos=(2,150)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Descrição do Produto { Kit-Conjunto }", pos=(2,188)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Quantidade/Unidades", pos=(495,188)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nKiT = wx.StaticText(self.painel,-1,u"", pos=(180,150))
		self.nKiT.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nKiT.SetForegroundColour("#A52A2A")

		self.oco = wx.StaticText(self.painel,-1,u"Ocorrências", pos=(495,150))
		self.oco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.oco.SetForegroundColour("#28738C")

		self.pm = wx.TextCtrl(self.painel,-1,value = '', pos=(0,162),size=(480,22), style=wx.TE_READONLY)
		self.pm.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		self.pm.SetForegroundColour('#0000FF')
		self.pm.SetBackgroundColour('#E5E5E5')

		self.ic = wx.TextCtrl(self.painel,-1,value = '', pos=(0,200),size=(480,22), style=wx.TE_READONLY)
		self.ic.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		self.ic.SetForegroundColour('#AC1E1E')
		self.ic.SetBackgroundColour('#E5E5E5')

		self.qT = mkn(self.painel, 700,  value = '0.0000', pos=(493,200), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 4, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.qT.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.altera = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/areceberm.png", wx.BITMAP_TYPE_ANY), pos=(650,150), size=(36,34))				
		self.adicio = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/cima26.png",    wx.BITMAP_TYPE_ANY), pos=(692,150), size=(36,34))				
		self.apagar = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(650,190), size=(36,34))				
		self.gravar = wx.BitmapButton(self.painel, 204, wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(692,190), size=(36,34))				

		self.adicio.Bind(wx.EVT_BUTTON, self.adicionar)
		self.altera.Bind(wx.EVT_BUTTON, self.alTerar)
		self.apagar.Bind(wx.EVT_BUTTON, self.alTerar)
		self.gravar.Bind(wx.EVT_BUTTON, self.gravacao)

		self.qT.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.informar()

	def TlNum(self,event):

		TelNumeric.decimais = 3
		tel_frame=TelNumeric(parent=self,id=-1)
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor == '':	valor = str( self.qT.GetValue() )

		if Decimal(valor) > Decimal('99999.9999') or Decimal(valor) == 0:
			valor = str( self.qT.GetValue() )
			alertas.dia(self,"Quantidade enviado é incompatível!!","Caixa: Recebimento")

		self.qT.SetValue(valor)
		if Decimal( valor ) !=0:	self.adicionar(wx.EVT_BUTTON)

	def alTerar(self,event):
		
		indice = self.mKit.GetFocusedItem()
		if self.mKit.GetItemCount() !=0 and event.GetId() == 200:
			
			self.a = True
			self.mKit.SetBackgroundColour('#D5B2B8')

			codigo = self.mKit.GetItem(indice, 0).GetText()
			descri = self.mKit.GetItem(indice, 1).GetText()
			quanTi = self.mKit.GetItem(indice, 2).GetText()
			self.pm.SetValue( codigo+"-"+descri )
			self.qT.SetValue( str( quanTi ) )
			self.nKiT.SetLabel("{ Modo de Alteração }")
		
		elif self.mKit.GetItemCount() !=0 and event.GetId() == 202:
			
			receb = wx.MessageDialog(self.painel,"{ Apagar Lançamento Selecionado }\n\nConfirme fazer p/Cancelamento!!\n"+(" "*150),"Produtos: Montar KIT de Vendas",wx.YES_NO|wx.NO_DEFAULT)
			if receb.ShowModal() ==  wx.ID_YES:	self.mKit.DeleteItem( indice )
		
	def informar(self):
		
		indice = self.p.list_ctrl.GetFocusedItem()
		nRegis = self.p.list_ctrl.GetItemCount()
		codigo = self.p.list_ctrl.GetItem(indice, 0).GetText()
		descri = self.p.list_ctrl.GetItem(indice, 2).GetText()
		kitcon = self.p.list_ctrl.GetItem(indice,37).GetText()
		relaca = self.p.list_ctrl.GetItem(indice,38).GetText()

		conn = sqldb()
		sql  = conn.dbc("Produtos: Relacionando Kit-Conjunto", fil = self.f, janela = self )

		if sql[0]:

			if sql[2].execute("SELECT pd_kitc,pd_codk FROM produtos WHERE pd_codi='"+ codigo +"'"):	kitcon, relaca = sql[2].fetchone()
		
			conn.cls( sql[1] )
			
			self.ic.SetValue( codigo+"-"+descri )
			if kitcon.strip() !="T":
				
				self.altera.Enable( False )
				self.adicio.Enable( False )
				self.apagar.Enable( False )
				self.gravar.Enable( False )
				self.nKiT.SetLabel("{ Produto não estar marcado como KIT-Conjunto!! }")

			if relaca !=None and relaca !="":
				
				indi = 0
				for i in relaca.split('|'):
					
					if i !='':

						self.mKit.InsertStringItem( indi, i.split(";")[0] )
						self.mKit.SetStringItem(indi,1, i.split(";")[1] )	
						self.mKit.SetStringItem(indi,2, i.split(";")[2] )	
						self.mKit.SetStringItem(indi,3, self.ic.GetValue().split("-")[0] )	
						self.mKit.SetStringItem(indi,4, i.split(";")[3] )	

						self.o.append(i.split(";")[0]+";"+i.split(";")[1]+";"+i.split(";")[2]+";"+i.split(";")[3])
						indi +=1
		
	def AtualizaProduto(self,event):
		
		indice = self.p.list_ctrl.GetFocusedItem()
		nRegis = self.p.list_ctrl.GetItemCount()
		codigo = self.p.list_ctrl.GetItem(indice, 0).GetText()
		descri = self.p.list_ctrl.GetItem(indice, 2).GetText()

		self.pm.SetValue( codigo+"-"+descri )

		self.a = False
		self.mKit.SetBackgroundColour('#9AADC0')

	def adicionar(self,event):
		
		if 	 self.pm.GetValue().split("-")[0] == "" or self.ic.GetValue().split("-")[0] == "" or Decimal( self.qT.GetValue() ) == 0:	alertas.dia(self.painel,"{ Falta dados p/Incluir-Alterar }\n"+(' '*110),"Produtos: Montar KIT de Vendas")
		elif self.pm.GetValue().split("-")[0] !="" and self.ic.GetValue().split("-")[0] !="" and self.pm.GetValue().split("-")[0] == self.ic.GetValue().split("-")[0]:	alertas.dia(self.painel,"{ Não pode adicionar o produto KIT }\n"+(' '*110),"Produtos: Montar KIT de Vendas")
		else:
				
			nRegis = self.mKit.GetItemCount()
			indice = self.mKit.GetFocusedItem()
			codigo = str( self.pm.GetValue().split('-')[0] )
			consTa = False

			if self.a == False:

				conn = sqldb()
				sql  = conn.dbc("Produtos: Relacionando Kit-Conjunto", fil = self.f, janela = self )
				gva = False

				if sql[0] == True:

					if sql[2].execute("SELECT ef_idfili,ef_codigo FROM estoque WHERE ef_codigo='"+str( codigo )+"' and ef_idfili='"+str( self.f )+"'") == 0:

						alertas.dia(self.painel,"{ Produto não pertence a filial do Kit-Conjunto }\n"+(' '*110),"Produtos: Montar KIT de Vendas")

					else:
						
						for i in range( nRegis ):
								
							if self.mKit.GetItem(i, 0).GetText() == self.pm.GetValue().split('-')[0]:
					
								consTa = True
								break

						if consTa == False:

							self.mKit.InsertStringItem( nRegis, self.pm.GetValue().split("-")[0] )
							self.mKit.SetStringItem(nRegis,1, self.pm.GetValue().split("-")[1] )	
							self.mKit.SetStringItem(nRegis,2, str( Trunca.trunca( 5, self.qT.GetValue() ) ) )	
							self.mKit.SetStringItem(nRegis,3, self.ic.GetValue().split("-")[0] )	
							self.mKit.SetStringItem(nRegis,4, self.f )	

						if consTa == True:	alertas.dia(self.painel,"{ Produto ja consta na lista }\n"+(' '*110),"Produtos: Montar KIT de Vendas")

			elif self.a == True:

				self.mKit.SetStringItem(indice,2, str( Trunca.trunca( 5, self.qT.GetValue() ) ) )	

			self.a = False
			self.mKit.SetBackgroundColour('#9AADC0')
			self.nKiT.SetLabel("")

	def gravacao(self,event):

		if len( self.ic.GetValue().split('-') ) == 2: # and self.mKit.GetItemCount() !=0:
			
			conn = sqldb()
			sql  = conn.dbc("Produtos: Relacionando Kit-Conjunto", fil = self.f, janela = self )
			gva = False

			if sql[0] == True:

				nRegis = self.mKit.GetItemCount()
				
				codigo = self.ic.GetValue().split('-')[0]
				descri = self.ic.GetValue().split('-')[1]
				relaca = ""
				
				if codigo !='' and descri !='':
					
					for i in range( self.mKit.GetItemCount() ):
					
						relaca +=str(self.mKit.GetItem(i, 0).GetText())+";"+str( self.mKit.GetItem(i, 1).GetText() )+";"+str( self.mKit.GetItem(i, 2).GetText() )+";"+str( self.f )+"|"
					
						"""   ATualiza produtos pertencentes ao KIT   """
						
						_codigo = str( self.mKit.GetItem(i, 0).GetText() )
						_codKiT = str( self.mKit.GetItem(i, 3).GetText() )
				
						aTp = "UPDATE produtos SET pd_cokt='"+str( _codKiT )+"' WHERE pd_codi='"+str( _codigo )+"'"
						sql[2].execute( aTp )

					"""  Elimina Items Desmarcado   """
					for el in self.o:
						
						apagar = False
						
						for ls in range( self.mKit.GetItemCount() ):
							
							if el.split(";")[0] == str(self.mKit.GetItem(ls, 0).GetText()):	apagar = True
						
						if apagar == False:

							aTp = "UPDATE produtos SET pd_cokt='' WHERE pd_codi='"+str( el.split(";")[0] )+"'"
							sql[2].execute( aTp )

				if relaca !="" or not self.mKit.GetItemCount():
					
					if not self.mKit.GetItemCount(): relaca = ""
					grv = "UPDATE produtos SET pd_codk='"+str( relaca )+"' WHERE pd_codi='"+str( codigo )+"'"
					sql[2].execute( grv )
					sql[1].commit()
					gva = True
										
				conn.cls(sql[1])
				
				if gva == True:
					
					alertas.dia(self,"Processo finalizado dados atualizados!!\n"+(' '*110),"Produtos: Montar KIT de Vendas")
					self.Destroy()
					
				else:	alertas.dia(self,"Processo não finalizado...\n"+(' '*110),"Produtos: Montar KIT de Vendas")
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#26667B") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Montagem do KIT\nde Vendas", 0, 146, 90)


class ajCodigoFiscal(wx.Frame):

	cF = ""
	def __init__(self, parent,id):

		self.p = parent
		self.f = parent.ppFilial


		wx.Frame.__init__(self, parent, 209, 'Produtos: Ajuste de Códigos Fiscais', size=(505,135), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		wx.StaticText(self.painel,-1, u"Código Fiscal-Primario", pos=(16,3)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Código Fiscal-Regime Normal", pos=(16,48)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Código Fiscal-NFCe", pos=(16,95)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Descrição dos Grupo,Sub-Grupos", pos=(231,88)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ajgrupo = wx.RadioButton(self.painel, 601 , "Grupo",       pos=(233,5))
		self.ajsubg1 = wx.RadioButton(self.painel, 602 , "Sub-Grupo 1", pos=(233,27))
		self.ajsubg2 = wx.RadioButton(self.painel, 603 , "Sub-Grupo 2", pos=(233,50))
		self.ajgrupo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajsubg1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajsubg2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

#---------: Codigos Fiscais
		self.pd_cfis = wx.TextCtrl(self.painel, 500, '', pos=(15,17), size=(200,22), style = wx.TE_PROCESS_ENTER|wx.TE_READONLY)
		self.pd_cfis.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))


		self.pd_cfsc = wx.TextCtrl(self.painel, 502, '', pos=(15,62), size=(200,22), style = wx.TE_PROCESS_ENTER|wx.TE_READONLY)
		self.pd_cfsc.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pd_cfir = wx.TextCtrl(self.painel, 501, '', pos=(15,108), size=(200,22), style = wx.TE_PROCESS_ENTER|wx.TE_READONLY)
		self.pd_cfir.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.grupoSu = wx.ComboBox(self.painel, 604, '', pos=(230,102), size=(275,27), choices = '', style = wx.CB_READONLY)

		self.saida = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(470, 7), size=(34,34))
		self.salva = wx.BitmapButton(self.painel, 228, wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(470,52), size=(34,34))


		self.ajgrupo.Bind(wx.EVT_RADIOBUTTON, self.AjusteFiscal)
		self.ajsubg1.Bind(wx.EVT_RADIOBUTTON, self.AjusteFiscal)
		self.ajsubg2.Bind(wx.EVT_RADIOBUTTON, self.AjusteFiscal)

		self.AjusteFiscal(wx.EVT_RADIOBUTTON)
		self.saida.Bind(wx.EVT_BUTTON, self.sair)
		self.salva.Bind(wx.EVT_BUTTON, self.gravarCodigos)
		
		self.pd_cfis.Bind(wx.EVT_LEFT_DCLICK, self.buscaCodigoFiscal)				
		self.pd_cfis.Bind(wx.EVT_TEXT_ENTER,  self.buscaCodigoFiscal)			
		self.pd_cfir.Bind(wx.EVT_LEFT_DCLICK, self.buscaCodigoFiscal)				
		self.pd_cfir.Bind(wx.EVT_TEXT_ENTER,  self.buscaCodigoFiscal)
		self.pd_cfsc.Bind(wx.EVT_TEXT_ENTER,  self.buscaCodigoFiscal)
		self.pd_cfsc.Bind(wx.EVT_LEFT_DCLICK, self.buscaCodigoFiscal)
		
		
	def sair(self,event):	self.Destroy()
	def AjusteFiscal(self,event):

		self.grupoSu.SetValue('')
		if self.ajgrupo.GetValue() == True:	self.grupoSu.SetItems(self.p.grupos)
		if self.ajsubg1.GetValue() == True:	self.grupoSu.SetItems(self.p.subgr1)
		if self.ajsubg2.GetValue() == True:	self.grupoSu.SetItems(self.p.subgr2)

		
	def buscaCodigoFiscal(self,event):

		codigo = self.pd_cfis.GetValue()
		if event.GetId() == 501:	codigo = self.pd_cfir.GetValue()
		if event.GetId() == 502:	codigo = self.pd_cfsc.GetValue()

		TTributos.TLista = self.p.cdncms
		TTributos.cdfisc = codigo
		TTributos.TCodig = event.GetId()

		ajs_frame=TTributos(parent=self,id=-1)
		ajs_frame.Centre()
		ajs_frame.Show()

	def ajcodigos(self,_id,codigo,cst,Tipo):

		"""  Testa o codigo fiscal p/simples e regime-normal  """
		rT = self.cF.vCodigos(_id,codigo,cst,Tipo, self.f, self)
				
		if rT !=None and _id == 500:	self.pd_cfis.SetValue(codigo)
		if rT !=None and _id == 501:	self.pd_cfir.SetValue(codigo)
		if rT !=None and _id == 502:	self.pd_cfsc.SetValue(codigo)
		
		
	def gravarCodigos(self,event):

		grp = self.grupoSu.GetValue()

		pri = self.pd_cfis.GetValue().strip()
		nor = self.pd_cfsc.GetValue().strip()
		nfc = self.pd_cfir.GetValue().strip()
		
		grv = ""
		rTo = ""
		aTu = ""
		
		gok = False

		if pri !="":	grv = "UPDATE produtos SET pd_cfis='"+str( pri )+"' WHERE"
		if nor !="":	grv = "UPDATE produtos SET pd_cfsc='"+str( nor )+"' WHERE"
		if nfc !="":	grv = "UPDATE produtos SET pd_cfir='"+str( nfc )+"' WHERE"

		if pri != "" and nor != "":	grv = "UPDATE produtos SET pd_cfis='"+str( pri )+"', pd_cfsc='"+str( nor )+"' WHERE"
		if pri != "" and nfc != "":	grv = "UPDATE produtos SET pd_cfis='"+str( pri )+"', pd_cfir='"+str( nfc )+"' WHERE"
		if pri != "" and nor != "" and nfc !="":	grv = "UPDATE produtos SET pd_cfis='"+str( pri )+"', pd_cfsc='"+str( nor )+"', pd_cfir='"+str( nfc )+"' WHERE"
		if pri == "" and nor != "" and nfc !="":	grv = "UPDATE produtos SET pd_cfsc='"+str( nor )+"', pd_cfir='"+str( nfc )+"' WHERE"

		if grv !="" and grp !="" and self.ajgrupo.GetValue() == True:	grv = grv.replace("WHERE","WHERE pd_nmgr='"+str( grp )+"'")
		if grv !="" and grp !="" and self.ajsubg1.GetValue() == True:	grv = grv.replace("WHERE","WHERE pd_sug1='"+str( grp )+"'")
		if grv !="" and grp !="" and self.ajsubg2.GetValue() == True:	grv = grv.replace("WHERE","WHERE pd_sug2='"+str( grp )+"'")
		
			
		if grv !="" and grp !="":

 			conn = sqldb()
			sql  = conn.dbc("Produtos, Alteração de Códigos Fiscais", fil = self.f, janela = self )

			if sql[0] == True:

				cns = ""
				if self.ajgrupo.GetValue() == True:	cns = "SELECT pd_fili,pd_codi,pd_nome,pd_cfis,pd_cfsc,pd_cfir,pd_nmgr,pd_sug1,pd_sug2 FROM produtos WHERE pd_nmgr='"+str( grp )+"' ORDER BY pd_nome"
				if self.ajsubg1.GetValue() == True:	cns = "SELECT pd_fili,pd_codi,pd_nome,pd_cfis,pd_cfsc,pd_cfir,pd_nmgr,pd_sug1,pd_sug2 FROM produtos WHERE pd_sug1='"+str( grp )+"' ORDER BY pd_nome"
				if self.ajsubg2.GetValue() == True:	cns = "SELECT pd_fili,pd_codi,pd_nome,pd_cfis,pd_cfsc,pd_cfir,pd_nmgr,pd_sug1,pd_sug2 FROM produtos WHERE pd_sug2='"+str( grp )+"' ORDER BY pd_nome"
				
				if cns !="" and sql[2].execute( cns ) !=0:
					
					anT = sql[2].fetchall()
					aTu = "AT||||"+str( pri )+"|"+str( nor )+"|"+str( nfc )+"\n"
					for i in anT:
						
						aTu +="AN|"+str( i[0] )+"|"+str( i[1] )+"|"+str( i[2] )+"|"+str( i[3] )+"|"+str( i[4] )+"|"+str( i[5] )+"|"+str( i[6] )+"|"+str( i[7] )+"|"+str( i[8] )+"\n"
					
					"""  Atualiza os codigos  """
					try:
						
						sql[2].execute( grv )
						sql[1].commit()
						gok = True
						
					except Exception, _reTornos:
						
						rTo = _reTornos
				
				conn.cls( sql[1] )
				

			if gok == False and rTo !="":	alertas.dia(self,"{ Erro na gravação }\n\n"+str( rTo )+"\n"+(" "*100),"Produtos: Alteração de Códigos Fiscais")
			if gok == True  and rTo =="":
				
				dTa = datetime.datetime.now().strftime("%d%m%Y_%H%M")+'_'+login.usalogin
				_nomeArq = "/home/"+diretorios.usPrinci+"/direto/codigofiscal/ACF_"+dTa.lower()+".csv"

				__arquivo = open(_nomeArq,"w")
				__arquivo.write( aTu )
				__arquivo.close()

				alertas.dia(self,"{ Alterção de Códigos Fiscais, [ OK ]\n\nArquivo de Backup\n"+str( _nomeArq )+"\n"+(" "*150),"Produtos: Alteração de Códigos Fiscais")
				
				self.sair( wx.EVT_BUTTON )
				
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2F71B1") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Codificação Fiscal", 0, 130, 90)


class RecuperaCodigoFiscal(wx.Frame):

	arquivo = ""
	def __init__(self, parent,id):

		self.p = parent
		self.f = parent.f #ppFilial

		wx.Frame.__init__(self, parent, 209, 'Recuperação do código fiscal', size=(900,302), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaCF = wx.ListCtrl(self.painel, 400,pos=(14,1), size=(885,262),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaCF.SetBackgroundColour('#BFD7DF')
		self.ListaCF.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ListaCF.InsertColumn(0, 'Código', width=100)
		self.ListaCF.InsertColumn(1, 'Descrição dos Produtos', width=400)
		self.ListaCF.InsertColumn(2, 'CF-Primario',            width=145)
		self.ListaCF.InsertColumn(3, 'CF-Regime Normal',       width=145)
		self.ListaCF.InsertColumn(4, 'CF-NFCe',                width=145)
		self.ListaCF.InsertColumn(5, 'Grupo',                  width=200)
		self.ListaCF.InsertColumn(6, 'Sub-Gripo 1',            width=200)
		self.ListaCF.InsertColumn(7, 'Sub-Grupo 2',            width=200)
		self.ListaCF.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)

		ardp = open(self.arquivo,"r").read()
		orde = 0
		anTe = ""
		for rd in ardp.split('\n'):
			
			if rd !="":
				
				lsT = rd.split("|")
				if lsT[0] == "AT":	anTe = lsT
				if lsT[0] == "AN":
					
					self.ListaCF.InsertStringItem(orde, lsT[2])
					self.ListaCF.SetStringItem(orde,1,  lsT[3] )
					self.ListaCF.SetStringItem(orde,2,  lsT[4] )
					self.ListaCF.SetStringItem(orde,3,  lsT[5] )
					self.ListaCF.SetStringItem(orde,4,  lsT[6] )

					self.ListaCF.SetStringItem(orde,5,  lsT[7] )
					self.ListaCF.SetStringItem(orde,6,  lsT[8] )
					self.ListaCF.SetStringItem(orde,7,  lsT[9] )
					if orde % 2:	self.ListaCF.SetItemBackgroundColour(orde, "#92B8C4")

					orde +=1

		wx.StaticText(self.painel,-1, u"Códigos de Substituição\ndos produtos adicionados na lista", pos=(145,270)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Código Primario", pos=(330,265)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Código Regime Normal", pos=(523,265)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Código de NFCe", pos=(715,265)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.saida = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(13, 265), size=(36,34))
		self.salum = wx.BitmapButton(self.painel, 228, wx.Bitmap("imagens/importp.png",   wx.BITMAP_TYPE_ANY), pos=(55, 265), size=(36,34))
		self.salal = wx.BitmapButton(self.painel, 229, wx.Bitmap("imagens/agrupar16.png", wx.BITMAP_TYPE_ANY), pos=(100,265), size=(36,34))

#---------: Codigos Fiscais
		gp = gn = ge = ""

		if anTe !="" and len( anTe ) >= 5:	gp = anTe[4]
		if anTe !="" and len( anTe ) >= 6:	gn = anTe[5]
		if anTe !="" and len( anTe ) >= 7:	ge = anTe[6]

		self.pd_cfis = wx.TextCtrl(self.painel, 500, gp , pos=(327,278), size=(190,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pd_cfis.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pd_cfis.SetBackgroundColour("#BFBFBF")

		self.pd_cfsc = wx.TextCtrl(self.painel, 502, gn , pos=(520,278), size=(190,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pd_cfsc.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pd_cfsc.SetBackgroundColour("#BFBFBF")

		self.pd_cfir = wx.TextCtrl(self.painel, 501, ge , pos=(712,278), size=(188,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pd_cfir.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pd_cfir.SetBackgroundColour("#BFBFBF")

		self.saida .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.salum .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.salal .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.saida .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.salum .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.salal .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.saida.Bind(wx.EVT_BUTTON, self.sair)
		self.salum.Bind(wx.EVT_BUTTON, self.recupera)
		self.salal.Bind(wx.EVT_BUTTON, self.recupera)
		
	def sair(self,event):	self.Destroy()
	def passagem(self,event):

		indice = self.ListaCF.GetFocusedItem()
		self.pd_cfis.SetValue( self.ListaCF.GetItem( indice, 2 ).GetText() )
		self.pd_cfsc.SetValue( self.ListaCF.GetItem( indice, 2 ).GetText() )
		self.pd_cfir.SetValue( self.ListaCF.GetItem( indice, 2 ).GetText() )
		
	def recupera(self,event):

		receb = wx.MessageDialog(self,"Confirme para iniciar a recuperação de codigos fiscais...\n"+(" "*140),u"Recuperação de codigos fiscais",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() ==  wx.ID_YES:

			nRegis = self.ListaCF.GetItemCount()
			indice = self.ListaCF.GetFocusedItem()
			codigo = self.ListaCF.GetItem(indice, 0).GetText()

			codpri = self.ListaCF.GetItem(indice, 2).GetText()
			codnor = self.ListaCF.GetItem(indice, 3).GetText()
			codnfc = self.ListaCF.GetItem(indice, 4).GetText()
			
			conn = sqldb()
			sql  = conn.dbc("Produtos: Recuperação de Códigos Fiscais", fil = self.f, janela = self.painel )
			rTo = ""
			grv = ""
			
			if sql[0] == True:
			
				try:
					
					if event.GetId() == 228:
						
						rec = "UPDATE produtos SET pd_cfis='"+str( codpri )+"',pd_cfsc='"+str( codnor )+"',pd_cfir='"+str( codnfc )+"' WHERE pd_codi='"+str( codigo )+"'"
						sql[2].execute( rec )
						
					elif event.GetId() == 229:
						
						for i in range( nRegis ):

							codigo = self.ListaCF.GetItem(i, 0).GetText()

							codpri = self.ListaCF.GetItem(i, 2).GetText()
							codnor = self.ListaCF.GetItem(i, 3).GetText()
							codnfc = self.ListaCF.GetItem(i, 4).GetText()

							rec = "UPDATE produtos SET pd_cfis='"+str( codpri )+"',pd_cfsc='"+str( codnor )+"',pd_cfir='"+str( codnfc )+"' WHERE pd_codi='"+str( codigo )+"'"
							sql[2].execute( rec )
						
					sql[1].commit()
					grv = True
		
				except Exception, _reTornos:
					
					rTo = _reTornos
						
				conn.cls( sql[1] )
			
			if rTo !="":	alertas.dia(self,"{ Recuperação não concluída }\n\n"+str( rTo )+"\n"+(" "*150),"Produtos: Recuperação de Códigos Fiscais")
			if rTo =="" and grv == True:	alertas.dia(self,"{ Recuperação concluída }\n\n"+str( rTo )+"\n"+(" "*100),"Produtos: Recuperação de Códigos Fiscais")

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 222:	sb.mstatus("  Sair - Voltar",0)
		elif event.GetId() == 228:	sb.mstatus("  Recupera o código do produto selecioando",0)
		elif event.GetId() == 229:	sb.mstatus("  Recupera os códigos de todos os produtos da lista",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Recuperação de Códigos Fiscais",0)
		event.Skip()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2F71B1") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Recuperação dos Códigos Fiscais", 0, 298, 90)


class analiseABC:
	
	def analisaCurva(self, sql, parent, TP ):

		self.p = parent
		
		if TP == 1:	_descric = self.p.selecao.GetValue()
		
		dI = datetime.datetime.strptime(self.p.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		dF = datetime.datetime.strptime(self.p.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

		Id = datetime.datetime.strptime(self.p.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		Fd = datetime.datetime.strptime(self.p.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

		y,m,d=int( Fd.split('/')[2] ), ( int( Fd.split('/')[1] ) -1 ), int( login.qdiaMes[ Fd.split('/')[1] ] )
		if not self.p.fixData.GetValue():	self.p.datafinal.SetValue( wx.DateTimeFromDMY( d, m, y ) )

		
		""" 	Eliminando dados do Temporario    	"""	
		eliminar = "DELETE FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"' and tc_relat='GIROP'"
		sql[2].execute( eliminar )
		sql[1].commit()

		_produto = "SELECT * FROM produtos WHERE pd_regi!=0 ORDER BY pd_nome"
		
		if TP == 1 and self.p.pGrupo.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY pd_nome","and pd_nmgr='"+str( _descric )+"' ORDER BY pd_nome")
		if TP == 1 and self.p.psGru1.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY pd_nome","and pd_sug1='"+str( _descric )+"' ORDER BY pd_nome")
		if TP == 1 and self.p.psGru2.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY pd_nome","and pd_sug2='"+str( _descric )+"' ORDER BY pd_nome")
		if TP == 1 and self.p.pFabri.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY pd_nome","and pd_fabr='"+str( _descric )+"' ORDER BY pd_nome")
		if TP == 1 and self.p.pEnder.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY pd_nome","and pd_ende='"+str( _descric )+"' ORDER BY pd_nome")

		if TP == 1 and self.p.produT.GetValue() == True:	_produto = "SELECT * FROM produtos WHERE pd_codi='"+str( self.p._cd )+"' ORDER BY pd_nome"
		if TP == 2:	_produto = "SELECT * FROM produtos WHERE pd_codi='"+str( self.p._cd )+"' ORDER BY pd_nome"
		
		_car = sql[2].execute( _produto )
		_rca = sql[2].fetchall()

		iTem = 1
		if _car > 0:

			_mensagem = mens.showmsg("Totalizando { Inlcuindo/Atualizando }!!\n.\nAguarde...")

			for i in _rca:

				qAnterior = qPesquisar = False

				iTem +=1
				
				if self.p.fixData.GetValue() == True:	Id = Id.split("/")[0]+"/"+Id.split("/")[1]+"/"+Id.split("/")[2]
				else:	Id = "01/"+Id.split("/")[1]+"/"+Id.split("/")[2]
				
				"""  Atualiza a Data Inicial p/Enviar ao relatorio  """
				self.p.dindicial.SetValue( wx.DateTimeFromDMY( int(Id.split("/")[0]), ( int(Id.split("/")[1]) - 1 ), int(Id.split("/")[2])) )
				
				
				intervalo = Id+" - "+Fd 
				inicio, fim = [datetime.datetime.strptime(data.strip(), '%d/%m/%Y') for data in intervalo.split('-')]
				
				#meses = ( (fim - inicio).days / 30 ) #//Formula foi retirada pq estava considerando apenas inteiros, e  numero de meses a vezes fica menor [ 11-05-2018 ]
				meses = (fim.year - inicio.year) * 12 + fim.month - inicio.month + 1

				if self.p.fixData.GetValue() == True:	_daTa = Id.split("/")[2]+"/"+Id.split("/")[1]+"/"+Id.split("/")[0]
				else:	_daTa = Id.split("/")[2]+"/"+Id.split("/")[1]+"/01"
				
				daTap = datetime.datetime.strptime(_daTa, "%Y/%m/%d")

				""" Guarda a Data Inicial p/opcao de Relacionar Produtos """
				self.p.dp = Id 
				
				dias  = 0
				
				QTComp = QTVend = QTDevo = TVenda = Decimal("0.0000")

				""" Custo Medio,Vendas Medias Nº Vezes q Vendeu """
				_custo = _venda = _qTVez = vlrVnda = vlrDevo = Decimal('0.000')
				_qTT = _dTT = _dsc = _esF = ""


				""" Busca o Estoque Fisico Atual """
				EST = Decimal( "0.0000" )
				if self.p.rFilial.GetValue() == True:

					if nF.fu( self.p.pRFilial ) == "T":	EsF = sql[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_codigo='"+str( i[2] )+"'" )
					else:	EsF = sql[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( self.p.pRFilial )+"' and ef_codigo='"+str( i[2] )+"'" )
					
					EsR = sql[2].fetchall()
					if EsF !=0:	EST = EsR[0][0]


				if self.p.rFilial.GetValue() == False:

					EsF = sql[2].execute( "SELECT SUM( ef_fisico ) FROM estoque WHERE ef_codigo='"+str( i[2] )+"'" )
					EsR = sql[2].fetchall()
					if EsR[0][0] !=None:	EST = EsR[0][0]


				"""  Busca Movimentacao do Produto e Totalizacao  """
				if meses == 0:	meses = 1
				for m in range( meses ):

					if meses == 0 or meses == 1:	ven = format( daTap,"%d/%m/%Y")
					else:	ven =  ( daTap + datetime.timedelta(days=dias) ).strftime("%d/%m/%Y")

					"""  Alteracao p/data inicial e final fixa  """
					ultimo_dia_mes = str( calendar.monthrange( int( ven.split("/")[2] ), int( ven.split("/")[1] ) )[1] )
					
					if self.p.fixData.GetValue() == True:	ddI = ven.split("/")[2]+"/"+ven.split("/")[1]+"/"+ven.split("/")[0]
					else:	ddI = ven.split("/")[2]+"/"+ven.split("/")[1]+"/01"
					
					"""  Alteracao p/data inicial e final fixa  """
					if self.p.fixData.GetValue() == True:	ddF = ven.split("/")[2]+"/"+ven.split("/")[1]+"/"+str( fim ).split("-")[2]
					else:	ddF = ven.split("/")[2]+"/"+ven.split("/")[1]+"/"+ultimo_dia_mes

					Mes = ( ( datetime.datetime.strptime(ddI, "%Y/%m/%d").month ) - 1 )
					NMe = login.meses[Mes]+"-"+ven.split("/")[2]
					gRp = sG1 = sG2 = faB = ""

					if i[8] !="":	gRp = "Grupo: "+str(i[8])
					if i[61]!="":	sG1 = " Sub-Grupo1: "+str(i[61])
					if i[62]!="":	sG2 = " Sub-Grupo2: "+str(i[62])
					if i[9] !="":	faB = " Fabricante: "+str(i[9])

					_mensagem = mens.showmsg("Totalizando { Incluindo/Atualizando }!!\n"+gRp+sG1+sG2+faB+"\n\nDescição { "+str( iTem )+" de "+str( _car+1 )+" }: "+str( i[3] )+"\n"+str(NMe)+" ["+str( ddI )+"  "+str( ddF )+"]\n\nAguarde...")

					sCompra = "SELECT SUM(ic_fichae), SUM(ic_qtante) FROM iccmp WHERE ic_lancam>='"+str( ddI )+"' and ic_lancam<='"+str( ddF )+"' and ic_cdprod='"+str( i[2] )+"' and ic_cancel='' and ic_tipoen='1'"
					sVendas = "SELECT SUM(it_quan), SUM(it_prec), SUM(it_cprc), SUM(it_qtan), SUM(it_subt), COUNT(*) FROM idavs  WHERE it_lanc>='"+str( ddI )+"' and it_lanc<='"+str( ddF )+"' and it_codi='"+str( i[2] )+"' and it_canc='' and it_futu!='T' and it_tped='1'"
					sDevolu = "SELECT SUM(it_quan), SUM(it_prec), SUM(it_cprc), SUM(it_subt), COUNT(*) FROM didavs WHERE it_lanc>='"+str( ddI )+"' and it_lanc<='"+str( ddF )+"' and it_codi='"+str( i[2] )+"' and it_canc='' and it_futu!='T' and it_tped='1'"

					if self.p.rFilial.GetValue() == True:
						
						sCompra = sCompra.replace("WHERE","WHERE ic_filial='"+str( self.p.pRFilial )+"' and")
						sVendas = sVendas.replace("WHERE","WHERE it_inde='"+  str( self.p.pRFilial )+"' and")
						sDevolu = sDevolu.replace("WHERE","WHERE it_inde='"+  str( self.p.pRFilial )+"' and")

				
					pCompra = sql[2].execute(sCompra)
					qCompra = sql[2].fetchall()
	
					pVendas = sql[2].execute(sVendas)
					qVendas = sql[2].fetchall()

					pDevolu = sql[2].execute(sDevolu)
					qDevolu = sql[2].fetchall()

					IncluirAlterar = False
					if qCompra[0][0] != None:	IncluirAlterar = True
					if qVendas[0][0] != None:	IncluirAlterar = True
					if qDevolu[0][0] != None:	IncluirAlterar = True
		
					"""  Apurar o Saldo do Estoque Anterior ao primeiro lancamento  """
					if pCompra !=0 and qCompra[0][1] !=None and qPesquisar == False:	qAnterior = True
					if pVendas !=0 and qVendas[0][3] !=None and qPesquisar == False:	qAnterior = True

					if qAnterior == True and qPesquisar == False:

						__sCompra = "SELECT SUM( ic_qtante ), ic_lancam, ic_descri, COUNT(*) FROM iccmp WHERE ic_lancam>='"+str( ddI )+"' and ic_lancam<='"+str( ddF )+"' and ic_cdprod='"+str( i[2] )+"' and ic_cancel='' and ic_qtante!=0 and ic_tipoen='1' GROUP BY ic_lancam,ic_qtante"
						__sVendas = "SELECT SUM( it_qtan ), it_lanc, it_nome, COUNT(*) FROM idavs WHERE it_lanc>='"+str( ddI )+"' and it_lanc<='"+str( ddF )+"' and it_codi='"+str( i[2] )+"' and it_canc='' and it_qtan!=0 and it_futu!='T' and it_tped='1' GROUP BY it_lanc,it_qtan"

						if self.p.rFilial.GetValue() == True:	__sCompra = __sCompra.replace("WHERE","WHERE ic_filial='"+str( self.p.pRFilial )+"' and")
						if self.p.rFilial.GetValue() == True:	__sVendas = __sVendas.replace("WHERE","WHERE it_inde='"+str( self.p.pRFilial )+"' and")

						__qCompra = sql[2].execute(__sCompra)
						__cResult = sql[2].fetchall()

						__qVendas = sql[2].execute(__sVendas)
						__vResult = sql[2].fetchall()

						_qTc = _dTc = _qTv = _dTv = ""
						
						if __qCompra !=0:	_qTc, _dTc = __cResult[0][0],__cResult[0][1]
						if __qVendas !=0:	_qTv, _dTv = __vResult[0][0],__vResult[0][1]

						if _qTc !="":	_qTT, _dTT, _dsc, _esF = __cResult[0][0],__cResult[0][1],"Compra",str( EST )
						if _qTc !="" and _qTv !="" and _dTv < _dTc:	_qTT, _dTT, _dsc, _esF = __vResult[0][0],__vResult[0][1],"Venda",str( EST )
							
						qPesquisar = True

					if IncluirAlterar == True:
			
						achar = "SELECT tc_inform,tc_quantf,tc_quantd,tc_quant1 FROM tmpclientes WHERE tc_codi='"+str( i[2] )+"' and tc_usuari='"+str( login.usalogin )+"' and tc_relat='GIROP'"
						_acha = sql[2].execute(achar)
						racha = sql[2].fetchall()

						QIComp = QIVend = QIDevo = sVenda = sv = sd = Decimal("0.0000")

						""" Custo Medio,Vendas Medias Nº Vezes q Vendeu """
						custo = venda = qTVez = Decimal('0.000')

						if qCompra[0][0] != None:	QTComp += qCompra[0][0]
						if qVendas[0][0] != None:	QTVend += qVendas[0][0]
						if qDevolu[0][0] != None:	QTDevo += qDevolu[0][0]

						if qVendas[0][5] != None:

							qTVez   = qVendas[0][5]
							_qTVez += qVendas[0][5]

						if qVendas[0][2] != None:

							custo   = qVendas[0][2]
							_custo += qVendas[0][2]

						if qVendas[0][1] != None:
							venda   = qVendas[0][1]
							_venda += qVendas[0][1]
						
						if qVendas[0][4] != None:

							vlrVnda += qVendas[0][4]

						if qDevolu[0][3] != None:

							vlrDevo += qDevolu[0][3]

						if QTVend > QTDevo:	TVenda = ( QTVend - QTDevo )

						if qCompra[0][0] != None:	QIComp = format(qCompra[0][0],',')
						if qVendas[0][0] != None:	QIVend = format(qVendas[0][0],',')
						if qDevolu[0][0] != None:	QIDevo = format(qDevolu[0][0],',')

						if qVendas[0][0] != None:	sv = qVendas[0][0]
						if qDevolu[0][0] != None:	sd = qDevolu[0][0]
						
						if sv > sd:	sVenda = ( sv - sd )

						_dados = NMe+"|"+str(QIComp)+"|"+str(QIVend)+"|"+str(QIDevo)+"|"+str(sVenda)+"|"+str(qTVez)+"|"+str(custo)+"|"+str(venda)+"\n"
						_media = str(_qTVez)+"|"+str(_custo)+"|"+str(_venda)+"|"+str(_qTT)+"|"+str(_dTT)+"|"+str(_dsc)+"|"+str(_esF)+"|"+str(vlrVnda)+"|"+str(vlrDevo)

						if _acha !=0 and racha[0][0] != None and racha[0][0] != "":	_dados = racha[0][0]+_dados

						if _acha == 0:	IncluiDados = "INSERT INTO tmpclientes (tc_usuari,tc_inform,tc_codi,tc_nome,tc_relat,tc_quantf,tc_quantd,tc_quant1,tc_quant2,tc_infor2,tc_valor,tc_valor2) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
						if _acha != 0:	AlteraDados = "UPDATE tmpclientes SET tc_inform='"+str( _dados )+"',tc_quantf='"+str( QTComp )+"',tc_quantd='"+str( QTVend )+"',tc_quant1='"+str( QTDevo )+"',tc_quant2='"+str( TVenda )+"',tc_infor2='"+str( _media )+"',tc_valor='"+str( vlrVnda )+"',tc_valor2='"+str( vlrDevo )+"' WHERE tc_codi='"+str( i[2] )+"' and tc_usuari='"+str( login.usalogin )+"' and tc_relat='GIROP'"

						if _acha==0:	inserirc = sql[2].execute( IncluiDados, ( login.usalogin, _dados, i[2], i[3], "GIROP", QTComp, QTVend, QTDevo, TVenda, _media, vlrVnda, vlrDevo ) )
						if _acha!=0:	alterarc = sql[2].execute( AlteraDados )
						
					dias +=31

			sql[1].commit()

			del _mensagem

			if TP == 2:

				""" Finalizacao Giro de Produto """
				_Finaliza = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' and tc_relat='GIROP' ORDER BY tc_nome"
				_FinaRegi = sql[2].execute(_Finaliza)
				_FinaResu = sql[2].fetchall()

				indice = 0
				
				self.p.RLTprodutos.DeleteAllItems()					
				if _FinaRegi !=0:

					for f in _FinaResu:

						vQCompra = vQVendas = vQDevolu = sLVendas = mediavnd = ""
						if f[5]  !=0:	vQCompra = format( f[5],  ',' )
						if f[20] !=0:	vQVendas = format( f[20], ',' )
						if f[25] !=0:	vQDevolu = format( f[25], ',' )
						if f[26] !=0:	sLVendas = format( f[26], ',' )
							
						qTMeses = 0
						if len( f[1].split('\n') ) !=0:	qTMeses = ( len( f[1].split('\n') ) -  1 )
						if f[26] > f[25] and qTMeses !=0:	mediavnd = format( ( f[26] / qTMeses ), ',' )

						self.p.RLTprodutos.InsertStringItem( indice, str( f[16] ) )

						self.p.RLTprodutos.SetStringItem(indice,1, str( f[18] ) )	
						self.p.RLTprodutos.SetStringItem(indice,2, vQCompra )	
						self.p.RLTprodutos.SetStringItem(indice,3, vQVendas )	
						self.p.RLTprodutos.SetStringItem(indice,4, vQDevolu )	
						self.p.RLTprodutos.SetStringItem(indice,5, sLVendas )	
						self.p.RLTprodutos.SetStringItem(indice,6, mediavnd )	
						self.p.RLTprodutos.SetStringItem(indice,7, str( f[1] ) )	
						self.p.RLTprodutos.SetStringItem(indice,8, str( f[23] ) )	
						self.p.RLTprodutos.SetStringItem(indice,9, str( f[21] ) )	
						self.p.RLTprodutos.SetStringItem(indice,10,str( f[31] ) )

						indice +=1
			
	def gravaAbcProduto(self, parent, Filial ):

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Produtos Gravando Curva ABC...", fil = Filial, janela = parent )
		grv  = True
		""" Finalizacao Giro de Produto """
		if sql[0] == True:

			try:
				
				for i in range( parent.RLTprodutos.GetItemCount() ):

					if parent.RLTprodutos.GetItem(i, 0).GetText() !="":
						
						codigo = parent.RLTprodutos.GetItem(i, 0).GetText()
						descri = parent.RLTprodutos.GetItem(i, 1).GetText()
						
						qTComp = parent.RLTprodutos.GetItem(i, 2).GetText()
						qTVend = parent.RLTprodutos.GetItem(i, 3).GetText()
						qTDevo = parent.RLTprodutos.GetItem(i, 4).GetText()
						
						slVend = parent.RLTprodutos.GetItem(i, 5).GetText()
						mdVend = parent.RLTprodutos.GetItem(i, 6).GetText()
						
						ddRel1 = parent.RLTprodutos.GetItem(i, 7).GetText()
						ddRel2 = parent.RLTprodutos.GetItem(i, 8).GetText()
						
						TTVend = parent.RLTprodutos.GetItem(i, 9).GetText()
						TTDevo = parent.RLTprodutos.GetItem(i,10).GetText()
				
						if ";" in descri:	descri = descri.replace(";"," ")

						TxGrv = codigo+";"+descri+";"+qTComp+";"+qTVend+";"+qTDevo+";"+slVend+";"+mdVend+";"+ddRel1+";"+ddRel2+";"+TTVend+";"+TTDevo

						sql[2].execute("UPDATE produtos SET pd_dabc='"+ TxGrv +"' WHERE pd_codi='"+ codigo +"'")
						

				sql[1].commit()
				
				
			except Exception, Falha:	grv = False
			
			conn.cls( sql[1] )
			
			if grv == False:	alertas.dia(parent,"{ Falha na gravando curva ABC }\n\nRetorno: "+str( Falha )+"\n"+(" "*140),"Produtos: Gravando dados da curva ABC")
			if grv == True:	alertas.dia(parent,"{ Dados da curva ABC, Gravdo(s) com sucesso!!\n"+(" "*140),"Produtos: Gravando dados da curva ABC")


class TabelaCEST(wx.Frame):

	codigoc = ""
	
	def __init__(self, parent,id):

		self.p = parent
		self.t = ''
		self.pesqu  = ""
			
		if len( self.codigoc.split(".") ) >=4:	self.pesqu = self.codigoc.split(".")[0]

		wx.Frame.__init__(self, parent, 209, 'Tabela de Códigos CEST', size=(900,305), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaCEST = wx.ListCtrl(self.painel, 400,pos=(12,0), size=(882,265),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.ListaCEST.SetBackgroundColour('#BFD7DF')
		self.ListaCEST.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ListaCEST.InsertColumn(0, 'Nº ORDEM',      width=80)
		self.ListaCEST.InsertColumn(1, 'Código CEST',   width=100)
		self.ListaCEST.InsertColumn(2, 'Código NCM/SH', width=100)
		self.ListaCEST.InsertColumn(3, 'Grupo',         width=300)
		self.ListaCEST.InsertColumn(4, 'Descrição',     width=3000)
		self.ListaCEST.InsertColumn(5, 'NCM',           width=1000)
		
		wx.StaticText(self.painel,-1,"Código do NCM/SH, ou Fração do Código", pos=(13, 267)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"NCM/SH produto", pos=(400, 267)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ncmp = wx.TextCtrl(self.painel, 100, self.pesqu, pos=(397,280),size=(100, 20))
		self.ncmp.SetBackgroundColour('#BFBFBF')
		self.ncmp.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.consultar = wx.TextCtrl(self.painel, 100, "", pos=(10,280),size=(375, 20),style=wx.TE_PROCESS_ENTER)
		self.consultar.SetBackgroundColour('#E5E5E5')
		self.consultar.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.procu = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(530,265), size=(36,36))
		self.expor = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/one.png",      wx.BITMAP_TYPE_ANY), pos=(570,265), size=(36,36))
		self.saida = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/voltam.png",   wx.BITMAP_TYPE_ANY), pos=(860,265), size=(36,36))

		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.FilTrarCEST)
		self.expor.Bind(wx.EVT_BUTTON, self.exporTarCEST)
		self.procu.Bind(wx.EVT_BUTTON, self.FilTrarCEST)
		self.saida.Bind(wx.EVT_BUTTON, self.sair)
		
		self.levanTarCEST(wx.EVT_BUTTON)

	def sair(self,event):	self.Destroy()
	def FilTrarCEST(self,event):

		if self.t !="" and self.consultar.GetValue().strip() !="":
			
			indice = 0
			linhas = 0
			pesqu  = str( self.consultar.GetValue().strip() ).replace(".","")

			self.ListaCEST.DeleteAllItems()

			numero = len( pesqu )
			pesqui = pesqu
			if numero >= 5:	pesqui = pesqu[:4]+"."+pesqu[4:]
			if numero >= 6:	pesqui = pesqu[:4]+"."+pesqu[4:]
			if numero >= 7:	pesqui = pesqu[:4]+"."+pesqu[4:6]+"."+pesqu[6:]
			nLeTra = len( pesqui )

			for rd in self.t:
				
				if rd !="" and linhas !=0:

					if rd.split(";")[2][:nLeTra] == pesqui:

						descricao = rd.split(";")[3].decode('UTF-8')
						descgrupo = rd.split(";")[4]+"-"+rd.split(";")[5].decode('UTF-8')

						self.ListaCEST.InsertStringItem( indice, rd.split(";")[0] )
						self.ListaCEST.SetStringItem( indice,1, rd.split(";")[1])
						self.ListaCEST.SetStringItem( indice,2, rd.split(";")[2])
						self.ListaCEST.SetStringItem( indice,3, descgrupo )
						self.ListaCEST.SetStringItem( indice,4, descricao )
						self.ListaCEST.SetStringItem( indice,5, rd.split(";")[6] )
						if rd.split(";")[1] == pesqui:	achei = indice
						
						if indice % 2:	self.ListaCEST.SetItemBackgroundColour(indice, "#9CC0CC")
						indice +=1
					
				linhas +=1

	def levanTarCEST(self,event):
		
		if os.path.exists(diretorios.aTualPsT+"/srv/cest.csv") == True:
		
			self.t = open(diretorios.aTualPsT+"/srv/cest.csv","r").read()
			indice = 0
			linhas = 0
			achei  = -1
			self.t = self.t.strip().split("\n")

			numero = len( self.pesqu )
			pesqui = self.pesqu
			if numero >= 5:	pesqui = self.pesqu[:4]+"."+self.pesqu[4:]
			if numero >= 6:	pesqui = self.pesqu[:4]+"."+self.pesqu[4:]
			if numero >= 7:	pesqui = self.pesqu[:4]+"."+self.pesqu[4:6]+"."+self.pesqu[6:]
			self.ncmp.SetValue( pesqui )

			for rd in self.t:
				
				if rd !="" and linhas !=0:

#					descricao = str( rd.split(";")[3].decode('UTF-8') )
#					descgrupo = str( rd.split(";")[4] )+"-"+str( rd.split(";")[5].decode('UTF-8') )
					descricao = rd.split(";")[3]
					descgrupo = rd.split(";")[4]+"-"+rd.split(";")[5]

					self.ListaCEST.InsertStringItem( indice, rd.split(";")[0] )
					self.ListaCEST.SetStringItem( indice,1, rd.split(";")[1])
					self.ListaCEST.SetStringItem( indice,2, rd.split(";")[2])
					self.ListaCEST.SetStringItem( indice,3, descgrupo )
					self.ListaCEST.SetStringItem( indice,4, descricao )
					self.ListaCEST.SetStringItem( indice,5, rd.split(";")[6] )
					if rd.split(";")[2] == pesqui:	achei = indice
					
					if indice % 2:	self.ListaCEST.SetItemBackgroundColour(indice, "#9CC0CC")
					indice +=1
					
				linhas +=1
		

			if achei !=-1:

				self.ListaCEST.Select( achei )
				self.ListaCEST.Focus( achei )
				wx.CallAfter(self.ListaCEST.SetFocus) #-->[Forca o curso voltar a lista]


	def exporTarCEST(self,event):

		if self.ListaCEST.GetItemCount() !=0:

			indice = self.ListaCEST.GetFocusedItem()
			
			self.p.pd_cest.SetValue( self.ListaCEST.GetItem(indice, 1).GetText().replace(".","") )
			self.Destroy()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		

		dc.SetTextForeground("#712323") 	
		dc.DrawRotatedText("Cadastro de Códigos CEST", 0, 295, 90)


class TabelaPISCOFINS(wx.Frame):

	def __init__(self, parent,id):

		self.p = parent

		wx.Frame.__init__(self, parent, 209, 'Tabela de Códigos PIS-COFINS', size=(800,300), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaCST = wx.ListCtrl(self.painel, 400,pos=(12,0), size=(782,265),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		#self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.ListaCST.SetBackgroundColour('#BFD7DF')
		self.ListaCST.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ListaCST.InsertColumn(0, 'CST', width=100)
		self.ListaCST.InsertColumn(1, 'Descrição',   width=3000)
		
		#wx.StaticText(self.painel,-1,"Código do NCM, ou Fração do Código", pos=(13, 267)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		#wx.StaticText(self.painel,-1,"NCM do produto", pos=(400, 267)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		#ncmp = wx.TextCtrl(self.painel, 100, self.pesqu, pos=(397,280),size=(100, 20))
		#ncmp.SetBackgroundColour('#BFBFBF')
		#ncmp.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		#self.consultar = wx.TextCtrl(self.painel, 100, "", pos=(10,280),size=(375, 20),style=wx.TE_PROCESS_ENTER)
		#self.consultar.SetBackgroundColour('#E5E5E5')
		#self.consultar.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		#self.procu = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(530,265), size=(36,36))
		#self.expor = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/one.png",      wx.BITMAP_TYPE_ANY), pos=(570,265), size=(36,36))
		self.saida = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/voltam.png",   wx.BITMAP_TYPE_ANY), pos=(760,265), size=(36,36))

		#self.consultar.Bind(wx.EVT_TEXT_ENTER, self.FilTrarCEST)
		#self.expor.Bind(wx.EVT_BUTTON, self.exporTarCEST)
		#self.procu.Bind(wx.EVT_BUTTON, self.FilTrarCEST)
		self.saida.Bind(wx.EVT_BUTTON, self.sair)
		
		self.levanTarCST(wx.EVT_BUTTON)
		
	def sair(self,event):	self.Destroy()
	def levanTarCST(self,event):

		if os.path.exists(diretorios.aTualPsT+"/srv/piscofins.csv") == True:

			self.t = open(diretorios.aTualPsT+"/srv/piscofins.csv","r").readlines()
			indice = 0
			linhas = 0
			achei  = -1
			for rd in self.t:
				
				if rd !="" and linhas !=0:
					
					descricao = rd.split(";")[1]
					self.ListaCST.InsertStringItem( indice, rd.split(";")[0] )
					self.ListaCST.SetStringItem( indice,1, descricao )
					if indice % 2:	self.ListaCST.SetItemBackgroundColour(indice, "#9CC0CC")
					indice +=1
					
				linhas +=1


class rTabelas:
	
	def pis_cofins(self):
		
		rT = ['']
		if os.path.exists(diretorios.aTualPsT+"/srv/piscofins.csv") == True:

		
			self.t = open(diretorios.aTualPsT+"/srv/piscofins.csv","r").readlines()
			linhas = 0
			for rd in self.t:
				
				if rd !="" and linhas !=0:	rT.append( str( rd.split(";")[0] ) )
					
				linhas +=1

		return rT

	def parameTrosProduTos(self,paraMetros ):
		
		cpis = ppis = "0.00"
		ccof = pcof = "0.00"
		
		rpicf = []
		for p in paraMetros.split("|"):
	
			if p.split(":")[0] == "PIS":	cpis, ppis = p.split(":")[1].split(";")[0], p.split(":")[1].split(";")[1]
			if p.split(":")[0] == "COF":	ccof, pcof = p.split(":")[1].split(";")[0], p.split(":")[1].split(";")[1]
		
			
		rpicf = [cpis,ppis,ccof,pcof]
		rnnnm = [''] 
		return rpicf,rnnnm


	def calculaPrecoFilial(self,lisTa, cusTo, margem ):

		rT = lisTa.strip().split("|")
		ffl,fpv,fpr,foT,fcm = rT[0],rT[1],rT[2],rT[3],rT[4]
		ppv = fpv.split(";")
		ppr = fpr.split(";")
		mar = fcm.split(";")
		
		"""  Margem do produto original
			 Coloquei para usar depois se o clientes se houver a necessidade de fazer algum ajuste
		"""
		marOriginal = Decimal("0.00")
		if str( margem ) !="" and Decimal( str( margem ) ) > 0:	marOriginal = Decimal( str( margem ) )
		
		
		pv1 = pv2 = pv3 = pv4 = pv5 = pv6 = Decimal("0.00")
						
		if ppv[0] !="" and Decimal( ppv[0] ) >0 and mar[0] !="" and Decimal( mar[0] ) > 0:	pv1 =  Trunca.trunca(1 , ( cusTo + ( cusTo * Decimal(mar[0]) / 100 ) ) )
						
		if foT.split(";")[1] == "T": #-: Desconto
							 
			if ppv[1] !="" and Decimal( ppv[1] ) >0 and ppr[1] !="" and Decimal( ppr[1] ) > 0:	pv2	= str( Trunca.trunca(1 , ( pv1 - ( pv1 * Decimal(ppr[1]) / 100 ) ) ) )
			if ppv[2] !="" and Decimal( ppv[2] ) >0 and ppr[2] !="" and Decimal( ppr[2] ) > 0:	pv3	= str( Trunca.trunca(1 , ( pv1 - ( pv1 * Decimal(ppr[2]) / 100 ) ) ) )
			if ppv[3] !="" and Decimal( ppv[3] ) >0 and ppr[3] !="" and Decimal( ppr[3] ) > 0:	pv4	= str( Trunca.trunca(1 , ( pv1 - ( pv1 * Decimal(ppr[3]) / 100 ) ) ) )
			if ppv[4] !="" and Decimal( ppv[4] ) >0 and ppr[4] !="" and Decimal( ppr[4] ) > 0:	pv5	= str( Trunca.trunca(1 , ( pv1 - ( pv1 * Decimal(ppr[4]) / 100 ) ) ) )
			if ppv[5] !="" and Decimal( ppv[5] ) >0 and ppr[5] !="" and Decimal( ppr[5] ) > 0:	pv6	= str( Trunca.trunca(1 , ( pv1 - ( pv1 * Decimal(ppr[5]) / 100 ) ) ) )

		else: #------------------------: Acrescimo
							
			if ppv[1] !="" and Decimal( ppv[1] ) >0 and ppr[1] !="" and Decimal( ppr[1] ) > 0:	pv2	= str( Trunca.trunca(1 , ( pv1 + ( pv1 * Decimal(ppr[1]) / 100 ) ) ) )
			if ppv[2] !="" and Decimal( ppv[2] ) >0 and ppr[2] !="" and Decimal( ppr[2] ) > 0:	pv3	= str( Trunca.trunca(1 , ( pv1 + ( pv1 * Decimal(ppr[2]) / 100 ) ) ) )
			if ppv[3] !="" and Decimal( ppv[3] ) >0 and ppr[3] !="" and Decimal( ppr[3] ) > 0:	pv4	= str( Trunca.trunca(1 , ( pv1 + ( pv1 * Decimal(ppr[3]) / 100 ) ) ) )
			if ppv[4] !="" and Decimal( ppv[4] ) >0 and ppr[4] !="" and Decimal( ppr[4] ) > 0:	pv5	= str( Trunca.trunca(1 , ( pv1 + ( pv1 * Decimal(ppr[4]) / 100 ) ) ) )
			if ppv[5] !="" and Decimal( ppv[5] ) >0 and ppr[5] !="" and Decimal( ppr[5] ) > 0:	pv6	= str( Trunca.trunca(1 , ( pv1 + ( pv1 * Decimal(ppr[5]) / 100 ) ) ) )


		mReal = '0.00'
		if cusTo != 0 and pv1 != 0:	mReal = Trunca.trunca(1 , ( ( pv1 - cusTo ) / pv1 * 100 ) )


		npv = str(pv1)+";"+str(pv2)+";"+str(pv3)+";"+str(pv4)+";"+str(pv5)+";"+str(pv6)
		npr = str(mReal)+";"+str(ppr[1])+";"+str(ppr[2])+";"+str(ppr[3])+";"+str(ppr[4])+";"+str(ppr[5])
		nmc = str(mar[0])+";"+format(cusTo,'.4f')
		gpv = ffl+"|"+npv+"|"+npr+"|"+foT+"|"+nmc


		return gpv



"""   Tela de Entrada de dados para compra   """
class TelaCompra(wx.Frame):
	
	def __init__(self,parent,id):

		self.p = parent
		
		mkn = wx.lib.masked.NumCtrl
		self.Trunca = truncagem()
                              
		
		wx.Frame.__init__(self, parent, id, str( self.p.pcFilial )+' QT-Preço', size=( 215, 165 ), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self, style=wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_KEY_UP,self.Teclas)
		self.Bind(wx.EVT_CLOSE, self.sair)

		"""  Preco,Quantidade,IPI """
		wx.StaticText(self.painel,-1,"Preço:",      pos=(15, 9)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Quantidade: ",pos=(15,34)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"% I P I: ",   pos=(15,59)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"ST.Tributaria: ", pos=(15,84)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"[ + /F10 ]-Incluir Compra   Esc-Voltar\nF11-Entrada F12-Saida", pos=(15,108)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.preco = mkn(self.painel, id = 300, value = str( self.p.preccompra.GetValue() ), pos=(85, 5),style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 4, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#11617B", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry = True )
		self.quant = mkn(self.painel, id = 301, value = str( self.p.quantidade.GetValue() ), pos=(85,30),style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 4, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#11617B", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry = True )
		self.pripi = mkn(self.painel, id = 302, value = str( self.p.percentipi.GetValue() ), pos=(85,55),style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#11617B", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry = True )
		self.prstt = mkn(self.painel, id = 303, value = str( self.p.persubstit.GetValue() ), pos=(85,80),style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#11617B", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry = True )
		self.quant.SetFocus()

		self.preco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.quant.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pripi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.prstt.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.preco.SetFocus()

		self._entra = wx.RadioButton(self.painel, 377, "Entrada", pos=(10, 135),style=wx.RB_GROUP)
		self._saida = wx.RadioButton(self.painel, 378, "Saida  ", pos=(100,135))

		self._entra.SetValue( self.p.entra.GetValue() )
		self._saida.SetValue( self.p.saida.GetValue() )
		self._entra.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self._saida.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		if not self.p.p.acerto.GetValue():

			self._entra.Enable( False )
			self._saida.Enable( False )

		self.voltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltap.png",  wx.BITMAP_TYPE_ANY), pos=(172,60), size=(38,34))
		self.voltar.Bind(wx.EVT_BUTTON, self.sair)
		self._entra.Bind(wx.EVT_RADIOBUTTON, self.entradaSaida)
		self._saida.Bind(wx.EVT_RADIOBUTTON, self.entradaSaida)
		
	
	def sair(self,event):	self.Destroy()
	def entradaSaida(self,event):
		
		self.p.entra.SetValue( self._entra.GetValue() )
		self.p.saida.SetValue( self._saida.GetValue() )

	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()

		if keycode == wx.WXK_ESCAPE:	self.sair(wx.EVT_BUTTON)
		if keycode == 388 or keycode == wx.WXK_F10:
			
			self.p.insercao(wx.EVT_BUTTON)
			self.sair( wx.EVT_BUTTON )

		if keycode == wx.WXK_F11:

			self._entra.SetValue( True )
			self.entradaSaida(wx.EVT_BUTTON)

		if keycode == wx.WXK_F12:

			self._saida.SetValue( True )
			self.entradaSaida(wx.EVT_BUTTON)

		if controle !=None and controle.GetId() == 300:	self.p.preccompra.SetValue( str( self.preco.GetValue() ) )
		if controle !=None and controle.GetId() == 301:	self.p.quantidade.SetValue( str( self.quant.GetValue() ) )
		if controle !=None and controle.GetId() == 302:	self.p.percentipi.SetValue( str( self.pripi.GetValue() ) )
		if controle !=None and controle.GetId() == 303:	self.p.persubstit.SetValue( str( self.prstt.GetValue() ) )
		
		if controle !=None:	self.p.calCularPreco(controle.GetId())	
	
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#0E5C76") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Preço-Quantidade", 0, 162, 90)


"""   Tela de Entrada de dados para compra   """
class TelaLisTaPrecoSeparado(wx.Frame):
	
	Filial = ""
	
	def __init__(self,parent,id):

		self.p  = parent
		indice  = self.p.list_ctrl.GetFocusedItem()
		self.cp = self.p.list_ctrl.GetItem(indice,0).GetText()

		self.lsTa = "" #-: Guarda as filiais q for diferente da selecionada
		
		mkn = wx.lib.masked.NumCtrl
		self.Trunca = truncagem()
                              
		wx.Frame.__init__(self, parent, id, "Preços Individualizados p/Filial", size=( 365, 230 ), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self, style=wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_KEY_UP,self.Teclas)

		wx.StaticText(self.painel,-1,"Preço_1:", pos=(15, 14)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_2:", pos=(15, 34)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_3:", pos=(15, 54)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_4:", pos=(15, 74)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_5:", pos=(15, 94)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_6:", pos=(15,114)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Margem Real:", pos=(180, 14)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Acrescimo/Desconto_2:", pos=(180, 34)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Acrescimo/Desconto_3:", pos=(180, 54)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Acrescimo/Desconto_4:", pos=(180, 74)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Acrescimo/Desconto_5:", pos=(180, 94)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Acrescimo/Desconto_6:", pos=(180,114)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Margem:", pos=(15,143)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Custo:",  pos=(15,163)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"ID-Filial:", pos=(15,195)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.msg = wx.StaticText(self.painel,-1,"{ Mensagem }", pos=(15,210))
		self.msg.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.msg.SetForegroundColour("#7F7F7F")

		self.pd_tpr1 = mkn(self.painel, id = 241,  value = "0.00", pos = (67, 10), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False, selectOnEntry=True)
		self.pd_tpr2 = mkn(self.painel, id = 704,  value = "0.00", pos = (67, 30), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_tpr3 = mkn(self.painel, id = 705,  value = "0.00", pos = (67, 50), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_tpr4 = mkn(self.painel, id = 706,  value = "0.00", pos = (67, 70), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_tpr5 = mkn(self.painel, id = 707,  value = "0.00", pos = (67, 90), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_tpr6 = mkn(self.painel, id = 708,  value = "0.00", pos = (67,110), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

		self.pd_vdp1 = mkn(self.painel, id = 231, value = "0.00", pos = (305, 10), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_vdp2 = mkn(self.painel, id = 231, value = "0.00", pos = (305, 30), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_vdp3 = mkn(self.painel, id = 232, value = "0.00", pos = (305, 50), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_vdp4 = mkn(self.painel, id = 233, value = "0.00", pos = (305, 70), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_vdp5 = mkn(self.painel, id = 234, value = "0.00", pos = (305, 90), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pd_vdp6 = mkn(self.painel, id = 235, value = "0.00", pos = (305,110), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

		self.pd_marg = mkn(self.painel, id = 240, value = "0.00", pos = (67, 137), style = wx.ALIGN_RIGHT|0, integerWidth = 4,fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

		self.pd_pcus = wx.TextCtrl(self.painel,-1,"0.00",pos=(67,160),size=(83,15),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pd_pcus.SetBackgroundColour("#E5E5E5")
		self.pd_pcus.SetForegroundColour("#31819B")
		self.pd_pcus.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		if self.Filial !="":	self.nnFilial = self.Filial
		else:	self.nnFilial = str( self.p.rfilia.GetValue().split('-')[0] )
			 
		self.idFilia = wx.TextCtrl(self.painel,-1,str( self.nnFilial ),pos=(67,193),size=(83,15),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.idFilia.SetBackgroundColour("#E5E5E5")
		self.idFilia.SetForegroundColour("#31819B")
		self.idFilia.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pd_tpr1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pd_marg.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pd_marc = wx.CheckBox(self.painel, -1 , "Calculo { Marcação/Valor }",(173,187))
		self.pd_marc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.desconto = wx.RadioButton(self.painel,-1,"Desconto ",  pos=(173,136),style=wx.RB_GROUP)
		self.acrescim = wx.RadioButton(self.painel,-1,"Acréscimo",  pos=(173,158))

		self.desconto.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.acrescim.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.voltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(278,140), size=(36,32))
		self.gravar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(320,140), size=(36,32))
		self.voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.Bind(wx.EVT_CLOSE, self.sair)
		self.pd_marc.Bind(wx.EVT_CHECKBOX, self.marcapreco)

		self.pd_tpr1.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_tpr2.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_tpr3.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_tpr4.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_tpr5.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_tpr6.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

		self.pd_vdp1.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_vdp2.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_vdp3.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_vdp4.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_vdp5.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pd_vdp6.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

		self.pd_marg.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.desconto.Bind(wx.EVT_RADIOBUTTON, self.evTRadio)
		self.acrescim.Bind(wx.EVT_RADIOBUTTON, self.evTRadio)

		self.gravar.Bind(wx.EVT_BUTTON, self.gravacao)
		
		self.levantar()
		self.marcapreco(wx.EVT_CHECKBOX)
		
	def sair(self,event):	self.Destroy()
	def evTRadio(self,event):	nF.calcularProduto( 0, self, Filial = self.p.ppFilial, mostrar = True, retornar_valor = False )
	def levantar(self):
				
		conn = sqldb()
		sql  = conn.dbc("Produtos : Precos separados", fil = self.p.ppFilial, janela = self.painel )

		if sql[0] == True:
		
			if sql[2].execute("SELECT * FROM produtos WHERE pd_codi='"+str( self.cp )+"'") !=0:
				
				resT = sql[2].fetchall()[0]
				info = False
				
				self.lsTa = ""
				
				pv1,pv2,pv3,pv4,pv5,pv6 = str(resT[28]),str(resT[29]),str(resT[30]),str(resT[31]),str(resT[32]),str(resT[33])
				pc1,pc2,pc3,pc4,pc5,pc6 = str(resT[34]),str(resT[35]),str(resT[36]),str(resT[37]),str(resT[38]),str(resT[39])
				mar,cus,acd,Tmc = str(resT[20]),str(resT[24]),resT[70],resT[68]
				
				if resT[90] !=None and resT[90] !="":
					
					for i in resT[90].split("\n"):
						
						if i !="":
							
							if i.split("|")[0].split(";")[0] == self.nnFilial:

								info = True
								pc = i.split("|")[1].split(";") #-: Precos
								pr = i.split("|")[2].split(";") #-: Percentuais
								oT = i.split("|")[3].split(";") #-: Marcacao,Acrescimo,Desconto
								mc = i.split("|")[4].split(";") #-: Margem,Custo
								
							if i.split("|")[0].split(";")[0] != self.nnFilial:	self.lsTa += i+"\n"
						
				if info == True:

					pv1,pv2,pv3,pv4,pv5,pv6 = pc[0],pc[1],pc[2],pc[3],pc[4],pc[5]
					pc1,pc2,pc3,pc4,pc5,pc6 = pr[0],pr[1],pr[2],pr[3],pr[4],pr[5]
					Tmc,acd = oT[0],oT[1]
					mar,cus = mc[0],mc[1]

					self.msg.SetLabel("1-Produto-Alteração")
					self.msg.SetForegroundColour("#5994A7")

				else:
						
					self.msg.SetLabel("1-Produto-Inclusão")
					self.msg.SetForegroundColour("#A52A2A")
						
				self.pd_tpr1.SetValue( pv1 )
				self.pd_tpr2.SetValue( pv2 )
				self.pd_tpr3.SetValue( pv3 )
				self.pd_tpr4.SetValue( pv4 )
				self.pd_tpr5.SetValue( pv5 )
				self.pd_tpr6.SetValue( pv6 )

				self.pd_vdp1.SetValue( pc1 ) 
				self.pd_vdp2.SetValue( pc2 )
				self.pd_vdp3.SetValue( pc3 )
				self.pd_vdp4.SetValue( pc4 )
				self.pd_vdp5.SetValue( pc5 )
				self.pd_vdp6.SetValue( pc6 )
					
				self.pd_marg.SetValue( mar )
				self.pd_pcus.SetValue( cus )

				if acd == "T":	self.desconto.SetValue( True )
				else:	self.acrescim.SetValue( True )
				if Tmc == "T":	self.pd_marc.SetValue( True )

			conn.cls( sql[1] )
							
	def TlNum(self,event):

		two  = [231,232,233,234,235]

		TelNumeric.decimais = 3
		if event.GetId() in two:	TelNumeric.decimais = 2

		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		try:
			
			if valor == '':	valor = '0.000'

			if idfy == 241:	self.pd_tpr1.SetValue( valor )
			if idfy == 704:	self.pd_tpr2.SetValue( valor )
			if idfy == 705:	self.pd_tpr3.SetValue( valor )
			if idfy == 706:	self.pd_tpr4.SetValue( valor )
			if idfy == 707:	self.pd_tpr5.SetValue( valor )
			if idfy == 708:	self.pd_tpr6.SetValue( valor )

			if idfy == 231:	self.pd_vdp2.SetValue( valor )
			if idfy == 232:	self.pd_vdp3.SetValue( valor )
			if idfy == 233:	self.pd_vdp4.SetValue( valor )
			if idfy == 234:	self.pd_vdp5.SetValue( valor )
			if idfy == 235:	self.pd_vdp6.SetValue( valor )

			if idfy == 240:	self.pd_marg.SetValue( valor )
			
			nF.calcularProduto( idfy, self, Filial = self.p.ppFilial, mostrar = True, retornar_valor = False )
			
		except Exception as _reTornos:
			
			print "Produtos Precos Separados p/Filial\n"+_reTornos

	def marcapreco(self,event):

		if self.pd_marc.GetValue() == True:
			
			self.pd_tpr2.Disable()
			self.pd_tpr3.Disable()
			self.pd_tpr4.Disable()
			self.pd_tpr5.Disable()
			self.pd_tpr6.Disable()

			self.pd_vdp2.Enable()
			self.pd_vdp3.Enable()
			self.pd_vdp4.Enable()
			self.pd_vdp5.Enable()
			self.pd_vdp6.Enable()

		else:

			self.pd_tpr2.Enable()
			self.pd_tpr3.Enable()
			self.pd_tpr4.Enable()
			self.pd_tpr5.Enable()
			self.pd_tpr6.Enable()

			self.pd_vdp2.Disable()
			self.pd_vdp3.Disable()
			self.pd_vdp4.Disable()
			self.pd_vdp5.Disable()
			self.pd_vdp6.Disable()

	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()

		if keycode == wx.WXK_ESCAPE:	self.sair(wx.EVT_BUTTON)
		
		__id = 0
		if controle !=None:	__id = controle.GetId()
		nF.calcularProduto( __id, self, Filial = self.p.ppFilial, mostrar = True, retornar_valor = False )
		
	def gravacao( self, event ):

		pc1 = pc2 = pc3 = pc4 = pc5 = pc6 = "0.00"
		if self.pd_marc.GetValue() == True:

			pc1 = str( self.Trunca.trunca(1, self.pd_vdp1.GetValue() ) )
			pc2 = str( self.Trunca.trunca(1, self.pd_vdp2.GetValue() ) )
			pc3 = str( self.Trunca.trunca(1, self.pd_vdp3.GetValue() ) )
			pc4 = str( self.Trunca.trunca(1, self.pd_vdp4.GetValue() ) )
			pc5 = str( self.Trunca.trunca(1, self.pd_vdp5.GetValue() ) )
			pc6 = str( self.Trunca.trunca(1, self.pd_vdp6.GetValue() ) )
	
		pv1 = str( self.Trunca.trunca(1, self.pd_tpr1.GetValue() ) )
		pv2 = str( self.Trunca.trunca(1, self.pd_tpr2.GetValue() ) )
		pv3 = str( self.Trunca.trunca(1, self.pd_tpr3.GetValue() ) )
		pv4 = str( self.Trunca.trunca(1, self.pd_tpr4.GetValue() ) )
		pv5 = str( self.Trunca.trunca(1, self.pd_tpr5.GetValue() ) )
		pv6 = str( self.Trunca.trunca(1, self.pd_tpr6.GetValue() ) )

		prc = self.idFilia.GetValue()+"|"+str( pv1 )+";"+str( pv2 )+";"+str( pv2 )+\
		";"+str( pv4 )+";"+str( pv5 )+";"+str( pv6 )

		per = pc1+";"+pc2+";"+pc3+";"+pc4+";"+pc5+";"+pc6
		ouT = str( self.pd_marc.GetValue() )[:1]+";"+str( self.desconto.GetValue() )[:1]+";"+str( self.acrescim.GetValue() )[:1]
		mag = str( self.pd_marg.GetValue() )+";"+str( self.pd_pcus.GetValue() )

		lsTGrv = prc+"|"+per+"|"+ouT+"|"+mag
		self.lsTa +=lsTGrv

		conn = sqldb()
		sql  = conn.dbc("Produtos: Precos Separados", fil = self.p.ppFilial, janela = self.painel )
		grv  = True

		if sql[0] == True:
		
			try:
	
				aTualiza = "UPDATE produtos SET pd_pcfl='"+str( self.lsTa )+"' WHERE pd_codi='"+str( self.cp )+"'"
				aa=sql[2].execute( aTualiza )
				sql[1].commit()

			except Exception, reTornos:

				sql[1].rollback()
				grv = False
		
			conn.cls( sql[1] )

		if grv == True:
			
			alertas.dia(self,"Atualizado com sucesso!!\n"+(" "*110),"Produtos: Preços p/Filial")
			self.p.pesquisarProduto(wx.EVT_BUTTON)
			self.sair( wx.EVT_BUTTON )
			
		if grv == False:	alertas.dia(self,"Erro na atualização!!\n\n"+str( reTornos )+"\n"+(" "*140),"Produtos: Preços p/Filial")
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#217B99") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Preços Individualizador p/Filial", 0, 180, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,  1, 347, 132, 3) #-: Consulta
		dc.DrawRoundedRectangle(12,135, 347,  50, 3) #-: Consulta


class TrocaCodigosFiscais(wx.Frame):
	
	def __init__(self,parent, id):

		self.f = parent.ppFilial

		wx.Frame.__init__(self, parent, id, "Ajustes: { Substituição de códigos fiscais }", size=( 450,363 ), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self, style=wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1, u"Condição/Compara NCM:",  pos=(18,10)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Condição/Compara CFOP:", pos=(18,35)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Condição/Compara CST:",  pos=(18,60)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Condição/Compara ICMS:", pos=(18,85)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u">->Substituir p/NCM:",  pos=(235,10)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u">->Substituir p/CFOP:", pos=(235,35)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u">->Substituir p/CST:",  pos=(235,60)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u">->Substituir p/ICMS:", pos=(235,85)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Selecione uma filial",  pos=(17,318)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		inf = wx.StaticText(self.painel,-1, u"- Não use ponto ou virgula para separar casas decimais para icms\n-Campos vazio não serão considerados\n\n{ Exemplo de uso }"+\
		u"\n     Todo NCM 12345678, Alterar CFOP p/5401,CST 0010, ICSM 10.00\n     nesse caso os CFOP,CST,ICMS de comparação não precisa ser preenchido\n"+\
		u"      CFOP,CST,ICMS so precisa ser preenchidos se for fazer comparação p/substituição\n\n- Os códigos NCM,CFOP,CST,ICMS separadamente so serão substituidos"+\
		u" se houver\n  referência de substituição se não permance o que estar no cadastro", pos=(18,190))
		
		inf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		inf.SetForegroundColour("#7F7F7F")

#---------: Codigos Fiscais
		self.mncm = wx.TextCtrl(self.painel, 501, '', pos=(145, 5), size=(90, 20) )
		self.mcfo = wx.TextCtrl(self.painel, 502, '', pos=(145,30), size=(90, 20) )
		self.mcst = wx.TextCtrl(self.painel, 503, '', pos=(145,55), size=(90, 20) )
		self.micm = wx.TextCtrl(self.painel, 504, '', pos=(145,80), size=(90, 20) )
		self.ancm = wx.TextCtrl(self.painel, 601, '', pos=(340, 5), size=(100,20) )
		self.acfo = wx.TextCtrl(self.painel, 602, '', pos=(340,30), size=(100,20) )
		self.acst = wx.TextCtrl(self.painel, 603, '', pos=(340,55), size=(100,20) )
		self.aicm = wx.TextCtrl(self.painel, 604, '', pos=(340,80), size=(100,20) )

		self.mncm.SetMaxLength(8)
		self.mcfo.SetMaxLength(4)
		self.mcst.SetMaxLength(4)
		self.micm.SetMaxLength(4)
		self.ancm.SetMaxLength(8)
		self.acfo.SetMaxLength(4)
		self.acst.SetMaxLength(4)
		self.aicm.SetMaxLength(4)

		self.primario = wx.RadioButton(self.painel,100,"Substituição dos códigos fiscais primario",   pos=(13,100),style=wx.RB_GROUP)
		self.rgnormal = wx.RadioButton(self.painel,101,"Substituição dos códigos fiscais do regime normal", pos=(13,120))
		self.emisnfce = wx.RadioButton(self.painel,102,"Substituição dos códigos fiscais de nfce", pos=(13,140))

		self.acionarg = wx.CheckBox(self.painel, -1,  "Gravação { Mantenha desmarcado p/teste }", pos=(13,160))

		self.primario.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.rgnormal.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.emisnfce.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.acionarg.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		voltar = wx.BitmapButton(self.painel, 301, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(365, 120), size=(36,34))				
		gravar = wx.BitmapButton(self.painel, 305, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(403, 120), size=(36,34))				

		voltar.SetBackgroundColour('#E8E8B6')
		gravar.SetBackgroundColour('#6F9A6F')

		self.filial_finalizacao = wx.ComboBox(self.painel, -1, '', pos=(13, 330), size=(256,27), choices = login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.filial_finalizacao.SetValue( self.f + '-' + login.filialLT[ self.f ][14] )

		self.todas_filias = wx.CheckBox(self.painel, -1, "Marque opção para alterar\nem todas filiais", pos=(287, 324))
		self.todas_filias.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		gravar.Bind(wx.EVT_BUTTON, self.gravarCodigos)
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.Bind(wx.EVT_CLOSE, self.sair)
	
	def sair(self,event):	self.Destroy()	
	def gravarCodigos(self,event):
		
		icms_compara = self.micm.GetValue().strip().replace(",",'').replace('.','')
		icms_alterar = self.aicm.GetValue().strip().replace(",",'').replace('.','')

		c_ncm = self.mncm.GetValue().strip()
		a_ncm = self.ancm.GetValue().strip()

		c_cfo = self.mcfo.GetValue().strip()
		a_cfo = self.acfo.GetValue().strip()

		c_cst = self.mcst.GetValue().strip()
		a_cst = self.acst.GetValue().strip()

		c_icm = self.micm.GetValue().strip()
		a_icm = self.aicm.GetValue().strip()

		altera = []
		nocorr = 0
		altera.append('T') if c_ncm and a_ncm else altera.append('F') if not c_ncm and not a_ncm else altera.append('S') if not a_ncm else altera.append('A')
		altera.append('T') if c_cfo and a_cfo else altera.append('F') if not c_cfo and not a_cfo else altera.append('S') if not a_cfo else altera.append('A')
		altera.append('T') if c_cst and a_cst else altera.append('F') if not c_cst and not a_cst else altera.append('S') if not a_cst else altera.append('A')
		altera.append('T') if c_icm and a_icm else altera.append('F') if not c_icm and not a_icm else altera.append('S') if not a_icm else altera.append('A')
		
		if c_ncm:	nocorr +=1
		if c_cfo:	nocorr +=1
		if c_cst:	nocorr +=1
		if c_icm:	nocorr +=1

		
		continuar = True if 'T' in altera or 'S' in altera else False
		if not a_ncm and not a_cfo and not a_cst and not a_icm:	continuar = False
		
		if not continuar:
			
			alertas.dia( self, "Nenhuma ocorrência para comparação c/substituição...\n"+(" "*100),"Alteração-Substituição de códigos fiscais")
			return

	
		__rt = True
		__ms = ''
		
		if __rt and icms_compara:	__rt, __ms = self.validaCodigos( icms_compara, "ICMS","C",4)
		if __rt and icms_alterar:	__rt, __ms = self.validaCodigos( icms_alterar, "ICMS","S",4)
		
		if __rt and c_ncm:	__rt, __ms = self.validaCodigos( c_ncm, "NCM", "C",8)
		if __rt and a_ncm:	__rt, __ms = self.validaCodigos( a_ncm, "NCM", "S",8)
		if __rt and c_cfo:	__rt, __ms = self.validaCodigos( c_cfo, "CFOP","C",4)
		if __rt and a_cfo:	__rt, __ms = self.validaCodigos( a_cfo, "CFOP","S",4)
		if __rt and c_cst:	__rt, __ms = self.validaCodigos( c_cst, "CST", "C",4)
		if __rt and a_cst:	__rt, __ms = self.validaCodigos( a_cst, "CST", "S",4)
		
		if not __rt:

			alertas.dia( self, __ms,"Alteração-Substituição de códigos fiscais")
			return


		recalcular = wx.MessageDialog(self,"{ Substituição de códigos fiscais } \n\nConfirme para continuar\n"+(" "*100),"Produtos",wx.YES_NO|wx.NO_DEFAULT)
		if recalcular.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Produtos: Relacionando Grupos,Fabricantes", fil = self.f, janela = self )
			muda = 0
			atua = ""
			ggva = True
			
			codigos_alterados = ""
			
			if sql[0]:
				
				try:
				
					for i in [] if not sql[2].execute("SELECT * FROM produtos ORDER BY pd_cfis") else sql[2].fetchall():
						
						nregistro = i[0]
												
						if self.primario.GetValue():	cfis = i[47].split('.')
						if self.rgnormal.GetValue():	cfis = i[82].split('.')
						if self.emisnfce.GetValue():	cfis = i[53].split('.')
						
						ncm1 = ncm2 = ncm3 = ""
						cfo1 = cfo2 = cfo3 = ""
						cst1 = cst2 = cst3 = ""
						icm1 = icm2 = icm3 = ""

						if len( cfis ) >= 1:	ncm1 = cfis[0]
						if len( cfis ) >= 2:	cfo1 = cfis[1]
						if len( cfis ) >= 3:	cst1 = cfis[2]
						if len( cfis ) >= 4:	icm1 = cfis[3]

						__ncm = a_ncm if altera[0] in ['T','A'] else ncm1
						__cfo = a_cfo if altera[1] in ['T','A'] else cfo1
						__cst = a_cst if altera[2] in ['T','A'] else cst1
						__icm = a_icm if altera[3] in ['T','A'] else icm1
						
						codigo_fiscal = __ncm+'.'+__cfo+'.'+__cst+'.'+__icm
						
						compara  = True
						compara1 = False
						compara2 = False
						compara3 = False
						compara4 = False
						nc = cf = cs = ic = ""
						
						if altera[0] in ['T','S']:	compara1, nc = True, cfis[0] if len( cfis ) >=1 else ""
						if altera[1] in ['T','S']:	compara2, cf = True, cfis[1] if len( cfis ) >=2 else ""
						if altera[2] in ['T','S']:	compara3, cs = True, cfis[2] if len( cfis ) >=3 else ""
						if altera[3] in ['T','S']:	compara4, ic = True, cfis[3] if len( cfis ) >=4 else ""


						condicoes = []
						if compara1:	condicoes.append(True) if nc and c_ncm == nc else condicoes.append(False)
						if compara2:	condicoes.append(True) if cf and c_cfo == cf else condicoes.append(False)
						if compara3:	condicoes.append(True) if cs and c_cst == cs else condicoes.append(False)
						if compara4:	condicoes.append(True) if ic and c_icm == ic else condicoes.append(False)
							
						for nco in range( nocorr ):
							
							if len( condicoes ) == nocorr and not condicoes[ nco ]:

								compara = False
								break
						
						if len( condicoes ) != nocorr:	compara = False

						if not self.todas_filias.GetValue() and compara:

							__filial = self.filial_finalizacao.GetValue().split('-')[0]
							if not sql[2].execute("SELECT ef_fisico FROM estoque WHERE ef_idfili='"+ __filial +"' and ef_codigo='"+ i[2] +"'"):	compara = False

						if compara:
						
							grva1 = "UPDATE produtos SET pd_cfis='"+str( codigo_fiscal )+"' WHERE pd_regi='"+str( nregistro )+"'"
							grva2 = "UPDATE produtos SET pd_cfsc='"+str( codigo_fiscal )+"' WHERE pd_regi='"+str( nregistro )+"'"
							grva3 = "UPDATE produtos SET pd_cfir='"+str( codigo_fiscal )+"' WHERE pd_regi='"+str( nregistro )+"'"
							atua +="AN|"+str( i[1] )+"|"+str( i[2] )+"|"+str( i[3] )+"|"+str( i[47] )+"|"+str( i[82] )+"|"+str( i[53] )+"|"+str( i[8] )+"|"+str( i[61] )+"|"+str( i[62] )+"\n"

							if self.acionarg.GetValue():
								
								if self.primario.GetValue():	sql[2].execute( grva1 )
								if self.rgnormal.GetValue():	sql[2].execute( grva2 )
								if self.emisnfce.GetValue():	sql[2].execute( grva3 )
														
							codigos_alterados += "Sequencia: "+str( muda + 1 ).zfill(4)+"  Anterior: "+ncm1+'.'+cfo1+'.'+cst1+'.'+icm1+"  Substituido: "+codigo_fiscal+"  Produto: "+ i[2] +" - "+ i[3].decode("UTF-8") +"\n"
							
							muda +=1

					if muda:	sql[1].commit()
				
				except Exception as erro:
					sql[1].rollback()
					ggva = False
					
				conn.cls( sql[1] )

				
				if muda and atua and ggva:
					
					if self.acionarg.GetValue():	
						
						dTa = datetime.datetime.now().strftime("%d%m%Y_%H%M")+'_'+login.usalogin
						_nomeArq = "/home/"+diretorios.usPrinci+"/direto/codigofiscal/SUB_"+dTa.lower()+".csv"

						__arquivo = open(_nomeArq,"w")
						__arquivo.write( atua )
						__arquivo.close()

						alertas.dia(self,u"{ Alterção de Códigos Fiscais, [ OK ]\n\nArquivo de Backup\n"+str( _nomeArq )+"\n"+(" "*150),u"Produtos: Alteração de Códigos Fiscais")

					if not self.acionarg.GetValue():	codigos_alterados = "{ TESTE,TESTE,TESTE,TESTE,TESTE,TESTE }\n\n"+codigos_alterados
					else:	codigos_alterados = u"{ Finalizando com alteraçẽos dos codigos fiscais Nº Alterações: "+str( muda )+" }\n\n"+codigos_alterados

					MostrarHistorico.hs = codigos_alterados
					MostrarHistorico.TP = ""
					MostrarHistorico.TT = u"Subsituição de códigos fiscais"
					MostrarHistorico.AQ = ""
					MostrarHistorico.FL = self.f

					his_frame=MostrarHistorico(parent=self,id=-1)
					his_frame.Centre()
					his_frame.Show()

				elif not ggva:	alertas.dia(self,u"Erro, na substituição de códigos fiscais!!\n\n"+str( erro )+"\n"+(" "*150),u"Produtos: Alteração de Códigos Fiscais")
				elif not muda:	alertas.dia(self,u"Sem ocorrências, para condição colocada!!\n"+(" "*100),u"Produtos: Alteração de Códigos Fiscais")
		
	def validaCodigos(self, codigo, modulo, compara, caracters ):

		retorno, menssagem = True, ""
		if codigo and not codigo.isdigit() and compara == "C":	retorno, menssagem = False, modulo+u" de comparação: Aceita apenas digitos...\n"+(" "*100)
		if codigo and not codigo.isdigit() and compara == "S":	retorno, menssagem = False, modulo+u" de substituição: Aceita apenas digitos...\n"+(" "*100)
	
		if len( codigo ) != caracters:	retorno ,menssagem = False, modulo+" Quantidade de digitos incompativel...\n"+(" "*100)

		return retorno, menssagem

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#317EC9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Substituição NCM, CFOP, CST, ICMS", 0, 238, 90)
		dc.DrawRotatedText("Filial", 0, 358, 90)


class DescricaoTabelas(wx.Frame):
	
	def __init__(self,parent, id):

		self.f = parent.ppFilial

		wx.Frame.__init__(self, parent, id, "Descrição das Tabelas {"+str( self.f )+"}", size=(480,202 ), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sairgravar)
		
		wx.StaticText(self.painel,-1,"Descrição de preços",pos=(15,4)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Descrição de preços p/Cortes",pos=(276,4)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Tabela-1:",pos=(15,  24)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Tabela-2:",pos=(15, 54)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Tabela-3:",pos=(15, 84)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Tabela-4:",pos=(15,114)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Tabela-5:",pos=(15,144)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Tabela-6:",pos=(15,174)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		
		self.tab1 = wx.TextCtrl( self.painel,-1,'',pos=(60, 20), size=(200,20))
		self.tab2 = wx.TextCtrl( self.painel,-1,'',pos=(60, 50), size=(200,20))
		self.tab3 = wx.TextCtrl( self.painel,-1,'',pos=(60, 80), size=(200,20))
		self.tab4 = wx.TextCtrl( self.painel,-1,'',pos=(60,110), size=(200,20))
		self.tab5 = wx.TextCtrl( self.painel,-1,'',pos=(60,140), size=(200,20))
		self.tab6 = wx.TextCtrl( self.painel,-1,'',pos=(60,170), size=(200,20))

		self.tcb1 = wx.TextCtrl( self.painel,-1,'',pos=(275, 20), size=(200,20))
		self.tcb2 = wx.TextCtrl( self.painel,-1,'',pos=(275, 50), size=(200,20))
		self.tcb3 = wx.TextCtrl( self.painel,-1,'',pos=(275, 80), size=(200,20))
		self.tcb4 = wx.TextCtrl( self.painel,-1,'',pos=(275,110), size=(200,20))
		self.tcb5 = wx.TextCtrl( self.painel,-1,'',pos=(275,140), size=(200,20))
		self.tcb6 = wx.TextCtrl( self.painel,-1,'',pos=(275,170), size=(200,20))

		self.tab1.SetBackgroundColour("#E5E5E5")
		self.tab2.SetBackgroundColour("#E5E5E5")
		self.tab3.SetBackgroundColour("#E5E5E5")
		self.tab4.SetBackgroundColour("#E5E5E5")
		self.tab5.SetBackgroundColour("#E5E5E5")
		self.tab6.SetBackgroundColour("#E5E5E5")

		self.tcb1.SetBackgroundColour("#E5E5E5")
		self.tcb2.SetBackgroundColour("#E5E5E5")
		self.tcb3.SetBackgroundColour("#E5E5E5")
		self.tcb4.SetBackgroundColour("#E5E5E5")
		self.tcb5.SetBackgroundColour("#E5E5E5")
		self.tcb6.SetBackgroundColour("#E5E5E5")

		self.tab1.SetMaxLength(20)
		self.tab2.SetMaxLength(20)
		self.tab3.SetMaxLength(20)
		self.tab4.SetMaxLength(20)
		self.tab5.SetMaxLength(20)
		self.tab6.SetMaxLength(20)

		self.tcb1.SetMaxLength(20)
		self.tcb2.SetMaxLength(20)
		self.tcb3.SetMaxLength(20)
		self.tcb4.SetMaxLength(20)
		self.tcb5.SetMaxLength(20)
		self.tcb6.SetMaxLength(20)

		self.levantaTabela()
		
	def levantaTabela(self):
		
		conn = sqldb()
		sql  = conn.dbc("Produtos: Descriçao da tabela de preços", fil = self.f, janela = self )
					
		if sql[0] == True:
		
			if sql[2].execute("SELECT ep_prdo FROM cia WHERE ep_inde='"+self.f+"'"):
				
				_s =sql[2].fetchone()[0]
				if _s:

					self.tab1.SetValue( _s.split("|")[0].split(";")[0] )
					self.tab2.SetValue( _s.split("|")[0].split(";")[1] )
					self.tab3.SetValue( _s.split("|")[0].split(";")[2] )
					self.tab4.SetValue( _s.split("|")[0].split(";")[3] )
					self.tab5.SetValue( _s.split("|")[0].split(";")[4] )
					self.tab6.SetValue( _s.split("|")[0].split(";")[5] )
					
					self.tcb1.SetValue( _s.split("|")[1].split(";")[0] )
					self.tcb2.SetValue( _s.split("|")[1].split(";")[1] )
					self.tcb3.SetValue( _s.split("|")[1].split(";")[2] )
					self.tcb4.SetValue( _s.split("|")[1].split(";")[3] )
					self.tcb5.SetValue( _s.split("|")[1].split(";")[4] )
					self.tcb6.SetValue( _s.split("|")[1].split(";")[5] )
			
			conn.cls(sql[1])		
		
	def sairgravar(self,event):
		
		receb = wx.MessageDialog(self,"Confirme para atualizar os dados\n"+(" "*100),"Tabelas de preços",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() ==  wx.ID_YES:

			_t =str( self.tab1.GetValue().replace("-","_").replace(" ","_") )+';'+str( self.tab2.GetValue().replace("-","_").replace(" ","_") )+";"+\
                str( self.tab3.GetValue().replace("-","_").replace(" ","_") )+";"+str( self.tab4.GetValue().replace("-","_").replace(" ","_") )+";"+\
                str( self.tab5.GetValue().replace("-","_").replace(" ","_") )+";"+str( self.tab6.GetValue().replace("-","_").replace(" ","_") )

			_c = str( self.tcb1.GetValue().replace("-","_").replace(" ","_") )+";"+str( self.tcb2.GetValue().replace("-","_").replace(" ","_") )+";"+\
			     str( self.tcb3.GetValue().replace("-","_").replace(" ","_") )+";"+str( self.tcb4.GetValue().replace("-","_").replace(" ","_") )+";"+\
			     str( self.tcb5.GetValue().replace("-","_").replace(" ","_") )+";"+str( self.tcb6.GetValue().replace("-","_").replace(" ","_") )

			_g = _t + '|' + _c

			conn = sqldb()
			sql  = conn.dbc("Produtos: Descriçao da tabela de preços", fil = self.f, janela = self )
						
			if sql[0] == True:

				_gv = sql[2].execute("UPDATE cia SET ep_prdo='"+ _g +"' WHERE ep_inde='"+ self.f +"'")
				sql[1].commit()
				
				conn.cls( sql[1] )

		self.Destroy()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#28738C") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Tabelas de preços { Descricção }", 0,  198, 90)
		dc.SetTextForeground("#7F7F7F") 	
		dc.DrawRotatedText("Tabelas de cortes { Descricção }", 263,198, 90)


class ArquivosBackup(wx.Frame):
	
	tipo_backup = 0
	
	def __init__(self,parent, id):

		self.f = parent.ppFilial
		self.p = parent

		wx.Frame.__init__(self, parent, id, "Descrição das Tabelas {"+str( self.f )+"}", size=(680,330 ), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.list_arquivos = ListCtrlArquivos(self.painel,300,pos=(40,1),size=(640,274),
						style=wx.LC_REPORT
						|wx.BORDER_SUNKEN
						|wx.LC_VIRTUAL
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)
		self.list_arquivos.SetBackgroundColour('#80A7CA')
		self.list_arquivos.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if self.tipo_backup == 616:	self.SetTitle(u"Produtos: Recuperação de codigos ficais p/grupo,sub-grupos")
		if self.tipo_backup == 619:	self.SetTitle(u"Produtos: Substituiçao codigos fiscais {NCM,CFO,CST,ICM}")
		if self.tipo_backup == 624:	self.SetTitle(u"Produtos: Recuperação de preços")
		if self.tipo_backup ==5000:	self.SetTitle(u"Produtos: Estoque fisico diario")
		
		self.list_arquivos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.processarArquivo)
			
		wx.StaticText(self.painel,-1,u"{ Opções para ralacionar arquivos }", pos=(41, 282)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Lista de usuarios", pos=(333, 288)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Dia:", pos=(41, 305)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Més:", pos=(130,305)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Ano:", pos=(230,305)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.numero_dia = wx.TextCtrl(self.painel,-1,"", pos=(63,300), size=(50,20), style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER)
		self.numero_dia.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_dia.SetBackgroundColour('#E5E5E5')

		self.numero_mes = wx.TextCtrl(self.painel,-1,"", pos=(160,300), size=(50,20), style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER)
		self.numero_mes.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_mes.SetBackgroundColour('#E5E5E5')

		self.numero_ano = wx.TextCtrl(self.painel,-1,"", pos=(260,300), size=(50,20), style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER)
		self.numero_ano.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_ano.SetBackgroundColour('#E5E5E5')

		self.usuario = wx.ComboBox(self.painel, 605, '',  pos=(331,300), size=(220,27), choices = login.caixals, style=wx.NO_BORDER)

		procurar = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(593, 292), size=(36,35))				
		voltar   = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/voltap.png",   wx.BITMAP_TYPE_ANY), pos=(643, 292), size=(36,35))				

		_dia, _mes, _ano = datetime.datetime.now().strftime("%d/%m/%Y").split('/')
		self.numero_mes.SetValue( _mes )
		self.numero_ano.SetValue( _ano )

		self.numero_dia.SetMaxLength(2)
		self.numero_mes.SetMaxLength(2)
		self.numero_ano.SetMaxLength(4)
	
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		procurar.Bind(wx.EVT_BUTTON, self.levantarArquivos)
		self.usuario.Bind(wx.EVT_COMBOBOX, self.levantarArquivos)
		self.usuario.Bind(wx.EVT_TEXT_ENTER, self.levantarArquivos)

		self.numero_dia.Bind(wx.EVT_TEXT_ENTER, self.levantarArquivos)
		self.numero_mes.Bind(wx.EVT_TEXT_ENTER, self.levantarArquivos)
		self.numero_ano.Bind(wx.EVT_TEXT_ENTER, self.levantarArquivos)

		self.levantarArquivos(wx.EVT_BUTTON)
		
	def sair(self,event):	self.Destroy()
	def processarArquivo(self,event):
		
		self.p.a = self.list_arquivos.GetItem( self.list_arquivos.GetFocusedItem(), 4 ).GetText() 
		if   self.tipo_backup == 624:	self.p.restauraProdutos()
		elif self.tipo_backup in [616,619]:
		
			RecuperaCodigoFiscal.arquivo = self.list_arquivos.GetItem( self.list_arquivos.GetFocusedItem(), 4 ).GetText() 
			rcf_frame=RecuperaCodigoFiscal(parent=self,id=-1)
			rcf_frame.Centre()
			rcf_frame.Show()
		
		else:	self.p.abrirDanfe( self.tipo_backup )	
		
	def levantarArquivos(self,event):

		lista_arquivos = []
		pesquisar = "*"
		relacao = {}
		_registros = 0
		
		if self.numero_dia.GetValue().strip():	pesquisar +=self.numero_dia.GetValue().strip().zfill(2)
		if self.numero_mes.GetValue().strip():	pesquisar +=self.numero_mes.GetValue().strip().zfill(2)
		if self.numero_ano.GetValue().strip():	pesquisar +=self.numero_ano.GetValue().strip()
		if len( pesquisar ) > 1:	pesquisar +="*"
		
		for lista_usuarios in glob.glob("/home/*"):
			
			if self.tipo_backup == 616:	lista_arquivos += glob.glob( lista_usuarios + '/direto/codigofiscal/ACF_'+ pesquisar +'.csv' )
			if self.tipo_backup == 619:	lista_arquivos += glob.glob( lista_usuarios + '/direto/codigofiscal/SUB_'+ pesquisar +'.csv' )
			if self.tipo_backup == 624:	lista_arquivos += glob.glob( lista_usuarios + '/direto/precos/'+ pesquisar +'.sql' )
			if self.tipo_backup== 5000:
				
				for _f in glob.glob( lista_usuarios + '/direto/fisico/*' ):
				 
					lista_arquivos += glob.glob( _f + '/'+ pesquisar +'.xls')

				lista_arquivos = sorted( lista_arquivos, key = lambda file: os.path.getctime(file))
		
		for arquivos in lista_arquivos:

			passar = True
	
			_us  = self.usuario.GetValue().strip().split('-')
			__us = ""
			if _us[0]:	__us = _us[1] if len( _us ) == 2 else self.usuario.GetValue().strip()
			if __us and arquivos.split("/")[2].upper() != __us.upper(): passar = False
			data_arquivo = "{}||{}".format(arquivos, time.ctime(os.path.getctime(arquivos))).split("||")[1]
			
			if passar:
				
				if self.tipo_backup in [616,619,624]: # == 624 or self.tipo_backup == 616:	

					_lst = arquivos.split("/")
					_tpo = _lst[5].split('.')[1]
					relacao[_registros] = _tpo, _lst[2], _lst[5], data_arquivo, arquivos
					_registros +=1
				
				elif self.tipo_backup == 5000:

					_lst = arquivos.split("/")

					_tpo = _lst[6].split('.')[1]
					relacao[_registros] = _tpo, _lst[2], _lst[6], data_arquivo, arquivos
					_registros +=1

		self.list_arquivos.SetItemCount( _registros )
		ListCtrlArquivos.itemDataMap  = relacao
		ListCtrlArquivos.itemIndexMap = relacao.keys()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#28738C") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Recuperação dos arquivos de backup", 5,  323, 90)

		dc.SetTextForeground("#235262") 	
		if ArquivosBackup.tipo_backup == 616:	dc.DrawRotatedText("CSV da alteração do codigo fiscai p/grupo,sub-grupos", 22,  323, 90)
		if ArquivosBackup.tipo_backup == 619:	dc.DrawRotatedText("CSV substituição de codigos fiscais NCM,CFOP,CST", 22,  323, 90)
		if ArquivosBackup.tipo_backup == 624:	dc.DrawRotatedText("SQL da alteração de preços", 22,  323, 90)
		if ArquivosBackup.tipo_backup == 5000:	dc.DrawRotatedText("XLS Planilha do estoque fisico { dia anterior a emissão }", 22,  323, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(3,  1, 34,  325,  3)	#	dc.SetTextForeground("#7F7F7F") 	

class ListCtrlArquivos(wx.ListCtrl):

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
		self.attr6 = wx.ListItemAttr()
		self.attr7 = wx.ListItemAttr()

		self.attr1.SetBackgroundColour("#5380A7")
		self.attr2.SetBackgroundColour("#EEFFEE")
		self.attr3.SetBackgroundColour("#FFBEBE")
		self.attr4.SetBackgroundColour("#F6F6AE")
		self.attr5.SetBackgroundColour("#EB9494")
		self.attr6.SetBackgroundColour("#B07C7C")
		self.attr7.SetBackgroundColour("#DAE6DA")

		self.InsertColumn(0, 'Tipo', width=70)
		self.InsertColumn(1, 'Usuario', width=90)
		self.InsertColumn(2, 'Nome do arquivo', width=300)
		self.InsertColumn(3, 'Data do arquivo', width=200)
		self.InsertColumn(4, 'Endereço do arquivo', width=1000)
					
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
		if item % 2:	return self.attr1
		
	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][0] == "sql":	return self.sql
		if self.itemDataMap[index][0] == "xls":	return self.xls
		if self.itemDataMap[index][0] == "csv":	return self.csv
		return self.i_idx

	def GetListCtrl(self):	return self


class GerenciadorGrupos(wx.Frame):

	lisTar = []
	TTFisc = 0
	produT = ''
	
	def __init__(self, parent,id):

		self.p = parent
		
		wx.Frame.__init__(self, parent, 209, 'Produtos: Gerenciador de grupos-fabricantes ', size=(530,440), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.gruposub = wx.ListCtrl(self.painel, 209,pos=(15,1), size=(514,315),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.gruposub.SetBackgroundColour('#8AA3BB')
		self.gruposub.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.gruposub.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
	
		self.gruposub.InsertColumn(0,  u'ID-Registro', format=wx.LIST_ALIGN_LEFT, width=100)
		self.gruposub.InsertColumn(1,  u'Tipo',  format=wx.LIST_ALIGN_TOP,width=40)
		self.gruposub.InsertColumn(2,  u'Descrição grupo,sub-grupo,fabricante e endereços', width=400)

		self.ocorrencias = wx.StaticText(self.painel,-1, "Ocorrências:{ }", pos=(130,320)  )
		self.ocorrencias.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ocorrencias.SetForegroundColour('#2269AD')

		wx.StaticText(self.painel,-1, "Dados p/apagar", pos=(130,340) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Inclusão e substituição", pos=(130,382) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Incluir { Anterior }", pos=(130,397) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Substituir { Atual }", pos=(260,397) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, "Tipo: G-Grupo 1-Sub-grupo 1\n2 Sub-grupo 2 F-Fabricante\nE-Endereço", pos=(240,317) ).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.grupos = wx.RadioButton(self.painel,-1,"Grupo",       pos=(13,320),style=wx.RB_GROUP)
		self.grupo1 = wx.RadioButton(self.painel,-1,"Sub-grupo_1", pos=(13,343))
		self.grupo2 = wx.RadioButton(self.painel,-1,"Sub-grupo_2", pos=(13,366))
		self.fabric = wx.RadioButton(self.painel,-1,"Fabricante",  pos=(13,389))
		self.endere = wx.RadioButton(self.painel,-1,"Endereço",    pos=(13,412))
		
		self.grupos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.grupo1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.grupo2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fabric.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.endere.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dapagar = wx.TextCtrl(self.painel,350,'',pos=(127,353),size=(250,22),style=wx.TE_PROCESS_ENTER)
		self.dapagar.SetBackgroundColour("#E5E5E5")
		self.dapagar.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.danterior = wx.TextCtrl(self.painel,351,'',pos=(127,410),size=(120,22))
		self.danterior.SetBackgroundColour("#E5E5E5")
		self.danterior.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.datual = wx.TextCtrl(self.painel,352,'',pos=(257,410),size=(120,22))
		self.datual.SetBackgroundColour("#E5E5E5")
		self.datual.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.forcar = wx.CheckBox(self.painel, 328 , u"Ignore a lista de produtos\npara apagar",  pos=(385,313))
		self.forcar.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		procura = wx.BitmapButton(self.painel, 250, wx.Bitmap("imagens/procurap.png",  wx.BITMAP_TYPE_ANY), pos=(385, 343), size=(40,32))				
		apagar  = wx.BitmapButton(self.painel, 251, wx.Bitmap("imagens/apagar.png",  wx.BITMAP_TYPE_ANY), pos=(435, 343), size=(40,32))				
		incluir = wx.BitmapButton(self.painel, 252, wx.Bitmap("imagens/adiciona24.png",  wx.BITMAP_TYPE_ANY), pos=(385, 401), size=(40,32))				
		substituir = wx.BitmapButton(self.painel, 253, wx.Bitmap("imagens/previewp.png",  wx.BITMAP_TYPE_ANY), pos=(435, 401), size=(40,32))				
		voltar = wx.BitmapButton(self.painel, 254, wx.Bitmap("imagens/voltap.png",  wx.BITMAP_TYPE_ANY), pos=(487, 401), size=(40,32))				

		procura.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		apagar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		incluir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		substituir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.dapagar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.danterior.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.datual.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		procura.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		apagar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		incluir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		substituir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.dapagar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.danterior.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.datual.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.grupos.Bind(wx.EVT_RADIOBUTTON, self.levantarGrupos)
		self.grupo1.Bind(wx.EVT_RADIOBUTTON, self.levantarGrupos)
		self.grupo2.Bind(wx.EVT_RADIOBUTTON, self.levantarGrupos)
		self.fabric.Bind(wx.EVT_RADIOBUTTON, self.levantarGrupos)
		self.endere.Bind(wx.EVT_RADIOBUTTON, self.levantarGrupos)
		
		procura.Bind(wx.EVT_BUTTON, self.levantarGrupos)
		self.dapagar.Bind(wx.EVT_TEXT_ENTER, self.levantarGrupos)
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		apagar.Bind(wx.EVT_BUTTON, self.apagarTitulos)
		incluir.Bind(wx.EVT_BUTTON, self.incluirTitulo)
		substituir.Bind(wx.EVT_BUTTON, self.substituirTitulos )
		
		self.levantarGrupos(wx.EVT_BUTTON)
		
	def sair(self,event):	self.Destroy()
	def substituirTitulos(self,event):

		tipo = self.tipoGrupo()
		tian = self.danterior.GetValue().upper()
		tiat = self.datual.GetValue().upper()
		subs = u"{ Substituição de titulos }\n\nTipo: "+tipo[1]+"\nSubstituir: "+ tian +"\n"+(" "*12)+"por: "+ tiat +"\n\nConfirme para continuar...\n"

		grupos = wx.MessageDialog(self.painel,subs+(" "*130),u"Produtos: Gerenciador",wx.YES_NO|wx.NO_DEFAULT)
		if grupos.ShowModal() ==  wx.ID_YES:			
	
			conn = sqldb()
			sql  = conn.dbc("Produtos: Grupos,sub-grupos e fabricantes", fil = self.p.ppFilial, janela = self )
		
			acg = True
			aca = True
			grv = False
			err = False
				
			if sql[0]:

				if not sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_cdpd='"+ tipo[0] +"' and fg_desc='"+ tiat +"'"):	acg = False
				if acg:
					
					if tipo[0] == "G":	_ng = "SELECT pd_codi,pd_nome,pd_nmgr FROM produtos WHERE pd_nmgr='"+ tian +"' ORDER BY pd_nome"
					if tipo[0] == "1":	_ng = "SELECT pd_codi,pd_nome,pd_sug1 FROM produtos WHERE pd_sug1='"+ tian +"' ORDER BY pd_nome"
					if tipo[0] == "2":	_ng = "SELECT pd_codi,pd_nome,pd_sug2 FROM produtos WHERE pd_sug2='"+ tian +"' ORDER BY pd_nome"
					if tipo[0] == "F":	_ng = "SELECT pd_codi,pd_nome,pd_fabr FROM produtos WHERE pd_fabr='"+ tian +"' ORDER BY pd_nome"
					if tipo[0] == "E":	_ng = "SELECT pd_codi,pd_nome,pd_ende FROM produtos WHERE pd_ende='"+ tian +"' ORDER BY pd_nome"

					__ng = sql[2].execute( _ng )
					___ng = sql[2].fetchall()

					if not __ng:	grv == False
					if __ng:
						
						try:
							
							if tipo[0] == "G":	_gr = "UPDATE produtos SET pd_nmgr='"+ tiat +"' WHERE pd_nmgr='"+ tian +"'"
							if tipo[0] == "1":	_gr = "UPDATE produtos SET pd_sug1='"+ tiat +"' WHERE pd_sug1='"+ tian +"'"
							if tipo[0] == "2":	_gr = "UPDATE produtos SET pd_sug2='"+ tiat +"' WHERE pd_sug2='"+ tian +"'"
							if tipo[0] == "F":	_gr = "UPDATE produtos SET pd_fabr='"+ tiat +"' WHERE pd_fabr='"+ tian +"'"
							if tipo[0] == "E":	_gr = "UPDATE produtos SET pd_ende='"+ tiat +"' WHERE pd_ende='"+ tian +"'"

							sql[2].execute( _gr )
							sql[1].commit()
							grv = True

						except Exception as erro:
							sql[1].rollback()
							err = True
				
				conn.cls( sql[1] )

				if   not acg:	alertas.dia( self, u"Titulo atual não localizado no cadastro de grupos, sub-grupos, fabricantes, endereços...\n"+(" "*190),"Produtos: Gerenciador")
				elif not grv:	alertas.dia( self, u"Titulo anterior não localizado no cadastro de produtos...\n"+(" "*140),"Produtos: Gerenciador")
				
				if err:
					
					if type( erro ) != unicode:	erro = str( erro )
					alertas.dia( self, u"Erro na gravação da substituição...\n\n"+ erro +"\n"+(" "*140),"Produtos: Gerenciador")  
				
				if grv:

					lista_produtos = str( __ng )+" Registro(s) no cadastro de produtos com o titulo para substituir\nAnterior: "+tian+"\nAtual: "+tiat+"\n\n"
					for i in ___ng:
						
						lista_produtos += "Tipo: "+tipo[0]+" "+i[0]+" "+i[2].decode('UTF-8')+" "+i[1].decode('UTF-8')+'\n'

					dTa = datetime.datetime.now().strftime("%d%m%Y_%H%M")+'_'+login.usalogin
					_nomeArq = "/home/"+diretorios.usPrinci+"/direto/apagargrupos/substituir_"+dTa.lower()+".csv"

					__arquivo = open(_nomeArq,"w")
					__arquivo.write( lista_produtos )
					__arquivo.close()
					
					alertas.dia( self, "Dados gravados para "+ str( __ng )+" registros...\n"+(" "*120),"Produtos: Gerenciador")  
					self.levantarGrupos(wx.EVT_BUTTON)

	def incluirTitulo(self,event):

		tipo = self.tipoGrupo()

		if self.danterior.GetValue() and tipo[0]:
			
			grupos = wx.MessageDialog(self.painel,u"Confirme para incluir o "+tipo[1]+"-"+self.danterior.GetValue()+", no cadastro de grupos...\n"+(" "*130),u"Produtos: Gerenciador",wx.YES_NO|wx.NO_DEFAULT)
			if grupos.ShowModal() ==  wx.ID_YES:			

				conn = sqldb()
				sql  = conn.dbc("Produtos: Grupos,sub-grupos e fabricantes", fil = self.p.ppFilial, janela = self )
				achei = False
				grava = True
				
				if sql[0]:

					if sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_cdpd='"+ tipo[0] +"' and fg_desc='"+ self.danterior.GetValue() +"'"):	achei = True
					else:
						
						try:
							
							adicionar = "INSERT INTO grupofab (fg_cdpd,fg_desc) VALUE( %s,%s)"
							sql[2].execute( adicionar, ( tipo[0], self.danterior.GetValue().upper() ) )
							sql[1].commit()

						except Exception as erro:
							
							sql[1].rollback()
							grava = False
							
					conn.cls( sql[1] )
					
					if not achei and grava:
						
						alertas.dia( self, "Titulo de grupos, incluido com sucesso...\n"+(" "*120),"Produtos: Gerenciador")
						self.levantarGrupos(wx.EVT_BUTTON)
						
					if not achei and not grava:
						
						if not type( erro ) == unicode:	erro = str( erro )
						alertas.dia( self, "Erro na inclusão de titulo de grupos...\n\n"+ erro +"\n"+(" "*120),"Produtos: Gerenciador")
						
					if achei:	alertas.dia( self, "Titulo de grupos, ja cadastrado...\n"+(" "*120),"Produtos: Gerenciador")

			self.dapagar.SetValue('')
			self.danterior.SetValue('')
			self.datual.SetValue('')
			
	def apagarTitulos(self,event):

		if self.dapagar.GetValue().strip() and self.gruposub.GetItemCount():
			
			conn = sqldb()
			sql  = conn.dbc("Produtos: Grupos,sub-grupos e fabricantes", fil = self.p.ppFilial, janela = self )
			
			if sql[0]:

				_g = self.gruposub.GetItem( self.gruposub.GetFocusedItem(), 1 ).GetText()

				if _g == "G":	_ng = "SELECT pd_codi,pd_nome,pd_nmgr FROM produtos WHERE pd_nmgr='"+ self.dapagar.GetValue().upper() +"' ORDER BY pd_nome"
				if _g == "1":	_ng = "SELECT pd_codi,pd_nome,pd_sug1 FROM produtos WHERE pd_sug1='"+ self.dapagar.GetValue().upper() +"' ORDER BY pd_nome"
				if _g == "2":	_ng = "SELECT pd_codi,pd_nome,pd_sug2 FROM produtos WHERE pd_sug2='"+ self.dapagar.GetValue().upper() +"' ORDER BY pd_nome"
				if _g == "F":	_ng = "SELECT pd_codi,pd_nome,pd_fabr FROM produtos WHERE pd_fabr='"+ self.dapagar.GetValue().upper() +"' ORDER BY pd_nome"
				if _g == "E":	_ng = "SELECT pd_codi,pd_nome,pd_ende FROM produtos WHERE pd_ende='"+ self.dapagar.GetValue().upper() +"' ORDER BY pd_nome"

				lista_registros = sql[2].execute( _ng )
				resul_registros = sql[2].fetchall()
				

				"""  Apagar o titulo no cadastros de grupos etc...  """
				if self.forcar.GetValue():

					apagar = True
					try:
						__rg = self.gruposub.GetItem( self.gruposub.GetFocusedItem(), 0 ).GetText()

						sql[2].execute("DELETE FROM grupofab WHERE fg_regi='"+ str( __rg ) +"'")
						sql[1].commit()
						
					except Exception as erro:
						
						apagar = False
						sql[1].rollback()
						
				conn.cls( sql[1] )

				lista_produtos = str( lista_registros )+" Registro(s) no cadastro de produtos com o titulo para apagar: "+self.dapagar.GetValue()+"\n\n"
				if lista_registros:
					
					for i in resul_registros:
						
						lista_produtos += "Tipo: "+_g+" "+i[0]+" "+i[2].decode('UTF-8')+" "+i[1].decode('UTF-8')+'\n'

					if not self.forcar.GetValue():
						
						MostrarHistorico.hs = lista_produtos
						
						MostrarHistorico.TP = ""
						MostrarHistorico.TT = "Produtos { Apagar grupos }"
						MostrarHistorico.AQ = ""
						MostrarHistorico.FL = self.p.ppFilial

						his_frame=MostrarHistorico(parent=self,id=-1)
						his_frame.Centre()
						his_frame.Show()
	
				if self.forcar.GetValue() and apagar:

					dTa = datetime.datetime.now().strftime("%d%m%Y_%H%M")+'_'+login.usalogin
					_nomeArq = "/home/"+diretorios.usPrinci+"/direto/apagargrupos/apagar_"+dTa.lower()+".csv"

					__arquivo = open(_nomeArq,"w")
					__arquivo.write( lista_produtos )
					__arquivo.close()

					alertas.dia(self, "Titulo apagado, no cadastro de grupos...\n"+(" "*120),"Produtos: Gerenciador")
					self.levantarGrupos(wx.EVT_BUTTON)

				elif self.forcar.GetValue() and not apagar:

					if not type( erro ) == unicode:	erro = str( erro )
					alertas.dia(self, "Erro ao apagar titulo, no cadastro de grupos...\n\n"+ erro +"\n"+(" "*120),"Produtos: Gerenciador")
					self.levantarGrupos(wx.EVT_BUTTON)

				if not self.forcar.GetValue() and not lista_registros:	alertas.dia(self, u"Esse titulo não consta para nenhum produto\nMarque a opção, Ignore a lista de produtos para apagar\n"+(" "*130),"Produtos: Gerenciador")

				self.dapagar.SetValue('')
				self.danterior.SetValue('')
				self.datual.SetValue('')
					
		self.forcar.SetValue( False )
				
	def levantarGrupos(self,event):

		_ng = self.tipoGrupo()[0]
		self.forcar.SetValue( False )
		
		conn = sqldb()
		sql  = conn.dbc("Produtos: Grupos,sub-grupos e fabricantes", fil = self.p.ppFilial, janela = self )
		
		if sql[0]:
			
			if   "PyEventBinder".upper() in str( event ).upper():	__s = "SELECT fg_regi,fg_cdpd,fg_desc FROM grupofab WHERE fg_cdpd='"+ _ng +"' ORDER BY fg_desc"
			elif event.GetId() in [250,350]:	__s = "SELECT fg_regi,fg_cdpd,fg_desc FROM grupofab WHERE fg_desc='"+ self.dapagar.GetValue()+ "' ORDER BY fg_desc"
			else:	__s = "SELECT fg_regi,fg_cdpd,fg_desc FROM grupofab WHERE fg_cdpd='"+ _ng +"' ORDER BY fg_desc"
			
			__n = sql[2].execute( __s )
			_result = sql[2].fetchall()
	
			conn.cls( sql[1] )
			indice = 0

			self.ocorrencias.SetLabel("Ocorrências:{ "+ str( __n ) +" }")

			self.gruposub.DeleteAllItems()
			self.gruposub.Refresh()			

			for i in _result:
				
				if i[1] in ["G","1","2","F","E"]:

					self.gruposub.InsertStringItem( indice, str( i[0] ) )
					self.gruposub.SetStringItem(indice,1, i[1] )
					self.gruposub.SetStringItem(indice,2, i[2] )
					
					if indice % 2:	self.gruposub.SetItemBackgroundColour(indice, "#859CB2")
					indice +=1

	def passagem(self,event):

		self.dapagar.SetValue( self.gruposub.GetItem( self.gruposub.GetFocusedItem(), 2 ).GetText() )

	def tipoGrupo(self):

		tipo = [""]
		if self.grupos.GetValue():	tipo = ["G","grupo"]
		if self.grupo1.GetValue():	tipo = ["1","sub-grupo_1"]
		if self.grupo2.GetValue():	tipo = ["2","sub_grupo_2"]	 
		if self.fabric.GetValue():	tipo = ["F","fabricante"]
		if self.endere.GetValue():	tipo = ["E",u"endereço"]

		return tipo
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Produtos: Gerenciador de grupos, sub-brupos", 0, 437, 90)

		dc.SetTextForeground("#0A59A7") 	
		dc.DrawRotatedText(u"Filial", 492, 390, 90)
		dc.DrawRotatedText(self.p.ppFilial, 513, 390, 90)

		""" Boxes """
		""" Dados da NFE-ECF"""
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(485, 344, 44, 93, 3) #-: Dados da NFE

	def OnEnterWindow(self, event):

		if   event.GetId() == 350:	sb.mstatus(u"  Grupo,sub-gupos, fabricante, endereços para apagar",0)
		elif event.GetId() == 351:	sb.mstatus(u"  Utilize para incluir um novo titulo ou para substituir ele por outro titulo",0)
		elif event.GetId() == 352:	sb.mstatus(u"  Utilize para ser o substituto do titulo anterior",0)
		elif event.GetId() == 250:	sb.mstatus(u"  Procurar por descrição do titulo desejado",0)
		elif event.GetId() == 251:	sb.mstatus(u"  Utilize para apagar o titulo no campo dados para apagar",0)
		elif event.GetId() == 252:	sb.mstatus(u"  Incluir um novo titulo",0)
		elif event.GetId() == 253:	sb.mstatus(u"  Substituição do titulo anteriror pelo atual",0)
		elif event.GetId() == 254:	sb.mstatus(u"  Sair do gerenciador",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus(u"  Produtos: Gerenciador de grupo, sub-grupos",0)
		event.Skip()

class CalcularConversao:
	
	#def calcularEmbalagens( self, p, dados ):
	
	#	quantidade_compras = dados[0]
	#	quantidade_unidade = dados[1]

	#	indice_lista_compras = dados[2]
	#	valor_total_produto  = dados[3]
		
	#	p.ListaCMP.SetStringItem( indice_lista_compras, 69, "0.0000" ) #-:QT em Unidades
	#	p.ListaCMP.SetStringItem( indice_lista_compras ,77, "0.0000" ) #-:Valor de cada unidade de produtos

	#	if quantidade_compras and quantidade_unidade:

	#		qTu = (  Decimal( quantidade_compras ) * Decimal( quantidade_unidade ) )
	#		p.ListaCMP.SetStringItem( indice_lista_compras, 69, str( qTu ) ) #-:QT em Unidades
				
	#		if valor_total_produto and Decimal( valor_total_produto ) and qTu:
					
	#			vvTP = Decimal( valor_total_produto )
	#			vpUn = Trunca.trunca( 5, ( vvTP / qTu ) )
	#			p.ListaCMP.SetStringItem( indice_lista_compras ,77, str( vpUn ) ) #-:Valor de cada unidade de produtos

	def calcularEmbalagensAutomatico( self, p, dados, gravar ):

		quantidade_embalagens = dados[0]
		valor_unitario = dados[1]
		quantidade_compras = dados[2]
		indice_lista_compras = dados[3]
			
		valor_manual = Trunca.trunca( 5, ( valor_unitario / quantidade_embalagens ) )
		quantidade_manual = ( quantidade_embalagens * quantidade_compras )

		if gravar:	p.ListaCMP.SetStringItem( indice_lista_compras ,69, str( quantidade_manual ) ) #// Quantidade
		if gravar:	p.ListaCMP.SetStringItem( indice_lista_compras, 77, str( valor_manual ) ) #// Valor unitario
	
		return quantidade_manual, valor_manual
		
	def calcularMetragens( self, p, dados, gravar ):

		comprimento = dados[0]
		largura = dados[1]
		expessura = dados[2]
		quantidade_compras = dados[3]
		valor_total_produto = dados[4]
		dados_com_lar_exp = dados[5]
		indice_lista_compras =  dados[6]
			
		resul =  nF.metrosUnidade( 1,  dados_com_lar_exp, quantidade_compras, valor_total_produto,p )
			
		if gravar:	p.ListaCMP.SetStringItem( indice_lista_compras, 69, '0.0000' ) #-: Quantidade
		if gravar:	p.ListaCMP.SetStringItem( indice_lista_compras ,77, '0.0000' ) #-: Valor unitario
			
		if resul[0] and gravar:	p.ListaCMP.SetStringItem( indice_lista_compras, 69, str( resul[1] ) ) #-: Quantidade
		if resul[0] and gravar:	p.ListaCMP.SetStringItem( indice_lista_compras ,77, str( resul[2] ) ) #-: Valor unitario

		return resul[0], str( resul[1] ), str( resul[2] )
