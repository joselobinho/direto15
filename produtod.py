#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Jose de almeida lobinho 30/10/2017 8:50
import wx
import time
import datetime
import commands

from decimal  import *
from conectar import sqldb,diretorios,login,menssagem,dialogos,sbarra,formasPagamentos,numeracao,TelNumeric, PrinterSocket, MostrarHistorico, gerenciador
from produtof import vinculacdxml,fornecedores
from bdavs import RelacaoReservas

from wx.lib.buttons import GenBitmapTextButton

mens = menssagem()
sb   = sbarra()
nF   = numeracao()
alertas = dialogos()
formas = formasPagamentos()
psk = PrinterSocket()

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
			fisico = self.controle_filiais.GetItem( indice, 3).GetText().replace(',','')
			reserv = self.controle_filiais.GetItem( indice, 4).GetText().replace(',','')
			
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

		wx.Frame.__init__(self, parent, id, 'Relacionar produtos para pre-compra', size=(900,520), style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
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
		wx.StaticText(self.painel,-1,u"Consulta de fornecedores", pos=(22, 477)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Previsão de compra", pos=(770,390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Duplo click para alterar a quantidade para sugestão de compra do produto acima selecionado", pos=(20,228)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.media_venda = wx.StaticText(self.painel,-1,u"Dias de venda: {}", pos=(20,212))
		self.media_venda.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.media_venda.SetForegroundColour('#21588E')

		self.data_inicial = wx.DatePickerCtrl(self.painel, -1, pos=(20,403), size=(120,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.data_final = wx.DatePickerCtrl(self.painel, -1, pos=(150,403), size=(120,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.rfiliao = wx.ComboBox(self.painel, -1, self.p.fid +'-'+ login.filialLT[self.p.fid][14], pos=(280, 403), size=(238,27), choices = [''] + login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.descricao = wx.TextCtrl(self.painel,-1,'',pos=(20,450), size=(460,25), style=wx.TE_PROCESS_ENTER)
		self.fornecedo = wx.TextCtrl(self.painel,-1,'',pos=(20,490), size=(360,25), style=wx.TE_PROCESS_ENTER)

		self.selecionar_grupo = wx.RadioButton(self.painel,501,"Selecionar por grupo ",     pos=(530,390))
		self.selecionar_fabricante = wx.RadioButton(self.painel,504,"Selecionar por fabricante", pos=(530,415))
		self.selecionar_subgrupo1 = wx.RadioButton(self.painel,505,"Selecionar por sub-grupo 1", pos=(530,440))
		self.selecionar_subgrupo2 = wx.RadioButton(self.painel,506,"Selecionar por sub-grupo 2", pos=(530,465))
		self.selecionar_endereco  = wx.RadioButton(self.painel,505,"Selecionar por endereco", pos=(530,490))

		self.selecionar_grupo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.selecionar_fabricante.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.selecionar_subgrupo1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.selecionar_subgrupo2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.selecionar_endereco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.selecao  = wx.ComboBox(self.painel, 601, '',  pos=(698, 487), size=(208,27), choices = '')
		self.previsao = wx.ComboBox(self.painel, 602, '',  pos=(769, 403), size=(132,27), choices = [u'1 Mês',u'2 Mêses',u'3 Mêses',u'4 Mêses',u'5 Mêses',u'6 Mêses',u'7 Mêses',u'8 Mêses',u'9 Mêses',u'10 Mêses',u'11 Mêses',u'12 Mêses'])

		self.enviar_orcamento = GenBitmapTextButton(self.painel,233,label=u'   E n v i a r para o orçamento de compra', pos=(600,212),size=(300,27), bitmap=wx.Bitmap("imagens/import16.png", wx.BITMAP_TYPE_ANY))
		self.enviar_orcamento.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.consultar_descricao = wx.BitmapButton(self.painel, 229, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(482,449), size=(36,26))

		self.gerar_compra = wx.BitmapButton(self.painel, 228, wx.Bitmap("imagens/cima20.png",    wx.BITMAP_TYPE_ANY), pos=(865,240), size=(36,36))
		self.apagar_todo  = wx.BitmapButton(self.painel, 226, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(865,306), size=(36,36))
		self.apagar_item  = wx.BitmapButton(self.painel, 227, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(865,346), size=(36,36))

		self.enviar_grupo_fabricantes = GenBitmapTextButton(self.painel,230,label=' E n v i a r\n Grupos e/ou outros', pos=(770,442),size=(131,35), bitmap=wx.Bitmap("imagens/ok16.png", wx.BITMAP_TYPE_ANY))
		self.enviar_fornecedores = GenBitmapTextButton(self.painel,230,label=' Pesquisar\n Fornecedores', pos=(388,482),size=(131,35), bitmap=wx.Bitmap("imagens/ok16.png", wx.BITMAP_TYPE_ANY))
		self.enviar_grupo_fabricantes.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.enviar_fornecedores.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.selecionar_grupo.Bind(wx.EVT_RADIOBUTTON, self.selecionarGruposFabricantes)
		self.selecionar_fabricante.Bind(wx.EVT_RADIOBUTTON, self.selecionarGruposFabricantes)
		self.selecionar_subgrupo1.Bind(wx.EVT_RADIOBUTTON, self.selecionarGruposFabricantes)
		self.selecionar_subgrupo2.Bind(wx.EVT_RADIOBUTTON, self.selecionarGruposFabricantes)
		self.selecionar_endereco.Bind(wx.EVT_RADIOBUTTON, self.selecionarGruposFabricantes)
		
		self.enviar_grupo_fabricantes.Bind(wx.EVT_BUTTON, self.relacionarGruposFabricantes)
		
		self.apagar_todo.Bind(wx.EVT_BUTTON, self.apagarItems)
		self.apagar_item.Bind(wx.EVT_BUTTON, self.apagarItems)
		self.descricao.Bind(wx.EVT_TEXT_ENTER, self.vincularProduto)
		self.consultar_descricao.Bind(wx.EVT_BUTTON, self.vincularProduto)
		self.gerar_compra.Bind(wx.EVT_BUTTON, self.selecionarComprasVendas)
		self.enviar_orcamento.Bind(wx.EVT_BUTTON, self.enviarOrcamento )
		self.previsao.Bind(wx.EVT_COMBOBOX, self.selecionarComprasVendas)

		self.fornecedo.Bind(wx.EVT_TEXT_ENTER, self.fornecedoresPesquisar)
		self.enviar_fornecedores.Bind(wx.EVT_BUTTON, self.fornecedoresPesquisar)
		
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

	def fornecedoresPesquisar(self,event):
	    
		fornecedores.pesquisa = True

		fornecedores.nmFornecedor = self.fornecedo.GetValue().upper().strip()
		fornecedores.NomeFilial   = self.p.fid
		fornecedores.transportar  = True
	    
		arq_frame=fornecedores(parent=self, id=-1 )
		arq_frame.Centre()
		arq_frame.Show()

	def retornoFornecedor( self, __id, __dc, __nm, __cg, __cm ):
	    
	    if __dc.strip():
		self.relacionarGruposFabricantesItems( 90001, codigo = __dc )
	    else:	alertas.dia(self,'Fornecedor sem numero de documento cpf/cnpj...'+'\n'+(' '*130),'Fornecedor')
	    
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

		if self.selecionar_subgrupo1.GetValue():	self.selecao.SetItems(self.subgr1)
		if self.selecionar_subgrupo2.GetValue():	self.selecao.SetItems(self.subgr2)
		if self.selecionar_endereco.GetValue():	self.selecao.SetItems(self.endere)

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

		if __id not in [90000,90001] and not self.selecao.GetValue():	alertas.dia(self,"Selecione um grupo ou fabricante valido...\n"+(" "*140),u"Selecionar grupos-fabricantes")
		else:

			if not self.rfiliao.GetValue():

				avancar = wx.MessageDialog(self,u"{ Apuração do estoque físico sem escolha de filial }\n\n1-O sistema vai consolidar os estoques das filiais localizadas...\n\nConfirme para continuar\n"+(" "*160),u"Sugestão de compras",wx.YES_NO|wx.NO_DEFAULT)
				if not avancar.ShowModal() ==  wx.ID_YES:	return
				
			filial = self.rfiliao.GetValue().split('-')[0] if self.rfiliao.GetValue() else self.p.fid
			
			conn = sqldb()
			sql  = conn.dbc("Cadastro de Produtos, grupos/fabricantes...", fil = filial, janela = self.painel )
			
			lista = []
			if __id!=90000:	self.ListaProdutos.DeleteAllItems()
			if sql[0]:	

				if self.selecionar_grupo.GetValue():	pesquisar = "SELECT pd_codi,pd_nome,pd_unid,pd_nmgr,pd_fabr, pd_pcom, pd_pcus, pd_tpr1, pd_para,pd_ende FROM produtos WHERE pd_nmgr='" + self.selecao.GetValue().upper() + "' ORDER BY pd_nome"
				if self.selecionar_fabricante.GetValue():	pesquisar = "SELECT pd_codi,pd_nome,pd_unid,pd_nmgr,pd_fabr, pd_pcom, pd_pcus, pd_tpr1, pd_para,pd_ende FROM produtos WHERE pd_fabr='" + self.selecao.GetValue().upper() + "' ORDER BY pd_nome"
				if self.selecionar_subgrupo1.GetValue():	pesquisar = "SELECT pd_codi,pd_nome,pd_unid,pd_sug1,pd_fabr, pd_pcom, pd_pcus, pd_tpr1, pd_para,pd_ende FROM produtos WHERE pd_sug1='" + self.selecao.GetValue().upper() + "' ORDER BY pd_nome"
				if self.selecionar_subgrupo2.GetValue():	pesquisar = "SELECT pd_codi,pd_nome,pd_unid,pd_sug2,pd_fabr, pd_pcom, pd_pcus, pd_tpr1, pd_para,pd_ende FROM produtos WHERE pd_sug2='" + self.selecao.GetValue().upper() + "' ORDER BY pd_nome"
				if  self.selecionar_endereco.GetValue():
				    
				    pesquisar = "SELECT t1.pd_codi,t1.pd_nome,t1.pd_unid,t1.pd_nmgr,t1.pd_fabr, t1.pd_pcom, t1.pd_pcus, t1.pd_tpr1, t1.pd_para,t1.pd_ende, t2.ef_endere FROM produtos t1 inner join estoque t2 on (t1.pd_codi=t2.ef_codigo ) WHERE t2.ef_endere= '"+self.selecao.GetValue().upper()+"' ORDER BY pd_nome"

				if __id == 90000:	pesquisar = "SELECT pd_codi,pd_nome,pd_unid,pd_nmgr,pd_fabr, pd_pcom, pd_pcus, pd_tpr1, pd_para FROM produtos WHERE pd_codi='" + codigo + "' ORDER BY pd_nome"
				if __id == 90001:	pesquisar = "SELECT pd_codi,pd_nome,pd_unid,pd_nmgr,pd_fabr, pd_pcom, pd_pcus, pd_tpr1, pd_para FROM produtos WHERE pd_docf='" + codigo + "' ORDER BY pd_nome"
				
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
		comprados = sql[2].execute("SELECT ic_quanti, ic_quncom, ic_vcusto  FROM iccmp WHERE ic_lancam >='"+str( inicial )+"' and ic_lancam <='"+str( final )+"' and ic_cdprod='"+ str( codigo )+"' and ic_cancel!='1' and ic_tipoen='1'")
		__cpr = sql[2].fetchall()

		compras = Decimal('0.0000')
		compras_quantidade = 0

		_precocompra = Decimal('0.0000')
		_precocustos = Decimal('0.0000')
		ultimo_compra = ""
		ultimo_custos = ""

		"""  Totaliza vendas no periodo  """
		vendedidos = sql[2].execute("SELECT  SUM(it_quan) FROM idavs WHERE it_lanc >='"+str( inicial )+"' and it_lanc <='"+str( final )+"' and it_codi='"+ str( codigo )+"' and it_canc!='1' and it_tped='1'")
		vendas = sql[2].fetchone()[0]

		"""  Totaliza devolucao de vendas no periodo  """
		vendedidos = sql[2].execute("SELECT  SUM(it_quan) FROM didavs WHERE it_lanc >='"+str( inicial )+"' and it_lanc <='"+str( final )+"' and it_codi='"+ str( codigo )+"' and it_canc!='1' and it_tped='1'")
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
		dc.DrawRotatedText(u"Relatorio para previsão de comrpas", 3, 510, 90)
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

class ZebraEtiquetas(wx.Frame):
    
    lista_produtos=[]
    def __init__(self, parent,id):
	
	self.p=parent
	self.filial=parent.pRFilial
	self.grupos=['']
	self.fabricantes=['']

	wx.Frame.__init__(self, parent, id, 'Emissão de etiquetas', size=(1024,495), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel = wx.Panel(self,-1)

	self.gerencia_etiqueta = Zebra(self.painel, 10 ,pos=(12,1), size=(650,393),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

	self.gerencia_etiqueta.SetBackgroundColour('#557E8C')
	self.gerencia_etiqueta.SetForegroundColour("#000000")
	self.gerencia_etiqueta.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.painel.Bind(wx.EVT_PAINT,self.desenho)
	self.gerencia_etiqueta.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.copiarDados)

	self.impressao_etiqueta = wx.ListCtrl(self.painel, 11,pos=(665,1), size=(360,350),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

	self.impressao_etiqueta.SetBackgroundColour('#BFBFBF')
	self.impressao_etiqueta.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

	self.impressao_etiqueta.InsertColumn(0, u'Descrição dos Produtos', width=360)
	self.impressao_etiqueta.InsertColumn(1, u'Barras', width=100)
	self.impressao_etiqueta.InsertColumn(2, u'Preço',format=wx.LIST_ALIGN_LEFT,width=105)
	self.impressao_etiqueta.InsertColumn(3, u'Codigo', width=120)
	self.impressao_etiqueta.InsertColumn(4, u'Endereco', width=200)
	self.impressao_etiqueta.InsertColumn(5, u'Fabricante', width=200)
	self.impressao_etiqueta.InsertColumn(6, u'Dados argox', width=2000)

	self.impressao_etiqueta.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.apagarUnitario)
	
	"""  Lista Fabricantes/Grupos  """
	self.selecionaFabGr()
	
	"""  Impressoras  """
	simm, impressoras, user, self.printers = formas.listaprn( 1 )
	lista_printer = ['']
	for i in impressoras:
	    if i[8].split('-')[0]=='9':	lista_printer.append(i[0]+'-'+i[1])

	self.lista_argox=['',
	u'100 - Argox 107x25 1 carreira',
	u'101 - Argox 25x15 4 carreiras',
	u'102 - Argox 75x25 1 carreira',
	u'103 - Argox 40x20 2 carreiras',
	u'104 - Argox 33x23 3 carreiras { Código e descrição }',
	u'105 - Argox 33x23 3 carreiras { Barras,Descricao,Preço }',
	u'106 - Argox 100x50 1 carreira',
	u'107 - Argox 100x67 1 carreira',
	u'108 - Argox 83x40 1 carreira {Gondola}',
	u'109 - Argox 75x25 1 carreira {Gondola}'	
	]
	
	wx.StaticText(self.painel,-1,"Pesquisar p/descrição{ Expressão (*)Encadeado (c)Codigo (b)Barras }",pos=(12,402)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,"Selecione o tipo de etiqueta para impressão",pos=(12,452)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,"Selecione uma fila de impressão",pos=(666,452)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,"Tabela de preços",pos=(877,452)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,"Selecione uma impressora",pos=(666,362)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

	self.lp = wx.StaticText(self.painel,-1,"[00000]",pos=(570,395))
	self.lp.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.lp.SetForegroundColour('#0C3E6E')

	self.li = wx.StaticText(self.painel,-1,"[00000]",pos=(621,395))
	self.li.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.li.SetForegroundColour('#0C3E6E')

	self.fb = wx.StaticText(self.painel,-1,"Fabricante/Grupo",pos=(322,455))
	self.fb.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.fb.SetForegroundColour('#1C531C')

	self.selfabricante = wx.RadioButton(self.painel,-1,u"Fabricantes", pos=(420,400),style=wx.RB_GROUP)
	self.selgrupos = wx.RadioButton(self.painel,-1,u"Grupos ",  pos=(420, 425))
	self.selfabricante.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.selgrupos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	
	self.consultar = wx.TextCtrl(self.painel,302,pos=(10,415), size=(400,27),style=wx.TE_PROCESS_ENTER)
	self.consultar.SetBackgroundColour('#E5E5E5')
	self.consultar.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.tabelas_precos=['Tabela de preço-1','Tabela de preço-2','Tabela de preço-3','Tabela de preço-4','Tabela de preço-5','Tabela de preço-6']
	self.tipos_impressoras = wx.ComboBox(self.painel,-1 , value='1-Impressora Zebra', pos=(665, 375), size = (360,27), choices = ['1-Impressora Zebra','2-Impressora Argox'], style=wx.NO_BORDER|wx.CB_READONLY)
	self.tipos_etiquetas = wx.ComboBox(self.painel,-1 , value='', pos=(10, 465), size = (300,27), choices = login.lista_zebra, style=wx.NO_BORDER|wx.CB_READONLY)
	self.grupo_fabricante = wx.ComboBox(self.painel,500 , value='', pos=(320,465), size = (200,27), choices = self.fabricantes, style=wx.NO_BORDER)
	self.impressoras = wx.ComboBox(self.painel,-1 , value='', pos=(665, 465), size = (205,27), choices = lista_printer, style=wx.NO_BORDER|wx.CB_READONLY)
	self.tabelas = wx.ComboBox(self.painel,-1 , value=self.tabelas_precos[0], pos=(875, 465), size = (150,27), choices=self.tabelas_precos, style=wx.NO_BORDER|wx.CB_READONLY)

	procurar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(526,415), size=(42,34))
	copiar_tudo = wx.BitmapButton(self.painel, 20, wx.Bitmap("imagens/sair24.png", wx.BITMAP_TYPE_ANY), pos=(573,415), size=(42,34))
	apagar_tudo = wx.BitmapButton(self.painel, 21, wx.Bitmap("imagens/lixo24.png", wx.BITMAP_TYPE_ANY), pos=(620,415), size=(42,34))

	send_printer = GenBitmapTextButton(self.painel,-1,label='  Enviar\n  Para impressora  ', pos=(526,458),size=(135,33), bitmap=wx.Bitmap("imagens/printing20.png", wx.BITMAP_TYPE_ANY))
	send_printer.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

	self.sair_codigo=wx.CheckBox(self.painel, -1, "Sair código do produto no lugar do codigo de barras", pos=(665,405))
	self.sair_preco=wx.CheckBox(self.painel, -1, "Sair preço do produto", pos=(665,430))
	self.sair_cnpj=wx.CheckBox(self.painel, -1, "Sair cnpj da filial", pos=(800,430))
	self.sair_endereco=wx.CheckBox(self.painel, -1, u"Relacionar endereço", pos=(915,405))
	self.sair_fantasia=wx.CheckBox(self.painel, -1, "Sair fantasia", pos=(915,430))
	self.sair_preco.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.sair_cnpj.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.sair_fantasia.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.sair_codigo.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.sair_endereco.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.sair_preco.SetValue(True)
	self.sair_cnpj.SetValue(True)
	self.sair_fantasia.SetValue(True)
	self.sair_codigo.Enable(False)

	self.sair_preco.Enable(False)
	self.sair_cnpj.Enable(False)

	self.gerencia_etiqueta.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
	self.impressao_etiqueta.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
	copiar_tudo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
	apagar_tudo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
            
	self.gerencia_etiqueta.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
	self.impressao_etiqueta.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
	copiar_tudo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
	apagar_tudo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

	self.consultar.Bind(wx.EVT_TEXT_ENTER, self.consultaProduto)
	copiar_tudo.Bind(wx.EVT_BUTTON, self.adicionarTodos)
	apagar_tudo.Bind(wx.EVT_BUTTON, self.apagarTodos)
	procurar.Bind(wx.EVT_BUTTON, self.consultaProduto)
	self.selfabricante.Bind(wx.EVT_RADIOBUTTON, self.mudarFabGru)
	self.selgrupos.Bind(wx.EVT_RADIOBUTTON, self.mudarFabGru)
	self.grupo_fabricante.Bind(wx.EVT_TEXT_ENTER, self.setarFabGru)
	self.grupo_fabricante.Bind(wx.EVT_COMBOBOX, self.selecionarFabGru)
	
	send_printer.Bind(wx.EVT_BUTTON, self.enviarImpressao)
	self.tipos_etiquetas.Bind(wx.EVT_COMBOBOX, self.etiquetasTipos)
	self.tipos_impressoras.Bind(wx.EVT_COMBOBOX, self.selecaoImpressora)
	
	self.consultar.SetFocus()

	if self.lista_produtos:
	    
	    _mensagem = mens.showmsg("Adicionando items na lista para impressao\n\nAguarde...")
	    for codigo in self.lista_produtos:

		self.consultar.SetValue('C:'+codigo)
		self.consultaProduto(wx.EVT_BUTTON)
		self.gerencia_etiqueta.Select( 0 )
		self.gerencia_etiqueta.Focus( 0 )
		
		self.copiarDados(wx.EVT_BUTTON)

	    self.gerencia_etiqueta.DeleteAllItems()
	    self.gerencia_etiqueta.Refresh()
	    del _mensagem

    def selecaoImpressora(self,event):

	if self.tipos_impressoras.GetValue().split('-')[0]=='1':

	    self.tipos_etiquetas.SetItems(login.lista_zebra)
	    self.tipos_etiquetas.SetValue(login.lista_zebra[0])
	    self.impressoras.Enable(True)
	    self.sair_endereco.Enable(True)
	    self.sair_fantasia.Enable(True)
	    
	elif self.tipos_impressoras.GetValue().split('-')[0]=='2':

	    self.tipos_etiquetas.SetItems(self.lista_argox)
	    self.tipos_etiquetas.SetValue(self.lista_argox[0])
	    self.impressoras.Enable(False)
	    self.sair_endereco.Enable(False)
	    self.sair_fantasia.Enable(False)
	    
    def etiquetasTipos(self,event):

	self.sair_preco.Enable(False)
	self.sair_cnpj.Enable(False)
	self.sair_codigo.Enable(False)
	self.sair_codigo.SetValue(False)
	etiqueta = self.tipos_etiquetas.GetValue().split('-')[0].strip()
	if   etiqueta in ['02','03']:	self.sair_preco.Enable(True)
	elif etiqueta in ['04']:
	    self.sair_preco.Enable(True)
	    self.sair_cnpj.Enable(True)
	
	if etiqueta in ['03']:	self.sair_codigo.Enable(True)
	
    def enviarImpressao(self,event):
	
	if self.tipos_etiquetas.GetValue().split('-')[0].strip() in ['01']:
	    
	    alertas.dia(self.painel,'{ Modelo de etiqueta não implementada }\n'+(' '*120),u'Emissão de etiquetas')
	    return
	
	if not self.impressoras.GetValue() and self.tipos_impressoras.GetValue().split('-')[0]=='1':	alertas.dia(self.painel,'{ Selecione uma impressora de etiquetas valida }\n'+(' '*120),u'Emissão de etiquetas')
	elif not self.tipos_etiquetas.GetValue():	alertas.dia(self.painel,'{ Selecione o tipo de etiqueta para impressão }\n'+(' '*120),u'Emissão de etiquetas')
	elif not self.impressao_etiqueta.GetItemCount() and self.tipos_etiquetas.GetValue().split('-')[0].strip()!='99':	alertas.dia(self.painel,'{ Lista de produtos para impressão vazio}\n'+(' '*120),u'Emissão de etiquetas')
	else:

	    if self.tipos_impressoras.GetValue().split('-')[0]=='1':

		port = self.printers[self.impressoras.GetValue().split('-')[0]][9]
		ip = self.printers[self.impressoras.GetValue().split('-')[0]][10]

		ipt = ImpressaoEtiquetasZPL()
		
		ipt.imprimindoEtiquetas(self, self.impressao_etiqueta, (ip,port), self.tipos_etiquetas.GetValue().split('-')[0], self.filial)
		if self.lista_produtos:	self.gravar_etiquetas_impressas()

	    elif self.tipos_impressoras.GetValue().split('-')[0]=='2':

		ETQ = ArgoxPrinter()
		lisTa = carre = ''
		linha = 0
		for i in range( self.impressao_etiqueta.GetItemCount() ):
		
		    if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="100":	lisTa +=ETQ.eTiqueTa01( self.impressao_etiqueta.GetItem(i, 6).GetText() )
		    if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="102":	lisTa +=ETQ.eTiqueTa02( self.impressao_etiqueta.GetItem(i, 6).GetText() )
		    if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="106":	lisTa +=ETQ.eTiqueTa07( self.impressao_etiqueta.GetItem(i, 6).GetText() )
		    if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="107":	lisTa +=ETQ.eTiqueTa08( self.impressao_etiqueta.GetItem(i, 6).GetText() )
		    if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="108":	lisTa +=ETQ.eTiqueTa09( self.impressao_etiqueta.GetItem(i, 6).GetText() )
		    if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="109":	lisTa +=ETQ.eTiqueTa10( self.impressao_etiqueta.GetItem(i, 6).GetText() )
		    if self.tipos_etiquetas.GetValue().split('-')[0].strip() in ["101","103","104","105"]:
		    
			carre +=self.impressao_etiqueta.GetItem(i, 6).GetText()+"\n"
			linha +=1
			
			if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="101" and linha == 4:	lisTa += ETQ.eTiqueTa04( carre )
			if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="101" and linha == 4:
				
			    linha = 0
			    carre = ''

			if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="104" and linha == 3:	lisTa += ETQ.eTiqueTa03( carre )
			if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="104" and linha == 3:
				
			    linha = 0
			    carre = ''

			if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="103" and linha == 2:	lisTa += ETQ.eTiqueTa05( carre )
			if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="103" and linha == 2:
				
			    linha = 0
			    carre = ''

			if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="105" and linha == 3:	lisTa += ETQ.eTiqueTa06( carre )
			if self.tipos_etiquetas.GetValue().split('-')[0].strip()=="105" and linha == 3:
				
			    linha = 0
			    carre = ''

		if self.lista_produtos:	self.gravar_etiquetas_impressas()

		_nomeArq = diretorios.usPasta+login.usalogin.lower()+"_etiquetas.txt"
		_emitida = open(_nomeArq,'w')
		_emitida.write( lisTa.encode("UTF-8") )
		_emitida.close()
		
		MostrarHistorico.hs = u"Nº de Etiques: "+str(self.impressao_etiqueta.GetItemCount())+"\n\n"+lisTa
		MostrarHistorico.TP = "ETQ"
		MostrarHistorico.TT = "Etiquetas { Produtos }"
		MostrarHistorico.AQ = _nomeArq
		MostrarHistorico.FL = self.filial
		MostrarHistorico.GD = ""
		
		gerenciador.parente  = self
		gerenciador.Filial   = self.filial

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
    
    def gravar_etiquetas_impressas(self):

	conn = sqldb()
	sql  = conn.dbc("Produtos: Marcando produtos, etiqueta impressa", fil = login.identifi, janela = self.painel )
	if sql[2]:

	    for i in range(self.impressao_etiqueta.GetItemCount()):
		
		codigo = self.impressao_etiqueta.GetItem(i, 6).GetText().split("|")[0]
		data = datetime.datetime.now().strftime("%Y/%m/%d")
		print codigo,data
		sql[2].execute("UPDATE produtos SET pd_has3='"+ data+"' WHERE pd_codi='"+ codigo +"'")
	    
	    sql[1].commit()
	    conn.cls(sql[1],sql[2])
	    print "Gravados"
    def selecionaFabGr(self):
		
	conn = sqldb()
	sql  = conn.dbc("Produtos: Fabricantes/Grupos", fil = self.filial, janela = self.painel )
	if sql[0]:

	    if sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_cdpd='F' ORDER BY fg_desc"):
		for i in sql[2].fetchall():	self.fabricantes.append(i[0])
		    
	    if sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_cdpd='G' ORDER BY fg_desc"):
		for i in sql[2].fetchall():	self.grupos.append(i[0])

	    conn.cls(sql[1])

    def selecionarFabGru(self,event):
	
	self.consultaProduto(wx.EVT_BUTTON)
	
    def setarFabGru(self,event):
	if self.grupo_fabricante.GetValue():

	    relacao = self.fabricantes if self.selfabricante.GetValue() else self.grupos
	    self.grupo_fabricante.SetItems(relacao)	    

	    cons = nF.acentuacao(self.grupo_fabricante.GetValue().strip().upper())
	    relacao = self.fabricantes if self.selfabricante.GetValue() else self.grupos
	    nova_relacao = ['']
	    for i in relacao:
			    
		if type(i)!=unicode:	i=i.decode('UTF-8')
		ii=nF.acentuacao(i)
		if cons == ii[:len(cons)]:
			    
		    nova_relacao.append(ii)
			
	    if cons:	self.fb.SetLabel(cons)
	    self.grupo_fabricante.SetItems(nova_relacao)
	    if len(nova_relacao)>=2:
		self.grupo_fabricante.SetValue(nova_relacao[1])
		self.fb.SetLabel(nova_relacao[1])
	else:
	    relacao = self.fabricantes if self.selfabricante.GetValue() else self.grupos
	    self.grupo_fabricante.SetItems(relacao)	    
	
    def buscarFabGru(self,event):

	if event.GetId()==500 and self.grupo_fabricante.GetValue():
	    
	    self.fb.SetLabel(self.grupo_fabricante.GetValue())
	    self.consultaProduto(wx.EVT_BUTTON)

	else:
	    relacao = self.fabricantes if self.selfabricante.GetValue() else self.grupos
	    self.grupo_fabricante.SetItems(relacao)	    
	    
    def mudarFabGru(self,event):
	self.grupo_fabricante.SetItems(self.fabricantes if self.selfabricante.GetValue() else  self.grupos)
	
    def copiarDados(self,event):
	
	indice = self.gerencia_etiqueta.GetFocusedItem()
	registros = self.impressao_etiqueta.GetItemCount()
	
	#--// Inserindo produtos individual
	produto = self.gerencia_etiqueta.GetItem(indice,1).GetText()
	barras  = self.gerencia_etiqueta.GetItem(indice,0).GetText()

	precos  = format( Decimal(format(Decimal(self.gerencia_etiqueta.GetItem(indice,3).GetText().replace(',','')),'.2f')), ',' ) if self.gerencia_etiqueta.GetItem(indice,3).GetText() else ''

	codigo = self.gerencia_etiqueta.GetItem(indice,4).GetText()
	endereco = self.gerencia_etiqueta.GetItem(indice,5).GetText()
	fabricante = self.gerencia_etiqueta.GetItem(indice,6).GetText()
	dadosargox = self.gerencia_etiqueta.GetItem(indice,7).GetText()

	if not self.existente(produto):

	    self.impressao_etiqueta.InsertStringItem(registros,produto)
	    self.impressao_etiqueta.SetStringItem(registros,1,barras)
	    self.impressao_etiqueta.SetStringItem(registros,2,precos)

	    self.impressao_etiqueta.SetStringItem(registros,3,codigo)
	    self.impressao_etiqueta.SetStringItem(registros,4,endereco)
	    self.impressao_etiqueta.SetStringItem(registros,5,fabricante)
	    self.impressao_etiqueta.SetStringItem(registros,6,dadosargox)
	    
	    self.definirCor()
	    
	else:	alertas.dia(self.painel,'Produto ja selecionado para impressão...\n'+(' '*150),'Emissão de etiquetas')

    def adicionarTodos(self,event):
	
	indice = self.impressao_etiqueta.GetItemCount()

	if self.gerencia_etiqueta.GetItemCount():

	    confima = wx.MessageDialog(self.painel,"{ Confirme para copiar todos os produtos p/impressão }\n"+(" "*140),"Produtos: Etiquetas",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal() ==  wx.ID_YES:

		for i in range(self.gerencia_etiqueta.GetItemCount()):

		    produto = self.gerencia_etiqueta.GetItem(i,1).GetText()
		    barras  = self.gerencia_etiqueta.GetItem(i,0).GetText()
		    precos  = self.gerencia_etiqueta.GetItem(i,3).GetText()

		    codigo  = self.gerencia_etiqueta.GetItem(i,4).GetText()
		    endereco  = self.gerencia_etiqueta.GetItem(i,5).GetText()
		    fabricante  = self.gerencia_etiqueta.GetItem(i,6).GetText()
		    dadosargox = self.gerencia_etiqueta.GetItem(indice,7).GetText()

		    if not self.existente(produto):
			
			self.impressao_etiqueta.InsertStringItem(indice,produto)
			self.impressao_etiqueta.SetStringItem(indice,1,barras)
			self.impressao_etiqueta.SetStringItem(indice,2,precos)

			self.impressao_etiqueta.SetStringItem(indice,3,codigo)
			self.impressao_etiqueta.SetStringItem(indice,4,endereco)
			self.impressao_etiqueta.SetStringItem(indice,5,fabricante)
			self.impressao_etiqueta.SetStringItem(indice,6,dadosargox)
			indice +=1
	    
		self.definirCor()

    def apagarTodos(self,event):

	if self.impressao_etiqueta.GetItemCount():
	    
	    confima = wx.MessageDialog(self.painel,"{ Confirme para apagar todos os produtos da impressão }\n"+(" "*140),"Produtos: Etiquetas",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal() ==  wx.ID_YES:
		
		self.impressao_etiqueta.DeleteAllItems()
		self.impressao_etiqueta.Refresh()

    def apagarUnitario(self,event):

	if self.impressao_etiqueta.GetItemCount():
	    
	    confima = wx.MessageDialog(self.painel,"{ Confirme para apagar o produto selecionado }\n"+(" "*140),"Produtos: Etiquetas",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal() ==  wx.ID_YES:
		
		indice = self.impressao_etiqueta.GetFocusedItem()
		self.impressao_etiqueta.DeleteItem(indice)
		self.impressao_etiqueta.Refresh()
		self.definirCor()
		
    def definirCor(self):
	
	self.impressao_etiqueta.Refresh()
	self.li.SetLabel('['+str(self.impressao_etiqueta.GetItemCount()).zfill(5)+']')

    def existente(self, produto):
	
	existente = False
	if self.impressao_etiqueta.GetItemCount():
	    
	    for i in range(self.impressao_etiqueta.GetItemCount()):
		if self.impressao_etiqueta.GetItem(i,0).GetText() == produto:
		    existente = True
		    break
		    
	return existente
	
    def consultaProduto(self,event):

	if self.consultar.GetValue().strip() or self.grupo_fabricante.GetValue():
	    
	    self.gerencia_etiqueta.DeleteAllItems()
	    cons = self.consultar.GetValue().strip()
	    letr = self.grupo_fabricante.GetValue()
	    psqr = 0
	    self.grupo_fabricante.SetValue('')
	    
	    conn = sqldb()
	    sql  = conn.dbc("Produtos: Etiquetas", fil = self.filial, janela = self.painel )
	    if sql[0]:

		if "*" in cons:
		    ps = "SELECT pd_codi,pd_nome,pd_barr,pd_unid,pd_fabr,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_nmgr,pd_ende FROM produtos WHERE pd_canc='' ORDER BY pd_nome"
		    for cs in cons.split('*'):
			if cs:
			    ps = ps.replace("WHERE","WHERE pd_nome like '%"+ cs +"%' and")

		elif 'C:' in cons.upper():
		    ps = "SELECT pd_codi,pd_nome,pd_barr,pd_unid,pd_fabr,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_nmgr,pd_ende FROM produtos WHERE pd_codi='"+ cons.upper().split('C:')[1] +"' and pd_canc='' ORDER BY pd_nome"
		    if not sql[2].execute(ps):	
			ps = "SELECT pd_codi,pd_nome,pd_barr,pd_unid,pd_fabr,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_nmgr,pd_ende FROM produtos WHERE pd_codi='"+ cons.upper().split('C:')[1].zfill(14) +"' and pd_canc='' ORDER BY pd_nome"
			if not sql[2].execute(ps):
			    ps = "SELECT pd_codi,pd_nome,pd_barr,pd_unid,pd_fabr,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_nmgr,pd_ende FROM produtos WHERE pd_codi like '"+ cons.upper().split('C:')[1] +"%' and pd_canc='' ORDER BY pd_nome"
		elif 'B:' in cons.upper():
		    ps = "SELECT pd_codi,pd_nome,pd_barr,pd_unid,pd_fabr,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_nmgr,pd_ende FROM produtos WHERE pd_barr like '"+ cons.upper().split('B:')[1] +"%' and pd_canc='' ORDER BY pd_nome"

		else:	
		    ps = "SELECT pd_codi,pd_nome,pd_barr,pd_unid,pd_fabr,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_nmgr,pd_ende FROM produtos WHERE pd_nome like '%"+ cons +"%' and pd_canc='' ORDER BY pd_nome"
		    if   self.selfabricante.GetValue() and letr:	ps="SELECT pd_codi,pd_nome,pd_barr,pd_unid,pd_fabr,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_nmgr,pd_ende FROM produtos WHERE pd_fabr='"+ letr +"' and pd_canc='' ORDER BY pd_nome"
		    elif self.selgrupos.GetValue() and letr:	ps="SELECT pd_codi,pd_nome,pd_barr,pd_unid,pd_fabr,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_nmgr,pd_ende FROM produtos WHERE pd_nmgr='"+ letr +"' and pd_canc='' ORDER BY pd_nome"

		psqr = sql[2].execute(ps)
		rest = sql[2].fetchall()

		if psqr:
		    
		    relacao = {}
		    registros = 0
		    for i in rest:
			
			
			if self.sair_endereco.GetValue() and sql[2].execute('SELECT ef_endere FROM estoque WHERE ef_idfili="'+self.filial+'" and ef_codigo="'+i[0]+'"'):	endereco = sql[2].fetchone()[0]
			else:	endereco=''
			if not endereco and i[12]:	endereco = i[12]

			descricao=nF.acentuacao(i[1] if type(i[3])==unicode else i[1].decode('UTF-8'))
			endereco=nF.acentuacao(endereco if type(endereco)==unicode else endereco.decode('UTF-8'))
			fabricante=nF.acentuacao(i[4] if type(i[1])==unicode else i[4].decode('UTF-8'))
			descricao=descricao.replace('"',' ').replace("'",' ')
			
			pv=format(i[5],',')
			if self.tabelas.GetValue() and self.tabelas.GetValue().split('-')[1]=='2' and i[6]:	pv=format(i[6],',')
			if self.tabelas.GetValue() and self.tabelas.GetValue().split('-')[1]=='3' and i[7]:	pv=format(i[7],',')
			if self.tabelas.GetValue() and self.tabelas.GetValue().split('-')[1]=='4' and i[8]:	pv=format(i[8],',')
			if self.tabelas.GetValue() and self.tabelas.GetValue().split('-')[1]=='5' and i[9]:	pv=format(i[9],',')
			if self.tabelas.GetValue() and self.tabelas.GetValue().split('-')[1]=='6' and i[10]:	pv=format(i[10],',')
			
			pv = format( Decimal(format(Decimal(pv.replace(',','')),'.2f')) , ',' )
			
			argox = i[0]+"|"+i[2]+"|"+descricao+"|"+i[11]+"|"+fabricante+"|"+endereco+"|"+pv+"|"+i[3]
			relacao[registros]=i[2],descricao,i[3], pv ,str(int(i[0]) if i[0].isdigit() else i[0]),endereco,fabricante,argox

			registros +=1

		    self.gerencia_etiqueta.SetItemCount(psqr)
		    Zebra.itemDataMap  = relacao
		    Zebra.itemIndexMap = relacao.keys()

		conn.cls(sql[1])

	    self.grupo_fabricante.SetValue('')
	    #self.buscarFabGru(wx.EVT_BUTTON)

    def OnEnterWindow(self, event):
	
	if   event.GetId() == 10:	sb.mstatus("  Click duplo para copiar o produto selecionado para a lista de impressao",0)
	elif event.GetId() == 11:	sb.mstatus("  Click duplo para apagar o produto selecionada da lista de impressao",0)
	elif event.GetId() == 20:	sb.mstatus("  Copiar todos os produto da lista para a lista de impressao",0)
	elif event.GetId() == 21:	sb.mstatus(u"  Apagar todos os produtos da lista de impressao",0)

	event.Skip()
		
    def OnLeaveWindow(self,event):
	sb.mstatus("  Genrenciador do estoque fisico das filiais e produtos",0)
	event.Skip()
	
    def desenho(self,event):

	dc = wx.PaintDC(self.painel)

	dc.SetTextForeground("#245485") 	
	dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
	dc.DrawRotatedText(self.filial+ u" Linguagem ZPL-Emissão de etiquetas", 0, 393, 90)
	dc.DrawRotatedText(u"Pesquisa", 0, 495, 90)

class Zebra(wx.ListCtrl):

    itemDataMap  = {}
    itemIndexMap = {}

    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		  
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
	self.attr4 = wx.ListItemAttr()
	self.attr1.SetBackgroundColour("#F8F8E1")
	self.attr2.SetBackgroundColour("#3B7486")
	self.attr3.SetBackgroundColour("#597F8C")
	self.attr4.SetBackgroundColour("#D19595")

	self.InsertColumn(0, u'Barras',width=120)
	self.InsertColumn(1, u'Descrição dos produtos',width=375)
	self.InsertColumn(2, u'UN', width=30)
	self.InsertColumn(3, u'Preço',format=wx.LIST_ALIGN_LEFT,width=105)
	self.InsertColumn(4, u'Codigo',width=120)
	self.InsertColumn(5, u'Endereco',width=200)
	self.InsertColumn(6, u'Fabricante',width=200)
	self.InsertColumn(7, u'Dados da argox',width=2000)
		
    def OnGetItemText(self, item, col):

	try:
	    index      = self.itemIndexMap[item]
	    lista      = self.itemDataMap[index][col]
	    return lista

	except Exception, _reTornos:	pass
						
    def OnGetItemAttr(self, item): #Ajusta cores sim/nao

	if self.itemIndexMap != []:

	    index=self.itemIndexMap[item]
	    if item % 2:	return self.attr3
	    else:	return self.attr2

	else:	return None
		
    def OnGetItemImage(self, item):

	if self.itemIndexMap != []:

	    index=self.itemIndexMap[item]
	    return self.menu
		    
	else:	return None
		
    def GetListCtrl(self):	return self

class ImpressaoEtiquetasZPL:
    
    def imprimindoEtiquetas(self, parent, lista, impressora, etiqueta, filial):
	
	self.f = login.filialLT[filial][14]
	self.d = nF.conversao(login.filialLT[filial][9],4)
	self.p = parent
	self.i = impressora
	self.fl = filial
	r = True
	vezes = 1
	colunas = {}
	
	self.p.consultar.SetValue('Imprimindo AGUARDE...')
	self.p.consultar.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.p.consultar.SetForegroundColour('#E83030')
	
	ca = {'02':2,"03":3,'04':1,'05':1,'06':1,'07':1,'08':2,"09":1,"10":1,"11":1} #--// [ Tipo de etiquetas e quantidades de carreiras ]
	if etiqueta.strip()=='99':	self.emitir(colunas,etiqueta)
	else:

	    for i in range(lista.GetItemCount()):
		
		ds = lista.GetItem(i,0).GetText()
		ba = lista.GetItem(i,1).GetText()
		pc = lista.GetItem(i,2).GetText()

		cd = lista.GetItem(i,3).GetText()
		en = lista.GetItem(i,4).GetText()
		fa = lista.GetItem(i,5).GetText()
		colunas[str(vezes)]=ds,ba,pc, cd,en,fa

		vezes +=1
		if len(colunas)==ca[etiqueta.strip()]:
		    r=self.emitir(colunas,etiqueta)
		    colunas,vezes={},1
		    if not r:	break
		    
	    if len(colunas) and r:	r = self.emitir(colunas,etiqueta)

	self.p.consultar.SetValue('')
	self.p.consultar.SetForegroundColour('#000000')
	self.p.consultar.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	return r
	
    def emitir(self,l, tipo_etiqueta):

	fantasia=self.f if self.p.sair_fantasia.GetValue() else 'L O J A'
	s=''
	ca = 20 #--// Numero de carcter na descricao
	if   tipo_etiqueta.strip()=='02':	ca = 40 #--// Numero de carcter na descricao
	elif tipo_etiqueta.strip()=='03':	ca = 35 #--// Numero de carcter na descricao
	elif tipo_etiqueta.strip()=='04':	ca = 58 #--// Numero de carcter na descricao
	elif tipo_etiqueta.strip()=='05':	ca = 45 #--// Numero de carcter na descricao

	if tipo_etiqueta.strip()=='02':  #--// [ Etiqueta 40x20 2 carreiras ]

	    s+='^XA'
	    s+='^LL200'
	    s+='^FO110,10^ADN,20,10^FD'+ fantasia +'^FS'
	    if len(l)>=2:	s+='^FO460,10^ADN,20,10^FD'+ fantasia +'^FS'
	    s+='^FO110,30^A0N,15,0^FD'+l['1'][0][:ca]+'^FS'
	    if self.p.sair_preco.GetValue():	s+='^FO110,50^ADN,30,10^FDR$'+l['1'][2]+'^FS'
	    if len(l)>=2:	s+='^FO460,30^A0N,15,0^FD'+l['2'][0][:ca]+'^FS'
	    if len(l)>=2 and self.p.sair_preco.GetValue():	s+='^FO460,50^ADN,30,10^FDR$'+l['2'][2]+'^FS'

	    s+='^FO110,80^BY2,,90^BEN,60,Y,N^FD'+l['1'][1]+'^FS'
	    if len(l)>=2:	s+='^FO460,80^BY2,,90^BEN,60,Y,N^FD'+l['2'][1]+'^FS'
	    s+='^XZ'

	elif tipo_etiqueta.strip()=='03':  #--// [ Etiqueta 34x23 3 carreiras ]

	    s+='^XA'
	    s+='^LL200'
	    #s+='^FO10,10^ADN,20,10^FD'+ fantasia +'^FS'
	    #if len(l)>=2:	s+='^FO300,10^ADN,20,10^FD'+ fantasia +'^FS'
	    #if len(l)==3:	s+='^FO590,10^ADN,20,10^FD'+ fantasia +'^FS'

	    if self.p.sair_codigo.GetValue():
		s+='^FO00,35^A0N,25,0^FD'+l['1'][0][:20]+'^FS'
		s+='^FO00,60^A0N,25,0^FD'+l['1'][0][20:40]+'^FS'
		s+='^FO00,85^A0N,25,0^FD'+l['1'][0][40:60]+'^FS'
		s+='^FO00,110^A0N,25,0^FD'+l['1'][0][60:80]+'^FS'
		
	    else:
		s+='^FO10,10^A0N,22,0^FD'+l['1'][0][:21]+'^FS'
		s+='^FO10,30^A0N,22,0^FD'+l['1'][0][21:42]+'^FS'
		s+='^FO10,50^A0N,22,0^FD'+l['1'][0][42:63]+'^FS'
		
	    if self.p.sair_preco.GetValue():	s+='^FO60,75^ADN,30,10^FDR$'+l['1'][2]+'^FS'
	    if len(l)>=2:
		if self.p.sair_codigo.GetValue():
		    s+='^FO300,35^A0N,25,0^FD'+l['2'][0][:20]+'^FS'
		    s+='^FO300,60^A0N,25,0^FD'+l['2'][0][20:40]+'^FS'
		    s+='^FO300,85^A0N,25,0^FD'+l['2'][0][40:60]+'^FS'
		    s+='^FO300,110^A0N,25,0^FD'+l['2'][0][60:80]+'^FS'
		else:
		    s+='^FO300,10^A0N,22,0^FD'+l['2'][0][:21]+'^FS'
		    s+='^FO300,30^A0N,22,0^FD'+l['2'][0][21:42]+'^FS'
		    s+='^FO300,50^A0N,22,0^FD'+l['2'][0][42:63]+'^FS'

	    if len(l)>=2 and self.p.sair_preco.GetValue():	s+='^FO340,75^ADN,30,10^FDR$'+l['2'][2]+'^FS'
	    if len(l)==3:
		if self.p.sair_codigo.GetValue():
		    s+='^FO590,35^A0N,25,0^FD'+l['3'][0][:20]+'^FS'
		    s+='^FO590,60^A0N,25,0^FD'+l['3'][0][20:40]+'^FS'
		    s+='^FO590,85^A0N,25,0^FD'+l['3'][0][40:60]+'^FS'
		    s+='^FO590,110^A0N,25,0^FD'+l['3'][0][60:80]+'^FS'
		else:
		    s+='^FO590,10^A0N,22,0^FD'+l['3'][0][:21]+'^FS'
		    s+='^FO590,30^A0N,22,0^FD'+l['3'][0][21:42]+'^FS'
		    s+='^FO590,50^A0N,22,0^FD'+l['3'][0][42:63]+'^FS'

	    if len(l)==3 and self.p.sair_preco.GetValue():	s+='^FO630,75^ADN,30,10^FDR$'+l['3'][2]+'^FS'

	    if self.p.sair_codigo.GetValue():	s+='^FO00,140^ADN,30,10^FDCodigo: '+str(int(l['1'][3]))+'^FS'
	    else:	s+='^FO40,110^BY2,,30^BEN,40,Y,N^FD'+l['1'][1]+'^FS'
	    
	    if len(l)>=2:
		if self.p.sair_codigo.GetValue():	s+='^FO290,140^ADN,30,10^FDCodigo: '+str(int(l['2'][3]))+'^FS'
		else:	s+='^FO330,110^BY2,,30^BEN,40,Y,N^FD'+l['2'][1]+'^FS'
		
	    if len(l)==3:
		if self.p.sair_codigo.GetValue():	s+='^FO580,140^ADN,30,10^FDCodigo: '+str(int(l['3'][3]))+'^FS'
		else:	s+='^FO620,110^BY2,,30^BEN,40,Y,N^FD'+l['3'][1]+'^FS'
	    s+='^XZ'

	elif tipo_etiqueta.strip()=='04': #--// [ Etiqueta 70x30 1 carreira ]
	    s='^XA'
	    s+='^LL200'

	    s+='^FO140,15^ADN,32,12^FD'+ fantasia +'^FS'
	    if self.p.sair_cnpj.GetValue():	s+='^FO410,20^A0N,22,0^FDCNPJ: '+self.d+'^FS'
    	    s+='^FO140,47^A0N,20,0^FD'+l['1'][0][:ca]+'^FS'
	    if self.p.sair_preco.GetValue():	s+='^FO140,70^ADN,30,10^FDR$'+l['1'][2]+'^FS'
	    s+='^FO480,70^ADN,10,1^FD[ FABRICANTE ]^FS'
	    s+='^FO480,90^ADN,10,1^FD'+l['1'][5]+'^FS'
	    s+='^FO480,110^ADN,10,1^FD[ CODIGO INTERNO ]^FS'
	    s+='^FO480,130^ADN,35,12^FD'+l['1'][3]+'^FS'
	    s+='^FO480,170^ADN,1,1^FD[ ENDERECO ]^FS'
	    s+='^FO480,190^ADN,1,1^FD'+l['1'][4]+'^FS'

	    s+='^FO160,110^BY3,,90^BEN,70,Y,N^FD'+l['1'][1]+'^FS'
	    s+='^XZ'

	elif tipo_etiqueta.strip()=='05': #--// [ Perfil para etiqueta as gavetas do estoque 100x48 ]
	    s='^XA'
	    s+='^LL1200'
	    s+='^FO65,15^GB705,60,4,B^FS' #----// Caixa grande
	    s+='^FO425,115^GB340,45,3,B^FS' #--// Caixa pequena
	    s+='^FO76,30^A0N,30,0^FD'+l['1'][0][:ca]+'^FS'
	    s+='^FO70,90 ^A0N,20,0 ^FH^FD'+l['1'][0]+'^FS'
	    s+='^FO70,120^ADN,35,12^FDCodigo....: '+l['1'][3]+'^FS'
	    s+='^FO438,122^ADN,30,15^FD'+l['1'][1]+'^FS'
	    s+='^FO70,160^ADN,35,12^FDEndereco..: '+l['1'][4]+'^FS'
	    s+='^FO70,200^ADN,35,12^FDFabricante: '+l['1'][5]+'^FS'
	    s+='^FO70,240^BY5,,140^BEN,90,Y,N^FD'+l['1'][1]+'^FS'
	    s+='^FO645,100^BQ,2,5^FDLA,'+l['1'][1]+'^FS' #--// Impressao do qrcode
	    s+='^XZ'
	    
	elif tipo_etiqueta.strip()=='06': #--// [ Enderecamento do estoque 107x70 ]
	    _p1 = l['1'][0][:27]
	    _p2 = l['1'][0][27:]
	    if _p2.strip():	_p1 +='-'
	    s='^XA'
	    s+='^LL1200'
	    s+='^FO25,15^GB790,200,4,B^FS' #----// Caixa grande
	    s+='^FO25,210^GB250,120,3,B^FS' #--// Caixa descricao codigo
	    s+='^FO270,210^GB545,120,3,B^FS' #--// Caixa codigo barra
	    s+='^FO25,329^GB250,130,3,B^FS' #--// Caixa descricao do local
	    s+='^FO270,329^GB545,130,3,B^FS' #--// Caixa codigo local
	    s+='^FO40,50^A0N,50,0^FD'+_p1+'^FS'
	    s+='^FO40,110^A0N,50,0^FD'+_p2+'^FS'
    	    s+='^FO40,180 ^A0N,30,0 ^FH^FD'+l['1'][0]+'^FS'
	    s+='^FO40,245^A0N,60,0^FD'"CODIGO"'^FS'
	    s+='^FO280,245^A0N,75,0^FD'+l['1'][1]+'^FS'
	    s+='^FO40,355^A0N,80,0^FD'"LOCAL"'^FS'
	    s+='^FO280,355^A0N,80,0^FD'+l['1'][4]+'^FS'
	    s+='^XZ'

	elif tipo_etiqueta.strip()=='07': #--// [ Enderecamento do estoque 107x70 ]
	    _p1 = l['1'][0][:29]
	    _p2 = l['1'][0][29:]
	    _p3 = l['1'][0][58:]

	    codigo = l['1'][3] #--//Codigo do produto
	    if _p2.strip():	_p1 +='-'
	    s='^XA'
	    s+='^LL1200'
	    s+='^FO115,30^GB620,155,4,B^FS' #----// Caixa grande
	    s+='^FO115,183^GB180,100,4,B^FS' #----// Caixa descricao codigo
	    s+='^FO290,183^GB445,100,4,B^FS' #----// Caixa codigo barras
	    s+='^FO115,285^GB180,100,4,B^FS' #----// Caixa descricao local
	    s+='^FO290,285^GB445,100,4,B^FS' #----// Caixa endereco
	    s+='^FO122,50^A0N,40,0^FD'+_p1+'^FS'
	    s+='^FO122,90^A0N,40,0^FD'+_p2+'^FS'
	    if _p3:	s+='^FO122,145^A0N,40,0^FD'+_p3+'^FS'
    	    else:	s+='^FO122,145 ^A0N,25,0 ^FH^FD'+l['1'][0][:49]+'^FS'
	    s+='^FO122,210^A0N,50,0^FD'"CODIGO"'^FS'
	    s+='^FO320,210^A0N,60,0^FD'+codigo+'^FS'
	    s+='^FO122,310^A0N,50,0^FD'"LOCAL"'^FS'
	    s+='^FO320,310^A0N,60,0^FD'+l['1'][4]+'^FS'
	    s+='^XZ'

	if tipo_etiqueta.strip()=='08':  #--// [ Etiqueta 40x20 2 carreiras ]
	    s+='^XA'
	    s+='^LL200'
	    s+='^FO20,7^ADN,40,20^FD'+ fantasia +'^FS'
	    s+='^FO440,7^ADN,40,20^FD'+ fantasia +'^FS'
	    """ Descricao """
	    s+='^FO20,90^A0N,25,0^FD'+l['1'][0][:28]+'^FS'
	    s+='^FO20,115^A0N,25,0^FD'+l['1'][0][28:]+'^FS'
	    s+='^FO440,90^A0N,25,0^FD'+l['2'][0][:28]+'^FS'
	    s+='^FO440,115^A0N,25,0^FD'+l['2'][0][28:]+'^FS'
	    
	    """ Precos """
	    if self.p.sair_preco.GetValue():
		
		vl1 = l['1'][2][:-1] if l['1'][2].split('.')[1][2:] == '0' else l['1'][2]
		vl2 = l['2'][2][:-1] if l['2'][2].split('.')[1][2:] == '0' else l['2'][2]

		s+='^FO20,47^ADN,30,15^FDR$'+vl1+'^FS'
		s+='^FO440,47^ADN,30,15^FDR$'+vl2+'^FS'

	    """ Codigos de barras """
	    s+='^FO50,150^BY3,,210^BEN,55,Y,N^FD'+l['1'][1]+'^FS'
	    s+='^FO470,150^BY3,,210^BEN,55,Y,N^FD'+l['2'][1]+'^FS'
	    s+='^XZ'

	elif tipo_etiqueta.strip()=='09': #--// [ Perfil para etiqueta as gavetas do estoque 100x48 ]
	    s='^XA'
	    s+='^LL1200'
	    s+='^FO40,40^ADN,40,20^FD'+fantasia.upper()+'     R$ '+l['1'][2]+'^FS'
	    s+='^FO40,90 ^A0N,30,0 ^FH^FD'+l['1'][0]+'^FS'
	    s+='^FO40,120^ADN,35,12^FDCodigo....: '+str(int(l['1'][3]))+'^FS'
	    s+='^FO40,160^ADN,35,12^FDEndereco..: '+l['1'][4]+'^FS'
	    s+='^FO40,200^ADN,35,12^FDFabricante: '+l['1'][5]+'^FS'
	    s+='^FO080,250^BY5,,160^BEN,100,Y,N^FD'+l['1'][1]+'^FS'
	    s+='^FO660,100^BQ,2,5^FDLA,'+l['1'][1]+'^FS' #--// Impressao do qrcode
	    s+='^XZ'

	elif tipo_etiqueta.strip()=='10': #--// [ Perfil para etiqueta as gavetas do estoque 100x48 ]
	    s='^XA'
	    s+='^LL1200'
	    s+='^FO40,40^ADN,40,20^FD'+fantasia.upper()+'     R$ '+l['1'][2]+'^FS'
	    s+='^FO40,90 ^A0N,30,0 ^FH^FD'+l['1'][0][:50]+'^FS'
	    s+='^FO40,120 ^A0N,30,0 ^FH^FD'+l['1'][0][50:100]+'^FS'
	    s+='^FO40,170^ADN,35,12^FDCodigo....: '+str(int(l['1'][3]))+'^FS'
	    s+='^FO40,210^ADN,35,12^FDEndereco..: '+l['1'][4]+'^FS'
	    s+='^FO40,250^ADN,35,12^FDFabricante: '+l['1'][5]+'^FS'
	    s+='^FO100,330^BY5,,160^BEN,100,Y,N^FD'+l['1'][1]+'^FS'
	    s+='^FO660,180^BQ,2,5^FDLA,'+l['1'][1]+'^FS' #--// Impressao do qrcode
	    s+='^XZ'

	elif tipo_etiqueta.strip()=='11': #--// [ Etiqueta 70x30 1 carreira ]
	    s='^XA'
	    s+='^LL200'

	    s+='^FO140,15^ADN,40,12^FD'+ fantasia +'^FS'
	    s+='^FO140,60^A0N,27,0^FD'+l['1'][0][:42]+'^FS'
	    s+='^FO140,90^A0N,27,0^FD'+l['1'][0][42:84]+'^FS'
	    if self.p.sair_preco.GetValue():	s+='^FO140,150^ADN,30,20^FDR$'+l['1'][2]+'^FS'
	    #s+='^FO480,70^ADN,10,1^FD[ FABRICANTE ]^FS'
	    #s+='^FO480,90^ADN,10,1^FD'+l['1'][5]+'^FS'
	    #s+='^FO480,110^ADN,10,1^FD[ CODIGO INTERNO ]^FS'
	    #s+='^FO480,130^ADN,35,12^FD'+l['1'][3]+'^FS'
	    #s+='^FO480,170^ADN,1,1^FD[ ENDERECO ]^FS'
	    #s+='^FO480,190^ADN,1,1^FD'+l['1'][4]+'^FS'
	    codigo = l['1'][1] if l['1'][1] else l['1'][3]
	    s+='^FO440,150^A0N,27,0^FD'+'CODIGO: '+l['1'][3]+'^FS'
	    s+='^FO180,200^BY5,,120^BEN,80,Y,N^FD'+ codigo +'^FS'
	    s+='^XZ'

	elif tipo_etiqueta.strip()=='99': #--// [ Resetar e calibrar a impressora ]

	    s+='^XA'
	    s+='^LL200'
	    s+='^FO~JC^FS'
	    s+='^XZ'

	impressora = self.p.printers[self.p.impressoras.GetValue().split('-')[0]][1]
	printer_number = self.p.impressoras.GetValue().split('-')[0]

	simm,impressoras, user, prn = formas.listaprn(1)		
	pr = prn[printer_number]
	ip, port, tp = pr[10], pr[9], pr[11]
	if ip and port: #--// [ Emissao via IP ]

	    conn=psk.connectPrinter(self.p, ip, port, self.fl )
	    if conn[0]:
		
		conn[1].send(s)
		psk.closePrinter(conn[1])
	    return conn[0]

	else: #--// [ Emissao via CUPS ]

	    __arqvo = diretorios.usPasta+login.usalogin+"_etiqueta.zpl"
	    arquivo = open(__arqvo,"w")
	    arquivo.write(s)
	    arquivo.close()
	    if impressora.strip():	saida = commands.getstatusoutput("lpr -P"+impressora+" "+__arqvo)
	    else:	saida=[1,'Impressora nao localizada']

	    if saida[0]:	alertas.dia(self.p,'Erro no envio da impressao...\n'+ saida[1] +'\n'+(' '*180),'Impressao de etiquetas')

	    return True


    """ Impressora ARGOX """
class ArgoxPrinter:
    
    def parametrosArgox(self):
	
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
	
	return GT01+GT02+GT03+GT04+GT05+GT06+GT07+GT08+GT09+GT10+GT11+GT12+GT13+GT14
	
    def eTiqueTa01(self,prd):

	""" 1 Carreira 107 x 25 """
	_prd = prd.split('|')
	GT15 = '131100300700015'+login.emfantas+"  R$"+_prd[6]+"\n"
	GT16 = '121100300550015'+"Produto.: "+_prd[2]+"\n"
	GT17 = '121100400400015'+"Endereco: "+_prd[5]+"  { ["+_prd[3]+"] [ "+_prd[4]+"] }\n"
	GT18 = '121100300200015'+"Codigo..: "+_prd[0]+(" "*2)+"Barras: "+_prd[1]+"\n"
	GT19 = '1F2203500050015'+_prd[1]
	
	GT20 = 'Q0001\n' # +strzero(_quanti,4) // 0001'
	GT21 = 'E\n' #Ejetar

	return self.parametrosArgox() + GT15+GT16+GT17+GT18+GT19+GT20+GT21

    def eTiqueTa02(self,prd):
	
	""" 1 Carreira 107 x 25 """
	_prd = prd.split('|')

	codigo = _prd[0].strip()
	if _prd[1]:	codigo = _prd[1].strip()
	GT15 = '131100300750010'+login.emfantas+"\n"
	GT24 = '121200100800165'+'CODIGO:'+str( int( _prd[0] ) )+"\n"
	GT16 = '121100300540010'+"Fabricante: "+_prd[4].strip()+"\n"
	GT17 = '121100300650010'+"Produto: "+_prd[2].strip()+"\n"
	GT18 = '1F2203500050015'+codigo+"\n"
	GT19 = '121200100200120['+_prd[5].strip()+"]\n" #-: Endereco
	GT20 = '121100100090120['+_prd[3].strip()+"]\n" #-: Grupo
	GT21 = '131200100200218R$'+_prd[6]+" "+_prd[7]+"\n" #-: Preco

	GT22 = 'Q0001\n' # +strzero(_quanti,4) // 0001'
	GT23 = 'E\n' #Ejetar

	return self.parametrosArgox() + GT15+ GT24 +GT16+GT17+GT18+GT19+GT20+GT21+GT22+GT23

    def eTiqueTa03(self,prd):
	
	col = 18
	PT01 = PT02 = PT03 = PT04 = PT05= PT06=''
	for i in prd.split('\n'):
		
		_prd = i.split('|')
		if _prd[0] !='':

			PT01 += '111200700650'+str(col).zfill(3)+login.emfantas+"\n"
			PT02 += '121100700480'+str(col).zfill(3)+'CODIGO:'+str(  int(_prd[0])  )+"\n" 
			PT04 += '121100300290'+str(col).zfill(3)+_prd[2][:20]+"\n"
			if len(_prd[2])>20:	PT05 += '121100300170'+str(col).zfill(3)+_prd[2][20:40]+"\n"
			if len(_prd[2])>40:	PT06 += '121100300030'+str(col).zfill(3)+_prd[2][40:60]+"\n"
			col +=142
			
	GT15 = 'Q0001\n'			
	GT16 = 'E\n'

	return self.parametrosArgox() + PT01+PT02+PT03+PT04+PT05+PT06 +GT15+GT16

    def eTiqueTa04(self,prd):
	
	col = 0
	PT01 = PT02 = PT03 = PT04 = ''
	for i in prd.split('\n'):
		
		_prd = i.split('|')
		if _prd[0] !='':
			
			PT01 += '111100700420'+str((col+9)).zfill(3)+login.emfantas+"\n"
			PT02 += '111100700350'+str((col+9)).zfill(3)+_prd[2]+"\n" 
			PT03 += '121100300350'+str(col).zfill(3)+"R$ "+_prd[6]+"\n"
			PT04 += "1F1202000050"+str(col).zfill(3)+_prd[1]+"\n"
			col +=99
			
			
	GT15 = 'Q0004\n'			
	GT16 = 'E\n'
	return self.parametrosArgox() + PT01+PT02+PT03+PT04 +GT15+GT16

    def eTiqueTa05(self,prd):
	
	col = 0
	PT01 = PT02 = PT03 = PT04 = ''
	for i in prd.split('\n'):
		
		_prd = i.split('|')
		if _prd[0] !='':

			PT01 += '111100700420'+str((col+9)).zfill(3)+login.emfantas+"\n"
			PT02 += '111100700350'+str((col+9)).zfill(3)+_prd[2]+"\n" 
			PT03 += '121100300350'+str(col).zfill(3)+"R$ "+_prd[6]+"\n"
			PT04 += "1F1202000050"+str(col).zfill(3)+_prd[1]+"\n"
			col +=44
			
			
	GT15 = 'Q0004\n'			
	GT16 = 'E\n'

	return self.parametrosArgox() + PT01+PT02+PT03+PT04 + GT15+ GT16

    def eTiqueTa06(self,prd):
	
	col = 18
	PT01 = PT02 = PT03 = PT04 = PT05= PT06=''
	for i in prd.split('\n'):
		
		_prd = i.split('|')
		if _prd[0] !='':

			PT01 += '111200700720'+str(col).zfill(3)+login.emfantas+"\n"
			PT02 += '121100300600'+str(col).zfill(3)+_prd[2][:20]+"\n"
			if len(_prd[2])>20:	PT03 += '121100300480'+str(col).zfill(3)+_prd[2][20:40]+"\n"
			PT04 += '121100300340'+str(col).zfill(3)+"R$ "+_prd[6]+"\n"
			PT05 += "1F1202000030"+str(col).zfill(3)+_prd[1]+"\n"
			col +=142
			
	GT15 = 'Q0001\n'			
	GT16 = 'E\n'

	return self.parametrosArgox() + PT01+PT02+PT03+PT04+PT05+PT06 +GT15+GT16

    def eTiqueTa07(self,prd):
	
	""" 1 Carreira 100 x 50 """
	
	_prd = prd.split('|')
	GT15 = '151100301600025'+login.emfantas+"  R$ "+_prd[6]+"\n"
	GT16 = '131100301400025'+_prd[2]+"\n"

	GT17 = '131100401150025'+"Endereco..: "+_prd[5]+"\n"
	GT19 = '131100401150225'+"Fabricante: "+_prd[4]+"\n"
	GT18 = '131100400950025'+"Grrupo....: "+_prd[3]+"\n"

	GT20 = '131100400700240'+"CODIGO DO PRODUTO\n"
	GT21 = '141100400450240'+str(int(_prd[0]))+"\n"
	GT22 = '1F2405500150025'+_prd[1]+"\n"
	
	GT23 = 'Q0001\n' # +strzero(_quanti,4) // 0001'
	GT24 = 'E\n' #Ejetar

	return self.parametrosArgox() + GT15+GT16+GT17+GT18+GT19+GT20+GT21+GT22+GT23+GT24

    def eTiqueTa08(self,prd):
	
	""" 1 Carreira 100 x 50 """
	
	_prd = prd.split('|')
	
	GT15 = '151100302300025'+login.emfantas+"  R$ "+_prd[6]+"\n"
	GT16 = '131100302000025'+_prd[2]+"\n"

	GT17 = '131100401700025'+"Endereco..: "+_prd[5]+"\n"
	GT19 = '131100401500025'+"Fabricante: "+_prd[4]+"\n"
	GT18 = '131100401300025'+"Grrupo....: "+_prd[3]+"\n"
	GT20 = '131100401050025'+"CODIGO....: "+str(int(_prd[0]))+"\n"
	GT21 = ''
	GT22 = '1F3705500150025'+_prd[1]+"\n"
	
	GT23 = 'Q0001\n' # +strzero(_quanti,4) // 0001'
	GT24 = 'E\n' #Ejetar

	return self.parametrosArgox() + GT15+GT16+GT17+GT18+GT19+GT20+GT21+GT22+GT23+GT24

    def eTiqueTa09(self,prd):
        
	""" 1 Carreira 100 x 50 """
	
	_prd = prd.split('|')
	codigo = _prd[1] if _prd[1] else _prd[0]
	GT15 = '151100301250025'+login.emfantas+"  R$ "+_prd[6]+"\n"
	GT16 = '131100301050025'+_prd[2][:38]+"\n"
	GT17 = '131100300870025'+_prd[2][38:76]+"\n" if len(_prd[2]) > 38 else ''

	codigo_produto = str(int(_prd[0])) if _prd[0].isdigit() else _prd[0]
	GT18 = '131100300680045'+"CODIGO: "+ codigo_produto +"\n"
	GT19 = '' #'131100401150225'+"Fabricante: "+_prd[4]+"\n"
	GT20 = '' #'131100300850025'+"CODIGO DO PRODUTO:"+str(int(_prd[0]))+"\n"
	GT21 = '' #'131100400450240'+str(int(_prd[0]))+"\n"
	GT22 = '1F2503500100025'+codigo+"\n"

	GT23 = 'Q0001\n' # +strzero(_quanti,4) // 0001'
	GT24 = 'E\n' #Ejetar

	return self.parametrosArgox() + GT15+GT16+GT17+GT18+GT19+GT20+GT21+GT22+GT23+GT24

    def eTiqueTa10(self,prd):
	
	""" 1 Carreira 107 x 25 [ ]""" 
	_prd = prd.split('|')

	codigo = _prd[0].strip()
	if _prd[1]:	codigo = _prd[1].strip()
	GT24 = '131100300780030'+'CODIGO:'+str( int( _prd[0] ) )+"\n"
	GT17 = '121103000600030'+_prd[2].strip()+"\n"
	GT18 = '1F2303500030035'+codigo+"\n"
	GT21 = '131200100200238R$'+_prd[6]+" "+_prd[7]+"\n" #-: Preco

	GT22 = 'Q0001\n' # +strzero(_quanti,4) // 0001'
	GT23 = 'E\n' #Ejetar
	return self.parametrosArgox() + GT24 +GT17+GT18+GT21+GT22+GT23
    

class ImportcaoOrcamento(wx.Frame):
    
    def __init__(self, parent,id):
	
	self.p=parent
	self.filial=parent.fid

	wx.Frame.__init__(self, parent, id, 'Relação de orçamento', size=(800,302), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel = wx.Panel(self,-1)

	self.orcamentos_compras = Rorcamentos(self.painel, 10 ,pos=(12,1), size=(788,265),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

	self.orcamentos_compras.SetBackgroundColour('#557E8C')
	self.orcamentos_compras.SetForegroundColour("#000000")
	self.orcamentos_compras.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.painel.Bind(wx.EVT_PAINT,self.desenho)
	#self.orcamentos_compras.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.copiarDados)
	wx.StaticText(self.painel,-1,"Data inicial:",pos=(15, 280)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,"Data final:",pos=(200,280)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(75, 273), size=(110,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
	self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(255,273), size=(110,25))
	
	procurar=wx.BitmapButton(self.painel,200,wx.Bitmap("imagens/procurapp.png",wx.BITMAP_TYPE_ANY), pos=(375,270), size=(40,30))				
	voltar=wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/volta16.png",  wx.BITMAP_TYPE_ANY), pos=(420,270), size=(40,30))				
	importar=wx.BitmapButton(self.painel,202,wx.Bitmap("imagens/import16.png", wx.BITMAP_TYPE_ANY), pos=(465,270), size=(40,30))

	self.ftodos=wx.RadioButton(self.painel,-1,u"Filtrar filial\nLista todas as filias",pos=(510,267),style=wx.RB_GROUP)
	self.fatual=wx.RadioButton(self.painel,-1,u"Filtrar filial\nLista apenas a filial ["+self.filial+"]",  pos=(640,267))
	self.ftodos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.fatual.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))				

	self.ftodos.Bind(wx.EVT_RADIOBUTTON,self.relacionar)
	self.fatual.Bind(wx.EVT_RADIOBUTTON,self.relacionar)
	procurar.Bind(wx.EVT_BUTTON,self.relacionar)
	voltar.Bind(wx.EVT_BUTTON,self.sair)
	importar.Bind(wx.EVT_BUTTON,self.exportar)
	self.relacionar(wx.EVT_BUTTON)

    def sair(self,event):	self.Destroy()
    def relacionar(self,event):
	
	conn  = sqldb()
	sql   = conn.dbc("Produtos compras: Importar orcamentos", fil = self.filial, janela = self )

	if sql[0]:

	    registros=0
	    relacao={}

	    inicial=datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
	    final=datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

	    psq="SELECT cc_contro,cc_nomefo,cc_dtlanc,cc_filial FROM ccmp WHERE cc_tipoes='5' and cc_status='' and cc_dtlanc>='"+inicial+"' and cc_dtlanc<='"+final+"' ORDER BY cc_dtlanc"
	    if self.fatual.GetValue():	psq=psq.replace('WHERE','WHERE cc_filial="'+self.filial+'" and')
	    numero=sql[2].execute(psq)
    
	    for i in sql[2].fetchall():
		
		relacao[registros]=i[0],i[2].strftime("%d/%m/%Y"),i[3],i[1]
		registros +=1
	    
	    conn.cls(sql[1])

	    Rorcamentos.itemDataMap  = relacao
	    Rorcamentos.itemIndexMap = relacao.keys()
	
	    self.orcamentos_compras.SetItemCount(numero)

    def exportar(self,event):

	if not self.orcamentos_compras.GetItemCount():	alertas.dia(self,u"Lista de orçamento vazio...\n"+(" "*160),u'Produtos compras: Exportar orçamentos')
	else:
	    
	    controle=self.orcamentos_compras.GetItem(self.orcamentos_compras.GetFocusedItem(),0).GetText()
	    
	    conn=sqldb()
	    sql=conn.dbc("Produtos compras: Exportar orcamentos", fil = self.filial, janela = self )

	    if sql[0]:

		achar=sql[2].execute('SELECT * FROM iccmp WHERE ic_contro="'+controle+'"')
		result=sql[2].fetchall()
		conn.cls(sql[1])
		
		if not achar:	alertas.dia(self,u"Numero de controle selecionado, não foi localizado...\n"+(" "*160),u'Produtos compras: Exportar orçamentos')
		else:
		    ordems=1
		    indice=0
		    for i in result:
		    
			self.p.ListaCMP.InsertStringItem(indice,"-"+str( i[66] )+"-"+str(ordems).zfill(3)) #-: Incluir um novo produto

			self.p.ListaCMP.SetStringItem(indice,1, i[59])
			self.p.ListaCMP.SetStringItem(indice,2, i[5])
			self.p.ListaCMP.SetStringItem(indice,3, i[6])
			self.p.ListaCMP.SetStringItem(indice,4, str(i[10]))
			self.p.ListaCMP.SetStringItem(indice,5, i[9])
			self.p.ListaCMP.SetStringItem(indice,6, str(i[11]))
			self.p.ListaCMP.SetStringItem(indice,7, str(i[12]))
			self.p.ListaCMP.SetStringItem(indice,9, i[18])
			self.p.ListaCMP.SetStringItem(indice,10,i[7])
			self.p.ListaCMP.SetStringItem(indice,11,i[19])
			self.p.ListaCMP.SetStringItem(indice,12,i[20])
			self.p.ListaCMP.SetStringItem(indice,13,i[13])
			self.p.ListaCMP.SetStringItem(indice,14,str(i[14]))
			self.p.ListaCMP.SetStringItem(indice,15,str(i[15]))
			self.p.ListaCMP.SetStringItem(indice,16,i[21])
			self.p.ListaCMP.SetStringItem(indice,17,str(i[24]))
			self.p.ListaCMP.SetStringItem(indice,18,str(i[25]))
			self.p.ListaCMP.SetStringItem(indice,19,str(i[26]))
			self.p.ListaCMP.SetStringItem(indice,20,i[22])
			self.p.ListaCMP.SetStringItem(indice,21,str(i[27]))
			self.p.ListaCMP.SetStringItem(indice,22,str(i[28]))
			self.p.ListaCMP.SetStringItem(indice,23,str(i[29]))
			self.p.ListaCMP.SetStringItem(indice,24,str(i[30]))
			self.p.ListaCMP.SetStringItem(indice,25,i[23])
			self.p.ListaCMP.SetStringItem(indice,26,i[31])
			self.p.ListaCMP.SetStringItem(indice,27,str(i[32]))
			self.p.ListaCMP.SetStringItem(indice,28,str(i[33]))
			self.p.ListaCMP.SetStringItem(indice,29,str(i[34]))
			self.p.ListaCMP.SetStringItem(indice,34,i[35])
			self.p.ListaCMP.SetStringItem(indice,35,str(i[36]))
			self.p.ListaCMP.SetStringItem(indice,36,str(i[37]))
			self.p.ListaCMP.SetStringItem(indice,37,str(i[38]))
			self.p.ListaCMP.SetStringItem(indice,39,i[17])
			self.p.ListaCMP.SetStringItem(indice,41,i[59])
			self.p.ListaCMP.SetStringItem(indice,42,str(i[48]))
			self.p.ListaCMP.SetStringItem(indice,52,i[8])
			self.p.ListaCMP.SetStringItem(indice,60,i[46])
			self.p.ListaCMP.SetStringItem(indice,61,i[47])
			self.p.ListaCMP.SetStringItem(indice,69,str(i[49]))
			self.p.ListaCMP.SetStringItem(indice,70,i[50])
			self.p.ListaCMP.SetStringItem(indice,71,str(i[51]))
			self.p.ListaCMP.SetStringItem(indice,72,str(i[52]))
			self.p.ListaCMP.SetStringItem(indice,73,str(i[53]))
			self.p.ListaCMP.SetStringItem(indice,74,str(i[54]))
			self.p.ListaCMP.SetStringItem(indice,75,str(i[55]))
			self.p.ListaCMP.SetStringItem(indice,76,str(i[56]))
			self.p.ListaCMP.SetStringItem(indice,77,str(i[57]))
			self.p.ListaCMP.SetStringItem(indice,78,str(i[61]))

			self.p.ListaCMP.SetStringItem(indice,79,i[58])
			self.p.ListaCMP.SetStringItem(indice,81,str(i[60]))
			self.p.ListaCMP.SetStringItem(indice,89,str(i[62]))
			self.p.ListaCMP.SetStringItem(indice,90,str(i[63]))
			self.p.ListaCMP.SetStringItem(indice,91,str(i[64]))
			self.p.ListaCMP.SetStringItem(indice,92,str(i[65]))
			self.p.ListaCMP.SetStringItem(indice,93,i[66])
			self.p.ListaCMP.SetStringItem(indice,98,str(i[82]))

			self.p.ListaCMP.SetStringItem(indice,100, str(i[83]))
			self.p.ListaCMP.SetStringItem(indice,102, str(i[84]))
			self.p.ListaCMP.SetStringItem(indice,103, str(i[85]))
			self.p.ListaCMP.SetStringItem(indice,105, i[86])
			self.p.ListaCMP.SetStringItem(indice,111, i[89])
			self.p.ListaCMP.SetStringItem(indice,112, str(i[90]))
			self.p.ListaCMP.SetStringItem(indice,113, str(i[91]))

			ordems+=1
			indice+=1


		    self.p.ListaCMP.Refresh()
		    self.p.calculoTotais()
		    self.p.recalculaST()
		    self.p.evradio(wx.EVT_RADIOBUTTON)
		    self.p.ajusTar()

		    self.p.relerLista(wx.EVT_BUTTON)
		    self.p.ajusTarma()
		    self.sair(wx.EVT_BUTTON)
		    
    def desenho(self,event):

	dc = wx.PaintDC(self.painel)
      
	dc.SetTextForeground("#27A327") 	
	dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
	dc.DrawRotatedText(u"Importar orçamento { aprovietamento }", 0, 300, 90)
	
class Rorcamentos(wx.ListCtrl):

    itemDataMap  = {}
    itemIndexMap = {}

    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		  
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
	self.attr4 = wx.ListItemAttr()
	self.attr1.SetBackgroundColour("#F8F8E1")
	self.attr2.SetBackgroundColour("#3B7486")
	self.attr3.SetBackgroundColour("#597F8C")
	self.attr4.SetBackgroundColour("#D19595")

	self.InsertColumn(0, u'Numero de controle',format=wx.LIST_ALIGN_LEFT,width=120)
	self.InsertColumn(1, u'Data lançamento',format=wx.LIST_ALIGN_LEFT,width=120)
	self.InsertColumn(2, u'Filial',width=90)
	self.InsertColumn(3, u'Descrição do fornecedor',width=500)
		
    def OnGetItemText(self, item, col):

	try:
	    index      = self.itemIndexMap[item]
	    lista      = self.itemDataMap[index][col]
	    return lista

	except Exception, _reTornos:	pass
						
    def OnGetItemAttr(self, item): #Ajusta cores sim/nao

	if self.itemIndexMap:

	    index=self.itemIndexMap[item]
	    if item % 2:	return self.attr3
	    else:	return self.attr2

	else:	return None
		
    def OnGetItemImage(self, item):

	if self.itemIndexMap:

	    index=self.itemIndexMap[item]
	    return self.e_sim
		    
	else:	return self.e_sim
		
    def GetListCtrl(self):	return self


class MensagemQuimicos(wx.Frame):
    
    importar=False
    filial=None
    def __init__(self, parent,id):

	self.p=parent
	
	wx.Frame.__init__(self, parent, id, u'Produtos: Texto para impressão de químicos', size=(800,400), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel=wx.Panel(self,style=wx.BORDER_SUNKEN)		

	self.quimicos=wx.ListCtrl(self.painel, -1,pos=(0,0), size=(793,193),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

	self.quimicos.SetBackgroundColour('#7F7F7F')
	self.quimicos.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.Bind(wx.EVT_CLOSE, self.sair)
	self.quimicos.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
	
	self.quimicos.InsertColumn(0, u'Código',  width=80)
	self.quimicos.InsertColumn(1, u'Informações para impressão com vendas para químicos', width=3000)

	self.historico=wx.TextCtrl(self.painel,900,value='', pos=(0,200), size=(755,195),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
	self.historico.SetBackgroundColour('#4D4D4D')
	self.historico.SetForegroundColour('#90EE90')
	self.historico.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL))

	incluir=wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/adicionam.png", wx.BITMAP_TYPE_ANY), pos=(757,198), size=(40,45))				
	alterar=wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(757,250), size=(40,45))				
	apagar=wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/cancelar.png",  wx.BITMAP_TYPE_ANY), pos=(757,300), size=(40,45))				
	exporta=wx.BitmapButton(self.painel, 203, wx.Bitmap("imagens/importm.png",  wx.BITMAP_TYPE_ANY), pos=(757,350), size=(40,45))				

	if not self.importar:	exporta.Enable(False)
	elif   self.importar:
	    incluir.Enable(False)
	    alterar.Enable(False)
	    apagar.Enable(False)
	    
	incluir.Bind(wx.EVT_BUTTON, self.incluirAlterar)
	alterar.Bind(wx.EVT_BUTTON, self.incluirAlterar)
	apagar.Bind(wx.EVT_BUTTON, self.incluirAlterar)
	exporta.Bind(wx.EVT_BUTTON, self.exportarQuimicos)

	self.quimicos.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)

	self.selecionar()
	
    def sair(self,event):	self.Destroy()
    def exportarQuimicos(self,event):

	if self.quimicos.GetItem(self.quimicos.GetFocusedItem(),0).GetText():
	    self.p.importacaoQuimicosGravar( self.quimicos.GetItem(self.quimicos.GetFocusedItem(),0).GetText() )
	    self.Destroy()

    def incluirAlterar(self,event):

	if self.historico.GetValue().strip():
	    
	    ev=event.GetId()
	    e="{ Incluir uma nova menssagem }"
	    h=self.historico.GetValue().strip()
	    r=str(int(self.quimicos.GetItem(self.quimicos.GetFocusedItem(),0).GetText())) if self.quimicos.GetItem(self.quimicos.GetFocusedItem(),0).GetText() else ''
	    
	    if   ev==201:	e="{ Alterar a messagem selecioanda [Registro: "+r+"] }"
	    elif ev==202:	e="{ Apagar a menssagem selecionada [Registro: "+r+"] }"
	    
	    if ev==201 and not r:
		alertas.dia(self.painel,'Selecionar um registro valido p/alterar...\n'+(' '*140),u"Produtos: Messagem paraquímico")
		return

	    if ev==202 and not r:
		alertas.dia(self.painel,'Selecionar um registro valido p/apagar...\n'+(' '*140),u"Produtos: Messagem paraquímico")
		return

	    confima=wx.MessageDialog(self.painel,e+'\n\nConfirme para gravar...\n'+(" "*140),u"Produtos: Messagem paraquímico",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal()==wx.ID_YES:

		conn=sqldb()
		sql=conn.dbc("Produtos: Excluindo-Marcando", fil = self.filial, janela = self.painel )
		if sql[0]:
		    
		    if ev==200:
			sql[2].execute("INSERT INTO grupofab (fg_cdpd,fg_info) VALUES('Q','"+h+"')")
			sql[1].commit()
		
		    elif ev==201 and r:

			sql[2].execute("UPDATE grupofab SET fg_info='"+h+"' WHERE fg_regi='"+r+"'")
			sql[1].commit()

		    elif ev==202:
			sql[2].execute("DELETE FROM grupofab WHERE fg_regi='"+r+"'")
			sql[1].commit()

		    conn.cls(sql[1])

		    self.selecionar()

    def passagem(self,even):
	
	if self.quimicos.GetItemCount():	self.historico.SetValue(self.quimicos.GetItem(self.quimicos.GetFocusedItem(),1).GetText())
	    

    def selecionar(self):
	
	conn=sqldb()
	sql=conn.dbc("Produtos: Messagem quimicos", fil = self.filial, janela = self.painel )
	if sql[0]:
	    
	    if sql[2].execute("SELECT fg_regi,fg_info FROM grupofab WHERE fg_cdpd='Q'"):
		
		result=sql[2].fetchall()
		indice=0
		conn.cls(sql[1])
		
		self.quimicos.DeleteAllItems()
		self.quimicos.Refresh()
		
		for i in result:

		    self.quimicos.InsertStringItem( indice, str(i[0]).zfill(8) )
		    self.quimicos.SetStringItem( indice, 1, i[1] )
		    indice+=1
		
		self.quimicos.Refresh()
