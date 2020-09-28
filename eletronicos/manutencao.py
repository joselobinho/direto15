#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tempfile
import re
import os
import requests
import datetime
import hashlib
import warnings
import time
from json import dumps

from conectar import login,diretorios
from signxml import XMLSigner,methods,XMLVerifier
from OpenSSL import crypto
from lxml import etree
from xml.dom import minidom
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .__init__ import *

class ManutencaoSefaz:

    def statusNFs(self, tags ):

#----// MDFe
	if nf.modelo=='58':
	    raiz = etree.Element('consStatServMDFe', versao=nf.versao, xmlns=MDFENAMESPACES['MDFE'])
	    for i in tags: etree.SubElement( raiz, i ).text=tags[i] #--// Adicionando dinamicamente tags no XML

	    return ev.envio_post( self.url('MDFeStatusServico',''), cb.cabecalho('MDFeStatusServico', raiz, ''), False, None )

#----// NFe, NFCe
	else:
	    NotaFiscalParametros.metodo = 'status_' + datetime.datetime.now().strftime("%d%m%Y%T").replace(':','')
	    raiz = etree.Element('consStatServ', versao=nf.versao, xmlns=NAMESPACES['NFE'])
	    for i in tags: etree.SubElement( raiz, i ).text=tags[i] #--// Adicionando dinamicamente tags no XML

	    return ev.envio_post( self.url('STATUS',''), cb.cabecalho('NFeStatusServico4', raiz, ''), False, None )

    def consultaCadastro(self,tags):

        raiz = etree.Element('ConsCad', versao='2.00', xmlns=NAMESPACES['NFE'])
        cons = etree.SubElement(raiz, 'infCons')

        for i in tags:  etree.SubElement(cons, i ).text = tags[i] #--// Adicionando dinamicamente tags no XML
        return ev.envio_post( self.url('CADASTRO',''), cb.cabecalho('CadConsultaCadastro4', raiz, ''), False, None )

    def inutilizacao(self, tags ):

        NotaFiscalParametros.metodo = 'inutilizacao_' + datetime.datetime.now().strftime("%d%m%Y%T").replace(':','')

        identificacao = 'ID' + tags['cUF'] + tags['ano'] + cnpjNumeros(tags['CNPJ']) + tags['mod'] + tags['serie'].zfill(3) + tags['nNFIni'].zfill(9) + tags['nNFFin'].zfill(9)

        raiz = etree.Element('inutNFe', versao=nf.versao, xmlns=NAMESPACES['NFE'])
        inf_inut = etree.SubElement(raiz, 'infInut', Id=identificacao)
        for i in tags: 
	    etree.SubElement( inf_inut, i ).text=tags[i] #--// Adicionando dinamicamente tags no XML
 
        return ev.envio_post( self.url('INUTILIZACAO',''), cb.cabecalho('NFeInutilizacao4', ca.assinarXml( raiz, '#' + identificacao ), ''), False, None )

    def sefazEventos( self, tags, d):

        NotaFiscalParametros.metodo = str( d['descEvento'].strip().lower() )+'_' + datetime.datetime.now().strftime("%d%m%Y%T").replace(':','')
 
        identificacao = 'ID' + tags['tpEvento'] + tags['chNFe'] + tags['nSeqEvento'].zfill(2)

        raiz = etree.Element('evento', versao='1.00', xmlns=NAMESPACES['NFE'])
        inev = etree.SubElement(raiz, 'infEvento', Id=identificacao)
        for i in tags:  etree.SubElement(inev, i ).text = tags[i] #--// Adicionando dinamicamente tags no XML
        etree.SubElement(inev, 'verEvento').text = '1.00'

        detev = etree.SubElement(inev, 'detEvento', versao='1.00')
        etree.SubElement(detev, 'descEvento').text = d['descEvento']

        if d['descEvento'] == 'Cancelamento':
            etree.SubElement(detev, 'nProt').text = d['nProt']
            etree.SubElement(detev, 'xJust').text = d['xJust']

        elif d['descEvento'] == 'Carta de Correcao':
            etree.SubElement(detev, 'xCorrecao').text = d['xCorrecao']
            etree.SubElement(detev, 'xCondUso').text = CARTA_CORRECAO

        return ev.envio_post( self.url('RECEPCAO', tags['cOrgao']), cb.cabecalho('NFeRecepcaoEvento4', ca.assinarXml( raiz, '#' + identificacao ), d['idLote']), False, None )

    def consultarNotaFiscalChave(self, tags):

