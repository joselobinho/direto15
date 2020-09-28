#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
#  
#  Copyright 2016 lykos users <lykos@linux-714r.site>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
LOBO_UF={1:2}
CODIGOS_UF = {
'AN':'91',
'RO':'11',
'AC':'12',
'AM':'13',
'RR':'14',
'PA':'15',
'AP':'16',
'TO':'17',
'MA':'21',
'PI':'22',
'CE':'23',
'RN':'24',
'PB':'25',
'PE':'26',
'AL':'27',
'SE':'28',
'BA':'29',
'MG':'31',
'ES':'32',
'RJ':'33',
'SP':'35',
'PR':'41',
'SC':'42',
'RS':'43',
'MS':'50',
'MT':'51',
'GO':'52',
'DF':'53',
'AN':'91'
}
CODIGO_PAIS = {'BR':'1058'}
NAMESPACES = {
'NFE':'http://www.portalfiscal.inf.br/nfe',
'SIG':'http://www.w3.org/2000/09/xmldsig#',
'SOAP':'http://www.w3.org/2003/05/soap-envelope',
'XSD':'http://www.w3.org/2001/XMLSchema',
'XSI':'http://www.w3.org/2001/XMLSchema-instance',
'METODO':'http://www.portalfiscal.inf.br/nfe/wsdl/',
'XMLD':'<?xml version="1.0" encoding="utf-8"?>',
}

ALERTANAMESPACES = {
'SOAP':'http://schemas.xmlsoap.org/soap/envelope/',
}

MDFENAMESPACES={
"MDFE":"http://www.portalfiscal.inf.br/mdfe",
'METODO':'http://www.portalfiscal.inf.br/mdfe/wsdl/'
}

DECLARACAO_NFE = '<?xml version="1.0" ?>'
DECLARACAO_XML = '<?xml version="1.0" encoding="UTF-8"?>'
POST_HEADER = {
'content-type': 'application/soap+xml; charset=utf-8;',
'Accept': 'application/soap+xml; charset=utf-8;',
}

CARTA_CORRECAO = 'A Carta de Correcao e disciplinada pelo paragrafo 1o-A do art. 7o do Convenio S/N, de 15 de dezembro de 1970 e pode ser utilizada para regularizacao de erro ocorrido na emissao de documento fiscal, desde que o erro nao esteja relacionado com: I - as variaveis que determinam o valor do imposto tais como: base de calculo, aliquota, diferenca de preco, quantidade, valor da operacao ou da prestacao; II - a correcao de dados cadastrais que implique mudanca do remetente ou do destinatario; III - a data de emissao ou de saida.'

