#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import datetime
from decimal  import *
import os

from xml.dom import minidom
import xml.dom.minidom

from reportlab.lib.pagesizes import letter,A4,inch,landscape
from StringIO import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep,Color, black, blue, red, green, yellow, orange, magenta, violet, pink, brown,HexColor

from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm,cm
from conectar import sqldb,login,dialogos,relatorios,gerenciador,formasPagamentos,truncagem,listaemails,diretorios,numeracao,acesso

nF  = numeracao()
acs = acesso()
alertas = dialogos()

class danfeGerar:
	
	xmlFilial = ""
	codModulo = ""
	codigo = ['']
	
	def XMLLeitura(self,dom,pai,filho ):

		campos  = dom.getElementsByTagName(pai)
		valores = []
		aTribuT = ''
		
		if campos != []:	#-:[ Campo pai existir ]
			
			for node in campos:

				""" Pegar Atributos ex: ID da NFE """
				aTribuT = node.getAttribute(filho)
				
				flista=node.getElementsByTagName(filho)

				if flista != []:	#-:[ Campo filho existir ]
							
					for fl in flista:
						if fl.firstChild != None:
							
							dados = fl.firstChild.nodeValue
							valores.append(dados)

						else:
		
							""" Retorno vazio preenchimento 0.0000 para valores,percentuais,quantidades """
							if filho[:1] == 'p' or filho[:1] == 'v'	or filho[:1] == 'q':	valores.append('0.00')
							else:	valores.append('')

				else:
		
					""" Retorno vazio preenchimento 0.0000 para valores,percentuais,quantidades """
					if filho[:1] == 'p' or filho[:1] == 'v'	or filho[:1] == 'q':	valores.append('0.00')
					else:	valores.append('')

		else:	#-:[ Campo pai nao existir ]

			""" Preenche lacunas do impostor vazio p/apresentar no campo especifico """
			for i in self.codigo:
				
				""" Retorno vazio preenchimento 0.0000 para valores,percentuais,quantidades """
				if filho[:1] == 'p' or filho[:1] == 'v'	or filho[:1] == 'q':	valores.append('0.00')
				else:	valores.append('')
							
		return valores,aTribuT
			
	def MontarDanfe(self, par, arquivo='', TexTo='', emails = [''], Filial = "", automatico = False ):

		try:
			
			if arquivo !='':	doc = xml.dom.minidom.parse( arquivo )
			elif TexTo !='':	doc = xml.dom.minidom.parseString( TexTo )
			else:	return

		except Exception, _reTornos:
			
			alertas.dia( par, "Erro na abertura do XML\n\n"+str( _reTornos ),"Abertura do XML")
			return
		
#-------: Retorno SEFAZ
		danfeGerar.codigo = ['']
		idch,aT = self.XMLLeitura(doc,"infNFe","Id") #-:[ Numero do DANFE ]
		self.idch = aT

		self.prve,ve = self.XMLLeitura(doc,"protNFe","versao") #---: Versao NFE
		self.pram,am = self.XMLLeitura(doc,"infProt","tpAmb") #----: Ambiente
		self.prda,da = self.XMLLeitura(doc,"infProt","chNFe") #----: Numero do DANFE
		self.prdr,dr = self.XMLLeitura(doc,"infProt","dhRecbto") #-: DaTa Recebimento
		self.prpr,pr = self.XMLLeitura(doc,"infProt","nProt") #----: Protocolo
		self.prcs,cs = self.XMLLeitura(doc,"infProt","cStat") #----: Codigos de Retorno
		self.ve = ve

#-------: Identificacao
		self.idcu,aT = self.XMLLeitura(doc,"ide","cUF")		 #--:[ Codigo da Unidade Federal ]
		self.idcn,aT = self.XMLLeitura(doc,"ide","cNF")		 #--:[ Codigo que compoe a chave da nfe ]
		self.idno,aT = self.XMLLeitura(doc,"ide","natOp")	 #--:[ Natureza da Operacao ]
		self.idpg,aT = self.XMLLeitura(doc,"ide","indPag")	 #--:[ Indicador da forma de pagamento ]
		self.idsr,aT = self.XMLLeitura(doc,"ide","serie")	 #--:[ Numero de Serie da NFE  ]
		self.idnf,aT = self.XMLLeitura(doc,"ide","nNF") 	 #--:[ Numero da NFE ]
		self.idem,aT = self.XMLLeitura(doc,"ide","dEmi")	 #--:[ Data de Emissao ]
		self.ide3,aT = self.XMLLeitura(doc,"ide","dhEmi")	 #--:[ Data de Emissao 3.10]
		self.idds,aT = self.XMLLeitura(doc,"ide","dSaiEnt")  #--:[ Data de Saida ]
		self.idd3,aT = self.XMLLeitura(doc,"ide","dhSaiEnt") #--:[ Data de Saida 3.10]
		self.idhr,aT = self.XMLLeitura(doc,"ide","hSaiEnt")  #--:[ Horario de Saida ]
		self.idtn,aT = self.XMLLeitura(doc,"ide","tpNF")	 #--:[ Tipo da NFE { 0-Entrada 1-Saida } ]
		self.idcm,aT = self.XMLLeitura(doc,"ide","cMunFG")	 #--:[ Codigo do Municipio ]
		self.idrp,aT = self.XMLLeitura(doc,"ide","tpImp")	 #--:[ Formato de Impressão do DANFE 1-Retrato 2-Paisagem ]
		self.idnc,aT = self.XMLLeitura(doc,"ide","tpEmis")	 #--:[ Forma de Emissão da NF-e 1-normal 2-contigencia ]
		self.iddg,aT = self.XMLLeitura(doc,"ide","cDV")		 #--:[ Dígito Verificador da Chave de Acesso da NF-e ]
		self.idam,aT = self.XMLLeitura(doc,"ide","tpAmb")	 #--:[ Tipo de Ambiente  { 1-Producao 2-Homologacao } ]
		self.idfi,aT = self.XMLLeitura(doc,"ide","finNFe")	 #--:[ Finalidade de emissão da NF-e 1 a NF-e normal/ 2-NF-e complementar / 3 – NF-e de ajuste  ]
		self.idvp,aT = self.XMLLeitura(doc,"ide","verProc")  #--:[ Emissor da DANFE ]

		self.iadp,aT = self.XMLLeitura(doc,"det","infAdProd") #-:[ Dados Adicionais do produto ]

#-------: Emitente
		self.emcu,aT = self.XMLLeitura(doc,"emit","CNPJ")		#-:[ Codigo da Unidade Federal ]
		self.emnm,aT = self.XMLLeitura(doc,"emit","xNome")		#-:[ Codigo da Unidade Federal ]
		self.emft,aT = self.XMLLeitura(doc,"emit","xFant")		#-:[ Codigo da Unidade Federal ]
		self.emlg,aT = self.XMLLeitura(doc,"emit","xLgr")		#-:[ Codigo da Unidade Federal ]
		self.emnr,aT = self.XMLLeitura(doc,"emit","nro")		#-:[ Codigo da Unidade Federal ]
		self.emcl,aT = self.XMLLeitura(doc,"emit","xCpl")       #-:[ Complemento ]
		self.embr,aT = self.XMLLeitura(doc,"emit","xBairro")	#-:[ Codigo da Unidade Federal ]
		self.emcm,aT = self.XMLLeitura(doc,"emit","cMun")		#-:[ Codigo da Unidade Federal ]
		self.emmu,aT = self.XMLLeitura(doc,"emit","xMun")		#-:[ Codigo da Unidade Federal ]
		self.emuf,aT = self.XMLLeitura(doc,"emit","UF")			#-:[ Codigo da Unidade Federal ]
		self.emce,aT = self.XMLLeitura(doc,"emit","CEP")		#-:[ Codigo da Unidade Federal ]
		self.emcp,aT = self.XMLLeitura(doc,"emit","cPais")		#-:[ Codigo da Unidade Federal ]
		self.empa,aT = self.XMLLeitura(doc,"emit","xPais")		#-:[ Codigo da Unidade Federal ]
		self.emfn,aT = self.XMLLeitura(doc,"emit","fone")		#-:[ Codigo da Unidade Federal ]
		self.emie,aT = self.XMLLeitura(doc,"emit","IE")			#-:[ Insc.Estadua ]
		self.emis,aT = self.XMLLeitura(doc,"emit","IEST")		#-:[ Insc.Estadua Substituto ]
		self.emim,aT = self.XMLLeitura(doc,"emit","IM")			#-:[ Insc.Municipal ]
		self.emcn,aT = self.XMLLeitura(doc,"emit","CNAE")		#-:[ Este campo deve ser informado quando o campo IM for informadol ]
		self.emcr,aT = self.XMLLeitura(doc,"emit","CRT")		#-:[ Codigo de Regime Tributario 1-Simples Nacional 2-Simples Nacional - excesso de sublimite da receita bruta 3-Normal ]

