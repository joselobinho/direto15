#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 16-09-2014 10:59
# Jose Lobinho
import wx
import pyboleto

from pyboleto.bank.caixa import BoletoCaixa
from pyboleto.bank.bancodobrasil import BoletoBB
from pyboleto.bank.itau import BoletoItau
from pyboleto.bank.bradesco import BoletoBradesco
from pyboleto.bank.santander import BoletoSantander
from pyboleto.bank.real import BoletoReal
from pyboleto.bank.hsbc import BoletoHsbc
from pyboleto.bank.banrisul import BoletoBanrisul

from pyboleto.pdf import BoletoPDF
from conectar import diretorios,numeracao,login,gerenciador,truncagem,sqldb,dialogos,listaemails
from decimal  import *

import datetime
import os
import decimal

alertas = dialogos()
lemails = listaemails()

class GerarBoletoBancario:

	Filial = ""
	def Gerar_boletos(self,_par):

		""" Lista de Bancos Suportados
			001-Banco Brasil 033-Santander 041-Barinsul 104-CaixaEconomica 237-Bradesco 341-Itau 356-Real 399-HSBC
		"""

		""" Recebe Informacoes do Contas Areceber """
		indiceConta = _par.ListaReceber.GetFocusedItem()
		RegisTConta = _par.ListaReceber.GetItemCount()
		indiceBanco = _par.ListaBancos.GetFocusedItem()
		CodigoIDBan = str( _par.ListaBancos.GetItem(indiceBanco,8).GetText() )
		codigo_clie = _par.ListaReceber.GetItem(indiceConta,11).GetText().strip() #-: Codigo do cliente
		PrintaGrupo = _par.bolGru.GetValue()
		email_clien = []
	
		_banco = str( _par.ListaBancos.GetItem(indiceBanco,0).GetText() )
		
		__lisTaBancos = ["001","033","041","104","237","341","356","399"]
		if _banco in __lisTaBancos:

			conn = sqldb()
			sql  = conn.dbc("Emissão de Boletos", fil = self.Filial, janela = _par )
			grv  = True
			
			if sql[0] == True:

				self.numer = numeracao()
				self.forma = truncagem()
				
				if PrintaGrupo == False:	RegisTConta = 1
				if PrintaGrupo == True:	indiceConta = 0

				if RegisTConta > 10:	_demostrar = ['Relacao de Documentos e Vencimentos { Apenas os 10 Primeiros Lancamentos... }','']
				else:	_demostrar = ['Relacao de Documentos e Vencimentos:','']

				if codigo_clie:	email_clien = lemails.listar( 1, codigo_clie, sql[2] )
				
				""" Relacionar os Documentos Antes Para colocar no demonstrativo """
				if PrintaGrupo == True:
					
					indice = 0
					Linhas = 1
					for b in range(RegisTConta):

						_boleto = _par.ListaReceber.GetItem(indice,7).GetText()[:2]
						_aberto = _par.ListaReceber.GetItem(indice,8).GetText()

						if _boleto == '06' and _aberto == '':
						
							__nfe = ''
							nfcoo = _par.ListaReceber.GetItem(indice,31).GetText().split('-')
							if nfcoo[0] !='':	__nfe = " NF: "+nfcoo[0].zfill(9)
							if nfcoo[0] == '' and nfcoo[1] !='':	__nfe = " COO: "+nfcoo[1].zfill(9)
							
							nDav = _par.ListaReceber.GetItem(indice,0).GetText()
							_demostrar.append('No: '+str(Linhas).zfill(2)+' DAV: '+str(nDav)+__nfe+' Vencimento: '+str(_par.ListaReceber.GetItem(indice,3).GetText())+" Valor: "+str( _par.ListaReceber.GetItem(indice,5).GetText() ) )
							Linhas +=1

						indice +=1
						
						if Linhas > 10:	break
						
				else:
					
					__nfe = ''
					nfcoo = _par.ListaReceber.GetItem(indiceConta,31).GetText().split('-')
					if nfcoo[0] !='':	__nfe = " NF: "+nfcoo[0].zfill(9)
					if nfcoo[0] == '' and nfcoo[1] !='':	__nfe = " COO: "+nfcoo[1].zfill(9)
					
					_demostrar.append('No 01 DAV: '+str( _par.ListaReceber.GetItem( indiceConta, 0 ).GetText())+ __nfe +' Vencimento: '+str( _par.ListaReceber.GetItem(indiceConta,3).GetText() )+" Valor: "+str( _par.ListaReceber.GetItem(indiceConta,5).GetText() ) )
				""" F I M  da Relacao de Documentos """

				""" Pesquisa as Instrucoes"""
				_instrucao = []
				_ins = "SELECT fr_insbol,fr_bancof,fr_agenci,fr_contac,fr_cartei FROM fornecedor WHERE fr_regist='"+str( CodigoIDBan )+"'"
				
				_ach = sql[2].execute(_ins)
				bbol = ''
				if _ach !=0:
					
					rs = sql[2].fetchall()
					bbol = rs[0][1]+' '+rs[0][2]+' '+rs[0][3]+' '+rs[0][4]
					
					if rs[0][0] !=None and rs[0][0] !='':
						
						Linhas = 1
						_insTru = rs[0][0].split("\n")
						for s in _insTru:

							_instrucao.append(s)
							Linhas +=1

							if Linhas > 7:	break
				
				
				self.listaDados = []
				nTiTulos   = 0
				arquivo    = ''
				
				for i in range(RegisTConta):

					_boleto = _par.ListaReceber.GetItem(indiceConta,7).GetText()[:2]
					_aberto = _par.ListaReceber.GetItem(indiceConta,8).GetText()

					if _boleto == '06' and _aberto == '':

						""" Busca o Cliente """
						scNome = str( _par.ListaReceber.GetItem(indiceConta,4).GetText() )
						scCNPJ = str( self.forma.formata( 1, _par.ListaReceber.GetItem(indiceConta,6).GetText() ) )
						scEnde = scCom1 = scBair = scCida = scCepe = scEsta = ''
						
						codigoClien = _par.ListaReceber.GetItem(indiceConta,11).GetText()

						pesquisaCli = "SELECT * FROM clientes WHERE cl_codigo='"+str( codigoClien )+"'"
						if sql[2].execute(pesquisaCli) !=0:
							
							rsClie = sql[2].fetchall()
							
							scNome = str( rsClie[0][1] )
							scCNPJ = str( self.forma.formata( 1, rsClie[0][3] ) )
							scEnde = str( rsClie[0][8] )
							scCom1 = str( rsClie[0][13]+' '+rsClie[0][14] )
							scBair = str( rsClie[0][9] )
							scCida = str( rsClie[0][10] )
							scCepe = str( rsClie[0][12] )
							scEsta = str( rsClie[0][15] )
					
						try:
							
							nTiTulos +=1 #-: Contabiliza Titulos Validos
							
							""" Nosso Numero { Se Ja Tiver Nosso Numero Cadastrado Utilizar !! [ Nao Criar Novo] }"""
							if _par.ListaReceber.GetItem(indiceConta,45).GetText() == '':
								
								finding    = sql[2].execute("SELECT pr_bole FROM parametr where pr_regi=1")
								__valor    = sql[2].fetchall()
								NossoNumer = ( int(__valor[0][0] +1 ) )
								ajuste = "UPDATE parametr SET pr_bole=%s WHERE pr_regi=%s"
								sql[2].execute(ajuste,(NossoNumer,1))
								sql[1].commit()
							
							#--: Reaproveitamento do Nosso Numero
							elif _par.ListaReceber.GetItem(indiceConta,45).GetText() !='':	NossoNumer = str( _par.ListaReceber.GetItem(indiceConta,45).GetText() )
				
							""" F I M Nosso Numero """

							#-------------: Area de Informacoes e Dados do Boleto
							fl = login.filialLT[ self.Filial ]
							_endereco = str( fl[2] +' '+ fl[7] +' '+ fl[8] +' '+ fl[3] +' '+ fl[4] +' '+ fl[6] +' '+ fl[5] )
							NumeroDAV = _par.ListaReceber.GetItem(indiceConta,0).GetText()

							convenio         = str( _par.ListaBancos.GetItem(indiceBanco,5).GetText() ) #'7777777'
							especie_documento= str( _par.ListaBancos.GetItem(indiceBanco,6).GetText() ) #'DM'

							if _banco != "033":	carteira = str( _par.ListaBancos.GetItem(indiceBanco,7).GetText() ) # '18'
							else:	carteira = ''

							cedente          = str( fl[1] ) #'Empresa ACME LTDA'
							cedente_documento= str( self.forma.formata( 1,login.cnpj ) ) #"102.323.777-01"
							cedente_endereco = _endereco #"Rua Acme, 123 - Centro - Sao Paulo/SP - CEP: 12345-678"
							agencia_cedente  = str( _par.ListaBancos.GetItem(indiceBanco,1).GetText() ) # '9999'
							conta_cedente    = str( _par.ListaBancos.GetItem(indiceBanco,2).GetText() ).split('-')[0] # '99999'
						
							_vencimento = datetime.datetime.strptime(str(_par.ListaReceber.GetItem(indiceConta,3).GetText()), "%d/%m/%Y").date()
							_daTaDocume = datetime.datetime.strptime(str(_par.ListaReceber.GetItem(indiceConta,1).GetText()), "%d/%m/%Y").date()
							_daTaHoje   = datetime.datetime.now().date()
							
							valor_documento = Decimal( _par.ListaReceber.GetItem(indiceConta,5).GetText().replace(',','') )

							_sacado = [
								"%s" % ( scNome +' CPF/CNPJ: '+scCNPJ ),
								"%s" % ( scEnde +' '+scCom1+' CEP: '+scCepe),
								"%s" % ( scBair +' '+scCida+'  [ '+scEsta+' ]' )
								]

							numero_carteira = NossoNumer,NumeroDAV,carteira
							dados_cendente  = cedente, cedente_documento, cedente_endereco, agencia_cedente, conta_cedente   
							vencimentosdata = _vencimento, _daTaDocume, _daTaHoje  
							convenioespecie = convenio, especie_documento
							demostrarvalor  = _demostrar, valor_documento

							self.gerarBoletoBancario( banco = _banco, carteira = numero_carteira, cedente = dados_cendente, datas = vencimentosdata, sacado = _sacado, convenio = convenioespecie, instrucao=_instrucao, valor = demostrarvalor )

							""" Atualiza o Nosso Numero no Contas Areceber """
							_nDav  = str( NumeroDAV  ).split('/')[0]
							_nPar  = str( NumeroDAV  ).split('/')[1]
							EMD = datetime.datetime.now().strftime("%Y/%m/%d")
							DHO = datetime.datetime.now().strftime("%T")

							_nosso = "UPDATE receber SET rc_nosson=%s,rc_bcobol=%s,rc_dtbole=%s,rc_hobole=%s WHERE rc_ndocum=%s and rc_nparce=%s"
							nosson = sql[2].execute(_nosso,(str( NossoNumer ),bbol, EMD,DHO,_nDav, _nPar))
							sql[1].commit()

						except Exception as _reTornos:  
							print "_________________: ",type( _reTornos )
							print "=================: ",_reTornos
							#if type( _reTornos ) == str:	_reTornos = _reTornos.decod("UTF-8")
							#alertas.dia(_par,u"Erro na confecção do boleto...\n\nRetorno:\n"+ _reTornos +"\n"+(" "*120),u"Contas Areceber: Emissção de Boleto")

					indiceConta +=1

				try:
					
					#---------: Gravacao do Boleto
					if nTiTulos != 0:
						
						if RegisTConta == 1:	arquivo = diretorios.usPasta+"boleto_"+str(NossoNumer)+".pdf"
						else:	arquivo = diretorios.usPasta+"boletoGrupo_"+str(NossoNumer)+".pdf"
						boleto  = BoletoPDF(arquivo)

						""" Dividir em paginas """

						for i in range( len( self.listaDados ) ):

							boleto.drawBoleto( self.listaDados[i] )
							boleto.nextPage()
							
						boleto.save()
						
				except Exception as _reTornos:
					grv = False

				conn.cls(sql[1])

				if not grv:	alertas.dia(_par,"Erro-Gravando na confecção do boleto...\n\nRetorno:\n"+str(_reTornos)+"\n"+(" "*140),"Contas Areceber: Emissção de Boleto")

				if arquivo and os.path.exists(arquivo) and grv:
					
					_par.selecionar(wx.EVT_BUTTON)
					self.ImpressaoVisualizacao(arquivo,_par, email = email_clien)
	
		else:
			_suportados = "001 - Banco Brasil\n033 - Santander\n041 - Barinsul\n104 - Caixa Economica\n237 - Bradesco\n341 - Itau\n356 - Real\n399 - HSBC"
			alertas.dia(_par,u"Banco: "+str(_banco)+", não suportado...\n\n\nLista de Bancos Suportados pelo Sistema:\n"+_suportados+"\n"+(" "*100),"Contas Receber: Emissão de Boletos")


	def geraBoletoNossoCliente(self, par, parent ):

		p = parent

		lancamentos_selecionados = 0
		dados_banco = 0
		dados_boleto = 0
		lista_boleto = []
		
		for i in range( p.contasreceber.GetItemCount() ):
			
			if p.contasreceber.GetItem( i, 11 ).GetText().strip():	lancamentos_selecionados +=1
			if len( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|') ) <= 1:	dados_banco +=1
			if len( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|') ) <= 1:	dados_boleto +=1

		if not lancamentos_selecionados:	alertas.dia( par,"Nenhum lançamento selecionado para gerar boleto...\n"+(" "*140),"Contas areceber: Gerar boletos")
		if dados_banco:	alertas.dia( par,"Banco não definido para gerar boleto...\n"+(" "*140),"Contas areceber: Gerar boletos")
		if dados_boleto:	alertas.dia( par,"Dados do boleto não definido para gerar boleto...\n"+(" "*140),"Contas areceber: Gerar boletos")
		else:
			
			ced_doc = str( login.cadcedente.split('|')[0].split(";")[0] )
			ced_des = str( login.cadcedente.split('|')[0].split(";")[1] )
			ced_end = str( login.cadcedente.split('|')[0].split(";")[2] )
			ced_cmp = str( login.cadcedente.split('|')[0].split(";")[3] )
			ced_bai = str( login.cadcedente.split('|')[0].split(";")[4] )
			ced_cid = str( login.cadcedente.split('|')[0].split(";")[5] )
			ced_est = str( login.cadcedente.split('|')[0].split(";")[6] )
			ced_cep = str( login.cadcedente.split('|')[0].split(";")[7] )
			"""  Servidor de email  """
			ced_smt = str( login.cadcedente.split('|')[1].split(";")[0] )
			ced_usa = str( login.cadcedente.split('|')[1].split(";")[1] )
			ced_emr = str( login.cadcedente.split('|')[1].split(";")[2] )
			ced_sen = str( login.cadcedente.split('|')[1].split(";")[3] )
			ced_prt = str( login.cadcedente.split('|')[1].split(";")[4] )
			
			
			data_hoje = datetime.datetime.now().date()
			arquivo = ''
			listabl = []
			for i in range( p.contasreceber.GetItemCount() ):
				
				if p.contasreceber.GetItem( i, 11 ).GetText().strip():

					""" Dados do banco """
					ban_num = str( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[0].strip() )
					ban_age = str( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[1].strip() )
					ban_coc = str( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[2].split("-")[0].strip() )
					ban_car = str( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[3].strip() )
					ban_emp = str( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[7].strip() ).split(';')

					"""  Se os dados do cente no cadastro de bancos estiver preenchido o sistema usa ele se nao usa o do cadastro de cedente  """
					if ban_emp:	ced_des, ced_doc, ced_end = ban_emp
					
					
					"""  Bradesco utiliza o digito da conta   """
					if ban_num == '237':	ban_coc = str( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[2].strip() )
					if ban_num == '237':	ban_car = str( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[3].strip() ).zfill(2)

					ban_cvn = str( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[4].strip() )
					ban_esp = str( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[5].strip() )
					ban_ins = str( p.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[6].strip() )
					
					""" Dados do cedente  """
					cl_idcl = str( p.contasreceber.GetItem( i,  0 ).GetText().strip() )
					cl_nome = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[0].strip()  )
					cl_fant = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[1].strip()  )
					cl_docu = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[2].strip()  )
					cl_ende = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[3].strip()  )
					cl_bair = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[4].strip()  )
					cl_cida = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[5].strip()  )
					cl_ibge = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[6].strip()  )
					cl_ceps = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[7].strip()  )
					cl_cmp1 = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[8].strip()  )
					cl_cmp2 = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[9].strip()  )
					cl_esta = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[10].strip() )
					cl_emai = str( p.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[11].strip() )

					cl_serv = str( p.contasreceber.GetItem( i, 16 ).GetText().strip() )

					id_cliente_creceber = str( p.contasreceber.GetItem( i, 0 ).GetText().strip() )
					lancamento_nosso_numero = str( int( p.contasreceber.GetItem( i, 1 ).GetText().strip() ) )
					valor_documento = Decimal( p.contasreceber.GetItem( i, 6 ).GetText().strip().replace(',','') )

					venci_bole = str( p.contasreceber.GetItem( i, 5 ).GetText().strip() )
					vencimento = datetime.datetime.strptime( p.contasreceber.GetItem( i, 5 ).GetText().strip(), "%d/%m/%Y").date()
					data_docum = datetime.datetime.strptime( p.contasreceber.GetItem( i,14 ).GetText().strip(), "%d/%m/%Y").date()
					

					sacado  = [
						"%s" % ( cl_nome +' CPF/CNPJ: '+cl_docu ),
						"%s" % ( cl_ende +' '+cl_cmp1+' '+cl_cmp2+' CEP: '+cl_ceps),
						"%s" % ( cl_bair +' '+cl_cida+'  [ '+cl_esta+' ]' )
						]

					instru = []
					linhas = 0

					if cl_serv:
						instru.append( cl_serv )
						instru.append( ' ' )

					for s in ban_ins.split('\n'):
						
						instru.append(s)
						linhas +=1
						if linhas == 6:	break


					dados_cendente  = ced_des, ced_doc, ced_end, ban_age, ban_coc
					numero_carteira = lancamento_nosso_numero, str( lancamento_nosso_numero).zfill(10),ban_car
					vencimentosdata = vencimento, data_docum, data_hoje 
					convenioespecie = ban_cvn, ban_esp
					demostrarvalor  = ["Lancamento 01-Individualizado ID-Cliente: "+id_cliente_creceber], valor_documento

					self.listaDados = []
					self.gerarBoletoBancario( banco = ban_num, carteira = numero_carteira, cedente = dados_cendente, datas = vencimentosdata, sacado = sacado, convenio = convenioespecie, instrucao=instru, valor = demostrarvalor )

					arquivo = diretorios.usPasta+"cobranca_"+str( cl_idcl )+".pdf"
					boleto  = BoletoPDF( arquivo )

					boleto.drawBoleto( self.listaDados[0] )
					boleto.nextPage()
							
					boleto.save()
					
					lista_boleto.append( cl_nome+';'+venci_bole+';'+cl_emai+';'+arquivo+";"+cl_serv )

		
		return lista_boleto


	def geraBoletonoCliente(self, par, parent, bc = "", bo = "" ):

		p = parent
		self.listaDados = []
			
		ced_doc = str( login.cadcedente.split('|')[0].split(";")[0] )
		ced_des = str( login.cadcedente.split('|')[0].split(";")[1] )
		ced_end = str( login.cadcedente.split('|')[0].split(";")[2] )
		ced_cmp = str( login.cadcedente.split('|')[0].split(";")[3] )
		ced_bai = str( login.cadcedente.split('|')[0].split(";")[4] )
		ced_cid = str( login.cadcedente.split('|')[0].split(";")[5] )
		ced_est = str( login.cadcedente.split('|')[0].split(";")[6] )
		ced_cep = str( login.cadcedente.split('|')[0].split(";")[7] )

		"""  Servidor de email  """
		ced_smt = str( login.cadcedente.split('|')[1].split(";")[0] )
		ced_usa = str( login.cadcedente.split('|')[1].split(";")[1] )
		ced_emr = str( login.cadcedente.split('|')[1].split(";")[2] )
		ced_sen = str( login.cadcedente.split('|')[1].split(";")[3] )
		ced_prt = str( login.cadcedente.split('|')[1].split(";")[4] )
			
		data_hoje = datetime.datetime.now().date()

		""" Dados do banco """
		ban_num = str( bc.strip().split('|')[0].strip() )
		ban_age = str( bc.strip().split('|')[1].strip() )
		ban_coc = str( bc.strip().split('|')[2].split("-")[0].strip() )
		ban_car = str( bc.strip().split('|')[3].strip() )

		"""  Bradesco utiliza o digito da conta   """
		if ban_num == '237':	ban_coc = str( bc.strip().split('|')[2].strip() )
		if ban_num == '237':	ban_car = str( bc.strip().split('|')[3].strip() ).zfill(2)
        
		ban_cvn = str( bc.strip().split('|')[4].strip() )
		ban_esp = str( bc.strip().split('|')[5].strip() )
		ban_ins = str( bc.strip().split('|')[6].strip() )
					
		""" Dados do cedente  """
		i = p.ListaBoleto.GetFocusedItem()
		cl_idcl = str( p.ListaBoleto.GetItem( i,  7 ).GetText().strip() )
		
		cl_nome = str( bo.strip().split('|')[0].strip()  )
		cl_fant = str( bo.strip().split('|')[1].strip()  )
		cl_docu = str( bo.strip().split('|')[2].strip()  )
		cl_ende = str( bo.strip().split('|')[3].strip()  )
		cl_bair = str( bo.strip().split('|')[4].strip()  )
		cl_cida = str( bo.strip().split('|')[5].strip()  )
		cl_ibge = str( bo.strip().split('|')[6].strip()  )
		cl_ceps = str( bo.strip().split('|')[7].strip()  )
		cl_cmp1 = str( bo.strip().split('|')[8].strip()  )
		cl_cmp2 = str( bo.strip().split('|')[9].strip()  )
		cl_esta = str( bo.strip().split('|')[10].strip() )
		cl_emai = str( bo.strip().split('|')[11].strip() )

		id_cliente_creceber = str( p.ListaBoleto.GetItem( i,  7 ).GetText().strip() )
		lancamento_nosso_numero = int( p.ListaBoleto.GetItem( i, 6 ).GetText().strip() )
		valor_documento = Decimal( p.ListaBoleto.GetItem( i, 3 ).GetText().strip().replace(',','') )
		
		
		venci_bole = str( p.ListaBoleto.GetItem( i, 2 ).GetText().strip() )
		vencimento = datetime.datetime.strptime( p.ListaBoleto.GetItem( i, 2 ).GetText().strip(), "%d/%m/%Y").date()
		data_docum = datetime.datetime.strptime( p.ListaBoleto.GetItem( i, 8 ).GetText().strip(), "%d/%m/%Y").date()
        
		sacado  = [
		"%s" % ( cl_nome +' CPF/CNPJ: '+cl_docu ),
		"%s" % ( cl_ende +' '+cl_cmp1+' '+cl_cmp2+' CEP: '+cl_ceps),
		"%s" % ( cl_bair +' '+cl_cida+'  [ '+cl_esta+' ]' )
		]

		instru = []
		linhas = 0
		for s in ban_ins.split('\n'):
						
			instru.append(s)
			linhas +=1
			if linhas == 6:	break

		dados_cendente  = ced_des, ced_doc, ced_end, ban_age, ban_coc
		numero_carteira = lancamento_nosso_numero, str( lancamento_nosso_numero).zfill(10),ban_car
		vencimentosdata = vencimento, data_docum, data_hoje 
		convenioespecie = ban_cvn, ban_esp
		demostrarvalor  = ["Lancamento 01-Individualizado ID-Cliente: "+id_cliente_creceber], valor_documento

		self.gerarBoletoBancario( banco = ban_num, carteira = numero_carteira, cedente = dados_cendente, datas = vencimentosdata, sacado = sacado, convenio = convenioespecie, instrucao=instru, valor = demostrarvalor )
        
		arquivo = diretorios.usPasta+"cobranca_"+str( cl_idcl )+".pdf"
		boleto  = BoletoPDF( arquivo )
        
		boleto.drawBoleto( self.listaDados[0] )
		boleto.nextPage()
							
		boleto.save()
		if arquivo:	self.ImpressaoVisualizacao( arquivo, par, email = '' )

		
	def gerarBoletoBancario(self, banco='', carteira='', cedente='', datas='', sacado='', convenio='', instrucao='', valor = '0.00' ):
		
		""" Dados Exclusivo do BB """
		if banco == "001":

			d = BoletoBB(7, 2)
			d.convenio         = convenio[0]
			d.especie_documento= convenio[1] #'DM'

		""" Exclusivo do Santander """
		if banco == "033":
			d = BoletoSantander()
			d.ios = '0'
		
		if banco == "041":	d = BoletoBanrisul()	
		if banco == "104":	d = BoletoCaixa()
		if banco == "237":	d = BoletoBradesco()
		if banco == "341":	d = BoletoItau()
		if banco == "356":	d = BoletoReal()
		if banco == "399":	d = BoletoHsbc()

		d.nosso_numero     = str( carteira[0] ) # '87654'
		d.numero_documento = str( carteira[1] ) # '27.030195.10'
		if banco != "033":	d.carteira = str( carteira[2] ) # '18'

		d.especie_documento= convenio[1]
		
		d.cedente          = cedente[0] #'Empresa ACME LTDA'
		d.cedente_documento= cedente[1] #"102.323.777-01"
		d.cedente_endereco = cedente[2] #"Rua Acme, 123 - Centro - Sao Paulo/SP - CEP: 12345-678"
		d.agencia_cedente  = cedente[3] # '9999'
		d.conta_cedente    = cedente[4] # '99999'
		
		d.data_vencimento    = datas[0] # datetime.date(2010, 3, 27)
		d.data_documento     = datas[1] # datetime.date(2010, 2, 12)
		d.data_processamento = datas[2] # datetime.date(2010, 2, 12)
		
		""" Instrucao """
		d.instrucoes = instrucao
		""" Vc pode dar for antes e relacionar todos os documento e depois encaixar aqui!!! """
		d.demonstrativo   = valor[0] #'' #valor[0]
		d.valor_documento = valor[1] #Decimal( valor[1].replace(',','') )
		
		d.sacado = sacado


		#print "Convenio..........: ",convenio[0], type( convenio[0])
		#print "Especie...........: ",convenio[1], type( convenio[1])
		#print "Nosso numero......: ",carteira[0], type( carteira[0])
		#print "Numero documento..: ",carteira[1], type( carteira[1])
		#print "Carteira..........: ",carteira[2], type( carteira[2])
		#print "Cedente...........: ",cedente[0], type( cedente[0])
		#print "Cedente documento.: ",cedente[1], type( cedente[1])
		#print "Cedente endereco..: ",cedente[2], type( cedente[2])
		#print "Cedente agencia...: ",cedente[3], type( cedente[3])
		#print "Cedente conta.....: ",cedente[4], type( cedente[4])
		#print "Data vencimento...: ",datas[0], type(datas[0] )
		#print "Data documento....: ",datas[1], type(datas[1] )
		#print "Data processamento: ",datas[2], type(datas[2] )
		#print "Instrucao.........: ",instrucao, type( instrucao)
		#print "Demonstrativo.....: ",valor[0], type(valor[0] )
		#print "Valor documento...: ",valor[1], type(valor[1] )
		#print "Sacado............: ",sacado, type(sacado )


		self.listaDados.append(d)

		
	def ImpressaoVisualizacao(self,_arquivo,par, email=''):

		gerenciador.Anexar = _arquivo

		gerenciador.secund = ''
		gerenciador.emails = email
		gerenciador.TIPORL = ''
		gerenciador.Filial = self.Filial
			
		ger_frame=gerenciador(parent=par,id=-1)
		ger_frame.Centre()
		ger_frame.Show()
