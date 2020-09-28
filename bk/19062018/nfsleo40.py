#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  nfceleo40.py
#  Inicio: 17-02-2018 19:43 Jose de almeida lobinho
#  Utilizando a lib do leodata
import wx
import datetime
import requests
requests.packages.urllib3.disable_warnings()
from xml.dom import minidom
from decimal import Decimal
import os
from lxml import etree
import wx.html as html
	
from pynfe.processamento.comunicacao import ComunicacaoSefaz
from pynfe.entidades.cliente import Cliente
from pynfe.entidades.emitente import Emitente
from pynfe.entidades.notafiscal import NotaFiscal
from pynfe.entidades.fonte_dados import _fonte_dados
from pynfe.entidades.transportadora import Transportadora
from pynfe.processamento.serializacao import SerializacaoXML, SerializacaoQrcode
from pynfe.processamento.assinatura import AssinaturaA1
from pynfe.utils.flags import CODIGO_BRASIL, CODIGOS_ESTADOS
from pynfe.entidades.evento import EventoCancelarNota, EventoManifestacaoDest, EventoCartaCorrecao

from conectar import login,dialogos,menssagem, numeracao, diretorios, sqldb, MostrarHistorico, gerenciador, emailenviar, truncagem
from prndireta import ConfiguracoesPrinters
from danfepdf  import danfeGerar

alertas = dialogos()
mens = menssagem()

entrega = ConfiguracoesPrinters()
numeros = numeracao()
montar_danfe = danfeGerar()
enviar_email = emailenviar()
Truncar = truncagem()

class StatusEventos:

#---{ Eventos }-------------------------------------------------// Status do sevidor	
	def status( self, parent, dados ):

		rtn, snh, cer, sis, sie, amb, uf, fus, __cnpj, __nfce, regime_tributario = informes.certificados( dados[0], parent )

		if rtn:
				
			_mensagem = mens.showmsg("STATUS: Comunicando com o servidor da SEFAZ\n\nAguarde...")
			try:

				_mensagem = mens.showmsg("STATUS: Comunicando com o servidor da SEFAZ\n\nAguarde...")
				con = ComunicacaoSefaz(uf, cer, snh, amb)
				xml = con.status_servico( dados[2] )
				del _mensagem

				rt = informes.retornosSefaz( xml.text, ["retConsStatServ"], parent, nome_evento = 'STATUS' )
				if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], 1, dados[1], rt[4], '', dados[0], '', '' )
			
			except Exception as erro:
				
				_mensagem = mens.showmsg("STATUS ERROR: Comunicando com o servidor da SEFAZ\n\nAguarde...")
				if type( erro ) !=unicode:	erro = str( erro )
				del _mensagem
				alertas.dia( parent, u"[ Enviando requisição de status a sefaz {  filial "+ dados[0] +" NFCe 4.0 } ]\n\n[ ERROR ]: "+ erro +"\n"+(" "*180),u"Status do servidor da sefaz" )

#---{ Eventos }-------------------------------------------------// Inutilizacao da NF	
	def inutilizarNfe(self, parent, filial, ambiente, nota_fiscal, motivo, nfe_nfce, dav, id_lancamento, tipo_pedido, serie ):

		rtn, snh, cer, sis, sie, amb, uf, fus, __cnpj, __nfce, regime_tributario = informes.certificados( filial, parent )

		amb = True if ambiente == '2' else False
		mod = 'nfe' if nfe_nfce == '1' else 'nfce'
		modelo_nfe = '55' if mod == 'nfe' else '65'
		
		amb = True if ambiente == '2' else False
		
		modulo = 1
		con = ComunicacaoSefaz(uf, cer, snh, amb)
		envio = con.inutilizacao(
			modelo = mod,                                # nfe ou nfce
			cnpj = __cnpj,                       # cnpj do emitente
			numero_inicial = int( nota_fiscal ),                            # Número da NF-e inicial a ser inutilizada
			numero_final = int( nota_fiscal ),                              # Número da NF-e final a ser inutilizada
			serie = serie, 
			justificativa=motivo)    # Informar a justificativa do pedido de inutilização (min 15 max 255)

		rt = informes.retornosSefaz( envio.text, ["retInutNFe"], parent, nome_evento = 'INUTILIZACAO' )
		retorno = rt[1]+ '\n'

		diretorio_gravacao = diretorios.usFolder+'nfe400/' if mod == 'nfe' else diretorios.nfceacb+'nfce400/'
		__f = filial.lower()
		__n = datetime.datetime.now().strftime("%m-%Y") +'/'+ str( serie ).zfill(3)+'-'+nota_fiscal.zfill(9)
		__d = diretorio_gravacao + __f +"/homologacao/"+ __n if amb else diretorio_gravacao + __f +"/producao/"+ __n
		if os.path.exists( __d ) == False:	os.makedirs( __d )

		string_xml = ''
		if rt[4] != '102':	modulo = 3
		if rt[4] in ['102','563']:

			retorno = rt[1]+"{ Nota fiscal inutilizada usando dados da SEFAZ }\n\n" if rt[4] == '563' else rt[1]+'\n'
			parent.NFEinuTiliza( rT = ( rt[5], rt[6], retorno, motivo, dav, id_lancamento, tipo_pedido, filial, envio.text ) )

			string_xml = envio.text
			__arquivo = open( __d  +'/inutilizacao_autorizado.xml', "w" )
			__arquivo.write( envio.text )
			__arquivo.close()
			
		if rt[0]:
			
			_arquivo = open( __d + "/inutilizacao_nao_autorizado.xml", "w" )
			_arquivo.write( envio.text )
			_arquivo.close()

			informes.mostrarInformacoesRetorno( parent, retorno, rt[2], modulo, modelo_nfe, rt[4], string_xml, filial, '', '' )
		
#---{ Eventos }-------------------------------------------------// Cancelamento da NF
	def cancelamentoNfe(self, parent, filial='', xml='', motivo='', origem = '' ):

		rtn, snh, cer, sis, sie, amb, uf, fus, __cnpj, __nfce, regime_tributario = informes.certificados( filial, parent )

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
		""" ------------------------------------------------------FIM """

		amb = True if ambiente == '2' else False
		mod = 'nfe' if modelo == '55' else 'nfce'
		tipo_nf = '1' if modelo == '55' else '2'

		diretorio_gravacao = diretorios.usFolder+'nfe400/' if mod == 'nfe' else diretorios.nfceacb+'nfce400/'
		
		__f = filial.lower()
		__n = datetime.datetime.now().strftime("%m-%Y") +'/'+ str( numero_serie ).zfill(3)+'-'+numero_nf.zfill(9)
		__d = diretorio_gravacao+ __f +"/homologacao/"+ __n if amb else diretorio_gravacao + __f +"/producao/"+ __n
		if os.path.exists( __d ) == False:	os.makedirs( __d )

		cancelar = EventoCancelarNota(
			cnpj=__cnpj,                                # cnpj do emissor
			chave=chave, # chave de acesso da nota
			data_emissao=datetime.datetime.now(),
			uf=uf,
			protocolo=protocolo,                                      # número do protocolo da nota
			justificativa='Venda cancelada a pedido do cliente'
			)

		serializador = SerializacaoXML(_fonte_dados, homologacao=amb)
		nfe_cancel = serializador.serializar_evento(cancelar)

		a1 = AssinaturaA1( cer, snh)
		xml = a1.assinar(nfe_cancel)

		con = ComunicacaoSefaz(uf, cer, snh, amb)
		envio = con.evento(modelo=mod, evento=xml)               # modelo='nfce' ou 'nfe'

		rt = informes.retornosSefaz( envio.text, ["retEnvEvento","infEvento"], parent, nome_evento = 'CANCELAMENTO' )
		modulo = 1
		string_xml = ''
		if rt[0] and rt[4] in ['135','573']:
			
			parent.cannfe( rt[4], rt[3], rt[5], motivo, filial, envio.text )

			dados = numero_nf, numero_serie, origem, tipo_nf, rt[1]
			gravar_retorno = EmissaoNotasFiscais()	
			gravar_retorno.salvarNotaFiscal( emissao = 1, gravacao = 3, dados = dados, filial = filial )

			string_xml = envio.text
			__arquivo = open( __d  +'/cancelamento_autorizado.xml', "w" )
			__arquivo.write( envio.text )
			__arquivo.close()

		else:

			modulo = 3
			if rt[0]:	

				dados = numero_nf, numero_serie, origem, tipo_nf, rt[1]
				
				gravar_retorno = EmissaoNotasFiscais()	
				gravar_retorno.salvarNotaFiscal( emissao = 1, gravacao = 3, dados = dados, filial = filial )

				_arquivo = open( __d + "/cancelamento_nao_autorizado.xml", "w" )
				_arquivo.write( envio.text )
				_arquivo.close()

		if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulo, mod, rt[4], string_xml, filial, '', '' )

	def downloadNfe(self, parent, filial, chave ):

		rtn, snh, cer, sis, sie, amb, uf, fus, __cnpj, __nfce, regime_tributario = informes.certificados( filial, parent )
		
		mod = 'nfe'
		modelo = 1
		
		con = ComunicacaoSefaz( uf, cer, snh, amb)
		xml = con.download( __cnpj, chave )

		if '<!DOCTYPE html>' in xml.text:

			hsu_frame=LerHtml(parent=parent,id=-1, inf = xml.text )
			hsu_frame.Centre()
			hsu_frame.Show()

		else:

			rt = informes.retornosSefaz( xml.text.encode('utf-8'), ["retEnvEvento","infEvento"], parent, nome_evento = 'MANIFESTO' )
			#if rt[0] and rt[4] !='135':	modulo = 3
			if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulo, mod, rt[4], '', filial, '', '' )

	def manifestoNfe(self, parent, filial, chave ):

		rtn, snh, cer, sis, sie, amb, uf, fus, __cnpj, __nfce, regime_tributario = informes.certificados( filial, parent )

		""" Numero da operacao 
			1=Confirmação da Operação
			2=Ciência da Emissão
			3=Desconhecimento da Operação
			4=Operação não Realizada
		"""
		mod = 'nfe'
		modulo = 1
		manif_dest = EventoManifestacaoDest(
			cnpj=__cnpj,
			chave=chave,
			data_emissao=datetime.datetime.now(),
			uf=uf,
			operacao=1
			)
		
		# serialização
		serializador = SerializacaoXML(_fonte_dados, homologacao=amb)
		nfe_manif = serializador.serializar_evento(manif_dest)

		# assinatura
		a1 = AssinaturaA1(cer, snh)
		xml = a1.assinar(nfe_manif)
		
		# XML de envio ao sefaz
		#xml_autorizado = etree.tostring(xml, encoding="unicode")
		#print( xml_autorizado )

		con = ComunicacaoSefaz(uf, cer, snh, amb) #-// Para manifesto no ambiente nacionar utiliza { AN como uf }
		envio = con.evento(modelo=mod, evento=xml) # modelo='nfce' ou 'nfe'

		rt = informes.retornosSefaz( envio.text.encode('utf-8'), ["retEnvEvento","infEvento"], parent, nome_evento = 'MANIFESTO' )
		if rt[0] and rt[4] !='135':	modulo = 3
		if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulo, mod, rt[4], '', filial, '', '' )

	def cartaCorrecao(self, parent, filial, __i ):

		rtn, snh, cer, sis, sie, amb, uf, fus, __cnpj, __nfce, regime_tributario = informes.certificados( filial, parent )


		chave = __i[0] #-: Chave
		motivo = __i[1] #-: Motivo do cancelamento
		xml_anterior = __i[5] #-: XML Anterior
		sequencial_envio = __i[6] #-: Sequencial de Envio de CCe { No Maximo ate 20 correcoes }
		cliente = __i[8] #-: Cliente
	
		numero_nf = chave[25:34]
		numero_serie = chave[22:25]
		mod = 'nfe' if chave[20:22] == '55' else 'nfce'
		modulo = 1

		diretorio_gravacao = diretorios.usFolder+'nfe400/' if mod == 'nfe' else diretorios.nfceacb+'nfce400/'
		
		__f = filial.lower()
		__n = datetime.datetime.now().strftime("%m-%Y") +'/'+ str( numero_serie ).zfill(3)+'-'+numero_nf.zfill(9)
		__d = diretorio_gravacao+ __f +"/homologacao/"+ __n if amb else diretorio_gravacao + __f +"/producao/"+ __n
		if os.path.exists( __d ) == False:	os.makedirs( __d )

		carta_correcao = EventoCartaCorrecao(
			cnpj = __cnpj,
			chave = chave,
			data_emissao=datetime.datetime.now(),
			uf = uf,
			n_seq_evento = sequencial_envio,
				correcao = motivo,
			)

		# serialização
		serializador = SerializacaoXML( _fonte_dados, homologacao = amb )
		nfe_cc = serializador.serializar_evento( carta_correcao )

		# assinatura
		a1 = AssinaturaA1( cer, snh )
		xml = a1.assinar( nfe_cc )

		con = ComunicacaoSefaz (uf, cer, snh, amb )
		envio = con.evento( modelo = mod, evento = xml )               # modelo='nfce' ou 'nfe'

		rt = informes.retornosSefaz( envio.text.encode('utf-8'), ["retEnvEvento","infEvento"], parent, nome_evento = 'CCE' )

		if rt[0] and rt[4] == '135':

			"""  Levantar informacoes do XML original  """
			lerXml = DadosCertificadoRetornos()
			docxml = minidom.parseString( envio.text )

			_ch = lerXml.leituraXml( docxml, 'infEvento', 'chNFe' )[0][0] #--// Chave
			_dt = lerXml.leituraXml( docxml, 'infEvento', 'dhRegEvento' )[0][0] #--// Data de recebimento

			_arquivo = open( __d + "/sequencial_"+str( sequencial_envio).zfill(2)+"_cartacorrecao.xml", "w" )
			_arquivo.write( envio.text )
			_arquivo.close()

			informe = _ch, _dt, envio.text, rt[1], xml_anterior, motivo
			grv = EmissaoNotasFiscais()
			grv.salvarNotaFiscal(  emissao = 1, gravacao = 4, dados = informe, filial = filial )

		if rt[0] and rt[4] !='135':	modulo = 3
		if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulo, mod, rt[4], envio.text, filial, '', '' )