#----// MDFe
	if nf.modelo=='58':

	    raiz = etree.Element('consSitMDFe', versao=nf.versao, xmlns=MDFENAMESPACES['MDFE'])
	    for i in tags:  etree.SubElement(raiz, i ).text = tags[i] #--// Adicionando dinamicamente tags no XML
	    return ev.envio_post( self.url('MDFeConsulta',''), cb.cabecalho('MDFeConsulta', raiz, ''), False, None )

#----// NFe,NFCe
	else:

	    NotaFiscalParametros.metodo = 'concultachave_' + datetime.datetime.now().strftime("%d%m%Y%T").replace(':','')

	    raiz = etree.Element('consSitNFe', versao=nf.versao, xmlns=NAMESPACES['NFE'])
	    for i in tags:  etree.SubElement(raiz, i ).text = tags[i] #--// Adicionando dinamicamente tags no XML
	    return ev.envio_post( self.url('CHAVE',''), cb.cabecalho('NFeConsultaProtocolo4', raiz, ''), False, None )
 
    def downloadNfeSefazDistribuicao(self, tags, d):

        raiz = etree.Element('distDFeInt', xmlns=NAMESPACES['NFE'], versao="1.01")
        for i in tags:
           if tags[i]: etree.SubElement(raiz, i ).text = tags[i] #--// Adicionando dinamicamente tags no XML

        if d['ultNSU']: #--// Lista pelo nsu
            dNSU = etree.SubElement(raiz, 'distNSU')
            etree.SubElement(dNSU, 'ultNSU').text = d['ultNSU']

        if d['consChNFe']: #--// Chave { Manifesta e Download }
            chave = etree.SubElement(raiz, 'consChNFe')
            etree.SubElement(chave, 'chNFe').text = d['consChNFe']

        return ev.envio_post( self.url('DISTRIBUICAO','91'), cb.cabecalho('NFeDistribuicaoDFe', raiz, ''), False, None )

    def autorizacaoSefaz(self, tags=None, xml=None, chave=None, modelo='55', recuperar=None):

        NotaFiscalParametros.metodo = 'autorizacao_' + datetime.datetime.now().strftime("%d%m%Y%T").replace(':','')

        if modelo=='58':	raiz_nfe = etree.Element('MDFe', xmlns=MDFENAMESPACES['MDFE'])
        else:	raiz_nfe = etree.Element('NFe', xmlns=NAMESPACES['NFE'])

        raiz_nfe.append(xml)
        assinado = ca.assinarXml( raiz_nfe, '#'+chave )
        ca.validaSchema(assinado)
	
	""" MDFe Grava o XML original, para recuperar atraves do recibo se for o caso """
	if modelo=='58':	nf.gravar_xml_original_mdfe.salvaDados( nf.gravar_xml_original_mdfe_parent, nf.gravar_xml_original_mdfe_filial, 6, chave,etree.tostring(assinado, encoding="unicode", pretty_print=False),None)

        """ Confeccao do QR-CODE 2.00 """
        if modelo == '65':

	    qrcode, consulta = self.geradorQrcode( etree.tostring(assinado), modelo )
	    raiz_qrc = etree.Element('infNFeSupl')
	    etree.SubElement(raiz_qrc, 'qrCode').text = qrcode
	    etree.SubElement(raiz_qrc, 'urlChave').text = consulta
	    assinado.insert(1,raiz_qrc)

	    """ Guarda o xml assinado para gravar na finalizacao e depois enviar a contingencia a sefazr e monta o xml final """
	    if nf.emissao_contingencia:
	        NotaFiscalParametros.xml_assinado_contingencia = etree.tostring(assinado, encoding='unicode').replace('\n', '')

	elif modelo == '58': #--// QR-CODE MDFE 3.00a em 9-10-2019

	    __xml = etree.tostring(assinado, encoding="unicode", pretty_print=False)
	    xml = minidom.parseString( __xml )
	    chave = ca.xmlLeitura(xml,'infMDFe','Id')[1].replace('MDFe','').strip()
	    ambiente = ca.xmlLeitura(xml,'infMDFe','tpAmb')[0][0].strip()
	
	    url_qrcode = urlQrcode( 'RJ','2', modelo )
	    qrcode = url_qrcode+'?chMDFe='+ chave +'&tpAmb=' + ambiente
	    raiz_qrc = etree.Element('infMDFeSupl')
	    etree.SubElement(raiz_qrc, 'qrCodMDFe').text = qrcode
	    assinado.insert(1,raiz_qrc)
	    
	#--// [ Grava pela primeira vez um xml original { Utilizo para recuperacao de rejeicao 204,359} ]
	if nf.gravar_original and recuperar:
	    
	    recover=recuperar[4]
	    xmlorginal=etree.tostring(assinado, encoding='unicode').replace('\n', '')
	    recover.copiaOriginalXml(xmlorginal,recuperar,chave)

	    mn.gravarXmlRetorno( etree.tostring(assinado, encoding='unicode').replace('\n', ''), 'original', False, chave) #--//Gravacao do xml na primeira emissao para recuperacap 204,359

        if modelo=='58':	raiz_env = etree.Element('enviMDFe', xmlns=MDFENAMESPACES['MDFE'], versao=nf.versao)
	else:	raiz_env = etree.Element('enviNFe', xmlns=NAMESPACES['NFE'], versao=nf.versao)
	
        etree.SubElement(raiz_env, 'idLote').text = tags['idLote']  # numero autoincremental gerado pelo sistema

        if modelo!='58':	etree.SubElement(raiz_env, 'indSinc').text = tags['indSinc']  # 0 para assincrono, 1 para sincrono
        raiz_env.append( assinado )

        if modelo=='58':	xmlstring, xml = ev.envio_post( self.url('MDFeRecepcao',''), cb.cabecalho('MDFeRecepcao', raiz_env,'' ), True, chave )
	else:	xmlstring, xml = ev.envio_post( self.url('AUTORIZACAO',''), cb.cabecalho('NFeAutorizacao4', raiz_env,'' ), True, chave )

        status_retorno = ''
	
        if xml and xml.status_code == 200:

            protocolo_envio = etree.fromstring(xml.content)[0][0]

