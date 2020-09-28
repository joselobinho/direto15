#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import xml.dom.minidom
from danfepdf  import danfeGerar
from decimal   import Decimal

geraPDF = danfeGerar()

arq = glob.glob( "/mnt/lykos/cdd/html/*.xml" )
grv = "/mnt/lykos/cdd/final/"

valor = Decimal("0.00")
total = Decimal("0.00")
_cfop = "5102"
mudar = "5405"
arquivos = 0
for i in arq:
	
	__na = i.split('/')[-1]

	doc = xml.dom.minidom.parse( i )
	ccd, aT = geraPDF.XMLLeitura(doc,"prod","cProd")
	cfo, aT = geraPDF.XMLLeitura(doc,"prod","CFOP")
	Tvpd,aT = geraPDF.XMLLeitura(doc,"ICMSTot","vProd")

	strdocume = doc.toprettyxml()
	documento_xml = "" 
	item = "0" 
	valores = Decimal("1508000.00")
	
	for x in strdocume.split('\n'):

		if total <= valores:

			if "<det nItem=" in x:	item = x.split("<det nItem=")[1].split(">")[0]
			if "<CFOP>" in x and _cfop in x:
				
				x = x.replace( _cfop, mudar )
				OK = False
				for v in strdocume.split('\n'):

					if "<det nItem=" in v and v.split("<det nItem=")[1].split(">")[0] == item:	OK = True
					if "<vProd>" in v and OK:

						valor_produto = Decimal( v.split("<vProd>")[1].split("</vProd>")[0] )
						total +=valor_produto

		documento_xml +=x.encode("utf-8")
		
	__arquivo = open(grv+'f_'+__na,"w")
	__arquivo.write( documento_xml )
	__arquivo.close()

arq_final = glob.glob( "/mnt/lykos/cdd/final/*.xml" )

total_final = Decimal("0.00")
total_proposto = Decimal("0.00")
for f in arq_final:

	doc = xml.dom.minidom.parse( f )
	strdocume = doc.toprettyxml()

	ccd,aT = geraPDF.XMLLeitura(doc,"prod","cProd")
	vTp,aT = geraPDF.XMLLeitura(doc,"prod","vProd")
	cfo,aT = geraPDF.XMLLeitura(doc,"prod","CFOP")

	ind = 0
	for i in ccd:

		#if cfo[ind] == mudar:	print cfo[ind],vTp[ ind ]
		if cfo[ind] == mudar:	total_final +=Decimal( vTp[ ind ] )
		if cfo[ind] == _cfop:	total_proposto +=Decimal( vTp[ ind ] )

		ind +=1

print( "Apuracao: ",_cfop, format(total,',') )
print( "Proposto: ",_cfop, format(total_proposto,',' ) )
print( "Final...: ",mudar, format(total_final,',' ) )
		