class DadosCertificadoRetornos:
	
#---{ Dados-Certificados Retornos SEFAZ }--------------------------// Certificado
	def certificados(self,filial, parent ):

		r = True
		e = ''
		try:

			d = login.filialLT[filial][30].split(';')
			senha = d[5]
			certificado = diretorios.esCerti + d[6] 
			sistema = d[7]
			sistema_emissor = d[8]
			homologacao = True if d[9] == "2" else False
			estado = d[12].upper()
			fuso = d[13]
			cnpj = login.filialLT[filial][9]
			serie_nfce = d[17]
			id_csc = d[20]
			numero_csc = d[21]
			regime = d[11]

			nfce = serie_nfce, id_csc, numero_csc

		except Exception as e:

			if type( e ) !=unicode:	e = str( e )
			r = False
			senha = certificado = sistema = sistema_emissor = homologacao = estado = fuso = ''
			nfce = '','',''

			alertas.dia( parent, u"[ Buscando informações da filial "+ filial +" ]\n\n{ Retorno do Erro }\n"+ e +"\n"+(" "*160),u"Pegando informações da filial selecionada" )

		return r, senha, certificado, sistema, sistema_emissor, homologacao, estado, fuso, cnpj, nfce, regime

#---{ Dados-Certificados Retornos SEFAZ }--------------------------// Retorno SEFAZ
	def retornosSefaz(self, xml, evento, parent, nome_evento='' ):

		s = True
		r = ''
		i = ''
		chave = ''
		csTaT = ''
		protocolo = ''
		data_recebimento = ''
		try:
			
			d = minidom.parseString( xml )
			r = {}
			lan = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
			for even in evento:
				
				if even in xml:

					r[u'Codigo de retorno'] = self.leituraXml( d, even, "cStat" )[0][0]
					r[u'Descrição do motivo'] = self.leituraXml( d, even, "xMotivo" )[0][0]
					r[u'Ambiente'] = self.leituraXml( d, even, "tpAmb" )[0][0]
					try:
						r[u'Versão da NFes'] = self.leituraXml( d, even, "versao" )[1]
					except Exception as erros:
						r[u'Versão da NFes'] = ''
						
					r[u'Data e hora do recebimento'] = self.leituraXml( d, even, "dhRecbto" )[0][0]
					r[u'Numero da chave da nfe'] = self.leituraXml( d, even, "chNFe" )[0][0]
					r[u'Protocolo de autorização'] = self.leituraXml( d, even, "nProt" )[0][0]
					r[u'Modelo da NFe'] = self.leituraXml( d, even, "mod" )[0][0]

					chave = r[u'Numero da chave da nfe']
					csTaT = r[u'Codigo de retorno']
					protocolo = r[u'Protocolo de autorização']
					data_recebimento = r[u'Data e hora do recebimento']
					
					i +='\n{ Evento: '+even+' '+lan+' [ '+nome_evento+' ] }\n'
					for ii in r:

						if r[ii]:	i += ii +': '+r[ii]+'\n'

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
	def mostrarInformacoesRetorno(self, parent, informacoes, retornos, modulos, modelo, cStat, xml, filial, filexml, email ):

		vsu_frame=VisualizarRetornos(parent=parent,id=-1, inf = informacoes, rt = retornos, md = modulos, modelo = modelo, csTaT = cStat, string_xml = xml, filial = filial, file_xml = filexml, emails = email )
		vsu_frame.Centre()
		vsu_frame.Show()


#-----------------------------------------------------------------------#
#                        Emissao NFe 4.00                               #
#-----------------------------------------------------------------------#
class EmissaoNotasFiscais:

#---{ Emissao NF }--------------------------// Confeccao da NF
	def nfe40( self, parent, tipo_emissao = 1 ):

		self.p = parent
		self.e = self.p.emails.strip()
		
		self.filial = self.p.filial_notas
		rtn, snh, cer, sis, sie, amb, uf, fus, __cnpj, __nfce, regime_tributario = informes.certificados( self.filial, self.p )

		if rtn:
			
			self.informacoes_clientes_gravacao = ''
			
			"""  Incluir emitente  """
			dados_emitente, uf_emi = self.informacoesEmitente( self.filial, tipo_emissao )

			"""  Incluir cliente  """
			dados_clientes, inf_clientes_gravacao, pessoa_juridica_fisica, uf_cli, endereco_entregar_retirar = self.informacoesCliente( tipo_emissao, amb, '55', parent )

			"""  Incluindo transportadora  """
			indice_transportadora = self.p.ListaTrans.GetFocusedItem()
			transportadora_documento = self.p.ListaTrans.GetItem( indice_transportadora, 0 ).GetText() #--------// CPF-CPPJ
			transportadora_nome = self.p.ListaTrans.GetItem( indice_transportadora, 2 ).GetText() #-------------// Descricao do Transportador
			transportadora_dados = self.p.ListaTrans.GetItem( indice_transportadora, 3 ).GetText().split('|') #-// Endereco

			dados_transportadora = self.adicionarTransportadora( transportadora_documento, transportadora_nome, transportadora_dados )

			"""  Incluir identificacao da nfe  """
			dados_identificacao, numero_nota, __serie, __origem, __nfe_nfce, estado_destino, uf_ide = self.indentificacaoNotaFiscal( dados_emitente, dados_clientes, dados_transportadora, tipo_emissao, self.p.cTClie[0], amb, pessoa_juridica_fisica, endereco_entregar_retirar )

			if '' in [uf_emi.strip(), uf_cli.strip(), uf_ide.strip() ]:
				
				alertas.dia( self.p, u"{ Unidade federativa }\n\n1-Identificação da nfe\n2-Emitente\n3-Cliente\n\nPode estar vazio...\n"+(" "*120),u"Emissção da NFe 40.00")
				return
				
			"""  Enviar ao sefaz atraves da LIB  """
			if self.adicionandoProdutos( dados_identificacao, regime_tributario, pessoa_juridica_fisica, estado_destino ):
					
				"""  Montar pasta para gravacao do XML  """
				numero_nota_fiscal = str( numero_nota ).zfill(9)
				__f = self.filial.lower()
				__n = datetime.datetime.now().strftime("%m-%Y") +'/'+ str( self.p.nserienf ).zfill(3)+'-'+numero_nota_fiscal
				__d = diretorios.usFolder+"nfe400/"+__f+"/homologacao/"+ __n if amb else diretorios.usFolder+"nfe400/"+__f+"/producao/"+ __n
				if os.path.exists( __d ) == False:	os.makedirs( __d )
				
				nota_enviada = True
				try:

					"""  Serialização  """
					serializador = SerializacaoXML(_fonte_dados, homologacao=amb)
					nfe = serializador.exportar()
					
					""" Assinatura """
					a1 = AssinaturaA1(cer, snh)
					xml = a1.assinar( nfe )

					"""  Envio  """
					con = ComunicacaoSefaz(uf, cer, snh, amb)
					envio = con.autorizacao(modelo='nfe', nota_fiscal=xml, ind_sinc = 1)

				except Exception as erro:

					if type(erro) !=unicode:	erro = str( erro )
					nota_enviada = False
					alertas.dia( self.p, u"{ Erro na montagem da NFe, para enviar }\n\n"+erro+u'\n'+(" "*120),'Envio de nfe ao sefaz')
					
				"""  Nota fiscal autorizada  """
				if nota_enviada:
					
					if envio[0] == 0:

						xml_autorizado = etree.tostring(envio[1], encoding="unicode").replace('\n','').replace('ns0:','')
						rt = informes.retornosSefaz( xml_autorizado, ["protNFe","retEnviNFe"], parent, nome_evento = 'EMISSAO' )
						
						lerXml = DadosCertificadoRetornos()
						docxml = minidom.parseString( xml_autorizado )
						
						numero_nf = lerXml.leituraXml( docxml, 'infNFe', 'nNF' )[0][0]
						numero_serie = lerXml.leituraXml( docxml, 'infNFe', 'serie' )[0][0]
						
						csTaT = lerXml.leituraXml( docxml, 'protNFe', 'cStat' )[0][0]
						chave = lerXml.leituraXml( docxml, 'protNFe', 'chNFe' )[0][0]
						protocolo = lerXml.leituraXml( docxml, 'protNFe', 'nProt' )[0][0]
						data_recebimento = lerXml.leituraXml( docxml, 'protNFe', 'dhRecbto' )[0][0]

						"""  Emissao da nfe com recebimento no caixa """
						if self.p.origem_emissao == '160':	self.p.fecharNfe310( "160", numero_nf, self.filial )

						nfe_nfce = '1'
						nfe_origem  = '2' if self.p.origem_emissao == 'RMA' else '1' #-----// Origem NFE, 1-vendas, 2-compras
						nfe_emissao = '1'

						"""  Atualizar dados nas tabelas cdavs, ocorrencia, receber, nfes, sefazxml  """
						gravar_gerenciador = self.p.numero_dav, protocolo, data_recebimento, chave, numero_nf, nfe_nfce, nfe_origem, csTaT, nfe_emissao, __d, xml_autorizado, rt[1], numero_serie
						self.salvarNotaFiscal( emissao = tipo_emissao, gravacao = 2, dados = gravar_gerenciador, filial = self.filial )

						modulos_nfe = 2 #--// Opcao para habilitar os icones e alternar a cor de fundo { 1-status, 2-emissao, 3-erro na emissao }

						arquivo_xml_pasta = __d  +'/'+ rt[3] +"-nfe.xml" if xml_autorizado else ''
						if xml_autorizado:

							__arquivo = open( __d  +'/'+ rt[3] +"-nfe.xml", "w" )
							__arquivo.write( xml_autorizado )
							__arquivo.close()

						if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulos_nfe, '55', csTaT, xml_autorizado, self.filial, arquivo_xml_pasta, self.e )
						
					else: #--// Rejeicao

						"""  Atualizar dados nas tabelas cdavs, ocorrencia, receber, nfes, sefazxml  """
						rt = informes.retornosSefaz( envio[1].text, ["protNFe","retEnviNFe"], parent, nome_evento = 'EMISSAO' )
						gravar_gerenciador= numero_nota, __serie, __origem, __nfe_nfce, rt[1]
						self.salvarNotaFiscal( gravacao = 3, dados = gravar_gerenciador, filial = self.filial )

						"""  Carrega o XML original para ser analisado posteriormente  """
						__xml = etree.tostring(xml, encoding="unicode") #.replace('\n','').replace('ns0:','')

						modulos_nfe = 3 #--// Opcao para habilitar os icones e alternar a cor de fundo { 1-status, 2-emissao, 3-erro na emissao }
						if rt[0]:

							arquivo_retorno = __d + "/retorno.xml"
							erro = 'original_assinado_erro_normal.xml'
							if rt[4] in ['225']: 
								
								erro = 'original_assinado_erro_shema.xml'
								arquivo_retorno = __d + '/' + erro
								
							_arquivo = open( __d + "/retorno.xml", "w" )
							_arquivo.write( envio[1].text )
							_arquivo.close()

							"""  Grava o XML original para analisar posteriormente  """
							_arquivo = open( __d + '/' + erro, "w" )
							_arquivo.write( __xml )
							_arquivo.close()

							informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulos_nfe, '55', rt[4], __xml, self.filial, arquivo_retorno, self.e )

