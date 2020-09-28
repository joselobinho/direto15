#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Jose de almeida lobinho 30/10/2017 8:50
import wx
import time
import datetime
import commands

from decimal  import *
from conectar import sqldb,diretorios,login,menssagem,dialogos,sbarra,formasPagamentos,numeracao,TelNumeric
from produtof import vinculacdxml

from wx.lib.buttons import GenBitmapTextButton

mens = menssagem()
sb   = sbarra()
nF   = numeracao()
alertas = dialogos()

class ControleEstoqueItems(wx.Frame):
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.i = id
		
		self.permisao_fisico  = False
		self.marcar_desmarcar = False
		
		wx.Frame.__init__(self, parent, id, 'Gerenciador de estoques e produtos de filiais', size=(900,473), style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.controle_filiais = ListaControleEstoque(self.painel, 300,pos=(13,75), size=(887,273),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)
		self.controle_filiais.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.controle_filiais.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.marcarDesmarcar )

		informe1 = u"{ Cuidado na utlização deste modulo para apagar produtos no cadastro de produtos }"
		informe2 = u"O produto e cadastrado apenas uma unica vez na tabela de produtos e replicado na tabela do estoque fisico para cada filiak, portando ao apagar os produtos\n"+\
				   u"no cadastro de produtos o mesmo e eliminado definitivamente na tabela de produtos e na tabela do estoque fisico para todas as filiais.\n\nEntão so utilize esta opçao se precisar eliminar esses produtos nas duas tabelas"
				   
		atencao1 = wx.StaticText(self.painel,-1, informe1, pos=(15, 2))
		atencao1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		atencao1.SetForegroundColour('#ED1A1A')

		atencao2 = wx.StaticText(self.painel,-1, informe2, pos=(15, 20))
		atencao2.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		atencao2.SetForegroundColour('#A52A2A')

		atencao3 = wx.StaticText(self.painel,-1, "{ Seleciona produtos com estoque zerado/negativo }", pos=(615, 60))
		atencao3.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		atencao3.SetForegroundColour('#0C7A9E')

		self.ocorrencias = wx.StaticText(self.painel,-1,u"Ocorrencias\n{}", pos=(440, 352))
		self.ocorrencias.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ocorrencias.SetForegroundColour('#2186E9')

		self.marcados_items = wx.StaticText(self.painel,-1,u"Marcados: { }", pos=(440, 385))
		self.marcados_items.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.marcados_items.SetForegroundColour('#4279AF')

		wx.StaticText(self.painel,-1,u"Pesquisar por descrição", pos=(15, 430)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de filiais", pos=(443, 430)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.selfilial = wx.ComboBox(self.painel, 100, '', pos=(440, 442), size=(256,27), choices = ['']+login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.selfilial.SetValue( self.p.rfilia.GetValue() if self.p.rfilia.GetValue() else login.ciaRelac[0] )

		self.sem_estoque = wx.CheckBox(self.painel, 101 , u"Produtos sem estoque fisico",  pos=(12,353))
		self.estoque_negativo = wx.CheckBox(self.painel, 102 , u"Produtos com estoque fisico negativo",  pos=(12,377))
		self.estoque_reservas = wx.CheckBox(self.painel, 105 , u"Produtos com estoque de reserva/virtual { opçao independente/individualizado }",  pos=(12,402))

		self.eliminar_cadastro = wx.CheckBox(self.painel, 103 , u"Eliminar produtos marcados no cadastro de produtos",  pos=(550,353))
		self.eliminar_esfisico = wx.CheckBox(self.painel, 104 , u"Eliminar produtos marcados apenas do cadastro de estoque fisico",  pos=(550,377))
		self.eliminar_evirtual = wx.CheckBox(self.painel, 106 , u"Zerar o estoque de reserva/virtual do produto/filial selecionado\nopção independente das duas acima",  pos=(550,400))

		self.sem_estoque.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.estoque_negativo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.estoque_reservas.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.eliminar_cadastro.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.eliminar_esfisico.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.eliminar_evirtual.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.eliminar_cadastro.SetForegroundColour('#FF0000')
		self.eliminar_evirtual.SetForegroundColour('#225E99')

		self.eliminar_esfisico.Enable( False )
		self.eliminar_cadastro.Enable( False )
		self.eliminar_esfisico.SetValue( True )
		
		self.sem_estoque.SetValue( True )
		self.estoque_negativo.SetValue( True )

		self.pesquisa  = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(700,438), size=(38,30))
		voltar = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(750,438), size=(38,30))				
		self.selecall = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/selectall.png", wx.BITMAP_TYPE_ANY), pos=(820,438), size=(38,32))				
		self.executar = wx.BitmapButton(self.painel, 204, wx.Bitmap("imagens/executa.png", wx.BITMAP_TYPE_ANY), pos=(862,438), size=(38,32))				
		self.selecall.Enable( False )
		
		self.consultar = wx.TextCtrl(self.painel, 200, "", pos=(12, 445),size=(420, 25),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)

		self.pesquisa.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.selecall.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.executar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
            
		self.pesquisa.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.selecall.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.executar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		self.pesquisa.Bind(wx.EVT_BUTTON, self.selecionar)
		self.selecall.Bind(wx.EVT_BUTTON, self.marcarDesmarcar)
		self.executar.Bind(wx.EVT_BUTTON, self.finalizarProcedimento)
		self.estoque_reservas.Bind(wx.EVT_CHECKBOX, self.selecionar)
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		
	def sair( self, event ):	self.Destroy()
	def selecionar(self,event):

		self.eliminar_cadastro.Enable( False )
		self.eliminar_cadastro.SetValue( False )
		self.selecall.Enable( False )
		self.permisao_fisico = False

		filial = self.selfilial.GetValue().split('-')[0] if self.selfilial.GetValue() else login.identifi
		conn = sqldb()
		sql  = conn.dbc("Produtos: Controle de estoque e filiais", fil = filial, janela = self.painel )
		
		if sql[0]:
		
			"""  Verifica se o usuario tem permisao para apagar produtos no cadastro de produtos neste modulo  """
			if sql[2].execute("SELECT us_para FROM usuario WHERE us_logi='"+str( login.usalogin )+"'" ):
				
				parametros_usuarios = sql[2].fetchone()[0]
				if len( parametros_usuarios.split(';') ) >= 20 and parametros_usuarios.split(';')[19] == "T":	self.eliminar_cadastro.Enable( True )
				if len( parametros_usuarios.split(';') ) >= 21 and parametros_usuarios.split(';')[20] == "T":
					
					self.selecall.Enable( True )
					self.permisao_fisico = True

			__f = self.selfilial.GetValue().split('-')[0]
			relacao_fisico = "SELECT t1.pd_codi,t1.pd_nome,t1.pd_ulvd,t1.pd_ulcm, t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on (t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_nome!='' ORDER BY t1.pd_nome"

			if self.estoque_reservas.GetValue():	relacao_fisico = relacao_fisico.replace("WHERE","WHERE t2.ef_virtua!=0 and ")
			else:	
				if __f:	relacao_fisico = relacao_fisico.replace("WHERE","WHERE t2.ef_idfili='"+ __f +"' and ")
				if self.sem_estoque.GetValue() and self.estoque_negativo.GetValue():		relacao_fisico = relacao_fisico.replace("WHERE","WHERE t2.ef_fisico<=0 and ")
				else:
					
					if self.sem_estoque.GetValue():	relacao_fisico = relacao_fisico.replace("WHERE","WHERE t2.ef_fisico=0 and ")
					if self.estoque_negativo.GetValue():	relacao_fisico = relacao_fisico.replace("WHERE","WHERE t2.ef_fisico<0 and ")

				if self.consultar.GetValue().strip():	relacao_fisico = relacao_fisico.replace("WHERE","WHERE t1.pd_nome like '"+self.consultar.GetValue().strip()+"%' and ")

			registros = 0
			relacao   = {}

			if sql[2].execute( relacao_fisico ):
				
				for i in sql[2].fetchall():

					ultima_venda = ""
					ultima_compra = ""
					if i[2]:
						
						for uv in i[2].split('\n'):
							
							if uv and uv.split('|') and len( uv.split('|') ) >=3:
								
								ultima_venda = uv.split('|')[2] + ' ' + uv.split('|')[3]
								break

					if i[3]:
						
						for uc in i[3].split('\n'):
							
							if uc and uc.split('|') and len( uc.split('|') ) >=3:
								
								ultima_compra = uc.split('|')[2] + ' ' + uc.split('|')[3]
								break

					relacao[registros] = i[6],i[0],i[1],format( i[4], ',' ),format( i[5], ','),ultima_compra,ultima_venda,''
					
					registros +=1

			self.controle_filiais.SetItemCount( registros )
			ListaControleEstoque.itemDataMap  = relacao
			ListaControleEstoque.itemIndexMap = relacao.keys()

			self.ocorrencias.SetLabel( "Ocorrencias\n{"+str( registros )+"}" )
			self.marcados_items.SetLabel("Marcados: { }")
			conn.cls( sql[1] )
			
	def marcarDesmarcar(self,event):

		if not self.permisao_fisico:
			
			alertas.dia( self, u"Sem permissão para apagar na tabela de estoque fisico...\n"+(" "*120),"Eliminar produtos: { Produtos, Estoque }")
			return
			
		indice = self.controle_filiais.GetFocusedItem()
		fl = self.controle_filiais.GetItem( indice, 0 ).GetText()
		cd = self.controle_filiais.GetItem( indice, 1 ).GetText()

		registros = 0
		relacao   = {}
		items_marcados = 0
		
		rl = self.controle_filiais
		
		if rl.GetItemCount():
			
			filial = self.selfilial.GetValue().split('-')[0] if self.selfilial.GetValue() else login.identifi
			_mensagem = mens.showmsg("Marcar/Desmarcar produtos\n\nAguarde...", filial = filial )

			if event.GetId() == 202 and not self.marcar_desmarcar:

				m = "MARCAR"
				self.marcar_desmarcar = True
				self.selecall.SetBitmapLabel (wx.Bitmap('imagens/unselect.png'))
				self.controle_filiais.SetForegroundColour("#008000")

			elif event.GetId() == 202 and self.marcar_desmarcar:

				m = ""
				self.marcar_desmarcar = False
				self.selecall.SetBitmapLabel (wx.Bitmap('imagens/selectall.png'))
				self.controle_filiais.SetForegroundColour("#000000")

			for i in range( rl.GetItemCount() ):
					
				_f = rl.GetItem(i, 0).GetText()
				_c = rl.GetItem(i, 1).GetText()

				if event.GetId() !=202:	m = rl.GetItem(i, 7).GetText()
				if _f == fl and _c == cd  and event.GetId() !=202:

					if m:	m = ""
					else:	m = "MARCAR"

				if m:	items_marcados +=1
				relacao[registros] = rl.GetItem(i, 0).GetText(),rl.GetItem(i, 1).GetText(),rl.GetItem(i, 2).GetText(),rl.GetItem(i, 3).GetText(),\
				rl.GetItem(i, 4).GetText(),rl.GetItem(i, 5).GetText(),rl.GetItem(i, 6).GetText(), m
				registros +=1

			del _mensagem
			
		self.controle_filiais.SetItemCount( registros )
		ListaControleEstoque.itemDataMap  = relacao
		ListaControleEstoque.itemIndexMap = relacao.keys()

		self.ocorrencias.SetLabel( "Ocorrencias\n{ "+str( registros )+" }" )
		self.marcados_items.SetLabel("Marcados: { "+str( items_marcados )+" }")
	
	def finalizarProcedimento( self, event ):

		if self.controle_filiais.GetItemCount():

			if self.eliminar_evirtual.GetValue():	self.zerarVirtual()
			else:

				"""  Pre-verificao dos items marcardos  """
				verificacao_items, relacao_gravar= self.verificarSelecao()
				if not verificacao_items:	return
				
				tipos = ""
				if self.eliminar_cadastro.GetValue():	tipos += u"Atenção: Opção para apagar produtos estar marcado, esta opção apaga definifitvamente os produtos no banco de dados\nse tiver certeza apenas confirme...\n\n1 - Eliminar no cadastro de produtos { Apagar definitivamente }\n"
				if self.eliminar_esfisico.GetValue():	tipos += "2 - Eliminar no cadastro de estoque   { Apagar definitivamente }"

				if tipos:
					
					fp = wx.MessageDialog(self.painel,"{ Eliminar produtos }\n\n"+tipos+"\n\nConfirme para continuar...\n"+(" "*140),"Eliminar produtos: { Produtos, Estoque }",wx.YES_NO|wx.NO_DEFAULT)
					if fp.ShowModal() ==  wx.ID_YES:
												
						"""  Backup das tabelas """
						ET  = datetime.datetime.now().strftime("%d%m%Y_%T")+"_"+login.usalogin.lower()
						_mensagem = mens.showmsg("Selecionando dados da TABELA de Produtos!!\n\nAguarde...")
						shost,suser,spass,sqlbd,sqlpo = login.spadrao.split(";") #-: Servidor padrao { spadrao.cmd }
						
						if not spass.strip():

							alertas.dia(self.painel,u"Os dados do servidor padrão para o banco de dados, estar faltando informações...\n"+(" "*160),u"Eliminar produtos: { Produtos, Estoque }")
							return
						
						bk_produto = "mysqldump -u%s -p%s sei produtos > %s" %( suser,spass,diretorios.usgerenciador+"produtos_"+str( ET )+".sql" )
						bk_estoque = "mysqldump -u%s -p%s sei estoque > %s" %( suser,spass,diretorios.usgerenciador+"estoque_"+str( ET )+".sql" )

						abrir1 = commands.getstatusoutput( bk_produto )
						abrir2 = commands.getstatusoutput( bk_estoque )
						del _mensagem
						
						if abrir1[0]:
							
							alertas.dia(self.painel,"O sistema não conseguiu fazer o backup do cadastro de produtos...\n\n%s" %(abrir[1])+"\n"+(" "*160),"Eliminar produtos: { Produtos, Estoque }")
							return

						if abrir2[0]:
							
							alertas.dia(self.painel,"O sistema não conseguiu fazer o backup do cadastro de produtos...\n\n%s" %(abrir[1])+"\n"+(" "*160),"Eliminar produtos: { Produtos, Estoque }")
							return

						"""  Gravando em CSV, relacao dos produtos eliminados no estoque fisico  """
						try:
							
							__arquivo = open(diretorios.usgerenciador+"estoque_"+str( ET )+".csv","w")
							__arquivo.write( relacao_gravar.encode("UTF-8") )
							__arquivo.close()
						
						except Exception as _erro:

							if type( _erro ) !=unicode:	_erro = str( _erro )
							alertas.dia(self.painel,"{ Erro na gravação do arquivo CSV }\n\n"+ _erro +"\n"+(" "*160),"AEliminar produtos: { Produtos, Estoque }")
							return
							
							
						"""  Gravacao dos dados em banco  """
						filial = self.selfilial.GetValue().split('-')[0] if self.selfilial.GetValue() else login.identifi
						conn = sqldb()
						sql  = conn.dbc("Produtos: Controle de estoque e filiais", fil = filial, janela = self.painel )
						grv  = True

						if sql[2]:
							
							try:
								
								for i in range( self.controle_filiais.GetItemCount() ):
									
									if self.controle_filiais.GetItem( i, 7).GetText():
										
										filial = self.controle_filiais.GetItem( i, 0).GetText()
										codigo = self.controle_filiais.GetItem( i, 1).GetText()

										apagar_produto = "DELETE FROM produtos WHERE pd_codi='"+ codigo +"'"
										apagar_estoque = "DELETE FROM estoque WHERE ef_idfili='"+ filial +"' and ef_codigo='"+ codigo +"'"
										
										"""  Elimina nas duas tabelas """
										if self.eliminar_cadastro.GetValue():

											sql[2].execute( apagar_produto )
											sql[2].execute( apagar_estoque )
											
										else:	

											"""  Elimina apenas no estoque fisico  """
											if self.eliminar_esfisico.GetValue():	sql[2].execute( apagar_estoque )

								sql[1].commit()

							except Exception as erros:
								
								grv = False
								
								sql[1].rollback()
								if type( erros ) !=unicode:	erros = str( erros )
								
							conn.cls( sql[1] )
						
						if not grv:		alertas.dia( self, u"{ Erro na gravação dos dados no banco }\n\n"+ erros +"\n"+(" "*160),"Eliminar produtos: { Produtos, Estoque }")
						else:	self.selecionar( wx.EVT_BUTTON )
						
				else:	alertas.dia( self, "Selecione uma opcao para continuar...\n"+(" "*120),"Eliminar produtos: { Produtos, Estoque }")

		else:	alertas.dia( self, "A lista de  produtos estar vazia...\n"+(" "*120),"Eliminar produtos: { Produtos, Estoque }")

	def verificarSelecao( self ):

		"""  Pre-verificao dos items marcardos  """
		relacao_gravar = ""
		rlg = self.controle_filiais
						
		verificacao_items = False
		for vf in range( self.controle_filiais.GetItemCount() ):
							
			if self.controle_filiais.GetItem( vf, 7).GetText():

				verificacao_items = True
				relacao_gravar +=rlg.GetItem( vf, 0).GetText()+'|'+rlg.GetItem( vf, 1 ).GetText()+'|'+rlg.GetItem( vf, 3 ).GetText()+'|'+rlg.GetItem( vf, 4).GetText()+'\n'

		if not verificacao_items:	alertas.dia( self, "Nenhum produto selecionado/marcado...\n"+(" "*120),"Eliminar produtos: { Produtos, Estoque }")

		return verificacao_items, relacao_gravar
		
	def zerarVirtual(self):

		if self.estoque_reservas.GetValue() and self.eliminar_evirtual.GetValue():
			
			indice = self.controle_filiais.GetFocusedItem()
			filial = self.controle_filiais.GetItem( indice, 0).GetText()
			codigo = self.controle_filiais.GetItem( indice, 1).GetText()
			pdnome = self.controle_filiais.GetItem( indice, 2).GetText()
			fisico = self.controle_filiais.GetItem( indice, 3).GetText()
			reserv = self.controle_filiais.GetItem( indice, 4).GetText()
			
			if not Decimal( reserv ):

				alertas.dia( self, "Estoque de reserva/virtual estar zerado...\n"+(" "*120),"Zerar estoque reserva/virtual: { Produtos, Estoque }")				
				return
				
			informe = "\n\n       Filia: "+filial+\
			"\n Codigo: "+codigo+\
			"\nProduto: "+pdnome+\
			"\nReserva: "+reserv
			
			zv = wx.MessageDialog(self.painel,"{ Zerar estoque reserva/virtual }\n\n"+ informe +"\n\nConfirme para continuar...\n"+(" "*160),"Zerar estoque reserva/virtual: { Produtos, Estoque }",wx.YES_NO|wx.NO_DEFAULT)
			if zv.ShowModal() ==  wx.ID_YES:

				"""  Gravacao dos dados em banco  """
				filial = self.selfilial.GetValue().split('-')[0] if self.selfilial.GetValue() else login.identifi
				conn = sqldb()
				sql  = conn.dbc("Produtos: Controle de estoque e filiais", fil = filial, janela = self.painel )
				if sql[2]:
					
					listar_reserva = ""
					temporario = sql[2].execute("SELECT tm_codi,tm_quan, tm_logi, tm_lanc, tm_hora, tm_tipo, tm_fili FROM tdavs WHERE tm_codi='"+ codigo +"' and tm_tipo!='O' and tm_tipo!='V'")
					erros = ""
					if not temporario:
						
						try:
							
							zerar = "UPDATE estoque SET ef_virtua='0' WHERE ef_idfili='"+ filial +"' and ef_codigo='"+ codigo+"'"
							sql[2].execute( zerar )
							sql[1].commit()

						except Exception as  erros:

							sql[1].rollback()
						if type( erros ):	erros = str( erros )							
							
					conn.cls( sql[1] )
					
					if erros:	alertas.dia( self, u"{ Erros na atualização }\n\n"+ erros +"\n"+(" "*150),"Zerar estoque reserva/virtual: { Produtos, Estoque }")
					
					if temporario and not erros:
							
						for ev in sql[2].fetchall():

							listar_reserva += ev[6] + '|'+ str( ev[3].strftime("%d/%m/%Y") )+'|'+str( ev[4] )+'|'+str( ev[2 ]) + '|'+str( ev[1] ) + '\n'
	
						if fisico and reserv:	saldo = str( ( Decimal( fisico ) - Decimal( reserv ) ) )
						else:	saldo = ""
						RelacaoReservas.lista = listar_reserva
						RelacaoReservas.infor = "|"+fisico+"|"+reserv+"|"+saldo
						RelacaoReservas.filia = filial
						RelacaoReservas.codig = codigo
						quem_frame=RelacaoReservas(parent=self,id=-1)
						quem_frame.Center()
						quem_frame.Show()
			
					else:	self.selecionar( wx.EVT_BUTTON )
					
		else:	alertas.dia( self, "Marque as duas opções de estoque reserva/virtual...\n"+(" "*120),"Zerar estoque reserva/virtual: { Produtos, Estoque }")
		
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 200:	sb.mstatus("  Procurar/Pesquisar produtos das filiais, filial selecionada",0)
		elif event.GetId() == 201:	sb.mstatus("  Sair - Voltar",0)
		elif event.GetId() == 202:	sb.mstatus("  Selecionar-deselecionar todos os produtos/filiais na lista",0)
		elif event.GetId() == 204:	sb.mstatus(u"  Avançar, executar opções selecionadas",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Genrenciador do estoque fisico das filiais e produtos",0)
		event.Skip()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2E7BC6") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Gerenciardor e controle do estoque fisico das filiais", 0, 448, 90)

		dc.SetTextForeground("#CF1818") 	
		dc.DrawRotatedText(u"ATENÇÃO", 0, 63, 90)

