#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  notafiscal400.py
#  Inicio: 06-08-2018 22:32 Jose de almeida lobinho
from lxml import etree
from collections import OrderedDict
from unicodedata import normalize

class PreenchimentoNotaFiscal:
    
    def informacaoNfe(self, versao='4.00', id_nfe = None):
	# raiz = etree.Element('infNFe', Id=id_nfe, versao=versao)
        raiz = etree.Element('infNFe', versao=versao)
        raiz.attrib['Id'] = id_nfe

        return raiz

    def identificacaoNFe(self,tags):

        raiz = etree.Element('ide')
        for i in tags:
            if tags[i] and i!='refNFe': etree.SubElement(raiz, i ).text = tags[i]
            elif i == 'refNFe' and tags[i]: #-// Devolucao nota fiscal referenciada
                nfref = etree.SubElement(raiz, 'NFref' )
                etree.SubElement(nfref, i ).text = mnf.acentos(tags[i])

        return raiz

    def emitente(self, dados = None, endereco =None, documentos = None):

        raiz = etree.Element('emit')
        for i in dados:
            if dados[i]: etree.SubElement(raiz, i ).text = mnf.acentos(dados[i])

        end = etree.SubElement(raiz, 'enderEmit')
        for i in endereco:
            if endereco[i]: etree.SubElement(end, i ).text = mnf.acentos(endereco[i])

        for i in documentos:
            if documentos[i]: etree.SubElement(raiz, i ).text = mnf.acentos(documentos[i])

        return raiz

    def destinatario(self, dados=None, endereco=None, documentos=None):

        raiz = etree.Element('dest')
        for i in dados:
            if dados[i]: etree.SubElement(raiz, i ).text = mnf.acentos(dados[i])

        if endereco:
            end = etree.SubElement(raiz, 'enderDest')
            for i in endereco:
                if endereco[i]: etree.SubElement(end, i ).text = mnf.acentos(endereco[i])

        if documentos:
            for i in documentos:
                if documentos[i]: etree.SubElement(raiz, i ).text = mnf.acentos(documentos[i])

        return raiz
    
    def localEntrega(self,tags):

        raiz = etree.Element('entrega')
        for i in tags:
            if tags[i]: etree.SubElement(raiz, i ).text = mnf.acentos(tags[i])

        return raiz

    def autorizaDownload(self,tags):

        raiz = etree.Element('autXML')
        for i in tags:
            if tags[i]: etree.SubElement(raiz, i ).text = mnf.acentos(tags[i])

        return raiz

    def itens(self, produtos = None, numero_item = '1'):

        raiz = etree.Element('det', nItem=numero_item)
        prod = etree.SubElement(raiz,'prod')
        for i in produtos:
            if produtos[i]: etree.SubElement(prod, i ).text = mnf.acentos(produtos[i])

        return raiz

    def modalidadeFrete(self, tags=None, transporte=None,veiculo=None,reboque=None,volume=None ):
    
        raiz = etree.Element('transp')
        etree.SubElement(raiz,'modFrete').text = tags
        if transporte:
            trans = etree.SubElement(raiz,'transporta')
            for t in transporte:
                if transporte[t]: etree.SubElement(trans, t ).text = mnf.acentos(transporte[t])

        if veiculo and veiculo['placa'] and veiculo['UF']:
            veic = etree.SubElement(raiz,'veicTransp')
            for v in veiculo:
                if veiculo[v]: etree.SubElement(veic, v ).text = mnf.acentos(veiculo[v])

        if reboque and reboque['placa'] and reboque['UF']:
            reboq = etree.SubElement(raiz,'reboque')
            for r in reboque:
                if reboque[r]: etree.SubElement(reboq, r ).text = mnf.acentos(reboque[r])

        if volume and volume['qVol'] and volume['pesoL']:
            volu = etree.SubElement(raiz,'vol')
            for v in volume:
                if volume[v]: etree.SubElement(volu, v ).text = mnf.acentos(volume[v])

        return raiz

    def detalharPagamentos(self, tags=None):

        raiz = etree.Element('pag')
        for i in tags:
	    
            detp = etree.SubElement(raiz,'detPag')
            etree.SubElement(detp,'indPag').text = tags[i][2] 
            etree.SubElement(detp,'tPag').text = i
            etree.SubElement(detp,'vPag').text = tags[i][0]

            if i in  ['03','04']:
                cartao = etree.SubElement(detp, 'card')
                etree.SubElement(cartao, 'tpIntegra').text = tags[i][1]
                if tags[i][0] == '1':
                    etree.SubElement(cartao, 'CNPJ').text = ''
                    etree.SubElement(cartao, 'tBand').text = ''
                    etree.SubElement(cartao, 'cAut').text = ''

        return raiz            

    def cobrancaPagamentos(self, tags=None,duplicatas=None):

        raiz = etree.Element('cobr')
        fatu = etree.SubElement(raiz,'fat')
        for i in tags:
            if tags[i]: etree.SubElement(fatu, i ).text = mnf.acentos(tags[i])

        for i in duplicatas:
            dupl = etree.SubElement(raiz,'dup')
            etree.SubElement(dupl,'nDup').text = str(i).zfill(3)
            etree.SubElement(dupl,'dVenc').text = duplicatas[i][0]
            etree.SubElement(dupl,'vDup').text = duplicatas[i][1]

        return raiz            

    def informacoesAdicionais(self,tags=None):

        raiz = etree.Element('infAdic')
        for i in tags:
            if tags[i]: etree.SubElement(raiz, i ).text = mnf.acentos(tags[i])

        return raiz

    def responsavelTecnico(self,tags=None):
 
        raiz = etree.Element('infRespTec')
        for i in tags:
            if tags[i]: etree.SubElement(raiz, i ).text = mnf.acentos(tags[i])

        return raiz

		
