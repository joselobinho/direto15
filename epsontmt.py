#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Emissao de NFCe e DAVs para impressora Epson TMT20
# Jose Lobinho 08/06/2020

from decimal import Decimal
from conectar  import diretorios, login, dialogos, numeracao, truncagem, sqldb, menssagem, formasPagamentos
from escpos.printer import Network
from emitirnfce import EmissaoNfce

alertas = dialogos()
printers = formasPagamentos()
message = menssagem()

class emissaoNotaNfce:
    
    def nfce(self, printer,parent):
	
	ip, port, tp = printers.listaprn(1)[3][printer][10], printers.listaprn(1)[3][printer][9], printers.listaprn(1)[3][printer][7].split('-')[0]
	if not ip.strip() or not port.strip():
	    alertas.dia(parent,u'{ Erro na conexao com host }\n\nIP: '+ip+u', Porta: '+port+u'\n\nDados de conexão incompletos\n'+(' '*140),u'Impressão NFC-e comunicação com o host')
	    return

	ms = message.showmsg("Buscando dados da impressora\n\nAguarde...")
	try:
	    p = Network(ip,int(port))
	except Exception as er:
	    del ms
	    if type(er)!=unicode:	er=str(er).decode('UTF-8')
	    alertas.dia(parent,u'{ Erro na conexão com host '+ip+' }\n\n'+er+'\n'+(' '*140),u'Impressão NFC-e comunicação com o host')
	    return
	    
	del ms
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.textln('jose de almeida lobinho\n')
	p.qr('jose de almeida lobinho e maria de lourdes pinheiro',size=3)
	p.close()
