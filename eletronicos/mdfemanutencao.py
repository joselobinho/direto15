#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  mdfemanutencao.py

#  Jose de almeida lobinho { 18-12-2018 13:17 }
import os
import datetime
from lxml import etree
from xml.dom import minidom

from conectar import login,dialogos,menssagem, diretorios, numeracao, sqldb
from collections import OrderedDict

from eletronicos.manutencao import ManutencaoSefaz, NotaFiscalParametros
from eletronicos.__init__ import CODIGOS_UF,CODIGO_PAIS
from nfe400 import DadosCertificadoRetornos,Nfs400

alertas=dialogos()
mens=menssagem()
msf=ManutencaoSefaz()
informes=DadosCertificadoRetornos()
nfs4=Nfs400()
numeros= numeracao()

class EventosMdfe:
	
    def status(self,parent,filial):
	ds=informes.dadosIdentificacao( filial, parent, modelo='58', gravar = False)

	if ds[0]:

	    _mensagem = mens.showmsg("STATUS: Comunicando com o servidor da SEFAZ\n\nAguarde...")
	    status = OrderedDict([
	    ('tpAmb',ds[2]),
	    ('xServ','STATUS')
	    ])

	    xml = msf.statusNFs( status )

	    del _mensagem
	    rt = informes.retornosSefaz( xml, ["retConsStatServMDFe"], parent, nome_evento = 'STATUS-Lykos',modelo=None )
	    if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], 1, '58', rt[4], '', filial, '', '', '', None, False )

    def consultaMdfeChave(self,parent,filial,chave):

	ds=informes.dadosIdentificacao( filial, parent, modelo='58', gravar = False)
	if ds[0]:

	    _mensagem = mens.showmsg("CONSULTAR CHAVE MDFE: Comunicando com o servidor da SEFAZ\n\nAguarde...")
	    consultar = OrderedDict([
	    ('tpAmb',ds[2]),
	    ('xServ','CONSULTAR'),
	    ('chMDFe',chave)
	    ])

	    xml = msf.consultarNotaFiscalChave( consultar )

	    del _mensagem
	    rt = informes.retornosSefaz( xml, ["retConsSitMDFe","protMDFe","procEventoMDFe"], parent, nome_evento = 'Consultar chave MDFe-Lykos', modelo=None )
	    if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], 1, '58', rt[4], '', filial, '', '', '', None, False )

    def consultaRecibo(self,parent,filial,recibo):

	ds=informes.dadosIdentificacao( filial, parent, modelo='58', gravar = False)
	if ds[0]:

	    _mensagem = mens.showmsg("CONSULTAR RECIBO MDFE: Comunicando com o servidor da SEFAZ\n\nAguarde...")

	    xml = msf.mdfeConsultaRecibo(recibo)
	    del _mensagem
	    rt = informes.retornosSefaz( xml, ["retConsReciMDFe","protMDFe"], parent, nome_evento = 'Consultar recibo MDFe-Lykos' )
	    if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], 1, '58', rt[4], '', filial, '', '', '', None, False )
	    if rt[0] and xml:	return True,xml
	    else:	return False,None

    def consNaoEncerrada(self,parent,filial):

	ds=informes.dadosIdentificacao( filial, parent, modelo='58', gravar = False)
	if ds[0]:

	    _mensagem = mens.showmsg("CONSULTAR MDFE NAO ENCERRADAS: Comunicando com o servidor da SEFAZ\n\nAguarde...")
	    xmlstring = msf.mdfeConsultaNaoEncerrada(ds[6])
	    del _mensagem
	    rt = informes.retornosSefaz( xmlstring, ["retConsMDFeNaoEnc"], parent, nome_evento = 'Consultar MDFe nao encerradas' )

	    if rt[0] and rt[4]=='111':	parent.adicionaNaoEncerradas(xmlstring,ds[6])
	    else:
		if rt[0]:	informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], 1, '58', rt[4], '', filial, '', '', '', None, False )

    def encarramentoMdfe(self,parent,filial,tags):

	grva=gravaRetorno()
	
	ds=informes.dadosIdentificacao( filial, parent, modelo='58', gravar = False)
	df=login.filialLT[filial]
	dd=ConfeccaoMDFe()
	data_emissao=dd.retornaData(filial)
	data_hoje=datetime.datetime.now().strftime("%Y-%m-%d")
	if ds[0]:

	    id_evento="ID110112"+tags['chave']+"01"
	    infEvento=OrderedDict([
	    ("cOrgao",tags['chave'][:2]),
	    ("tpAmb",tags["ambiente"]),
	    ("CNPJ",tags["cnpj"]),
	    ("chMDFe",tags['chave']),
	    ("dhEvento",data_emissao),
	    ("tpEvento","110112"),
	    ("nSeqEvento","1")
	    ])

	    detEvento=OrderedDict([
	    ("descEvento","Encerramento"),
	    ("nProt",tags['protocolo']),
	    ("dtEnc",data_hoje),
	    ("cUF",tags['cmunicipiodescarga'][:2]),
	    ("cMun",tags['cmunicipiodescarga'])
	    ])
	
	    xml=msf.encerramentoMdfe(id_evento,infEvento,detEvento)
    	    rt = informes.retornosSefaz( xml, ["retEventoMDFe"], parent, nome_evento = 'Encerramento da MDFe', modelo=None )
	    if rt[0]:
		
		if rt[4] in ['135','631']:
		    grva.salvaDados(parent,filial,3,xml, tags['chave'], None)
		    parent.atualizarLista()	
		    
		informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], 1, '58', rt[4], '', filial, '', '', '', None, False )

    def cancelamentoMdfe(self,parent,filial,tags):

	grva=gravaRetorno()
	
	ds=informes.dadosIdentificacao( filial, parent, modelo='58', gravar = False)
	df=login.filialLT[filial]
	dd=ConfeccaoMDFe()
	data_emissao=dd.retornaData(filial)
	data_hoje=datetime.datetime.now().strftime("%Y-%m-%d")

	NotaFiscalParametros.gravar_xml_original_mdfe=grva
	NotaFiscalParametros.gravar_xml_original_mdfe_parente=parent
	NotaFiscalParametros.gravar_xml_original_mdfe_filial=filial
	NotaFiscalParametros.gravar_envio_retorno=True
	NotaFiscalParametros.metodo='cancelamento'

	m.pastaGravacao(filial,tags["serie"],tags["numero"],tags["ambiente"])

	if ds[0]:

	    id_evento="ID110111"+tags['chave']+"01"
	    infEvento=OrderedDict([
	    ("cOrgao",tags['chave'][:2]),
	    ("tpAmb",tags["ambiente"]),
	    ("CNPJ",tags["cnpj"]),
	    ("chMDFe",tags['chave']),
	    ("dhEvento",data_emissao),
	    ("tpEvento","110111"),
	    ("nSeqEvento","1")
	    ])

	    detEvento=OrderedDict([
	    ("descEvento","Cancelamento"),
	    ("nProt",tags['protocolo']),
	    ("xJust",tags['justificativa'])
	    ])
	
	    xml=msf.cancelamentoMdfe(id_evento,infEvento,detEvento)
    	    rt = informes.retornosSefaz( xml, ["retEventoMDFe"], parent, nome_evento = 'Cancelamento da MDFe', modelo=None )
	    if rt[0]:
		
		if rt[4] in ['135','631']:

		    grva.salvaDados(parent,filial,8,xml, tags['chave'], rt[4])
		    parent.atualizarLista()	
		    
		informes.mostrarInformacoesRetorno( parent, rt[1], rt[2], 1, '58', rt[4], '', filial, '', '', '', None, False )

	    