class ImpostoExcessivo:

    def impostosNfe400(self, icms = '00', origem = '0', tags=None, vTotTrib='0', pis=None, cofins=None, difal=None, ipi=None, modelo='55' ):

        raiz = etree.Element('imposto')
        etree.SubElement(raiz, 'vTotTrib').text = vTotTrib
        licms = etree.SubElement(raiz, 'ICMS')

        rnormal=['00','10','20','30','40','41','50','51','60','70','90'] #-------// [ codigos CST do regime normal CRT 2 ou 3 ]
        rsimples=['101','102','103','201','202','203','300','400','500','900'] #-// [ codigos CST do regime simples-nalcional CRT 1 ]

	__icms = '102' if icms in ['102','103','300','400'] else icms

	""" Tratando o grupo de ICMS 40 { 41,50,}"""
	xicms = icms
	if icms in ['41','50']:	icms='40'
	
        ricms = etree.SubElement(licms, 'ICMSSN'+__icms if icms in rsimples else 'ICMS'+icms)
        etree.SubElement(ricms, 'orig').text = origem
        etree.SubElement(ricms, 'CSOSN' if icms in rsimples else 'CST').text = xicms

	#--// Icms
        if tags:
            for i in tags:
                if tags[i]: etree.SubElement(ricms, i ).text = tags[i]

	if ipi:
	    lipt = etree.SubElement(raiz, 'IPI')
	    etree.SubElement(lipt, 'cEnq').text = "999"
	    lipi = etree.SubElement(lipt, 'IPITrib')
	    etree.SubElement(lipi, 'CST').text = '50'
	    for i in ipi:
		if ipi[i]:	etree.SubElement(lipi, i).text = ipi[i]
		    	
        if pis and pis:

	    lpis = etree.SubElement(raiz, 'PIS')
	    if pis['CST'] in ['01','02']:	cpis = etree.SubElement(lpis, 'PISAliq')
	    elif pis['CST'] in ['99']:	cpis = etree.SubElement(lpis, 'PISOutr')
	    else:	cpis = etree.SubElement(lpis, 'PISNT')
			
	    for i in pis:
		if pis[i]: etree.SubElement(cpis, i ).text = pis[i]

	if cofins and cofins:
	    		
	    lcofins = etree.SubElement(raiz, 'COFINS')
	    if cofins['CST'] in ['01','02']:	ccofins = etree.SubElement(lcofins, 'COFINSAliq')
	    elif cofins['CST'] in ['99']:	ccofins = etree.SubElement(lcofins, 'COFINSOutr')
	    else:	ccofins = etree.SubElement(lcofins, 'COFINSNT')
	    
	    for i in cofins:
		if cofins[i]: etree.SubElement(ccofins, i ).text = cofins[i]

	if difal:
	    ldifal = etree.SubElement(raiz, 'ICMSUFDest')
	    for i in difal:
		if difal[i]: etree.SubElement(ldifal, i ).text = difal[i]
	    
        return raiz

    def devolucaoImposto(self,tags=None):

        raiz = etree.Element('impostoDevol')
        etree.SubElement(raiz, "pDevol").text=tags['pDevol']
        IPI = etree.SubElement(raiz, "IPI")
        etree.SubElement(IPI, "vIPIDevol").text=tags['vIPIDevol']

        return raiz

    def infadProdutos(self,raiz=None,tags=None):

        etree.SubElement(raiz,"infAdProd").text=mnf.acentos(tags)
	return raiz

    def totalizacaoNotaFiscal(self, tags=None):

        raiz = etree.Element('total')
        icms = etree.SubElement(raiz, "ICMSTot")
        for i in tags:  etree.SubElement(icms, i ).text = tags[i]

        return raiz

class manutencaoNfe:

    def acentos(self,txt):
        
        txt = txt.replace('\n','').replace('\r','')
        if type(txt) == unicode:  return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')
        else:   return txt

mnf = manutencaoNfe()
