#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  nfceleo40.py
#  Inicio: 10-09-2018 09:43 Jose de almeida lobinho
#  Utilizando a lib do leodata
import wx
import datetime
import requests
import os,sys
import wx.html as html
from random import randint

from xml.dom import minidom
from decimal import Decimal
from unicodedata import normalize
from lxml import etree
from time import strftime
requests.packages.urllib3.disable_warnings()

from conectar import login,dialogos,menssagem, numeracao, diretorios, sqldb, MostrarHistorico, gerenciador, emailenviar, truncagem, formasPagamentos
from danfepdf  import danfeGerar,DanfeMdfe

from eletronicos.manutencao import ManutencaoSefaz, NotaFiscalParametros
from eletronicos.notafiscal400 import PreenchimentoNotaFiscal,ImpostoExcessivo
from eletronicos.__init__ import CODIGOS_UF,CODIGO_PAIS
from collections import OrderedDict

alertas = dialogos()
mens = menssagem()

numeros = numeracao()
montar_danfe = danfeGerar()
montar_mdfe=DanfeMdfe()
enviar_email = emailenviar()
Truncar = truncagem()

msf = ManutencaoSefaz()
nF  = formasPagamentos()
nfe400 = PreenchimentoNotaFiscal()
nfe400imposto = ImpostoExcessivo()

class Eventos:

#---{ Eventos }-------------------------------------------------// Status do sevidor	
	def status( self, parent, dados ):
	    
		retorno, uf, ambiente, serie_nfe, serie_nfce, regime, cnpj = informes.dadosIdentificacao( dados[0], parent, modelo=dados[1], gravar = False)
		if not retorno: return
		_mensagem = mens.showmsg("STATUS: Comunicando com o servidor da SEFAZ\n\nAguarde...")

		NotaFiscalParametros.contingencia_enviar = False
		try:

			_mensagem = mens.showmsg("STATUS: Comunicando com o servidor da SEFAZ\n\nAguarde...")
			status = OrderedDict([
				('tpAmb',ambiente),
				('cUF',CODIGOS_UF[uf]),
				('xServ','STATUS')
			])

			xml = msf.statusNFs( status )
			del _mensagem
			rt = informes.retornosSefaz( xml, ["retConsStatServ"], parent, nome_evento = 'STATUS-Lykos', modelo=None, contingencia=False )
			if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], 1, dados[1], rt[4], '', dados[0], '', '', '', None, False )

		except Exception as erro:

			_mensagem = mens.showmsg("STATUS ERROR: Comunicando com o servidor da SEFAZ\n\nAguarde...")
			if type( erro ) !=unicode:	erro = str( erro ).encode('utf-8')
			del _mensagem
			alertas.dia( parent, u"[ Enviando requisição de status a sefaz {  filial "+ dados[0] +" NFCe 4.0 } ]\n\n[ ERROR ]: "+ erro +"\n"+(" "*180),u"Status do servidor da sefaz" )

	def consultarCadastro(self, parent, filial ):

		retorno, uf, ambiente, serie_nfe, serie_nfce, regime,cnpj = informes.dadosIdentificacao( filial, parent, gravar = True)
		if not retorno: return
				
		_mensagem = mens.showmsg("CONSULTA CADASTRO: Comunicando com o servidor da SEFAZ\n\nAguarde...")
		dados_consultar = OrderedDict([
				('xServ','CONS-CAD'),
				('UF',uf),
				('CNPJ',cnpj)
				])

		xml_retorno = msf.consultaCadastro( dados_consultar )

		del _mensagem
		rt = informes.retornosSefaz( xml_retorno, ["soap:Reason","infCons"], parent, nome_evento = 'CONSULTA CADASTRO-Lykos', modelo=None )
		if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1],   rt[2], 1,'',rt[4],'',filial, '', '', '', None, False )

#---{ Eventos }-------------------------------------------------// Inutilizacao da NF	
	def inutilizarNfe(self, parent, filial, ambiente, nota_fiscal, motivo, nfe_nfce, dav, id_lancamento, tipo_pedido, serie ):

		retorno, uf, _ambiente, serie_nfe, serie_nfce, regime,cnpj = informes.dadosIdentificacao( filial, parent, modelo=nfe_nfce, gravar = True)
		if not retorno: return
		NotaFiscalParametros.contingencia_enviar = False

		erro = pasta_gravacao = ''
		dados_inutilizacao = OrderedDict([
		('tpAmb',ambiente),
		('xServ','INUTILIZAR'),
		('cUF',CODIGOS_UF[uf]),
		('ano',str( datetime.date.today().year )[2:]),
		('CNPJ',cnpj),
		('mod',str(nfe_nfce)),
		('serie',str( serie )),
		('nNFIni',str( int(nota_fiscal) )),
		('nNFFin',str( int(nota_fiscal) )),
		('xJust',informes.remover_acentos( motivo.replace('\n','|') ))
		])
		try:
			pasta_gravacao = informes.gravarRetorno( str(nfe_nfce), str( serie ), str( int(nota_fiscal) ), ambiente, filial )
			xml_retorno = msf.inutilizacao( dados_inutilizacao )

		except Exception as erro:

			if type( erro ) !=unicode:	erro = str( erro ).decode('utf-8')
			alertas.dia( parent, u"[ Enviando requisição de inutilizacao a sefaz {  filial "+ filial +" NFCe 4.0 } ]\n\n[ ERROR ]: "+ erro +"\n"+(" "*180),u"Pedido de inutilizacao a sefaz" )

		if not erro:

			modulo = 1
			rt = informes.retornosSefaz( xml_retorno, ["retInutNFe"], parent, nome_evento = 'INUTILIZACAO', modelo=None, contingencia=False )
			retorno = rt[1]+ '\n'

			if rt[4] != '102':	modulo = 3
			if rt[4] in ['102','563']:

				retorno = rt[1]+"{ Nota fiscal inutilizada usando dados da SEFAZ }\n\n" if rt[4] == '563' else rt[1]+'\n'
				if dav and dav !='MANUAL':	parent.NFEinuTiliza( rT = ( rt[5], rt[6], retorno, motivo, dav, id_lancamento, tipo_pedido, filial, xml_retorno ) )
				if dav == 'MANUAL' and NotaFiscalParametros.gravar_envio_retorno_pasta:	alertas.dia(parent,'{ Inutlizacao avulso de NFe [ XML-Salvo ] }\n\nPasta de gravcao do retorno do sefaz:\n'+NotaFiscalParametros.gravar_envio_retorno_pasta+'\n'+(' '*200),'Inutilizacao manual')

			if rt[0]:

				html = xml_retorno if '!DOCTYPE html' in xml_retorno else ''
				informes.mostrarInformacoesRetorno( parent, retorno, rt[2], modulo, str( nfe_nfce ), rt[4], xml_retorno, filial, NotaFiscalParametros.pasta_gravaca_xml_final, '', html, None, False )

#---{ Eventos }-------------------------------------------------// Cancelamento da NF
	def cancelamentoNfe(self, parent, filial='', xml='', motivo='', origem = '', retorno_html = '' ):

		retorno, uf, ambiente, serie_nfe, serie_nfce, regime,cnpj = informes.dadosIdentificacao( filial, parent, gravar = True)
		if not retorno: return
		NotaFiscalParametros.contingencia_enviar = False

		"""  Levantar informacoes do XML original  """
		lerXml = DadosCertificadoRetornos()
		docxml = minidom.parseString( xml )
					
		numero_nf = lerXml.leituraXml( docxml, 'infNFe', 'nNF' )[0][0]
		numero_serie = lerXml.leituraXml( docxml, 'infNFe', 'serie' )[0][0]
		
		csTaT = lerXml.leituraXml( docxml, 'protNFe', 'cStat' )[0][0]
		modelo = lerXml.leituraXml( docxml, 'infNFe', 'mod' )[0][0]

		chave = lerXml.leituraXml( docxml, 'protNFe', 'chNFe' )[0][0]
		protocolo = lerXml.leituraXml( docxml, 'protNFe', 'nProt' )[0][0]
		ambiente =  lerXml.leituraXml( docxml, 'protNFe', 'tpAmb' )[0][0]

		informes.gravarRetorno( str(modelo), str( numero_serie ), str( int(numero_nf) ), ambiente, filial )
		NotaFiscalParametros.ambiente = ambiente
		NotaFiscalParametros.modelo = modelo
		NotaFiscalParametros.serie = str( numero_serie ).zfill(3)
		time_zone = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '{}:{}'.format(strftime('%z')[:-2], strftime('%z')[-2:])
		informes.gravarRetorno( modelo, numero_serie, numero_nf, ambiente, filial )

		#--// Codigo do evento { Cancelamento(110111), Carta de correcao(110110) }
		__dd = {'nProt':protocolo, 'xJust':informes.remover_acentos( motivo.replace('\n','|') ), 'idLote':'1','descEvento':'Cancelamento'}
		dados_cancelamento = OrderedDict([
			('cOrgao',CODIGOS_UF[uf]),
			('tpAmb',str(ambiente)),
			('CNPJ',cnpj),
			('chNFe',str( chave )),
			('dhEvento',time_zone),
			('tpEvento','110111'),
			('nSeqEvento','1')
		])

		xml_retorno = msf.sefazEventos( dados_cancelamento, __dd )
		tipo_nf = '1' if modelo == '55' else '2'
		rt = informes.retornosSefaz( xml_retorno, ["retEnvEvento","infEvento"], parent, nome_evento = 'CANCELAMENTO', modelo=None )

		modulo = 1
		if rt[0] and rt[4] in ['135','573']:	parent.cannfe( rt[4], rt[3], rt[5], motivo, filial, xml_retorno )
		else:

			modulo = 3
			if rt[0]:	

				dados = numero_nf, numero_serie, origem, tipo_nf, rt[1]
				informes.salvarNotaFiscal( emissao = 1, gravacao = 3, dados = dados, filial = filial, chave='', par=parent)

		if rt[0]:

			html = xml_retorno if '!DOCTYPE html' in xml_retorno else ''
			informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulo, modelo, rt[4], xml_retorno, filial, NotaFiscalParametros.pasta_gravaca_xml_final, '', html, None, False )

	def downloadNfe(self, parent, filial, chave, nsu ):

		retorno, uf, ambiente, serie_nfe, serie_nfce, regime,cnpj = informes.dadosIdentificacao( filial, parent, gravar = True)
		if not retorno: return
		NotaFiscalParametros.contingencia_enviar = False

		__dd = {'ultNSU':nsu, 'consChNFe':chave}
		dados_download = OrderedDict([
			('tpAmb',ambiente),
			('cUFAutor',CODIGOS_UF[uf]),
			('CNPJ',cnpj),
			('CPF',''),
		])
		xml_retorno = msf.downloadNfeSefazDistribuicao( dados_download, __dd )
		html = xml.text if '!DOCTYPE html' in xml_retorno else ''
		if 'ReadTimeoutError' in str(xml_retorno):	alertas.dia(parent,'{ Erro na conexao com sefaz nacional }\n\n'+str(xml_retorno)+'\n'+(' '*180),'Erro de time out')
		elif 'ConnectTimeout' in str(xml_retorno):	alertas.dia(parent,'{ Erro na conexao com sefaz nacional }\n\n'+str(xml_retorno)+'\n'+(' '*180),'Erro de time out')
		else:

			rt = informes.retornosSefaz( xml_retorno.encode('utf-8'), ["retDistDFeInt",], parent, nome_evento = 'DOWNLOAD', modelo=None, contingencia=False )
			if rt[0]:
				
				if rt[4] == '653':	parent.cancelamentoNotaFiscalCompras( chave, rt[4] )
				if rt[4] == '138':	parent.relacionarNotasXML( xml_retorno )
				else:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], 3, 'nfe', rt[4], '', filial, '', '', html, None, False )

	def manifestoNfe(self, parent, filial, chave, evento ):

		retorno, uf, ambiente, serie_nfe, serie_nfce, regime,cnpj = informes.dadosIdentificacao( filial, parent, gravar = True)
		if not retorno: return
		NotaFiscalParametros.contingencia_enviar = False

		""" Código do evento  210200 – Confirmação da Operação  210210 – Ciência da Emissão 210220 – Desconhecimento da Operação 210240 – Operação não Realizada """
		""" Numero da operacao 1=Confirmação da Operação 2=Ciência da Emissão 3=Desconhecimento da Operação 4=Operação não Realizada """
		modulo = 1
		time_zone = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '{}:{}'.format(strftime('%z')[:-2], strftime('%z')[-2:])
		__dd = {'idLote':'1','descEvento':'Confirmacao da Operacao'}

		dados_manifesto = OrderedDict([
			('cOrgao',CODIGOS_UF['AN']),
			('tpAmb',str(ambiente)),
			('CNPJ',cnpj),
			('chNFe',str( chave )),
			('dhEvento',time_zone),
			('tpEvento',str( evento )) ,
			('nSeqEvento','1')
		])

		xml_retorno = msf.sefazEventos( dados_manifesto, __dd )
		rt = informes.retornosSefaz( xml_retorno.encode('utf-8'), ["retEnvEvento","infEvento"], parent, nome_evento = 'MANIFESTO', modelo=None, contingencia=False )

		if rt[4] in ['135']:	parent.gravarManifesto()
		else:
			if rt[4] in ['573']:	parent.gravarManifesto() #--// Duplicidade de evento { Nota ja manifestada apenas atualiza }
			if rt[0] and rt[4] !='135':	modulo = 3
			if rt[0]:

				html = xml_retorno if '!DOCTYPE html' in xml_retorno else ''
				informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulo, 'nfe', rt[4], '', filial, NotaFiscalParametros.pasta_gravaca_xml_final, '', html, None, False )

	def cartaCorrecao(self, parent, filial, __i ):

		retorno, uf, ambiente, serie_nfe, serie_nfce, regime,cnpj = informes.dadosIdentificacao( filial, parent, gravar = True)
		if not retorno: return
		NotaFiscalParametros.contingencia_enviar = False

		chave = __i[0] #-: Chave
		motivo = __i[1] #-: Motivo do cancelamento
		xml_anterior = __i[5] #-: XML Anterior
		sequencial_envio = str( __i[6] ) #-: Sequencial de Envio de CCe { No Maximo ate 20 correcoes }
		cliente = __i[8] #-: Cliente
	
		numero_nf = chave[25:34]
		numero_serie = chave[22:25]
		modelo = chave[20:22]
		modulo = 1

		informes.gravarRetorno( modelo, str( numero_serie ), str( int(numero_nf) ), ambiente, filial )
		NotaFiscalParametros.ambiente = ambiente
		NotaFiscalParametros.modelo = int(chave[20:22])
		NotaFiscalParametros.serie = str(numero_serie).zfill(3)
		time_zone = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '{}:{}'.format(strftime('%z')[:-2], strftime('%z')[-2:])

		#--// Codigo do evento { Cancelamento(110111), Carta de correcao(110110) }
		__dd = {'xCorrecao':informes.remover_acentos( motivo.replace('\n','|') ), 'idLote':'1','descEvento':'Carta de Correcao'}
		carta_correcao = OrderedDict([
			('cOrgao',CODIGOS_UF[uf]),
			('tpAmb',ambiente),
			('CNPJ',cnpj),
			('chNFe',str( chave )),
			('dhEvento',time_zone),
			('tpEvento','110110'),
			('nSeqEvento',sequencial_envio)
		])

		xml_retorno = msf.sefazEventos( carta_correcao, __dd )
		rt = informes.retornosSefaz( xml_retorno.encode('utf-8'), ["retEnvEvento","infEvento"], parent, nome_evento = 'CCE', modelo=None, contingencia=False )

		if rt[0] and rt[4] == '135':

			"""  Levantar informacoes do XML original  """
			lerXml = DadosCertificadoRetornos()
			docxml = minidom.parseString( xml_retorno )

			_ch = lerXml.leituraXml( docxml, 'infEvento', 'chNFe' )[0][0] #--// Chave
			_dt = lerXml.leituraXml( docxml, 'infEvento', 'dhRegEvento' )[0][0] #--// Data de recebimento

			informe = _ch, _dt, xml_retorno, rt[1], xml_anterior, motivo
			informes.salvarNotaFiscal(  emissao = 1, gravacao = 4, dados = informe, filial = filial,chave='', par=parent)

		if rt[0] and rt[4] !='135':	modulo = 3
		if rt[0]:
			
			html = xml_retorno if '!DOCTYPE html' in xml_retorno else '' 
			informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulo, modelo, rt[4], xml_retorno, filial, NotaFiscalParametros.pasta_gravaca_xml_final, '', html,None, False )

	def consultaNotaFiscal(self, parent, chave, filial, retornar=False ):

		retorno, uf, ambiente, serie_nfe, serie_nfce, regime,cnpj = informes.dadosIdentificacao( filial, parent, gravar = True)
		if not retorno: return
		NotaFiscalParametros.contingencia_enviar = False
	
		numero_nf = chave[25:34]
		numero_serie = chave[22:25]
		modelo = chave[20:22]
		modulo = 1

		informes.gravarRetorno( modelo, str( numero_serie ), str( int(numero_nf) ), ambiente, filial )
		NotaFiscalParametros.ambiente = ambiente
		NotaFiscalParametros.modelo = chave[20:22]
		NotaFiscalParametros.serie = str(numero_serie).zfill(3)

		consulta_chave =  OrderedDict([
			('tpAmb',ambiente),
			('xServ','CONSULTAR'),
			('chNFe',chave)
		])
		
		xml_retorno = msf.consultarNotaFiscalChave( consulta_chave )
		rt = informes.retornosSefaz( xml_retorno, ["nfeResultMsg","infProt"], parent, nome_evento = 'CONSULTAR_NF', modelo=None, contingencia=False )

		if rt[0]:

		    if retornar:	return xml_retorno
		    else:
			if rt[4] !='100':	modulo = 3
			html = xml_retorno if '!DOCTYPE html' in xml_retorno else ''
			informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulo, modelo, rt[4], xml_retorno, filial, NotaFiscalParametros.pasta_gravaca_xml_final, '', html,None, False )


