#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ftplib import FTP
from danfepdf import danfeGerar
from conectar import NotificacaoEmail

import os
import datetime
import MySQLdb
import glob
import zipfile
import commands
import xml.dom.minidom

geraPDF = danfeGerar()
notifica_email = NotificacaoEmail()

class BackupCloud:
	
	def conexaoFtp(self):

		conn  = sqldbs()
		sql   = conn.dbc( "Backup", 1 )

		if sql[0]:

		    rls=sql[2].execute('SELECT ep_cnpj,ep_inde,ep_dnfe,ep_bkcl FROM cia')
		    result=sql[2].fetchall()
		    conn.cls(sql[1])
		    if rls:
			listar=""
			for i in result:
			    
			    passar=False
			    if i[2].split(';')[0]=='T':	passar=True
			    if len(i[2].split(';'))>=19 and i[2].split(';')[18]=='T':	passar=True
			    if passar and i[3] and len(i[3].split('|'))>=3:
				
				listar=i[3].split('|')
				break

			retorno_prepara_xml = ""
			retorno_backup_xml = ""
			implantado = False

			self.c = False
			self.sftp = ""	
			
			self.dados_backup_cloud = ""
			if listar:
				
				self.ano = datetime.datetime.now().strftime("%Y")
				self.mes = datetime.datetime.now().strftime("%m")
				self.dia = datetime.datetime.now().strftime("%d")
				if len( listar ) == 3:
				
					self.pasta, sql, xml = listar

					pasta_local   = "/home/lykos/bkcloud"
					pasta_retorno = "/home/lykos/bkcloud/retorno"
					if not os.path.exists( pasta_local ):	os.makedirs( pasta_local )
					if not os.path.exists( pasta_retorno ):	os.makedirs( pasta_retorno )

					retorno_sql = pasta_retorno + "/retorno_sql_"+datetime.datetime.now().strftime("%d%m%Y")+'.txt'
					retorno_xml = pasta_retorno + "/retorno_xml_"+datetime.datetime.now().strftime("%d%m%Y")+'.txt'

					self.dados_sql = open( retorno_sql, "a")
					self.dados_xml = open( retorno_xml, "a")
							
					""" Iniciado os backups """
					bak_sql = False
					bak_xml = False
					arquivo_sql = ""
					
					if sql:	bak_sql = self.preparaSQL()
					if xml:	bak_xml = self.preparaXML()

					if self.conexaoFTP():		
						
						if self.c:

							self.erro_ano_retorno=""
							if bak_sql:	self.backupSQL()
							if bak_xml:	self.backupXML()
							if self.erro_ano_retorno:    self.dados_sql.write( str(self.erro_ano_retorno)+"\n")
							print "Fecha conexao"
							self.sftp.close()

					self.dados_sql.close()
					self.dados_xml.close()
                    
					conteudo_erro_sql = open( retorno_sql, 'r' ).read() if os.path.exists( retorno_sql ) else ""
					conteudo_erro_xml = open( retorno_xml, 'r' ).read() if os.path.exists( retorno_xml ) else ""

					if conteudo_erro_sql and "ERRO" in conteudo_erro_sql:  notifica_email.notificar( ar = retorno_sql, tx = "Notificacao do sistema BACKUP SQL", sj = "Notificacao do backup SQL "+str( self.pasta )  )
					if conteudo_erro_xml and "ERRO" in conteudo_erro_xml:  notifica_email.notificar( ar = retorno_xml, tx = "Notificacao do sistema BACKUP XML", sj = "Notificacao do backup XML "+str( self.pasta )  )
					
	def conexaoFTP(self):

		implantado = False
		try:

			print "Conectando ao servidor"
			self.sftp = FTP('drive.caxiashost.com.br', timeout=100)
			self.sftp.login(user='joselobinho', passwd = '151407jml')
			self.c = True
			print "Conectado ao servidor"
			
		except Exception as erro:
			
			self.c = False
			if type( erro ) !=unicode:	erro = str( erro )

		if self.c:
			
			conteudo = []
			self.sftp.dir( '/', conteudo.append )
			for i in conteudo:

				s = filter( None, i.split(' ') )
				if len( s ) >= 8 and s[8] == self.pasta:	implantado = True

		if self.c and not implantado:	self.sftp.close()
		
		return implantado
		
	def backupSQL( self ):

		pasta_sql_ano = "/"+ self.pasta + "/SQL/"+self.ano
		pasta_sql_ano_ok = False
		erro_ano = ""
		self.erro_ano_retorno = ""
		""" Criando a pasta do ano atual """
		try:
			self.sftp.mkd( pasta_sql_ano )
			pasta_sql_ano_ok = True
		
		except Exception as erro_ano:
			
			if 'exists' in str( erro_ano ):	pasta_sql_ano_ok = True
			else:	self.dados_xml.write( "backup_SQL|ERRO|criando pasta remoto ano "+str( pasta_sql_ano  ) )
			self.erro_ano_retorno = erro_ano
            
		if pasta_sql_ano_ok:
			
			pasta_destino = pasta_sql_ano +"/"
			pasta_origem  = "/home/lykos/bkcloud/sql/"
			filelist = glob.glob( pasta_origem + '*.zip' )
		
			if filelist:

				self.dados_sql.write( "backup_sql|OK|Copiando o arquivo para o FTP\n")
				for f in filelist:

					if f:

						try:
							
							print "Enviando ao servidor remoto ",f
							arquivo_remoto = f.split('/')[-1]
							self.sftp.storbinary("STOR " + pasta_destino + arquivo_remoto, open( f, 'r') )
							print "Enviado ao servidor remoto ",arquivo_remoto, f

						except Exception as erro_copia_remoto:

							self.dados_sql.write( "backup_sql|ERRO|Copiando o arquivo para o FTP "+str( erro_copia_remoto ) + "\n" )
    
	def preparaSQL(self):

		retorno = False
		""" Cria pasta para copiar os arquivo para backup, apaga arquivos anteriores se existir  """
		pasta_bak = "/home/lykos/bkcloud/sql"
		pasta_tabela = "/mnt/lykos/direto/importar/tabelas.py"

		if not os.path.exists( pasta_bak ):	os.makedirs( pasta_bak )
		if os.path.exists( pasta_bak ) and os.path.exists( pasta_tabela ):
		
			self.dados_sql.write( "prepara_sql|OK|Preparando BACKUP SQL\n" )
	
			print "Removendo arquivos antigos SQL-ZIP pasta local"

			filelist = glob.glob( pasta_bak + '/*')
			if filelist:
				
				for f in filelist:
					
					os.remove( f )

			tabelas_sql = open(pasta_tabela,"r").readlines()
			passagem = True	
			for i in tabelas_sql:
						
				"""  Filtra apenas o nome das tabelas  """
				if 'IF NOT EXISTS' in i:

					tabelas = i.split("IF NOT EXISTS")[1].split('(')[0].strip()
					if tabelas:
						
						backup_sql = pasta_bak + '/' + self.pasta.split('_')[0].lower() +'_'+ tabelas +'_'+ self.ano +'.sql'
						backup_zip = backup_sql.split('.')[0] +'.zip'

						print "Montando BACKUP SQL ",backup_sql
						back = "mysqldump sei "+ tabelas +" -u root -p151407jml > "+backup_sql
						abri = commands.getstatusoutput( back )
		
						if abri[0] == 0:
							
							print "Compactando o arquivo SQL para ZIP ",backup_zip
							try:
		
								jungle_zip = zipfile.ZipFile( backup_zip, 'w')
								jungle_zip.write( backup_sql, compress_type=zipfile.ZIP_DEFLATED)

								if os.path.exists( backup_zip ):

									print "Removendo o arquivo SQL ",backup_sql
									os.remove( backup_sql )
									retorno = True

							except Exception as erro_zip:

								self.dados_sql.write( "prepara_sql|ERRO|Compactando o arquivo SQL para ZIP " + str( erro_zip ) + '\n' )
								print "erro_zip: ",erro_zip
								
						else:

							print "Monta arquivo de backup SQL ",abri
							self.dados_sql.write( "prepara_sql|ERRO|MysqlDUMP, Backup do SQL " + str( abri ) + '\n' )
							
		return retorno
		