#---{ Transportadora }--------------------------// Adicionar transportadora
	def adicionarTransportadora(self, documento, nome, dados ):

		transportadora = ''
		if nome and documento and dados:

			transportadora = Transportadora( razao_social = nome,
							 tipo_documento = 'CNPJ' if len( documento ) == 14 else 'CPF',
							 numero_documento = documento,
							 inscricao_estadual = dados[0],
							 endereco_logradouro = dados[4]+', '+dados[5]+' '+dados[6],
							 endereco_uf = dados[10],
							 endereco_municipio = dados[8],
			)

		return transportadora
		
#---{ Emissao NF }--------------------------// Adicionar produtos
	def adicionandoProdutos(self, nota_fiscal, regime_tributacao, pessoa, estado_destino ):
	
		for i in range( self.p.editdanfe.GetItemCount() ):

			descricao_produto = self.p.editdanfe.GetItem(i,3).GetText().strip()

			prod_cfop = str( self.p.editdanfe.GetItem( i, 32 ).GetText().strip() )
			prod_cst  = str( self.p.editdanfe.GetItem( i, 33 ).GetText().strip() )
			prod_ncm  = str( self.p.editdanfe.GetItem( i, 34 ).GetText().strip() )

			prod_desconto = Decimal( self.p.editdanfe.GetItem(i,16).GetText().strip() )
			prod_frete = Decimal( self.p.editdanfe.GetItem(i,14).GetText().strip() )
			prod_outras_depesas_acessorias = Decimal( self.p.editdanfe.GetItem(i,15).GetText().strip() )

			"""	
			       Simples nacional 
			    Tributacao e codificacao
			"""
			cst_origem = int( prod_cst[:1].strip() )
			cst_csosn  = str( int( prod_cst[1:] ) ) # prod_cst[1:].strip() if regime_tributacao == '1' else str( int( prod_cst[1:] ) ).zfill(2)
			mod_pis    = str( self.p.editdanfe.GetItem( i, 51 ).GetText().strip() ) if self.p.editdanfe.GetItem( i, 51 ).GetText().strip() else '06'
			mod_cofins = str( self.p.editdanfe.GetItem( i, 52 ).GetText().strip() ) if self.p.editdanfe.GetItem( i, 52 ).GetText().strip() else '06'
			if cst_csosn == '0':	cst_csosn = '00'
			
			"""  Modalidade do icms  """
			modalidade_icms = cst_csosn
			if modalidade_icms in ['102','103','300','400']:	modalidade_icms = '102'
			
			modalidade_base_calculo = '3'
			#-// Tributos municipais, estaduais, federais, FONTE: IBPT
			
			"""  
				Tributacao regime normal
			"""
			valor_produto_ibpt = self.valorAproximadoTributos( produto_geral = 2, ibpt_produto = str( self.p.editdanfe.GetItem( i, 43 ).GetText().strip() ), tipo = 'nfe' )
			icms_valor_base_calculo = Decimal( self.p.editdanfe.GetItem(i,22).GetText().strip() )
			icms_aliquota = Decimal( self.p.editdanfe.GetItem(i,17).GetText().strip() )
			icms_valor = Decimal( self.p.editdanfe.GetItem(i,27).GetText().strip() )
			icms_40valor_desoneracao = Decimal('0.00')
			icms_40motivo_desoneracao = ''

			"""  Partilha do ICMS vendas inter-estadual e fundo de combate a pobreza
				 0 -: Valor da BC do ICMS na UF de destino	
				 1 -: Percentual do ICMS relativo ao Fundo de Combate à Pobreza (FCP) na UF de destino
				 2 -: Alíquota interna da UF de destino
				 3 -: Alíquota interestadual das UF envolvidas
				 4 -: Percentual provisório de partilha do ICMS Interestadual
				 5 -: Valor do ICMS relativo ao Fundo de Combate à Pobreza (FCP) da UF de destino
				 6 -: Valor do ICMS Interestadual para a UF de destino
				 7 -: Valor do ICMS Interestadual para a UF do remetente
			"""
			indicador_destino = int('2') if self.p.estadoe != estado_destino else int('1')
			dfal_fcp_aliquota_inserido_uf_destino = dfal_valor_icms_fcp_uf_destino = dfal_basec_uf_destino = dfal_fcp_basec_uf_destino = dfal_aliquota_uf_destino = Decimal('0.00')
			dfal_aliquota_interestadual = dfal_percentual_partilha_uf_destino = dfal_valor_partilha_icms_uf_destino = dfal_valor_partilha_icms_uf_origem = Decimal('0.00')
			
			icms_partilha_fcp = self.partilhaIcmsDifal( self.p.editdanfe, i )
			if indicador_destino == 2 and pessoa == '2' and Decimal( self.p.cTDavs[0][110].split(";")[1] ) and Decimal( self.p.cTDavs[0][110].split(";")[2] ) and Decimal( icms_partilha_fcp[0] ):
				
				dfal_fcp_aliquota_inserido_uf_destino = Decimal('0.00') # pFCPUFDest icms_partilha_fcp[1]
				dfal_valor_icms_fcp_uf_destino = Decimal('0.00') # vFCPUFDest icms_partilha_fcp[5]
				dfal_basec_uf_destino = Decimal( icms_partilha_fcp[0] ) # vBCUFDest
				dfal_fcp_basec_uf_destino = Decimal('0.00') # vBCFCPUFDest
				dfal_aliquota_uf_destino = Decimal( icms_partilha_fcp[2] ) # pICMSUFDest
				dfal_aliquota_interestadual = Decimal( icms_partilha_fcp[3] ) # pICMSInter
				dfal_percentual_partilha_uf_destino = Decimal( icms_partilha_fcp[4] ) # pICMSInterPart
				dfal_valor_partilha_icms_uf_destino = Decimal( icms_partilha_fcp[6] ) # vICMSUFDest
				dfal_valor_partilha_icms_uf_origem = Decimal( icms_partilha_fcp[7] ) # vICMSUFRemet
			#----------------// Partilha
			"""  Colocar em dados adicionais do produto  { ano aceita quebra de linha [ qubra de linha da erroa shema ] }"""
			numero_series = self.p.editdanfe.GetItem(i,68).GetText().replace('|','')
			produto_dados_adicionais = numero_series.strip()
			codigo_barras = self.p.editdanfe.GetItem(i,2).GetText().strip() if not self.p.descartar_barras.GetValue() else ''

			nota_fiscal.adicionar_produto_servico(
				codigo = self.p.editdanfe.GetItem(i,1).GetText().strip(),                           # id do produto
				ean = codigo_barras,
				ean_tributavel = codigo_barras,
				descricao = descricao_produto,
				informacoes_adicionais_produto = produto_dados_adicionais,
				ncm = self.p.editdanfe.GetItem(i,34).GetText().strip(),
				cest = self.p.editdanfe.GetItem(i,44).GetText().strip(),                            # NT2015/003
				cfop = self.p.editdanfe.GetItem(i,32).GetText().strip(),
				unidade_comercial = self.p.editdanfe.GetItem(i,5).GetText().strip(),
				quantidade_comercial = Decimal( self.p.editdanfe.GetItem(i,4).GetText().strip().replace(',','') ),        # 12 unidades
				valor_unitario_comercial = Decimal( self.p.editdanfe.GetItem(i,6).GetText().strip() .replace(',','') ),  # preço unitário
				valor_total_bruto = Decimal( self.p.editdanfe.GetItem(i,7).GetText().strip().replace(',','') ),       # preço total
				unidade_tributavel = self.p.editdanfe.GetItem(i,5).GetText().strip(),
				quantidade_tributavel = Decimal( self.p.editdanfe.GetItem(i,4).GetText().strip().replace(',','') ) ,
				valor_unitario_tributavel = Decimal( self.p.editdanfe.GetItem(i,6).GetText().strip() .replace(',','') ),
				desconto = prod_desconto,
				total_frete = prod_frete,
				outras_despesas_acessorias = prod_outras_depesas_acessorias,
				ind_total = 1, #-// 0-Nao compoe o valor da nota 1-Compoe o valor da nota
				numero_pedido = self.p.numero_dav,             # xPed
				numero_item = str( i + 1 ),                    # nItemPed
				icms_modalidade = modalidade_icms,
				icms_origem = cst_origem,
				icms_csosn = cst_csosn,
				icms_modalidade_determinacao_bc = modalidade_base_calculo,
				icms_valor_base_calculo = icms_valor_base_calculo,
				icms_aliquota = icms_aliquota, #-// ICMSSN, pCredSN
				icms_valor = icms_valor,
				icms_valor_base_retido_fonte_st = Decimal('0.00'),
				icms_valor_icms_st_retido = Decimal('0.00'),
				icms_percentual_fcp = Decimal('0.00'),
				icms_valor_base_calculo_fcp_retido = Decimal('0.00'),
				icms_percentual_fcp_retido = Decimal('0.00'),
				icms_valor_fcp_retido = Decimal('0.00'),
				icms_40valor_desoneracao = icms_40valor_desoneracao,
				icms_40valor_desoneracao_motivo = icms_40motivo_desoneracao,
				icms_credito = '0.00', #--// ICMSSN, vCredICMSSN
				pis_modalidade = mod_pis,
				cofins_modalidade = mod_cofins,
				difal_basec_uf_destino = dfal_basec_uf_destino, # vBCUFDest
				difal_fcp_basec_uf_destino = dfal_fcp_basec_uf_destino, # vBCFCPUFDest
				difal_fcp_aliquota_inserido_uf_destino = dfal_fcp_aliquota_inserido_uf_destino, # pFCPUFDest
				difal_aliquota_uf_destino = dfal_aliquota_uf_destino, # pICMSUFDest
				difal_aliquota_interestadual = dfal_aliquota_interestadual, # pICMSInter
				difal_percentual_partilha_uf_destino = dfal_percentual_partilha_uf_destino, # pICMSInterPart
				difal_valor_icms_fcp_uf_destino = dfal_valor_icms_fcp_uf_destino, # vFCPUFDest
				difal_valor_partilha_icms_uf_destino = dfal_valor_partilha_icms_uf_destino, # vICMSUFDest
				difal_valor_partilha_icms_uf_origem = dfal_valor_partilha_icms_uf_origem, # vICMSUFRemet
				valor_tributos_aprox = valor_produto_ibpt,
				)
	
		return True

