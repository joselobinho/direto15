#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Emissao de dav para epson termica

from conectar  import diretorios, login, dialogos, numeracao, truncagem, sqldb, menssagem, formasPagamentos
from prndireta import ConfiguracoesPrinters,DavTermicas
from decimal   import *
import six

import epsonnfce as comandos
import datetime

alertas = dialogos()
numerar = numeracao()
formata = truncagem()
termica = DavTermicas()

cmd=comandos.c


class EpsonEmissaoDav:
    
    def dav3(self, parent, filial=None,ii=None,dd=None, cc=None, rr=None, recibo=False, modelo='', inibirvalores=False, tipo_impressao=''):

	em=login.filialLT[filial]
	emitente = str(em[1])
	if len( login.filialLT[filial][35].split(";") ) >= 31 and login.filialLT[filial][35].split(";")[30] == "T" and login.filialLT[filial][14].strip()!="":	emitente=login.filialLT[filial][14].upper()

	d = dd[0]
	i = ii
	c = ''
	if cc:	c=cc[0]

	cnpj=numerar.conversao(str(em[9]),4)
	cep =numerar.conversao(str(em[5]),2)

	a = chr(27)+'@' #--//Resete da impressora
	a += chr(27) + chr(33) + chr(20)
	if rr:	a+= "\nR E I M P R E S S A O\n"
	if d[74] == "3":	a+= "\nCANCELADO\n"
	if d[41] == "2":	a+= "\nO  R  C  A  M  E  N  T  O\n\n"
	if tipo_impressao=="EXAV":	a+="\nE X P E D I C A O AVULSO\n"

	a += emitente
	a += chr(27) + chr(33) + chr(8)
	a += "\n\nCNPJ: "+cnpj +"  Ins.Est.: "+em[11]+"\n"+em[2]+" "+em[7]+" "+em[8]+"\n"+em[3]+" "+em[4]+" "+em[6]+"\nCEP: "+cep+"  TEL: "+em[10]
	a +="\n"+("."*48)

	dp = format(datetime.datetime.strptime(str(d[11]), "%Y-%m-%d"),"%d/%m/%Y")+" "+str(d[12])
	tp = "\nPedido No: "+str(d[2]).strip()+" "+dp
	dh = datetime.datetime.now().strftime("%d/%m/%Y %T")
		
	if d[41]=="2":	tp="\nOrçamento No: "+str(d[2]).strip()
	if d[2][:3]=="DEV":	tp="\nDevolucao No: "+str(d[2]).strip()

	a += tp
	a += chr(27) + chr(33) + chr(5)

	if rr == True:	a += '\nHoje....: '+dh+" Vendedor: "+str(d[9])
	else:	a += "\nVendedor: "+str(d[9])
	a +='\nEmissao.: '+format(d[11],'%d/%m/%Y')+' '+str(d[12])+' Impressao: '+dh

	a += chr(27) + chr(33) + chr(8)
	a +='\n'

	if c:

	    if c[3]:	a+="\nCPF/CNPJ: "+numerar.conversao(str(c[3]),4)
	    if c[3]=='' and d[39] !='':	a+="\nCPF/CNPJ: "+numerar.conversao(str(d[39]),4)
	    if c[1]:	a+="\nNome....: "+c[1]

	    entrega = ConfiguracoesPrinters()
	    __c, __n = entrega.enderecoSegundo(c,d[76],c[51])

	    if __c[0]:	a+="\nEndereco: "+__c[0]
	    if __c[1]:	a+="\nNumero..: "+__c[1]
	    if __c[2]:	a+="\nBairro..: "+__c[2]
	    if __c[3]:	a+="\nMunicipo: "+__c[3]
	    if __c[4]:	a+="\nCEP.....: "+__c[4]
	    if __c[5]:	a+="\nTelefone: "+__c[5]
	    if d[38]:	a+="\nReferencia: "+d[38]
	    a+='\n'
				
	else:
	    if d[39]:	a+="\nCPF/CNPJ: "+numerar.conversao(str(d[39]),4)
	    if d[4]:
		a+="\nNome....: "+d[4]+"\n"

	"""   Impressao dos Produto    """
	if len(login.filialLT[filial][35].split(";"))>=68 and login.filialLT[filial][35].split(";")[67]!="T" and not recibo:
	
	    a += chr(27)+'@' #--//Resete da impressora
	    a += cmd["justificado_centro"]
	    a += cmd["condensado_negrito"]
	    a += "\nDOCUMENTO AUXILIAR DE VENDA"
	    a += "\nNAO E DOCUMENTO FISCAL, NAO E VALIDO COMO RECIBO DE PAGAMENTO"
	    a += "\nNAO E VALIDO COMO GARANTIA DE MERCADORIA, NAO COMPROVA PAGAMENTO"
	    a += "."
	    a += chr(27)+'@' #--//Resete da impressora
	    if d[41] == "2" and len(login.filialLT[filial][35].split(";"))>=187 and login.filialLT[filial][35].split(";")[186]=="T":	a+= "\nO  R  C  A  M  E  N  T  O\n"
	a += chr(27) + chr(33) + chr(8)
	a += "\nCodigo-Descricao dos Produtos\nQuantidade UN  Valor Unitario  Valor Total"
	a += "\n"+("."*48)+"\n"

	""" Impressao """
	iTem   = 1
	kiTVnd = ""
	_ar = ""

	conn = sqldb()
	sql  = conn.dbc("Impressao do DAV", fil = filial, janela = parent )

	if sql[0]:

	    cliente_vai_retirar = "\n<< "+login.filialLT[filial][35].split(";")[84].upper()+" >>" if len(login.filialLT[filial][35].split(";"))>=85 and login.filialLT[filial][35].split(";")[84] else "\n<< CLIENTE VAI RETIRAR >>"
	    riTems=i
	    for p in i:

		"""     Controla o Conteudo do KIT, Mostar apenas o produto principal    """
		passar = True
		kiTAlT = False
		numkiT = p[91]

		if p[91] !="" and kiTVnd != p[91]:	kiTAlT = True
		if p[91] !="" and kiTVnd == p[91]:	passar = False
		kiTVnd = p[91]

		if passar == True:
					
		    if p[5] !='':	b1 = p[5] #-: Codigo
		    else:	b1 = p[6]

		    """ Tabela de beneficiamento """
		    tabelas_feneficamento={}
		    if sql[2].execute("SELECT ep_prdo FROM cia WHERE ep_inde='"+filial+"'"):
			_s =sql[2].fetchone()[0]
			if _s:
					
			    tabelas_feneficamento['TB01']=_s.split("|")[1].split(";")[0]
			    tabelas_feneficamento['TB02']=_s.split("|")[1].split(";")[1]
			    tabelas_feneficamento['TB03']=_s.split("|")[1].split(";")[2]
			    tabelas_feneficamento['TB04']=_s.split("|")[1].split(";")[3]
			    tabelas_feneficamento['TB05']=_s.split("|")[1].split(";")[4]
			    tabelas_feneficamento['TB06']=_s.split("|")[1].split(";")[5]

		    """  Sair codigo interno no dav """
		    codigo_interno = True if len(login.filialLT[filial][35].split(";"))>=69 and login.filialLT[filial][35].split(";")[68]=="T" else False
		    if codigo_interno and sql[2].execute("SELECT pd_intc FROM produtos WHERE pd_codi='"+str( p[5] )+"'"):

			__codigo_interno = sql[2].fetchone()[0]
			if __codigo_interno.strip():	b1 = __codigo_interno.strip()
					    
		    b2 = p[7] #----------------------------------------------------------: Descricao do produto
		    b3 = numerar.eliminaZeros( str( formata.intquantidade( p[12] ) ) ) #-: Quantidade
		    b4 = p[8] #-----------------: Unidade
		    b5 = format( p[11],',' ) #--: Valor Unitario
		    b5 = numerar.eliminaZeros( b5 )
		    b6 = format( p[13],',' ) #--: Valor Total
		    b7 = str( p[10] )
		    b8 = str( p[9] )

		    """  Medidas de madeiras  """
		    _medidas = formata.intquantidade(p[23])+" PC "+  str(p[15])+'CM'
					    
		    if p[16]:	_medidas += " "+ str(p[16])+'LG'
		    if p[17]:	_medidas += " "+ str(p[17])+'EX'
		    if p[16] or p[17]:	b3, b4 = formata.intquantidade( p[23] ), "PC"

		    if ( p[15] + p[16] + p[17] ) > 0: #->[Medidas do Cliente COM X LAR X EXP]

			b3 = numerar.eliminaZeros( str( formata.intquantidade( p[23] ) ) ) #---------: Quantidade
			b4 = "PC"
			b5 = format(p[14],',')
			b5 = numerar.eliminaZeros( b5 )

		    av = 0
		    ac = 0
		    ap = 0
		    at = 0
		    en = 0

		    """   Alerar os dados se o produto for KIT   """
		    if kiTAlT == True:

			if len( p[91].split('|') ) >= 2:	b1, b2 = p[91].split('|')[0],p[91].split('|')[1]
			b5, b6 = termica.reTKiTvlr( riTems, p[91], p[92] ) #-: Retorna o valor unitario e Total do KIT
			if inibirvalores:	b5,b6="",""

			b3 = formata.intquantidade(p[92])
			b4 = "KT"

		    if inibirvalores==True and b5:	b5 = b6 = ''
		    b1=str(int(b1)) if b1.strip().isdigit() else b1

		    if len( b1 ) < 14:	ac = ( 14 - len( b1 ) )
		    if len( b3 ) < 15:	ap = ( 10 - len( b3 ) )
		    if len( b5 ) < 21:	au = ( 10 - len( b5 ) )
		    if len( b6 ) < 19:	at = ( 10 - len( b6 ) )

		    if len( b2 ) < 46:	av = ( 46 - len( b2 ) )
		    if len( b7 ) < 10:	en = ( 10 - len( b7 ) )
			
		    carx = "  X" if b5 and b6 else ""
		    dsc = b1+' '+b2+'\n'+  (" "*ap)+b3+" "+b4 + carx + (" "*au)+b5+(" "*at)+b6
		    if ( p[15] + p[16] + p[17] ) !=0:	dsc +='\nMedidas: '+str( _medidas )

		    """ Quantifica as devolucoes para determinar o numero de caixas """
		    quantidade_devolucao = Decimal()
		    if sql[2].execute("SELECT cr_ndav FROM dcdavs WHERE cr_cdev='"+ d[2]+"' and cr_reca!='3'"):
			quantidade_devolucao, devolucao_ocorrencias = numerar.calcularDevolucoes( sql[2], p[5], p[0], sql[2].fetchall())

		    """  Embalagens  """
		    if p[99]:
			""" Quantidade p/embalagens para calculo das embalagens faltantes """
			saldo_caixas = ''
			if p[99] and 'Embalagens' in p[99] and len(p[99].split(' '))==3 and p[99].split(' ')[1]:

			    metros = p[22]
			    entregue = p[64]
			    caixas = p[99].split(' ')[1]
			    if sql[2].execute("SELECT pd_para FROM produtos WHERE pd_codi='"+ p[5] +"'"):	caixas = numerar.retornoCaixasEmbalagens( 1, metros,entregue, sql[2].fetchone()[0], saldo_devolucao=quantidade_devolucao )
			    saldo_caixas = ">==>Saldo: "+str(caixas)
			    dsc+="\n"+p[99]+saldo_caixas+"\n"
			
		    if b7 or b8:	dsc +='\nEndereco: '+b7 if b7 else "" +"\nFabricante: "+b8 if b8 else ""
		    if str( p[88] ).strip():	dsc +='\nReferencia: '+str( p[88] )
		    if str( p[62] ).strip():	dsc +=cliente_vai_retirar
		    if p[25]:	dsc +='\nCORTE: '+p[25]
		    
		    """ Imprime o beneficiamento da tabela de precos """
		    if b4 in ['M2','M3','ML','PC'] and tabelas_feneficamento and tabelas_feneficamento['TB'+str(p[75]).zfill(2)]:	dsc+='\nBeneficiamento: '+tabelas_feneficamento['TB'+str(p[75]).zfill(2)]

		    """ Expedicao local [Loja]->Cliente retirando """
		    if p[76] and p[76].strip():
			dsc+='\n'+ chr(27) + chr(33) + chr(20)+"< < < R E T I R A D O PELO C L I E N T E > > >"+ chr(27) + chr(33) + chr(8)+"\n"
			dsc +=p[76].split('\n')[0].replace('ç','c').strip()+'\n'+p[76].split('\n')[9]+'\n'+p[76].split('\n')[7]+' '+p[76].split('\n')[6]
		    if kiTAlT:	dsc +='\nK I T'+("."*43)+str( iTem ).zfill(2)+'\n'
		    else:	dsc +='\n'+("."*38)+'['+str( iTem ).zfill(2)+']..TB'+str(p[75]).zfill(2)+'\n'
			
		    iTem +=1
		    a+= dsc

	    """ Pagamento """
	    conn.cls( sql[1] )

	    qTdI = str(len(i))
	    sTOT = format(d[36],',')
	    sDes = format(d[25],',')
	    sAcr = format(d[24],',')
	    sFrt = format(d[23],',')
	    vTOT = format(d[37],',')
	    vTro = format(d[49],',') #-: Valor do Troco
	    vRec = format(d[48],',') #-: Valor do recebido

	    qTv = sTo = vAc = vDe = vFr = vlT = vTR = Tro = vRe = 0

	    if len(qTdI)<34:	qTv=(22 - len(qTdI))
	    if len(sTOT)<49:	sTo=(37 - len(sTOT))
	    if len(sDes)<41:	vDe=(29 - len(sDes))
	    if len(sAcr)<40:	vAc=(28 - len(sAcr))
	    if len(sFrt)<44:	vFr=(32 - len(sFrt))
	    if len(vTOT)<47:	vlT=(35 - len(vTOT))
	    if len(vTro)<43:	Tro=(41 - len(vTro))
	    if len(vRec)<34:	vRe=(32 - len(vRec))
	    a+="Sub-Total: "+(" "*sTo)+sTOT
	    
	    if sDes !='' and Decimal( sDes.replace(",",'') ) !=0:	a+="\nValor do Desconto: "+(" "*vDe)+sDes
	    if sAcr !='' and Decimal( sAcr.replace(",",'') ) !=0:	a+="\nValor do Acrescimo: "+(" "*vAc)+sAcr
	    if sFrt !='' and Decimal( sFrt.replace(",",'') ) !=0:	a+="\nValor do Frete: "+(" "*vFr)+sFrt
	    
	    sair_troco = True if len(login.filialLT[filial][35].split(";"))>=122 and login.filialLT[filial][35].split(";")[121]=='T' else False
	    if sair_troco and d[49]:
		a+="\nValor recebido: "+("."*vRe)+vRec
		a+="\nTroco: "+("."*Tro)+vTro

	    a+="\nValor Total: "+(" "*vlT)+vTOT
	    a+="\n"+("."*48)+"\n{ Formas de Pagamentos }\n"

	    if d[97]:
			    
		for fp in d[97].split('|'):

		    if fp:
			forma_pagamento, valor=fp.split(";")[2].strip(), fp.split(";")[3].strip()
			l=( 47 - (len(forma_pagamento) +  len(valor)) )
			a+=forma_pagamento+' '+("."*l)+str(valor)+"\n"
	    
	    if d[95] and not d[97]:

		for fp in d[95].split('|'):

		    if fp:
				    
			fpg = fp.split(";")
			vnc_rlocal = fpg[3].strip().split('-')[1] if fpg[3] else ""

			l=( 47 - ( len(fpg[0].strip()) + len(vnc_rlocal) + len(fpg[2].strip()) ) )
			a+=fpg[0].strip()+' '+vnc_rlocal+("."*l)+str( fpg[2] )+"\n"


	    if d[117] and d[117].split('|')[0]:	a+='\n\nPagamento em dinheiro: '+d[117]+'\n\n'
	    entrega = ConfiguracoesPrinters()
	    if d[41] == "2" and len(login.filialLT[filial][35].split(";"))>=187 and login.filialLT[filial][35].split(";")[186]=="T":	a+= "\nO  R  C  A  M  E  N  T  O\n"
	    previsao_entrega = "\nPrevisao para entrega: "+format( d[21],'%d/%m/%Y' ) if d[21] else ""
	    a+="\n"+ previsao_entrega +"\n"+str( login.rdpdavs )
	    if len(login.filialLT[filial][35].split(";"))>=133 and login.filialLT[filial][35].split(";")[132]=="T" and not recibo:

		a+="\n"+("."*48)+'\n'
		a+="\nRECEBEMOS DE\n"
		a+="OS PRODUTOS E/OU  SERVICOS CONSTANTES NO  NUMERO\nDE DOCUMENTO AO LADO"+(' '*8)+"Numero:"+d[2].strip()+"\n\n"
		a+="DATA_____________/____________________/_________\n\n"
		a+="Assinatura:_____________________________________\n"

	    a+='\n'
	    
	    #a+=b'\x1D\x6B'+  'ITF-14' +str(d[2]).strip()+ b'\x05'
	    
    

	    """ https://comp.lang.pascal.delphi.misc.narkive.com/rqUXxkwA/epson-receipt-printer
		https://www.bztech.com.br/arquivos/manual-codigo-barras-diebold-im402td.pdf
	    
		Exemplo de programa para todas as impressoras Amostra de impressão
		PRINT # 1, CHR $ (& H1D); "h"; CHR $ (80); . Definir altura
		PRINT # 1, CHR $ (& H1D); "H"; CHR $ (2); . Selecione a posição de impressão
		PRINT # 1, CHR $ (& H1D); "f"; CHR $ (0); . Selecionar fonte
		PRINT # 1, CHR $ (& H1D); "k"; CHR $ (2); . Imprimir código de barras
		PRINT # 1, "496595707379"; CHR $ (0);
		IMPRIMIR # 1, CHR $ (& HA);
		IMPRIMIR # 1, CHR $ (& H1D); "f"; CHR $ (1); . Selecionar fonte
		PRINT # 1, CHR $ (& H1D); "k"; CHR $ (2); . Imprimir código de barras
		PRINT # 1, "496595707379"; CHR $ (0);
		
		1D 68 50 1D 48 02 1D 66 00 1D 6b 2 <barcode> 00 0A  ( hexa )
		# 29 + # 104 + # 80 + # 29 + # 72 + # 2 + # 29 + # 102 + # 0 + # 29 + # 107 + # 2 + código de barras + # 0 + # 10; ( chr() )
	    """
	    if d[41] == "2" and len(login.filialLT[filial][35].split(";"))>=187 and login.filialLT[filial][35].split(";")[186]=="T":	a+= "\nO  R  C  A  M  E   N  T  O\n"
	    data = str(d[2]).strip()
	    a+=chr(27) + chr(97)  + chr(1)  #// Alinhamento centrado
	    a+="\nLykos Solucoes em TI\n"
	    
	    a+=chr(29) + chr(104) + chr(80) #--// Altura do codito
	    a+=chr(29) + chr(119) + chr(2) #---// Largura do codigo
	    #a+=chr(29) + 'kA' + chr(11) + data + chr(0) + data + '\n\n\n'
	    #a+=chr(29) + 'kC' + chr(12) + data + chr(0) + data + '\n\n\n'
	    a+=chr(29) + 'kH' + chr(13) + data + chr(0) + (' '.join(data)) +'\n\n\n'

	    _ar2 = diretorios.usPasta+"epsontmt20vias_"+ str(login.usalogin ).lower() +".nfc"

	    """ Impressao do dav com entrega programada saindo a informacao para VIA ESTABELECIMENTO, VIA CLIENTE """
	    if d[21] and  len(login.filialLT[filial][35].split(";"))>=147 and login.filialLT[filial ][35].split(";")[146]=='T':
		
		b='Via do Cliente\n'+a
		c='Via do Estabelecimento\n'+a
		__arquivo = open( _ar2, "w" )
		__arquivo.write( c )
		__arquivo.close()
	    else:	b, c = a,a

	a +="\n"+("."*48)
	a += chr(27)+'@' #--//Resete da impressora
	a += cmd['corta']
	arq=diretorios.usPasta+"epsontmt20"+ str(login.usalogin ).lower() +".nfc"
	arquivo = open(arq,"w")
	arquivo.write(a)
	arquivo.close()
	
	return arq