#------: Destinatario
		self.decu,aT = self.XMLLeitura(doc,"dest","CNPJ") #----: CNPJ
		self.dcpf,aT = self.XMLLeitura(doc,"dest","CPF") #-----: CPF
		self.denm,aT = self.XMLLeitura(doc,"dest","xNome") #---: Nome
		self.deen,aT = self.XMLLeitura(doc,"dest","xLgr") #----: Endereco
		self.denu,aT = self.XMLLeitura(doc,"dest","nro") #-----: Numero
		self.decl,aT = self.XMLLeitura(doc,"dest","xCpl") #----: Complemento
		self.deba,aT = self.XMLLeitura(doc,"dest","xBairro") #-: Bairro
		self.demu,aT = self.XMLLeitura(doc,"dest","xMun") #----: Municipio
		self.deuf,aT = self.XMLLeitura(doc,"dest","UF") #------: UF
		self.decp,aT = self.XMLLeitura(doc,"dest","CEP") #-----: CEP
		self.defn,aT = self.XMLLeitura(doc,"dest","fone") #----: Telefone
		self.deie,aT = self.XMLLeitura(doc,"dest","IE") #------: Inscricao Estadual

#-------: Endereco de Entrega
		self.edcu,aT = self.XMLLeitura(doc,"entrega","CNPJ") #----: CNPJ
		self.edlg,aT = self.XMLLeitura(doc,"entrega","xLgr") #----: Endereco
		self.ednu,aT = self.XMLLeitura(doc,"entrega","nro") #-----: Numero
		self.edcl,aT = self.XMLLeitura(doc,"entrega","xCpl") #----: Complemento
		self.edbr,aT = self.XMLLeitura(doc,"entrega","xBairro") #-: Bairro
		self.edce,aT = self.XMLLeitura(doc,"entrega","cMun") #----: Codigo do municipio { CEP }
		self.edmu,aT = self.XMLLeitura(doc,"entrega","xMun") #----: Municipio
		self.eduf,aT = self.XMLLeitura(doc,"entrega","UF") #------: UF

#------: Duplicata/Fatura
		self.Dnum,aT = self.XMLLeitura(doc,"dup","nDup") #--: Numero
		self.dven,aT = self.XMLLeitura(doc,"dup","dVenc") #-: Vencimento
		self.Dvlr,aT = self.XMLLeitura(doc,"dup","vDup") #--: Valor 

#-------: Impostos
		self.Tvbc,aT = self.XMLLeitura(doc,"ICMSTot","vBC")		#-:[ Valor da Base de Calculo do ICMS ]
		self.Tvic,aT = self.XMLLeitura(doc,"ICMSTot","vICMS")	#-:[ Valor do ICMS ]
		self.Tvbs,aT = self.XMLLeitura(doc,"ICMSTot","vBCST")	#-:[ Valor da Base de Calculo da ST ]
		self.Tvst,aT = self.XMLLeitura(doc,"ICMSTot","vST")		#-:[ Valor da ST ]
		self.Tvpd,aT = self.XMLLeitura(doc,"ICMSTot","vProd")	#-:[ Valor dos Produtos ]
		self.Tvfr,aT = self.XMLLeitura(doc,"ICMSTot","vFrete")	#-:[ Valor do  Frete ]
		self.Tvsg,aT = self.XMLLeitura(doc,"ICMSTot","vSeg")	#-:[ Valor do  Seguro ]
		self.Tvds,aT = self.XMLLeitura(doc,"ICMSTot","vDesc")	#-:[ Valor do  Desconto ]
		self.Tvii,aT = self.XMLLeitura(doc,"ICMSTot","vII")		#-:[ Valor do  Imposto de Importacao ]
		self.Tvip,aT = self.XMLLeitura(doc,"ICMSTot","vIPI")	#-:[ Valor do  IPI ]
		self.Tvps,aT = self.XMLLeitura(doc,"ICMSTot","vPIS")	#-:[ Valor do  PIS ]
		self.Tvcf,aT = self.XMLLeitura(doc,"ICMSTot","vCOFINS")	#-:[ Valor do  COFINS ]
		self.Tvou,aT = self.XMLLeitura(doc,"ICMSTot","vOutro")	#-:[ Valor do  Outros Valores ]
		self.Tvnf,aT = self.XMLLeitura(doc,"ICMSTot","vNF")		#-:[ Valor da  Nota Fiscal ]

#-------: Transportadora
		self.TraFpc,aT = self.XMLLeitura(doc,"transp","modFrete") #---:[ Frete por conta ]
		self.TraCNP,aT = self.XMLLeitura(doc,"transporta","CNPJ") #---:[ CNPJ ]
		self.TraCPF,aT = self.XMLLeitura(doc,"transporta","CPF") #----:[ CPF ]
		self.TraNom,aT = self.XMLLeitura(doc,"transporta","xNome") #--:[ Nome ]
		self.TraIES,aT = self.XMLLeitura(doc,"transporta","IE") #-----:[ Inscricao Estadual ]
		self.TraEnd,aT = self.XMLLeitura(doc,"transporta","xEnder") #-:[ Endereco ]
		self.TraMun,aT = self.XMLLeitura(doc,"transporta","xMun") #---:[ Codigo do Municipio ]
		self.TraUfe,aT = self.XMLLeitura(doc,"transporta","UF") #-----:[ Unidade Federal ]

		self.TrapVe,aT = self.XMLLeitura(doc,"veicTransp","placa") #-:[ Placa do Veiculo ]
		self.TraUFv,aT = self.XMLLeitura(doc,"veicTransp","UF") #----:[ Unidade Federal ]
		self.TraRNT,aT = self.XMLLeitura(doc,"veicTransp","RNTC") #--:[ ANTT - Cpdog Nacional da Transportadora ]

		self.TraVol,aT = self.XMLLeitura(doc,"vol","qVol") #--:[ Quantidade Volume ]
		self.TraEsp,aT = self.XMLLeitura(doc,"vol","esp") #--:[ Especie ]
		self.TraMar,aT = self.XMLLeitura(doc,"vol","marca") #-:[ Marca ]
		self.TranVo,aT = self.XMLLeitura(doc,"vol","nVol") #--:[ Numeroacao ]
		self.TraPsL,aT = self.XMLLeitura(doc,"vol","pesoL") #-:[ Peso Liquido ]
		self.TraPsB,aT = self.XMLLeitura(doc,"vol","pesoB") #-:[ Peso Bruto   ]