#---{ Emissao NF }--------------------------// Identificacao da Nota Fiscal
	def indentificacaoNotaFiscal(self, informar_dados_emitente, informar_dados_clientes, informar_dados_transportadora, emissao, dados_cliente, ambiente, pessoa, endereco_entrega_retira ):

		"""  Dados sobre a nota fiscal  """
		#-// Composicao do numero da nNF
		rT, nfis = numeros.VerificaNFE( self.p.numero_dav, Tnf = emissao, Filial = self.filial ) #-// Numero de NF gerado ou utilizando um numero ja gerado
		if rT == False:	nfis = numeros.numero("5","Numero da NFe",self.p, self.filial ) #-// Gerando um novo numero

		if nfis == '':
						
			alertas.dia(self.p,u"Numero de NFe não foi gerado, Tente novamente!!\n"+(" "*110),u"Emissão de NFes")
			return
		
		"""  Gravando dados NF em gerenciador de NFs  """
		remessa_simples_faturamento = ''
		if self.p.converte.GetValue().split("-")[0] == "02":	remessa_simples_faturamento = "1" #-----: Simples Faturamento p/Entrega Futura
		if self.p.converte.GetValue().split("-")[0] == "01":	remessa_simples_faturamento = "2" #-----: Remessa de Entrega Futura

		nfe_nfce = '1'
		nfe_inutilizar = '2' #-// Marca para inutilizar
		nfe_origem = '2' if self.p.origem_emissao == 'RMA' else '1' #-----// Origem NFE, 1-vendas, 2-compras
		nfe_ambiente = '2' if ambiente else '1'

		"""  Valor total da nota, Se o sistema estiver configurado para nao retear o frete  """
		referenciar_nota = [] #--// Devolucao, RMA
		if emissao == 3:

			nfe_valor_nota = str( self.p.cTDavs[0][26] ).strip().replace(",","")
			referenciar_nota = [self.p.NumeroChav.GetValue()]
			
		else:
			
			nfe_valor_nota = str( self.p.cTDavs[0][37] ).strip().replace(",","")
			if not self.p.reateio_frete and self.p.cTDavs[0][23]:	nfe_valor_nota = str( ( self.p.cTDavs[0][37] - self.p.cTDavs[0][23] ) )

		"""  Incluir nas tabelas>--> cdavs, dcdavs, nfes """
		if not rT:

			gravar_gerenciador = str( nfis ), self.p.numero_dav, remessa_simples_faturamento, nfe_nfce, nfe_inutilizar, nfe_origem, nfe_ambiente, self.filial, self.p.nserienf, nfe_valor_nota, self.informacoes_clientes_gravacao
			self.salvarNotaFiscal( emissao = emissao, gravacao = 1, dados = gravar_gerenciador )

		indicar_presenca = "9" #-: Operação presencial

		if emissao == 3:	estado_destino = dados_cliente[14] #-// Devolucao de RMA
		else:	estado_destino = dados_cliente[15]

		cli_consumidor_final = int( self.p.indconfina.GetValue().split('-')[0] )

		indicador_destino = int('2') if self.p.estadoe != estado_destino else int('1')
		data_entrada_saida = str( datetime.datetime.strptime( self.p.EntraSaida.GetValue().FormatDate(),'%d-%m-%Y') ).split(' ')[0]
		
		horas = datetime.datetime.now() + datetime.timedelta(minutes=20)
		horad = data_entrada_saida+' '+str( horas.strftime("%T") )
		data_entrada_saida = datetime.datetime.strptime(horad, "%Y-%m-%d %H:%M:%S")

		""" Tributos municipais, estaduais, federais, FONTE: IBPT """
		ibpt_federal, ibpt_estadual, ibpt_municipal, ibpt_valortotal = self.valorAproximadoTributos( produto_geral = 1, ibpt_produto = self.p.editdanfe, tipo = 'nfe' )
		
		""" Frete por Conta, Endereço da Transportadora """
		frete_modalidade = int( self.p.modalidade_frete.GetValue().split('-')[0] )

		"""  Dados adicionais
			Aproveitamento do credito de ICMS
		"""
		valor_apropencentual = "" if not self.p.percentual_aproveitamento_icms or not self.p.aproveitamento_credito.GetValue() else format( self.p.percentual_aproveitamento_icms, ',' ) 
		valor_aproveitamento = "" if not self.p.percentual_aproveitamento_icms or not self.p.aproveitamento_credito.GetValue() else format( self.p.valor_total_aproveitamento_icm, ',' )

		dados_adicionais = informacoes_ibpt_imposto = adicionais_rodape = ""
		informe_1 = 'DOCUMENTO EMITIDO POR ME OU EPP OPTANTE PELO SIMPLES NACIONAL|'+ \
					'NAO GERA DIREITO A CREDITO FISCAL DE IPI|'
					
		informe_2 = 'PERMITE O APROVEITAMENTO DO CREDITO DE ICMS NO VALOR DE R$ "'+str( valor_aproveitamento )+'"|'+ \
					'CORRESPONDENTE À ALIQUOTA DE "'+str( valor_apropencentual )+'" %, NOS TERMOS DO ART. 23 DA LEI COMPLEMENTAR Nº 123, DE 2006|'+ \
					'NF-e: Emitida nos termos do Art. 158, caput e  Paragrafo 1o do RICMS Livro VI do Decreto numero 27427/2000.|'

		if emissao == 1 and self.p.cTDavs[0][109]:

			dados_ibpt = self.p.cTDavs[0][109].split("|")
			valo_imposto = "Trib aprox R$ "+format( Decimal( ibpt_valortotal ),',')+" { Federal R$ "+format( Decimal( ibpt_federal ),',')+" Estadual R$ "+format( Decimal( ibpt_estadual ),',')+" Municipal R$: "+format( Decimal( ibpt_municipal ),',')+" }|Fonte: "+str( dados_ibpt[6] )+" "+str( dados_ibpt[5] )+" "+str( dados_ibpt[4] ) +'|'
			informacoes_ibpt_imposto = "Tributos Totais Incidentes Lei Federal 12.741/2012|"+valo_imposto

		regime_tributario = login.filialLT[ self.filial ][30].split(";")[11]
		if emissao == 1 and regime_tributario == '1':	dados_adicionais +=informe_1
		if emissao == 1 and regime_tributario == '1' and valor_apropencentual and valor_aproveitamento:	dados_adicionais +=informe_2

		if emissao and informacoes_ibpt_imposto:	dados_adicionais +='|'+ informacoes_ibpt_imposto #--// IBPT >--> Informacoes de tributos federal,estadual,municipal
		if self.p.dadosA.strip():	dados_adicionais +='|'+self.p.dadosA.strip().replace('\n','|') #--// Informacoes de rodape da nota vindo do cadastro de filiais sistema
		
		"""  Notas de rodape"""
		if login.rdpnfes:	dados_adicionais += '|'+login.rdpnfes.strip().replace('\n','|')
		
		"""  Fim dados adicionais  """
	
		"""  Dados do veiculo  { Parece que o dados do veiculo nao entra pq o CTe ja tem essas informacoes e nao se sabe qual o veiculo q vai levar os produtos na coleta }  """
		#		transp_veiculo_placa = str( self.p.vplaca ).replace('-','').replace(' ','')
		#		transp_veiculo_uf = str( self.p.veicuf )
		#		transp_Veiculo_rntc = str( self.p.cdanTT )

		"""  Total da partilha do icms p/consumidor final  p/venda interstadual  """
		partilha_fundo_pobreza = partilha_icms_origem = partilha_icms_destino = Decimal('0.00')

		if indicador_destino == 2 and pessoa == '2' and Decimal( self.p.cTDavs[0][110].split(";")[1] ) and Decimal( self.p.cTDavs[0][110].split(";")[2] ):

			#partilha_fundo_pobreza = Decimal( self.p.cTDavs[0][110].split(";")[0] ) #-: Partilha fundo de pobreza { vFCPUFDest }
			partilha_icms_origem   = Decimal( self.p.cTDavs[0][110].split(";")[1] ) #-: Partilha icms origen { vICMSUFDest }
			partilha_icms_destino  = Decimal( self.p.cTDavs[0][110].split(";")[2] ) #-: Partilha icms destino { vICMSUFRemet }
			
		"""  Identificacao da NF  """
		ide_uf = str( self.p.estadoe )
		ide_noperacao = self.p.natureza.GetValue()[:60].decode('UTF-8').strip()
		ide_forma_pagamento = 0         # 0=Pagamento à vista; 1=Pagamento a prazo; 2=Outros.
		ide_tipo_pagamento = 1          # 1-Dinheiro,2-Cheque,3-CartaoCredito,4-CartaoDebito,5-CreditoLoja,10-Alimentacao,11-ValeRefeicao,13-ValeCombustivel,14-DuplicataMercantil,90-Sem pagamentos,99-Outros
		ide_modelo = 55                 # 55=NF-e; 65=NFC-e
		ide_serie = self.p.nserienf
		ide_numero_nf = str( nfis )           # Número do Documento Fiscal.
		ide_data_emissao = datetime.datetime.now()
		ide_data_saidaentrada = data_entrada_saida
		ide_tipodocumento = int( self.p.saidanetra.GetValue().split('-')[0] )          # 0=entrada; 1=saida
		ide_municipio = login.filialLT[ self.filial ][13]       # Código IBGE do Município 
		ide_tipo_impressao_danfe=1    # 0=Sem geração de DANFE;1=DANFE normal, Retrato;2=DANFE normal Paisagem;3=DANFE Simplificado;4=DANFE NFC-e;
		ide_forma_emissao = '1'         # 1=Emissão normal (não em contingência);
		ide_cliente_final = cli_consumidor_final           # 0=Normal;1=Consumidor final;
		ide_indicador_destino = indicador_destino
		ide_indicador_presencial = 1

		"""  Finalidade da emissao  """
		ide_finalidade_emissao = int( self.p.finnfefornece.GetValue().split('-')[0] )  #--// 1=NF-e normal;2=NF-e complementar;3=NF-e de ajuste;4=Devolução de mercadoria.

		ide_processo_emissao=0      #0=Emissão de NF-e com aplicativo do contribuinte;

		ide_transporte_modalidade_frete=frete_modalidade
		ide_informacoes_adicionais_interesse_fisco=''
		ide_informacoes_complementares_interesse_contribuinte = dados_adicionais
		ide_totais_tributos_aproximado=Decimal( ibpt_valortotal )
		ide_valor_total_nota = self.p.cTDavs[0][26] if emissao == 3 else self.p.cTDavs[0][37]
		ide_valor_troco = str( self.p.cTDavs[0][49] ) if emissao != 3 and self.p.cTDavs[0][49] else ''

		"""
			Formas de pagamento
			POS=Emissao posterior ao recebimento
			RMA=Nota de devolucao de compras
			160=Emissao com recebimento no caixa
			1-"01", 56-Dinheiro  2-"02", 57-Ch.Avista  3-"02", 58-Ch.Predatado  4-"03", 59-CT Credito 5-"04", 60-CT Debito  6-"99", 61-FAT Boleto
			7-"99", 62-FAT Carteira  8-"99", 63-Finaceira  9-"10", 64-Tickete  10-"05", 65-PGTO Credito  11-"99", 66-DEP. Conta  12-"99", 85-Receber Local   
		"""
		
		lista_pagamentos = []
		if emissao == 1 and self.p.origem_emissao == "160":	lista_pagamentos = self.retornarPagamentos( origem_emissao = '160', lista1_pagamentos = self.p.lista_recebimentos160 )
		if emissao == 1 and self.p.origem_emissao == "POS":	lista_pagamentos = self.retornarPagamentos( origem_emissao = 'POS', lista1_pagamentos = self.p.cTDavs[0] )

		"""  Relacionando e totalizando formas de pagamentos  """
		lista_duplicatas, valor_total_faturado = self.relacionarDuplicatas( emissao )

		"""  Reteamento do frete { Debita frete do valor total do pedido, Colocando a forma de pagamento em dinheiro, se tiver duplicatas o sistema discarta }  """
		if not self.p.reateio_frete and self.p.cTDavs[0][23]:
			
			ide_valor_total_nota = ( self.p.cTDavs[0][37] - self.p.cTDavs[0][23] )
			lista_pagamentos = {}

		"""  Meia nota { Emissao da nfe na opcao de pagamento DINHEIRO }  """
		if self.p.meia_nf400:	lista_pagamentos = {}

		"""  Devolucao de vendas  { Forma de pagamento 90-sem pagamento, tipo 2-outros} """
		numero_fatura =  str( int(self.p.numero_dav) ) if emissao == 1 else ''
		if emissao in [2,3]:	ide_forma_pagamento, ide_tipo_pagamento = 2, 90

		unidade_ferederativa = ide_uf

		entregando =[]
		"""  Adicionar endereco para entregar e/ou retirar
			0-loc_endereco, 1-loc_numero, 2-loc_complemento, 3-loc_bairro, 4-loc_municipio, 5-loc_cdmunicipio, 6-loc_uf, 7-loc_cep, 8-tipo_documento{CPF,CNPJ}, 9-Numero Documento
		"""	
		if endereco_entrega_retira:

			entregando.append( endereco_entrega_retira[0] )
			entregando.append( endereco_entrega_retira[1] )
			entregando.append( endereco_entrega_retira[2] )
			entregando.append( endereco_entrega_retira[3] )
			entregando.append( endereco_entrega_retira[4] )
			entregando.append( endereco_entrega_retira[5] )
			entregando.append( endereco_entrega_retira[6] )
			entregando.append( endereco_entrega_retira[7] )
			entregando.append( endereco_entrega_retira[8] )
			entregando.append( endereco_entrega_retira[9] )
		
		"""  Identificacacao da nota  """
		nota_fiscal = NotaFiscal(
		   emitente = informar_dados_emitente,
		   cliente = informar_dados_clientes,
		   transporte_transportadora = informar_dados_transportadora,
		   entrega = entregando,
		   uf = ide_uf,
		   natureza_operacao = ide_noperacao,
		   forma_pagamento = ide_forma_pagamento,
		   tipo_pagamento = ide_tipo_pagamento,
		   modelo = ide_modelo,
		   serie = ide_serie,
		   numero_nf = ide_numero_nf,
		   data_emissao = ide_data_emissao,
		   data_saida_entrada = ide_data_saidaentrada,
		   tipo_documento = ide_tipodocumento,
		   municipio = ide_municipio,
		   tipo_impressao_danfe = ide_tipo_impressao_danfe,
		   forma_emissao = ide_forma_emissao,
		   cliente_final = ide_cliente_final,
		   indicador_destino = ide_indicador_destino,
		   indicador_presencial = ide_indicador_presencial,
		   finalidade_emissao = ide_finalidade_emissao,
		   processo_emissao = ide_processo_emissao,
		   transporte_modalidade_frete = ide_transporte_modalidade_frete,
		   informacoes_adicionais_interesse_fisco = ide_informacoes_adicionais_interesse_fisco,
		   informacoes_complementares_interesse_contribuinte = ide_informacoes_complementares_interesse_contribuinte,
		   totais_icms_total_nota = ide_valor_total_nota,
		   totais_tributos_aproximado = ide_totais_tributos_aproximado,
		   pagamentos_formas_pagamentos = lista_pagamentos,
		   pagamentos_troco = '',
		   fatura_numero = numero_fatura,
		   fatura_valor_original = valor_total_faturado,
		   fatura_valor_desconto = Decimal('0.00'),
		   fatura_valor_liquido = valor_total_faturado,
		   totais_fcp_destino = partilha_fundo_pobreza,
		   totais_icms_inter_destino = partilha_icms_destino,
		   totais_icms_inter_remetente = partilha_icms_origem,
		   notas_fiscais_referenciadas = referenciar_nota,
		)

		"""  Volumes { Adiciona volumes }"""
		volume_quantidade = self.p.qVolum if self.p.qVolum and self.p.qVolum.isdigit() and Decimal( self.p.qVolum ) > 0 else ''
		volume_marca = self.p.marcar if self.p.marcar else ''
		volume_numera = self.p.numera if self.p.numera else ''
		volume_especie = self.p.especi if self.p.especi else ''
		volume_pliquido = str( Truncar.trunca( 1, Decimal( self.p.pesoLQ ) ) ) if Decimal( self.p.pesoLQ ) > 0 else ''
		volume_pbruto = str( Truncar.trunca( 1, Decimal( self.p.pesoBR ) ) ) if Decimal( self.p.pesoBR ) > 0 else ''

		if volume_quantidade and volume_especie and volume_marca and volume_numera and volume_pliquido  and volume_pbruto:

			nota_fiscal.adicionar_transporte_volume( quantidade = volume_quantidade,
												  especie = volume_especie,
												  marca = volume_marca,
												  numeracao = volume_numera,
												  peso_liquido = volume_pliquido,
												  peso_bruto = volume_pbruto,
												)		
		
		"""  Adicionado duplicatas
		     Nao fazer rateamento do frete { se tiver duplicatas o sistema discarta }
		"""
		faturar = True
		if self.p.meia_nf400:	faturar = False #--// Meia nota { Emissao da nfe na opcao de pagamento DINHEIRO }
		if not self.p.reateio_frete and self.p.cTDavs[0][23]:	faturar = False #--// Rateiro do frete { Apenas DINHEIRO }

		if lista_duplicatas and faturar:
				
			for ldp in lista_duplicatas:

				numero_boleto,parcelas = lista_duplicatas[ ldp ][0].split('-')
				numero_titulo = str( int( numero_boleto ) )+ '-'+ parcelas
				nota_fiscal.adicionar_duplicata( numero = numero_titulo,
				data_vencimento = lista_duplicatas[ ldp ][1],
				 valor = Decimal( lista_duplicatas[ ldp ][2] ),
				)
		
		return nota_fiscal, str( nfis ), self.p.nserienf, nfe_origem, nfe_nfce, estado_destino, unidade_ferederativa

	def relacionarDuplicatas( self, emissao ):

		ordem = 1	
		contas_areceber = ""
		relacao_duplicatas = {}
		valor_total_parcelas = Decimal('0.00')
		if self.p.relacao_cobranca_receber and len( login.filialLT[ self.filial ][35].split(";") ) >= 97 and login.filialLT[ self.filial ][35].split(";")[96] == "T":	contas_areceber = self.p.relacao_cobranca_receber
		if emissao !=3 and self.p.listaQuan == '' and contas_areceber and ( len( contas_areceber.split('|') ) - 1 ) > 0:
			
			for dpl in contas_areceber.split('|'):
			
				if dpl and dpl[0]:
						
					fp = dpl.split(';')
					duplicata = str( fp[0] )
					vencimento = format( datetime.datetime.strptime( str( fp[1] ), "%d/%m/%Y").date(), '%Y-%m-%d' )
					formapagamento = str( fp[2] )
					valor_apagar = str( fp[3] ).replace(',','')

					imprimir = False
					if formapagamento[:2] == "06":	imprimir = True
					if formapagamento[:2] == "07" and len( login.filialLT[ self.filial ][35].split(";") ) >=37 and login.filialLT[ self.filial ][35].split(";")[36] == "T":	imprimir = True	

					if imprimir:
						relacao_duplicatas[ordem] = duplicata, vencimento, valor_apagar
						valor_total_parcelas += Decimal( valor_apagar )
						ordem +=1

		elif emissao !=3 and self.p.listaQuan: #-: Recebimento no caixa com emissao do danfe
				
			for dpl in range( self.p.listaQuan ):
					
				duplicata = str( self.p.davNumero )+ "-" + str( self.p.listaRece.GetItem( dpl, 0 ).GetText())
				vencimento = format( datetime.datetime.strptime( str( self.p.listaRece.GetItem( dpl, 1 ).GetText() ), "%d/%m/%Y").date(), '%Y-%m-%d' )
				formapagamento = str( self.p.listaRece.GetItem( dpl, 2 ).GetText() )					
				valor_apagar = str( self.p.listaRece.GetItem( dpl, 3 ).GetText() ).replace(',','')
			
				imprimir = False
				if formapagamento[:2] == "06":	imprimir = True
				if formapagamento[:2] == "07" and len( login.filialLT[ self.filial ][35].split(";") ) >=37 and login.filialLT[ self.filial ][35].split(";")[36] == "T":	imprimir = True	
					
				if imprimir:
					relacao_duplicatas[ordem] = duplicata, vencimento, valor_apagar
					valor_total_parcelas += Decimal( valor_apagar )
					ordem +=1

		return relacao_duplicatas, valor_total_parcelas
		
