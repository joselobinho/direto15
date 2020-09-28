#!/usr/bin/env python
# -*- coding: utf-8 -*-
#sAbicomp := Chr(27) + Chr(116) + Chr(1);
#TextoTeste := sAbicomp + 'TEXTO IMPRESSO NA IPRESSORA MP 4200TH '+ #13 + #10 +
#'TEXTO IMPRESSO NA IPRESSORA MP 4200TH '+ #13 + #10 +
#'TEXTO IMPRESSO NA IPRESSORA MP 4200TH '+ #13 + #10 +
#'TEXTO IMPRESSO NA IPRESSORA MP 4200TH '+ #13 + #10 +
#'TEXTO IMPRESSO NA IPRESSORA MP 4200TH '+ #13 + #10 +
#'TEXTO IMPRESSO NA IPRESSORA MP 4200TH '+ #13 + #10;

lla = len("http://homologacao.sefaz.mt.gov.br/nfce/consultanfce?chNFe=00000000000000000000000000000000000000000000&nVersao=100&tpAmb=2&cDest=73576136150&dhEmi=323031352d30352d31335430383a34323a30352d30333a3030&vNF=1.00&vICMS=0.00&digVal=67556c3942635969757771454f74466b7071752f7746586a7838733d&cIdToken=000001&cHashQRCode=27774B100C966273E4B1F9794DACCC80ACB376D1")            
ll = "http://homologacao.sefaz.mt.gov.br/nfce/consultanfce?chNFe=00000000000000000000000000000000000000000000&nVersao=100&tpAmb=2&cDest=73576136150&dhEmi=323031352d30352d31335430383a34323a30352d30333a3030&vNF=1.00&vICMS=0.00&digVal=67556c3942635969757771454f74466b7071752f7746586a7838733d&cIdToken=000001&cHashQRCode=27774B100C966273E4B1F9794DACCC80ACB376D1"

#lla = len("?chNFe=51131003460900000290650010000000031000000031&nVersao=100&tpAmb=2&cDest=02801244147&dhEmi=323031332D31302D32345431363A32313A30332D30333A3030&vNF=1,00&vICMS=0,00&digVal=78764D34764E2B48586A735657516F653474415A547855547764383D&cIdToken=000001&cHashQRCode=7AF4285DA2D18133BEF9F9370AD4A185B2527AFB")            
#ll = "?chNFe=51131003460900000290650010000000031000000031&nVersao=100&tpAmb=2&cDest=02801244147&dhEmi=323031332D31302D32345431363A32313A30332D30333A3030&vNF=1,00&vICMS=0,00&digVal=78764D34764E2B48586A735657516F653474415A547855547764383D&cIdToken=000001&cHashQRCode=7AF4285DA2D18133BEF9F9370AD4A185B2527AFB"
print "Tamanho: ",lla
a=  chr(27) + chr(20) + chr(18)
a+= chr(27) + chr(97) + chr(0) #-: Retorna com Alinhamento Normal
a+= chr(27) + chr(69) + "B & M Madeiras e Compensados LTDA" + chr(27) + chr(70) + chr(13) + chr(10)
#a+= chr(27) + chr(1) + "CNPJ: 12.112.856/0001-38 Ins.Estadual: 79101974\nAV.Automvel Clube, 1747 Vilar dos Teles\nSao Joao do Meriti RJ\n"+("."*48)
a+= "CNPJ: 12.112.856/0001-38 Ins.Estadual: 79101974\nAV.Automvel Clube, 1747 Vilar dos Teles\nSao Joao do Meriti RJ\n"+("."*48)


#a+= chr(27) + chr(69) + "Modo Negrito" + chr(27) + chr(70) + chr(13) + chr(10)
#a+= chr(27) + chr(87) + chr(1) + "Modo Expandido" + chr(27) + chr(87) + chr(0) + chr(13) + chr(10)
#a+= chr(27) + chr(15) + chr(1) + "Modo Condensado" + chr(27) + chr(15) + chr(0) + chr(13) + chr(10) 

if lla > 255:
	
	x1 = lla % 255
	x2 = lla / 255

else:
	x1 = lla
	x2 = 0
	