#-------: Classificar Produtos
		self.ccd,aT = self.XMLLeitura(doc,"prod","cProd")
		danfeGerar.codigo = self.ccd
		
		self.cbr,aT = self.XMLLeitura(doc,"prod","cEAN")
		self.dsc,aT = self.XMLLeitura(doc,"prod","xProd")
		self.ncm,aT = self.XMLLeitura(doc,"prod","NCM")
		self.cfo,aT = self.XMLLeitura(doc,"prod","CFOP")
		self.uco,aT = self.XMLLeitura(doc,"prod","uCom")		#-:[ Unidade comercializada ]
		self.qco,aT = self.XMLLeitura(doc,"prod","qCom")		#-:[ Quantidade Comercializada ]
		self.vuc,aT = self.XMLLeitura(doc,"prod","vUnCom")		#-:[ Valor da unidade comercializada ]
		self.vTp,aT = self.XMLLeitura(doc,"prod","vProd")		#-:[ Valor Total do Produto ]
		self.uTb,aT = self.XMLLeitura(doc,"prod","uTrib")		#-:[ Unidade Tributada ]
		self.qTv,aT = self.XMLLeitura(doc,"prod","qTrib")		#-:[ Quantidade Tributada ]
		self.vuT,aT = self.XMLLeitura(doc,"prod","vUnTrib")		#-:[ Valor da Unidade Tributada ]
		self.npd,aT = self.XMLLeitura(doc,"prod","xPed")		#-:[ Numero do Pedido ]
		self.cfi,aT = self.XMLLeitura(doc,"prod","nFCI")		#-:[ CFI-Controle da Ficha de Importacao ]

		#----: Imposto ICMS
		self.cso,aT = self.XMLLeitura(doc,"ICMS","orig")		#-:[ Origem da Mercadoria ]
		self.cst,aT = self.XMLLeitura(doc,"ICMS","CST")  		#-:[ CST CSOSN ]
		self.csn,aT = self.XMLLeitura(doc,"ICMS","CSOSN")		#-:[ CST CSOSN ]

		self.imb,aT = self.XMLLeitura(doc,"ICMS","modBC")		#-:[ Modalidade da Base de Calculo ]
		self.ivb,aT = self.XMLLeitura(doc,"ICMS","vBC")		#-:[ Valor da Base de Calculo  ]
		self.ipe,aT = self.XMLLeitura(doc,"ICMS","pICMS")		#-:[ Percentual do ICMS ]
		self.ivi,aT = self.XMLLeitura(doc,"ICMS","vICMS")		#-:[ Valor do ICMS ]
		self.ims,aT = self.XMLLeitura(doc,"ICMS","modBCST")	#-:[ Modalidade de determinação da Base de Cálculo do ICMS ST ]
		self.ipm,aT = self.XMLLeitura(doc,"ICMS","pMVAST")		#-:[ Percentual do MVA-ST ]
		self.ibs,aT = self.XMLLeitura(doc,"ICMS","vBCST")		#-:[ Valor da Base de Calculo ST ]
		self.ips,aT = self.XMLLeitura(doc,"ICMS","pICMSST")	#-:[ Percentual do ICMS ST ]
		self.ivs,aT = self.XMLLeitura(doc,"ICMS","vICMSST")	#-:[ Valor do ICMS ST ]

		#----: IPI
		self.pce,aT = self.XMLLeitura(doc,"IPI","cEnq")	#-:[ Código de Enquadramento Legal do IPI ]
		self.pcs,aT = self.XMLLeitura(doc,"IPI","CST")		#-:[ Codigo CST ]
		self.pbc,aT = self.XMLLeitura(doc,"IPI","vBC")		#-:[ Base de Calcuo IPI ]
		self.ppe,aT = self.XMLLeitura(doc,"IPI","pIPI")	#-:[ Percentual do IPI ]
		self.pvl,aT = self.XMLLeitura(doc,"IPI","vIPI")	#-:[ Valor do IPI ]

		#----: PIS
		self.scs,aT = self.XMLLeitura(doc,"PIS","CST")		#-:[ Codigo CST ]
		self.sbc,aT = self.XMLLeitura(doc,"PIS","vBC")		#-:[ Base de Calcuo IPI ]
		self.spe,aT = self.XMLLeitura(doc,"PIS","pPIS")	#-:[ Percentual do IPI ]
		self.svl,aT = self.XMLLeitura(doc,"PIS","vPIS")	#-:[ Valor do IPI ]

		#----: COFINS
		self.fcs,aT = self.XMLLeitura(doc,"COFINS","CST")		#-:[ Codigo CST ]
		self.fbc,aT = self.XMLLeitura(doc,"COFINS","vBC")		#-:[ Base de Calcuo IPI ]
		self.fpe,aT = self.XMLLeitura(doc,"COFINS","pCOFINS")	#-:[ Percentual do IPI ]
		self.fvl,aT = self.XMLLeitura(doc,"COFINS","vCOFINS")	#-:[ Valor do IPI ]

		#----: Referenciar ECF
		self.ecm,aT = self.XMLLeitura(doc,"refECF","mod")		#-:[ Modelo ]
		self.ecn,aT = self.XMLLeitura(doc,"refECF","nECF")		#-:[ Numero Sequencial do ECF ]
		self.eco,aT = self.XMLLeitura(doc,"refECF","nCOO")	    #-:[ Numero do COO ]
		
#-------: Dados Adicionais
		self.TraAdi,aT = self.XMLLeitura(doc,"infAdic","infCpl") #------:[ Dados Adicionais Informacoes Comprlementares ]

		filial = self.emft[0].lower().replace(' ','')
		nomeArquivo = diretorios.usPasta+str( self.prda[0] )+"-"+filial+".pdf"
		cv = canvas.Canvas(nomeArquivo, pagesize=A4)
		cv.setLineWidth(.3)