#---{ Emissao NF }--------------------------// emitente
	def informacoesEmitente(self, filial, emissao ):
		
		unidade_ferederativa = ''

		"""  Dados da filial-emitente  """
		emi_dados = login.filialLT[ filial ][30].split(";")
		emi_telefone = login.filialLT[ filial ][10].split('|')[0].replace(' ','').replace('-','').replace('(','').replace(')','').replace('.','').decode('UTF-8')
		
		emi_razao = login.filialLT[ filial ][1].decode('UTF-8').strip()
		emi_fantasia = login.filialLT[ filial ][14].decode('UTF-8').strip()
		emi_cnpj = login.filialLT[ filial ][9].decode('UTF-8')
		emi_crt = emi_dados[11]
		emi_ie = login.filialLT[ filial ][11]
		emi_im = login.filialLT[ filial ][12]
		emi_cnae = emi_dados[22]
		emi_logradouro = login.filialLT[ filial ][2].decode('UTF-8').strip()
		emi_numero = login.filialLT[ filial ][7].decode('UTF-8').strip()
		emi_complemento = login.filialLT[ filial ][8].decode('UTF-8').strip()
		emi_bairro = login.filialLT[ filial ][3].decode('UTF-8').strip()
		emi_municipio = login.filialLT[ filial ][4].decode('UTF-8').strip()
		emi_cmunicipio = login.filialLT[ filial ][13].decode('UTF-8').strip()
		emi_uf = login.filialLT[ filial ][6].decode('UTF-8').strip()
		emi_cep = login.filialLT[ filial ][5].decode('UTF-8').strip()
		emi_cpais = CODIGO_BRASIL
		
		"""  Alteracao do CRT para RMA  """
		if emissao == 3 and self.p.crTFornecedor.GetValue() and self.p.crTFornecedor.GetValue().split('-')[0] !="RMA":	emi_crt = str( self.p.crTFornecedor.GetValue().split("-")[0] ) #-: RMA-Regime do Fornecedor

		unidade_ferederativa = emi_uf
		emitente = Emitente(
			razao_social=emi_razao,
			nome_fantasia=emi_fantasia,
			cnpj = emi_cnpj,
			codigo_de_regime_tributario = str( emi_crt ),
			inscricao_estadual = emi_ie,
			inscricao_municipal = emi_im,
			cnae_fiscal = emi_cnae,
			endereco_logradouro = emi_logradouro,
			endereco_numero = emi_numero,
			endereco_complemento = emi_complemento,
			endereco_bairro = emi_bairro,
			endereco_municipio = emi_municipio,
			endereco_cod_municipio = emi_cmunicipio,
			endereco_telefone = emi_telefone,
			endereco_uf = str( emi_uf ),
			endereco_cep = emi_cep,
			endereco_pais = emi_cpais
		)
		
		return emitente, unidade_ferederativa

