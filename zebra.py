#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 10-10-2018 Jose de Almeida Lobinho
import commands
#s=""

s='^XA'
s+='^LL200'
#s+='^FO130,60^BY2^BEN,60,Y,N^FD789123456789^FS'
s+='^FO65,15^GB705,60,4,B^FS'
s+='^FO425,115^GB340,45,3,B^FS'
s+='^FO90,30^ADN,30,14^FDPERFIL { MONFARDINI MDF }^FS'
s+='^FO70,90^ADN,1,1^FDSEAL ELETRONICA JOSE DE ALMEIDA LOBINHO E MARCIA^FS'
s+='^FO70,120^ADN,35,12^FDCodigo....: 00000000988761^FS'
s+='^FO430,122^ADN,30,15^FD00000000988761^FS'
s+='^FO70,160^ADN,35,12^FDEndereco..: 1.2.312.A1^FS'
s+='^FO70,200^ADN,35,12^FDFabricante: FULANDO DE TAL^FS'
s+='^FO70,240^BY5,,140^BEN,90,Y,N^FD789123456743^FS'
s+='^FO645,100^BQ,2,5^FDLA,789123456743^FS'
"""
s+='^LL200'

s+='^FO140,15^ADN,32,12^FDIMPRESSORAS ZEBRA^FS'
s+='^FO380,20^ADN,20,10^FDCNPJ: ^FS'
##s+='^FO460,10^ADN,20,10^FDIMPRESSORAS ZEBRA^FS'
#s+='^FO590,10^ADN,20,10^FDIMPRESSORAS ZEBRA^FS'

s+='^FO140,50^ADN,1,1^A4^FDSEAL ELETRONICA JOSE DE ALMEIDA LOBINHO E MARCIA^FS'
s+='^FO480,70^ADN,10,1^FD[ FABRICANTE ]^FS'
s+='^FO480,90^ADN,10,1^FDRAIO DE LUAR^FS'
s+='^FO480,110^ADN,10,1^FD[ CODIGO INTERNO ]^FS'
s+='^FO480,130^ADN,35,12^FD00000021212325^FS'
s+='^FO480,170^ADN,1,1^FD[ ENDERECO ]^FS'
s+='^FO480,190^ADN,1,1^FDJOSE ALMEIDA LOBINHO MARCIA ZIGOLI^FS'
##s+='^FO110,50^ADN,30,10^FDR$ 221,90^FS'
##s+='^FO460,30^ADN,1,1^FDSEAL ELETRONICA^FS'
##s+='^FO460,50^ADN,30,10^FDR$ 221,90^FS'
#s+='^FO590,30^ADN,1,1^FDSEAL ELETRONICA^FS'
#s+='^FO590,50^ADN,30,10^FDR$ 221,90^FS'

s+='^FO160,110^BY3,,90^BEN,70,Y,N^FD789123456743^FS'
##s+='^FO460,80^BY2,,90^BEN,50,Y,N^FD789123456743^FS'
#s+='^FO590,80^BY2,,90^BEN,60,Y,N^FD789123456743^FS'


#s+='^FO~JC^FS' #--// Resete calibragem

"""
s+='^XZ'




#s+='^XA'
#s+='^LL160'
#s+='^FX EXEMPLO03 - MOLDURAS ^FS'
#s+='^FO30,10^ADN,18,10^FDSEAL ELETRONICA^FS'
#s+='^FO30,55^BY2^BEN,60,Y,N^FD789123456789^FS'
#s+='^FO1,1^GB260,150,4,B^FS'
#s+='^XZ'

#s+='^XA'
#s+='^ILFIXO0001^FS'
#s+='^FO40,125^BY2^BCN,90,Y,N^FD745404^FS4'
#s+='^FO320,120^ADR,36,20^FD0001^FS5'
#s+='^XZ'


arquivo = open("lobo.zpl","w")
arquivo.write(s)
arquivo.close()

#arquivo = open('lobo.txt.','w')
saida = commands.getstatusoutput("lpr -Pzebra lobo.zpl")
print(saida)
