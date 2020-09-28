#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------------#
# Integracao com alerta fiscal { Sergil [ usando para o desenvolvimento e teste] } #
# Jose de Almeida Lobinho 09/08/2020                                               #
#----------------------------------------------------------------------------------#
import requests
import xml.dom.minidom
from lxml import etree
from collections import OrderedDict
from .__init__ import *
from danfepdf  import danfeGerar

from datetime import datetime,timedelta
from conectar import login,sqldb,dialogos,menssagem

geraPDF = danfeGerar()
alertas = dialogos()
mens = menssagem()

class ConfeccaoXxmlAlerta:
    
    def preencherTags(self,parente,filial, tags={}, incluir=False):

	self.p = parente
	
	""" Dados de conexao """
	self.rfilial = filial
	id_usuario = self.p.consumersecret
	token = self.p.consumerkey
	url_producao = self.p.urlconexao
	url_homologacao = self.p.urlconexao1 
	url = url_producao if self.p.homologacao=='F' else url_homologacao
	
	""" 
		Solicitacao de cadastro
		URL de Acesso ao ambiente de Produção/Homologação
	"""
	if incluir:
	    if self.p.homologacao=='F':	url = "http://soap.alertafiscalintranet.com.br/WsSolicitacaoCadastro.asmx?wsdl"
	    else:	url = "http://homologacao.soap.alertafiscalintranet.com.br/WsSolicitacaoCadastro.asmx?wsdl"
	"""--------------------------------------------------------------------"""

	data_padrao = "0001-01-01T00:00:00.000-00:00"
	estado_filial = login.filialLT[filial][30].split(";")[12] if len(login.filialLT[filial][30].split(";"))>=13 else ""
	
	data_filtro = tags['data']
	codigo = tags['codigo']
	id_event = tags['opcao']
	self.indice = tags['indice']
	
	data = data_padrao if id_event==101 and codigo else data_filtro
	if id_event in [102,105]:	data = data_padrao

	_mensagem = mens.showmsg("Enviando solicitacao ao servidor alerta fiscal\n\nAguarde...")
		
	raiz = etree.Element('{%s}Envelope' % NAMESPACES['SOAP'], nsmap={'xsi': NAMESPACES['XSI'], 'xsd': NAMESPACES['XSD'], 'soap': NAMESPACES['SOAP']})
	head = etree.SubElement(raiz,'{%s}Header' % NAMESPACES['SOAP'])
	body = etree.SubElement(raiz,'{%s}Body' % NAMESPACES['SOAP'])
	validation = etree.SubElement(head, 'ValidationSoapHeader', XmlAttribute="", xmlns="http://soap.alertafiscalintranet.com.br")
	etree.SubElement(validation,'Id').text=id_usuario
	etree.SubElement(validation,'Token').text=token
	
	"""  Solicitacao para incluir um produto """
	if incluir:
	    
	    codigo = tags['codigo']
	    barras = tags['barras']
	    dsnome = tags['nome']
	    unidad = tags['unidade']
	    
	    inclusao = etree.SubElement(body, 'SolicitarCadastroProduto', xmlns="http://soap.alertafiscalintranet.com.br")
	    if barras:	etree.SubElement(inclusao,'Ean').text=barras
	    else:	etree.SubElement(inclusao,'Ean')
	    
	    etree.SubElement(inclusao,'DescricaoCompleta').text=dsnome
	    etree.SubElement(inclusao,'MarcaProduto')
	    etree.SubElement(inclusao,'DetalheProduto')
	    etree.SubElement(inclusao,'ConteudoProduto')
	    etree.SubElement(inclusao,'MedidaProduto')
	    etree.SubElement(inclusao,'ProdutoImportado').text='false'
	    etree.SubElement(inclusao,'CodigoInterno').text=codigo

	else:
	    """
		Consultas
		Lista os produtos atualizados da filial
	    """
	    #if codigo:	consulta = etree.SubElement(body, 'ConsultarTributacoes'+estado_filial.upper()+'Final', xmlns="http://soap.alertafiscalintranet.com.br")
	    if codigo:	consulta = etree.SubElement(body, 'ConsultarTributacoes'+estado_filial.upper(), xmlns="http://soap.alertafiscalintranet.com.br")
	    else:	consulta = etree.SubElement(body, 'ConsultarCodigosInternosAtualizados', xmlns="http://soap.alertafiscalintranet.com.br")
	    obconsulta = etree.SubElement(consulta,'objConsulta')

	    etree.SubElement(obconsulta,'Id').text='0'
	    etree.SubElement(obconsulta,'Token')
	    etree.SubElement(obconsulta,'Ean')
	    etree.SubElement(obconsulta,'Ncm')
	    
	    if codigo:	etree.SubElement(obconsulta,'CodigoInterno').text=codigo
	    else:	etree.SubElement(obconsulta,'CodigoInterno')
	    etree.SubElement(obconsulta,'DataFiltro').text=data
	
	string = DECLARACAO_XML + etree.tostring(raiz, encoding="unicode").replace('ns0:','').replace(':ns0','').replace('\n','')
	
	#print string
	#print("-"*100)
	
	doc = xml.dom.minidom.parseString( string )
	docTree = doc.toprettyxml()
	
	#print 'URL Passada: ',url
	#print("-"*100)
	#print docTree
	
	""" Request POST """
	result = requests.post(url, string, headers=POST_HEADER, verify=True)
	del _mensagem

	docReturn = result.content
	docRead = xml.dom.minidom.parseString( docReturn )
	
	if result.status_code==200:
	    if id_event==101: 

		codigos_retornados, __id = geraPDF.XMLLeitura( docRead, "ConsultarCodigosInternosAtualizadosResult","CodigosInternos")
		data_solicitacao, __id = geraPDF.XMLLeitura( docRead, "ConsultarCodigosInternosAtualizadosResult","DataSolicitacao")

		if codigos_retornados[0]:
		    self.listarCodigosAlterados( sorted(codigos_retornados[0].split(';')) )
		    return True,'',''

	    elif id_event==102:	
		return self.adicionarProdutosAlteracao(docRead, id_event)

	    elif id_event==105: #//-[ Pesquisa pelo codigo digitado ]
		self.listarCodigosAlterados( [codigo] )
		self.indice = ( self.p.lista_codigos_alterados.GetItemCount()-1 )
		return self.adicionarProdutosAlteracao(docRead, id_event)

	    elif id_event==106: #//-[ Incluindo item na lista ]
		inclusao, __id = geraPDF.XMLLeitura( docRead, "SolicitarCadastroProdutoResponse","SolicitarCadastroProdutoResult")
		if inclusao[0].upper()=='TRUE':	alertas.dia(parente,u"Status do servidor alerta-fiscal { "+str(result.status_code)+ u" }\n\nSolicitação de cadastro, Aprovada..\n"+(' '*200),u'Solicitação de cadastro')
		return True,'',''

	elif result.status_code!=200:
	    
	    erros, __id = geraPDF.XMLLeitura( docRead, "soap:Reason","soap:Text")
	    alertas.dia(parente,u"Status do servidor alerta-fiscal { "+str(result.status_code)+" }\n\n"+ erros[0] +'\n'+(' '*200),u'Retorno de consutla')
	    saida = ''
	    if 'LIMITE' in erros[0].upper():	saida='LIMITE'
	    return False, saida, ''

    def adicionarProdutosAlteracao(self,docRead,id_event):
	
	ncm, __id1 = geraPDF.XMLLeitura( docRead, "Detalhamento","Ncm")
	categoria, __id2 = geraPDF.XMLLeitura( docRead, "Detalhamento","NomeCategoriaProduto")
	lei, __id4 = geraPDF.XMLLeitura( docRead, "IcmsInterno","IcmsInternoEmbasamentoLei")
	
	icms_cfcp,__id3 = geraPDF.XMLLeitura( docRead, "Saida","IcmsSaidaConsumidorFinal") #//--------[ SEM FCP ]
	icms_sfcp,__id3 = geraPDF.XMLLeitura( docRead, "Saida","IcmsSaidaConsumidorFinalSemFecp") #//-[ COM FCP ]
	fcp, __id3 = geraPDF.XMLLeitura( docRead, "Saida","FecpConsumidorFinal")
	
	cst, __id5 = geraPDF.XMLLeitura( docRead, "Saida","CodigoCstIcmsSaidaConsumidorFinal")
	cest,__id6 = geraPDF.XMLLeitura( docRead, "Saida","CodigoCest")
	descricao_cest,__id7 = geraPDF.XMLLeitura( docRead, "Saida","DescricaoCest")
	
	cosn,__id8 = geraPDF.XMLLeitura( docRead, "Saida","CodigoCsosn")
	cfop,__id9 = geraPDF.XMLLeitura( docRead, "Saida","CodigoCfopSaida")
	beneficiamento, __id10 = geraPDF.XMLLeitura( docRead, "Saida","CodigoBeneficioConsumidorFinal")

	codigopis_cofins,__id11 = geraPDF.XMLLeitura( docRead, "Federal","CodigoCstPisCofinsSaida")
	PisSaida,__id12 = geraPDF.XMLLeitura( docRead, "Federal","PisSaida")
	CofinsSaida,__id13 = geraPDF.XMLLeitura( docRead, "Federal","CofinsSaida")

	codigo_produto=self.p.lista_codigos_alterados.GetItem(self.indice,1).GetText() if self.p.lista_codigos_alterados.GetItemCount() else ""
	id_produto=self.p.lista_codigos_alterados.GetItem(self.indice,3).GetText() if self.p.lista_codigos_alterados.GetItemCount() else ""
	descricao=self.p.lista_codigos_alterados.GetItem(self.indice,4).GetText() if self.p.lista_codigos_alterados.GetItemCount() else ""
	status=self.p.lista_codigos_alterados.GetItem(self.indice,2).GetText() if self.p.lista_codigos_alterados.GetItemCount() else ""
	
	ordem = self.p.lista_produtos.GetItemCount()
	
	self.p.lista_produtos.InsertStringItem( ordem, str(ordem+1).zfill(3) )
	self.p.lista_produtos.SetStringItem(ordem,1, codigo_produto )
	self.p.lista_produtos.SetStringItem(ordem,2, status )
	self.p.lista_produtos.SetStringItem(ordem,3, descricao )

	self.p.lista_produtos.SetStringItem(ordem,4, ncm[0] )
	self.p.lista_produtos.SetStringItem(ordem,5, cfop[0] )
	self.p.lista_produtos.SetStringItem(ordem,6, cosn[0] )
	self.p.lista_produtos.SetStringItem(ordem,7, cst[0] )
	self.p.lista_produtos.SetStringItem(ordem,8, icms_sfcp[0] )

	self.p.lista_produtos.SetStringItem(ordem,9, icms_cfcp[0] )
	self.p.lista_produtos.SetStringItem(ordem,10,fcp[0] )

	self.p.lista_produtos.SetStringItem(ordem,11, cest[0] )
	self.p.lista_produtos.SetStringItem(ordem,12,beneficiamento[0] )
	self.p.lista_produtos.SetStringItem(ordem,13,codigopis_cofins[0] )
	self.p.lista_produtos.SetStringItem(ordem,14,codigopis_cofins[0] )
	self.p.lista_produtos.SetStringItem(ordem,15,PisSaida[0] )
	self.p.lista_produtos.SetStringItem(ordem,16,CofinsSaida[0] )

	self.p.lista_produtos.SetStringItem(ordem,30,fcp[0] )

	self.p.lista_produtos.SetStringItem(ordem,31,lei[0] )
	self.p.lista_produtos.SetStringItem(ordem,32,categoria[0] )
	self.p.lista_produtos.SetStringItem(ordem,33,descricao_cest[0] )
	
	if ordem % 2:	self.p.lista_produtos.SetItemBackgroundColour(ordem, "#D4F4D4")
	return True, ordem, self.indice
	
    def listarCodigosAlterados(self,lista):

	conn = sqldb()
	sql  = conn.dbc("Verificando vinculos de produtos", fil = self.rfilial, janela = self )

	if sql[0]:
	
	    self.p.lista_codigos_alterados.DeleteAllItems()
	    self.p.lista_codigos_alterados.Refresh()
	    data_ultima_atualizacao=datetime.strptime(self.p.dinicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
	    
	    self.p.lista_codigos_alterados_futuro={}
	    ordem = 0
	    ordem1 =0

	    for i in lista:
		
		codigo_localizado = "OK" if sql[2].execute("SELECT pd_regi,pd_codi,pd_nome,pd_afat FROM produtos WHERE pd_codi='"+ i +"'") else "Nao localizado"
		if codigo_localizado!="OK":
		    codigo_localizado = "OK" if sql[2].execute("SELECT pd_regi,pd_codi,pd_nome,pd_afat FROM produtos WHERE pd_codi='"+ i.zfill(14) +"'") else "Nao localizado"
		
		if codigo_localizado=="OK":	reg, cod, nom, dat = sql[2].fetchone()
		else:	reg= cod= nom= dat = str()

		produto_atulizado = 'OK' if str(data_ultima_atualizacao).strip()==str(dat.strip()) else ''
		
		avancar = False if not self.p.nao_sair_codigos_atualizados.GetValue() and produto_atulizado=='OK' else True
		if avancar:

		    self.p.lista_codigos_alterados.InsertStringItem( ordem, str(ordem+1).zfill(3) )
		    self.p.lista_codigos_alterados.SetStringItem(ordem,1, i )
		    self.p.lista_codigos_alterados.SetStringItem(ordem,2, codigo_localizado )
		    self.p.lista_codigos_alterados.SetStringItem(ordem,3, str(reg) )
		    self.p.lista_codigos_alterados.SetStringItem(ordem,4, nom )
		    self.p.lista_codigos_alterados.SetStringItem(ordem,5, dat )
		    """ Marcar para nao atualizar """
		    if produto_atulizado=='OK':	self.p.lista_codigos_alterados.SetStringItem(ordem,6, 'OK' )

		    if ordem % 2:	self.p.lista_codigos_alterados.SetItemBackgroundColour(ordem, "#92B892")
		    if codigo_localizado!="OK":	self.p.lista_codigos_alterados.SetItemBackgroundColour(ordem, "#E3D3D6")
		    if produto_atulizado=='OK':	self.p.lista_codigos_alterados.SetItemBackgroundColour(ordem, "#E5E5E5")
		    ordem +=1
		
		self.p.lista_codigos_alterados_futuro[ordem1]=i,codigo_localizado,str(reg),nom,dat,produto_atulizado
		ordem1 +=1