#---{ Emissao NF }--------------------------// Adicionando o cliente
	def informacoesCliente(self, emissao, ambiente, modelo_nf, parent ):

		unidade_ferederativa = ''
		"""  Dados do cliente  """
		cli_dados = cli_endereco = ''
		if modelo_nf == '55':	cli_dados  = self.p.cTClie[0]
		if modelo_nf == '55':	cli_endere = self.p.destinat.GetValue().split('-')[0] #-// Endereco para impressao 1-endereco, 2-endereco

		if modelo_nf == '65' and parent.resul_clientes:	cli_dados = parent.resul_clientes[0]
		if modelo_nf == '65' and parent.resul_clientes:	cli_endere = parent.resul_dav[0][76] #-// Endereco para impressao 1-endereco, 2-endereco
		
		
		cli_pessoa = '1' #-// Pessoa juridica
		cli_tipo_documento = 'CNPJ' #-// Identificacao do documento 'CPF,CNPJ'

		""" { cli_ie_indIEDest } [ Vendas Destinada a fisica-juridica ]
			Indicador da IE do Destinatário, informar:
			1 - Contribuinte ICMS (informar a tag IE do destinatário);
			2 - Contribuinte isento de Inscrição no cadastro de Contribuintes do ICMS - não informar a tag IE;
			9 - Não Contribuinte, que pode ou não possuir Inscrição Estadual no Cadastro de Contribuintes do ICMS - não informar a tag IE.
			Nota 1: No caso de NFC-e informar indIEDest=9 e não informar a tag IE do destinatário;
			Nota 2: No caso de operação com o Exterior informar indIEDest=9 e não informar a tag IE do destinatário;
			Nota 3: No caso de Contribuinte Isento de Inscrição (indIEDest=2), não informar a tag IE do destinatário.
			
			informar a IE do destinatário (somente quando informar a tag indIEDest=1), sem formatação ou máscara
			A tag não aceita mais a literal "ISENTO", assim só informe a Inscrição Estadual, isto é só informe está tag quando informar a tag indIEDest=1.
			Nota: Não informar esta tag no caso da NFC-e.				
			
		"""
		if modelo_nf == '55':	cli_ie_indIEDest = int( self.p.indcadIEst.GetValue().split("-")[0] )
		if modelo_nf == '65':	cli_ie_indIEDest = 9
		endereco_retirar_entregar = []

		cli_codigo = cli_cpfcnpj = cli_fantasia = cli_razao = ''
		
		if emissao == 3: #-// Devolucao de compra RMA
			
			cli_codigo      = cli_dados[0]
			cli_endereco    = cli_dados[8].decode('utf-8').strip()
			cli_numero      = cli_dados[9].decode('utf-8').strip()
			cli_complemento = cli_dados[10].decode('utf-8').strip()
			cli_bairro      = cli_dados[11].decode('utf-8').strip()
			cli_municipio   = cli_dados[12].decode('utf-8').strip()
			cli_cdmunicipio = cli_dados[15].decode('utf-8').strip()
			cli_uf          = cli_dados[14].decode('utf-8').strip()
			cli_cep         = cli_dados[13].decode('utf-8').strip()

			cli_razao    = cli_dados[6].decode('utf-8').strip()
			cli_fantasia = cli_dados[7].decode('utf-8').strip()
			cli_cpfcnpj  = cli_dados[1]
			cli_ie       = cli_dados[2]
			cli_telefone = cli_dados[16].replace(' ','').replace('-','').replace(')','').replace('(','').replace('.','')
			cli_email = ''

			if len( cli_dados[1].strip() ) == 11:	cli_pessoa, cli_tipo_documento = '2', 'CPF'
		else: #-// Cliente vendas enderecos

			enderecamento = True
			if modelo_nf == '65':
				
				"""  Cliente nao identificado { Emissao como consumidor final }  """
				if not parent.resul_clientes or parent.impressao_consumidor.GetValue():	enderecamento = False
				
			if enderecamento:

				"""  cli-Endereco do cliente { Endereco 1,2 ou outros enderecos cadastrados } // loc-Endereco para entrega/retirada { Endereco 2 ou outros enderecos cadastrados }  """
				cli_endereco, cli_numero, cli_complemento, cli_bairro, cli_municipio, cli_cdmunicipio, cli_uf, cli_cep = self.retornarEnderecoEntregaLocal( cli_dados, 1, emissao, cli_endere, modelo_nf )
				loc_endereco, loc_numero, loc_complemento, loc_bairro, loc_municipio, loc_cdmunicipio, loc_uf, loc_cep = self.retornarEnderecoEntregaLocal( cli_dados, 2, emissao, cli_endere, modelo_nf )
				unidade_ferederativa = cli_uf
				
				cli_codigo   = cli_dados[46]
				cli_razao    = cli_dados[1].decode('utf-8').strip()
				cli_fantasia = cli_dados[2].decode('utf-8').strip()
				cli_cpfcnpj  = cli_dados[3]
				cli_ie       = cli_dados[4]
				cli_telefone = cli_dados[17].replace(' ','').replace('-','').replace(')','').replace('(','').replace('.','')
				cli_email    = cli_dados[16].strip()

				if len( cli_dados[3].strip() ) == 11:	 cli_pessoa, cli_tipo_documento = '2', 'CPF'

				"""   Endereco para entregar-retirar  """
				if loc_endereco and loc_bairro  and loc_uf:	endereco_retirar_entregar = loc_endereco, loc_numero, loc_complemento, loc_bairro, loc_municipio, loc_cdmunicipio, loc_uf, loc_cep, cli_tipo_documento, cli_cpfcnpj

		"""  Informacoes do cliente para alimentar o cadastro de nfs no gerenciador de NFs  """
		self.informacoes_clientes_gravacao = cli_codigo, cli_cpfcnpj, cli_fantasia, cli_razao
		if ambiente:	cli_razao = 'NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL'

		"""  Cliente nao identificado  """
		if modelo_nf == '65' and not enderecamento:

			unidade_ferederativa = ''
			cliente = Cliente()
			
		else:

			cliente = Cliente(
				razao_social=cli_razao,
				tipo_documento=cli_tipo_documento,
				email=cli_email,
				numero_documento=cli_cpfcnpj,
				indicador_ie=cli_ie_indIEDest,
				inscricao_estadual = cli_ie,
				endereco_logradouro=cli_endereco,
				endereco_numero=cli_numero,
				endereco_complemento=cli_complemento,
				endereco_bairro=cli_bairro,
				endereco_municipio=cli_municipio,
				endereco_uf=str( cli_uf ),
				endereco_cep=cli_cep,
				endereco_pais=CODIGO_BRASIL,
				endereco_cod_municipio = cli_cdmunicipio,
				endereco_telefone=cli_telefone
			)
		
		return cliente, self.informacoes_clientes_gravacao, cli_pessoa, unidade_ferederativa, endereco_retirar_entregar

	def retornarEnderecoEntregaLocal(self, cli_dados, opcao, emissao, cli_endere, modelo_nf ):
	
		avancar_endereco1 = False
		avancar_endereco2 = False

		if opcao == 1 and modelo_nf == '55' and emissao in [1,2] and self.p.destinat.GetValue().split('-')[0] == "2":	avancar_endereco1 = True
		if opcao == 1 and modelo_nf == '55' and emissao in [1,2] and len( self.p.destinat.GetValue().split('-')[0] ) == 3 and cli_dados[51]:	avancar_endereco2 = True
		
		if opcao == 2 and modelo_nf == '55' and self.p.entregar.GetValue().split('-')[0] == "2":	avancar_endereco1 = True
		if opcao == 2 and modelo_nf == '55' and len( self.p.entregar.GetValue().split('-')[0] ) == 3 and cli_dados[51]:	avancar_endereco2 = True
		
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
		
			endereco_destino = numeros.retornoEndrecos( cli_dados[51], self.p.destinat.GetValue().split('-')[0] )
		
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
		
#---{ Emissao NF }--------------------------// Caculo dos tributos aproximados
	def valorAproximadoTributos( self, produto_geral = 1, ibpt_produto = '', tipo = 'nfe' ):

		if produto_geral == 1:

			total_federal =	total_estadual = total_municipal = total_aproximado = Decimal('0.00')
			if tipo == 'nfe':	registros = ibpt_produto.GetItemCount()
			if tipo == 'nfce':	registros = len( ibpt_produto )
			
			for i in range( registros ):
				
				if tipo == 'nfe':	dados_ibpt = str( ibpt_produto.GetItem( i, 43 ).GetText().strip() )
				if tipo == 'nfce':	dados_ibpt = ibpt_produto[i][94]
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

			return valor_produto_ibpt	