#----------------------------// Emissao de NFe 4.00 Atraves da nossa solucao //---------------------#
# Inicio em 07-07-2018                                                                              #
# Jose de almeida lobinho                                                                           #
#---------------------------------------------------------------------------------------------------#
class Nfs400:

	emitir_nfce = ''
	epson_nfce = ''
	def emissao( self, parent='', filial='', modelo='55', informe_dav={}, dados={}, it=None):
	
	    self.p = parent
	    emissao_contingencia_offline = False
	    self.informacoes_impressao_termica = self.p.informacoes_impressao_termica
#-----[ IDENTIFICACAO DA NOTA FISCAL ]
	    """  IDENTIFICACAO DA NOTA FISCAL  """
	    """  emissao tip_nota { 1-Nota fiscal de vendas, 2-Nota fiscal de devolucao de vendas, 3-Nota fiscal de devolucao de compras RMA }  """
	    """  lancamento tipo_emissao {1-emissa, 2-para inutilizar, 3-cancelamento 4-inutilizada, 5-denagada  """
	    """  origem {1-vendas, 2-compras } """

	    retorno, uf, ambiente, serie_nfe, serie_nfce, regime, cnpj = informes.dadosIdentificacao( filial, parent, modelo=modelo, gravar = True)
	    if not retorno: return
	    NotaFiscalParametros.contingencia_enviar = False

	    gravar_xml_recuperacao=False
	    serie = serie_nfe if modelo == '55' else serie_nfce
	    nota_referenciada = dados['refNFe']

	    """  Permitir o envio de uma contigencia q esteja com problemas de calculo ou de de shemas mantendo o mesmo numero de nota e serie  """
	    if self.p.contingencia_serie and self.p.contingencia_status and self.p.contingencia_numeronf and self.p.contingencia_status in ['806','225']:
		serie = self.p.contingencia_serie
		nota_referenciada= ''

	    retorno, numero_nota = numeros.VerificaNFE( self.p.numero_dav, Tnf = int( informe_dav['tipo_nota'] ), Filial = filial ) #-// Numero de NF gerado ou utilizando um numero ja gerado

	    """ No caso da contingencia e necessario sempre criar um nota para evitar q o XML em contingencia esteja em duplicidade """
	    if not retorno or informe_dav['tpEmis']=='9':
		
		sequencial_nf = "5" #--// NFe
		if modelo == "65":	sequencial_nf = "15" #--// NFCe
		
		#numero_nota = numeros.numero("15" if modelo == '65' else "5","Numero da NFe",self.p, filial ) #-// Gerando um novo numero
		numero_nota = numeros.numero(sequencial_nf, "Numero da NFe", self.p, filial ) #-// Gerando um novo numero
		gravar_xml_recuperacao=True
		
	    if not numero_nota:
					
		alertas.dia(self.p,u"Numero de NFe não foi gerado, Tente novamente!!\n"+(" "*110),u"Emissão de NFes")
		return

	    """ Finalidade da emissão da NF-e: 1 - NFe normal 2 - NFe complementar 3 - NFe de ajuste 4 - Devolução/Retorno """
	    self.nota_fiscal_complementar=True if dados['finNFe']=='2' else False

	    if numero_nota:
	    
		modelo_nota = '1' if modelo == '55' else '2'
		
		if self.nota_fiscal_complementar:	informe_dav['tipo_nota']='4'
		gravar_gerenciador=str(numero_nota),informe_dav['numero_dav'],'',modelo_nota,'2',informe_dav['origem'],ambiente,filial,serie,informe_dav['valor_nota'],informe_dav['cliente']
		
		informes.salvarNotaFiscal( emissao = int(informe_dav['tipo_nota']), gravacao = 1, dados = gravar_gerenciador, filial = filial,chave='', par=parent)
		
		if gravar_xml_recuperacao:	gravacao_recupercao=int(informe_dav['tipo_nota']), 6, gravar_gerenciador, filial, self
		else:	 gravacao_recupercao=None
		
		"""  Composicao do numero da chave  """
		numero_nota_fiscal  = str( numero_nota )
		numero_nota_fiscalf = str( numero_nota_fiscal ).zfill(9)
		numero_compoe_chave = str( self.numeroCompoeChave( numero_nota_fiscal ) ).zfill(8) 
		ano_mes_compoe_nota = str( datetime.datetime.now().strftime("%y%m") )
		documento_emissor   = str( login.filialLT[ filial ][9] ).zfill(14)
		modelo_nota_fiscal  = str( modelo )
		numero_serie_nota   = str( serie ).zfill(3)
		forma_emissao_nota  = informe_dav['tpEmis']
		codigo_municipio_ocorrencia = str( CODIGOS_UF[uf] )
		chave = codigo_municipio_ocorrencia+ano_mes_compoe_nota+documento_emissor+modelo_nota_fiscal+numero_serie_nota+numero_nota_fiscalf+forma_emissao_nota+numero_compoe_chave
		chave_digito = self.nfeCalculaDigito( chave )
		chave_numero = chave + chave_digito
		chave_id = 'NFe'+chave_numero

		"""  Alguns servidore nao estavam sincronizando """
		if len(login.filialLT[filial][30].split(';')) >=14 and login.filialLT[filial][30].split(';')[13]:
			data_emissao = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '-' +login.filialLT[filial][30].split(';')[13]
		else:	data_emissao = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '{}:{}'.format(strftime('%z')[:-2], strftime('%z')[-2:])

		""" Contingencia na NFCe """
		contingencia_dhcont =""
		contingencia_xjust = ""
		if informe_dav['tpEmis'] == '9' and modelo == '65':

		    contingencia_dhcont = data_emissao
		    contingencia_xjust  = "Falha de conexao com a outra ponta"
		    NotaFiscalParametros.emissao_contingencia = True

		nota_fiscal = nfe400.informacaoNfe( versao='4.00', id_nfe=chave_id )
		ide = OrderedDict([
		("cUF",CODIGOS_UF[uf]), #--// Código da UF do emitente do Documento Fiscal. Utilizar a Tabela do IBGE.
		("cNF",numero_compoe_chave), #--// Código numérico que compõe a Chave de Acesso. Número aleatório gerado pelo emitente para cada NF-e. [0-9]{8}
		("natOp",dados['natOp']), #--// Descrição da Natureza da Operação { 60 }
		("mod",str( modelo )), #--// Código do modelo do Documento Fiscal. 55 = NF-e; 65 = NFC-e.
		("serie",serie), #--// Série do Documento Fiscal série normal 0-889 Avulsa Fisco 890-899 SCAN 900-999
		("nNF",str(int(numero_nota_fiscal))), #--// Número do Documento Fiscal
		("dhEmi",data_emissao), #--// Data e Hora de emissão do Documento Fiscal (AAAA-MM-DDThh:mm:ssTZD) ex.: 2012-09-01T13:00:00-03:00
		("dhSaiEnt",'' if modelo=='65' else dados['dhSaiEnt']), #--// Data e Hora da saída ou de entrada da mercadoria / produto (AAAA-MM-DDTHH:mm:ssTZD)
		("tpNF",dados['tpNF']), #--// Tipo do Documento Fiscal (0 - entrada; 1 - saída)
		("idDest",dados['idDest']), #--// Identificador de Local de destino da operação (1-Interna;2-Interestadual;3-Exterior)
		("cMunFG",login.filialLT[filial][13]), #--// Código do Município de Ocorrência do Fato Gerador (utilizar a tabela do IBGE)
		("tpImp",informe_dav['tipo_impressao']), #--// Formato de impressão do DANFE (0-sem DANFE;1-DANFe Retrato; 2-DANFe Paisagem;3-DANFe Simplificado; 4-DANFe NFC-e;5-DANFe NFC-e em mensagem eletrônica)
		("tpEmis",informe_dav['tpEmis']), #--// Forma de emissão da NF-e 1 - Normal; 2 - Contingência FS 3 - Contingência SCAN 4 - Contingência DPEC 5 - Contingência FSDA 6 - Contingência SVC - AN 7 - Contingência SVC - RS 9 - Contingência off-line NFC-e
		("cDV",chave_digito), #--// Digito Verificador da Chave de Acesso da NF-e [0-9]{1}
		("tpAmb",ambiente), #--// Identificação do Ambiente: 1 - Produção 2 - Homologação
		("finNFe",dados['finNFe']), #--// Finalidade da emissão da NF-e: 1 - NFe normal 2 - NFe complementar 3 - NFe de ajuste 4 - Devolução/Retorno
		("indFinal",dados['indFinal']), #--// Indica operação com consumidor final (0-Não;1-Consumidor Final)
		("indPres",dados['indPres']), #--// Indicador de presença do comprador no estabelecimento comercial no momento da oepração (0-Não se aplica (ex.: Nota Fiscal complementar ou de ajuste;1-Operação presencial;2-Não presencial, internet;3-Não presencial, teleatendimento;4-NFC-e entrega em domicílio;5-Operação presencial, fora do estabelecimento;9-Não presencial, outros)
		("procEmi",'0'), #--// Processo de emissão utilizado com a seguinte codificação: 0 - emissão de NF-e com aplicativo do contribuinte; 1 - emissão de NF-e avulsa pelo Fisco; 2 - emissão de NF-e avulsa, pelo contribuinte com seu certificado digital, através do site do Fisco; 3- emissão de NF-e pelo contribuinte com aplicativo fornecido pelo Fisco.
		("verProc",'NFe_DIRETO'), #--// versão do aplicativo utilizado no processo de emissão { 20 }
		("dhCont",contingencia_dhcont), #--// Informar a data e hora de entrada em contingência contingência no formato (AAAA-MM-DDThh:mm:ssTZD) ex.: 2012-09-01T13:00:00-03:00.
		("xJust",contingencia_xjust), #--// Informar a Justificativa da entrada
		("refNFe",nota_referenciada) #--// Chave de acesso das NF-e referenciadas. Chave de acesso compostas por Código da UF (tabela do IBGE) + AAMM da emissão + CNPJ do Emitente + modelo, série e número da NF-e Referenciada + Código Numérico + DV. 
		])
		nota_fiscal.append( nfe400.identificacaoNFe(ide) )

#-----[ IDENTIFICACAO DO EMITENTE ]
		""" Identificacao do emitente """
		telefone = login.filialLT[ filial ][10].split('|')[0].replace(' ','').replace('-','').replace('(','').replace(')','').replace('.','').decode('UTF-8')
		crt = login.filialLT[ filial ][30].split(";")[11]
		if informe_dav['tipo_nota'] == '3' and self.p.crTFornecedor.GetValue() and self.p.crTFornecedor.GetValue().split('-')[0] !="RMA":	crt = str( self.p.crTFornecedor.GetValue().split("-")[0] ) #-: RMA-Regime do Fornecedor

		df=login.filialLT[filial]

		emi_dados = OrderedDict([
		("CNPJ",df[9].strip()),
		("CPF",""),
		("xNome",df[1].strip().decode('UTF-8')),
		("xFant",df[14].strip().decode('UTF-8'))
		])

		emi_endereco = OrderedDict([
		("xLgr",df[2].strip().decode('UTF-8')),
		("nro",df[7].strip().decode('UTF-8')),
		("xCpl",df[8].strip().decode('UTF-8')),
		("xBairro",df[3].strip().decode('UTF-8')),
		("cMun",df[13].strip().decode('UTF-8')),
		("xMun",df[4].strip().decode('UTF-8')),
		("UF",df[6].strip().decode('UTF-8')),
		("CEP",df[5].strip().decode('UTF-8')),
		("cPais",CODIGO_PAIS['BR']),
		("xPais","BRASIL"),
		("fone",telefone)
		])

		emi_documentos = OrderedDict([
		("IE",df[11].strip()),
		("IEST",""), #--// Inscricao Estadual do Substituto Tributário
		("CRT",crt) #--// Código de Regime Tributário. Este campo será obrigatoriamente preenchido com: 1 – Simples Nacional; 2 – Simples Nacional – excesso de sublimite de receita bruta; 3 – Regime Normal.
		])
		nota_fiscal.append( nfe400.emitente( dados = emi_dados, endereco = emi_endereco, documentos = emi_documentos ) )

#-----[ IDENTIFICACAO DO DESTINATARIO ]
		"""  Identificacao do destinatario  """
		en, ee, dc = self.enderecos( modelo=modelo, dav_tipo = informe_dav['tipo_nota'])
		nome_cliente = 'NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL' if ambiente == '2' else dc[0] if dc else ''

		if modelo == '65' and not dc and informe_dav['cliente'][3] and informe_dav['cliente'][1]:

    		#--//Indentificacao do consumidor com nome,cpf [ Nome, fantasia, cpf,cnpj,'','','','9-Consumidor final' ]
		    dc = informe_dav['cliente'][3], informe_dav['cliente'][2], informe_dav['cliente'][1],'','','','9'
		    if ambiente == '1':	nome_cliente = dc[0]

		des_dados = des_endereco = des_documentos = []
		if modelo=='65' and dc and not dc[2] and self.p.impressao_consumidor.GetValue():	dc=None
		if dc and dc[0]:
			
		    cpf = dc[2] if len( dc[2] ) == 11 else ''
		    cnpj = dc[2] if len( dc[2] ) == 14 else ''
		    des_dados = OrderedDict([
		    ("CPF",cpf),
		    ("CNPJ",cnpj),
		    ("idEstrangeiro",""),
		    ("xNome",nome_cliente)
		    ])

		    if self.p.forcar_endereco_nfce:	passar_endereco=True
		    else:
			passar_endereco = True if en and en[0] and en[1] and en[3] and en[4] and en[5] and en[6] and en[7] else False
			
		    if passar_endereco:
			des_endereco = OrderedDict([
			("xLgr",en[0]),
			("nro",en[1]),
			("xCpl",en[2]),
			("xBairro",en[3]),
			("cMun",en[5]),
			("xMun",en[4]),
			("UF",en[6]),
			("CEP",en[7]),
			("cPais",CODIGO_PAIS['BR']),
			("xPais","BRASIL"),
			("fone",dc[4])
			])

		    des_documentos = OrderedDict([
		    ("indIEDest",dc[6]), #--// Indicador da IE do destinatário: 1 – Contribuinte ICMSpagamento à vista; 2 – Contribuinte isento de inscrição; 9 – Não Contribuinte
		    ("IE",dc[3] if modelo == '55' else ''), #--// Inscrição Estadual (obrigatório nas operações com contribuintes do ICMS)
		    ("ISUF",""), #--// Inscrição na SUFRAMA (Obrigatório nas operações com as áreas com benefícios de incentivos fiscais sob controle da SUFRAMA) PL_005d - 11/08/09 - alterado para aceitar 8 ou 9 dígitos1
		    ("email",dc[5])
		    ])
		    nota_fiscal.append( nfe400.destinatario( dados = des_dados, endereco = des_endereco, documentos = des_documentos ) )

#-----[ LOCAL DE ENTEREGA ]
		"""  Local de entrega """
		if len(ee) !=0 and ee[0]:

		    local_entrega = OrderedDict([
		    ("CNPJ",cnpj),
		    ("CPF",cpf),
		    ("xLgr",ee[0]),
		    ("nro",ee[1]),
		    ("xCpl",ee[2]),
		    ("xBairro",ee[3]),
		    ("cMun",ee[5]),
		    ("xMun",ee[4]),
		    ("UF",ee[6])
		    ])
		    nota_fiscal.append( nfe400.localEntrega( local_entrega ) )

#-----[ Autorizacao para downloando { CNPJ do contador } ]
		doc_download = login.filialLT[filial][38].strip() if login.filialLT[filial][38] else ""
		if doc_download and doc_download.isdigit() and len(doc_download) in [11,14]:
		    autoriza_download = OrderedDict([
			("CNPJ",doc_download if len(doc_download)==14 else ""),
			("CPF",doc_download if len(doc_download)==11 else ""),
			])
		    nota_fiscal.append( nfe400.autorizaDownload( autoriza_download ) )