#---------// MDFe	    
            if modelo=='58' and xmlstring:

		xml=minidom.parseString( xmlstring.encode('UTF-8') )
		status_retorno=ca.xmlLeitura(xml,'retEnviMDFe','cStat')[0][0]
		numero_recibo=ca.xmlLeitura(xml,'infRec','nRec')[0][0]
		
		""" MDFe Grava o numero do recibo, para recuperar atraves do recibo se for o caso """
		if numero_recibo:	nf.gravar_xml_original_mdfe.salvaDados( nf.gravar_xml_original_mdfe_parent, nf.gravar_xml_original_mdfe_filial, 7, chave, numero_recibo, status_retorno)
		if status_retorno=='103' and numero_recibo:

		    time.sleep( nf.time_out_recibo )

		    xmlstring=self.mdfeConsultaRecibo(numero_recibo)
		    xml=minidom.parseString(xmlstring.encode('UTF-8'))
		    status_retorno, a1=ca.xmlLeitura(xml,'infProt','cStat')
		    status_recibo, a2=ca.xmlLeitura(xml,'retConsReciMDFe','cStat')

		    if status_retorno and status_retorno[0]=='100':
			
			status_retorno=status_retorno[0]
			
			pm01,p01=ca.xmlLeitura(xml,'protMDFe','versao')
			pm02,p02=ca.xmlLeitura(xml,'infProt','Id')
			pm03,p03=ca.xmlLeitura(xml,'infProt','tpAmb')
			pm04,p04=ca.xmlLeitura(xml,'infProt','verAplic')
			pm05,p05=ca.xmlLeitura(xml,'infProt','chMDFe')
			pm06,p06=ca.xmlLeitura(xml,'infProt','dhRecbto')
			pm07,p07=ca.xmlLeitura(xml,'infProt','nProt')
			pm08,p08=ca.xmlLeitura(xml,'infProt','digVal')
			pm09,p09=ca.xmlLeitura(xml,'infProt','cStat')
			pm10,p10=ca.xmlLeitura(xml,'infProt','xMotivo')
			raiz_final = etree.Element('mdfeProc', xmlns=MDFENAMESPACES['MDFE'], versao=nf.versao)

			raiz_aprovado=etree.Element('protMDFe', versao=p01)
			raiz_protocolo=etree.SubElement(raiz_aprovado,'infProt', Id=p02)
			etree.SubElement(raiz_protocolo,"tpAmb").text=pm03[0]
			etree.SubElement(raiz_protocolo,"verAplic").text=pm04[0]
			etree.SubElement(raiz_protocolo,"chMDFe").text=pm05[0]
			etree.SubElement(raiz_protocolo,"dhRecbto").text=pm06[0]
			etree.SubElement(raiz_protocolo,"nProt").text=pm07[0]
			etree.SubElement(raiz_protocolo,"digVal").text=pm08[0]
			etree.SubElement(raiz_protocolo,"cStat").text=pm09[0]
			etree.SubElement(raiz_protocolo,"xMotivo").text=pm10[0]
			raiz_final.append(assinado)
			raiz_final.append(raiz_aprovado)
			xmlstring = DECLARACAO_NFE + etree.tostring(raiz_final, encoding="unicode").replace('ns0:','').replace(':ns0','')
			
			pasta_gravar=diretorios.usPasta+chave+'-'+login.filialLT[nf.gravar_xml_original_mdfe_filial][14].lower().replace(' ','')+'.xml'
			if modelo=='58':	pasta_gravar=nf.gravar_envio_retorno_pasta+'/'+chave+'-'+login.filialLT[nf.gravar_xml_original_mdfe_filial][14].lower().replace(' ','')+'.xml'
			
			__arquivo = open(pasta_gravar, "w" )
			__arquivo.write(xmlstring.encode('utf-8'))
			__arquivo.close()

			nf.relacao_xmls_utilizados.append(pasta_gravar)

		    else:
			if status_retorno and (status_retorno)>1:	status_retorno=status_retorno[0]
			else:	status_retorno=status_recibo[0]

