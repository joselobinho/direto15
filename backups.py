#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Jose de Almeida Lobinho
# 01-11-2014 11:40
# Manutencao dos Backups
from conectar import sqldb,login,diretorios

class CopiasSeguranca:
	
	def estoqueFisico(self):

		conn = sqldb()
		sql  = conn.dbc("Estoque Fisico",1)

		if sql[0] == True:

			eFisico = "SELECT * FROM produtos"
			if sql[2].execute(eFisico) !=0:
				
				eFis = sql[2].fetchall()
				conn.cls(sql[1])
				
				for i in eFis:
					
					print "Estoque Fisico: ",i[0]

		
		print "Estamos Juntos!!",diretorios.fsPasta