#---{ Emissao NF }--------------------------// Salvando informacoes de emissao, inutitilizacao, cancelamento e rejeicao nas tabelas de controles
	def salvarNotaFiscal( self, emissao = 1, gravacao = 1, dados = '', filial = '' ):

		data_emissao = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
		hora_emissao = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
		data_hora_retorno = datetime.datetime.now().strftime("%d-%m-%Y %T")

		conn = sqldb()
		sql  = conn.dbc("NFE: Gerenciador de nota fiscal", fil = filial, janela = "" )
		if sql[0]:
			
			if gravacao == 1: #--// Gravacao inicial atualiza { cadastro de davs-vendas/devolucao e inserir no controle de nfs os dados do DAV e NF }

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
				
				if emissao != 3:	gravar_dav = "UPDATE cdavs SET cr_nota='"+str( dados[0] )+"',cr_tfat='"+str( dados[2] )+"', cr_tnfs='"+str( dados[3] )+"', cr_seri='"+dados[8]+"' WHERE cr_ndav='"+str( dados[1] )+"'"
				if emissao == 3:	gravar_dav = "UPDATE ccmp  SET cc_numenf='"+str( dados[0] )+"' WHERE cc_contro='"+str( dados[1] )+"'"
				if emissao == 2:	gravar_dav = gravar_dav.replace('cdavs','dcdavs')

				emissao_nfe = str( emissao ) #--/ 1-venda 2-devolucao venda 3-pedido rma
				if dados[2] == '1':	emissao_nfe = '6' #-// Emissao p/Simples Faturamento - Entrega Futura
				if dados[2] == '2':	emissao_nfe = '7' #-// Entrega Futura de Simples Faturamento
				if emissao == 3:	emissao_nfe = '4' #-// Devolucao de compra-RMA

				gerente = "INSERT INTO nfes (nf_nfesce,nf_tipnfe,nf_tipola,nf_envdat,nf_envhor,\
							nf_envusa,nf_numdav,nf_oridav,nf_ambien,nf_idfili,nf_nnotaf,\
							nf_codigc,nf_cpfcnp,nf_fantas,nf_clforn,nf_nserie,nf_vlnota)\
							VALUES(%s,%s,%s,%s,%s,\
								   %s,%s,%s,%s,%s,%s,\
								   %s,%s,%s,%s,%s,%s)"
				
				codigo_cliente, cpf_cnpj, fantasia, nome = dados[10]
				if not nome:	nome = 'consumidor nao identificado'
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
				if emissao != 3:	atualiza_dav = "UPDATE cdavs SET cr_nota='"+ dados[4] +"',cr_chnf='"+ dados[3] +"',cr_nfem='"+str( emi )+"',cr_csta='"+ dados[7] +"' WHERE cr_ndav='"+ dados[0] +"'"
				if emissao == 3:	atualiza_dav = "UPDATE ccmp  SET cc_numenf='"+ dados[4] +"',cc_ndanfe='"+ dados[3] +"',cc_protoc='"+str( emi )+"', cc_nfemis='"+str( dados[2].split('T')[0] )+"', cc_nfdsai='"+str( dados[2].split('T')[0] )+"',cc_nfhesa='"+str( dados[2].split('T')[1][:8] )+"' WHERE cc_contro='"+ dados[0] +"'"
				if emissao == 2:	atualiza_dav = atualiza_dav.replace('cdavs','dcdavs')
				hitorico_retornos = u'SEFAZ Retorno: '+ dados[11] +'\n\n'+ retorno_sefaz_anterior
				if emissao == 3:	hitorico_retornos = u'SEFAZ Retorno: '+ data_hora_retorno +'\n'+ dados[11] +'\n\n'+ retorno_sefaz_anterior
				
				#-// Atualiza no gerenciador de notas
				atualiza_gerenciador = "UPDATE nfes SET nf_tipola='"+ dados[8] +"',nf_retorn='"+ data_hora_retorno +"',nf_rsefaz='"+ hitorico_retornos.replace("'",'') +"',\
				nf_rethor='"+ hora_emissao +"',nf_protoc='"+ dados[1] +"',nf_nchave='"+ dados[3] +"',nf_ncstat='"+ dados[7] +"'\
				WHERE nf_nnotaf='"+ dados[4] +"' and nf_nfesce='"+ dados[5] +"' and nf_oridav='"+ dados[6] +"' and nf_idfili='"+ filial +"' and nf_nserie='"+ dados[12] +"'"

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
				
				if emissao != 3:	sql[2].execute( receber )
				sql[1].commit()
			
			elif gravacao == 3: #-// Rejeicao

				"""  DADOS
					 [0]>-->Numero da NF
					 [1]>-->Numero Serie
					 [2]>-->Origem
					 [3]>-->Nfe ou NFCe
					 [4]>-->Retorno SEFAZ
				"""
			elif gravacao == 4: #--// Cartao de correncao

				danf = dados[0]
				dTar = dados[1]
				xmlc = dados[2] + '[MOT]' + dados[5]
				hist = dados[3]
				xman = dados[4]

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

			conn.cls( sql[1] )
			
	def retornarPagamentos(self, origem_emissao = '160', lista1_pagamentos = '' ):

		"""  Emissao c/Recebimento no caixa  """
		self.listagem_pagamentos = {}
		self.forma_pagamento = {'01':'01', '02':'02', '03':'02', '04':'03',\
						   '05':'04', '06':'15', '07':'99', '08':'99',\
						   '09':'10', '10':'05', '11':'99', '12':'99'}

		separando = ""
		""" 
			Separacao das formas de pagamentos para totalizacao
		"""
		#----// Emissao POS recebimento MNF-Meia nota
		if origem_emissao in ["POS","MNF"]:
 
			if origem_emissao == "POS":	lista = lista1_pagamentos[107].split('|')
        	if origem_emissao == "MNF":	lista = lista1_pagamentos
 
    		for i in lista:
				if i:
					f, v = i.split(';')
					separando +=self.forma_pagamento[f]+';'+str( v )+'|'

		#--// Separando ja ajustando com as formas de pagamento do NFE4.00
		if separando:
			
			for i in separando.split('|'):
				if i:
					f, v = i.split(';')
					valor = self.somatoria( f, separando.split('|') )
					if f not in self.listagem_pagamentos and valor:
						indPag = '1' if f in ['15'] else '0'
						integracao = '2' if f in ['03','04'] else ''
						self.listagem_pagamentos[f] = ( str( valor ), integracao, indPag )

		return self.listagem_pagamentos

	def somatoria(self, f, l ):
    	
		valor = Decimal('0.00')
		for i in l:
			if i.split(';')[0] == f:	valor +=Decimal( i.split(';')[1] )

		return valor

	def partilhaIcmsDifal(self, lista, indice ):

		"""  Partilha do ICMS  """
		base_calculo = str( lista.GetItem( indice, 53 ).GetText().strip()) #----------------------------------------: Valor da BC do ICMS na UF de destino	
		aliquota_fundo = str( lista.GetItem( indice, 54 ).GetText().strip() ) #-------------------------------------: Percentual do ICMS relativo ao Fundo de Combate à Pobreza (FCP) na UF de destino
		aliquota_destino = str( format( Decimal( lista.GetItem( indice, 55 ).GetText().strip() ),'.2f' ) ) #--------: Alíquota interna da UF de destino
		aliquota_inter_estadual = str( format( Decimal( lista.GetItem( indice, 56 ).GetText().strip() ),'.2f' ) ) #-: Alíquota interestadual das UF envolvidas
		aliquota_provisoria = str( format( Decimal( lista.GetItem( indice, 57 ).GetText().strip() ),'.2f' ) ) #-----: Percentual provisório de partilha do ICMS Interestadual
		valor_icms_fundo = str( lista.GetItem( indice, 58 ).GetText().strip() ) #-----------------------------------: Valor do ICMS relativo ao Fundo de Combate à Pobreza (FCP) da UF de destino
		valor_icms_destino = str( lista.GetItem( indice, 59 ).GetText().strip() ) #---------------------------------: Valor do ICMS Interestadual para a UF de destino
		valor_icms_origem = str( lista.GetItem( indice, 60 ).GetText().strip() ) #----------------------------------: Valor do ICMS Interestadual para a UF do remetente

		saida_retorno = base_calculo, aliquota_fundo, aliquota_destino, aliquota_inter_estadual, aliquota_provisoria, valor_icms_fundo, valor_icms_destino, valor_icms_origem
		
		return saida_retorno