class ConfeccaoMDFe:
	
    def mdfe300(self,parent,parente,filial):

	grva=gravaRetorno()
	self.p=parent
	ds=informes.dadosIdentificacao( filial, self.p, modelo='58', gravar = False)
	
	gravar_anterior=False
	if self.p.aproveitamento_ultimo.GetValue() and len(self.p.aproveitamento_ultimo.GetLabel().split(':'))==2:

	    gravar_anterior=True
	    mdfe=int(self.p.aproveitamento_ultimo.GetLabel().split(':')[1])
	else:

	    mdfe=numeros.numero("18" ,"Numero da MDFe",self.p, filial ) #-// Gerando um novo numero
	    if not mdfe:
					    
		alertas.dia(self.p,u"Numero de MDFe não foi gerado, Tente novamente...\n"+(" "*160),u"Emissão de NFes")
		return

	"""  Composicao do numero da chave  """
	numero_mdfe=str(mdfe)
	numero_mdfe_fiscal=str(numero_mdfe).zfill(9)
	numero_compoe_chave=str(nfs4.numeroCompoeChave(numero_mdfe)).zfill(8) 
	ano_mes_compoe_mdfe=str(datetime.datetime.now().strftime("%y%m"))
	documento_emissor=str(login.filialLT[filial][9]).zfill(14)
	modelo_mdfe='58'
	numero_serie=str(login.filialLT[filial][44]).zfill(3)
	forma_emissao='1' #--// 1-Emissao normal 2-contigencia
	codigo_municipio_ocorrencia=str(CODIGOS_UF[ds[1]])
	chave = codigo_municipio_ocorrencia+ano_mes_compoe_mdfe+documento_emissor+modelo_mdfe+numero_serie+numero_mdfe_fiscal+forma_emissao+numero_compoe_chave
	chave_digito = nfs4.nfeCalculaDigito( chave )
	chave_numero=chave + chave_digito
	chave_id='MDFe'+chave_numero

	""" Gravacao inicial da MDFe no controle """
	grv_inicial=ds[2], numero_mdfe, numero_serie, chave_numero 
	if not gravar_anterior:	grva.salvaDados(parent,filial,1,grv_inicial,None,None)
	
