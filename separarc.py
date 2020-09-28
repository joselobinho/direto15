#!/usr/bin/env python
# -*- coding: utf-8 -*-
from escpos.printer import Network
import os
try:
    p = Network("10.0.0.106",9100)
    
    p._raw(chr(27)+'@')
    imagem_logo = 'imagens/i5.jpeg' if os.path.exists('imagens/i5.jpeg') else ''
    if imagem_logo:	p.image(imagem_logo)

    #p._raw(chr(27)+"E")
    #p._raw(chr(27)+chr(15))
    p._raw('\x1B\x61\x01')
    #27 + chr(116) + chr(8) + #15
    #p.textln("Hello World\n")
    #p.barcode('1324354657687','EAN13',64,2,'','')
    
    p._raw(chr(27) + chr(33) + chr(12))
    p.textln("CNPJ: 10.405.336/0001-98")
    
    
    
    
    
    
    
    
    for i in range(2):
	p.textln('jose de almeida lobinho')
   # p._raw(chr(27)+chr(18))
#    p._raw(chr(27) + chr(33) + chr(18))
    p._raw(chr(27)+'@')
    p.textln('-----------------------')
    p.textln('jose de almeida lobinho')
    p.textln('-----------------------')
	
except Exception as er:
    print er