#-----------------------------------------------------------------------#
#                       Emissao NFCe 4.00                               #
#-----------------------------------------------------------------------#
class EmissaNfce400:
	
	def emitirNfce400( self, parent, numero_dav, modulo_emissao ):

		emissao = 1 #--// Nota fiscal de vendas 
		self.p = parent
		self.filial = self.p.efilial
		
		rtn, snh, cer, sis, sie, amb, uf, fus, __cnpj, __nfce, regime_tributario = informes.certificados( self.filial, self.p )
		numero_serie, id_csc, numero_csc = __nfce

		emissaoNfe400  = EmissaoNotasFiscais()
		dados_emitente, unidade_federativa = emissaoNfe400.informacoesEmitente( self.filial, emissao )
		dados_cliente, informacoes_clientes_gravacao, pessoa_juridica_fisica, unidade_federativa, endereco_entregar_retirar = emissaoNfe400.informacoesCliente( 1, amb, '65', parent )
		rT, nfis = numeros.VerificaNFE( numero_dav, Tnf = 1, Filial = self.filial )
		if rT == False:	nfis = numeros.numero("15","Numero da NFCe",parent, self.filial )

		if nfis == '':

			alertas.dia(self.p,u"Numero de NFe não foi gerado, Tente novamente!!\n"+(" "*110),u"Emissão de NFes")
			return

		"""  Incluir nas tabelas>--> cdavs, dcdavs, nfes """
		nfe_nfce = '2'
		origem   = '1'
		ambiente = '2' if amb else '1'
		emissao  = 1 #--// 1-Vendas, 2-devolucal de vendas, 3- RMA
		
		valor_nota = str( self.p.resul_dav[0][37] )
		inutilizar = '2'
		remessa_simples_faturamento = ''

		"""  Incluir nas tabelas>--> cdavs, dcdavs, nfes """
		if not rT:

			gravar_gerenciador = str( nfis ), numero_dav, remessa_simples_faturamento, nfe_nfce, inutilizar, origem, ambiente, self.filial, numero_serie, valor_nota, informacoes_clientes_gravacao, remessa_simples_faturamento
			emissaoNfe400.salvarNotaFiscal( emissao = emissao, gravacao = 1, dados = gravar_gerenciador )

		__f = self.filial.lower()
		__n = datetime.datetime.now().strftime("%m-%Y") +'/'+ str( numero_serie ).zfill(3)+'-'+str( nfis ).zfill(9)
		__d = diretorios.nfceacb+"nfce400/"+__f+"/homologacao/"+ __n if amb else diretorios.nfceacb+"nfce400/"+__f+"/producao/"+ __n
		if os.path.exists( __d ) == False:	os.makedirs( __d )

		""" Tributos municipais, estaduais, federais, FONTE: IBPT """
		ibpt_federal, ibpt_estadual, ibpt_municipal, ibpt_valortotal = emissaoNfe400.valorAproximadoTributos( produto_geral = 1, ibpt_produto = self.p.resul_items, tipo = 'nfce' )
		if modulo_emissao == 1:	lista_pagamentos = emissaoNfe400.retornarPagamentos( origem_emissao = '160', lista1_pagamentos = self.p.r )
		if modulo_emissao == 2:	lista_pagamentos = emissaoNfe400.retornarPagamentos( origem_emissao = 'POS', lista1_pagamentos = self.p.resul_dav[0] )
		if self.p.meian.GetValue():	lista_pagamentos = emissaoNfe400.retornarPagamentos( origem_emissao = 'MNF', lista1_pagamentos = self.p.forma_pagamentos ) #--// Meia nf { Ajusta para priorizar o cartao }

		"""  Identificacao da nota fiscal  """
		nota_fiscal = NotaFiscal(
		   emitente = dados_emitente,
		   cliente = dados_cliente,
		   uf = uf.upper(),
		   natureza_operacao = 'VENDA', # venda, compra, transferência, devolução, etc
		   forma_pagamento = 0,         # 0=Pagamento à vista; 1=Pagamento a prazo; 2=Outros.
		   tipo_pagamento = 1,
		   modelo = 65,                 # 55=NF-e; 65=NFC-e
		   serie = str( numero_serie ),
		   numero_nf = str( nfis ),           # Número do Documento Fiscal.
		   data_emissao = datetime.datetime.now(),
		   data_saida_entrada = datetime.datetime.now(),
		   tipo_documento = 1,  # 0=entrada; 1=saida
		   municipio = login.filialLT[ self.filial ][13],       # Código IBGE do Município 
		   tipo_impressao_danfe = 4,    # 0=Sem geração de DANFE;1=DANFE normal, Retrato;2=DANFE normal Paisagem;3=DANFE Simplificado;4=DANFE NFC-e;
		   forma_emissao = '1',         # 1=Emissão normal (não em contingência);
		   cliente_final = 1,           # 0=Normal;1=Consumidor final;
		   indicador_destino = 1,       # 1-Operacao interna, 2-interEstadual, 3-Exterior
		   indicador_presencial = 1,    # 1-Precensial, 2-pela internet, 3-tele adtendimento, 4-NFCe entrega em domicilio
		   finalidade_emissao = '1',    # 1-normal, 2-complementar, 3-ajuste, 4-Devolução
		   processo_emissao = '0',      #0=Emissão de NF-e com aplicativo do contribuinte;
		   transporte_modalidade_frete = 9, # 9=Sem Ocorrência de Transporte.
		   informacoes_adicionais_interesse_fisco = '',
		   totais_tributos_aproximado = Decimal( ibpt_valortotal ),
		   totais_icms_total_nota = self.p.resul_dav[0][37],
		   pagamentos_formas_pagamentos = lista_pagamentos,
		   pagamentos_troco = '',
		)

		numero_item_nf = 1

		conn = sqldb()
		sql  = conn.dbc("Caixa: Consulta de Items do DAVs", fil =  self.filial, janela = self.p )
		
		if sql[0]:
				
			for i in self.p.resul_items:

				#-// Tributos municipais, estaduais, federais, FONTE: IBPT
				valor_produto_ibpt = emissaoNfe400.valorAproximadoTributos( produto_geral = 2, ibpt_produto = str( i[94] ), tipo = 'nfce' )

				modalidade_base_calculo = '3'
				icms_valor_base_calculo = i[34]
				icms_aliquota = i[29]
				icms_valor = i[39]

				icms_40valor_desoneracao = Decimal('0.00')
				icms_40motivo_desoneracao = ''
				
				cst_origem = int( i[58][:1].strip() )
				cst_csosn  = i[58][1:].strip() if regime_tributario == '1' else str( int( i[58][1:] ) ).zfill(2)
				"""  Troca os codigos fiscais  se for regime normal, passa a utilizar o codigo fiscal da nfce no cadastro de produtos   """
				if sql[2].execute("SELECT pd_cfir,pd_cest,pd_para FROM produtos WHERE pd_codi='"+ i[5] +"'"):
						
					cfs = sql[2].fetchone()
					ces = cfs[1]

				if amb and numero_item_nf == 1:	nome_produto = 'NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL'
				else:	nome_produto = i[7].strip()
				"""  Dados adicionais para o prdotuo { Nao aceita quebra de linha [ a quebra de linha da erro shema ] }"""
				numero_serie = "No.Serie: "+i[98].replace('|','') if i[98] else ''
				dados_adicionais_produto = numero_serie.strip()
				
				nota_fiscal.adicionar_produto_servico(
					codigo = i[5],                           # id do produto
					descricao = nome_produto,
					ean = i[6],
					ean_tributavel = i[6],
					ncm = i[56].strip(),
					cest = ces.strip(),
					cfop = i[57],
					unidade_comercial = i[8],
					quantidade_comercial = i[12],        # 12 unidades
					valor_unitario_comercial = i[11],  # preço unitário
					valor_total_bruto = i[13],       # preço total
					unidade_tributavel = i[8],
					quantidade_tributavel = i[12],
					valor_unitario_tributavel = i[11],
					desconto = i[28],
					outras_despesas_acessorias = ( i[27] + i[26] ),
					ind_total=1,
					numero_item = str( numero_item_nf ),                    # nItemPed
					icms_modalidade = str( int( i[58] ) ).zfill(2),
					icms_origem = cst_origem,
					icms_csosn = str( int( cst_csosn ) ),
					icms_modalidade_determinacao_bc = modalidade_base_calculo,
					icms_valor_base_calculo = icms_valor_base_calculo,
					icms_aliquota = icms_aliquota, #-// ICMSSN, pCredSN
					icms_valor = icms_valor,
					icms_valor_base_retido_fonte_st = Decimal('0.00'),
					icms_valor_icms_st_retido = Decimal('0.00'),
					icms_percentual_fcp = Decimal('0.00'),
					icms_valor_base_calculo_fcp_retido = Decimal('0.00'),
					icms_percentual_fcp_retido = Decimal('0.00'),
					icms_valor_fcp_retido = Decimal('0.00'),
					icms_40valor_desoneracao = icms_40valor_desoneracao,
					icms_40valor_desoneracao_motivo = icms_40motivo_desoneracao,
					pis_modalidade='06',
					cofins_modalidade='06',
					informacoes_adicionais_produto = dados_adicionais_produto,
					valor_tributos_aprox = valor_produto_ibpt,
					
					)

				numero_item_nf +=1
				
			conn.cls( sql[1] )

			# serialização
			serializador = SerializacaoXML( _fonte_dados, homologacao = amb )
			nfce = serializador.exportar()

			# assinatura
			a1 = AssinaturaA1( cer, snh)
			xml = a1.assinar(nfce)
			xml_com_qrcode = SerializacaoQrcode().gerar_qrcode( id_csc, numero_csc, xml)

			con = ComunicacaoSefaz(uf, cer, snh, amb)
			envio = con.autorizacao(modelo='nfce', nota_fiscal=xml_com_qrcode)

			"""  Nota fiscal autorizada  """
			if envio[0] == 0:

				xml_autorizado = etree.tostring(envio[1], encoding="unicode").replace('\n','').replace('ns0:','')
				rt = informes.retornosSefaz( xml_autorizado, ["protNFe","retEnviNFe"], parent, nome_evento = 'EMISSAO' )
				
				lerXml = DadosCertificadoRetornos()
				docxml = minidom.parseString( xml_autorizado )
				
				numero_nf = lerXml.leituraXml( docxml, 'infNFe', 'nNF' )[0][0]
				numero_serie = lerXml.leituraXml( docxml, 'infNFe', 'serie' )[0][0]
				
				csTaT = lerXml.leituraXml( docxml, 'protNFe', 'cStat' )[0][0]
				chave = lerXml.leituraXml( docxml, 'protNFe', 'chNFe' )[0][0]
				protocolo = lerXml.leituraXml( docxml, 'protNFe', 'nProt' )[0][0]
				data_recebimento = lerXml.leituraXml( docxml, 'protNFe', 'dhRecbto' )[0][0]

				"""  Emissao da nfe com recebimento no caixa """
				if modulo_emissao == 1:	self.p.p.fechamento( "160", str( nfis ), filial = self.filial )
				nfe_emissao = '1' #--// Emissao { TipoLancamento: 1 - Emissao, 2 - ParaInutilizar, 3 - Cancelamento, 4 - Inutilizadas, 5 - Denegada }


				"""  Atualizar dados nas tabelas cdavs, ocorrencia, receber, nfes, sefazxml  """
				gravar_gerenciador = numero_dav, protocolo, data_recebimento, chave, numero_nf, nfe_nfce, origem, csTaT, nfe_emissao, __d, xml_autorizado, rt[1], numero_serie
				emissaoNfe400.salvarNotaFiscal( emissao = emissao, gravacao = 2, dados = gravar_gerenciador, filial = self.filial )

				modulos_nfe = 2 #--// Opcao para habilitar os icones e alternar a cor de fundo { 1-status, 2-emissao, 3-erro na emissao }
				if xml_autorizado:

					__arquivo = open( __d  +'/'+ rt[3] +"-nfce.xml", "w" )
					__arquivo.write( xml_autorizado )
					__arquivo.close()
				
				self.p.historico_sefaz.SetValue( rt[1] )

				self.p.historico_sefaz.SetBackgroundColour('#1A1A1A')
				self.p.historico_sefaz.SetForegroundColour('#87B5E1')

				"""  Habilita e impressao p/manulal e se automatico estiver habilitado imprimi direto  """
				self.p.fechamento_total = True
				self.p.numero_chave = chave	
				self.p.abilitarEnvioImpressao()
				
			else: #--// Rejeicao

				"""  Atualizar dados nas tabelas cdavs, ocorrencia, receber, nfes, sefazxml  """
				rt = informes.retornosSefaz( envio[1].text, ["protNFe","retEnviNFe"], parent, nome_evento = 'EMISSAO' )

				"""  Carrega o XML original para ser analisado posteriormente  """
				__xml = etree.tostring(xml, encoding="unicode") #.replace('\n','').replace('ns0:','')

				modulos_nfe = 3 #--// Opcao para habilitar os icones e alternar a cor de fundo { 1-status, 2-emissao, 3-erro na emissao }
				if rt[0]:

					self.p.historico_sefaz.SetValue( rt[1] )
					
					self.p.historico_sefaz.SetBackgroundColour("#976868")
					self.p.historico_sefaz.SetForegroundColour("#E7E7E7")

					arquivo_retorno = __d + "/retorno.xml"
					erro = 'original_assinado_erro_normal.xml'
					if rt[4] in ['225']: 
						
						erro = 'original_assinado_erro_shema.xml'
						arquivo_retorno = __d + '/' + erro
						
					_arquivo = open( __d + "/retorno.xml", "w" )
					_arquivo.write( envio[1].text )
					_arquivo.close()

					"""  Grava o XML original para analisar posteriormente  """
					_arquivo = open( __d + '/' + erro, "w" )
					_arquivo.write( __xml )
					_arquivo.close()

					informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], modulos_nfe, '65', rt[4], __xml, self.filial, arquivo_retorno, '' )


class VisualizarRetornos(wx.Frame):

#---{ Visualizacao de Retorno do SEFAZ }--------------------------// Construtor
	def __init__(self, parent, id, inf, rt, md, modelo, csTaT, string_xml, filial, file_xml, emails ):

		""" MD - Modulo
			1-Eventos status, inutilizacao, cancelamento
			2-Emissao
			3-Erro na emissao
		"""
		self.p = parent
		self.s = csTaT
		self.x = string_xml
		self.f = filial

		self.xml_file = file_xml
		self.emails   = emails.strip()

		tipo_nota = "65 - NFCe" if str( modelo ) == "65" else "55 - NFe"
		wx.Frame.__init__(self,parent,id, "Retorno da SEFAZ { "+tipo_nota+" NF-4.0 Filial: "+self.f+" }",size=(900,500),style=wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX|wx.CAPTION)
		self.painel = wx.Panel(self,wx.NewId(),style=wx.SUNKEN_BORDER)

		self.Bind(wx.EVT_CLOSE, self.sair)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		self.saida_infomacoes = wx.TextCtrl(self.painel, value='', pos=(40,2), size=(855,390),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.saida_infomacoes.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.enviar_email_automatico = wx.TextCtrl(self.painel, value='', pos=(0,400), size=(895,90),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.enviar_email_automatico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.enviar_email_automatico.SetBackgroundColour("#B9C4CF")
		self.enviar_email_automatico.SetForegroundColour('#002B56' if emails else '#B99292')
		self.enviar_email_automatico.SetValue(u'Envio automático de email' if emails else u'Envio automático de email\nCliente sem email cadastrado')

		self.saida_infomacoes.SetBackgroundColour("#4D4D4D")
		self.saida_infomacoes.SetForegroundColour('#90EE90')
		self.saida_infomacoes.SetValue( "{ Retorno da SEFAZ [ "+ tipo_nota+" ] }\n"+ inf )

		self.impressao = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/printing20.png",   wx.BITMAP_TYPE_ANY), pos=(2,2), size=(34,34))				
		self.visualizar_xml = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/xml224.png",   wx.BITMAP_TYPE_ANY), pos=(2,42), size=(34,34))				
		self.sair_visualizador = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/sair24.png",   wx.BITMAP_TYPE_ANY), pos=(2,122), size=(34,34))				
		
		if csTaT in ['100','107','102','135','573']:

			self.saida_infomacoes.SetBackgroundColour("#1D5083")
			self.saida_infomacoes.SetForegroundColour('#FFFFFF')
			self.saida_infomacoes.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD))

		if md == 3: #--// Erro na emissao

			self.saida_infomacoes.SetBackgroundColour("#B76666")
			self.saida_infomacoes.SetForegroundColour('#FFFFFF')
			self.saida_infomacoes.SetValue( "{ Retorno da SEFAZ [ "+ tipo_nota+" ] }\n"+ inf )

		libera_icones = True if md in [2] else False
		if not self.x:	libera_icones = False
		self.impressao.Enable( libera_icones )
		self.visualizar_xml.Enable( libera_icones )
		
		"""  Se existir XML Habilita para visualizar  """
		if string_xml:	self.visualizar_xml.Enable( True )

		"""  Envio automatico de emails  """
		sr, us, re, ps, pr = login.filialLT[self.f][29].split(';')
		if   len( login.filialLT[ self.f ][35].split(";") ) >= 100 and login.filialLT[ self.f ][35].split(";")[99] == 'T':	self.enviar_email_automatico.SetValue(u'Envio automático de email\nFilial configurada para nao enviar email automaticamente...')
		elif not emails:	self.enviar_email_automatico.SetValue(u'Envio automático de email\nCliente sem email cadastrado para envio automatico...')
		else:
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

#---{ Visualizacao de Retorno do SEFAZ }--------------------------// Sair
	def sair(self,event):
		
		if self.s in ['100']:	self.p.sair(wx.EVT_BUTTON)
		else:	self.Destroy()
	
#---{ Visualizacao de Retorno do SEFAZ }--------------------------// Gerar DANFE
	def gerarDanfe(self,event):

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
		MostrarHistorico.GD = montar_danfe 

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
		dc.DrawRotatedText(u"Visualizador de retornos SEFAZ", 22, 390, 90)

class LerHtml(wx.Frame):

    def __init__(self, parent, id , inf ):

		wx.Frame.__init__(self,parent,id, "Retorno da SEFAZ { HTML }",size=(900,500),style=wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX|wx.CAPTION)
		self.painel = wx.Panel(self,wx.NewId(),style=wx.SUNKEN_BORDER)

		self.html = html.HtmlWindow(self.painel, -1, size=(900, 500), style=wx.VSCROLL|wx.HSCROLL|wx.TE_READONLY|wx.BORDER_SIMPLE)
		self.html.SetPage( inf )


"""  Instanciamento  """
informes = DadosCertificadoRetornos()