#---// Confeccaao da MDFE [ ID-Informe ]
	mdfe=m.identifca( versao='3.00', id_mdfe=chave_id )

#---// Confeccaao da MDFE [ Ide ]
	tpemit=self.p.emitente_tipo.GetValue().split('-')[0].strip()
	tptransp=self.p.transporte_tipo.GetValue().split('-')[0].strip()
	modal=self.p.modal_transporte.GetValue().split('-')[0].strip()

	carga=self.p.estado_carga.GetValue().split('-')[0].strip()
	descarga=self.p.estado_descarga.GetValue().split('-')[0].strip()
	
	municipio_codigo_carga=self.p.municipio_carga.GetValue().strip(),self.p.codigo_municipio_carga.GetValue().strip()
	municipio_percurso=[self.p.lista_percurso.GetItem(mp,0).GetText().split('-')[0] for mp in range(self.p.lista_percurso.GetItemCount())] if self.p.lista_percurso.GetItemCount() else []
	viagem_verde=['','']

	"""  Alguns servidore nao estavam sincronizando """
	data_emissao=self.retornaData(filial)
	
	ide=OrderedDict([
	("cUF",CODIGOS_UF[ds[1]]),
	("tpAmb",ds[2]),
	("tpEmit",tpemit), #--// 1 - Prestador de serviço de transporte 2 - Transportador de Carga Própria 3 - Prestador de serviço de transporte que emitirá CT-e Globalizado OBS: Deve ser preenchido com 2 para emitentes de NF-e e pelas transportadoras quando estiverem fazendo transporte de carga própria. Deve ser preenchido com 3 para transportador de carga que emitirá à posteriori CT-e Globalizado relacionando as NF-e.
	("tpTransp",tptransp), #--// 1 - ETC 2 - TAC 3 - CTC
	("mod","58"), #--// Utilizar o código 58 para identificação do MDF-e
	("serie",str(int(numero_serie))), #--// Informar a série do documento fiscal (informar zero se inexistente). Série na faixa [920-969]: Reservada para emissão por contribuinte pessoa física com inscrição estadual.
	("nMDF",numero_mdfe), #--// Número que identifica o Manifesto. 1 a 999999999
	("cMDF",numero_compoe_chave), #--// Código numérico que compõe a Chave de Acesso
	("cDV",chave_digito), #--// Informar o dígito de controle da chave de acesso do MDF-e, que deve ser calculado com a aplicação do algoritmo módulo 11 (base 2,9) da chave de acesso.
	("modal",modal), #--// 1 - Rodoviário; 2 - Aéreo; 3 - Aquaviário; 4 - Ferroviário.
	("dhEmi",data_emissao), #--// Data e hora de emissão do Manifesto, Formato AAAA-MM-DDTHH:MM:DD TZD
	("tpEmis","1"), #--// 1 - Normal ; 2 - Contingência
	("procEmi","0"), #--// 0 - emissão de MDF-e com aplicativo do contribuinte; 3- emissão MDF-e pelo contribuinte com aplicativo fornecido pelo Fisco.
	("verProc","MDFe_Direto"), #--// Informar a versão do aplicativo emissor de MDF-e
	("UFIni",carga), #--// Sigla da UF do Carregamento
	("UFFim",descarga) #--// Sigla da UF do Descarregamento
	])
	mdfe.append( m.ide( ide, municipio_codigo_carga, municipio_percurso, viagem_verde ) )
	