#--------// NFe			
	    else:
		if protocolo_envio.xpath("ns:retEnviNFe/ns:cStat",namespaces={'ns':NAMESPACES['NFE']})[0].text == '104': #--// Processado

		    autorizada = protocolo_envio.xpath("ns:retEnviNFe/ns:protNFe", namespaces={'ns':NAMESPACES['NFE']})[0]
		    status_retorno = autorizada.xpath('ns:infProt/ns:cStat', namespaces={'ns':NAMESPACES['NFE']})[0].text
		    if status_retorno == '100':
			
			raiz = etree.Element('nfeProc', xmlns=NAMESPACES['NFE'], versao=nf.versao)
			raiz.append(assinado)
			raiz.append(autorizada)
			xmlstring = DECLARACAO_NFE + etree.tostring(raiz, encoding="unicode").replace('ns0:','').replace(':ns0','')
			mn.gravarXmlRetorno(xmlstring, 'autorizacao', False, chave)
		
        return xmlstring, status_retorno

    def geradorQrcode(self, xml_string, modelo ):

        """ 
            QRCODE Normal, http://<dominio>/nfce/qrcode?p=<chave_acesso>|<versao_qrcode>|<tipo_ambiente>|<identificador_csc>|<codigo_hash>
            QRCODE-Contigencia, http://<dominio>/nfce/qrcode/?p=<chave_acesso>|<versao_qrcode>|<tipo_ambiente>|<dia_data_emissao>|<valor_total_nfce>|<digVal>|<identificador_csc>|<codigo_hash>
        """
        xml = minidom.parseString( xml_string )
        chave = ca.xmlLeitura(xml,'infNFe','Id')[1].replace('NFe','').strip()
        dhemissao = ca.xmlLeitura(xml,'infNFe','dhEmi')[0][0].strip()
        ambiente = ca.xmlLeitura(xml,'infNFe','tpAmb')[0][0].strip()
        uf = ca.xmlLeitura(xml,'infNFe','UF')[0][0].strip().upper()
        valornota = ca.xmlLeitura(xml,'ICMSTot','vNF')[0][0].strip()
        digestvalue = ca.xmlLeitura(xml,'Signature','DigestValue')[0][0].encode('hex')

        urlqrcode, urlconsulta = urlQrcode( uf,ambiente, modelo )

        #//--[ QRCODE em contigencia ]
        dia_emissao = dhemissao.split('-')[2][:2]
        qrcode_contigencia = '{}|{}|{}|{}|{}|{}|{}'.format(chave,'2',ambiente,dia_emissao,valornota,digestvalue,str(int(nf.csc_id)))
        hash_contigencia = hashlib.sha1(qrcode_contigencia+nf.csc_numero).hexdigest() #.upper()

        qrcode_contigencia = urlqrcode +'p='+ qrcode_contigencia + '|'+ hash_contigencia
        url_contigencia = '<![CDATA['+qrcode_contigencia+']]>'

        #-----[ QRCODE normal ]
        qrcode  = '{}|{}|{}|{}'.format(chave,'2',ambiente,str(int(nf.csc_id)))
        hash_normal = hashlib.sha1(qrcode+nf.csc_numero).hexdigest() #.upper()

        qrcode = urlqrcode +'p='+ qrcode + '|'+ hash_normal
        url = '<![CDATA['+qrcode+']]>'

	if nf.emissao_contingencia:	url = url_contigencia

        return url, urlconsulta
 
    def gravarXmlRetorno(self, xml, metodo, strstring = False, chave=''):
	
        if nf.gravar_envio_retorno_pasta and metodo and NotaFiscalParametros.metodo and NotaFiscalParametros.gravar_envio_retorno:

            arquivo = nf.gravar_envio_retorno_pasta +'/'+ NotaFiscalParametros.metodo +'_'+ metodo + '.xml'
            if metodo=='autorizacao': arquivo = nf.gravar_envio_retorno_pasta +'/'+ chave + '.xml'
	    if metodo=='original' and nf.gravar_original:	arquivo = nf.gravar_envio_retorno_pasta +'/original_'+ chave[3:] + '.xml'
            if strstring:   xml_grv = etree.tostring(xml, encoding="unicode", pretty_print=False)
            else:   xml_grv = xml
	    
            __arquivo = open(arquivo, "w" )
            __arquivo.write( xml_grv.encode('UTF-8') )
            __arquivo.close()
            NotaFiscalParametros.pasta_gravaca_xml_final = arquivo
            NotaFiscalParametros.relacao_xmls_utilizados.append( arquivo )

    def url(self, metodo, unidade_eventos ):
 
        unidade = nf.uf
        if unidade_eventos == '91': unidade = 'AN' #--// Ambiente nacional

	if nf.modelo=='58':	return mdfewebService( nf.ambiente, unidade, nf.modelo, metodo ) #--// MDFE
        else:	return webService( nf.ambiente, unidade, nf.modelo, metodo )

    def mdfeConsultaRecibo(self,recibo):

	raiz = etree.Element('consReciMDFe', versao=nf.versao, xmlns=MDFENAMESPACES['MDFE'])
	etree.SubElement(raiz, 'tpAmb' ).text = str(nf.ambiente)
	etree.SubElement(raiz, 'nRec' ).text = recibo
	return ev.envio_post( self.url('MDFeRetRecepcao',''), cb.cabecalho('MDFeRetRecepcao', raiz, ''), False, None )

    def mdfeConsultaNaoEncerrada(self,cnpj):
	
	raiz = etree.Element('consMDFeNaoEnc', versao=nf.versao, xmlns=MDFENAMESPACES['MDFE'])
	etree.SubElement(raiz, 'tpAmb' ).text = nf.ambiente
	etree.SubElement(raiz, 'xServ' ).text = u"CONSULTAR NÃO ENCERRADOS"
	etree.SubElement(raiz, 'CNPJ' ).text = cnpj
	return ev.envio_post( self.url('MDFeConsNaoEnc',''), cb.cabecalho('MDFeConsNaoEnc', raiz, ''), False, None )

    def encerramentoMdfe(self,_id,tags1,tags2):

	raiz=etree.Element('eventoMDFe', versao=nf.versao, xmlns=MDFENAMESPACES['MDFE'])
	raiz_inf=etree.SubElement(raiz, 'infEvento', Id=_id)
	for i in tags1:
	    if tags1[i]:	etree.SubElement(raiz_inf, i).text=tags1[i]

	raiz_det=etree.SubElement(raiz_inf, 'detEvento', versaoEvento=nf.versao)
	raiz_eve=etree.SubElement(raiz_det, 'evEncMDFe')
	for i in tags2:
	    if tags2[i]:	etree.SubElement(raiz_eve, i).text=tags2[i]
	
	return ev.envio_post( self.url('MDFeRecepcaoEvento', ''), cb.cabecalho('MDFeRecepcaoEvento', ca.assinarXml( raiz, '#' + _id ), ''), False, None )

    def cancelamentoMdfe(self,_id,tags1,tags2):

	raiz=etree.Element('eventoMDFe', versao=nf.versao, xmlns=MDFENAMESPACES['MDFE'])
	raiz_inf=etree.SubElement(raiz, 'infEvento', Id=_id)
	for i in tags1:
	    if tags1[i]:	etree.SubElement(raiz_inf, i).text=tags1[i]

	raiz_det=etree.SubElement(raiz_inf, 'detEvento', versaoEvento=nf.versao)
	raiz_eve=etree.SubElement(raiz_det, 'evCancMDFe')
	for i in tags2:
	    if tags2[i]:	etree.SubElement(raiz_eve, i).text=tags2[i]
	
	return ev.envio_post( self.url('MDFeRecepcaoEvento', ''), cb.cabecalho('MDFeRecepcaoEvento', ca.assinarXml( raiz, '#' + _id ), ''), False, None )
	