def webService( ambiente, uf, modelo, servico ):

    #--// Estados que utiliza o SVRS
    SVRS = ['AC','AL','AP','DF','ES','PB','PI','RJ','RN','RO','RR','SC','SE','TO']
    dominio = ''
    if uf.upper() in SVRS:

        HTTPS = 'https://nfe.' if ambiente == '1' else 'https://nfe-homologacao.'
        if str(modelo) == '65':    HTTPS = 'https://nfce.' if ambiente == '1' else 'https://nfce-homologacao.'

        SERVIDORES = {
        'INUTILIZACAO':'svrs.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao4.asmx',
        'CHAVE':'svrs.rs.gov.br/ws/NfeConsulta/NfeConsulta4.asmx',
        'STATUS':'svrs.rs.gov.br/ws/NfeStatusServico/NfeStatusServico4.asmx',
        'CADASTRO':'https://cad.svrs.rs.gov.br/ws/cadconsultacadastro/cadconsultacadastro4.asmx',
        'RECEPCAO':'svrs.rs.gov.br/ws/recepcaoevento/recepcaoevento4.asmx',
        'AUTORIZACAO':'svrs.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao4.asmx',
        'RETAUTORIZACAO':'svrs.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao4.asmx'
        }
        dominio = SERVIDORES[servico.upper()] if servico.upper() in ['CADASTRO'] else HTTPS + SERVIDORES[servico.upper()]

    elif uf.upper() == 'BA':

        HTTPS = 'https://nfe.' if ambiente == '1' else 'https://hnfe.'
        if str(modelo) == '65':    HTTPS = 'https://nfce.' if ambiente == '1' else 'https://nfce-homologacao.'
        SERVIDORES = {
        'INUTILIZACAO':'sefaz.ba.gov.br/webservices/NFeInutilizacao4/NFeInutilizacao4.asmx',
        'CHAVE':'sefaz.ba.gov.br/webservices/NFeConsultaProtocolo4/NFeConsultaProtocolo4.asmx',
        'STATUS':'sefaz.ba.gov.br/webservices/NFeStatusServico4/NFeStatusServico4.asmx',
        'CADASTRO':'sefaz.ba.gov.br/webservices/CadConsultaCadastro4/CadConsultaCadastro4.asmx',
        'RECEPCAO':'sefaz.ba.gov.br/webservices/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx',
        'AUTORIZACAO':'sefaz.ba.gov.br/webservices/NFeAutorizacao4/NFeAutorizacao4.asmx',
        'RETAUTORIZACAO':'sefaz.ba.gov.br/webservices/NFeRetAutorizacao4/NFeRetAutorizacao4.asmx'
        }
        dominio = SERVIDORES[servico.upper()] if servico.upper() in ['CADASTRO'] else HTTPS + SERVIDORES[servico.upper()]

    elif uf.upper() in ['AN']: #--// Ambiente nacional

        HTTPS = 'https://www.' if ambiente == '1' else 'https://hom.'
        if servico.upper() == 'DISTRIBUICAO':   HTTPS = 'https://www1.' if ambiente == '1' else 'https://hom.'

        SERVIDORES = {
            'RECEPCAO': 'nfe.fazenda.gov.br/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx',
            'DISTRIBUICAO': 'nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx',
            }
        dominio = HTTPS + SERVIDORES[servico.upper()]

    #print dominio
    return dominio

def mdfewebService( ambiente, uf, modelo, servico ):

    #--// Estados que utiliza o SVRS
    SVRS = ['AC','AL','AP','DF','ES','PB','PI','RJ','RN','RO','RR','SC','SE','TO']
    dominio = ''
    if uf.upper() in SVRS:

        HTTPS = 'https://mdfe.' if ambiente == '1' else 'https://mdfe-homologacao.'

        SERVIDORES = {
		"MDFeRecepcao":"svrs.rs.gov.br/ws/MDFeRecepcao/MDFeRecepcao.asmx",
		"MDFeRetRecepcao":"svrs.rs.gov.br/ws/MDFeRetRecepcao/MDFeRetRecepcao.asmx",
		"MDFeRecepcaoEvento":"svrs.rs.gov.br/ws/MDFeRecepcaoEvento/MDFeRecepcaoEvento.asmx",
		"MDFeConsulta":"svrs.rs.gov.br/ws/MDFeConsulta/MDFeConsulta.asmx",
		"MDFeStatusServico":"svrs.rs.gov.br/ws/MDFeStatusServico/MDFeStatusServico.asmx",
		"MDFeConsNaoEnc":"svrs.rs.gov.br/ws/MDFeConsNaoEnc/MDFeConsNaoEnc.asmx",
		"MDFeDistribuicaoDFe":"svrs.rs.gov.br/ws/MDFeDistribuicaoDFe/MDFeDistribuicaoDFe.asmx"
		}
        dominio = HTTPS + SERVIDORES[servico]

    return dominio

def urlQrcode( uf,ambiente, modelo ):

    if modelo=='65':

	#lista_url = {'RJ':('http://www4.fazenda.rj.gov.br/consultaNFCe/QRCode?','www.nfce.fazenda.rj.gov.br/consulta'), Mudanca em 18-07-2019
	lista_url = {'RJ':('http://www4.fazenda.rj.gov.br/consultaNFCe/QRCode?','www.fazenda.rj.gov.br/nfce/consulta'),
	'ES':('','')}

    elif modelo == '58':
	lista_url = {'RJ':'https://dfe-portal.svrs.rs.gov.br/mdfe/qrCode'}
		
    return lista_url[uf]

def cnpjNumeros( cnpj ):
    return ''.join(filter(lambda c: ord(c) in range(48, 58), cnpj))