#---// Emitente [ emit ]	
	df=login.filialLT[filial]
	telefone=login.filialLT[ filial ][10].split('|')[0].replace(' ','').replace('-','').replace('(','').replace(')','').replace('.','').decode('UTF-8')
	
	emit=OrderedDict([
	("CNPJ",df[9].strip()),
	("CPF",""),
	("IE",df[11].strip()),
	("xNome",df[1].strip().decode('UTF-8')),
	("xFant",df[14].strip().decode('UTF-8'))
	])

	emit_endereco=OrderedDict([
	("xLgr",df[2].strip().decode('UTF-8')),
	("nro",df[7].strip().decode('UTF-8')),
	("xCpl",df[8].strip().decode('UTF-8')),
	("xBairro",df[3].strip().decode('UTF-8')),
	("cMun",df[13].strip().decode('UTF-8')),
	("xMun",df[4].strip().decode('UTF-8')),
	("CEP",df[5].strip().decode('UTF-8')),
	("UF",df[6].strip().decode('UTF-8')),
	("fone",telefone),
	("email",'')
	])

	mdfe.append( m.emit( emit, emit_endereco ) )

#---// Modal [ infModal, versao ]
	codigo_veiculo=str(int(self.p.veiculos_relacao.GetValue().split('-')[0])) if self.p.veiculos_relacao.GetValue().split('-')[0] else ""
	dv=self.p.veiculos[codigo_veiculo].split('|') #--// Dados do veiculo
	pp=dv[8].split(';')
	pro_cpf=pp[0] if len(pp[0])==11 else ''
	pro_cnpj=pp[0] if len(pp[0])==14 else ''
	versao='3.00'
	
	veiculo=OrderedDict([
	("cInt",codigo_veiculo), #--// Código interno do veículo
	("placa",dv[0]),
	("RENAVAM",dv[1]),
	("tara",dv[2]), #--// Tara em KG
	("capKG",dv[3]), #--// Capacidade em KG
	("capM3",dv[4]) #--// Capacidade em M3
	])

	proprietario=OrderedDict([
	("CPF",pro_cpf),
	("CNPJ",pro_cnpj),
	("RNTRC",pp[2]),
	("xNome",pp[1]),
	("IE",pp[3]),
	("UF",pp[4]),
	("tpProp",pp[5]) #--// Preencher com: 0-TAC – Agregado; 1-TAC Independente; ou 2 – Outros.
	])

#---// Informacoes do documento { infDoc }
	condutores=self.p.lista_condutores if self.p.lista_condutores else None
	
	rodo_tipo=OrderedDict([
	("tpRod",dv[5]), #--// Preencher com: 01 - Truck; 02 - Toco; 03 - Cavalo Mecânico; 04 - VAN; 05 - Utilitário; 06 - Outros.
	("tpCar",dv[6]), #--// Tipo de Carroceria - Preencher com: 00 - não aplicável; 01 - Aberta; 02 - Fechada/Baú; 03 - Granelera; 04 - Porta Container; 05 - Sider
	("UF",dv[7])
	])
	
	if veiculo['cInt'] and veiculo['placa']:	mdfe.append( m.modal( versao, veiculo, proprietario, condutores, rodo_tipo ) )
	if self.p.relacao_nfes:	mdfe.append( m.infoDoc( self.p.relacao_nfes ) )

#---// Totalizadores da carga transportada e seus documentos fiscais { tot }
	qNFe=self.p.quantidade_notas.GetValue().strip()
	vCarga=self.p.valor_total_carga.GetValue().strip().replace(',','')
	cUnid=self.p.unidade_carga.GetValue().strip().split('-')[0]
	qCarga=self.p.peso_bruto_carga.GetValue().strip().strip().replace(',','')

	tot_carga=OrderedDict([
	("qNFe",qNFe),
	("vCarga",vCarga),
	("cUnid",cUnid),
	("qCarga",qCarga)
	])
	mdfe.append( m.infTot( tot_carga ) )