class NFeCabecalho:

    def cabecalho( self, metodo='', __raiz='', id_lote='' ):

#-----: MDFE
	if nf.modelo=='58':
	    raiz = etree.Element('{%s}Envelope' % NAMESPACES['SOAP'], nsmap={'xsi': NAMESPACES['XSI'], 'xsd': NAMESPACES['XSD'], 'soap': NAMESPACES['SOAP']})
	    head = etree.SubElement(raiz,'{%s}Header' % NAMESPACES['SOAP'])
	    
	    cbhe = etree.SubElement(head,'mdfeCabecMsg',xmlns=MDFENAMESPACES['METODO']+str(metodo))
	    etree.SubElement(cbhe,'cUF').text=CODIGOS_UF[nf.uf]
	    etree.SubElement(cbhe,'versaoDados').text=nf.versao

	    body = etree.SubElement(raiz,'{%s}Body' % NAMESPACES['SOAP'])
	    sbe=etree.SubElement(body,'mdfeDadosMsg',xmlns=MDFENAMESPACES['METODO']+str(metodo))
	    sbe.append( __raiz )

#-----: NFe-NFCe	    
	else:

	    raiz = etree.Element('{%s}Envelope' % NAMESPACES['SOAP'], nsmap={'xsi': NAMESPACES['XSI'], 'xsd': NAMESPACES['XSD'], 'soap': NAMESPACES['SOAP']})
	    body = etree.SubElement(raiz,'{%s}Body' % NAMESPACES['SOAP'])
	    if metodo  in ['NFeDistribuicaoDFe']:
		sbe = etree.SubElement(body, 'nfeDistDFeInteresse', xmlns=NAMESPACES['METODO']+metodo)
		interesse = etree.SubElement(sbe, 'nfeDadosMsg')
		interesse.append(__raiz)
	    else:
		if metodo  in ['NFeRecepcaoEvento4'] and id_lote:
		    sbe=etree.SubElement(body,'nfeDadosMsg',xmlns=NAMESPACES['METODO']+metodo)
		    evento=etree.Element('envEvento', versao='1.00', xmlns=NAMESPACES['NFE'])
		    etree.SubElement(evento, 'idLote').text = str(id_lote)
		    evento.append(__raiz)
		    sbe.append(evento)
		else:
		    sbe=etree.SubElement(body,'nfeDadosMsg',xmlns=NAMESPACES['METODO']+metodo)
		    sbe.append( __raiz )

        mn.gravarXmlRetorno( raiz, 'cabecalho', True, '')
        return raiz

	