#-----[ GRUPOS DE PRODUTOS ]
		numero_registros = self.p.editdanfe.GetItemCount()
		valor_total_ibpt = Decimal()

		for i in range( numero_registros ):

		    pd = self.retornaProduto( modelo_nf = modelo, dav_tipo = informe_dav['tipo_nota'], indice = i )
		    xped = self.p.editdanfe.GetItem(i,76).GetText().strip() if self.p.editdanfe.GetItem(i,76).GetText().strip() else self.p.editdanfe.GetItem(i,76).GetText().strip()
		    
		    produto = 'NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL' if ambiente == '2' and i == 0 else pd['xProd']
		    if self.nota_fiscal_complementar:
			pd['qCom']='0'
			pd['vUnCom']='0.00'
			pd['vProd']='0.00'
			pd['qTrib']='0'
			pd['vUnTrib']='0.00'
			pd['vFrete']=''
			pd['vDesc']=''

		    produto = OrderedDict([
		    ("cProd",pd['cProd']),
		    ("cEAN",pd['cEAN']),
		    ("xProd",produto),
		    ("NCM",pd['NCM']),
		    ("CEST",pd['CEST']), #// o especificador da Substuicao Tributaria - CEST, que identifica a mercadoria sujeita aos regimes de substituicao tributária e de antecipação do recolhimento do imposto
		    ("indEscala",pd['indEscala']),
		    ("CNPJFab",pd['CNPJFab']), #// CNPJ do Fabricante da Mercadoria, obrigatório para produto em escala NÃO relevante.
		    ("cBenef",pd['cBenef']), #// Codigo de beneficio fiscal
		    ("EXTIPI",pd['EXTIPI']), #// Código EX TIPI (3 posições)
		    ("CFOP",pd['CFOP']),
		    ("uCom",pd['uCom']),
		    ("qCom",pd['qCom']),
		    ("vUnCom",pd['vUnCom']),
		    ("vProd",pd['vProd']),
		    ("cEANTrib",pd['cEANTrib']),
		    ("uTrib",pd['uTrib']),
		    ("qTrib",pd['qTrib']),
		    ("vUnTrib",pd['vUnTrib']),
		    ("vFrete",pd['vFrete']),
		    ("vSeg",pd['vSeg']),
		    ("vDesc",pd['vDesc']),
		    ("vOutro",pd['vOutro']),
		    ("indTot",pd['indTot']), #// Este campo deverá ser preenchido com: 0 – o valor do item (vProd) não compõe o valor total da NF-e (vProd) 1 – o valor do item (vProd) compõe o valor total da NF-e (vProd)
		    ("xPed",xped), #+'-'+pd['idProdVenda']),
		    ("nItemPed",str( ( i + 1) ))
		    ])
		    
		    """ Adiciona produtos { Instancia } """
		    prdo = nfe400.itens( produtos = produto, numero_item = str( ( i + 1) ) )

		    """ GRUPOS DE PRODUTOS { TRIBUTOS } """
		    icms_diferentes=['1000']
		    icms_diferentes_outros=['0570','0270','0100','0200','0510','0120','0110','0190','0160']
		    icms_cst=self.p.editdanfe.GetItem(i,33).GetText().strip()
		    
		    cst_icms='00' if int(self.p.editdanfe.GetItem(i,33).GetText().strip())==0 or self.p.editdanfe.GetItem(i,33).GetText().strip() in icms_diferentes else str( int( self.p.editdanfe.GetItem(i,33).GetText().strip() ) )
		    cst_orig=self.p.editdanfe.GetItem(i,33).GetText().strip()[:1]

		    """ RMA com CST 70 e origem 5, origem 2 """
		    if crt=='3' and icms_cst in icms_diferentes_outros:

			cst_icms, cst_orig=str(int(icms_cst))[1:], str(int(icms_cst))[:1]
		    
		    valor_produto_ibpt = self.valorAproximadoTributos( produto_geral = 2, ibpt_produto = str( self.p.editdanfe.GetItem( i, 43 ).GetText().strip() ), modelo=modelo )
		    valor_total_ibpt += Decimal( valor_produto_ibpt ) if valor_produto_ibpt else 0
		    tags_imposto,tags_pis, tags_cofins, tags_imp_dev, tags_imp_difal, tags_ipi = self.calculoTributosProduto(dav_tipo=informe_dav['tipo_nota'], indice=i, icms=cst_icms)

		    """ DIFAL """
		    __difal = True if informe_dav['tipo_nota']!='3' and modelo=='55' and dados['indFinal']=='1' and dados['idDest']=='2' and Decimal(self.p.cTDavs[0][110].split(";")[2]) and Decimal(tags_imp_difal['vBCUFDest']) else  False
		    
		    if self.p.forcar_difal.GetValue() and Decimal(tags_imp_difal['vBCUFDest']):	__difal=True #--// Forcar DIFAL para pessoa juridica sem inscricao estadual
		    difal = tags_imp_difal if __difal else None

		    """ Adiciona o imposto em produto { tags_imposto,tags_pis, tags_cofins, tags_imp_dev RETORNO EM DICIONARIO P/MONTAGEM NA LIB } """
		    prdo.append(nfe400imposto.impostosNfe400(icms=cst_icms,origem=cst_orig,tags=tags_imposto,vTotTrib=valor_produto_ibpt,pis=tags_pis,cofins=tags_cofins,difal=difal,ipi=tags_ipi,modelo=modelo))

		    """ Devolucao de imposto { IPI em produtos } """
		    if tags_imp_dev['pDevol'] and Decimal(tags_imp_dev['pDevol']):	prdo.append(nfe400imposto.devolucaoImposto(tags=tags_imp_dev))

    		    """ Informacoes adicionais do produto { Medidas [Monfardini 23-2019] } """
		    medidas_cliente=self.p.editdanfe.GetItem(i,10).GetText().strip() if self.p.editdanfe.GetItem(i,10).GetText().strip() else ''

		    #--// Informacoes adicionais no cadastro do produto { dados adicinais referente ao CST etc... }
		    if self.p.editdanfe.GetItem(i,75).GetText().strip():
			if medidas_cliente:	medidas_cliente += '\n\n'+self.p.editdanfe.GetItem(i,75).GetText().strip()
			else:	medidas_cliente = self.p.editdanfe.GetItem(i,75).GetText().strip()

		    #--// Informacoes adicionais no cadastro do produto { Numero de SERIE }
		    if self.p.editdanfe.GetItem(i,68).GetText().strip():
			if medidas_cliente:	medidas_cliente += '\n\n'+self.p.editdanfe.GetItem(i,68).GetText().strip()
			else:	medidas_cliente = self.p.editdanfe.GetItem(i,68).GetText().strip()
			
		    if medidas_cliente:	prdo=nfe400imposto.infadProdutos(raiz=prdo,tags=medidas_cliente)

		    nota_fiscal.append( prdo ) #--// Adiciona no SHEMA infNfe

#-----[ TOTALIZACAO DOS TRIBUTOS ]
		impostos, transportadora, veiculos, reboques, volumes=self.totalizarTributos(dav_tipo=informe_dav['tipo_nota'],valor_ibpt=str(valor_total_ibpt),crt=crt,difal=__difal,modelo=modelo)
		nota_fiscal.append(nfe400imposto.totalizacaoNotaFiscal(tags=impostos))

#-----[ PAGAMENTOD/FATURA/DUPLICATAS ]
		nota_fiscal.append( nfe400.modalidadeFrete(tags=informe_dav['modFrete'], transporte=transportadora, veiculo=veiculos,reboque=reboques,volume=volumes) )

		""" [ Detalhar pagamentos, dicionario {'02':('2.5','2','0')},{'tPag':('vPag','tpIntegra','indPag')} ] """
		lista_pagamentos, relacao_duplicatas, valor_fatura = self.retornarPagamentos(informe_dav['pag'],informe_dav['tipo_nota'],informe_dav['numero_dav'],filial, modelo)

		""" [ Cobranca: relacao_duplicatas Dicionario {1:('18/09/2018','841.90')}, {int(numeroParcela):('Vencimento','Valor')} ] """
		if relacao_duplicatas:	nota_fiscal.append( nfe400.cobrancaPagamentos(tags=valor_fatura,duplicatas=relacao_duplicatas) )

		""" [ Detalhar pagamentos, dicionario {'02':('2.5','2','0')},{'tPag':('vPag','tpIntegra','indPag')} ] """
		""" Emissao de orcamentos consolidando varios davs """
		if self.p.consolidado=='T':
		    
		    valor_nota_fiscal=str(self.p.cTDavs[0][37])
		    lista_pagamentos = {'01':(valor_nota_fiscal,'','0')}
		nota_fiscal.append( nfe400.detalharPagamentos(tags=lista_pagamentos) )

#-----[ INFORMACOES ADICIONAIS  ]
		informacoes_adicionais = OrderedDict([
		('infAdFisco',''),
		('infCpl',self.dadosAdicionais(self.p, filial, informe_dav['tipo_nota'])) #-----[ Informacoes adicionais
		])

		#if modelo == '55':	nota_fiscal.append( nfe400.informacoesAdicionais( tags = informacoes_adicionais ) )
		nota_fiscal.append( nfe400.informacoesAdicionais( tags = informacoes_adicionais ) ) #// Jpf 5/05/2020
	
#-----[ Responsavel tecnico ]
		responsavel_tecnico=OrderedDict([
		("CNPJ","10782612000137"),
		("xContato","Jose de Almeida Lobinho"),
		("email","joselobinho@gmail.com"),
		("fone","21998675961"),
		("idCSRT",""),
		("hashCSRT","")
		])
		nota_fiscal.append( nfe400.responsavelTecnico( tags = responsavel_tecnico ) )

