#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 18-09-2014 12:36 Jose Lobinho

import wx
import datetime
import os

from conectar import sqldb,gerenciador,listaemails,dialogos,cores,login,menssagem,sbarra,MostrarHistorico,diretorios,acesso

alertas = dialogos()
mens    = menssagem()
sb      = sbarra()
acs     = acesso()

class PlanoContas(wx.Frame):

	TipoAcesso = ""
	
	def __init__(self, parent,id):
		
		self.p = parent

		if self.TipoAcesso.upper() == "CONSULTA":

			wx.Frame.__init__(self, parent, id, 'Plano de Contas { Gerênciador }', size=(730,330), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
			
		else:	wx.Frame.__init__(self, parent, id, 'Plano de Contas { Gerênciador }', size=(730,506), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)

		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)

		if self.TipoAcesso.upper() == "CONSULTA":
		
			self.tree = wx.TreeCtrl(self.painel, 1, pos=(38,0),size=(689,300), style=wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_SINGLE)
			self.painel.Bind(wx.EVT_PAINT,self.desenho)

		else:	self.tree = wx.TreeCtrl(self.painel, 1, pos=(12,0),size=(713,365), style=wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_SINGLE)

		self.tree.SetBackgroundColour("#BFBFBF")
		self.tree.SetForegroundColour("#1A5EA1")
		self.tree.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		if self.TipoAcesso.upper() == "CONSULTA":

			wx.StaticText(self.painel,-1,u"Nº Conta-Descrição da Conta: ", pos=(38,308)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.cConta = wx.TextCtrl(self.painel,-1,'',pos=(215,303),size=(100,22),style = wx.TE_READONLY)
			self.cConta.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.cConta.SetBackgroundColour('#E5E5E5')
			self.cConta.SetForegroundColour('#366EA5')

			self.dConta = wx.TextCtrl(self.painel,-1,'',pos=(320,303),size=(407,22),style = wx.TE_READONLY)
			self.dConta.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.dConta.SetBackgroundColour('#E5E5E5')
			self.dConta.SetForegroundColour('#366EA5')

			voltar = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(0,247), size=(36,34))
			export = wx.BitmapButton(self.painel, 106, wx.Bitmap("imagens/cima20.png", wx.BITMAP_TYPE_ANY), pos=(0,290), size=(36,34))

			voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			export.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

			voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			export.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

			voltar.Bind(wx.EVT_BUTTON, self.sair)
			export.Bind(wx.EVT_BUTTON, self.exporTarConta)
			self.aplicacoes(wx.EVT_BUTTON)

		else:
		
			wx.StaticText(self.painel,-1,u"Nº Conta { Descrição da Conta } Nº Registro:", pos=(20,380)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,u"Nº Sub-Conta { Descrição da Sub-Conta }", pos=(20,420)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1,u"2-Sub-Conta", pos=(430,380)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,u"3-Sub-Conta", pos=(430,420)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,u"4-Sub-Conta", pos=(430,460)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,u"Descrição da Nova Conta", pos=(503,380)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,u"Descrição da Nova Conta", pos=(503,420)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,u"Descrição da Nova Conta", pos=(503,460)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.ins = wx.StaticText(self.painel,-1,u"Nº de Conta p/Alteração", pos=(235,460))
			self.ins.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.ins.SetForegroundColour('#4D4D4D')

			self.nrg = wx.StaticText(self.painel,-1,u"", pos=(260,380))
			self.nrg.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.nConta = wx.TextCtrl(self.painel,-1,'',pos=(17,393),size=(400,22),style = wx.TE_READONLY)
			self.nConta.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.nConta.SetBackgroundColour('#E5E5E5')
			self.nConta.SetForegroundColour('#366EA5')

			self.sConta = wx.TextCtrl(self.painel,-1,'',pos=(17,433),size=(400,22),style = wx.TE_READONLY)
			self.sConta.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.sConta.SetBackgroundColour('#E5E5E5')
			self.sConta.SetForegroundColour('#366EA5')

			""" Entrada de Contas """
			self.nvConta2 = wx.TextCtrl(self.painel,-1,'',pos=(427,393),size=(65,22))
			self.nvConta3 = wx.TextCtrl(self.painel,-1,'',pos=(427,433),size=(65,22))
			self.nvConta4 = wx.TextCtrl(self.painel,-1,'',pos=(427,473),size=(65,22))

			self.ndConta2 = wx.TextCtrl(self.painel,-1,'',pos=(500,393),size=(227,22))
			self.ndConta3 = wx.TextCtrl(self.painel,-1,'',pos=(500,433),size=(227,22))
			self.ndConta4 = wx.TextCtrl(self.painel,-1,'',pos=(500,473),size=(224,22))

			self.nvConta2.SetBackgroundColour('#E5E5E5')
			self.ndConta2.SetBackgroundColour('#E5E5E5')
			self.nvConta3.SetBackgroundColour('#E5E5E5')
			self.ndConta3.SetBackgroundColour('#E5E5E5')
			self.nvConta4.SetBackgroundColour('#E5E5E5')
			self.ndConta4.SetBackgroundColour('#E5E5E5')

			self.ndConta2.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.ndConta3.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.ndConta4.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			self.nvConta2.SetMaxLength(1)
			self.ndConta2.SetMaxLength(60)
			self.nvConta3.SetMaxLength(2)
			self.ndConta3.SetMaxLength(60)
			self.nvConta4.SetMaxLength(3)
			self.ndConta4.SetMaxLength(60)

			voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltam.png",        wx.BITMAP_TYPE_ANY), pos=(18, 460), size=(36,34))
			exempl = wx.BitmapButton(self.painel, 108, wx.Bitmap("imagens/pdf16.png",         wx.BITMAP_TYPE_ANY), pos=(390,464), size=(26,30))
			self.altera = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/alterarm.png", wx.BITMAP_TYPE_ANY), pos=(60, 460), size=(36,34))
			self.inclui = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/incluip.png",  wx.BITMAP_TYPE_ANY), pos=(100,460), size=(36,34))
			self.exclui = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/apagar.png",   wx.BITMAP_TYPE_ANY), pos=(140,460), size=(36,34))
			self.creler = wx.BitmapButton(self.painel, 107, wx.Bitmap("imagens/reler20.png",  wx.BITMAP_TYPE_ANY), pos=(180,460), size=(36,34))
		
			voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			exempl.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.altera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.inclui.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.exclui.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.creler.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

			voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			exempl.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.altera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.inclui.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.exclui.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.creler.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

			self.aplicacoes(wx.EVT_BUTTON)
			
			voltar.Bind(wx.EVT_BUTTON, self.sair)
			exempl.Bind(wx.EVT_BUTTON, self.ExemploPlano)
			self.inclui.Bind(wx.EVT_BUTTON, self.IncluirConta)
			self.altera.Bind(wx.EVT_BUTTON, self.AlterarConta)
			self.exclui.Bind(wx.EVT_BUTTON, self.apContas)
			self.creler.Bind(wx.EVT_BUTTON, self.relerConta)

			self.inclui.Enable( acs.acsm("1401",True) )
			self.altera.Enable( acs.acsm("1402",True) )
			self.exclui.Enable( acs.acsm("1403",True) )

	def sair(self,event):	self.Destroy()
	def relerConta(self,event):
		self.tree.DeleteAllItems()
		self.aplicacoes(wx.EVT_BUTTON)
		
	def apContas(self,event):

		apC_frame=ApagarContas(parent=self,id=-1)
		apC_frame.Centre()
		apC_frame.Show()

	def ExemploPlano(self,event):

		if os.path.exists(diretorios.aTualPsT+"/srv/planodecontas.pdf") == True:

			gerenciador.Anexar = diretorios.aTualPsT+"/srv/planodecontas.pdf"
			gerenciador.secund = ''
			gerenciador.emails = ''
			gerenciador.TIPORL = ''
			gerenciador.Filial = login.identifi

			ger_frame=gerenciador(parent=self,id=-1)
			ger_frame.Centre()
			ger_frame.Show()
		
		else:	alertas.dia(self.painel,u"Arquivo Exemplo não Localizado na Pasta!!\n","Plano de Contas Arquivo Exemplo")
		
	def aplicacoes(self,event):

		self.root = self.tree.AddRoot('Plano de Contas')

		aTivo    = self.tree.AppendItem(self.root, u'1 - ATIVO')
		passivo  = self.tree.AppendItem(self.root, u'2 - PASSIVO')
		receitas = self.tree.AppendItem(self.root, u'3 - RECEITAS')
		despesas = self.tree.AppendItem(self.root, u'4 - DESPESAS')
		
		conn = sqldb()
		sql  = conn.dbc("Plano de Contas", fil = login.identifi, janela = self.painel)
		
		if sql[0] == True:

			nRegis = sql[2].execute("SELECT * FROM plcontas ORDER BY pl_nconta")
			result = sql[2].fetchall()
			conn.cls(sql[1])
		
			_appen2 = _appen3 = _appen4 = ""
		
			indice = 0
			for i in result:

				_reg = str(i[0]).zfill(10)
				_cns = i[1].split('.')
				_ds2 = i[2]
				_ds3 = i[3]
				_ds4 = i[4]

				_n02 = _n03 = _n04 = ""
				if len(_cns) == 2:	_n02 = _cns[1]
				elif len(_cns) == 3:
					
					_n02 = _cns[1]
					_n03 = _cns[2]

				elif len(_cns) == 4:
					
					_n02 = _cns[1]
					_n03 = _cns[2]
					_n04 = _cns[3]

				if _cns[0] == "1":

					if _n02 !='' and _n03 == '' and _n04 == '':	_appen2 = self.tree.AppendItem(aTivo, str(_cns[0])+'.'+str(_cns[1])+' - '+str(i[2])+':    {'+_reg+'}')
					if _n03 !='' and _n04 == '':	_appen3 = self.tree.AppendItem(_appen2 , str(_cns[0])+'.'+str(_cns[1])+'.'+str(_cns[2])+' - '+str(i[3])+':    {'+_reg+'}')
					if _n04 !='':	_appen4 = self.tree.AppendItem(_appen3 , str(_cns[0])+'.'+str(_cns[1])+'.'+str(_cns[2])+'.'+str(_cns[3])+' - '+str(i[4])+':    {'+_reg+'}')

				elif _cns[0] == "2":

					if _n02 !='' and _n03 == '' and _n04 == '':	_appen2 = self.tree.AppendItem(passivo, str(_cns[0])+'.'+str(_cns[1])+' - '+str(i[2])+':    {'+_reg+'}')
					if _n03 !='' and _n04 == '':	_appen3 = self.tree.AppendItem(_appen2 , str(_cns[0])+'.'+str(_cns[1])+'.'+str(_cns[2])+' - '+str(i[3])+':    {'+_reg+'}')
					if _n04 !='':	_appen4 = self.tree.AppendItem(_appen3 , str(_cns[0])+'.'+str(_cns[1])+'.'+str(_cns[2])+'.'+str(_cns[3])+' - '+str(i[4])+':    {'+_reg+'}')

				elif _cns[0] == "3":

					if _n02 !='' and _n03 == '' and _n04 == '':	_appen2 = self.tree.AppendItem(receitas, str(_cns[0])+'.'+str(_cns[1])+' - '+str(i[2])+':    {'+_reg+'}')
					if _n03 !='' and _n04 == '':	_appen3 = self.tree.AppendItem(_appen2 , str(_cns[0])+'.'+str(_cns[1])+'.'+str(_cns[2])+' - '+str(i[3])+':    {'+_reg+'}')
					if _n04 !='':	_appen4 = self.tree.AppendItem(_appen3 , str(_cns[0])+'.'+str(_cns[1])+'.'+str(_cns[2])+'.'+str(_cns[3])+' - '+str(i[4])+':    {'+_reg+'}')

				elif _cns[0] == "4":

					if _n02 and despesas and _n03 == '' and _n04 == '':	_appen2 = self.tree.AppendItem(despesas, str(_cns[0])+'.'+str(_cns[1])+' - '+str(i[2])+':    {'+_reg+'}')
					if _n03 and _appen2 and _n04 == '':	_appen3 = self.tree.AppendItem(_appen2 , str(_cns[0])+'.'+str(_cns[1])+'.'+str(_cns[2])+' - '+str(i[3])+':    {'+_reg+'}')
					if _n04 and _appen3:	_appen4 = self.tree.AppendItem(_appen3 , str(_cns[0])+'.'+str(_cns[1])+'.'+str(_cns[2])+'.'+str(_cns[3])+' - '+str(i[4])+':    {'+_reg+'}')
		
	def AlterarConta(self,event):

		numero_conta = self.nConta.GetValue()
		numero_subconta = self.sConta.GetValue()

		_cp = self.sConta.GetValue().split(' - ')[0].split('.')[0]
		_s2 = self.nvConta2.GetValue()
		_s3 = self.nvConta3.GetValue().zfill(2)
		_s4 = str( self.nvConta4.GetValue() )
		if self.nrg.GetLabel() !='':	_rg = self.nrg.GetLabel().split('{')[1].split('}')[0]
		else:	_rg = ""
		
		_d2 = self.ndConta2.GetValue()
		_d3 = self.ndConta3.GetValue()
		_d4 = self.ndConta4.GetValue()
		
		_cT2 = _cT3 = _cT4 = ""
		_alTeracao = ''
		
		if _s2 !='' and _s2.isdigit() == True and _d2 !='':	_cT2 = _cp+'.'+_s2
		if _s3 !='' and _s3.isdigit() == True and _d3 !='':	_cT3 = _cp+'.'+_s2+'.'+_s3
		if _s4 !='' and _s4.isdigit() == True and _d4 !='':	_cT4 = _cp+'.'+_s2+'.'+_s3+'.'+_s4.zfill(3)

		if _cT2 !='':	_alTeracao = '2'	
		if _cT3 !='':	_alTeracao = '3'	
		if _cT4 !='':	_alTeracao = '4'	

		if _alTeracao == '':	alertas.dia(self.painel,u"Nenhuma Conta Selecionada para Alterar!!\n"+(' '*100),u"Plano de Contas: Alteração")
		if _alTeracao != '' and _rg == '':	alertas.dia(self.painel,u"Nenhuma Conta Selecionada para Alterar!!\nRegistro Vazio...\n"+(' '*100),u"Plano de Contas: Alteração")
		if _alTeracao != '' and _rg != '':
			
			_numeroconta = ''
			if _alTeracao == '2':	_numeroconta = _cT2+"-"+_d2
			if _alTeracao == '3':	_numeroconta = _cT3+"-"+_d3
			if _alTeracao == '4':	_numeroconta = _cT4+"-"+_d4

			segui = wx.MessageDialog(self.painel,u"Alterar Registro Nº: "+_rg+u"\nPara a Conta Nº "+_numeroconta+"\n\nConfirme para Alterar Conta!!\n"+(" "*120),u"Plano de Contas: Inclusão",wx.YES_NO|wx.NO_DEFAULT)
			if segui.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Plano de Contas", fil = login.identifi, janela = self.painel )
				grv  = False
					
				if sql[0] == True:

					"""  Backup do Plano de Contas  """
					
					self.BackConta( sql[2] )
					
					nConTa = _numeroconta.split('-')[0]
					dConTa = _numeroconta.split('-')[1]
					
					if _alTeracao == '2':	alTerar = "UPDATE plcontas SET pl_nconta=%s,pl_dconta=%s WHERE pl_regist=%s"
					if _alTeracao == '3':	alTerar = "UPDATE plcontas SET pl_nconta=%s,pl_dcont3=%s WHERE pl_regist=%s"
					if _alTeracao == '4':	alTerar = "UPDATE plcontas SET pl_nconta=%s,pl_dcont4=%s WHERE pl_regist=%s"

					lista_atualizadas = ""
					try:

						sql[2].execute(alTerar,(nConTa,dConTa,_rg))		
						sql[1].commit()
						grv = True
						
						EMD = datetime.datetime.now().strftime("%Y/%m/%d %T ")+login.usalogin
						lista_atualizadas +=EMD+'|'+numero_conta+' '+numero_subconta+' Descricao: '+_d2+'-'+_d3+'-'+_d4+'|'+nConTa+'|'+dConTa+str( _rg )+ '\n'

					except Exception as _reTornos:

						sql[1].rollback()
						grv = False
						
					conn.cls(sql[1])

					if grv and lista_atualizadas: #// Grava quem apagou

						__hoje = datetime.datetime.now().strftime("%Y%m%d%T").replace(':','')
						__arquivo = open( diretorios.plcontas + "plcontas_contasatualizadas_"+ __hoje + ".txt","w")
						__arquivo.write( lista_atualizadas )
						__arquivo.close()

					if grv == False:	alertas.dia(self.painel,u"Alteração não concluida !!\n \nRetorno: "+str(_reTornos),"Plano de Contas: Alteração")	
					if grv == True:

						self.tree.DeleteAllItems()
						self.aplicacoes(wx.EVT_BUTTON)

	def IncluirConta(self,event):

		_vl = False
		_cp = self.sConta.GetValue().split(' - ')[0].split('.')[0]
		_s2 = self.nvConta2.GetValue()
		_s3 = self.nvConta3.GetValue().zfill(2)
		_s4 = str( self.nvConta4.GetValue() )
		
		_d2 = self.ndConta2.GetValue()
		_d3 = self.ndConta3.GetValue()
		_d4 = self.ndConta4.GetValue()
		
		_cT2 = _cT3 = _cT4 = ""
		_ic2 = _ic3 = _ic4 = False

		if _s2 !='' and _s2.isdigit() == True:	_cT2 = _cp+'.'+_s2
		if _s2 !='' and _s3 !='' and _s3.isdigit() == True:	_cT3 = _cp+'.'+_s2+'.'+_s3
		if _s2 !='' and _s3 !='' and _s4 !='' and _s4.isdigit() == True:	_cT4 = _cp+'.'+_s2+'.'+_s3+'.'+_s4.zfill(3)
		
		if _s2 !='' and _d2 =='':	_vl = True
		if _s3 !='' and _d3 =='':	_vl = True
		if _s4 !='' and _d4 =='':	_vl = True

		if _vl == True:	alertas.dia(self.painel,u'Nº de Conta com Descrição Vazia...\n'+(" "*100),"Plano de Contas: Inclusão")
		else:

			conn = sqldb()
			sql  = conn.dbc("Plano de Contas: Inclusão/Alteração", fil = login.identifi, janela = self.painel )
			grv  = False
			err  = False
			
			if sql[0] == True:

				"""  Backup do Plano de Contas  """
				self.BackConta( sql[2] )

				acT2 = acT3 = acT4 = 0

				if _cT2 !='':	acT2 = sql[2].execute("SELECT * FROM plcontas WHERE pl_nconta='"+str(_cT2)+"'")
				if _cT3 !='':	acT3 = sql[2].execute("SELECT * FROM plcontas WHERE pl_nconta='"+str(_cT3)+"'")
				if _cT4 !='':	acT4 = sql[2].execute("SELECT * FROM plcontas WHERE pl_nconta='"+str(_cT4)+"'")
				
				InConTa = "Contas para Incluir:\n\n"
				Adicion = ""
				if acT2 == 0 and _cT2 !='' and _d2 !='':	Adicion +="Sub-Conta-2: {"+str(_cT2)+" - "+_d2+"}\n"
				if acT3 == 0 and _cT3 !='' and _d3 !='':	Adicion +="Sub-Conta-3: {"+str(_cT3)+" - "+_d3+"}\n"
				if acT4 == 0 and _cT4 !='' and _d4 !='':	Adicion +="Sub-Conta-4: {"+str(_cT4)+" - "+_d4+"}\n"

				if acT2 == 0 and _cT2 !='' and _d2 !='':	_ic2 = True
				if acT3 == 0 and _cT3 !='' and _d3 !='':	_ic3 = True
				if acT4 == 0 and _cT4 !='' and _d4 !='':	_ic4 = True
					
				if Adicion != '':
					
					segui = wx.MessageDialog(self.painel,InConTa+Adicion+(" "*120),"Plano de Contas: Inclusão",wx.YES_NO|wx.NO_DEFAULT)
					if segui.ShowModal() ==  wx.ID_YES:

						try:
							
							_conTa2 = "INSERT INTO plcontas (pl_nconta,pl_dconta) VALUES(%s,%s)"
							_conTa3 = "INSERT INTO plcontas (pl_nconta,pl_dcont3) VALUES(%s,%s)"
							_conTa4 = "INSERT INTO plcontas (pl_nconta,pl_dcont4) VALUES(%s,%s)"
							
							if _ic2 == True:	sql[2].execute(_conTa2,(_cT2,_d2))
							if _ic3 == True:	sql[2].execute(_conTa3,(_cT3,_d3))
							if _ic4 == True:	sql[2].execute(_conTa4,(_cT4,_d4))
							
							sql[1].commit()
							grv = True

						except Exception, _reTornos:
							err = True
							sql[1].rollback()

				conn.cls(sql[1])
				
				if Adicion == '':	alertas.dia(self.painel,u"Nenhuma Conta Valida para Incluir...\n"+(' '*100),"Plano de Contas: Inclusão")
				if err == True:	alertas.dia(self.painel,u"Inclusão não concluida !!\n \nRetorno: "+str(_reTornos),"Plano de Contas: Inclusão")	
				
				if Adicion != '' and grv == True:

					self.tree.DeleteAllItems()
					self.aplicacoes(wx.EVT_BUTTON)

	def BackConta( self, banco ):
		
		daTgr = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
		pasTa = "planocontas_"+login.emfantas.strip().lower()+str(daTgr)+'.csv'

		""" O servidor MariaDB está sendo executado com a opção --secure-file-priv para que não possa executar esta declaração se nao grava normal """
		if os.path.exists('/var/lib/mysql-files'):	_csv = banco.execute( "SELECT * FROM plcontas INTO OUTFILE '/var/lib/mysql-files/"+pasTa+"' FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n'" )
		else:	_csv = banco.execute( "SELECT * FROM plcontas INTO OUTFILE '/tmp/"+pasTa+"' FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n'" )
							
	def OnSelChanged(self, event):
		
		item = event.GetItem()
		filh = self.tree.GetItemText(item).split(':')[0]
		ipai = self.tree.GetItemText(self.tree.GetItemParent(item)).split(':')[0]

		regi = self.tree.GetItemText(item).split(':')

		if self.TipoAcesso.upper() == "CONSULTA":
	
			self.cConta.SetValue('')
			self.dConta.SetValue('')
			__conta = filh.split('-')[0].split('.')

			if len( __conta ) > 1:
				
				self.cConta.SetValue(filh.split('-')[0])
				self.dConta.SetValue(filh.split('-')[1])
	
		else:
			
			self.nConta.SetValue(ipai)
			self.sConta.SetValue(filh)

			_conta = filh.split('-')
			_selec = _conta[0].split('.')
			_quant = len(_selec)

			if len( regi ) > 1:	self.nrg.SetLabel(str(regi[1]))
		
			if _quant == 1:
				
				self.nvConta2.SetValue('')
				self.ndConta2.SetValue('')

				self.nvConta3.SetValue('')
				self.ndConta3.SetValue('')

				self.nvConta4.SetValue('')
				self.ndConta4.SetValue('')

			self.ins.SetLabel('Nº de Conta p/Alteração')
			if _quant !=1:	self.ins.SetLabel('Nº de Conta p/Alteração\n{ '+str( _conta[0].strip() )+' }')

			if _quant == 2:

				self.nvConta3.SetValue('')
				self.ndConta3.SetValue('')

				self.nvConta4.SetValue('')
				self.ndConta4.SetValue('')

			if _quant == 3:

				self.nvConta4.SetValue('')
				self.ndConta4.SetValue('')
		
			if _quant == 2:
				self.nvConta2.SetValue(_selec[1])
				self.ndConta2.SetValue(_conta[1].strip())
				
			if _quant == 3:
				self.nvConta2.SetValue(_selec[1])
				self.nvConta3.SetValue(_selec[2])
				self.ndConta3.SetValue(_conta[1].strip())

			if _quant == 4:

				self.nvConta2.SetValue(_selec[1])
				self.nvConta3.SetValue(_selec[2])
				self.nvConta4.SetValue(_selec[3])
				self.ndConta4.SetValue(_conta[1].strip())

			self.ndConta2.SetBackgroundColour('#E5E5E5')
			self.ndConta3.SetBackgroundColour('#E5E5E5')
			self.ndConta4.SetBackgroundColour('#E5E5E5')
			if _quant == 2:	self.ndConta2.SetBackgroundColour('#BFBFBF')
			if _quant == 3:	self.ndConta3.SetBackgroundColour('#BFBFBF')
			if _quant == 4:	self.ndConta4.SetBackgroundColour('#BFBFBF')
			
	def exporTarConta(self,event):
		
		if self.cConta.GetValue() == '':	alertas.dia(self.painel,u"Selecione uma sub-conta valida!!\n"+(" "*80),"Plano de Contas")
		else:
			self.p.AtualizaPlContas(self.cConta.GetValue())
			self.sair(wx.EVT_BUTTON)

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Gravar Alteração da Conta Selecionada",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Incluir uma Nova Conta",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Apagar Conta Selecionada",0)
		elif event.GetId() == 105:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 106:	sb.mstatus(u"  Exporta Conta para Modulo Chamador",0)
		elif event.GetId() == 107:	sb.mstatus(u"  Atualizar - Reler Lista de Plano de Contas",0)
		elif event.GetId() == 108:	sb.mstatus(u"  Exemplo de um Plano de Contas",0)
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Plano de Contas",0)
		event.Skip()

			
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#123B63") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		if self.TipoAcesso.upper() == "CONSULTA":

			dc.SetFont(wx.Font(17, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
			dc.SetTextForeground(cores.boxtexto)
			dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
			dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
			dc.DrawRoundedRectangle(2,2,32,240,   3) #-->[ Lykos ]
			dc.DrawRotatedText("Plano de Contas", 5, 220, 90)

		else:
			dc.DrawRotatedText("Plano de Contas", 0, 495, 90)
			dc.SetTextForeground("#2A5177") 	
			dc.DrawRotatedText("Lista de Contas e Sub-Contas", 0, 280, 90)

			dc.SetTextForeground(cores.boxtexto)
			dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
			dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
			dc.DrawRoundedRectangle(12,375,410,123,   3) #-->[ Lykos ]
			dc.DrawRoundedRectangle(425,458,300,40,   3) #-->[ Lykos ]


class ApagarContas(wx.Frame):
	
	def __init__(self, parent,id):
		
		self.p = parent
		_conta = self.p.sConta.GetValue().split('-')[0].split('.')
		_quanT = len(_conta)
		
		""" Montagem das Contas """
		self._cT2 = self._cT3 = self._cT4 = ''

		if _quanT == 2:	self._cT2 = _conta[0]+'.'+_conta[1]
		if _quanT == 3:
			self._cT2 = _conta[0]+'.'+_conta[1]
			self._cT3 = _conta[0]+'.'+_conta[1]+'.'+_conta[2]

		if _quanT == 4:
			self._cT2 = _conta[0]+'.'+_conta[1]
			self._cT3 = _conta[0]+'.'+_conta[1]+'.'+_conta[2]
			self._cT4 = _conta[0]+'.'+_conta[1]+'.'+_conta[2]+'.'+_conta[3]
		
		wx.Frame.__init__(self, parent, id, 'Plano de Contas { Apagar Conta(s) }', size=(485,135), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,"Nº Registro", pos=(20,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Ultima Sub-Conta { Descrição }", pos=(130,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nReg = wx.TextCtrl(self.painel,-1,value=str( self.p.nrg.GetLabel().strip() ), pos=(15,17), size=(100,18),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nReg.SetBackgroundColour('#BFBFBF')
		self.nReg.SetForegroundColour('#153E67')
		self.nReg.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.desc = wx.TextCtrl(self.painel,-1,value=str( self.p.sConta.GetValue() ), pos=(125,17), size=(355,20),style=wx.TE_READONLY)
		self.desc.SetBackgroundColour('#BFBFBF')
		self.desc.SetForegroundColour('#153E67')
		self.desc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cT2 = wx.RadioButton(self.painel,-1,"Apagar Grupo da Conta-SubContas 2   { "+str( self._cT2 )+" }", pos=(20, 45),style=wx.RB_GROUP)
		self.cT3 = wx.RadioButton(self.painel,-1,"Apagar Grupo da Conta-SubContas 3   { "+str( self._cT3 )+" }", pos=(20, 70))
		self.cT4 = wx.RadioButton(self.painel,-1,"Apagar Sub-Conta 4"+str( self.p.nrg.GetLabel() )+" { "+str( self._cT4 )+" }",  pos=(20, 95))

		avanca = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/executa.png", wx.BITMAP_TYPE_ANY), pos=(440, 47), size=(36,34))
		voltar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/voltam.png",  wx.BITMAP_TYPE_ANY), pos=(440, 87), size=(36,34))
	
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		avanca.Bind(wx.EVT_BUTTON, self.ApagarSContas)

		if self._cT2 == '':	self.cT2.Enable(False)
		if self._cT3 == '':	self.cT3.Enable(False)
		if self._cT4 == '':	self.cT4.Enable(False)
		if ( self._cT2 + self._cT3 + self._cT4 ) == '':	avanca.Enable(False)
	
	def sair(self,event):	self.Destroy()
	def ApagarSContas(self,event):

		numeroConta = ''
		nReg = 0

		if self.cT2.GetValue() == True:	numeroConta = self._cT2.strip()
		if self.cT3.GetValue() == True:	numeroConta = self._cT3.strip()
		if self.cT4.GetValue() == True:	numeroConta = self._cT4.strip()

		if numeroConta !='':

			segui = wx.MessageDialog(self.painel,"Apagar Conta(s) e Sub-Conta(s) Nº: "+str( numeroConta )+"\n\nConfirme para Apagar!!\n"+(" "*120),"Plano de Contas: Exclusão",wx.YES_NO|wx.NO_DEFAULT)
			if segui.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Plano de Contas: Apagar Conta(s)", fil = login.identifi, janela = self.painel )
				err  = False

				if sql[0] == True:

					lista_apagadas = ""

					try:
					
						conTa = "SELECT * FROM plcontas ORDER BY pl_nconta"
						selec = sql[2].execute(conTa)
						resul = sql[2].fetchall()

						for i in resul:
							
							if i[1][:len(numeroConta)] == numeroConta:

								EMD = datetime.datetime.now().strftime("%Y/%m/%d %T ")+login.usalogin
								lista_apagadas +=EMD+'|'+i[1]+ '\n'
								aPaga = "DELETE FROM plcontas WHERE pl_nconta='"+ str( i[1] )+"'"

								Final = sql[2].execute( aPaga )
								nReg +=1
						
						if nReg !=0:	sql[1].commit()		

					except Exception as _reTornos:
						err = True
						sql[1].rollback()
					
				conn.cls(sql[1])

			if err == True:	alertas.dia(self.painel,u"Exclusão não concluida !!\n \nRetorno: "+str(_reTornos),"Plano de contas: exclusão")	
			if not err and lista_apagadas: #// Grava quem apagou

				__hoje = datetime.datetime.now().strftime("%Y%m%d%T").replace(':','')
				__arquivo = open( diretorios.plcontas + "plcontas_contasapagadas_"+ __hoje + ".txt","w")
				__arquivo.write( lista_apagadas )
				__arquivo.close()

			if nReg != 0:

				self.p.tree.DeleteAllItems()
				self.p.aplicacoes(wx.EVT_BUTTON)
				
				self.sair(wx.EVT_BUTTON)
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#C13E3E") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Apagar Conta(s)", 0, 132, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(12,1,470,132,   3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(15,40,464,90,   3) #-->[ Lykos ]