class NFeEnvioSefaz:

    def contingenciaSefaz(self, url,xml,assinado):

	dados = ['','','','']
	try:
	    
	    arquivos_certificado = ce.certificadoArquivo(1)
	    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)	
	    result = requests.post(url, xml, headers=POST_HEADER, verify=False, cert=arquivos_certificado, timeout=nf.ntimeout)

	    resultado = result.text
	    result.encoding = 'utf-8'
	    status_retorno = ''
	    dados = ['','','','']

	    if result.status_code == 200:

		protocolo_envio = etree.fromstring(result.content)[0][0]
		if protocolo_envio.xpath("ns:retEnviNFe/ns:cStat",namespaces={'ns':NAMESPACES['NFE']})[0].text == '104': #--// Processado

		    autorizada = protocolo_envio.xpath("ns:retEnviNFe/ns:protNFe", namespaces={'ns':NAMESPACES['NFE']})[0]
		    status_retorno = autorizada.xpath('ns:infProt/ns:cStat', namespaces={'ns':NAMESPACES['NFE']})[0].text
		    motivo = autorizada.xpath('ns:infProt/ns:xMotivo', namespaces={'ns':NAMESPACES['NFE']})[0].text
		    chave = autorizada.xpath('ns:infProt/ns:chNFe', namespaces={'ns':NAMESPACES['NFE']})[0].text
		    protocolo = ""
		    data = autorizada.xpath('ns:infProt/ns:dhRecbto', namespaces={'ns':NAMESPACES['NFE']})[0].text
		    
		    if status_retorno == '100':

			chave = autorizada.xpath('ns:infProt/ns:chNFe', namespaces={'ns':NAMESPACES['NFE']})[0].text
			motivo = autorizada.xpath('ns:infProt/ns:xMotivo', namespaces={'ns':NAMESPACES['NFE']})[0].text
			protocolo = autorizada.xpath('ns:infProt/ns:nProt', namespaces={'ns':NAMESPACES['NFE']})[0].text
			data = autorizada.xpath('ns:infProt/ns:dhRecbto', namespaces={'ns':NAMESPACES['NFE']})[0].text
			    
			raiz = etree.Element('nfeProc', xmlns=NAMESPACES['NFE'], versao=nf.versao)
			raiz.append(assinado)
			raiz.append(autorizada)
			resultado = DECLARACAO_NFE + etree.tostring(raiz, encoding="unicode").replace('ns0:','').replace(':ns0','')
			mn.gravarXmlRetorno(resultado, 'autorizacao', False, chave)

		    dados = chave, motivo, protocolo, data

	except requests.exceptions.RequestException as resultado:
	    status_retorno = ''
		    
	return resultado, status_retorno, dados
	
    def envio_post(self, url, xml, modo_retorno, numero_chave):

        result = None
        try:

            arquivos_certificado = ce.certificadoArquivo(1)

	    xml = re.sub(
	    '<qrCode>(.*?)</qrCode>',lambda x: x.group(0).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', ''),etree.tostring(xml, encoding='unicode').replace('\n', '')
	    )
		
	    """ 14-01-2019 16:17
	    Alteracao para conseguir pesquisa MDFe nao encerrados pq o XML estava com unicode e a sefaz voltava vazio
	    vou testar para nfe se ficar tudo ok, permanece se nao fazer isso apenas para { mdfeConsultaNaoEncerrada }
	    """
	    xml = DECLARACAO_XML +  xml.encode('UTF-8') #--// Alteracao para conseguir pesquisa MDFe nao encerrados pq o XML estava com unicode e voltava vazio { }

	    if nf.emissao_contingencia:

		resultado = xml
		mn.gravarXmlRetorno(xml, 'contingencia', False, '')

	    else:
		
		requests.packages.urllib3.disable_warnings(InsecureRequestWarning)	
		result = requests.post(url, xml, headers=POST_HEADER, verify=False, cert=arquivos_certificado, timeout=nf.ntimeout)

		resultado = result.text
		result.encoding = 'utf-8'
		mn.gravarXmlRetorno( resultado , 'retorno_sefaz', False, '' )

	except requests.exceptions.RequestException as resultado:

	    return resultado,result

        if os.path.exists(arquivos_certificado[0]):   os.remove(arquivos_certificado[0])
        if os.path.exists(arquivos_certificado[1]):   os.remove(arquivos_certificado[1])

        if modo_retorno:    return resultado,result
        else:
	    return resultado