#-----[ PEDIDO DE AUTORIZACAO AO SEFAZ ]
		NotaFiscalParametros.gravar_original=gravar_xml_recuperacao #--// Grava o xml original na primeira emissao da nota [ Serve para recuperacao 204,359 ]
		informes.gravarRetorno( modelo, serie, numero_nota, ambiente, filial) #--// Pasta para gravar os xmls de envio e retorno
		
		"""  Gravacao a pasta de gravacao do XML para recuperacao  """
		if gravar_xml_recuperacao:	informes.salvarNotaFiscal( emissao = int(informe_dav['tipo_nota']), gravacao = 5, dados = gravar_gerenciador, filial = filial, chave=chave_numero, par=parent)

		""" Indicador de processamento síncrono. 0=NÃO; 1=SIM=Síncrono """
		sincassin = '0' if df[6].strip().upper() in ['BA'] else '1'
		
		xml_autorizado, status = msf.autorizacaoSefaz( tags={'idLote':'1','indSinc':sincassin}, xml=nota_fiscal, chave=chave_id, modelo=modelo, recuperar=gravacao_recupercao)
		NotaFiscalParametros.gravar_original=False

		""" Emissao em contingencia """
		if informe_dav['tpEmis'] == '9':	rt = informes.retornosSefaz( xml_autorizado, ["infNFe","ide"], parent, nome_evento = 'EMISSAO', modelo=None, contingencia=True )
		else:	rt = informes.retornosSefaz( xml_autorizado, ["protNFe","retEnviNFe"], parent, nome_evento = 'EMISSAO', modelo=None, contingencia=False )
		
		html = ''
		modulos_nfe = 3
		impressao_termica = None
		""" NOTA FISCAL DENEGADA
		Erro 205 - Nota ja denegaga na base de dados da sefaz
		Erro 301 – Uso Denegado: IE do emitente em situação irregular perante o Fisco;
		Erro 302 – Uso Denegado: IE do destinatário em situação irregular perante o Fisco;
		Erro 303 – Uso Denegado: Destinatário não habilitado a operar na UF.		
		"""
		lerXml=DadosCertificadoRetornos()
		if NotaFiscalParametros.retorno_validacao_xsd:	pass
		elif informe_dav['tpEmis'] == '9':

		    docxml=minidom.parseString( xml_autorizado )
		    chave = lerXml.leituraXml(docxml, 'infNFe', 'Id')[1].split('NFe')[1]
		    datar = lerXml.leituraXml(docxml, 'ide', 'dhEmi')[0][0]
		    nota  = lerXml.leituraXml(docxml, 'ide', 'nNF')[0][0]
		    __sr  = lerXml.leituraXml(docxml, 'ide', 'serie')[0][0]
		    proto = ''
		    dav = informe_dav['numero_dav']
		    dados = filial, str(chave), str(datar), str(nota), proto, dav, str(__sr)
		    __r, _i = informes.gravarContingencia(dados, xml_autorizado)

		    if not __r:	alertas.dia(self.p,'Erro na gravacao do xml\n\n'+str(_i)+'\n'+(' '*180),'Erro na gravacao do xml')
		    elif __r and self.p.origem_emissao == '160':

			self.p.fecharNfe310( "160", nota, filial )
			emissao_contingencia_offline = True

			#--// Impressao automatica da NFCe
			impressao_termica = it,  self.informacoes_impressao_termica, chave if modelo == '65' else None
			if modelo == '65' and it and  self.informacoes_impressao_termica['auto'] and self.informacoes_impressao_termica['printer'][8]:
			    
			    iit = self.informacoes_impressao_termica
			    xml = it.printar(parent=self.p, dav=iit['dav'], chave=chave, filial=filial)
			    
			    if xml and iit['printer']:
				""" Impressora Epson TMT20 """
				if nF.listaprn(1)[3][self.p.impressoras_nfce.GetValue().split('-')[0]][7].split('-')[0] == "10":
				    Nfs400.epson_nfce.nfce( parent, filial=filial, printar=iit['printer'][0], xml=xml, inform = iit,emissao=702, numero_dav=iit['dav'], segunda=False, autorizador='' )
				else:
				    Nfs400.emitir_nfce.nfce( parent, filial=filial, printar=iit['printer'][0], xml=xml, inform = iit,emissao=702, numero_dav=iit['dav'], segunda=False, autorizador='' )

		else:
		    if status in ['204','539']: #--//[ Recuperacao automatica do XML via status do Chave-XML {Duplicidade de NF-e} ]

			chave_sefaz=rt[3]
			status_sefaz=status

			"""  Recupera a chave do retorno p/rejeicao 539, Duplicidade de NF-e, com diferenca na Chave de Acesso """
			if status in ['539']: #--// Duplicidade de NF-e, com diferenca na Chave de Acesso
			    docxml_status=minidom.parseString( xml_autorizado )
			    nmotivo,s2=lerXml.leituraXml( docxml_status, 'infProt', 'xMotivo' )
			    if 'chNFe:' in str( nmotivo ):	chave_sefaz=str( nmotivo ).split('chNFe:')[1][:44]
			    
			xml_original=self.retornaCopiaOriginalXml(filial,chave_sefaz)
			    
			if not xml_original:	alertas.dia(parent,u"{ Recuperação de XML, XML nao localizado na base [SEFAZ RETORNO "+status+"] }\nInforme ao suporte para recuperacao manual do XML...\n"+(" "*200),u"Recuperação de XML, 24, 359")
			elif not len(chave_sefaz)==44:	alertas.dia(parent,u"{ Recuperação de XML,  tamanho de chave diferente de 44 [SEFAZ RETORNO "+status+"] }\nInforme ao suporte para recuperacao manual do XML...\n"+(" "*200),u"Recuperação de XML, 24, 359")
			elif xml_original and len(chave_sefaz)==44:

			    _mensagem = mens.showmsg(u"STATUS: "+status+u'\nTentando a recuperação do XML\n'+chave_sefaz+u'\n\nAguarde',)

			    recuperacao=Eventos()
			    xml_consulta=recuperacao.consultaNotaFiscal( parent, chave_sefaz, filial, retornar=True )
			    docxml_status=minidom.parseString( xml_consulta )
			    status1=lerXml.leituraXml( docxml_status, 'infProt', 'cStat' )
			    status2=lerXml.leituraXml( docxml_status, 'retConsSitNFe', 'cStat' )
			    status3=lerXml.leituraXml( docxml_status, 'retConsSitNFe', 'xMotivo' )
				
			    if status1[0]:	status_sefaz=status1[0][0]
			    if status2[0]:	status_sefaz=status2[0][0]
			    if status3[0]:	status3=status3[0][0]
			    del _mensagem
	    
			    if status2[0] and status_sefaz!='100':	alertas.dia(parent,u"{ Recuperação de XML }\n\nMotivo: "+status+'-'+status3+'\n'+(" "*200),u"Recuperação de XML, 24, 539")
			    if status_sefaz=='100':
				    
				confima = wx.MessageDialog(self.p,u"{ Recuperação de XML  [ SEFAZ-RETORNO "+status+"-Duplicidade de NF-e] }\n\nNumero da chave: "+chave_sefaz+"\n\nConfirme p/recuperar o xml da chave acima...\n"+(" "*200),"Recuperação de XML",wx.YES_NO|wx.NO_DEFAULT)
				if confima.ShowModal() ==  wx.ID_YES:

				    xml_autorizado,dados=numeros.recuperarXmlManual(xml_original, xml_consulta, montar_danfe, False)
				    rt = informes.retornosSefaz( xml_autorizado, ["protNFe","retEnviNFe"], parent, nome_evento = 'EMISSAO', modelo=None, contingencia=False )
					
				    arquivo=NotaFiscalParametros.gravar_envio_retorno_pasta+'/NFe'+chave_sefaz+'.xml'
				    NotaFiscalParametros.relacao_xmls_utilizados.append(arquivo)

				    status='100'
				    if not os.path.exists(arquivo):

					__arquivo = open(arquivo, "w" )
					__arquivo.write( str( xml_autorizado ) )
					__arquivo.close()
		    
		    if status in ['100','301','302','303','205']: 
						
			docxml=minidom.parseString( xml_autorizado.encode('UTF-8') )
			
			if status in ['205']: #--// [ Denegada quando foi reenviado ]

			    csTaT=lerXml.leituraXml( docxml, 'retEnviNFe', 'cStat' )[0][0]
			    nchave=lerXml.leituraXml( docxml, 'retEnviNFe', 'chNFe' )[0][0]
			    data_recebimento=lerXml.leituraXml( docxml, 'retEnviNFe', 'dhRecbto' )[0][0]
			    numero_nf=nchave[25:34]
			    numero_serie=nchave[22:25]
			    protocolo=''

			elif status in ['301','302','303']: #--// [ Denegado no primeiro envio ]

			    csTaT = lerXml.leituraXml( docxml, 'protNFe', 'cStat' )[0][0]
			    nchave = lerXml.leituraXml( docxml, 'protNFe', 'chNFe' )[0][0]
			    protocolo = lerXml.leituraXml( docxml, 'protNFe', 'nProt' )[0][0]
			    data_recebimento = lerXml.leituraXml( docxml, 'protNFe', 'dhRecbto' )[0][0]
			    numero_nf=nchave[25:34]
			    numero_serie=nchave[22:25]

			else:			
			    numero_nf = lerXml.leituraXml( docxml, 'infNFe', 'nNF' )[0][0]
			    numero_serie = lerXml.leituraXml( docxml, 'infNFe', 'serie' )[0][0]
			    csTaT = lerXml.leituraXml( docxml, 'protNFe', 'cStat' )[0][0]
			    nchave = lerXml.leituraXml( docxml, 'protNFe', 'chNFe' )[0][0]
			    protocolo = lerXml.leituraXml( docxml, 'protNFe', 'nProt' )[0][0]
			    data_recebimento = lerXml.leituraXml( docxml, 'protNFe', 'dhRecbto' )[0][0]
				
			modelo_nota = '1' if modelo == '55' else '2' #--// 1-NFe, 2-NFCe
			emissao_nota = '1' #--// 1 - Emissao, 2 - ParaInutilizar, 3 - Cancelamento, 4 - Inutilizadas, 5 - Denegada
			if status in ['301','302','303','205']:	emissao_nota = '5'

			"""  Atualizar dados nas tabelas cdavs, ocorrencia, receber, nfes, sefazxml  """
			gravar_gerenciador=informe_dav['numero_dav'],protocolo,data_recebimento,nchave,numero_nf,modelo_nota,informe_dav['origem'],csTaT,emissao_nota,NotaFiscalParametros.pasta_gravaca_xml_final,xml_autorizado,rt[1],numero_serie
			informes.salvarNotaFiscal(emissao=int(informe_dav['tipo_nota']),gravacao=2,dados=gravar_gerenciador,filial=filial, chave='', par=parent)

			"""  Emissao da nfe com recebimento no caixa """
			if self.p.origem_emissao == '160' and status=='100':	self.p.fecharNfe310( "160", numero_nf, filial )

			#--// Impressao automatica da NFCe
			impressao_termica = it,  self.informacoes_impressao_termica, nchave if modelo == '65' else None
			if modelo == '65' and it and  self.informacoes_impressao_termica['auto'] and self.informacoes_impressao_termica['printer'] and self.informacoes_impressao_termica['printer'][8]:

			    iit = self.informacoes_impressao_termica
			    xml = it.printar(parent=self.p, dav=iit['dav'], chave=nchave, filial=filial)

			    if xml and iit['printer']:	
				""" Impressora Epson TMT20 """
				if nF.listaprn(1)[3][self.p.impressoras_nfce.GetValue().split('-')[0]][7].split('-')[0] == "10":
				    Nfs400.epson_nfce.nfce( parent, filial=filial, printar=iit['printer'][0], xml=xml, inform = iit,emissao=702, numero_dav=iit['dav'], segunda=False, autorizador='' )
				else:
				    Nfs400.emitir_nfce.nfce( parent, filial=filial, printar=iit['printer'][0], xml=xml, inform = iit,emissao=702, numero_dav=iit['dav'], segunda=False, autorizador='' )

			modulos_nfe = 2 #--// Opcao para habilitar os icones e alternar a cor de fundo { 1-status, 2-emissao, 3-erro na emissao }

		if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulos_nfe, modelo, rt[4], xml_autorizado, filial, NotaFiscalParametros.pasta_gravaca_xml_final, self.p.emails, html, impressao_termica, emissao_contingencia_offline )
		    
	def copiaOriginalXml(self,xml,r,chave):

	    conn=sqldb()
	    sql=conn.dbc("NFe-NFCe: Gravando xml original para recuperacao", fil=r[3], janela=self.p )
	    if sql[0]:
		
		sql[2].execute("INSERT INTO nfeoriginal (no_chave,no_arxml) VALUES('"+chave.split('NFe')[1]+"','"+xml+"')")
		sql[2].execute("UPDATE nfes SET nf_urlqrc='"+ chave.split('NFe')[1] +"' WHERE nf_numdav='"+r[2][1]+"' and nf_ambien='"+r[2][6]+"' and nf_nnotaf='"+str(int(r[2][0]))+"' and nf_nfesce='"+r[2][3]+"' and nf_oridav='"+r[2][5]+"' and nf_idfili='"+r[2][7]+"' and nf_nserie='"+str(int(r[2][8]))+"'")

		sql[1].commit()
		conn.cls(sql[1])

	def retornaCopiaOriginalXml(self,filial,chave):

	    conn=sqldb()
	    sql=conn.dbc("NFe-NFCe: Recuperando xml original", fil=filial, janela=self.p )
	    xml=None
	    if sql[0]:
		
		if sql[2].execute("SELECT no_arxml FROM nfeoriginal WHERE no_chave='"+chave+"'"):	xml=sql[2].fetchone()[0]
		conn.cls(sql[1])
		
	    return xml
	    
	def totalizarTributos(self, dav_tipo='1', valor_ibpt='', crt='1', difal=False, modelo='55'):

		_vdIPI= _vBC= _vICMS= _vBCST= _vST= _vIPI= _vProd= _vFrete= _vDesc= _vOutro= _vNF= _vPIS= _vCOFINS= fundo_pobreza= icms_origem= icms_destino='0'
		if dav_tipo == '3':

			_vBC = str( self.p.cTDavs[0][14] ).strip()
			_vICMS = str( self.p.cTDavs[0][15] ).strip()
			_vBCST = str( self.p.cTDavs[0][16] ).strip()
			_vST = str( self.p.cTDavs[0][17] ).strip()
			_vIPI = '0'

			_vProd = str( self.p.cTDavs[0][13] ).strip()
			_vFrete = str( self.p.cTDavs[0][18] ).strip()
			_vDesc = str( self.p.cTDavs[0][20] ).strip()
			
			""" vOutros { Mudanca feita em 9-11-2017 pq nao estava pegando valor total da nota com o ST """
			#_vOutro = str( self.p.cTDavs[0][25] + self.p.cTDavs[0][22] ).strip() if self.p.ipi_voutros and self.p.cTDavs[0][22] else str( self.p.cTDavs[0][39] ).strip()
			_vOutro = str( self.p.cTDavs[0][25] + self.p.cTDavs[0][22] ).strip() if self.p.ipi_voutros and self.p.cTDavs[0][22] else self.p.valor_total_despesasacessorias
			if not _vOutro.strip():	_vOutro='0.00'
			
			_vNF = str( self.p.cTDavs[0][26] ).strip()
			_vdIPI = str(self.p.cTDavs[0][22]).strip()
			_vPIS  = str( self.p.cTDavs[0][23] ).strip()
			_vCOFINS  = str( self.p.cTDavs[0][24] ).strip()

		else:
			_vBC = str( self.p.cTDavs[0][31] ).strip()
			_vICMS = str( self.p.cTDavs[0][26] ).strip()
			_vBCST = str( self.p.cTDavs[0][34] ).strip()
			_vST = str( self.p.cTDavs[0][29] ).strip()
			_vIPI = '0'

			_vProd = str( self.p.cTDavs[0][36] ).strip()
			_vFrete = str( self.p.cTDavs[0][23] ).strip()
			_vDesc = str( self.p.cTDavs[0][25] ).strip()
			_vOutro = str( self.p.cTDavs[0][24] ).strip()
			_vNF = str( self.p.cTDavs[0][37] ).strip()

			"""  Se o sistema estiver configurado para nao retear o frete  """
			if not self.p.reateio_frete and self.p.cTDavs[0][23]:

				_vNF = str( ( self.p.cTDavs[0][37] - self.p.cTDavs[0][23] ) )
				_vFrete  = "0"
			_vPIS  = str( self.p.cTDavs[0][70] ).strip()
			_vCOFINS  = str( self.p.cTDavs[0][71] ).strip()
			
			BaseST = self.p.cTDavs[0][34]

			if difal:
				fundo_pobreza = self.p.cTDavs[0][110].split(";")[0] #-: Partilha fundo de pobreza { vFCPUFDest }
				icms_origem = self.p.cTDavs[0][110].split(";")[1] #---: Partilha icms origen { vICMSUFDest }
				icms_destino = self.p.cTDavs[0][110].split(";")[2] #--: Partilha icms destino { vICMSUFRemet }

		if self.nota_fiscal_complementar:
		    _vBC= _vNF= _vProd= valor_ibpt="0.00"
		    _vFrete= _vDesc="0.00"

		if self.p.forcar_ipi_rma.GetValue() and _vdIPI and Decimal(_vdIPI):
		    
		    _vIPI = _vdIPI
		    _vdIPI = '0.00'
		impostos = OrderedDict([
		("vBC",_vBC),
		("vICMS",_vICMS),
		("vICMSDeson",str( self.p.total_cbeneficio_vICMSDeson )),
		("vFCPUFDest",fundo_pobreza),
		("vICMSUFDest",icms_destino),
		("vICMSUFRemet",icms_origem),
		("vFCP",str( self.p.total_fcp_dentro_estado )),
		("vBCST",_vBCST),
		("vST",_vST),
		("vFCPST",'0.00'),
		("vFCPSTRet",'0.00'),
		("vProd",_vProd),
		("vFrete",_vFrete),
		("vSeg",'0.00'),
		("vDesc",_vDesc),
		("vII",'0.00'),
		("vIPI",_vIPI),
		("vIPIDevol",_vdIPI),
		("vPIS",_vPIS),
		("vCOFINS",_vCOFINS),
		("vOutro",_vOutro),
		("vNF",_vNF),
		("vTotTrib",valor_ibpt)
		])

