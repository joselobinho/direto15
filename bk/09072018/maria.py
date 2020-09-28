#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ctypes import cdll
import time
#import poppler
#import wx

#class xxl:
#class xxl(wx.Frame):
	
#	def mariaa(self):
			
print "lobo..................",time.time()

lib = cdll.LoadLibrary('/mnt/lykos/sei/nfce/daruma/rjsm1/lykos/libDarumaFramework.so')


ret = lib.aCFAbrir_NFCe_Daruma('','','','','','','','','');
print 'Abrir a nota1: ',ret

#ret = lib.aCFVender_NFCe_Daruma('I1','2.000','3.00','D$','0','1232123','UN','Teste legal')
ret = lib.aCFVender_NFCe_Daruma('FF','2.000','3.000','D$','1.00','1232123','UN','Teste legal')
print 'Abrir a nota2: ',ret


ret = lib.aCFTotalizar_NFCe_Daruma('D$','0');
print 'Abrir a nota3: ',ret

ret = lib.aCFEfetuarPagamento_NFCe_Daruma('1','5.00');
print 'pagamento: ',ret


ret = lib.tCFEncerrar_NFCe_Daruma('');
print 'encerrar: ',time.time()


time.sleep( 5 )
#mariaa('a','b')
#if __name__ == "__main__":
	#x = xxl()
	#x.mariaa()
	#main()
#	app = wx.PySimpleApp()
#	frame = xxl().Show(True)
#	app = xxl()
#	app.MainLoop()