#a+= chr(7)
a+= chr(27) + chr(69) + " DANFE NFCe - Documento Auxiliar da Nota Fiscal\n"+(" "*7)+"Eletronica Para Consumidor Final\n Nao Permite Aproveitamento de Credito de ICMS\n"+("."*48) + chr(27) + chr(70) + chr(13) + chr(10)
#a+= chr(27) + chr(97) + chr(0) #-: Retorna com Alinhamento Normal
a+= chr(27) + chr(15) + chr(1) + ("."*64)+"\n: Codigo         Descricao dos Produtos"+(" "*24)+":\n: Quantidade     Unidade       Val.Unitario         ValorTotal :\n"+("."*64) #+ chr(27) + chr(15) + chr(0) + chr(13) + chr(10) 

for p in range(5):
	
	b1 = "11111111111111"
	if p == 1:	b1 ="121231"
	if p == 2:	b1 ="121212331"
	if p == 3:	b1 ="121"
	
	b2 = "jose de almeida lobinho" #" Jose de Almeida Llobinh e maria"
	b3 = "21.0000"
	if p == 1:	b3 ="121,231.0000"
	if p == 2:	b3 ="12.0000"
	if p == 3:	b3 ="121.9999"



	b4 = "PC"
	b5 = "1,122,212.00"
	b6 = "12.00"

	if p == 1:	b6 ="121,231.00"
	if p == 2:	b6 ="12.00"
	if p == 3:	b6 ="121.99"
	
	av = 0
	ac = 0
	ap = 0
	at = 0
	
	if len( b1 ) < 14:	ac = ( 14 - len( b1 ) )
	if len( b3 ) < 15:	ap = ( 15 - len( b3 ) )
	if len( b5 ) < 21:	au = ( 19 - len( b5 ) )
	if len( b6 ) < 19:	at = ( 19 - len( b6 ) )

	if len( b2 ) > 46:	b2 = b2[:46]
	if len( b2 ) < 46:	av = ( 46 - len( b2 ) )
	dsc = ": "+(" "*ac)+b1+' '+b2+(" "*av)+\
		  ":\n:"+(" "*ap)+b3+" "+b4+"    X"+(" "*au)+b5+(" "*at)+b6+" :\n"
	a+= dsc

qTdI = "221211"
sTOT = "2,212.21"
sDes = "2,212.21"
sAcr = "2,212.21"
sFrt = "2,212.21"
vTOT = "2,212.21"
vTRI = "121,21"


qTv = 0
sTo = 0
vAc = 0
vDe = 0
vFr = 0
vlT = 0
vTR = 0

if len( qTdI ) < 34:	qTv = ( 34 - len( qTdI ) )
if len( sTOT ) < 49:	sTo = ( 49 - len( sTOT ) )
if len( sDes ) < 41:	vDe = ( 41 - len( sDes ) )
if len( sAcr ) < 40:	vAc = ( 40 - len( sAcr ) )
if len( sFrt ) < 44:	vFr = ( 44 - len( sFrt ) )
if len( vTOT ) < 47:	vlT = ( 47 - len( vTOT ) )

a+=":"+("."*62)+":"
a+="\n: Quantidade Total de Itens:"+(" "*qTv)+qTdI+" :"+\
"\n: Sub-Total: "+(" "*sTo)+sTOT+" :"+\
"\n: Valor do Desconto: "+(" "*vDe)+sDes+" :"+\
"\n: Valor do Acrescimo: "+(" "*vAc)+sAcr+" :"+\
"\n: Valor do Frete: "+(" "*vFr)+sFrt+" :"+\
"\n: Valor Total: "+(" "*vlT)+vTOT+" :"+\
"\n: Forma de Pagamento"+(" "*32)+"Valor Pago :"+\
"\n"

chave = "33150712112856000138650020000001101171026570"
site  = "http://www.portalfiscal.inf.br/nf"
mChav = ""
mTama = 0

for ch in chave:
	
	mTama += 1
	mChav += ch
	if mTama == 4:	mChav += ' '
	if mTama == 4:	mTama  = 0
	print mChav

a+=":"+("."*62)+":"