#-----[ Dados da transportadora ]
		transportadora = veiculo = reboque = volume = None
		if modelo == '55':
    			
			indice = self.p.ListaTrans.GetFocusedItem()
			if self.p.ListaTrans.GetFocusedItem() and self.p.ListaTrans.GetItem(indice, 0).GetText().strip() and self.p.ListaTrans.GetItem(indice, 2).GetText().strip():
				cnpj = cpf = ''
				if len(self.p.ListaTrans.GetItem(indice, 0).GetText().strip()) == 11:	cpf  = self.p.ListaTrans.GetItem(indice, 0).GetText().strip()
				if len(self.p.ListaTrans.GetItem(indice, 0).GetText().strip()) == 14:	cnpj = self.p.ListaTrans.GetItem(indice, 0).GetText().strip()
				ende = self.p.ListaTrans.GetItem(indice, 3 ).GetText().strip().split('|')

				endereco = ende[4].strip()
				if ende[5].strip():	endereco +=', '+ende[5].strip()
				if ende[6].strip():	endereco +=' '+ende[6].strip()

				transportadora = OrderedDict([
				("CNPJ",cnpj),
				("CPF",cpf),
				("xNome",self.p.ListaTrans.GetItem(indice, 2).GetText().strip()),
				("IE",ende[0].strip()),
				("xEnder",endereco),
				("xMun",ende[8].strip()),
				("UF",ende[10].strip())
				])

			#--[Veiculo transporte]
			veiculo = OrderedDict([
			('placa',str(self.p.vplaca ).replace('-','').replace(' ','')),
			('UF',str(self.p.veicuf)),
			('RNTC',str(self.p.cdanTT))
			])

			#--[Reboque]
			reboque = OrderedDict([
			('placa',''),
			('UF',''),
			('RNTC','')
			])

			#--[Volumes]
			volume = OrderedDict([
			('qVol',self.p.qVolum if self.p.qVolum and self.p.qVolum.isdigit() and Decimal( self.p.qVolum ) > 0 else ''),
			('esp',self.p.especi if self.p.especi else ''),
			('marca',self.p.marcar if self.p.marcar else ''),
			('nVol',self.p.numera if self.p.numera else ''),
			('pesoL',str(Truncar.trunca(1, Decimal(self.p.pesoLQ))) if Decimal(self.p.pesoLQ) > 0 else ''),
			('pesoB',str(Truncar.trunca(1, Decimal(self.p.pesoBR))) if Decimal(self.p.pesoBR) > 0 else '')
			])

		return impostos, transportadora, veiculo, reboque, volume

	def calculoTributosProduto(self, dav_tipo = '1', indice = 1, icms='00'):

	    _pICMS = _vBC = _vICMS = _pMVAST = _vBCST = _vICMSS = _pIPI = _vBCIPI = _vIPI = _prcPIS = _prcCOF = _bacPIS = _bacCOF = _valPIS = _valCOF = _cstPIS = _cstCOF = _pRedBCST = _pRedBC =''
	    ipi_percentual_devolucao = ipi_valor_devolucao = _pICMSST = ''

	    cFop_item = str(self.p.editdanfe.GetItem(indice,32).GetText().strip())

	    _pICMS   = str(self.p.editdanfe.GetItem(indice,17).GetText().strip())
	    _vBC     = str(self.p.editdanfe.GetItem(indice,22).GetText().strip())
	    _vICMS   = str(self.p.editdanfe.GetItem(indice,27).GetText().strip())
	    _pMVAST  = str(self.p.editdanfe.GetItem(indice,20).GetText().strip()) if self.p.editdanfe.GetItem(indice,20).GetText() and Decimal( self.p.editdanfe.GetItem(indice,20).GetText() ) else ''
	    _vBCST   = str(self.p.editdanfe.GetItem(indice,25).GetText().strip()) if self.p.editdanfe.GetItem(indice,25).GetText() and Decimal( self.p.editdanfe.GetItem(indice,25).GetText() ) else ''
	    _vICMSST = str(self.p.editdanfe.GetItem(indice,30).GetText().strip()) if self.p.editdanfe.GetItem(indice,30).GetText() and Decimal( self.p.editdanfe.GetItem(indice,30).GetText() ) else ''

	    _pIPI   = str(self.p.editdanfe.GetItem(indice,19).GetText().strip()) if self.p.editdanfe.GetItem(indice,19).GetText() and Decimal( self.p.editdanfe.GetItem(indice,19).GetText() ) else ''
	    _vBCIPI = str(self.p.editdanfe.GetItem(indice,24).GetText().strip()) if self.p.editdanfe.GetItem(indice,24).GetText() and Decimal( self.p.editdanfe.GetItem(indice,24).GetText() ) else ''
	    _vIPI   = str(self.p.editdanfe.GetItem(indice,29).GetText().strip()) if self.p.editdanfe.GetItem(indice,29).GetText() and Decimal( self.p.editdanfe.GetItem(indice,29).GetText() ) else ''

	    _prcPIS = str(self.p.editdanfe.GetItem(indice,45).GetText().strip()) if self.p.editdanfe.GetItem(indice,45).GetText() and Decimal( self.p.editdanfe.GetItem(indice,45).GetText() ) else ''
	    _bacPIS = str(self.p.editdanfe.GetItem(indice,47).GetText().strip()) if self.p.editdanfe.GetItem(indice,47).GetText() and Decimal( self.p.editdanfe.GetItem(indice,47).GetText() ) else ''
	    _valPIS = str(self.p.editdanfe.GetItem(indice,49).GetText().strip()) if self.p.editdanfe.GetItem(indice,49).GetText() and Decimal( self.p.editdanfe.GetItem(indice,49).GetText() ) else ''
	    _cstPIS = str(self.p.editdanfe.GetItem(indice,51).GetText().strip()) if self.p.editdanfe.GetItem(indice,51).GetText() else '06'

	    _prcCOF = str(self.p.editdanfe.GetItem(indice,46).GetText().strip()) if self.p.editdanfe.GetItem(indice,46).GetText() and Decimal( self.p.editdanfe.GetItem(indice,46).GetText() ) else ''
	    _bacCOF = str(self.p.editdanfe.GetItem(indice,48).GetText().strip()) if self.p.editdanfe.GetItem(indice,48).GetText() and Decimal( self.p.editdanfe.GetItem(indice,48).GetText() ) else ''
	    _valCOF = str(self.p.editdanfe.GetItem(indice,50).GetText().strip()) if self.p.editdanfe.GetItem(indice,50).GetText() and Decimal( self.p.editdanfe.GetItem(indice,50).GetText() ) else ''
	    _cstCOF = str(self.p.editdanfe.GetItem(indice,52).GetText().strip()) if self.p.editdanfe.GetItem(indice,52).GetText() else '06'

	    _pFCP = str(self.p.editdanfe.GetItem(indice,69).GetText().strip()) if self.p.editdanfe.GetItem(indice,69).GetText() and Decimal(self.p.editdanfe.GetItem(indice,69).GetText()) else ''
	    _vFCP = str(self.p.editdanfe.GetItem(indice,70).GetText().strip()) if self.p.editdanfe.GetItem(indice,70).GetText() and Decimal(self.p.editdanfe.GetItem(indice,70).GetText()) else ''

	    """ Desoneracao ICMS-Desoneracao [ CST 20 ] """
	    motivo_beneficio = str(self.p.editdanfe.GetItem(indice,72).GetText().strip()) 
	    reduca_beneficio = str(self.p.editdanfe.GetItem(indice,73).GetText().strip()) if self.p.editdanfe.GetItem(indice,73).GetText().strip() else '0' #--// pRedBC
	    valord_beneficio = str(self.p.editdanfe.GetItem(indice,74).GetText().strip()) #--// vICMSDeson
	    
	    #-------------// [ Partilha do ICMS Difal ]
	    """  Partilha do ICMS  """
	    base_calculo = str(self.p.editdanfe.GetItem(indice,53).GetText().strip()) #-----------------------------------: Valor da BC do ICMS na UF de destino	
	    aliquota_fundo = str(self.p.editdanfe.GetItem(indice,54).GetText().strip()) #---------------------------------: Percentual do ICMS relativo ao Fundo de Combate à Pobreza (FCP) na UF de destino
	    aliquota_destino = str(format(Decimal(self.p.editdanfe.GetItem(indice,55).GetText().strip()),'.2f')) #-------: Alíquota interna da UF de destino
	    aliquota_inter_estadual = str(format(Decimal(self.p.editdanfe.GetItem(indice,56).GetText().strip()),'.2f')) #-: Alíquota interestadual das UF envolvidas
	    aliquota_provisoria = str(format( Decimal( self.p.editdanfe.GetItem(indice,57).GetText().strip() ),'.2f')) #--: Percentual provisório de partilha do ICMS Interestadual
	    valor_icms_fundo = str(self.p.editdanfe.GetItem(indice,58).GetText().strip()) #-------------------------------: Valor do ICMS relativo ao Fundo de Combate à Pobreza (FCP) da UF de destino
	    valor_icms_destino = str(self.p.editdanfe.GetItem(indice,59).GetText().strip()) #-----------------------------: Valor do ICMS Interestadual para a UF de destino
	    valor_icms_origem = str(self.p.editdanfe.GetItem( indice,60).GetText().strip()) #-----------------------------: Valor do ICMS Interestadual para a UF do remetente
		
	    if _cstPIS in ['01','02'] and not _prcPIS:	_prcPIS = '0.00'
	    if _cstPIS in ['01','02'] and not _bacPIS:	_bacPIS = '0.00'
	    if _cstPIS in ['01','02'] and not _valPIS:	_valPIS = '0.00'

	    if _cstCOF in ['01','02'] and not _prcCOF:	_prcCOF = '0.00'
	    if _cstCOF in ['01','02'] and not _bacCOF:	_bacCOF = '0.00'
	    if _cstCOF in ['01','02'] and not _valCOF:	_valCOF = '0.00'

	    ipi_percentual_devolucao = str(self.p.editdanfe.GetItem(indice,19).GetText().strip())
	    ipi_valor_devolucao = str(self.p.editdanfe.GetItem(indice,29).GetText().strip())

	    imposto_ipi = ''
	    #----// Precisa ver o percentual do credito de icms
	    _pCredSN = ''
	    _vCredICMSSN = ''
	    
	    _modBC,_modBCST = '3', '4'
	    if self.p.modbcstnotasf.GetValue().split('-')[0]:	_modBCST = self.p.modbcstnotasf.GetValue().split('-')[0]
	    """ Alteracao do ICMS ST para devolucao com CST9000 """
	    avancar900 = False
	    if icms == "900" and _vBC and Decimal(_vBC) and _pICMS and Decimal(_pICMS) and _vICMS and Decimal(_vICMS):

		avancar900 = True
		_vBCST = '0.00'
		_pICMSST = '0.00'
		_vICMSST = '0.00'
		    
	    if icms == "900" and _vBCST and Decimal(_vBCST) and _vBCST and Decimal(_vICMSST):

		avancar900 = True
		_pICMSST = '0.00'
		_pMVAST = '0.00'

	    if  icms == '00':

		if self.nota_fiscal_complementar:	_vBC= _pICMS="0.00"
		imposto_diversos = OrderedDict([
		("modBC",_modBC), #--// Modalidade de determinação da BC do ICMS: 0 - Margem Valor Agregado (%); 1 - Pauta (valor); 2 - Preço Tabelado Máximo (valor); 3 - Valor da Operação.
		("vBC",_vBC),
		("pICMS",_pICMS),
		("vICMS",_vICMS),
		("pFCP",_pFCP),
		("vFCP",_vFCP)
		])

		if self.p.forcar_ipi_rma.GetValue() and cFop_item in ['6949']:
		    imposto_ipi = OrderedDict([
		    ("CST",""),
		    ("vBC",_vBCIPI),
		    ("pIPI",_pIPI),
		    ("vIPI",_vIPI)
		    ])

		    ipi_percentual_devolucao = ""
		    ipi_valor_devolucao = ""

	    elif icms == '10':
		if not _pRedBCST:	_pRedBCST="0.00"
		if not _vBCST:	_vBCST="0.00"
		if not _pICMSST:	_pICMSST="0.00"
		if not _vICMSST:	_vICMSST="0.00"
		
		imposto_diversos = OrderedDict([
		("modBC",_modBC),
		("vBC",_vBC),
		("pICMS",_pICMS),
		("vICMS",_vICMS),
		("vBCFCP",""),
		("pFCP",""),
		("vFCP",""),
		("modBCST",_modBCST),
		("pMVAST",_pMVAST),
		("pRedBCST",_pRedBCST),
		("vBCST",_vBCST),
		("pICMSST",_pICMSST),
		("vICMSST",_vICMSST),
		("vBCFCPST",""),
		("pFCPST",""),
		("vFCPST","")
		])

	    elif icms == '20':
		imposto_diversos = OrderedDict([
		("modBC",_modBC),
		("pRedBC",reduca_beneficio),
		("vBC",_vBC),
		("pICMS",_pICMS),
		("vICMS",_vICMS),
		("vBCFCP",""),
		("pFCP",""),
		("vFCP",""),
		("vFCPST",""),
		("vICMSDeson",valord_beneficio),
		("motDesICMS",motivo_beneficio)
		])
		
	    elif icms == '60':
		imposto_diversos = OrderedDict([
		("vBCSTRet",''),
		("pST",''),
		("vICMSSTRet",''),
		("vBCFCPSTRet",''),
		("pFCPSTRet",''),
		("vFCPSTRet",''),
		("pRedBCEfet",''),
		("vBCEfet",''),
		("pICMSEfet",''),
		("vICMSEfet",'')
		])
	    elif icms in ['70','90']:
		if not _pMVAST:	_pMVAST='0.00'
		if not _vBCST:	_vBCST='0.00'
		if not _pICMSST:	_pICMSST='0.00'
		if not _vICMSST:	_vICMSST='0.00'
		if not _pRedBC and icms=='70':	_pRedBC='0.00'
		if not _pRedBCST and icms=='70':	_pRedBCST='0.00'
		
		imposto_diversos = OrderedDict([
		("modBC",_modBC),
		("pRedBC",_pRedBC),
		("vBC",_vBC),
		("pICMS",_pICMS),
		("vICMS",_vICMS),
		("vBCFCP",''),
		("pFCP",''),
		("vFCP",''),
		("modBCST",_modBCST),
		("pMVAST",_pMVAST),
		("pRedBCST",_pRedBCST),
		("vBCST",_vBCST),
		("pICMSST",_pICMSST),
		("vICMSST",_vICMSST),
		("vBCFCPST",''),
		("pFCPST",''),
		("vFCPST",''),
		("vICMSDeson",''),
		("motDesICMS",motivo_beneficio)
		])
		
	    elif icms == "101":
		imposto_diversos = OrderedDict([
		("pCredSN",_pCredSN if _pCredSN else '0'),
		("vCredICMSSN",_vCredICMSSN if _vCredICMSSN else '0')])
		
	    elif icms == '102': imposto_diversos = None
	    elif icms in ['201']:
		imposto_diversos = OrderedDict([
		("modBCST",_modBCST),
		("pMVAST",_pMVAST),
		("pRedBCST",''),
		("vBCST",_vBCST),
		("pICMSST",''),
		("vICMSST",_vICMSST),
		("vBCFCPST",''),
		("pFCPST",''),
		("vFCPST",''),
		("pCredSN",_pCredSN),
		("vCredICMSSN",_vCredICMSSN)
		])

	    elif icms in ['202']:

		if not _pICMSST:	_pICMSST = '0.00'
		if not _pMVAST:	_pMVAST ='0.00'

		imposto_diversos = OrderedDict([
		("modBCST",_modBCST),
		("pMVAST",_pMVAST),
		("pRedBCST",''),
		("vBCST",_vBCST),
		("pICMSST",_pICMSST),
		("vICMSST",_vICMSST),
		("vBCFCPST",''),
		("pFCPST",''),
		("vFCPST",''),
		("pCredSN",_pCredSN),
		("vCredICMSSN",_vCredICMSSN)
		])
		
	    elif icms == '500':
		imposto_diversos = OrderedDict([
		("vBCSTRet",''),
		("pST",''),
		("vICMSSTRet",''),
		("vBCFCPSTRet",''),
		("pFCPSTRet",''),
		("vFCPSTRet",''),
		("pRedBCEfet",''),
		("vBCEfet",''),
		("pICMSEfet",''),
		("vICMSEfet",'')
		])
		
	    elif icms=='900' and avancar900:
		imposto_diversos = OrderedDict([
		("modBC",_modBC), #--// Modalidade de determinação da BC do ICMS: 0 - Margem Valor Agregado (%); 1 - Pauta (valor); 2 - Preço Tabelado Máximo (valor); 3 - Valor da Operação.
		("vBC",_vBC),
		("pICMS",_pICMS),
		("vICMS",_vICMS),
		("modBCST",_modBCST),
		("pMVAST",_pMVAST),
		("pRedBCST",_pRedBCST),
		("vBCST",_vBCST),
		("pICMSST",_pICMSST),
		("vICMSST",_vICMSST)
		])

	    else:

		#--// Imposto nao implementado [ Faz retornar de Schema ]
		imposto_diversos = OrderedDict([])
		
	    imposto_pis = OrderedDict([
	    ("CST",_cstPIS),
	    ("vBC",_bacPIS),
	    ("pPIS",_prcPIS),
	    ("vPIS",_valPIS)
	    ])
	    if _cstPIS=="99":
		_qBCProd="0.0000"
		_vAliqProd="0.0000"
		_valPIS="0.00"
		imposto_pis = OrderedDict([
		("CST",_cstPIS),
		("vBC",_bacPIS),
		("pPIS",_prcPIS),
		("qBCProd",_qBCProd),
		("vAliqProd",_vAliqProd),
		("vPIS",_valPIS)
		])
		
	    imposto_cofins = OrderedDict([
	    ("CST",_cstCOF),
	    ("vBC",_bacCOF),
	    ("pCOFINS",_prcCOF),
	    ("vCOFINS",_valCOF)
	    ])
	    if _cstCOF=="99":
		_qBCProd="0.0000"
		_vAliqProd="0.0000"
		_valCOF="0.00"
		imposto_cofins = OrderedDict([
		("CST",_cstCOF),
		("vBC",_bacCOF),
		("pCOFINS",_prcCOF),
		("qBCProd",_qBCProd),
		("vAliqProd",_vAliqProd),
		("vCOFINS",_valCOF)
		])
		
	    imposto_devolucao = {
	    "pDevol":ipi_percentual_devolucao,
	    "vIPIDevol":ipi_valor_devolucao
	    }

	    difal = OrderedDict([
	    ('vBCUFDest',base_calculo),
	    ('vBCFCPUFDest',base_calculo),
	    ('pFCPUFDest',aliquota_fundo),
	    ('pICMSUFDest',aliquota_destino),
	    ('pICMSInter',aliquota_inter_estadual),
	    ('pICMSInterPart',aliquota_provisoria),
	    ('vFCPUFDest',valor_icms_fundo),
	    ('vICMSUFDest',valor_icms_destino),
	    ('vICMSUFRemet',valor_icms_origem)
	    ])

	    return imposto_diversos, imposto_pis, imposto_cofins, imposto_devolucao, difal, imposto_ipi

	def retornaProduto( self, modelo_nf = '55', dav_tipo = '1', indice = 0 ):

		_cProd=self.p.editdanfe.GetItem(indice,1).GetText().strip()
		_cEAN=self.p.editdanfe.GetItem(indice,2).GetText().strip() if not self.p.descartar_barras.GetValue() else 'SEM GTIN'
		_xProd=self.p.editdanfe.GetItem(indice,3).GetText().strip()
		_NCM=self.p.editdanfe.GetItem(indice,34).GetText().strip()
		_CEST=self.p.editdanfe.GetItem(indice,44).GetText().strip()
		_CFOP=self.p.editdanfe.GetItem(indice,32).GetText().strip()
		_uCom=self.p.editdanfe.GetItem(indice,5).GetText().strip()
		_qCom=self.p.editdanfe.GetItem(indice,4).GetText().strip().replace(',','')
		_vUnCom=self.p.editdanfe.GetItem(indice,6).GetText().strip().replace(',','')
		_vProd=self.p.editdanfe.GetItem(indice,7).GetText().strip().replace(',','')
		_uTrib=self.p.editdanfe.GetItem(indice,5).GetText().strip()
		_qTrib=self.p.editdanfe.GetItem(indice,4).GetText().strip().replace(',','')
		_vUnTrib=self.p.editdanfe.GetItem(indice,6).GetText().strip().replace(',','')
		_vFrete=self.p.editdanfe.GetItem(indice,14).GetText().strip().replace(',','') if Decimal( self.p.editdanfe.GetItem(indice,14).GetText().strip().replace(',','') ) else ''
		_vDesc=self.p.editdanfe.GetItem(indice,16).GetText().strip().replace(',','') if Decimal( self.p.editdanfe.GetItem(indice,16).GetText().strip().replace(',','') ) else ''
		_vOutro=self.p.editdanfe.GetItem(indice,15).GetText().strip().replace(',','') if Decimal( self.p.editdanfe.GetItem(indice,15).GetText().strip().replace(',','') ) else ''
		_desAce=self.p.editdanfe.GetItem(indice,64).GetText().strip().replace(',','') if Decimal( self.p.editdanfe.GetItem(indice,64).GetText().strip().replace(',','') ) else ''
		_idProd=self.p.editdanfe.GetItem(indice,35).GetText().strip()
		_benfis=self.p.editdanfe.GetItem(indice,71).GetText().strip()

		if _desAce and _vOutro:	_vOutro=( Decimal(_vOutro) + Decimal(_desAce) )
		if _desAce and not _vOutro:	_vOutro=_desAce
		produtos = {
			"cProd":_cProd,
			"cEAN":_cEAN,
			"xProd":_xProd,
			"NCM":_NCM,
			"CEST":_CEST,
			"indEscala":"",
			"CNPJFab":"",
			"cBenef":_benfis,
			"EXTIPI":"",
			"CFOP":_CFOP,
			"uCom":_uCom,
			"qCom":_qCom,
			"vUnCom":_vUnCom,
			"vProd":_vProd,
			"cEANTrib":_cEAN,
			"uTrib":_uTrib,
			"qTrib":_qTrib,
			"vUnTrib":_vUnTrib,
			"vFrete":_vFrete,
			"vSeg":"",
			"vDesc":_vDesc,
			"vOutro":_vOutro,
			"indTot":'1',
			"idProdVenda":_idProd
			}

		return produtos

	def valorAproximadoTributos( self, produto_geral = 1, ibpt_produto = '', modelo = '55' ):

		if produto_geral == 1:

			total_federal =	total_estadual = total_municipal = total_aproximado = Decimal('0.00')
			registros = ibpt_produto.GetItemCount()
			
			for i in range( registros ):
    				
				dados_ibpt = str( ibpt_produto.GetItem( i, 43 ).GetText().strip() )
				if dados_ibpt:
					
					total_federal    += Decimal( dados_ibpt.split("|")[0] )	
					total_estadual   += Decimal( dados_ibpt.split("|")[2] )
					total_municipal  += Decimal( dados_ibpt.split("|")[3] ) 
					total_aproximado  = ( total_federal + total_estadual + total_municipal )

			return str( total_federal ), str( total_estadual ), str( total_municipal ), str( total_aproximado )

		elif produto_geral == 2:

			valor_produto_ibpt = str( '0.00' )
			if ibpt_produto and ibpt_produto:
					
				valor_federal   = Decimal( ibpt_produto.split("|")[0] )
				valor_estadual  = Decimal( ibpt_produto.split("|")[2] )
				valor_municipal = Decimal( ibpt_produto.split("|")[3] )
				
				valor_produto_ibpt  = str( ( valor_federal + valor_estadual + valor_municipal ) ) #-: Valor Individual Total dos Tributos ( Federal + Estadual + Municipal ) p/Produtos

			""" Nota fiscal complementar """
			if self.nota_fiscal_complementar:	valor_produto_ibpt = str( '0.00' )
			return valor_produto_ibpt	

	def enderecos(self, modelo='55', dav_tipo = '1'):

		cli_dados = ''
		cli_endere = ''
		endereco_nota = []
		endereco_entrega = []
		dados_cliente = []

		if self.p.cTClie:	cli_endere, cli_dados = self.p.destinat.GetValue().split('-')[0], self.p.cTClie[0] #-// Endereco para impressao 1-endereco, 2-endereco

		if dav_tipo == '3': #-// Devolucao de compra RMA
			endereco_nota.append( cli_dados[8].decode('utf-8').strip() ) #// Endreco
			endereco_nota.append( cli_dados[9].decode('utf-8').strip() ) #// Numero
			endereco_nota.append( cli_dados[10].decode('utf-8').strip() ) #// Complemento
			endereco_nota.append( cli_dados[11].decode('utf-8').strip() ) #// Bairro
			endereco_nota.append( cli_dados[12].decode('utf-8').strip() ) #// Municipio
			endereco_nota.append( cli_dados[15].decode('utf-8').strip() ) #// Codigo do municipio
			endereco_nota.append( cli_dados[14].decode('utf-8').strip() ) #// unidade federal
			endereco_nota.append( cli_dados[13].decode('utf-8').strip() ) #// CEP

			dados_cliente.append( cli_dados[6].decode('utf-8').strip() ) #// Razao socioa
			dados_cliente.append( cli_dados[7].decode('utf-8').strip() ) #// Fantasia
			dados_cliente.append( cli_dados[1] ) #// cpf-cnpj
			dados_cliente.append( cli_dados[2] ) #// Inscricao estadual
			dados_cliente.append( cli_dados[16].replace(' ','').replace('-','').replace(')','').replace('(','').replace('.','') ) #// Telefone
			dados_cliente.append( '' ) #// Email
			dados_cliente.append( self.p.indcadIEst.GetValue().split("-")[0] )
		else:
			if self.p.cTClie:

				dados_cliente.append( cli_dados[1].decode('utf-8').strip() ) #// Razao social
				dados_cliente.append( cli_dados[2].decode('utf-8').strip() ) #// Fantasia
				dados_cliente.append( cli_dados[3] ) #// CPF-CNPJ
				dados_cliente.append( cli_dados[4] if cli_dados[4].strip() !='ISENTO' else '' ) #// Inscricao estadual
				dados_cliente.append( cli_dados[17].replace(' ','').replace('-','').replace(')','').replace('(','').replace('.','') ) #// Telefone
				dados_cliente.append( informes.remover_acentos( cli_dados[16].decode('utf-8').strip() ) ) #// Email
				if modelo == '55':	dados_cliente.append( self.p.indcadIEst.GetValue().split("-")[0] )
				if modelo == '65':	dados_cliente.append('9') #-//

				endereco_nota = self.enderecosDados( cli_dados, 1, dav_tipo, cli_endere, str( modelo ) )
				endereco_entrega = self.enderecosDados( cli_dados, 2, dav_tipo, cli_endere, str( modelo ) )
		return endereco_nota, endereco_entrega, dados_cliente

	def nfeCalculaDigito(self, chave):

		soma = 0
		m = 2
		for i in range(len(chave)-1, -1, -1):
			
			c = chave[i]
			soma += int(c) * m
			m += 1
			if m > 9:
				m = 2

		digito = 11 - (soma % 11)
		if digito > 9:	digito = 0

		return str( digito )

	def numeroCompoeChave(self, numero_nota ):

		numeros_invalidos=[
		'00000000','11111111','22222222','33333333','44444444','55555555','66666666',
		'77777777','88888888','99999999','12345678','23456789','34567890','45678901',
		'56789012','78901234','78901234','89012345','90123456','01234567'
		]
		
		_cNF = {'0':'9','1':'8','2':'7','3':'6','4':'5','5':'4','6':'3','7':'2','8':'1','9':'0'}
		rcNF = ""
		for i in numero_nota:

		    rcNF +=_cNF[i]

		if rcNF in numeros_invalidos:	rcNF=str(randint(4**11, 4**13-1)).zfill(8)
		if rcNF in numeros_invalidos:	rcNF=str(randint(4**11, 4**13-1)).zfill(8)
		return rcNF

	def enderecosDados(self, cli_dados, opcao, emissao, cli_endere, modelo_nf ):
	
		avancar_endereco1=False
		avancar_endereco2=False

		if opcao == 1 and str(emissao) in ['1','2'] and self.p.destinat.GetValue().split('-')[0] == "2":	avancar_endereco1=True
		if opcao == 1 and str(emissao) in ['1','2'] and len(self.p.destinat.GetValue().split('-')[0])==3 and cli_dados[51]:	avancar_endereco2=True
		
		if opcao == 2 and str(modelo_nf.strip())=='55' and self.p.entregar.GetValue().split('-')[0]=="2":	avancar_endereco1=True
		if opcao == 2 and str(modelo_nf.strip())=='55' and len(self.p.entregar.GetValue().split('-')[0])==3 and cli_dados[51]:	avancar_endereco2=True
		
		cli_endereco = cli_numero = cli_complemento = cli_bairro = cli_municipio = cli_cdmunicipio = cli_uf = cli_cep = ''
		
		if opcao == 1:

			cli_endereco    = cli_dados[20].decode('utf-8').strip() if cli_endere == '2' else cli_dados[8].decode('utf-8').strip()
			cli_numero      = cli_dados[25].decode('utf-8').strip() if cli_endere == '2' else cli_dados[13].decode('utf-8').strip()
			cli_complemento = cli_dados[26].decode('utf-8').strip() if cli_endere == '2' else cli_dados[14].decode('utf-8').strip()
			cli_bairro      = cli_dados[21].decode('utf-8').strip() if cli_endere == '2' else cli_dados[9].decode('utf-8').strip()
			cli_municipio   = cli_dados[22].decode('utf-8').strip() if cli_endere == '2' else cli_dados[10].decode('utf-8').strip()
			cli_cdmunicipio = cli_dados[23].decode('utf-8').strip() if cli_endere == '2' else cli_dados[11].decode('utf-8').strip()
			cli_uf          = cli_dados[27].decode('utf-8').strip() if cli_endere == '2' else cli_dados[15].decode('utf-8').strip()
			cli_cep         = cli_dados[24].decode('utf-8').strip() if cli_endere == '2' else cli_dados[12].decode('utf-8').strip()

		""" Endereço 2-Entrega do Destinatario """
		if avancar_endereco1:
					
			cli_endereco    = cli_dados[20].decode('utf-8').strip()
			cli_numero      = cli_dados[25].decode('utf-8').strip()
			cli_complemento = cli_dados[26].decode('utf-8').strip()
			cli_bairro      = cli_dados[21].decode('utf-8').strip()
			cli_municipio   = cli_dados[22].decode('utf-8').strip()
			cli_cdmunicipio = cli_dados[23].decode('utf-8').strip()
			cli_uf          = cli_dados[27].decode('utf-8').strip()
			cli_cep         = cli_dados[24].decode('utf-8').strip()

		if avancar_endereco2:
		
			if opcao==2 and self.p.entregar.GetValue().split('-')[0]:	codigo_endereco=self.p.entregar.GetValue().split('-')[0].strip()
			else:	codigo_endereco=self.p.destinat.GetValue().split('-')[0].strip()
			
			endereco_destino = numeros.retornoEndrecos(cli_dados[51], codigo_endereco)
		
			if endereco_destino:
		
				cli_endereco    = endereco_destino[1].decode('utf-8').strip()
				cli_numero      = endereco_destino[2].decode('utf-8').strip()
				cli_complemento = endereco_destino[3].decode('utf-8').strip()
				cli_bairro      = endereco_destino[4].decode('utf-8').strip()
				cli_municipio   = endereco_destino[5].decode('utf-8').strip()
				cli_cdmunicipio = endereco_destino[9].decode('utf-8').strip()
				cli_uf          = endereco_destino[7].decode('utf-8').strip()
				cli_cep         = endereco_destino[6].decode('utf-8').strip()

		return cli_endereco, cli_numero, cli_complemento, cli_bairro, cli_municipio, cli_cdmunicipio, cli_uf, cli_cep        

	def retornarPagamentos(self, lista, tipo_dav, numero_dav, filial, modelo ):
        
		"""  Ajusta as nossas formas de pagamentos as formas da 4.00  """

		"""  Utilizar se nao houver rateio de frete  """
		rateio_frete = True if not self.p.reateio_frete and self.p.cTDavs[0][23] else False
		valor_nota_fiscal = str( ( self.p.cTDavs[0][37] - self.p.cTDavs[0][23] ) ) if tipo_dav!='3' else '0.00'
		#---------------------------// Nota com frete nao rateado //-------------------------#

		relacao_duplicatas = {}
		valor_total_parcelas = Decimal('0.00')

		self.listagem_pagamentos = {}
		self.forma_pagamento = {'01':'01', '02':'02', '03':'02', '04':'03',\
					'05':'04', '06':'15', '07':'99', '08':'99',\
					'09':'10', '10':'05', '11':'99', '12':'99'}

		u"""  Convertendo para formas de pagamento da 4.00
 			 01=Dinheiro, 02=Cheque, 03=Cartão de Crédito, 04=Cartão de Débito
			 05=Crédito Loja, 10=Vale Alimentação, 11=Vale Refeição, 12=Vale Presente
			 13=Vale Combustível, 15=Boleto Bancário, 90=Sem Pagamento, 99=Outros
		"""
		if rateio_frete and not self.nota_fiscal_complementar:	self.listagem_pagamentos = {'01':(valor_nota_fiscal,'','0')} #--// Frete nao rateado
		else:
			convertido = ""
			for p in lista.split('|'):
				if p:

					f, v = p.split(';')
					convertido +=self.forma_pagamento[f] +';'+ v +'|'
			
			#--// Separa, ajusta as formas de pagamentos e totaliza para 4.00
			for i in convertido.split('|'):
				if i:
					f, v = i.split(';')
					valor = self.somatoria( f, convertido.split('|') )
					if f not in self.listagem_pagamentos and valor:
						indPag = '1' if f in ['15'] else '0'
						integracao = '2' if f in ['03','04'] else ''
						self.listagem_pagamentos[f] = ( str( valor ), integracao, indPag )

			#--// Forma de pagamento para devolucao e RMA
			if tipo_dav in ['2','3']:	self.listagem_pagamentos = {'90':('0.00','','0')}
			if self.nota_fiscal_complementar:	self.listagem_pagamentos = {'90':('0.00','','0')}

			#--// Duplicatas e boletos
			ordem = 1	
			contas_areceber = ""
			if self.p.relacao_cobranca_receber and len( login.filialLT[filial][35].split(";") ) >= 97 and login.filialLT[filial][35].split(";")[96] == "T":	contas_areceber = self.p.relacao_cobranca_receber
			if tipo_dav !='3' and not self.p.listaQuan and contas_areceber and ( len( contas_areceber.split('|') ) - 1 ) > 0 and modelo == '55' and not self.p.meia_nf400:

				for dpl in contas_areceber.split('|'):
				
					if dpl and dpl[0]:
							
						fp = dpl.split(';')
						duplicata = str(fp[0])
						vencimento = format( datetime.datetime.strptime( str( fp[1] ), "%d/%m/%Y").date(), '%Y-%m-%d' )
						formapagamento = str(fp[2])
						valor_apagar = str(fp[3]).replace(',','')

						imprimir = False
						if formapagamento[:2] == "06":	imprimir = True
						if formapagamento[:2] == "07" and len( login.filialLT[ filial ][35].split(";") ) >=37 and login.filialLT[ filial ][35].split(";")[36] == "T":	imprimir = True	

						if imprimir:
						    
							relacao_duplicatas[ordem] = vencimento, valor_apagar
							valor_total_parcelas += Decimal( valor_apagar )
							ordem +=1

			elif tipo_dav !='3' and self.p.listaQuan and modelo=='55' and not self.p.meia_nf400: #-: Recebimento no caixa com emissao do danfe

				for dpl in range( self.p.listaQuan ):
						
					duplicata = str(self.p.davNumero)+ "-" + str(self.p.listaRece.GetItem( dpl, 0 ).GetText())
					vencimento = format( datetime.datetime.strptime( str( self.p.listaRece.GetItem( dpl, 1 ).GetText() ), "%d/%m/%Y").date(), '%Y-%m-%d' )
					formapagamento = str(self.p.listaRece.GetItem(dpl, 2).GetText())					
					valor_apagar = str(self.p.listaRece.GetItem(dpl, 3).GetText()).replace(',','')
				
					imprimir = False
					if formapagamento[:2] == "06":	imprimir = True
					if formapagamento[:2] == "07" and len( login.filialLT[filial][35].split(";") ) >=37 and login.filialLT[filial][35].split(";")[36] == "T":	imprimir = True	
						
					if imprimir:

						relacao_duplicatas[ordem] = vencimento, valor_apagar
						valor_total_parcelas += Decimal( valor_apagar )
						ordem +=1
			if valor_total_parcelas and modelo=='55':
				valor_total_parcelas = OrderedDict([
				('nFat',str(int(numero_dav))),
				('vOrig',str(valor_total_parcelas)),
				('vDesc','0.00'),
				('vLiq',str(valor_total_parcelas))
				])

		return self.listagem_pagamentos, relacao_duplicatas, valor_total_parcelas

	def somatoria(self, f, l ):
    	
		valor = Decimal('0.00')
		for i in l:
			if i.split(';')[0] == f:	valor +=Decimal( i.split(';')[1] )

		return valor

	def dadosAdicionais(self, parent, filial, emissao):

		ibpt_federal, ibpt_estadual, ibpt_municipal, ibpt_valortotal = self.valorAproximadoTributos( produto_geral=1, ibpt_produto=self.p.editdanfe, modelo=55 )

		dados_adicionais = informacoes_ibpt_imposto = adicionais_rodape = ""
		valor_apropencentual = "" if not parent.percentual_aproveitamento_icms or not parent.aproveitamento_credito.GetValue() else format( parent.percentual_aproveitamento_icms, ',' ) 
		valor_aproveitamento = "" if not parent.percentual_aproveitamento_icms or not parent.aproveitamento_credito.GetValue() else format( parent.valor_total_aproveitamento_icm, ',' )

		informe_1 = 'DOCUMENTO EMITIDO POR ME OU EPP OPTANTE PELO SIMPLES NACIONAL|NAO GERA DIREITO A CREDITO FISCAL DE IPI|'
		informe_2 = 'PERMITE O APROVEITAMENTO DO CREDITO DE ICMS NO VALOR DE R$ '+str( valor_aproveitamento )+'|CORRESPONDENTE A ALIQUOTA DE '+str( valor_apropencentual )+'%, NOS TERMOS DO ART. 23 DA LEI COMPLEMENTAR No 123, DE 2006|NF-e: Emitida nos termos do Art. 158, caput e  Paragrafo 1o do RICMS Livro VI do Decreto numero 27427/2000.|'

		if emissao == '1' and parent.cTDavs[0][109]:

			dados_ibpt = parent.cTDavs[0][109].split("|")
			valo_imposto = "Trib aprox R$ "+format( Decimal( ibpt_valortotal ),',')+" {Federal R$ "+format( Decimal( ibpt_federal ),',')+" Estadual R$:"+format( Decimal( ibpt_estadual ),',')+" Municipal R$:"+format( Decimal( ibpt_municipal ),',')+" }|Fonte: "+str( dados_ibpt[6] )+" "+str( dados_ibpt[5] )+" "+str( dados_ibpt[4] ) +'|'
			informacoes_ibpt_imposto = "Tributos Totais Incidentes Lei Federal 12.741/2012|"+valo_imposto

		regime_tributario = login.filialLT[filial][30].split(";")[11]
		if emissao == '1' and regime_tributario == '1':	dados_adicionais +=informe_1
		if emissao == '1' and regime_tributario == '1' and valor_apropencentual and valor_aproveitamento:	dados_adicionais +=informe_2
		
		if emissao and informacoes_ibpt_imposto:	dados_adicionais +='|'+ informacoes_ibpt_imposto #--// IBPT >--> Informacoes de tributos federal,estadual,municipal

		dados_complementar_filial = parent.informacoes_adicionais_filiais.strip() if parent.informacoes_adicionais_filiais else login.rdpnfes
		
		"""  Notas de rodape"""
		if dados_complementar_filial:

		    __fi='<'+filial.upper()+'>'
		    __ff='</'+filial.upper()+'>'
		    __rd=dados_complementar_filial.upper()
		    dados_rodape_filial = __rd.split(__fi)[1].split(__ff)[0].strip().replace('\n','|') if __fi in __rd and  __ff in __rd else ""
		    dados_adicionais += '|'+dados_rodape_filial
		
		if parent.dadosA.strip():	dados_adicionais +='||'+parent.dadosA.strip().replace('\n','|')
		return dados_adicionais