#---// Informacoes complementares
	if self.p.inf_complementares.GetValue().strip():	mdfe.append( m.infAdincionais( self.p.inf_complementares.GetValue().strip() ) )

	NotaFiscalParametros.gravar_xml_original_mdfe=grva
	NotaFiscalParametros.gravar_xml_original_mdfe_parente=parent
	NotaFiscalParametros.gravar_xml_original_mdfe_filial=filial
	NotaFiscalParametros.gravar_envio_retorno=True
	m.pastaGravacao(filial,numero_serie,numero_mdfe,ds[2])

	
	xml_autorizado, status = msf.autorizacaoSefaz( tags={'idLote':'1','indSinc':'1'}, xml=mdfe, chave=chave_id, modelo='58', recuperar=None)

	rt = informes.retornosSefaz( xml_autorizado, ["retConsReciMDFe","infProt"], parente, nome_evento = 'Retorno de autorizacao', modelo='58' )
	rt1= informes.retornosSefaz( xml_autorizado, ["protMDFe"], parente, nome_evento = 'Retorno de autorizacao', modelo='58' )

	if status=='104' and rt1[4]=='611': #--// Placa com mdfe nao encerrada
	    grva.salvaDados(parent,filial,4,chave_numero,rt1[4], None)

	if status in['100','611','612','101','102','225','580','663']:
	    if status in['100']:
		
		grva.salvaDados(parent,filial,2,xml_autorizado, (rt[3],rt[4],rt[5],rt[6]), self.p.nfes_envio)
		self.p.aproveitamento_ultimo.SetLabel(u"Aproveitamento da ultima MDFe")
		self.p.aproveitamento_ultimo.SetValue(False)
		self.p.limpeza()
		

	    if status in['611','612','101','102','225','580','663']:
		grva.salvaDados(parent,filial,4,chave_numero,status, xml_autorizado)
		self.p.aproveitamento_ultimo.SetLabel(u"Aproveitamento da ultima MDFe: "+numero_mdfe)

	parent.relacionarListaEmissao()
	    
	if rt[0]:	informes.mostrarInformacoesRetorno( parente, rt[1], rt[2], 1, '58', rt[4], '', filial, '', '', '', None, False )

    def retornaData(self,filial):
	
	"""  Alguns servidore nao estavam sincronizando """
	if len(login.filialLT[filial][30].split(';')) >=14 and login.filialLT[filial][30].split(';')[13]:
	    data_emissao=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')+'-'+login.filialLT[filial][30].split(';')[13] #--// utilizando o timezone do sistema
	else:	data_emissao=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')+'{}:{}'.format(strftime('%z')[:-2], strftime('%z')[-2:])

	return data_emissao