#--// Prepada arquivos XML na pasta p/fazer o backup
	def preparaXML(self):

		retorno = False
		
		filial = self.pasta.split('_')[0]
		conn  = sqldbs()
		sql   = conn.dbc( "Backup", 1 )

		data_hoje = datetime.datetime.now().strftime("%Y-%m-%d")

		""" Cria pasta para copiar os arquivo para backup, apaga arquivos anteriores se existir  """
		pasta_bak = "/home/lykos/bkcloud/xml"
		if not os.path.exists( pasta_bak ):	os.makedirs( pasta_bak )
		if os.path.exists( pasta_bak ):
			
			print "Removendo arquivos antigos XML pasta local"

			filelist = glob.glob( pasta_bak + '/*')
			if filelist:
				
				for f in filelist:
					
					os.remove( f )

		self.dados_xml.write( "prepara_xml|OK|Preparando XML\n"  )
		if not sql[0]:	self.dados_xml.write( "prepara_xml|OK|Preparando XML, Erro na abertura da tabela\n"  )

		if sql[0]:
			
			if sql[2].execute("SELECT nf_nchave, nf_candat FROM nfes WHERE nf_envdat='"+ data_hoje +"'"):
				
				for i in sql[2].fetchall():
					
					tipo = i[0][20:22]
					canc = i[1]
					
					if sql[2].execute("SELECT sf_arqxml FROM sefazxml WHERE sf_nchave='"+ i[0] +"'"):
						
						try:
							
							arquivo_leitura = sql[2].fetchone()[0]
							doc = xml.dom.minidom.parseString( arquivo_leitura )
							cst,  b1 = geraPDF.XMLLeitura(doc,"infProt","cStat") #--: CST de Retorno
							cnpj, b2 = geraPDF.XMLLeitura(doc,"emit","CNPJ") #------: CNPJ do emitente

							if cst[0] == '100':
								
								if canc:	cancela = "_cancelado"
								else:	cancela = ""
								arquivo = i[0]+ '_nfe_' + cnpj[0] + cancela +'.xml'
								if tipo == "65":	arquivo = i[0]+ '_nfce_' + cnpj[0] + cancela +'.xml'

								__arquivo = open( pasta_bak + '/' + arquivo,"w")
								__arquivo.write( arquivo_leitura )
								__arquivo.close()
								retorno = True

								print "Gravando XML na pasta local: ",arquivo

						except Exception as erro_xml:
							
							retorno = False
							self.dados_xml.write( "prepara_xml|ERRO|Gravando XML na pasta local arquivo: "+str( i[0] ) +' erro: '+str( erro_xml) + '\n'  )
							
		return retorno
		
	def backupXML(self):

		meses = {"01":"janeiro","02":"fevereiro","03":"marco","04":"abril","05":"maio","06":"junho","07":"julho","08":"agosto","09":"setembro","10":"outubro","11":"novembro","12":"dezembro"}
		__mes = meses[self.mes]
		pasta_xml_ano = "/"+ self.pasta + "/XML/"+self.ano
		pasta_xml_mes = "/"+ self.pasta + "/XML/"+self.ano+"/"+__mes
		pasta_xml_dia = "/"+ self.pasta + "/XML/"+self.ano+"/"+__mes +"/"+self.dia
		pasta_xml_ano_ok = False
		pasta_xml_mes_ok = False
		pasta_xml_dia_ok = False
		
		""" Criando a pasta do ano atual """
		try:
			
			self.sftp.mkd( pasta_xml_ano )
			pasta_xml_ano_ok = True
		
		except Exception as erro_ano:
			
			if 'exists' in str( erro_ano ):	pasta_xml_ano_ok = True
			else:	self.dados_xml.write( "backup_xml|ERRO|criando pasta remoto ano "+str( pasta_xml_ano  ) )

		""" Criando a pasta do mes atual """
		try:
			
			self.sftp.mkd( pasta_xml_mes )
			pasta_xml_mes_ok = True
		
		except Exception as erro_mes:
			
			if 'exists' in str( erro_mes ):	pasta_xml_mes_ok = True
			else:	self.dados_xml.write( "backup_xml|ERRO|criando pasta remoto mes "+str( pasta_xml_mes  ) )

		""" Criando a pasta do dia atual """
		try:
			
			self.sftp.mkd( pasta_xml_dia )
			pasta_xml_dia_ok = True
		
		except Exception as erro_dia:
			
			if 'exists' in str( erro_dia ):	pasta_xml_dia_ok = True
			else:	self.dados_xml.write( "backup_xml|ERRO|criando pasta remoto dia "+str( pasta_xml_dia  ) )

		#// Inicio do backup para arquivos de XML
		if pasta_xml_ano_ok and pasta_xml_mes_ok and pasta_xml_dia_ok:
			
			pasta_origem = "/home/lykos/bkcloud/xml/*.xml"
			pasta_destino = pasta_xml_dia +'/'

			filelist = glob.glob( pasta_origem )
			if filelist:
				
				try:
					
					for f in filelist:
						
						arquivo_remoto = f.split('/')[-1]
						self.sftp.storbinary("STOR " + pasta_destino + arquivo_remoto, open( f, 'r') )
						print "Enviando ao servidor remoto ",arquivo_remoto

				except Exception as erro_envia_xml:

					self.dados_xml.write( "backup_xml|ERRO|Enviando XML ao FTP "+str( erro_envia_xml  ) )
					
		
class sqldbs:

	def dbc(self,messa,op):

		try:

			conn = MySQLdb.connect(host = "127.0.0.1",user = "root",passwd = "151407jml", db = "sei", connect_timeout=10)
			curs = conn.cursor()

			return True,conn,curs

		except Exception, _reTornos:

			os.system("clear")
			print "E R R O !!\n\n{ Abertura do Banco de Dados }\n\nRetorno: "+str(_reTornos)	

		return False,'',''

	def cls(self,db):

		db.close()

if __name__ == '__main__':

	bk = BackupCloud()
	bk.conexaoFtp()