class DadosCertificadoRetornos:
    
	def dadosIdentificacao(self,filial, parent, modelo='55', gravar = False ):

		retorno = True
		i = login.filialLT[filial][30].split(';')

		serie_nfe  = i[3]
		serie_nfce = i[17]
		id_csc = i[20]
		numero_csc = i[21] 
		senha = i[5]
		certificado = diretorios.esCerti + i[6]
		uf = i[12]
		ambiente = i[9]
		regime = i[11]
		cnpj = login.filialLT[filial][9]

		versao='3.00' if modelo=='58' else i[2]
		if modelo=='58':	serie='1'
		else:
		    serie=serie_nfe if modelo == '55' else serie_nfce

		NotaFiscalParametros.caminho_certificado = certificado
		NotaFiscalParametros.senha_certificado = senha
		NotaFiscalParametros.ambiente = ambiente
		NotaFiscalParametros.modelo = modelo
		NotaFiscalParametros.serie = serie
		NotaFiscalParametros.cnpj = login.filialLT[filial][9]
		NotaFiscalParametros.uf = uf
		NotaFiscalParametros.versao = versao
		NotaFiscalParametros.gravar_envio_retorno = gravar
		NotaFiscalParametros.relacao_xmls_utilizados = []
		NotaFiscalParametros.csc_id = id_csc
		NotaFiscalParametros.csc_numero = numero_csc
		NotaFiscalParametros.pasta_arquivo_nfe_xsd_versao = diretorios.xsd+'nfe_v4.00.xsd'
		NotaFiscalParametros.retorno_validacao_xsd = ''
		NotaFiscalParametros.ntimeout = int(i[15]) if i[15] and int(i[15]) else 30
		NotaFiscalParametros.gravar_original=False
		NotaFiscalParametros.serie_mdfe=str(login.filialLT[filial][43]) if len(login.filialLT[filial])>=44 else "1"
		NotaFiscalParametros.contingencia_enviar = False
		NotaFiscalParametros.emissao_contingencia = False
		NotaFiscalParametros.xml_assinado_contingencia = str()

		if not os.path.exists(certificado) or not i[6]:
    		
			definir = u'\n\n[ Não foi definido um certificado para a filial selecionada }\n' if not i[6] else '\n'
			alertas.dia( parent, u'{ Certificado não localizado [ ' + certificado.split('/')[len(certificado.split('/') )-1]+' ] }'+definir+(' '*140),'Nota fiscal')
			retorno = False

		if not os.path.exists(diretorios.xsd+'nfe_v4.00.xsd'):

			alertas.dia( parent, u'{ Arquivo de schema não localizado }\n\n' + diretorios.xsd.upper()+'nfe_v4.00.xsd'.upper() + '\n'+(' '*180),u'Emissão da nota fiscal')
			retorno = False

		return retorno,  uf, ambiente, serie_nfe, serie_nfce, regime, cnpj

	def retornosSefaz(self, xml, evento, parent, nome_evento='', modelo=None, contingencia=False ):

		s = True
		r = ''
		i = ''
		chave = ''
		csTaT = ''
		protocolo = ''
		data_recebimento = ''
		try:
			
		    d = minidom.parseString( xml.encode('UTF-8') )
		    r = {}
		    c = ''
		    lan = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
		    for even in evento:
				    
			    if even in xml:

				    r[u'consultaCadastro'] = self.leituraXml( d, even, "soap:Text" )[0][0]
				    r[u'Codigo de retorno'] = self.leituraXml( d, even, "cStat" )[0][0]
				    r[u'Descrição do motivo'] = self.leituraXml( d, even, "xMotivo" )[0][0]
				    r[u'Ambiente'] = self.leituraXml( d, even, "tpAmb" )[0][0]
				    try:
					    r[u'Versão da NFes/MDFe'] = self.leituraXml( d, even, "versao" )[1]
				    except Exception as erros:
					    r[u'Versão da NFes'] = ''
						    
				    r[u'Data e hora do recebimento'] = self.leituraXml( d, even, "dhRecbto" )[0][0]
				    r[u'Numero da chave da nfe'] = self.leituraXml( d, even, "chNFe" )[0][0]
				    r[u'Numero da chave da mdfe'] = self.leituraXml( d, even, "chMDFe" )[0][0]
				    r[u'Protocolo de autorização'] = self.leituraXml( d, even, "nProt" )[0][0]
				    r[u'Modelo da NFe'] = self.leituraXml( d, even, "mod" )[0][0]

				    if modelo=='58':	chave = r[u'Numero da chave da mdfe']
				    else:	chave = r[u'Numero da chave da nfe']
				    csTaT = r[u'Codigo de retorno']
				    protocolo = r[u'Protocolo de autorização']
				    data_recebimento = r[u'Data e hora do recebimento']
					    
				    i +='\n{ Evento: '+even+' '+lan+' [ '+nome_evento+' ] }\n'
				    for ii in r:

					    if r[ii]:	i += ii +': '+r[ii]+'\n'
				    c = i
		    if contingencia and c:
			i +='\nNota Fiscal emitita em contingencia\nPS:Assim que o servico da sefaz retornar enviar a contingencia\n\n'+\
			    'emissao offline, com transmissao do arquivo para a SEFAZ ate o primeiro dia util\n'+\
			    'subsequente, contado da data de emissao do documento em contingencia'
		    
		except Exception as erro:
			
			s = False
			if type( erro ) !=unicode: erro = str( erro )
			alertas.dia( parent, u"[ Leitura do XML de retorno ]\n\n{ Retorno do Erro }\n"+ erro +"\n"+(" "*160),u"Pegando informações do XML de retorno" )
			
		return s, i, r, chave, csTaT, protocolo, data_recebimento