#-------: Confecciona DANFE Vazio, Imprimir o cabecalho	
		#----: Calcular Numero de Paginas
		self.Tp = 1
		Ti = len(self.ccd)
		for i in range( len( self.ccd ) ): 

			#if len( str( self.dsc[i] ) ) > 60:	Ti +=1
			if len( self.dsc[i] ) > 60:	Ti +=1

		if self.iadp !=[]:
			
			for a in self.iadp:
				
				if a !='':	Ti +=1

		if Ti > 22:

			self.Tp = int( str( ( float( Ti + 1 ) / 22 ) ).split('.')[0] )
			if Decimal( str( ( float( Ti + 1 ) / 22 ) ).split('.')[1] ) !=0:	self.Tp +=1

		self.danfeRetrato(cv) #-: DANFE Vazio
		self.danfeCabecalho(cv,1 ) #---: Cabecalho
		self.RelacionarProdutos(cv)

		cv.showPage ()
		cv.save()

		if automatico == False:
			
			gerenciador.Anexar = nomeArquivo,arquivo

			gerenciador.secund = ''
			gerenciador.emails = emails
			gerenciador.TIPORL = ''
			gerenciador.imprimir = acs.acsm(self.codModulo,True)
			gerenciador.Filial  = self.xmlFilial
				
			ger_frame=gerenciador(parent=par,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

		else:	return nomeArquivo
			#par.r = nomeArquivo

	def danfeCabecalho(self,cv,pg):

#------: Inserir Logomarca dados do Emitente e Referencia da NF

		danf = ""
		for i in range( len( str( self.prda[0] ) ) /3 ):
			danf += str( self.prda[0] )[(i*4):( (i*4) +4 )]+" "

		b128 = code128.Code128(str( self.prda[0] ), barHeight=35, barWidth=0.7,stop=1)

		proTDaTa = str( self.prpr[0] )+"  -  "+str( self.prdr[0] )
		TPregime = "Simples Nacional"
		if str( self.emcr[0] ).strip() == "2":	TPregime = "Simples Nacional-excesso de sublimite da receita bruta"
		if str( self.emcr[0] ).strip() == "3":	TPregime = "Normal"

		cv.setFillColor(HexColor('0x777777'))
		cv.setFont('Helvetica-Bold', 5)
		cv.drawString(20,772,"Regime: "+TPregime)

		cv.setFont('Helvetica', 6)
		cv.setFillColor(HexColor('0x000000'))
		cv.drawString(262,720,"Versão "+str( self.ve ) ) #----: Versao da NFE
		cv.drawString(22, 812,"RECEBEMOS DE" )
		cv.drawString(22, 802,"OS PRODUTOS E/OU SERVIÇOS CONSTANTES DA NOTA FISCAL ELETRÔNICA INDICADA AO LADO")
		
		""" Busca a Logomarca da Empresa dentro de um dicionario """
		_docXML = str( self.emcu[0] ).strip()
		_docEMP = login.filialLT[ self.xmlFilial ][9].strip()
		_logMar = login.filialLT[ self.xmlFilial ][15].strip()

		if _docXML == _docEMP and _logMar !='' and os.path.exists("imagens/"+_logMar) == True:	cv.drawImage(ImageReader("imagens/"+_logMar), 25,705, width=100, height=60)
		else:
			cv.rect(22, 710,206,58, fill=0) #--: Emitente
			cv.setFillColor(HexColor('0x7F7F7F'))
			cv.setFont('Helvetica-Bold', 10)
			cv.drawString(24 ,755,str( self.emft[0].split(' ')[0] ).upper() )
			cv.drawString(24 ,740,str( self.emnm[0][:40] ).title() )

		cv.setFillColor(HexColor('0x000000'))
		cv.setFont('Helvetica-Bold', 6)
		cv.drawString(72,812, self.emnm[0].upper() ) #-: Recebemos de 

		cv.setFont('Helvetica-Bold', 8)
		cv.drawString(22 ,700, self.emnm[0].title()) #-----------------------------------------------------------------: Nome
		cv.drawString(22 ,690, self.emlg[0].title()+" "+ self.emnr[0].title()+" "+ self.emcl[0].title()) #-: Endereco,Nr,Complemento
		cv.drawString(22 ,680, self.embr[0].title() ) #----------------------------------------------------------------: Bairro
		cv.drawString(22 ,670, self.converte( str( self.emce[0] ), 2)+" "+ self.emmu[0].title()+" "+ self.emuf[0] ) #-: CEP,Municipio,Estado
		cv.drawString(22 ,660, "Telefone(s): "+self.converte(str( self.emfn[0] ),1) ) #-------------------------------------------: Telefone
		cv.setFont('Helvetica-Bold', 7.7)
		b128.drawOn(cv, 345, 730) #--------------------: Codigo de Barras
		cv.drawString(355,708, danf.strip()) #---------: Chave de Acesso
		cv.drawString(22, 638, self.idno[0] ) #-: Natureza da Operacao
		cv.drawString(352,638, proTDaTa) #-------------: Procolo + Data Recebimento
		cv.drawString(22, 618, str( self.emie[0] ) ) #-: Insc.Estadual
		cv.drawString(175,618, str( self.emis[0] ) ) #-: INSCRIÇÃO ESTADUAL DO SUBSTITUTO TRIBUTÁRIO
		cv.drawString(352,618, self.converte(str( self.emcu[0] ),4) ) #-: CNPJ

		_nf = str( self.idnf[0] ).zfill(9)
		_sr = str( self.idsr[0] ).zfill(3)
		_nf = _nf[:3]+"."+_nf[3:6]+"."+_nf[6:]
		
		cv.setFont('Helvetica-Bold', 10)
		cv.drawString(310,704,str( self.idtn[0] ) ) #-: Entrada Saida

		cv.drawString(487,805,"Nº "+_nf)
		cv.drawString(497,792,"SÉRIE "+_sr)

		cv.drawString(242,685,"Nº "+_nf)
		cv.drawString(252,673,"SÉRIE "+_sr)
		cv.drawString(242,660,"FOLHA "+str(pg)+"-"+str(self.Tp))

#-------: Dados do Destinatario
		cv.setFont('Helvetica-Bold', 8)
		
		emi = self.idem[0]
		des = self.idds[0]
		hes = self.idhr[0]
		if self.ide3[0] !='':	emi = self.ide3[0][:10] #----------:Retorno da DataHora Emissao 3.10
		if self.idd3[0] !='':	des = self.idd3[0][:10] #----------:Retorno da DataHora E/S 3.10
		if self.idd3[0] !='':	hes = self.idd3[0].split("T")[1] #-:Retorno da Hora E/S 3.10

		cv.drawString(22, 585, self.denm[0] )
		cv.drawString(392,585, self.converte(str( self.decu[0] ),4) )
		if self.dcpf[0] !="":	cv.drawString(392,585, self.converte(str( self.dcpf[0] ),4) )
		if emi !='':	cv.drawString(502,585, self.converte( str( emi ),3) ) #------------------------------------------: DataHora da Emissao
		cv.drawString(22, 565, self.deen[0]+", "+self.denu[0]+" "+self.decl[0] )
		cv.drawString(312,565, self.deba[0] )
		cv.drawString(432,565, self.converte( str( self.decp[0] ) ,2) )
		if des !='':	cv.drawString(502,565, self.converte( str( des ) ,3) ) #-----------------: DataHora E/S
		cv.drawString(22, 545, self.demu[0] )
		cv.drawString(262,545, self.converte( str( self.defn[0] ) ,1) )
		cv.drawString(382,545, str( self.deuf[0] ) )
		cv.drawString(402,545, str( self.deie[0] ) )
		cv.drawString(502,545, str( hes ) ) #------------------------------------: Hora E/S

#-------: Local de Entrega
		cv.setFont('Helvetica-Bold', 6)
		cv.drawString(22, 465, self.edlg[0]+", "+ self.ednu[0] +" "+ self.edcl[0] ) #-: Endereco,Numero,Complemento
		cv.drawString(252,465, self.edbr[0] ) #-: Bairro
		cv.drawString(352,465, self.edmu[0] ) #-: Municipio
		cv.drawString(452,465, self.eduf[0] ) # : UF
#		cv.drawString(472,465, self.converte( str( self.edce[0] ), 2) ) # : CEP
		cv.drawString(472,465, str( self.edce[0] ) ) # : CEP
		cv.drawString(512,465, self.converte( str( self.edcu[0] ), 4) ) # : CNPJ/CPF

#-------: Duplicata/Fatura
		if self.Dnum[0] !='':

			nDpl = len( self.Dnum )
			cowl = 115
			
			cv.setFillColor(HexColor('0x7F7F7F'))
			cv.setFont('Helvetica-Bold', 4)
			if len( self.Dnum ) > 5:	nDpl = 5
			if len( self.Dnum ) > 5:	cv.drawString(522,500,"Mais...")
			cv.setFillColor(HexColor('0x000000'))

			for i in range( nDpl ):

				if self.Dnum[i] !='':

					cv.setFont('Helvetica-Bold', 5)
					cv.drawRightString(cowl,518, str( self.Dnum[i] ) )
					cv.setFont('Helvetica-Bold', 6)
					cv.drawRightString(cowl,508, self.converte( str( self.dven[i] ), 3) )
					cv.drawRightString(cowl,500, format( Decimal( str( self.Dvlr[i] ) ),',' ) )
					
					cowl +=100

#------: Transportadora
		cv.setFont('Helvetica-Bold', 6)
		fTc = "0-Emitente"
		if str( self.TraFpc[0] ) == "1":	fTc = "1-Destinatario"
		if str( self.TraFpc[0] ) == "2":	fTc = "2-Terceiros"
		if str( self.TraFpc[0] ) == "9" or str( self.TraFpc[0] ) == "":	fTc = "9-Sem Frete"

		if str( self.TrapVe[0] ).replace('.','').isdigit() == False:	placa = str( self.TrapVe[0] )
		else:	placa = ""

		cv.drawString(22, 377, str( self.TraNom[0] ) ) #--------------------: Nome
		cv.drawString(262,377, fTc ) #--------------------------------------: Frete por Conta
		cv.drawString(322,377, str( self.TraRNT[0] ) ) #--------------------: Codigo ANTT
		cv.drawString(382,377, placa ) #------------------------------------: Placa do Veiculo
		cv.drawString(442,377, self.TraUFv[0] ) #--------------------: UF-Veiculo

		if self.TraCNP[0]:	cv.drawString(462,377, self.converte( str( self.TraCNP[0] ), 4) ) #-: CNPJ-CPF
		else:	cv.drawString(462,377, self.converte( str( self.TraCPF[0] ), 4) ) #-: CNPJ-CPFself.TraCPF
		
		cv.drawString(22, 362, self.TraEnd[0] ) #--------------------: Endereco
		cv.drawString(262,362, self.TraMun[0] ) #--------------------: Municipio
		cv.drawString(442,362, self.TraUfe[0] ) #--------------------: UF-Transportadora
		cv.drawString(462,362, str( self.TraIES[0] ) ) #--------------------: IE

		if Decimal( str( self.TraVol[0] ) ) !=0:	cv.drawRightString(88, 342, format( Decimal( str( self.TraVol[0] ) ),',' ) ) #-: Volume Quantidade
		cv.drawString(92, 342, str( self.TraEsp[0] ) ) #-: Especie
		cv.drawString(162,342, str( self.TraMar[0] ) ) #---------: Marca
		cv.drawRightString(358,342, str( self.TranVo[0] ) ) #----: Numeracao

		if Decimal( str( self.TraPsB[0] ) ) !=0:	cv.drawRightString(458,342, format( Decimal( str( self.TraPsB[0] ) ),',' ) ) #-: Peso Bruto
		if Decimal( str( self.TraPsL[0] ) ) !=0:	cv.drawRightString(568,342, format( Decimal( str( self.TraPsL[0] ) ),',' ) ) #-: Peso Liquido

#------: Tributos
		cv.setFont('Helvetica-Bold', 7)
		if Decimal( str( self.Tvbc[0] ) ) !=0:	cv.drawRightString(138, 430, format( Decimal( str( self.Tvbc[0] ) ),',' ) ) #-: Base Calculo ICMS
		if Decimal( str( self.Tvic[0] ) ) !=0:	cv.drawRightString(262, 430, format( Decimal( str( self.Tvic[0] ) ),',' ) ) #-: Valor ICMS
		if Decimal( str( self.Tvbs[0] ) ) !=0:	cv.drawRightString(368, 430, format( Decimal( str( self.Tvbs[0] ) ),',' ) ) #-: Base Calculo ST
		if Decimal( str( self.Tvst[0] ) ) !=0:	cv.drawRightString(458, 430, format( Decimal( str( self.Tvst[0] ) ),',' ) ) #-: Valor ST
		if Decimal( str( self.Tvpd[0] ) ) !=0:	cv.drawRightString(568, 430, format( Decimal( str( self.Tvpd[0] ) ),',' ) ) #-: Valor dos Produtos
		if Decimal( str( self.Tvfr[0] ) ) !=0:	cv.drawRightString(92,  410, format( Decimal( str( self.Tvfr[0] ) ),',' ) ) #-: Valor do frete
		if Decimal( str( self.Tvsg[0] ) ) !=0:	cv.drawRightString(185, 410, format( Decimal( str( self.Tvsg[0] ) ),',' ) ) #-: Valor do seguro
		if Decimal( str( self.Tvds[0] ) ) !=0:	cv.drawRightString(263, 410, format( Decimal( str( self.Tvds[0] ) ),',' ) ) #-: Valor do desconto
		if Decimal( str( self.Tvou[0] ) ) !=0:	cv.drawRightString(368, 410, format( Decimal( str( self.Tvou[0] ) ),',' ) ) #-: Outros Valores [ Despesas Acessorias ]
		if Decimal( str( self.Tvip[0] ) ) !=0:	cv.drawRightString(458, 410, format( Decimal( str( self.Tvip[0] ) ),',' ) ) #-: Valor do IPI
		if Decimal( str( self.Tvnf[0] ) ) !=0:	cv.drawRightString(568, 410, format( Decimal( str( self.Tvnf[0] ) ),',' ) ) #-: Valor Total da Nota

		#-----: Mostar Pis-Cofins
		if ( Decimal( str( self.Tvps[0] ) ) + Decimal( str( self.Tvcf[0] ) ) ) !=0:

			cv.line(370,447,370,458 ) #-: Divisao de Impostos, Valor ICMS ST,Valor do IPI
			cv.line(460,447,460,458 ) #-: Divisao de Impostos, Valor ICMS ST,Valor do IPI

			cv.setFont('Helvetica-Bold', 5)
			cv.setFillColor(HexColor('0x4D4D4D'))
			if Decimal( str( self.Tvps[0] ) ) !=0:	cv.drawRightString(458, 450, format( Decimal( str( self.Tvps[0] ) ),',' ) ) #-: Valor do PIS
			if Decimal( str( self.Tvcf[0] ) ) !=0:	cv.drawRightString(568, 450, format( Decimal( str( self.Tvcf[0] ) ),',' ) ) #-: Valor do COFINS

#------: Dados Adicionais
		cv.setFillColor(HexColor('0x4D4D4D'))
		cv.setFont('Helvetica-Bold', 5)

		dd = unicode( self.TraAdi[0] ).strip()
		if self.ecm[0] !='':

			dd += "|Referencia ECF Modelo: "+str( self.ecm[0] )+" Sequencial ECF: "+str( self.ecn[0] )+" Nº COO: "+str( self.eco[0] ).decode("utf-8")

		aa = dd.split('\n')
		ab = dd.split(';')
		ac = dd.split('|')
		ad = dd.split('[q]')
	
		ia = []
		if len( dd ) <= 85:	ia.append(dd)
		
		if len( dd ) > 85:

			car = 1
			inf = ""
			for d in dd:

				inf +=d
				if car == 84:	inf +="|"
				if car == 84:	car  = 1
				car +=1

			ia = inf.split('|')

		if len( aa ) > 1:	ia = aa
		if len( ab ) > 1:	ia = ab
		if len( ac ) > 1:	ia = ac
		if len( ad ) > 1:	ia = ad

		fl = 122
		cr = ''
		for mt in ia:

			t = mt.strip() # .lower()
			if len(t) !=0 and len(t) <= 85:	cv.drawString(22,fl,t)
			if len(t) !=0 and len(t) > 85:
				
				Tx = ""
				for tt in t:

					Tx += tt
					if len( Tx ) == 85:

						fl -=5
						cv.drawString(22,fl,Tx)
						Tx = ""
					
				if Tx !="":
					fl -=5
					cv.drawString(22,fl,Tx)
			
			fl -=5
			""" Maximo de caracter em informacoes adicionais """
			for cc in t:	cr +=cc
			if len(cr) > 850:	break
				
		cv.setFillColor(HexColor('0x7F7F7F'))
		cv.setFont('Helvetica-Bold', 5)
		cv.drawString(132,130,str( self.idvp[0] )+" DANFE Gerado em: "+str( datetime.datetime.now().strftime("%d/%m/%Y %T")  ) )
		cv.drawString(282,122,"Reservado ao Fisco")

		""" Ambiente de Homogacao """
		if self.pram[0] == "2" or self.prpr[0] == '':

			cv.setFillColor(HexColor('0xCD4646'))
			cv.setFont('Helvetica-Bold', 30)
			cv.rotate(45) 

			if self.pram[0] == "2":	cv.drawString(100,0, "Ambiente de Homologação { Sem Valor Fiscal }")
			if self.pram[0] == "":	cv.drawString(300,90,"{ Sem Valor Fiscal }")
			cv.rotate(-45) 

	def RelacionarProdutos(self,cv):
		
		cow = 308
		lin = 1
		pag = 1
		tru = truncagem()
		ite = 0
		
		for i in range( len( self.ccd ) ): 
			
			ds = self.dsc[i].strip().upper().split("CI:")[0]

			if self.iadp[i] !='':	ad = self.iadp[i]
			else:	ad = ""
			
			if lin < 23 :	

				cv.setFillColor(HexColor('0x000000'))
				cv.setFont('Helvetica', 6)
				cdn = len( str(self.ccd[i]).upper() ) 
				if cdn > 11 and cdn <= 14:	cv.setFont('Helvetica', 4.6)
				if cdn > 14:	cv.setFont('Helvetica', 4)
				
				cv.drawString(21,  cow, str( self.ccd[i] ).upper() )
				
				cv.setFont('Helvetica', 6)
				cv.drawString(61,  cow, ds[:60] )

				cv.drawString(276, cow, self.ncm[i] )

				if str( self.emcr[0] ).strip() == "3":	cv.drawString(307, cow, str( self.cso[i] ) + str( self.cst[i] ) )
				else:	cv.drawString(307, cow, str( self.cso[i] ) + str( self.csn[i] ) )
				
				cv.drawString(323, cow, self.cfo[i] )
				if ad and ad.split("|")[0] == "PC":	cv.drawString(338, cow, "PC" )
				else:	cv.drawString(338, cow, self.uco[i] )

				vu = str( self.vuc[i] )
				if len( vu.split('.')[1] ) > 4:	vu = vu.split('.')[0]+'.'+vu.split('.')[1][:4]

				cv.setFont('Helvetica', 5)
				if ad and ad.split("|")[0] == "PC":
					
					cv.drawRightString(384, cow, format( Decimal( ad.split("|")[2] ),',' ) )
					cv.drawRightString(419, cow, format( Decimal( ad.split("|")[1] ),',' ) )
				else:
					cv.drawRightString(384, cow, format( Decimal( str( self.qco[i] ) ),',' ) )
					cv.drawRightString(419, cow, format( Decimal( vu ),',' ) )

				cv.drawRightString(454, cow, format( Decimal( str( self.vTp[i] ) ),',' ) )

				cv.setFont('Helvetica', 4)
				if len( self.ivb ) >= ( int(1) + 1 ) and Decimal( str( self.ivb[i] ) ):	cv.drawRightString(477, cow, format( Decimal( str( self.ivb[i] ) ),',' ) )
				cv.setFont('Helvetica', 4.5)
				if len( self.ivi ) >= ( int(1) + 1 ) and Decimal( str( self.ivi[i] ) ):	cv.drawRightString(510, cow, format( Decimal( str( self.ivi[i] ) ),',' ) )
				if len( self.pvl ) >= ( int(i) + 1 ) and Decimal( str( self.pvl[i] ) ):	cv.drawRightString(537, cow, format( Decimal( str( self.pvl[i] ) ),',' ) )
				if len( self.ipe ) >= ( int(1) + 1 ) and Decimal( str( self.ipe[i] ) ):	cv.drawRightString(557, cow, format( tru.trunca( 3, Decimal( str( self.ipe[i] ) ) ),',' ) )
				cv.setFont('Helvetica', 3)
				if len( self.ppe ) >= ( int(i) + 1 ) and Decimal( str( self.ppe[i] ) ):	cv.drawRightString(569, cow, format( Decimal( str( self.ppe[i] ) ),',' ) )
				cv.setFont('Helvetica', 4.5)
				ite +=1
				"""  Descricao do Produto Maior q 60car quebra o texto  """
				if len( ds ) > 60:

					if lin == 22:
		
						self.separaColunas(cv,cow )
						pag +=1
						cv.addPageLabel(pag)
						cv.showPage()						
						
						self.danfeRetrato(cv) #-: DANFE Vazio
						self.danfeCabecalho(cv,pag) #---: Cabecalho
						
						cow = 308
						lin = 1
					else:

						cow -=8
						lin +=1

					cv.setFont('Helvetica', 6)
					cv.setFillColor(HexColor('0x000000'))
					cv.drawString(61,  cow, ds[60:] )

				"""  Dados Adicionais do Produto  """
				
				if ad and ad.split("|")[0] !="PC":

					if lin == 22:
		
						self.separaColunas(cv,cow )
						pag +=1
						cv.addPageLabel(pag)
						cv.showPage()						
						
						self.danfeRetrato(cv) #-: DANFE Vazio
						self.danfeCabecalho(cv,pag) #---: Cabecalho
						
						cow = 308
						lin = 1
					else:

						cow -=8
						lin +=1

					cv.setFont('Helvetica', 6)
					cv.setFillColor(HexColor('0x000000'))
					cv.drawString(61,  cow, ad )

				cv.line(20, ( cow-2 ),570, ( cow-2 ) ) #-: Nome/Razao social,cnpj,data emissao

				if lin == 22:

					self.separaColunas(cv,( cow -2 ) )

					pag +=1
					if pag <= self.Tp:

						cv.addPageLabel(pag)
						cv.showPage()						

						self.danfeRetrato(cv) #-: DANFE Vazio
						self.danfeCabecalho(cv,pag) #---: Cabecalho

					cow = 316
					lin = 1

				cow -=8
			lin +=1

		if lin > 22:	self.separaColunas(cv,cow)
		else:	self.separaColunas(cv,( cow + 6 ) )
		
	def separaColunas(self,cv,cow):
		
		cv.line(60,  cow , 60,314 ) #-: Codigo,Descricao dos produtos
		cv.line(275, cow ,275,314 ) #-: NCM/SH
		cv.line(305, cow ,305,314 ) #-: CST
		cv.line(321, cow ,321,314 ) #-: CFOP
		cv.line(337, cow ,337,314 ) #-: Unidade
		cv.line(350, cow ,350,314 ) #-: Quantidde
		cv.line(385, cow ,385,314 ) #-: Valor Unitario
		cv.line(420, cow ,420,314 ) #-: Valor Total
		cv.line(455, cow ,455,314 ) #-: Base de Calculo ICMS
		cv.line(478, cow ,478,314 ) #-: Valor do ICMS
		cv.line(511, cow ,511,314 ) #-: Valor do IPI
		cv.line(538, cow ,538,314 ) #-: Aliquota ICMS
		cv.line(557, cow ,557,314 ) #-: Aliquota IPI

	def danfeRetrato(self,cv):

		cv.rect(20, 655,550,115, fill=0) #--: Emitente
		cv.rect(20, 800,455, 20, fill=0) #--: Recebemos
		cv.rect(20, 785, 95, 15, fill=0) #--: Data
		cv.rect(115,785,360, 15, fill=0) #--: Recebedor
		cv.rect(475,785, 95, 40, fill=0) #--: Nfe,Serie]
		cv.rect(305,700, 15, 15, fill=0) #--: Entrada Saida
		cv.drawString(20,775,("-"*138)) #---: Linha de Corte
		cv.rect(20, 635,550, 20, fill=0) #--: Natureza da Opercao/Protocolo
		cv.rect(20, 615,550, 20, fill=0) #--: Natureza da Opercao/Protocolo
		cv.rect(20, 540,550, 60, fill=0) #--: Dados do Destinatario
		cv.rect(20, 495,550, 30, fill=0) #--: Fatura/Diplicata
		cv.rect(20, 460,550, 20, fill=0) #--: Local de Entrega
		cv.rect(20, 405,550, 40, fill=0) #--: Calculo do Imposto
		cv.rect(20, 340,550, 50, fill=0) #--: Transportador
		cv.rect(20, 138,550,187, fill=0) #--: Dados de Produtos/Servicos
		cv.rect(20, 15, 550,113, fill=0) #--: Dados de Adicionais - Fisco

		cv.setFillGray(0.1,0.1) 
		cv.rect(20, 602,550, 11, fill=1) #--: Dados do Destinatario
		cv.rect(20, 527,550, 11, fill=1) #--: Fatura/Duplicata
		cv.rect(20, 482,550, 11, fill=1) #--: Endereço de Entrega
		cv.rect(20, 447,550, 11, fill=1) #--: Calculo do Imposto
		cv.rect(20, 392,550, 11, fill=1) #--: Dados da Transportadora
		cv.rect(20, 314,550, 11, fill=1) #--: Cabecalho dos Produtos
		cv.setFillColor(HexColor('0x000000'))

#-------: Cabeclha de Identificacao
		cv.line(230,655,230,770 ) #-:
		cv.line(350,615,350,770 ) #-: 2-Linha de divisao do DANFE-CHAVE(BARRAS)
		cv.line(350,725,570,725 )
		cv.line(350,705,570,705 )
		cv.line(173,615,173,635 ) #-: 2-Linha de divisao do DANFE-CHAVE(BARRAS)

		cv.line(20, 580,570,580 ) #-: Nome/Razao social,cnpj,data emissao
		cv.line(20, 560,570,560 ) #-: Endereco,bairro,cep,data entrada
		cv.line(500,600,500,540 ) #-: Divisao DT Emissao,Entrada-Saida,Hora Entrada Saida
		cv.line(390,600,390,580 ) #-: Divisao CNPJ/CPF
		cv.line(430,580,430,560 ) #-: Divisao CEP
		cv.line(310,580,310,560 ) #-: Divisao BAIRRO/DISTRITO
		cv.line(260,560,260,540 ) #-: Divisao FONE
		cv.line(380,560,380,540 ) #-: Divisao UF
		cv.line(400,560,400,540 ) #-: Divisao IE
		cv.line(280,128,280, 15 ) #-: Divisao Dados Adicionais Fisco

#-------:Divisao do Local de Entrega
		cv.line(250,480,250,460 ) #-: Local de Entrega Divisao Endereco
		cv.line(350,480,350,460 ) #-: Local de Entrega Divisao Bairro
		cv.line(450,480,450,460 ) #-: Local de Entrega Divisao Municipio
		cv.line(470,480,470,460 ) #-: Local de Entrega Divisao CEP
		cv.line(510,480,510,460 ) #-: Local de Entrega Divisao UF

#-------:Divisao do Impostp
		cv.line(20, 425,570,425 ) #-: Divisao Linha Central Impostos
		cv.line(94, 405, 94,425 ) #-: Divisao de Impostos, Frete
		cv.line(187,405,187,425 ) #-: Divisao de Impostos, Seguri,Desconto
		cv.line(140,425,140,445 ) #-: Divisao de Impostos, Base Cal ICMS,VAlorICMS
		cv.line(265,405,265,445 ) #-: Divisao de Impostos, Base ST,OutrasDespesas
		cv.line(370,405,370,445 ) #-: Divisao de Impostos, Valor ICMS ST,Valor do IPI
		cv.line(460,405,460,445 ) #-: Divisao de Impostos, TotalProduto,TotalNota

#-------:Divisao Transportadora	
		cv.line(20, 375,570,375 ) #-: Divisao Linha 1 Central Transportadora
		cv.line(20, 357,570,357 ) #-: Divisao Linha 1 Central Transportadora
		cv.line(260,340,260,390 ) #-: Divisao de Transportadora Codigo Frete p/Conta,Municipio
		cv.line(320,375,320,390 ) #-: Divisao de Transportadora Codigo ANTT
		cv.line(380,375,380,390 ) #-: Divisao de Transportadora Placa do Veiculo
		cv.line(440,357,440,390 ) #-: Divisao de Transportadora UF,UF
		cv.line(460,340,460,390 ) #-: Divisao de Transportadora Municipio,CNPJ,IE,Peso Liquido
		cv.line(360,340,360,357 ) #-: Divisao de Transportadora Numeracao Peso Bruto
		cv.line(90, 340,90, 357 ) #-: Divisao de Transportadora Quantidade Especie Marca
		cv.line(160,340,160,357 ) #-: Divisao de Transportadora Quantidade Especie Marca

		#-------: Mostar PIS-COFINS
		if ( Decimal( str( self.Tvps[0] ) ) + Decimal( str( self.Tvcf[0] ) ) ) !=0:

			cv.line(370,447,370,458 ) #-: Divisao de Impostos, Valor ICMS ST,Valor do IPI
			cv.line(460,447,460,458 ) #-: Divisao de Impostos, Valor ICMS ST,Valor do IPI

			cv.setFont('Helvetica-Bold', 5)
			cv.setFillColor(HexColor('0x777777'))
			cv.drawString(372,450,"PIS")
			cv.drawString(462,450,"COFINS")

#-------:Divisao do Cabecalho do Produto
		cv.setFont('Helvetica-Bold', 5)
		cv.line(60, 314, 60,325 ) #-: Codigo,Descricao dos produtos
		cv.line(275,314,275,325 ) #-: NCM/SH
		cv.line(305,314,305,325 ) #-: CST
		cv.line(321,314,321,325 ) #-: CFOP
		cv.line(337,314,337,325 ) #-: Unidade
		cv.line(350,314,350,325 ) #-: Quantidde
		cv.line(385,314,385,325 ) #-: Valor Unitario
		cv.line(420,314,420,325 ) #-: Valor Total
		cv.line(455,314,455,325 ) #-: Base de Calculo ICMS
		cv.line(478,314,478,325 ) #-: Valor do ICMS
		cv.line(511,314,511,325 ) #-: Valor do IPI
		cv.line(538,314,538,325 ) #-: Aliquota ICMS
		cv.line(557,314,557,325 ) #-: Aliquota IPI

#		cv.setFillColor(HexColor('0x4D4D4D'))
		cv.setFillColor(HexColor('0x000000'))
		cv.drawString(27, 318,"CÓDIGO")
		cv.drawString(120,318,"DESCRIÇÃO DOS PRODUTOS/SERVIÇOS")
		cv.drawString(280,318,"NCM/SH")
		
		if str( self.emcr[0] ).strip() == "3":	cv.drawString(308,318,"CST")
		else:
			
			cv.setFont('Helvetica', 4.1)
			cv.drawString(306,318,"CSOSN")
			cv.setFont('Helvetica', 5)
		
		cv.drawString(322,318,"CFOP")
		cv.drawString(338,318,"UND")
		cv.drawString(351,318,"QUANTIDADE")
		cv.drawString(387,318,"VL UNITÁRIO")
		cv.drawString(425,318,"VL TOTAL")
		cv.drawString(456,318,"BC ICMS")
		cv.drawString(479,318,"VALOR ICMS")
		cv.drawString(512,318,"VALOR IPI")
		cv.drawString(539,318,"%ICMS")
		cv.drawString(558,318,"%IPI")

#-------:Identificacao			
		cv.setFont('Helvetica', 6)
		cv.setFillColor(HexColor('0x000000'))
		cv.drawString(22, 793,"DATA DE RECEBIMENTO")
		cv.drawString(117,793,"IDENTIFICAÇÃO E ASSINATURA DO RECEBDOR")
		cv.drawString(352,718,"CHAVE DE ACESSO")
		cv.drawString(242,740,"DOCUMENTO AUXILIAR DA")
		cv.drawString(242,730,"NOTA FISCAL ELETRÔNICA")
		cv.drawString(242,710,"0 - ENTRADA")
		cv.drawString(242,700,"1 - SAIDA")
		cv.drawString(22, 648,"NATUREZA DA OPERAÇÃO")
		cv.drawString(352,648,"PROTOCOLO DE AUTORIZAÇÃO DE USO")
		cv.drawString(22, 628,"INSCRIÇÃO ESTADUAL")
		cv.drawString(175,628,"INSCRIÇÃO ESTADUAL DO SUBSTITUTO TRIBUTÁRIO")
		cv.drawString(352,628,"CNPJ")

		if self.prpr[0] == '':

			cv.setFont('Helvetica-Bold', 8)
			cv.setFillColor(HexColor('0xCE1C1C'))
			cv.drawString(385,690,"Impresso para simples conferência")
			cv.drawString(352,680,"Informações ainda não transmitidas a nenhuma SEFAZ")
			cv.drawString(395,670,"autorizadora, nem ao SCAN")
			cv.drawString(420,660,"Sem Valor Fiscal")

		else:

			cv.setFont('Helvetica-Bold', 8)
			cv.drawString(357,690,"Consulta de autenticidade no portal nacional da NF-e")
			cv.drawString(410,680,"www.nfe.fazenda.gov.br")
			cv.drawString(390,660,"ou no site da SEFAZ autorizadora")
			cv.line(410,677,502,677 ) #-: Linha q/fica abaixo do site

		cv.setFillColor(HexColor('0x4D4D4D'))
		cv.setFont('Helvetica-Bold', 13)
		cv.drawString(263,750,"DANFE")
		cv.drawString(505,815,"NF-e")

#------: Titulos
		cv.setFillColor(HexColor('0x4D4D4D'))
		cv.setFont('Helvetica-Bold', 10)
		cv.drawString(22,604.5,"Dados do Destinatário/Remetente")
		cv.drawString(22,530,"Fatura/Duplicata")
		cv.drawString(22,485,"Local de Entrega")
		cv.drawString(22,450,"Cálculo do Imposto")
		cv.drawString(22,395,"Transportador/Volumes Transportados")
		cv.drawString(22,330,"Dados dos Produtos / Serviços")
		cv.drawString(22,130,"Dados dos Adicionais")

#------: Destinatario
		cv.setFont('Helvetica', 5.8)
		cv.setFillColor(HexColor('0x000000'))
		cv.drawString(22, 594,"NOME/RAZÃO SOCIAL")
		cv.drawString(392,594,"CNPJ/CPF")
		cv.drawString(502,594,"DATA EMISSÃO")

		cv.drawString(22, 574,"ENDEREÇO")
		cv.drawString(312,574,"BAIRRO/DISTRITO")
		cv.drawString(432,574,"CEP")
		cv.drawString(502,574,"DATA ENTRADA/SAIDA")

		cv.drawString(22, 554,"MUNICÍPIO")
		cv.drawString(262,554,"FONE")
		cv.drawString(382,554,"UF")
		cv.drawString(402,554,"INSCRIÇÃO ESTADUAL")
		cv.drawString(502,554,"HORA ENTRADA/SAIDA")

#-------: Fatura/Diplicata
		cv.drawString(22,518,"Número:")
		cv.drawString(22,508,"Vencimento:")
		cv.drawString(22,500,"Valor:")

		cv.drawString(122,518,"Número:")
		cv.drawString(122,508,"Vencimento:")
		cv.drawString(122,500,"Valor:")

		cv.drawString(222,518,"Número:")
		cv.drawString(222,508,"Vencimento:")
		cv.drawString(222,500,"Valor:")

		cv.drawString(322,518,"Número:")
		cv.drawString(322,508,"Vencimento:")
		cv.drawString(322,500,"Valor:")

		cv.drawString(422,518,"Número:")
		cv.drawString(422,508,"Vencimento:")
		cv.drawString(422,500,"Valor:")

#-------: Local de Entrega
		cv.drawString(22, 475,"ENDEREÇO")
		cv.drawString(252,475,"BAIRRO")
		cv.drawString(352,475,"MUNICIPIO")
		cv.drawString(452,475,"UF")
		cv.drawString(512,475,"CNPJ")

		cv.setFont('Helvetica', 4)
		cv.drawString(472,475,"Codigo do Municipio")
		cv.setFont('Helvetica', 5.8)

#------: Tributos
		cv.drawString(22, 440,"BASE DE CÁLCULO DO ICMS")
		cv.drawString(142,440,"VALOR DO ICMS")
		cv.drawString(22, 420,"VALOR DO FRETE")
		cv.drawString(96, 420,"VALOR DO SEGURO")
		cv.drawString(189,420,"VALOR DO DESCONTO")

		cv.drawString(267,440,"BASE DE CÁLCULO DO ICMS ST")
		cv.drawString(267,420,"OUTRAS DESPESAS ACESSÓRIAS")
		cv.drawString(372,440,"VALOR DO ICMS ST")
		cv.drawString(372,420,"VALOR TOTAL IPI")
		cv.drawString(462,440,"VALOR TOTAL DOS PRODUTOS")
		cv.drawString(462,420,"VALOR TOTAL DA NOTA")

#------: Transportadora
		cv.setFont('Helvetica', 5)
		cv.drawString(22, 385,"NOME/RAZÃO SOCIAL")
		cv.drawString(262,385,"FRETE POR CONTA")
		cv.drawString(322,385,"CÓDIGO ANTT")
		cv.drawString(382,385,"PLACA DO VEÍCULO")
		cv.drawString(442,385,"UF")
		cv.drawString(462,385,"CNPJ/CPF")

		cv.drawString(22, 370,"ENDEREÇO")
		cv.drawString(262,370,"MUNICÍPIO")
		cv.drawString(442,370,"UF")
		cv.drawString(462,370,"INSCRIÇÃO ESTADUAL")

		cv.drawString(22, 352,"QUANTIDADE")
		cv.drawString(92, 352,"ESPÉCIE")
		cv.drawString(162,352,"MARCA")
		cv.drawString(262,352,"NUMERAÇÃO")
		cv.drawString(362,352,"PESO BRUTO")
		cv.drawString(462,352,"PESO LÍQUIDO")

#-------: Cabecalho do Produto



	def converte(self,st,tp):

		"""1-Tel 2-cep 3-data 4-cnpj,cpf"""
		vr = st.strip()

		if tp == 1:	vr = vr.replace('-','')
		if tp == 1 and len(vr) > 10:	vr = vr[( len( vr ) - 10 ):]

		if tp == 1 and len(vr) == 10:	vr = "(%s)%s-%s" % ( vr[:2], vr[2:6], vr[6:] )
		if tp == 1 and len(vr) == 8:	vr = "%s-%s" % ( vr[:4], vr[4:] )

		if tp == 2:	cep  = vr.replace('-','').strip()
		if tp == 2 and len(cep) == 8:	vr = "%s-%s" % ( cep[:5], cep[5:] )

		if tp == 3:	vr = format(datetime.datetime.strptime(vr, "%Y-%m-%d"),"%d/%m/%Y")
		if tp == 4 and len(vr) == 14:	vr = "%s.%s.%s/%s-%s" % ( vr[0:2], vr[2:5], vr[5:8], vr[8:12], vr[12:14] )
		if tp == 4 and len(vr) == 11:	vr = "%s.%s.%s-%s" % ( vr[:3], vr[3:6], vr[6:9], vr[9:] )

		return vr


class danfeCCe:

	cceFilial = ""

	def cceDANFE( self, par, arqxml, danfe, _fil, _clie, _cnpj, _moTi, emails = [''] ):
		
		doc = xml.dom.minidom.parseString( arqxml )

		g = danfeGerar()

		danf = ""
		for i in range( len( str( danfe ) ) /3 ):
			danf += str( danfe )[(i*4):( (i*4) +4 )]+" "
		b128 = code128.Code128( str( danfe ), barHeight=35, barWidth=0.7,stop=1)


		filial = "lobo" #self.emft[0].lower().replace(' ','')
		nomeArquivo = diretorios.usPasta+str( danfe )+"-cce-"+filial+".pdf"
		cv = canvas.Canvas(nomeArquivo, pagesize=A4)
		cv.setLineWidth(.3)
		
		cv.rect(20, 700, 550, 115, fill=0) #-: Quadro 1
		cv.rect(20, 668, 550,  28, fill=0) #-: CNPJ-Cliente
		cv.rect(20, 180, 550, 485, fill=0) #-: Descrição das Correções
		cv.rect(20,  40, 550, 120, fill=0) #-: Codicoes de uso
		
		cv.line(300,700,300,815 ) #-: Titulo CCe
		cv.line(300,798,570,798 ) #-: Codigo de Barras
		cv.line(300,748,570,748 ) #-: Chave de Acesso
		cv.line(300,728,570,728 ) #-: Protocolo
		cv.line(150,668,150,696 ) #-: CNP-CLIENTE
		cv.line(20, 640,570,640 ) #-: Descricao das Correcoes
		
		cv.setFillColor(HexColor('0x000000'))
		cv.setFont('Helvetica-Bold', 10)
		cv.drawString(360,804, "CARTA DE CORREÇÂO CCe")
		cv.drawString(245,647, "C O R R E Ç Õ E S")
		cv.drawString(20, 165, "CONDIÇOES DE USO")

		cv.setFont('Helvetica', 8)
		cv.drawString(302,740, "CHAVE DE ACESSO DA NFe")
		cv.drawString(302,720, "Nº PROTOCOLO EMISSÃO")
		cv.drawString(22, 687, "CNPJ")
		cv.drawString(150,687, "DESCRIÇÃO DO FORNECEDOR-CLIENTE")
		

#------: Informacoes do XML
		sit,aT1 = g.XMLLeitura(doc,"retEvento","xmlns") #----------: ID de Emissão 
		amb,aT4 = g.XMLLeitura(doc,"retEvento","tpAmb") #-------: Nº da DANFE
		dan,aT5 = g.XMLLeitura(doc,"retEvento","chNFe") #-------: Nº da DANFE
		dTr,aT6 = g.XMLLeitura(doc,"retEvento","dhRegEvento") #-: Data de Recebimento
		Pro,aT7 = g.XMLLeitura(doc,"retEvento","nProt") #-------: Numero do Protocolo
		cst,aT8 = g.XMLLeitura(doc,"retEvento","cStat") #-------: CST de Retorno 
		mot,aT9 = g.XMLLeitura(doc,"retEvento","xMotivo") #-----: Motivo
			
		site = vers = idrt = ambi = danf = dtar = prot = cstr = moti = ""
		if aT1 !="" and aT1 !=[]:	site = aT1
		if amb !=""	and amb !=[]:	ambi = amb[0]
		if dan !=""	and dan !=[]:	danf = dan[0]
		if dTr !=""	and dTr !=[]:	dtar = dTr[0]
		if Pro !=""	and Pro !=[]:	prot = Pro[0]
		if cst !=""	and cst !=[]:	cstr = cst[0]
		if mot !=""	and mot !=[]:	moti = mot[0]

		dHora = dtar
		if dtar !='':	dHora = format( datetime.datetime.strptime( dtar.split('T')[0], "%Y-%m-%d"), "%d/%m/%Y" )+" - "+dtar.split('T')[1][:8]

#------: Preenchimento dos Campos

		#_fid, _ffl, _frm = nF.rF( 1 )
		_logMar = login.filialLT[ self.cceFilial ][15].strip()
		if _logMar !='' and os.path.exists("imagens/"+_logMar) == True:	cv.drawImage(ImageReader("imagens/"+_logMar), 25,750, width=100, height=60)

		cv.setFillColor(HexColor('0x000000'))
		cv.setFont('Helvetica-Bold', 10)
		cv.drawString(22, 730, login.filialLT[ self.cceFilial ][14] )
		cv.drawString(22, 720, login.filialLT[ self.cceFilial ][1] )
		cv.drawString(22, 710, g.converte( str( login.filialLT[ self.cceFilial ][9] ), 4 ) )
		
		b128.drawOn(cv, 320, 755) #------: Codigo de Barras
		
		cv.setFont('Helvetica-Bold', 9)
		cv.drawString(302, 730, danf ) #-: Chave de Acesso
		cv.drawString(302, 710, prot+'  -  '+dHora ) #-: Chave de Acesso
		cv.drawString(22,  675, g.converte( str( _cnpj ),4) ) #-: Chave de Acesso
		cv.drawString(152, 675, _clie ) #-: cliente
		
		cv.setFont('Helvetica', 9)

		linha = 620
		moTivo = _moTi.split('\n')
		for m in moTivo:

			cv.drawString(30, linha, m )
			linha -=10

		cv.setFont('Helvetica-Bold', 9)
		cv.drawString(30, 130, "A Carta de Correcao e disciplinada pelo Â§ 1o-A do art. 7o do Convenio S/N, de 15 de dezembro de 1970 e pode ser" )
		cv.drawString(30, 120, "utilizada para regularizacao de erro ocorrido na emissao de documento fiscal, desde que o erro nao esteja relacionado")
		cv.drawString(30, 100, "I - as variaveis que determinam o valor do imposto tais como: base de calculo, aliquota, diferenca de preco, com")
		cv.drawString(30,  90, "quantidade, valor da operacao ou da prestacao")
		cv.drawString(30,  80, "II - a correcao de dados cadastrais que implique mudanca do remetente ou do destinatario")
		cv.drawString(30,  70, "III- a data de emissao ou de saida.")	

		cv.showPage ()
		cv.save()
		
		gerenciador.Anexar = nomeArquivo

		gerenciador.secund = ''
		gerenciador.emails = emails
		gerenciador.TIPORL = ''
		gerenciador.imprimir = True
		gerenciador.Filial   = self.cceFilial
			
		ger_frame=gerenciador(parent=par,id=-1)
		ger_frame.Centre()
		ger_frame.Show()