if len( vTRI ) < 11:	vTR = ( 11 - len( vTRI ) )
a+="Tributos Totais Incidentes Lei Federal 12.741/2012"+(" "*vTR)+"R$ "+vTRI+"\n"+("."*64)

a+= chr(27) + chr(20) + chr(18)+"Emitido Ambiente de Homologacao SEM VALOR FISCAL"+\
"\nNumero:      Serie:     Emissao:\n"+\
chr(27) + chr(97) + chr(1)+"Consulte pela Chave de Acesso em\n"+site+"\nCHAVE DE ACESSO\n"+mChav[:25]+"\n"+mChav[26:]+chr(27) + chr(97) + chr(0)
a+="\n"+("."*48)

a+= chr(27) + chr(97) + chr(1)+ chr(27) + chr(69) + "CONSUMIDOR"+  chr(27) + chr(70) + chr(27) + chr(97) + chr(0)
a+="\nCPF: 475791535-72\nNome: Jose de Almeida Lobinho"
a+="\n"+("."*48)
a+="Consulta via leitor de QRCODE"

print len(b2)
#a+= chr(27) + chr(15) + chr(0) + chr(13) + chr(10) 


a+= chr(27) + chr(97) + chr(1)
a+= chr(29) + chr(107) + chr(81)
a+= chr(2) + chr(8) + chr(4) + chr(1)
a+= chr(x1) + chr(x2) + chr(97)+chr(110)
#a+= chr(0)

for i in ll:
  # print i,ord(i)
   a+= chr( ord(i) )
   
print mChav  
#a+=chr(27) + chr( ord(i) )
    #        chr(119) + chr(119) + chr(119) + chr(46) + chr(98) + chr(101) + chr(109) + chr(97) + chr(116) + chr(101) + chr(99) + chr(104) + chr(46) + chr(99) + chr(111) + chr(109) + chr(46) + chr(98) + chr(114)+"\
    #        http://www.nfe.se.gov.br/portal/consultarNFCe.jsp?chNFe=43120910585504000174650010000000541123456781&nVersao=100&tpAmb=1&cDest=43708379006485&dhEmi=323031322d30392d32375431363a32303a33342d30333a3030&vNF=1000.00&vICMS=180.00&digVal=37327151612b623074616f514f3966414a7766646c5875715176383d&cIdToken=000001&cHashQRCode=80f5d4a1e4b12bc97aae0e971a61bff73270fd81\
#a+=chr(0)+chr(27)+"    jose de Almeida Lobinho"
#           chr(119) + chr(119) + chr(119) + chr(46) + chr(98) + chr(101) + chr(10)+"Jose de almeida lobinho"+chr(13)+chr(10)
#			chr(119) + chr(119) + chr(119) + chr(46) + chr(98) + chr(101) + chr(109) + chr(97) + chr(116) + chr(101) + chr(99) + chr(104) + chr(46) + chr(99) + chr(111) + chr(109) + chr(46) + chr(98) + chr(114)

#a+= chr(27) + chr(97) + chr(0)+"\n\n\n"
ProT = "333150001089670"
dTEm = "2015-07-10T18:41:04"
aa= "Protocolo de Autorizacao: "+ProT+"\n"+dTEm+"\n\n"
#a+= 
a+= chr(27) + chr(97) + chr(1)+ chr(27) + chr(20) + chr(18)+aa+chr(27) + chr(97) + chr(0) + chr(27) + chr(119)


#cBuffer :=  #27 + #97 + #1 +        // esse código faz a centralização
            #29 + #107 + #81 +      // esse é o do qr code
            #2 + #12 + #8 + #1 +    // aqui é o tamanho
            #19 +             // tamanho de caracteres correspondente ao texto
            #0 +                    // bit de partida
            #119 + #119 + #119 + #46 + #98 + #101 + #109 + #97 + #116 + #101 + #99 + #104 + #46 + #99 + #111 + #109 + #46 + #98 + #114;         // aqui começa o texto









# - VB
#27 + #69 + "Modo Negrito" + #27 + #70 + #13 + #10 -Delphi

__arquivo = open("/mnt/lykos/bema.txt","w")
__arquivo.write( a )
__arquivo.close()