class ListaControleEstoque(wx.ListCtrl):

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
		self.attr1.SetBackgroundColour("#D2D2D2")
		self.attr2.SetBackgroundColour("#D0BBBB")
		self.attr3.SetBackgroundColour("#ECDEDE")

		self.InsertColumn(0, 'Filial',    format=wx.LIST_ALIGN_LEFT,width=90)
		self.InsertColumn(1, 'Codigo', format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(2, 'Descrição dos produtos', width=400)
		self.InsertColumn(3, 'Fisico',  format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(4, 'Reserva', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(5, 'Ultima compra', width=200)
		self.InsertColumn(6, 'Ultima venda',  width=200)
		self.InsertColumn(7, 'Marcar',  width=100)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception as _reTornos:	pass
						

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index = self.itemIndexMap[item]
		fisico = Decimal( self.itemDataMap[index][3].replace(',','') )
		marcar = self.itemDataMap[index][7]

		if marcar:	return self.attr3
		if fisico < 0:	return self.attr2
		if item % 2:	return self.attr1
		else:	return None

	def OnGetItemImage(self, item):
		
		index = self.itemIndexMap[item]
		fisico = Decimal( self.itemDataMap[index][3].replace(',','') )
		marcar = self.itemDataMap[index][7]
		
		if marcar:	return self.i_idx
		if fisico < 0:	return self.e_est
		return self.i_orc

	def GetListCtrl(self):	return self
	def GetSortImages(self):	return (self.sm_dn, self.sm_up)

class RelacionarProdutosPrecompra(wx.Frame):
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.f = formasPagamentos()
		self.grupos = ''
		self.fabric = ''
		
		""" Sem efeito utilizado para vincular um produto na class vincular produtos pedidof.py linha 1471  """
		self.PosicaoAtuale = 0 # Sem efeito utilizado para a funcao de c
		self.ListaCMP = {}

		wx.Frame.__init__(self, parent, id, 'Relacionar produtos para pre-compra', size=(900,480), style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)
		self.Bind(wx.EVT_KEY_UP, self.teclas)
		
		self.previsao_compras = wx.ListCtrl(self.painel, 300,pos=(20,0), size=(880,210),
							style=wx.LC_REPORT
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)

		self.previsao_compras.InsertColumn(0, 'Código',  width=90)
		self.previsao_compras.InsertColumn(1, 'Descrição dos Produtos', width=180)
		self.previsao_compras.InsertColumn(2, 'Compras', format=wx.LIST_ALIGN_LEFT, width=75)
		self.previsao_compras.InsertColumn(3, 'Vendas', format=wx.LIST_ALIGN_LEFT, width=75)
		self.previsao_compras.InsertColumn(4,u'Devoluções', format=wx.LIST_ALIGN_LEFT,width=80)
		self.previsao_compras.InsertColumn(5, 'Saldo-vendas', format=wx.LIST_ALIGN_LEFT, width=80)
		self.previsao_compras.InsertColumn(6, 'Vendas-dia', format=wx.LIST_ALIGN_LEFT,width=80)
		self.previsao_compras.InsertColumn(7,u'Físico', format=wx.LIST_ALIGN_LEFT,width=75)
		self.previsao_compras.InsertColumn(8,u'Previsão', format=wx.LIST_ALIGN_LEFT,width=80)
		self.previsao_compras.InsertColumn(9,u'Sugestão', format=wx.LIST_ALIGN_LEFT,width=75)
		self.previsao_compras.InsertColumn(10,u'Paletes', width=80)
		self.previsao_compras.InsertColumn(11,u'Unidade', format=wx.LIST_ALIGN_TOP,width=80)
		self.previsao_compras.InsertColumn(12,u'Dados', width=80)

		self.previsao_compras.InsertColumn(13,u'Media-compra', format=wx.LIST_ALIGN_LEFT,width=80)
		self.previsao_compras.InsertColumn(14,u'Media-custo', format=wx.LIST_ALIGN_LEFT,width=80)
		self.previsao_compras.InsertColumn(15,u'Ultimo-compra', format=wx.LIST_ALIGN_LEFT,width=80)
		self.previsao_compras.InsertColumn(16,u'Ultimo-custo', format=wx.LIST_ALIGN_LEFT,width=80)

		self.previsao_compras.InsertColumn(17,u'Sugestão antes do ajuste do palete', format=wx.LIST_ALIGN_LEFT,width=300)
		self.previsao_compras.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.previsao_compras.SetBackgroundColour("#9BB3CA")
							
		self.previsao_compras.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.TlNum )

		self.ListaProdutos = wx.ListCtrl(self.painel, -1,pos=(20,242), size=(842,140),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaProdutos.InsertColumn(0, 'Item',  width=40)
		self.ListaProdutos.InsertColumn(1, 'Código', format=wx.LIST_ALIGN_LEFT,width=115)
		self.ListaProdutos.InsertColumn(2, 'Descrição dos Produtos', width=400)
		self.ListaProdutos.InsertColumn(3, 'UN', format=wx.LIST_ALIGN_TOP, width=30)
		self.ListaProdutos.InsertColumn(4, 'Estoque fisico', format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaProdutos.InsertColumn(5, 'Grupo', width=110)
		self.ListaProdutos.InsertColumn(6, 'Fabricante', width=110)
		self.ListaProdutos.InsertColumn(7, 'Dados', width=110)
		self.ListaProdutos.InsertColumn(8, 'Paletes', width=110)
		self.ListaProdutos.InsertColumn(9, 'Apuracao do fisico para relatorio sem filiais', width=2000)
		self.ListaProdutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ListaProdutos.SetBackgroundColour("#DCDCF1")

		wx.StaticText(self.painel,-1,u"Período de vendas/compras", pos=(20, 390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Selecione uma filial", pos=(282, 390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Consulta de produtos para adicionar na lista acima", pos=(22, 437)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Previsão de compra", pos=(770,390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Duplo click para alterar a quantidade para sugestão de compra do produto acima selecionado", pos=(20,228)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.media_venda = wx.StaticText(self.painel,-1,u"Dias de venda: {}", pos=(20,212))
		self.media_venda.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.media_venda.SetForegroundColour('#21588E')

		self.data_inicial = wx.DatePickerCtrl(self.painel, -1, pos=(20,403), size=(120,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.data_final = wx.DatePickerCtrl(self.painel, -1, pos=(150,403), size=(120,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.rfiliao = wx.ComboBox(self.painel, -1, self.p.fid +'-'+ login.filialLT[self.p.fid][14], pos=(280, 403), size=(238,27), choices = [''] + login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.descricao  = wx.TextCtrl(self.painel,-1,'',pos=(20,450), size=(460,25), style=wx.TE_PROCESS_ENTER)

		self.selecionar_grupo = wx.RadioButton(self.painel,501,"Selecionar por grupo ",     pos=(530,390))
		self.selecionar_fabricante = wx.RadioButton(self.painel,504,"Selecionar por fabricante", pos=(530,415))
		self.selecionar_grupo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.selecionar_fabricante.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.selecao  = wx.ComboBox(self.painel, 601, '',  pos=(530, 447), size=(230,27), choices = '')
		self.previsao = wx.ComboBox(self.painel, 602, '',  pos=(769, 403), size=(132,27), choices = [u'1 Mês',u'2 Mêses',u'3 Mêses',u'4 Mêses',u'5 Mêses',u'6 Mêses',u'7 Mêses',u'8 Mêses',u'9 Mêses',u'10 Mêses',u'11 Mêses',u'12 Mêses'])

		self.enviar_orcamento = GenBitmapTextButton(self.painel,233,label=u'   E n v i a r para o orçamento de compra', pos=(600,212),size=(300,27), bitmap=wx.Bitmap("imagens/import16.png", wx.BITMAP_TYPE_ANY))
		self.enviar_orcamento.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.consultar_descricao = wx.BitmapButton(self.painel, 229, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(482,449), size=(36,26))

		self.gerar_compra = wx.BitmapButton(self.painel, 228, wx.Bitmap("imagens/cima20.png",    wx.BITMAP_TYPE_ANY), pos=(865,240), size=(36,36))
		self.apagar_todo  = wx.BitmapButton(self.painel, 226, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(865,306), size=(36,36))
		self.apagar_item  = wx.BitmapButton(self.painel, 227, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(865,346), size=(36,36))

		self.enviar_grupo_fabricantes = GenBitmapTextButton(self.painel,230,label=' E n v i a r\n Grupo-Fabricante', pos=(770,442),size=(131,35), bitmap=wx.Bitmap("imagens/ok16.png", wx.BITMAP_TYPE_ANY))
		self.enviar_grupo_fabricantes.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.selecionar_grupo.Bind(wx.EVT_RADIOBUTTON, self.selecionarGruposFabricantes)
		self.selecionar_fabricante.Bind(wx.EVT_RADIOBUTTON, self.selecionarGruposFabricantes)
		self.enviar_grupo_fabricantes.Bind(wx.EVT_BUTTON, self.relacionarGruposFabricantes)
		
		self.apagar_todo.Bind(wx.EVT_BUTTON, self.apagarItems)
		self.apagar_item.Bind(wx.EVT_BUTTON, self.apagarItems)
		self.descricao.Bind(wx.EVT_TEXT_ENTER, self.vincularProduto)
		self.consultar_descricao.Bind(wx.EVT_BUTTON, self.vincularProduto)
		self.gerar_compra.Bind(wx.EVT_BUTTON, self.selecionarComprasVendas)
		self.enviar_orcamento.Bind(wx.EVT_BUTTON, self.enviarOrcamento )
		self.previsao.Bind(wx.EVT_COMBOBOX, self.selecionarComprasVendas)
		
		self.selecaoGrupoFabricante()

		self.consultar_descricao.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gerar_compra.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.apagar_todo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.apagar_item.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.enviar_grupo_fabricantes.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.consultar_descricao.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.gerar_compra.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.apagar_todo.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.apagar_item.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.enviar_grupo_fabricantes.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
			
	def selecaoGrupoFabricante(self):
		
		conn = sqldb()
		sql  = conn.dbc("Cadastro de Produtos, grupos/fabricantes...", fil = self.p.fid, janela = self.painel )
		
		if sql[0]:	
				
			self.grupos, self.subgr1, self.subgr2, self.fabric, self.endere, self.unidad, self.enddep = self.f.prdGrupos( sql[2] )
			conn.cls(sql[1])

			self.selecionarGruposFabricantes(wx.EVT_RADIOBUTTON)
			
	def selecionarGruposFabricantes(self,event):

		self.selecao.SetItems('')
		self.selecao.SetValue('')
		
		if self.selecionar_grupo.GetValue():	self.selecao.SetItems(self.grupos)		
		if self.selecionar_fabricante.GetValue():	self.selecao.SetItems(self.fabric)		

	def teclas(self,event):
		
		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		__id     = 0
		if controle !=None:	__id = controle.GetId()
		
		if controle !=None and __id == 601 and self.selecionar_grupo.GetValue():	self.selecao.SetItems( nF.retornaLista( 1, self.grupos, self.selecao.GetValue() ) )
		if controle !=None and __id == 601 and self.selecionar_fabricante.GetValue():	self.selecao.SetItems( nF.retornaLista( 1, self.fabric, self.selecao.GetValue() ) )

	def TlNum(self,event):

		TelNumeric.decimais = 4
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		indice = self.previsao_compras.GetFocusedItem()
		if Decimal( valor ):	self.previsao_compras.SetStringItem( indice, 9, format( Decimal( valor ),'.4f' ) )
		else:	self.previsao_compras.SetStringItem( indice, 9, '' )
		
	def relacionarGruposFabricantes( self, event ):	self.relacionarGruposFabricantesItems( event.GetId(), codigo = "" )
	def relacionarGruposFabricantesItems(self, __id, codigo = "" ):

		if not __id == 90000 and not self.selecao.GetValue():	alertas.dia(self,"Selecione um grupo ou fabricante valido...\n"+(" "*140),u"Selecionar grupos-fabricantes")
		else:

			if not self.rfiliao.GetValue():

				avancar = wx.MessageDialog(self,u"{ Apuração do estoque físico sem escolha de filial }\n\n1-O sistema vai consolidar os estoques das filiais localizadas...\n\nConfirme para continuar\n"+(" "*160),u"Sugestão de compras",wx.YES_NO|wx.NO_DEFAULT)
				if not avancar.ShowModal() ==  wx.ID_YES:	return
				
			filial = self.rfiliao.GetValue().split('-')[0] if self.rfiliao.GetValue() else self.p.fid
			
			conn = sqldb()
			sql  = conn.dbc("Cadastro de Produtos, grupos/fabricantes...", fil = filial, janela = self.painel )
			
			lista = []
			
			if sql[0]:	

				if self.selecionar_grupo.GetValue():	pesquisar = "SELECT pd_codi,pd_nome,pd_unid,pd_nmgr,pd_fabr, pd_pcom, pd_pcus, pd_tpr1, pd_para FROM produtos WHERE pd_nmgr='" + self.selecao.GetValue().upper() + "' ORDER BY pd_nome"
				if self.selecionar_fabricante.GetValue():	pesquisar = "SELECT pd_codi,pd_nome,pd_unid,pd_nmgr,pd_fabr, pd_pcom, pd_pcus, pd_tpr1, pd_para FROM produtos WHERE pd_fabr='" + self.selecao.GetValue().upper() + "' ORDER BY pd_nome"
				if __id == 90000:	pesquisar = "SELECT pd_codi,pd_nome,pd_unid,pd_nmgr,pd_fabr, pd_pcom, pd_pcus, pd_tpr1, pd_para FROM produtos WHERE pd_codi='" + codigo + "' ORDER BY pd_nome"
				
				sql[2].execute( pesquisar )
				resul = sql[2].fetchall()

				for i in resul:
					
					entrar = True
					fisico = Decimal('0.0000')
					apurar = ""
					if self.rfiliao.GetValue():
						
						if sql[2].execute("SELECT ef_fisico FROM estoque WHERE ef_codigo='"+ i[0] +"' and ef_idfili='" +filial+ "'"):	fisico = sql[2].fetchone()[0]
						else:	entrar = False

					else: #//Apuracao do estoque sem filial, o sistema consolida os estoques das filiais

						if sql[2].execute("SELECT ef_fisico,ef_idfili FROM estoque WHERE ef_codigo='"+ i[0] +"'"):
							
							for f in sql[2].fetchall():
								
								fisico +=f[0]
								apurar +="Filial: "+f[1]+" fisico: "+str( f[0] )+"   "
						
					paletes = i[8].split('|')[9] if i[8] and len( i[8].split('|') ) >= 10 else ""

					if entrar:	lista.append( i[0] +'|'+ i[1] +'|'+ i[2] +'|'+ i[3] +'|'+ i[4] +'|'+ str( fisico ) +'|'+ str( i[5] ) +'|'+ str( i[6] ) +'|'+ str( i[7] ) +'|'+ paletes +'|'+ apurar )
						
				conn.cls(sql[1])

			if lista:

				lista_produtos = self.ListaProdutos
				indice = self.ListaProdutos.GetItemCount()
				ordem  = self.ListaProdutos.GetItemCount() + 1
				for i in lista:
					
					p = i.split('|')
					if self.verificaDuplicidade( p[0], lista_produtos ):

						f = p[5] if Decimal( p[5] ) else ""
						self.ListaProdutos.InsertStringItem( indice, str( ordem ).zfill(3) )
						self.ListaProdutos.SetStringItem( indice, 1, p[0] )	
						self.ListaProdutos.SetStringItem( indice, 2, p[1] )	
						self.ListaProdutos.SetStringItem( indice, 3, p[2] )	
						self.ListaProdutos.SetStringItem( indice, 4, f )	
						self.ListaProdutos.SetStringItem( indice, 5, p[3] )	
						self.ListaProdutos.SetStringItem( indice, 6, p[4] )
						self.ListaProdutos.SetStringItem( indice, 7, p[6]+'|'+p[7]+'|'+p[8] )
						self.ListaProdutos.SetStringItem( indice, 8, p[9] )
						self.ListaProdutos.SetStringItem( indice, 9, p[10] )
						if indice % 2:	self.ListaProdutos.SetItemBackgroundColour(indice, "#E6E6FA")
						
						indice +=1
						ordem  +=1

	def verificaDuplicidade(self, codigo, lista ):
		
		r = True
		if lista.GetItemCount():
			
			for i in range( lista.GetItemCount() ):

				if codigo == lista.GetItem( i, 1 ).GetText():	r = False

		return r

	def apagarItems( self, event ):

		apagar = "Apagar o produto selecionado"
		if event.GetId() == 226:	apagar = "Apagar todos os produtos"
		
		__ap = wx.MessageDialog(self, apagar + "\n\nConfirme para continuar...\n"+(" "*140),u"Eliminar produto(s) da lista",wx.YES_NO|wx.NO_DEFAULT)
		if __ap.ShowModal() ==  wx.ID_YES:
			
			"""  Apagar item selecionado  """
			if event.GetId() == 227:
				
				self.ListaProdutos.DeleteItem( self.ListaProdutos.GetFocusedItem() )
				self.ListaProdutos.Refresh()

				for i in range( self.ListaProdutos.GetItemCount() ):
					
					self.ListaProdutos.SetStringItem( i, 0, str( i + 1 ).zfill(3) )	

				self.ListaProdutos.Refresh()

			"""  Apagar todos os items  """
			if event.GetId() == 226:
				
				self.ListaProdutos.DeleteAllItems()
				self.ListaProdutos.Refresh()

	def vincularProduto(self,event):

		vinculacdxml.rlFilial = self.rfiliao.GetValue().split('-')[0] if self.rfiliao.GetValue() else self.p.fid
		vinculacdxml.modulo_chamador = 2
		vlp_frame=vinculacdxml(parent=self,id=-1)
		vlp_frame.Centre()
		vlp_frame.Show()

	def gravarTemporario(self, __cd ):	self.relacionarGruposFabricantesItems( 90000, codigo = __cd )

	def selecionarComprasVendas(self,event):

		if not self.ListaProdutos.GetItemCount():	alertas.dia(self, "Lista de produtos vazia...\n"+(" "*120),"Gerar pedido de pre-compra")
		elif not self.previsao.GetValue():	alertas.dia(self, u"Selecione previsão para pre-compras em mêses...\n"+(" "*120),"Gerar pedido de pre-compra")
		else:

			inicial = datetime.datetime.strptime(self.data_inicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			final   = datetime.datetime.strptime(self.data_final.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

			di = datetime.datetime.strptime(self.data_inicial.GetValue().FormatDate(),'%d-%m-%Y')
			df = datetime.datetime.strptime(self.data_final.GetValue().FormatDate(),'%d-%m-%Y')
			nd = ( int( self.previsao.GetValue().split(' ')[0] ) * 30 ) #Previsao de compras em dias
				
			intervalo = inicial+" - "+final 
			inicio, fim = [datetime.datetime.strptime(data.strip(), '%d/%m/%Y') for data in intervalo.split('-')]
			meses = (fim.year - inicio.year) * 12 + fim.month - inicio.month + 1
			dias = abs((di - df).days + 1 )
			self.media_venda.SetLabel("Dias de venda: { "+ str( dias )+" }")
			
			if intervalo <= 25:	meses = 0
			
			filial = self.rfiliao.GetValue().split('-')[0] if self.rfiliao.GetValue() else self.p.fid
				
			conn = sqldb()
			sql  = conn.dbc("Gerando sugestão de compras...", fil = filial, janela = self.painel )

			if sql[0]:
				
				indice = 0
				self.previsao_compras.DeleteAllItems()
				self.previsao_compras.Refresh()
				
				for i in range( self.ListaProdutos.GetItemCount() ):
					
					codigo  = self.ListaProdutos.GetItem( i, 1).GetText()
					nome    = self.ListaProdutos.GetItem( i, 2).GetText()
					unidade = self.ListaProdutos.GetItem( i, 3).GetText()
					dados   = self.ListaProdutos.GetItem( i, 7).GetText()
					paletes = self.ListaProdutos.GetItem( i, 8).GetText()

					fisico = Decimal( self.ListaProdutos.GetItem( i, 4).GetText() ) if self.ListaProdutos.GetItem( i, 4).GetText() else Decimal('0.0000')
					
					quantidade_compra, quantidade_vendas, quantidade_devolucao, media_precocompra, media_precocustos, ultimo_compra, ultimo_custos = self.levantarDados( codigo, sql )
					
					saldo_vendas = ( quantidade_vendas - quantidade_devolucao )
					vendas_ndias = Decimal( format( ( saldo_vendas / dias ),'.4f' ) )
					previsao_compras = Decimal( format( ( vendas_ndias * nd ),'.0f' )+'.0000' )
					sugestao_compras = sugestao = Decimal( format( ( previsao_compras - fisico ),'.0f')+'.0000' )

					if quantidade_compra <=0:	quantidade_compra= ""
					if quantidade_vendas <=0:	quantidade_vendas = ""	
					if quantidade_devolucao <=0:	quantidade_devolucao = ""
					if saldo_vendas <=0:	saldo_vendas = ""
					if vendas_ndias	<=0:	vendas_ndias = ""
					if fisico <=0:	fisico = ""
					if previsao_compras <=0:	previsao_compras = ""
					if sugestao_compras <=0:	sugestao_compras = ""

					dv = ""
					if paletes and sugestao_compras:
						
						qp = Decimal( format( ( Decimal( sugestao_compras ) / Decimal( paletes ) ),'.0f' ) )
						dv = format( ( Decimal( sugestao_compras ) / Decimal( paletes ) ),'.4f' )
						if qp < 0:	qp = Decimal('1.0000')
						sugestao_compras = format( ( Decimal( paletes ) * qp ),'.4f')

					if sugestao_compras and not Decimal( sugestao_compras ):	sugestao_compras = ""
					
					self.previsao_compras.InsertStringItem( indice, codigo )
					self.previsao_compras.SetStringItem( indice, 1, nome )	
					self.previsao_compras.SetStringItem( indice, 2, str( quantidade_compra ) )	
					self.previsao_compras.SetStringItem( indice, 3, str( quantidade_vendas ) )	
					self.previsao_compras.SetStringItem( indice, 4, str( quantidade_devolucao ) )	
					self.previsao_compras.SetStringItem( indice, 5, str( saldo_vendas ) )	
					self.previsao_compras.SetStringItem( indice, 6, str( vendas_ndias ) )	
					self.previsao_compras.SetStringItem( indice, 7, str( fisico ) )	
					self.previsao_compras.SetStringItem( indice, 8, str( previsao_compras )+' '+unidade if previsao_compras else '' )	
					self.previsao_compras.SetStringItem( indice, 9, str( sugestao_compras ) )
					self.previsao_compras.SetStringItem( indice,10, paletes )
					self.previsao_compras.SetStringItem( indice,11, unidade )
					self.previsao_compras.SetStringItem( indice,12, dados )

					self.previsao_compras.SetStringItem( indice,13, media_precocompra )
					self.previsao_compras.SetStringItem( indice,14, media_precocustos )
					self.previsao_compras.SetStringItem( indice,15, ultimo_compra )
					self.previsao_compras.SetStringItem( indice,16, ultimo_custos )
					
					self.previsao_compras.SetStringItem( indice,17, "Divisao do palete: { "+str( dv )+" }  Sugestao: "+str( sugestao ) )

					if indice % 2:	self.previsao_compras.SetItemBackgroundColour(indice, "#A3BBD3")

					indice +=1

	def levantarDados( self, codigo, sql ):
		
		inicial = datetime.datetime.strptime(self.data_inicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		final   = datetime.datetime.strptime(self.data_final.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

		"""  Totaliza compras no periodo  """
		comprados = sql[2].execute("SELECT ic_quanti, ic_quncom, ic_vcusto  FROM iccmp WHERE ic_lancam >='"+str( inicial )+"' and ic_lancam <='"+str( final )+"' and ic_cdprod='"+ str( codigo )+"' and ic_cancel!='1'")
		__cpr = sql[2].fetchall()

		compras = Decimal('0.0000')
		compras_quantidade = 0

		_precocompra = Decimal('0.0000')
		_precocustos = Decimal('0.0000')
		ultimo_compra = ""
		ultimo_custos = ""

		"""  Totaliza vendas no periodo  """
		vendedidos = sql[2].execute("SELECT  SUM(it_quan) FROM idavs WHERE it_lanc >='"+str( inicial )+"' and it_lanc <='"+str( final )+"' and it_codi='"+ str( codigo )+"' and it_canc!='1'")
		vendas = sql[2].fetchone()[0]

		"""  Totaliza devolucao de vendas no periodo  """
		vendedidos = sql[2].execute("SELECT  SUM(it_quan) FROM didavs WHERE it_lanc >='"+str( inicial )+"' and it_lanc <='"+str( final )+"' and it_codi='"+ str( codigo )+"' and it_canc!='1'")
		devolucao = sql[2].fetchone()[0]
		
		for pc in __cpr:
			
			compras +=pc[0]
			_precocompra +=pc[1] 
			_precocustos +=pc[2]
			
			if compras_quantidade == ( comprados - 1 ):

				ultimo_compra = format( pc[1], '.2f' )
				ultimo_custos = format( pc[2], '.2f' )

			compras_quantidade +=1

		if not compras:	compras = Decimal('0.0000')
		if not vendas:	vendas = Decimal('0.0000')
		if not devolucao:	devolucao = Decimal('0.0000')

		media_precocompra = format( ( _precocompra / compras_quantidade ), '.2f' ) if compras_quantidade and _precocompra else ""
		media_precocustos = format( ( _precocustos / compras_quantidade ), '.2f' ) if compras_quantidade and _precocustos else ""
		
		return compras, vendas, devolucao, media_precocompra, media_precocustos, ultimo_compra, ultimo_custos

	def desenho(self,event):
			
		dc = wx.PaintDC(self.painel)     

		dc.SetTextForeground("#24588B") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Relatorio para previsão de comrpas", 3, 477, 90)
		dc.DrawRotatedText(u"sugestão de compras".upper(), 3, 240, 90)

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 229:	sb.mstatus(u"  Procurar por um produto",0)
		elif event.GetId() == 228:	sb.mstatus(u"  Gerar o relatório  de sugestão de compras",0)
		elif event.GetId() == 227:	sb.mstatus(u"  Apaga o produto selecionado na relação de produtos",0)
		elif event.GetId() == 226:	sb.mstatus(u"  Apaga todos os produtos na relação de produtos",0)
		elif event.GetId() == 230:	sb.mstatus(u"  Enviar produtos para a relação p/grupo e fabricante",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus(u"  Produtos-compras: Relatorio para sugestão de compras",0)

		event.Skip()

	def enviarOrcamento( self, event ):

		if self.previsao_compras.GetItemCount():
			
			gerar_compra = wx.MessageDialog( self, u"Confirme para geração do orçamento de compras...\n"+(" "*120),"Compras: Fechamento",wx.YES_NO|wx.NO_DEFAULT)
			if gerar_compra.ShowModal() ==  wx.ID_YES:

				ordems = 1
				indice = 0
				geral_produtos = Decimal('0.00')
				self.p.ListaCMP.DeleteAllItems()
				self.p.ListaCMP.Refresh()
				
				for i in range( self.previsao_compras.GetItemCount() ):
					
					codigo     = self.previsao_compras.GetItem( i, 0  ).GetText()
					nome       = self.previsao_compras.GetItem( i, 1  ).GetText()
					quantidade = self.previsao_compras.GetItem( i, 9  ).GetText().split(' ')[0]
					unidade    = self.previsao_compras.GetItem( i, 11 ).GetText()
					precocompra, precocusto, precovenda = self.previsao_compras.GetItem( i, 12 ).GetText().split('|')

					if quantidade and Decimal( quantidade ):
						
						valor_total = ( Decimal( precocompra ) * Decimal ( quantidade )  )

						self.p.ListaCMP.InsertStringItem( indice,"-E-"+str(ordems).zfill(3)) #-: Incluir um novo produto
						self.p.ListaCMP.SetStringItem( indice, 1, codigo ) #--: Codigo
						self.p.ListaCMP.SetStringItem( indice, 3, nome  ) #---: Descricao do Produto
						self.p.ListaCMP.SetStringItem( indice, 4, quantidade) # Quantidade
						self.p.ListaCMP.SetStringItem( indice, 5, unidade ) #-: Unidade
						self.p.ListaCMP.SetStringItem( indice, 6, precocompra ) #-: Valor da Unidade
						self.p.ListaCMP.SetStringItem( indice, 7, format( valor_total,'.2f' ) ) #-: Valor Total do Produto
						self.p.ListaCMP.SetStringItem( indice, 8, precovenda ) #-: Valor Total do Produto
														
						self.p.ListaCMP.SetStringItem( indice, 24, '0.00')	#-----: Valor do ICMS ST
						self.p.ListaCMP.SetStringItem( indice, 29, '0.00')	#-----: Valor do ICMS ST
						self.p.ListaCMP.SetStringItem( indice, 33, '0.00')	#-----: Valor do ICMS ST
						self.p.ListaCMP.SetStringItem( indice, 37, '0.00')	#-----: Valor do ICMS ST
						self.p.ListaCMP.SetStringItem( indice, 41, codigo )	#-----: Valor do ICMS ST
						self.p.ListaCMP.SetStringItem( indice, 42, precocusto )	#-----: Valor do ICMS ST
						indice +=1
						geral_produtos +=valor_total
						ordems +=1

				if self.p.ListaCMP.GetItemCount():

					self.p.TTprodu.SetValue( format( Decimal( format( geral_produtos,'.2f') ), ',' ) )
					self.p.Tvnotaf.SetValue( format( Decimal( format( geral_produtos,'.2f') ), ',' ) )
					self.p.recalculaST()

					self.p.impxml.Disable()
					self.p.pedido.Disable()
					self.p.devolu.Disable()
					self.p.transf.Disable()
					self.p.orcame.Disable()
					self.p.acerto.Disable()
					self.p.flTrans.Disable()
					self.p.orcame.SetValue( True )
					self.p.data_entrega.Enable( True )
					
					self.sair(wx.EVT_CLOSE)

	def sair( self, event ):	self.Destroy()