class NFeCertificado:

    def certificadoArquivo(self, retorno = 1):

		p12 = crypto.load_pkcs12(open(nf.caminho_certificado, 'rb').read(),nf.senha_certificado)
		pem = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate()) #.replace('\n','').replace('-----BEGIN PRIVATE KEY-----','').replace('-----END PRIVATE KEY-----','')
		chave = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey()) #.replace('\n','').replace('-----BEGIN PRIVATE KEY-----','').replace('-----END PRIVATE KEY-----','')

		with tempfile.NamedTemporaryFile(delete=False) as arquivo_certificado:  arquivo_certificado.write(pem)
		with tempfile.NamedTemporaryFile(delete=False) as arquivo_chave: arquivo_chave.write(chave)

		if retorno == 1:	return arquivo_certificado.name, arquivo_chave.name
		if retorno == 2:	return pem,chave 

class CertificadoAssinatura:

    def assinarXml(self, __raiz, __id ):
	
	certificado, chave = ce.certificadoArquivo( 2 )
	signer = XMLSigner(method=methods.enveloped, signature_algorithm="rsa-sha1", digest_algorithm='sha1', c14n_algorithm='http://www.w3.org/TR/2001/REC-xml-c14n-20010315')

	ns = {None: signer.namespaces['ds']}
	signer.namespaces = ns

	warnings.simplefilter("ignore") #--// Nao mostrar o erro de assinatura { pode ser problemas com SSL mais estar assinando normal 19-10-2018 18:42 }
	signed_root = signer.sign(__raiz, key=chave, cert=certificado, reference_uri=__id )

	xml_envio = etree.tostring(signed_root, encoding="unicode", pretty_print=False)
	mn.gravarXmlRetorno( signed_root, 'assinado', True, '' )      
	    
	return signed_root

    def xmlLeitura( self, doc, pai, filho):
    		
        valores = []
        aTribuT = ''

        campos  = doc.getElementsByTagName(pai)
        if campos != []:

            for node in campos:

                """ Pegar Atributos ex: ID da NFE """
                aTribuT = node.getAttribute(filho)
				
                flista=node.getElementsByTagName(filho)

                if flista != []: #-:[ Campo filho existir ]
							
                    for fl in flista:
						
                        if fl.firstChild != None:
							
                            dados = fl.firstChild.nodeValue
                            valores.append(dados)

                        else:	valores.append('')

                else:	valores.append('')
							
        return valores,aTribuT

    def validaSchema(self, xml=None ):

	xmlschema_doc = etree.parse(NotaFiscalParametros.pasta_arquivo_nfe_xsd_versao)
	xmlschema = etree.XMLSchema(xmlschema_doc)
	saida_erros = ''
	if not xmlschema.validate(xml): #--// Retorma boleano
	    erros =[]
	    for i in xmlschema.error_log:

		erros.append({
			    'message':i.message,'domain':i.domain,'type':i.type,'level':i.level,'line':i.line,'column':i.column,
			    'filename':i.filename,'domain_name':i.domain_name,'type_name':i.type_name,'level_name':i.level_name
			    })
	    
	    if erros:
		for i in erros:

		    saida_erros +='Tipo de erro: '+i['type_name']+'\n'
		    saida_erros +='Menssagem...: '+i['message']+'\n\n'
	NotaFiscalParametros.retorno_validacao_xsd = saida_erros

		
class NotaFiscalParametros:

    caminho_certificado = str()
    senha_certificado = str()
    ambiente = 2
    modelo = '55'
    serie = str()
    uf = str()
    cnpj = str()
    versao = str()
    gravar_envio_retorno_pasta = str()
    gravar_envio_retorno = False
    metodo = str()
    pasta_gravaca_xml_final = str()
    relacao_xmls_utilizados = []
    csc_id = None
    csc_numero = None
    pasta_arquivo_nfe_xsd_versao = str()
    retorno_validacao_xsd = ''
    ntimeout=30
    gravar_original=False
    serie_mdfe=str()
    time_out_recibo=3
    gravar_xml_original_mdfe=None
    gravar_xml_original_mdfe_parent=None
    gravar_xml_original_mdfe_filial=None
    contingencia_enviar = False
    emissao_contingencia = False
    
    xml_assinado_contingencia = str()

nf = NotaFiscalParametros()
cb = NFeCabecalho()
ev = NFeEnvioSefaz()
ce = NFeCertificado()
ca = CertificadoAssinatura()
mn = ManutencaoSefaz()