#---{ Dados-Certificados Retornos SEFAZ }--------------------------// Leitura XML	
	def leituraXml( self, doc, pai, filho):
		
		valores = []
		aTribuT = ''

		campos  = doc.getElementsByTagName(pai)
		if campos != []:

			for node in campos:

				""" Pegar Atributos ex: ID da NFE """
				aTribuT = node.getAttribute(filho)
				
				flista=node.getElementsByTagName(filho)

				if flista != []:	#-:[ Campo filho existir ]
							
					for fl in flista:
						
						if fl.firstChild != None:
							
							dados = fl.firstChild.nodeValue
							valores.append(dados)

						else:	valores.append('')

				else:	valores.append('')
							
		return valores,aTribuT

#---{ Dados-Certificados Retornos SEFAZ }--------------------------// Visualizar retornos
	def mostrarInformacoesRetorno(self, parent, informacoes, retornos, modulos, modelo, cStat, xml, filial, filexml, email, html, termica, contingencia ):

		if html:

			negado = '<h3>Verifique o seu certificado!!</h3>' if 'denied' in html else ''

			hsu_frame=LerHtml(parent=parent,id=-1, inf = html+negado )
			hsu_frame.Centre()
			hsu_frame.Show()
	
		else:

			vsu_frame=VisualizarRetornos(parent=parent,id=-1, inf = informacoes, rt = retornos, md = modulos, modelo = modelo, csTaT = cStat, string_xml = xml, filial = filial, file_xml = filexml, emails = email, termica=termica, contingencia=contingencia )
			vsu_frame.Centre()
			vsu_frame.Show()

	def remover_acentos(self,txt):

		return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

	def gravarRetorno(self, modelo, serie, nota, ambiente, filial):

		diretorio_gravacao = diretorios.usFolder+'nfe400/' if modelo == '55' else diretorios.nfceacb+'nfce400/'

		__f = filial.lower()
		__n = datetime.datetime.now().strftime("%m-%Y") +'/'+ str( serie ).zfill(3)+'-'+str( nota ).zfill(9)+'/'
		__d = diretorio_gravacao+ __f +"/homologacao/"+ __n if ambiente == '2' else diretorio_gravacao + __f +"/producao/"+ __n
		if os.path.exists( __d ) == False:	os.makedirs( __d )

		NotaFiscalParametros.gravar_envio_retorno_pasta = __d

		return __d

	def salvarNotaFiscal( self, emissao = 1, gravacao = 1, dados = '', filial = '', chave='', par=None):
    
		data_emissao = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
		hora_emissao = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
		data_hora_retorno = datetime.datetime.now().strftime("%d-%m-%Y %T")

		conn = sqldb()
		sql  = conn.dbc("NFE: Gerenciador de nota fiscal", fil = filial, janela = "" )
		erro=''
		if sql[0]:
			
			try:
			    
			    if gravacao == 1: #--// Gravacao inicial atualiza { cadastro de davs-vendas/devolucao e inserir no controle de nfs os dados do DAV e NF }

				if emissao!=3:
				    achar="SELECT cr_nota FROM cdavs WHERE cr_nota='"+str( dados[0] )+"' and cr_tfat='"+str( dados[2] )+"' and cr_tnfs='"+str( dados[3] )+"' and cr_seri='"+dados[8]+"' and cr_ndav='"+str( dados[1] )+"'"
				    if emissao==2:	achar = achar.replace('cdavs','dcdavs')
				elif emissao==3:	achar = "SELECT cc_numenf FROM ccmp WHERE cc_numenf='"+str( dados[0] )+"' and cc_contro='"+str( dados[1] )+"'"

				"""  DADOS 
				     [0]>-->Numero da Nota
				     [1]>-->Numero do pedido/dav/Numero de controle
				     [2]>-->1-Venda,2-Devolucao de Vendas
				     [3]>-->Tipo { 1 - NFe, 2 - NFCe }
				     [4]>-->TiloLancamento { 1 - Emissao, 2 - ParaInutilizar, 3 - Cancelamento, 4 - Inutilizadas, 5 - Denegada }
				     [5]>-->Orgime { 1 - Vendas, 2 - Compras }
				     [6]>-->Ambiente { 1 - Producao, 2 - Homologacao }
				     [7]>-->Filial ID-Filial
				     [8]>-->Numero serie da nfe
				     [9]>-->Valor total da nota
				     [10]>->Dados do cliente { codigo, cnpj-cpf, fantasia, nome-descricao }
				"""
				if sql[2].execute(achar):	pass #--// Localizado no gerenciador de notas
				else:
				    if emissao != 3:	gravar_dav = "UPDATE cdavs SET cr_nota='"+str( dados[0] )+"',cr_tfat='"+str( dados[2] )+"', cr_tnfs='"+str( dados[3] )+"', cr_seri='"+dados[8]+"' WHERE cr_ndav='"+str( dados[1] )+"'"
				    if emissao == 3:	gravar_dav = "UPDATE ccmp  SET cc_numenf='"+str( dados[0] )+"' WHERE cc_contro='"+str( dados[1] )+"'"
				    if emissao == 2:	gravar_dav = gravar_dav.replace('cdavs','dcdavs')

				    emissao_nfe = str( emissao ) #--/ 1-venda 2-devolucao venda 3-pedido rma
				    if dados[2] == '1':	emissao_nfe = '6' #-// Emissao p/Simples Faturamento - Entrega Futura
				    if dados[2] == '2':	emissao_nfe = '7' #-// Entrega Futura de Simples Faturamento
				    if emissao == 3:	emissao_nfe = '4' #-// Devolucao de compra-RMA
				    if emissao == 4:	emissao_nfe = '8' #-// Nota fiscal complementar

				    gerente = "INSERT INTO nfes (nf_nfesce,nf_tipnfe,nf_tipola,nf_envdat,nf_envhor,\
							    nf_envusa,nf_numdav,nf_oridav,nf_ambien,nf_idfili,nf_nnotaf,\
							    nf_codigc,nf_cpfcnp,nf_fantas,nf_clforn,nf_nserie,nf_vlnota)\
							    VALUES(%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s)"

				    codigo_cliente= cpf_cnpj= fantasia= nome=''
				    if dados[10]:	codigo_cliente, cpf_cnpj, fantasia, nome = dados[10]
						
				    sql[2].execute( gravar_dav )
				    sql[2].execute( gerente, ( dados[3], emissao_nfe, dados[4], data_emissao, hora_emissao, login.usalogin, dados[1], dados[5], dados[6], dados[7], dados[0], codigo_cliente, cpf_cnpj, fantasia, nome, dados[8], dados[9] ) )

				    sql[1].commit()

			    elif gravacao == 2: #--// Gravacao da nota emitida

				    """  DADOS
					     self.p.numero_dav, protocolo, data_recebimento, chave, numero_nf, nfe_nfce, nfe_origem, csTaT, nfe_emissao, __d
					     [0]>-->Numero do dav
					     [1]>-->Protocolo
					     [2]>-->Data do recebimento
					     [3]>-->Numero da chave nfe
					     [4]>-->Numero da NF
					     [5]>-->Tipo { 1-NFe, 2-NFCe }
					     [6]>-->Origem { 1-Vendas "POS","" 2-Comrpas "RMA"}
					     [7]>-->Retorno SEFAZ { csTat }
					     [8]>-->Emissao { TipoLancamento: 1 - Emissao, 2 - ParaInutilizar, 3 - Cancelamento, 4 - Inutilizadas, 5 - Denegada }
					     [9]>-->Pasta onde gravou o XML
					     [10]>->Arquivo XML
					     [11]>->Historico retorno SEFAZ
					     [12]>->Numero da serie
				    """
				    
				    lan = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
				    emi = dados[2].split('T')[0]+' '+dados[2].split('T')[1][:8]+' '+dados[1]+' '+login.usalogin

				    """  Pesquisa retornos anteriores da SEFAZ  """
				    achar = "SELECT nf_rsefaz FROM nfes WHERE nf_nnotaf='"+ dados[4] +"' and nf_nfesce='"+ dados[5] +"' and nf_oridav='"+ dados[6] +"' and nf_idfili='"+ filial +"' and nf_nserie='"+ dados[12] +"'"
				    __ret = sql[2].execute( achar )
				    __rsa = sql[2].fetchone()[0] if __ret else ()

				    retorno_sefaz_anterior = __rsa.decode('UTF-8') if __rsa else ''

				    #--------: Atualiza davs
				    if dados[8]=='5': #--// [ Nota fiscal denegada ]
					
					if emissao != 3:	atualiza_dav = "UPDATE cdavs SET cr_nota='',cr_chnf='',cr_nfem='',cr_csta='' WHERE cr_ndav='"+dados[0]+"'"
					if emissao == 3:	atualiza_dav = "UPDATE ccmp  SET cc_numenf='',cc_ndanfe='',cc_protoc='',cc_nfemis='',cc_nfdsai='',cc_nfhesa='' WHERE cc_contro='"+dados[0]+"'"
					if emissao == 2:	atualiza_dav = atualiza_dav.replace('cdavs','dcdavs')
					hitorico_retornos = u'SEFAZ Retorno: '+ dados[11] +'\n\n'+ retorno_sefaz_anterior
					if emissao == 3:	hitorico_retornos = u'SEFAZ Retorno: '+ data_hora_retorno +'\n'+ dados[11] +'\n\n'+ retorno_sefaz_anterior
					
				    else:
					
					if emissao != 3:	atualiza_dav = "UPDATE cdavs SET cr_nota='"+dados[4]+"',cr_chnf='"+dados[3]+"',cr_nfem='"+str(emi)+"',cr_csta='"+dados[7]+"' WHERE cr_ndav='"+dados[0]+"'"
					if emissao == 3:	atualiza_dav = "UPDATE ccmp  SET cc_numenf='"+dados[4]+"',cc_ndanfe='"+dados[3]+"',cc_protoc='"+str(emi)+"',cc_nfemis='"+str(dados[2].split('T')[0] )+"',cc_nfdsai='"+str(dados[2].split('T')[0])+"',cc_nfhesa='"+str(dados[2].split('T')[1][:8])+"' WHERE cc_contro='"+dados[0]+"'"
					if emissao == 2:	atualiza_dav = atualiza_dav.replace('cdavs','dcdavs')
					hitorico_retornos = u'SEFAZ Retorno: '+ dados[11] +'\n\n'+ retorno_sefaz_anterior
					if emissao == 3:	hitorico_retornos = u'SEFAZ Retorno: '+ data_hora_retorno +'\n'+ dados[11] +'\n\n'+ retorno_sefaz_anterior
				    
				    #-// Atualiza no gerenciador de notas
				    atualiza_gerenciador = "UPDATE nfes SET nf_tipola='"+ dados[8] +"',nf_retorn='"+ data_hora_retorno +"',nf_rsefaz='"+ hitorico_retornos.replace("'",'') +"',\
				    nf_rethor='"+ hora_emissao +"',nf_protoc='"+ dados[1] +"',nf_nchave='"+ dados[3] +"',nf_ncstat='"+ dados[7] +"',nf_nconti='' \
				    WHERE nf_nnotaf='"+ str(int(dados[4])) +"' and nf_nfesce='"+ dados[5] +"' and nf_oridav='"+ dados[6] +"' and nf_idfili='"+ filial +"' and nf_nserie='"+ str(int(dados[12])) +"'"

				    #-// Inclui o arquivo xml
				    incluir_xml = "INSERT INTO sefazxml (sf_numdav,sf_notnaf,sf_arqxml,sf_nchave,sf_tiponf,sf_filial)\
				    VALUES(%s,%s,%s,%s,%s,%s)"

				    #-// Incluir ocorrencia
				    grava_ocorren = "INSERT INTO ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde) VALUES (%s,%s,%s,%s,%s)"

				    #-// Atualiza no contas areceber
				    receber = "UPDATE receber SET rc_notafi='"+ dados[4] +"' WHERE rc_ndocum='"+ dados[0]+"'"

				    sql[2].execute( atualiza_dav )
				    sql[2].execute( atualiza_gerenciador )
				    sql[2].execute( incluir_xml, ( dados[0], dados[4], dados[10], dados[3], dados[5], filial ) )

				    if emissao == 3:	sql[2].execute( grava_ocorren, ( dados[0], lan, u"RMA-Emissão", 'NFE', filial ) )
				    else:	sql[2].execute( grava_ocorren, ( dados[0], lan, u"Emissão", 'NFE', filial ) )
				    
				    if emissao != 3 and dados[8]!='5':	sql[2].execute( receber ) #--// So grava no contas areceber se nao for denegada
				    sql[1].commit()
			    
			    elif gravacao == 3: #-// Rejeicao

				    """  DADOS	 [0]>-->Numero da NF, [1]>-->Numero Serie, [2]>-->Origem, [3]>-->Nfe ou NFCe, [4]>-->Retorno SEFAZ	"""
			    elif gravacao == 4: #--// Cartao de correncao

				    danf = dados[0]
				    dTar = dados[1]
				    xmlc = dados[2] + '[MOT]' + dados[5]
				    hist = dados[3]
				    xman = dados[4].decode('UTF-8')

				    ger = "SELECT nf_rsefaz FROM nfes WHERE nf_nchave='"+str( danf )+"'"
				    res = ""
				    if sql[2].execute(ger) !=0:	res = sql[2].fetchall()[0][0]
				    if res == None:	res = ""
				    
				    if type( res ) == str:	res = res.decode("UTF-8")
				    if type( hist ) == str:	hist = hist.decode("UTF-8")
				    if type( xmlc ) == str:	xmlc = xmlc.decode("UTF-8")

				    res += hist
				    if xman !='':	xmlc = xmlc + "-|-" + xman
				    
				    cce = "UPDATE sefazxml SET sf_pdfarq='"+ xmlc +"' WHERE sf_nchave='"+str( danf )+"'"
				    uge = "UPDATE nfes SET nf_rsefaz='"+ hist +"',nf_retcce='"+str( dTar )+"' WHERE nf_nchave='"+str( danf )+"'"

				    sql[2].execute(cce)
				    sql[2].execute(uge)
				    sql[1].commit()

			    elif gravacao==5: #--// Gravacao da pasta onde foi gravado o xml original para recuperacao 204,359

				pasta_arquivo=NotaFiscalParametros.gravar_envio_retorno_pasta+'/original_'+chave+'.xml'
				grv="UPDATE nfes SET nf_urlqrc='"+ pasta_arquivo +"' WHERE nf_nnotaf='"+ str(int(dados[0])) +"' and nf_nfesce='"+ dados[3] +"' and nf_oridav='"+ dados[5] +"' and nf_idfili='"+ dados[7] +"' and nf_nserie='"+ str(int(dados[8])) +"'"
				
				sql[2].execute( grv )
				sql[1].commit()
			except Exception as erro:
			    sql[1].rollback()
			    
			conn.cls( sql[1] )

		if erro:	alertas.dia(par,u'{ Erro na gravacao da NF }\n\n'+str(erro)+u'\n','Gravando retorno da NF')

	def gravarContingencia(self,dados, xml):

	    fl, chave, d, nf, protocolo, nd, sr = dados

	    try:
		conn = sqldb()
		sql  = conn.dbc("NFE: Gerenciador de nota fiscal/CONTINGENCIA", fil = fl, janela = "" )
		erro=''
		if sql[0]:
		
		    data, hora = d.split('T')[0], d.split('T')[1].split('-')[0]
		    datahorare = data+' '+hora
		    datahoraus = data+' '+hora+' '+login.usalogin

		    status = ''
		    tpEmis = '1'
		    #--// Utualizar dav
		    sql[2].execute("UPDATE cdavs SET cr_nota='" + nf + "',cr_chnf='" + chave + "',cr_nfem='" + datahoraus + "',cr_csta='100' WHERE cr_ndav='" + nd + "'")

		    #--// Atualiza no gerenciador de notas
		    sql[2].execute("UPDATE nfes SET nf_tipola='1',nf_retorn='" + datahorare + "',nf_rethor='" + hora + "',nf_protoc='" + protocolo + "',nf_nchave='" + chave + "',\
		    nf_ncstat='',nf_nconti='1' WHERE nf_nnotaf='" + str(int(nf)) + "' and nf_nfesce='2' and nf_oridav='1' and nf_idfili='" + fl + "' and nf_nserie='" + str(int(sr)) + "'")

		    # -// Inclui o arquivo xml
		    inc = "INSERT INTO sefazxml (sf_numdav,sf_notnaf,sf_arqxml,sf_nchave,sf_tiponf,sf_filial)\
		    VALUES(%s,%s,%s,%s,%s,%s)"
		    sql[2].execute( inc, (nd,nf,xml,chave,'2',fl))

		    # -// Atualiza no contas areceber
		    sql[2].execute("UPDATE receber SET rc_notafi='" + nf + "' WHERE rc_ndocum='" + nd + "'")

		    # --// Atualiza com o xml assinado para recuperacao depois q pegar a autorizacao do sefaz
		    if NotaFiscalParametros.xml_assinado_contingencia:
			sql[2].execute("UPDATE nfeoriginal SET no_asxml='"+ NotaFiscalParametros.xml_assinado_contingencia+"' WHERE no_chave='" + chave + "'")

		    sql[1].commit()

		    conn.cls(sql[1],sql[2])
		    return True,''

	    except:
		return False, sys.exc_info()[1]
	    
