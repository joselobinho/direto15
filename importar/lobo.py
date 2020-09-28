#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import os


class sqldb:

	def dbc(self,messa,op):
		

		print "Banco Abertura [ "+messa+" ]\n\n"
		try:

			conn = MySQLdb.connect(host = "localhost",user = "root",passwd = "151407jml", db = "qlf", connect_timeout=10)
			curs = conn.cursor()

			return True,conn,curs

		except Exception, _reTornos:

			os.system("clear")
			print "E R R O !!\n\n{ Abertura do Banco de Dados }\n\nRetorno: "+str(_reTornos)	

		return False,'',''

	def cls(self,db):

		db.close()