class gravaRetorno:
    
    def salvaDados(self,parent,filial,opcao,d1,d2,d3):
	
	""" Opcao
	    1-gravacao Numero NF,Serie,Emissao
	"""
	conn=sqldb()
	sql=conn.dbc("MDFe: Gravar retornos", fil = filial, janela=parent)
	if sql[0]:
	    
	    if opcao==1:

		emissao=datetime.datetime.now().strftime("%Y-%m-%d") #->[ Data de Recebimento ]
		hora_emissao=datetime.datetime.now().strftime("%T") #------->[ Hora do Recebimento ]
		
		grv="INSERT INTO mdfecontrole (md_filial,md_numdfe,md_ambien,md_nserie,md_emissa,md_horaem,md_usuari,md_nchave,md_usemis,md_ushora,md_ususua) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		sql[2].execute(grv,(filial, d1[1], d1[0], d1[2], emissao, hora_emissao, login.usalogin, d1[3], emissao, hora_emissao, login.usalogin ))
		sql[1].commit()

	    elif opcao==2: #--// Gravar XML autorizado
		chave, csTaT, protocolo, data_recebimento=d2

		data=data_recebimento.split('T')[0]
		hora=data_recebimento.split('T')[1].split('-')[0]

		listas_nfes=''
		if d3.GetItemCount():
		    
		    for i in range(d3.GetItemCount()):
			listas_nfes+=d3.GetItem(i,2).GetText()+','

		sql[2].execute("UPDATE mdfecontrole SET md_xmlmdf='"+d1+"', md_cstatu='"+csTaT+"',md_emissa='"+data+"',md_horaem='"+hora+"',md_usuari='"+login.usalogin+"',md_protoc='"+protocolo+"',md_status='2',md_relnfe='"+listas_nfes+"' WHERE md_nchave='"+ chave +"'")
		sql[1].commit()

	    elif opcao==3: #--// Gravar XML do encerramento

		encerramento="Encerramento: "+datetime.datetime.now().strftime("%Y-%m-%d %T")+" "+login.usalogin
		if sql[2].execute("SELECT md_dadosu FROM mdfecontrole WHERE md_nchave='"+ d2 +"'"):
		    d=sql[2].fetchone()[0]
		    if d:	encerramento+="\n\n"+d
		    
		sql[2].execute("UPDATE mdfecontrole SET md_xmlenc='"+d1+"',md_status='3',md_dadosu='"+encerramento+"' WHERE md_nchave='"+ d2 +"'")
		sql[1].commit()

	    elif opcao==4: #--// Foi emitida mdfe com a placa do veiculo e nao foi encerrada Rejeicao: 611
		    
		sql[2].execute("UPDATE mdfecontrole SET md_xmlrej='"+d3+"',md_cstatu='"+d2+"' WHERE md_nchave='"+ d1 +"'")
		sql[1].commit()

	    elif opcao==5: #--// Foi emitida mdfe com a placa do veiculo e nao foi encerrada Rejeicao: 611

		recuperado="Recuperado: "+datetime.datetime.now().strftime("%Y-%m-%d %T")+" "+login.usalogin
		if sql[2].execute("SELECT md_dadosu,md_recibo FROM mdfecontrole WHERE md_nchave='"+ d1 +"'"):
		    d=sql[2].fetchone()
		    if d[0]:	recuperado+="\n\n"+d
		    if d[1]:	recibo = d[1]

		data=d3[0].split('T')[0]
		hora=d3[0].split('T')[1].split('-')[0]
		if not recbio and len(d3)>=3 and d3[2]:	recibo = d[2]

		sql[2].execute("UPDATE mdfecontrole SET md_cstatu='100',md_emissa='"+data+"',md_horaem='"+hora+"',md_usuari='"+login.usalogin+"',md_protoc='"+d3[1]+"',md_xmlmdf='"+d2+"',md_status='2',md_dadosu='"+recuperado+"',md_recibo='"++"' WHERE md_nchave='"+ d1 +"'")
		sql[1].commit()
		parent.atualizarLista()

	    elif opcao==6: #--// Grava o XML original assinado para recuperacao anterior atraves do recibo
		
		sql[2].execute("UPDATE mdfecontrole SET md_xmlmdf='"+ d2 +"' WHERE md_nchave='"+ d1[4:] +"'")
		sql[1].commit()

	    elif opcao==7: #--// Grava o numero do recibo e o cstat para recuperacao posterior
		
		status='1' if d3.strip()=='103' else ''
		sql[2].execute("UPDATE mdfecontrole SET md_recibo='"+ d2 +"', md_cstatu='"+ d3 +"', md_status='"+ status +"' WHERE md_nchave='"+ d1[4:] +"'")
		sql[1].commit()

	    elif opcao==8: #--// Gravar XML do cacelamento

		cancelamento="Cancelamento: "+datetime.datetime.now().strftime("%Y-%m-%d %T")+" "+login.usalogin
		if d3=='631':	cancelamento="Cancelamento { Cancelado anteriormente }: "+datetime.datetime.now().strftime("%Y-%m-%d %T")+" "+login.usalogin

		if sql[2].execute("SELECT md_dadosu FROM mdfecontrole WHERE md_nchave='"+ d2 +"'"):
		    d=sql[2].fetchone()[0]
		    if d:	cancelamento+="\n\n"+d

		if d3=='631':	sql[2].execute("UPDATE mdfecontrole SET md_status='4' WHERE md_nchave='"+ d2 +"'")
		else:	sql[2].execute("UPDATE mdfecontrole SET md_xmlcan='"+d1+"',md_status='4',md_dadosu='"+cancelamento+"' WHERE md_nchave='"+ d2 +"'")
		sql[1].commit()

	    conn.cls(sql[1])

	
#--------------------------------------// Confeccao do XML //
class ConfeccaoXml:

#// IDE
    def identifca(self,versao='3.00', id_mdfe=None):

        raiz = etree.Element('infMDFe', versao=versao)
        raiz.attrib['Id']=id_mdfe

        return raiz
			
    def ide(self, tags, carregamento, percursos, viagemverde):

        raiz = etree.Element('ide')
        for i in tags:
            if tags[i]:	etree.SubElement(raiz, i ).text = tags[i]

	""" Carregamento """
	if carregamento and len(carregamento)==2:
	    municipio,codigo=carregamento
	    carga=etree.SubElement(raiz, 'infMunCarrega')
	    etree.SubElement(carga, 'cMunCarrega' ).text=codigo
	    etree.SubElement(carga, 'xMunCarrega' ).text=municipio

	if percursos:

	    for ufp in percursos:
		percurso=etree.SubElement(raiz, 'infPercurso')
		if ufp:	etree.SubElement(percurso, 'UFPer' ).text=ufp
	    

	""" Opcionais faz parte da raiz apos carregamento e percurso """
	if viagemverde and len(viagemverde)>=1 and viagemverde[0]:	etree.SubElement(raiz, 'dhIniViagem' ).text=viagemverde[0]
	if viagemverde and len(viagemverde)>=2 and viagemverde[1]:	etree.SubElement(raiz, 'indCanalVerde' ).text=viagemverde[1]

	return raiz

#// EMITENTE
    def emit(self,tags,enderecos):

        raiz = etree.Element('emit')
        for i in tags:
            if tags[i]:	etree.SubElement(raiz, i ).text = tags[i]

	endereco=etree.SubElement(raiz, 'enderEmit')
        for i in enderecos:
            if enderecos[i]:	etree.SubElement(endereco, i ).text = enderecos[i]

	return raiz

#// MODAL
    def modal(self,versao, veiculo, proprietario, condutor, rodo_tipo):

	raiz=etree.Element('infModal',versaoModal=versao)
	rodo=etree.SubElement(raiz, 'rodo')
	veic=etree.SubElement(rodo, 'veicTracao')
	for i in veiculo:
	    if veiculo[i]:	etree.SubElement(veic, i ).text = veiculo[i]

	if proprietario['xNome']:
	    prop=etree.SubElement(veic, 'prop')
	    for i in proprietario:
		if proprietario[i]:	etree.SubElement(prop, i ).text = proprietario[i]

	if condutor and condutor.GetItemCount():

	    for i in range(condutor.GetItemCount()):
		if condutor.GetItem(i,0).GetText() and condutor.GetItem(i,1).GetText():
		    cond=etree.SubElement(veic, 'condutor')
		    etree.SubElement(cond, 'xNome' ).text = condutor.GetItem(i,1).GetText()
		    etree.SubElement(cond, 'CPF' ).text = condutor.GetItem(i,0).GetText()
		
	if rodo_tipo:
	    for i in rodo_tipo:
		if rodo_tipo[i]:	etree.SubElement(veic, i ).text = rodo_tipo[i]
	    
	return raiz

#// INFODOC
    def infoDoc(self, tags):

	raiz=etree.Element('infDoc')
	if tags:
	    for d in tags:
		codigo,municipio=d.split('|')
		infdes=etree.SubElement(raiz,'infMunDescarga')
		etree.SubElement(infdes, 'cMunDescarga' ).text=codigo
		etree.SubElement(infdes, 'xMunDescarga' ).text=municipio
		for d in tags[d]:
		    if d:
			nfes=etree.SubElement(infdes,'infNFe')
			etree.SubElement(nfes,'chNFe').text=d
	
	return raiz

#// TOT
    def infTot(self,tags):

	raiz=etree.Element('tot')
	for d in tags:
	    etree.SubElement(raiz, d ).text=tags[d]
    
	return raiz

    def infAdincionais(self,tags):
	raiz=etree.Element('infAdic')
	etree.SubElement(raiz, 'infCpl' ).text=tags
	
	return raiz

    def pastaGravacao(self,filial,serie,nota,ambiente):
    
	__f = filial.lower()
	if os.path.exists(diretorios.esMdfe+__f)==False:	os.makedirs(diretorios.esMdfe+__f)
	diretorio_gravacao=diretorios.esMdfe+__f

	__n = datetime.datetime.now().strftime("%m-%Y") +'/'+ str( serie ).zfill(3)+'-'+str( nota ).zfill(9)
	__d = diretorio_gravacao + "/homologacao/"+ __n if ambiente == '2' else diretorio_gravacao + "/producao/"+ __n
	if os.path.exists( __d ) == False:	os.makedirs( __d )

	NotaFiscalParametros.gravar_envio_retorno_pasta = __d

	return __d

	
m=ConfeccaoXml()