class VisualizarRetornos(wx.Frame):

#---{ Visualizacao de Retorno do SEFAZ }--------------------------// Construtor
	def __init__(self, parent, id, inf, rt, md, modelo, csTaT, string_xml, filial, file_xml, emails, termica, contingencia=False ):

		""" MD - Modulo
			1-Eventos status, inutilizacao, cancelamento
			2-Emissao
			3-Erro na emissao
		"""
		self.p = parent
		self.s = csTaT
		self.x = string_xml
		self.f = filial
		self.t = termica

		self.xml_file = file_xml
		self.emails   = emails
		self.mod = modelo

		tipo_nota = "65 - NFCe" if modelo == "65" else "55 - NFe"
		if modelo=='58':	tipo_nota='58 - MDFe'

		wx.Frame.__init__(self,parent,id, "Retorno da SEFAZ { "+tipo_nota+" NF-4.0 Filial: "+self.f+" }",size=(900,500),style=wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX|wx.CAPTION)
		self.painel = wx.Panel(self,wx.NewId(),style=wx.SUNKEN_BORDER)

		self.Bind(wx.EVT_CLOSE, self.sair)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,u"Relação de xml [composição dos arquivos de envio e retorno da sefaz]",pos=(41,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL))
		
		if self.mod=='58' and NotaFiscalParametros.relacao_xmls_utilizados:	self.xml_file=NotaFiscalParametros.pasta_gravaca_xml_final=NotaFiscalParametros.relacao_xmls_utilizados[0]
		
		self.xmls_utilizados = wx.ComboBox(self.painel, 700, value=NotaFiscalParametros.pasta_gravaca_xml_final, pos=(39, 14), size = (856,30), choices = NotaFiscalParametros.relacao_xmls_utilizados, style=wx.NO_BORDER|wx.CB_READONLY)

		self.saida_infomacoes = wx.TextCtrl(self.painel, value='', pos=(40,46), size=(855,346),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.saida_infomacoes.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.enviar_email_automatico = wx.TextCtrl(self.painel, value='', pos=(0,400), size=(895,90),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.enviar_email_automatico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.enviar_email_automatico.SetBackgroundColour("#B9C4CF")
		self.enviar_email_automatico.SetForegroundColour('#002B56' if emails else '#B99292')
		self.enviar_email_automatico.SetValue(u'Envio automático de email' if emails else u'Envio automático de email\nCliente sem email cadastrado')

		self.saida_infomacoes.SetBackgroundColour("#4D4D4D")
		self.saida_infomacoes.SetForegroundColour('#90EE90')
		self.saida_infomacoes.SetValue( "{ Retorno da SEFAZ [ "+ tipo_nota+" ] }\n"+ inf )

		self.impressao=wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/printing20.png",   wx.BITMAP_TYPE_ANY), pos=(2,2), size=(34,34))				
		self.visualizar_xml=wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/xml224.png",   wx.BITMAP_TYPE_ANY), pos=(2,42), size=(34,34))				
		self.sair_visualizador = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/sair24.png",   wx.BITMAP_TYPE_ANY), pos=(2,110), size=(34,38))				
   		self.impressao_nfce = wx.BitmapButton(self.painel, 702, wx.Bitmap("imagens/cupomi.png",   wx.BITMAP_TYPE_ANY), pos=(2,152), size=(34,38))
   		self.impressao_a4 = wx.BitmapButton(self.painel, 701, wx.Bitmap("imagens/qrcode16.png",   wx.BITMAP_TYPE_ANY), pos=(2,192), size=(34,38))
		self.impressao_nfce.Enable(True if modelo == '65' and csTaT == '100' and termica and termica[0] and termica[1] and termica[2] else False)
		self.impressao_a4.Enable(True if modelo == '65' and csTaT == '100' and termica and termica[0] and termica[1] and termica[2] else False)
		if contingencia:

		    self.impressao_nfce.Enable(True if modelo == '65' and termica and termica[0] and termica[1] and termica[2] else False)
		    self.impressao_a4.Enable(True if modelo == '65' and termica and termica[0] and termica[1] and termica[2] else False)
		    self.s = '100'

		if csTaT in ['100','107','102','135','573']:

			self.saida_infomacoes.SetBackgroundColour("#1D5083")
			self.saida_infomacoes.SetForegroundColour('#FFFFFF')
			self.saida_infomacoes.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD))

		if md == 3: #--// Erro na emissao

			self.saida_infomacoes.SetBackgroundColour("#B76666")
			self.saida_infomacoes.SetForegroundColour('#FFFFFF')
			erro = '\n\n[ Tipo do erro { Validacao interna no XML } ]\n'+NotaFiscalParametros.retorno_validacao_xsd if NotaFiscalParametros.retorno_validacao_xsd else ''
			self.saida_infomacoes.SetValue( "{ Retorno da SEFAZ [ "+ tipo_nota+" ] }\n"+ inf + erro)

		libera_icones = True if md in [2] else False
		if not self.x:	libera_icones = False
		self.impressao.Enable( libera_icones )
		self.impressao.Enable(False if modelo == '65' else True)

		self.visualizar_xml.Enable( libera_icones )
		
		"""  Se existir XML Habilita para visualizar  """
		if string_xml:	self.visualizar_xml.Enable( True )

		"""  Envio automatico de emails  """
		sr, us, re, ps, pr = login.filialLT[self.f][29].split(';')
		if   len( login.filialLT[ self.f ][35].split(";") ) >= 100 and login.filialLT[ self.f ][35].split(";")[99] == 'T':	self.enviar_email_automatico.SetValue(u'Envio automático de email\nFilial configurada para nao enviar email automaticamente...')
		elif not emails:	self.enviar_email_automatico.SetValue(u'Envio automático de email\nCliente sem email cadastrado para envio automatico...')
		else:
			
			if modelo == '65' and len( login.filialLT[self.f][35].split(';') ) >= 130 and login.filialLT[self.f][35].split(';')[129] == 'T':	us = '' #--//Nao enviar email automatico
			if sr and us and re and ps and pr and self.s in ['100']:

				tx = u"Nota Fiscal Eletrônica (Nf-e) Emitida\n\nPrezado Cliente,\n\nVocê está recebendo o arquivo eletrônico (XML) da Nota Fiscal Eletrônica"
				tx+= u"\n\n- Você pode verificar a autenticidade desta nota fiscal acessando o endereço www.nfe.fazenda.gov.br (ou o site da Nf-e da Secretaria da Fazenda do Estado do Emitente) e informando o Nº da chave"
				tx+= u"\n- Consulte o seu contador sobre a necessidade e instruções de como, onde e por quanto tempo armazenar o arquivo eletrônico (XML) e a Danfe impressa\n\n"
				
				for rs in rt:

					if rt[rs]:	tx +=rs+u': '+rt[ rs ] +'\n'
				
				to = emails[0].strip()
				sb = u"Nota Fiscal Eletrônica (Nf-e) Emitida"
				at = u'Financeiro/Compras'

				montar_danfe.xmlFilial = self.f
				montar_danfe.codModulo = "504"
				arquivos_gerados = montar_danfe.MontarDanfe( self, arquivo = file_xml, TexTo = string_xml, emails = emails, Filial = self.f, automatico = True )
				
				arquivos_envios = arquivos_gerados, file_xml
				if "@" in to:
					
					self.TIPORL = "NFE" #-: Variavel declara no envio do emails
					retorno_envio, error = enviar_email.enviaremial( to, sb, tx, arquivos_envios, "", self.painel, self, Filial = self.f )
					if not retorno_envio:
						self.enviar_email_automatico.SetValue(u'Envio automático de email\nFaltando dados do servidor para o envio\n'+ error.decode('utf-8') )
						self.enviar_email_automatico.SetBackgroundColour("#E8C0C0")
						self.enviar_email_automatico.SetForegroundColour('#C12020')
						
					else:
						self.enviar_email_automatico.SetValue(u'Envio automático de email\n\nArquivos XML, PDF enviados com sucesso para '+ to +'...')
						self.enviar_email_automatico.SetBackgroundColour("#0E4B89")
						self.enviar_email_automatico.SetForegroundColour('#E7F4FF')
				
				else:			
					self.enviar_email_automatico.SetValue(u'Envio automático de email\n\nEmail do usuario incompativel...')
					self.enviar_email_automatico.SetBackgroundColour("#E8C0C0")
					self.enviar_email_automatico.SetForegroundColour('#C12020')

			else:	self.enviar_email_automatico.SetValue(u'Envio automático de email\nFaltando dados do servidor para o envio...')

		self.sair_visualizador.Bind(wx.EVT_BUTTON, self.sair)
		self.impressao.Bind(wx.EVT_BUTTON, self.gerarDanfe)
		self.visualizar_xml.Bind(wx.EVT_BUTTON, self.leituraVisualizarXml)
		self.impressao_nfce.Bind(wx.EVT_BUTTON, self.imprimirTermica)
		self.impressao_a4.Bind(wx.EVT_BUTTON, self.imprimirTermica)
		self.xmls_utilizados.Bind(wx.EVT_COMBOBOX, self.renovarXml)

		""" Enviar para o gerenciador quando for impressora diferente da TERMICA Quando impressao automatica  """
		if modelo == '65' and csTaT == '100' and termica and termica[0] and termica[1] and termica[2] and termica[1]['printer'] and not termica[1]['printer'][8] and termica[1]['auto']:	self.imprimirTermicaImpressao(701)
		
	def imprimirTermica(self,event):	self.imprimirTermicaImpressao(event.GetId())
	def imprimirTermicaImpressao(self,__id):
		
		iit = self.t[1]
		prn = iit['printer'][0] if iit['printer'] else None

		xml = self.t[0].printar(parent=self.p, dav=iit['dav'], chave=self.t[2].strip(), filial=self.f)
		if xml:
		    """ Impressora Epson TMT20 """
		    if nF.listaprn(1)[3][iit['printer'][0]][7].split('-')[0] == "10":
			Nfs400.epson_nfce.nfce(self, filial=self.f, printar=prn, xml=xml, inform = iit,emissao=__id, numero_dav=iit['dav'],segunda=False, autorizador='')
		    else:
			Nfs400.emitir_nfce.nfce(self, filial=self.f, printar=prn, xml=xml, inform = iit,emissao=__id, numero_dav=iit['dav'],segunda=False, autorizador='')

		self.impressao_nfce.Enable(False)
		self.impressao_a4.Enable(False)

#---{ Visualizacao de Retorno do SEFAZ }--------------------------// Sair
	def sair(self,event):
		
		if self.mod!='58' and self.s in ['100']:	self.p.sair(wx.EVT_BUTTON)
		else:	self.Destroy()

#---{ Leitura manual do xml }--------------------------//
	def renovarXml(self,event):

		if self.xmls_utilizados.GetValue().strip():
    			
			arquivo = self.xml_file = self.xmls_utilizados.GetValue().strip()
			_xml = minidom.parse(arquivo).toprettyxml()

			self.saida_infomacoes.SetBackgroundColour("#E5E9EE")
			self.saida_infomacoes.SetForegroundColour('#122943')
			self.saida_infomacoes.SetValue( "{ Leitura manual do XML }\n\n"+ _xml )
			self.saida_infomacoes.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

#---{ Visualizacao de Retorno do SEFAZ }--------------------------// Gerar DANFE
	def gerarDanfe(self,event):

	    if self.mod=='58':

		if self.xml_file:	montar_mdfe.gerarPdfMdfe(self.xml_file,self.f,self.p, True)
		else:	alertas.dia(self.p,'Selecione o arquivo que contem o xml para impressao...\n'+(" "*130),"MDFe: Impressao")

	    else:
		montar_danfe.xmlFilial = self.f
		montar_danfe.codModulo = "502"
		montar_danfe.MontarDanfe( self.p, arquivo=self.xml_file, TexTo=self.x, emails = self.emails, automatico = False )

#---{ Visualizacao de Retorno do SEFAZ }--------------------------// Visualizar XML
	def leituraVisualizarXml(self,event):

		_xml = minidom.parseString( self.x )
		_str = _xml.toprettyxml()

		MostrarHistorico.hs = _str
		
		MostrarHistorico.TP = "xml"
		MostrarHistorico.TT = "Leitura e Envio do XML"
		MostrarHistorico.GD = '' if self.mod == '65' else montar_danfe 

		MostrarHistorico.AQ = self.xml_file
		MostrarHistorico.FL = self.f
		
		gerenciador.parente = self
		gerenciador.Filial  = self.f

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#185189") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Emissão da NFe 4.00", 5, 390, 90)
		dc.DrawRotatedText(u"Visualiza retornos SEFAZ", 22, 390, 90)

class LerHtml(wx.Frame):

    def __init__(self, parent, id , inf ):

		wx.Frame.__init__(self,parent,id, "Retorno da SEFAZ { HTML }",size=(900,500),style=wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX|wx.CAPTION)
		self.painel = wx.Panel(self,wx.NewId(),style=wx.SUNKEN_BORDER)

		self.html = html.HtmlWindow(self.painel, -1, size=(900, 500), style=wx.VSCROLL|wx.HSCROLL|wx.TE_READONLY|wx.BORDER_SIMPLE)
		self.html.SetPage( inf )

"""  Instanciamento  """
informes = DadosCertificadoRetornos()
