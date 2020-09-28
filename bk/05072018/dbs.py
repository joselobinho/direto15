#!/usr/bin/env python
# -*- coding: utf-8 -*-
token dropbox: r0BPLaxKRsYAAAAAAAABuU6x9rvOcOPpJuTDaOMftQfPs3awyXXiuAYwOJhiYYrH
19-10-2016
MariaDB [sei]> select ef_idfili,ef_codigo,ef_virtua from estoque where ef_virtua <0;
+-----------+---------------+-----------+
| ef_idfili | ef_codigo     | ef_virtua |
+-----------+---------------+-----------+
| MONAT     | 7890100002423 |   -5.0000 |
| MONAT     | 7890100002676 |   -8.0000 |
+-----------+---------------+-----------+
JPF VER ESSE PRODUTO 230802017 { 372 mdf branco ipx dupla face de 18 }
# Descobrir uid de um usuario
#import pws
#			print diretorios.usAtual, os.getuid()
#			uid = uid = pwd.getpwnam( str( diretorios.usAtual ) )[2]
#			print uid


#####################################################################################################################
### vale americanas: 90800778007659, senha romulott lojas americanas 041110mi senha email romulott filhosdosenho  ###
#####################################################################################################################


## Validar XML no SEFAZ: Valide seu XML no site http://www.sefaz.rs.gov.br/nfe/nfe-val.aspx que vc verá as mensagens de erro.


## CODIGO PARA BEMATECH, 4200,2500 CLIPPER PARA IMPRESSAO DO QR-CODE { http://www.pctoledo.com.br/forum/viewtopic.php?f=20&t=17161 }



# Controle de Clientes e Pagamentos da LYKOS
00-                  create table clientes (cl_regist int(8) not null auto_increment primary key,
01-                  cl_nomecl varchar(100) default '',
02-                  cl_fantas varchar(60) default '',
03-                  cl_docume varchar(14) default '',
04-                  cl_iestad varchar(15) default '',
05-                  cl_imunic varchar(15) default '',
06-Aniv.Fundacao     cl_fundac date,
07-                  cl_cadast date,
08-                  cl_endere varchar(100) default '',
09-                  cl_bairro varchar(30) default '',
10-                  cl_cidade varchar(30) default '',
11-                  cl_cdibge varchar(7)  default '',
12-                  cl_cepcli varchar(9)  default '',
13-                  cl_compl1 varchar(5)  default '',
14-                  cl_compl2 varchar(20) default '',
15-                  cl_estado varchar(02) default '',
16-                  cl_emailc varchar(120) default '',
17-                  cl_telef1 varchar(13) default '',
18-                  cl_telef2 varchar(13) default '',
19-                  cl_telef3 varchar(13) default '',
20- Seguimento       cl_seguim varchar(60) default '',
21- P.Referencia     cl_refere text,
22- Redes Sociais    cl_redeso text,
23- Emails           cl_emails text,
24- Parceiro         cl_clmarc varchar(70)   default '',
25-DT-AlteraInclui   cl_dtincl date default '00-00-0000',
26-HR-AlteraInclus   cl_hrincl time default '00:00:00',
27-Pramametros       cl_parame MEDIUMBLOB,
28-DT-Bloqueio       cl_dtbloq date default '00-00-0000',
29-HR-Bloqueio       cl_hrbloq time default '00:00:00',
30-DT-p/Bloquear     cl_bloque date default '00-00-0000');
31-Valor Mensal      cl_valorm decimal(15,2) default 0,
32-login do servidor cl_logins varchar(100)  default '',
33-DT-atualizacao    cl_dtatua date default '00-00-0000',
34-HR-atualizacao    cl_hratua time default '00:00:00',
35-1-Impla 2-Produ   cl_improd varchar(1) default '2');

# Controle de Clientes e Pagamentos da LYKOS
00-                  create table creceber (rc_regist int(10) not null auto_increment primary key,
01-                  rc_idclie varchar(8) default '',
02-                  rc_nomecl varchar(100) default '',
03-                  rc_fantas varchar(60) default '',
04-                  rc_docume varchar(14) default '',
05-DT-AlteraInclui   rc_dtlanc date default '00-00-0000',
06-HR-AlteraInclus   rc_hrlanc time default '00:00:00',
07-DT-Bloqueio       rc_dtvenc date default '00-00-0000',
08-Valor Mensal      rc_valora decimal(15,2) default 0,
09-Valor Mensal      rc_valorp decimal(15,2) default 0,
10-DT-Baixa          rc_dtbaix date default '00-00-0000',
11-HR-Baixa          rc_hrbaix time default '00:00:00',
12-Dados do Boleto   rc_boleto MEDIUMBLOB,
13-Forma Baixa       rc_formab varchar(30) default '',
14-Dados do cliente  rc_clibol MEDIUMBLOB,
15-Dados do banco    rc_dbanco MEDIUMBLOB,
16-Status            rc_status varchar(1) default '',
17-Tipo de servico   rc_servic varchar(100) default '',
18-DT-Cancelamento   rc_dtcanc date default '00-00-0000',
19-HR-AlteraInclus   rc_hrcanc time default '00:00:00',
20-URL 2 via         rc_bl2via MEDIUMBLOB)

""" { 71 } Vazio aberto 1-baixado 2-cancelados"""


# Cadastro de bancos da LYKOS
00-                  create table bancos (bc_regist int(10) not null auto_increment primary key,
01-numero banco      bc_bnumero varchar(8) default '',
02-agencia           bc_agencia varchar(10) default '',
03-conta corrente    bc_contacr varchar(20) default '',
04-carteira          bc_carteir varchar(10) default '',
05-covenio           bc_conveni varchar(20) default '',
06-especie           bc_especie varchar(10) default '',
07-descricao banco   bc_descric varchar(100) default '',
08-instricao boleto  bc_instruc MEDIUMBLOB,
09-empresa p/boleto  bc_bcempre varchar(120) default '',
10-CPJ p/Cedente     bc_servdoc varchar(14) default '',
11-Endereco p/cedent bc_servend varchar(100) default '');


# Cadastro do cedente
00-                  create table cedente (cd_regist int(1) not null auto_increment primary key,
01-instrucao boleto  cd_dadoscd MEDIUMBLOB);


mysql -h sql8.freemysqlhosting.net -u sql8118814 -paVriEEvR7t
##############################################################################################################

#Parametro do sistema
0 - Registro               create table parametr (pr_regi int(8) not null auto_increment primary key,
1 - CD Produto             pr_cdpd int(7)      default 0,
2 - CD Usuario             pr_usid int(8)      default 0,
3 - CD Barras              pr_barr int(7)      default 0,
4 - No DAV                 pr_ndav int(13)     default 0,
5 - No Comanda             pr_ncmd int(14)     default 0,                                                        #-:Usando para controle do estoque de alocacao local da filial
6 -                        pr_tdav int(12)     default 0,
7 -                        pr_clie int(12)     default 0,                                                        #-:Usando para emitir notas de homologacao
8 - Rodape DAV             pr_rdap text,
9 - Processamento          pr_pros varchar(1)  default '1',
10-Host                    pr_phos varchar(50) default '',
11-Usuario                 pr_pusa varchar(12) default '',
12-Senha                   pr_psen varchar(12)	default '',
13-Banco SQL               pr_sqlb varchar(20) default '',
14-NFe Numero              pr_nfen int(9)      default 0,
15-Nfe Serie               pr_nfse int(3)      default 55,
16-Retra Paissag tpImp     pr_nfim int(1)      default 1,
17-Cod Emissao tpEmis      pr_nfci int(1)      default 1,
18-Finalidade finNFe       pr_nffi int(1)      default 1,
19-Emissao procEmi         pr_nfem int(1)      default 0,
20-Dados Fixo Rodape       pr_nfrd text,
21-Versao NFe              pr_nfvs varchar(4)  default '',
22-Contas AReceber         pr_rece int(11)     default 0,
23-Devolucao Vendas        pr_devv int(10)     default 0,
24-No Compras              pr_comp int(10)     default 0,
25-Codigo de Bordero       pr_bord int(10)     default 0,
26-Bordero Apagar Baixa    pr_borb int(10)     default 0,
27-Controle Contas Apag    pr_cona int(8)      default 0,
28-Romandeio de Entrega    pr_roma int(10)     default 0,
29-Nosso Numero            pr_bole int(10)     default 0,
30-DT p/EntregasApartir    pr_entr date default '00-00-0000',
31-Parametros de Bloqeuio  pr_pblq MEDIUMBLOB,
32-Apagar:FORMA PGT,LANCA  pr_apaf MEDIUMBLOB,
33-Forncedor UN-Manejo     pr_fcum MEDIUMBLOB);
                           
                           
00-ID CodigoFilial         create table cia (ep_regi int(3) not null auto_increment primary key,
01 Nome                    ep_nome varchar(50)  default '',
02-Endereco                ep_ende varchar(50)  default '',
03-Bairro                  ep_bair varchar(20)  default '',
04-Cidade                  ep_cida varchar(20)  default '',
05-CEP                     ep_cepe varchar(9)   default '',
06-Estado                  ep_esta varchar(2)   default '',
07-Complemento             ep_com1 varchar(5)   default '',
08-Complemento             ep_com2 varchar(20)  default '',
09-CPF CNPJ                ep_cnpj varchar(14)  default '',
10-Telefones               ep_tels varchar(60)  default '',
11-Insc.Estadual           ep_iest varchar(14)  default '',
12-Insc.Municipal          ep_imun varchar(14)  default '',
13-Codigo IBGE             ep_ibge varchar(7)   default '',
14-Nome Fantasia           ep_fant varchar(20)  default '',
15-Arquivo Logomarca       ep_logo varchar(30)  default '',
16-Indenficacao Filial     ep_inde varchar(5)   default '',
17-padrao DAV              ep_imdv varchar(200) default '',
18-padrao expedicao        ep_iexp varchar(200) default '',
19-1,2Casas Decimais       ep_arre varchar(1)   default '',
20-dias p/devolucao        ep_ddev varchar(3)   default '',
21-optante paf-ecf         ep_opaf varchar(1)   default '1',
22-Aberto DD Anterior      ep_ddan varchar(1)   default 'F',
23-Dinheir c/Desconto      ep_vdin varchar(1)   default 'F',
24-Ressalva p/Devedor      ep_resd varchar(2)   default '',
25-Email do contador       ep_econ varchar(120) default '',
26-Rodape NFE,DAV          ep_adic text,
27-Sequencial NFE          ep_nfes int(10)      default 0,
28-Sequencial NFCe         ep_nfce int(10)      default 0,
29-Servidro de Email       ep_svem text,
30-Dados NFE               ep_dnfe text,
31-Dados SQL,1             ep_sqls text,
32-Dados SQL,2Financei     ep_sqlf text,
33-Forcar Email venda      ep_fema varchar(1)   default 'F',
34-Ressalva p/Estorno      ep_rese varchar(2)   default '',
35-Parametros Sistema      ep_psis text,
36-FilControladora estLoca ep_darf text,
37-AutalizacoesRemotas     ep_atrm text,
38-Parametros do ACBr      ep_acbr text,
39-ID-do administrativo    ep_admi varchar(8) default '',
40-Parametros produtos     ep_prdo text,
41-credenciamento PJBANK   ep_pjba MEDIUMBLOB);                  #13/01/2018


00- _id do Grupo           create table grupofab (fg_regi int(8) not null auto_increment primary key,
01- Identificacao do Grupo fg_cdpd varchar(1)   default '',
02- Descricao     do Grupo fg_desc varchar(20)  default '',
03- Dados 1                fg_prin varchar(100) default '',
04- Dados 2                fg_fila varchar(100) default '',
05- Dados 3                fg_info MEDIUMBLOB);

# fg_cdpd 4-Descricao de historico curto do controle de conta corrente

00-Registro ID             create table tributos (cd_regi int(8) not null auto_increment primary key,                                                #""" 1-Cfop 2-Ncm 3-CST"""
01-ID Tributo              cd_cdpd varchar(1)    default '',
02-Codigo                  cd_codi varchar(30)   default '',
03-NCM                     cd_cdt1 varchar(12)   default '',
04-CFOP                    cd_cdt2 varchar(12)   default '',
05-CST                     cd_cdt3 varchar(12)   default '',
06-codigo Secundario       cd_cdt4 varchar(12)   default '',
07-Descricao               cd_desc varchar(2000) default '',
08-Operacao                cd_oper varchar(100)  default '',
09-Percentual ICMS         cd_icms decimal(6,2) default 0,
10-p IPI                   cd_tipi decimal(6,2) default 0,
11-p MVA-Dentro ST         cd_mvad decimal(6,2) default 0,
12-p MVA-Fora   ST         cd_mvaf decimal(6,2) default 0,
13-p PIS                   cd_piss decimal(6,2) default 0,
14-p CONFINS               cd_conf decimal(6,2) default 0,
15-p ISS                   cd_imp1 decimal(6,2) default 0,
16-p IBPT-N                cd_imp2 decimal(6,2) default 0,
17-p IBPT-I                cd_imp3 decimal(6,2) default 0,
18-p Reducao ICMS          cd_ricm decimal(6,2) default 0,
19-p Reducao ST            cd_rstb decimal(6,2) default 0,
20-p Imposto_1             cd_imp4 decimal(6,2) default 0,
21-p Imposto_2             cd_imp5 decimal(6,2) default 0,
22-Automatizar[ECF]        cd_auto varchar(20)  default '');


00-                        create table usuario (us_regi int(4) not null auto_increment primary key,
01-                        us_logi varchar(12)  default '',
02-                        us_nome varchar(50)  default '',
03-                        us_senh varchar(20)  default '',
04-                        us_empr varchar(3)   default '',
05-                        us_inde varchar(5)   default '',
06-                        us_ecfs varchar(30)  default '',
07-                        us_emai varchar(200) default '',
08-Impressora padrao       us_ipad varchar(100) default '',
09-Arquivo URL ASS         us_assi varchar(200) default '',
10-Senha do Email          us_shem varchar(50)  default '',
11-Magem de Desconto       us_desc decimal(6,2) not null default 0,
12-Autorizar               us_auto varchar(1)   default '',
13-EmitirCupomFiscal       us_ecfi varchar(1)   default 'F',
14-ECF c/Gaveta            us_gave varchar(1)   default 'F', 
15-PRN NFCe PrinTer        us_pnfc varchar(4)   default '', 
16-Emissao de NFCe         us_nfce varchar(1)   default 'F',
17-Aut-Financeiro          us_seri varchar(3)   default '',                                                                  #-Usado para usuario pode autorizar o financeiro autorizacao remoto e tem espaco p
18-Parametros              us_para MEDIUMBLOB);


0 - Registro               create table produtos (pd_regi int(8) not null auto_increment primary key,
1 - Filial                 pd_fili varchar(3)  not null default '',
2 - codigo                 pd_codi varchar(14) not null,
3 - nome                   pd_nome varchar(120) not null,
4 - caracteristica         pd_cara varchar(50) default '',
5 - feferencia             pd_refe varchar(60) default '',                                                                                           #FOI ALTERADO de 20-Para-30 em 08-05-2017 para 60
6 - codbarra               pd_barr varchar(14) default '',
7 - unidade                pd_unid varchar(2) default 'UN',
8 - grupo                  pd_nmgr varchar(20) default '',
9 - fabricante             pd_fabr varchar(20) default '',
10- cdointerno             pd_intc varchar(20) default '',
11- endereco               pd_ende varchar(10) default '',
12- garantia               pd_gara varchar(2) default '',
13- pesobruto              pd_pesb decimal(8,3) not null default 0,
14- pesoliquido            pd_pesl decimal(8,3) not null default 0,
15- estoquefisico          pd_estf decimal(15,4) not null default 0,
16- estoqueminimo          pd_estm decimal(15,4) not null default 0,
17- estoquemaximo          pd_estx decimal(15,4) not null default 0,
18-Troca-RMA               pd_estt decimal(15,4) not null default 0,
19- estoquevirtual         pd_virt decimal(15,4) not null default 0,
20- margem                 pd_marg decimal(8,3) not null default 0,
21- margemseguranca        pd_mrse decimal(6,2) not null default 0,
22- margemfinal            pd_mfin decimal(6,2) not null default 0,
23- preocicompra           pd_pcom decimal(15,4) not null default 0,
24- precocusto             pd_pcus decimal(15,4) not null default 0,
25- customedio             pd_cusm decimal(15,4) not null default 0,
26- controleunidade        pd_mdun varchar(1) default '1',
27- comissao               pd_coms decimal(6,2) not null default 0,
28-ValorAC-DSpreco1        pd_tpr1 decimal(15,3) not null default 0,
29-Preco2                  pd_tpr2 decimal(15,3) not null default 0,
30-preco3                  pd_tpr3 decimal(15,3) not null default 0,
31-preco4                  pd_tpr4 decimal(15,3) not null default 0,
32-preco5                  pd_tpr5 decimal(15,3) not null default 0,
33-preco6                  pd_tpr6 decimal(15,3) not null default 0,
34-Percentuaismargem1      pd_vdp1 decimal(15,3) not null default 0,
35-margem2                 pd_vdp2 decimal(15,3) not null default 0,
36-margem3                 pd_vdp3 decimal(15,3) not null default 0,
37-margem4                 pd_vdp4 decimal(15,3) not null default 0,
38-margem5                 pd_vdp5 decimal(15,3) not null default 0,
39-margem6                 pd_vdp6 decimal(15,3) not null default 0,
40-controle                pd_cont varchar(1) default '',
41-expedicao               pd_nimp varchar(2) default '',
42-promocao                pd_prom varchar(1) default '',
43-permitir desconto       pd_pdsc varchar(1) default '',
44-controlaritem           pd_prod varchar(1) default '',
45-benefeciamento          pd_bene varchar(1) default '',
46-cupomfiscal             pd_cupf varchar(1)    default 'N',
47- CodidgoFiscal          pd_cfis varchar(30)   default '',
48- ValoresIBPT            pd_has1 varchar(256)  default '',                                                                           #Estou Utilizando p/Gravar os valors do IBPT
49- hash2                  pd_has2 varchar(256)  default '',                                                                           #Estou utilizando para gravar dados de previsao de entrega do produto vou dividor p/| para outras informacoes
50- hash3                  pd_has3 varchar(256)  default '',                                                                           
51- cancelado              pd_canc varchar(1)    default '',
52- idfilial               pd_idfi varchar(5)    default '',
53- CF Revenda             pd_cfir varchar(30)   default '',
54- Reserva Filial         pd_esrf decimal(15,4) not null default 0,
55- Marcacao Preco         pd_mark varchar(25)   default '',
56- UlTimaAltera1          pd_ula1 varchar(32)   default '',
57- UlTimaAltera2          pd_ula2 varchar(32)   default '',
58- DataInclusao           pd_funa varchar(32)   default '',
59- Fracionar QT           pd_frac varchar(1)    default '',
60- CPF-CNPJ FORN          pd_docf varchar(14)   default '',
61- Subgrupo 1             pd_sug1 varchar(20)   default '',
62- Subgrupo 2             pd_sug2 varchar(20)   default '',
63- 20 UltVendas           pd_ulvd text,
64- 20 UltCompras          pd_ulcm text,
65- 20 UltAcertos          pd_ulac text,
66-Similares               pd_simi text,
67-agregados               pd_agre text,
68-Marcacao-Valor          pd_marc varchar(1)    default "T",
69-Referencia FORN         pd_cfor varchar(30)   default "",
70-Acrescimo-Desconto AD   pd_acds varchar(1)    default "A",
71-REFERENCIA FORN         pd_fbar varchar(90)   default "",                                                                                     #FOI ALTERADO de 20-Para-30 em 08-05-2017 para 90
72-Produto c/DEF           pd_pdof varchar(1)    default "F",
73-Alteracoes MARG         pd_marp text,
74-%ST Compra              pd_stcm decimal(6,2) not null default 0,
75-QT Embalagem            pd_qtem varchar(10)   default '',
76-AltercaoPrecos          pd_altp text,
77-Transferencias          pd_ultr text,
78-Alterar Produto         pd_alte varchar(1)   default 'F',
79-Marcar Como KIT         pd_kitc varchar(1)   default 'F',
80-Codigo+QT               pd_codk text,
81-Codigo do KIT           pd_cokt varchar(14)  default '',
82-CodigoFisSec            pd_cfsc varchar(30)  default '',
83-Endreco Imagem          pd_imag text,
84-DT-AlteraInclui         pd_dtal date default '00-00-0000',
85-HR-AlteraInclus         pd_hcal time default '00:00:00',
86-AlteracaoInclus         pd_salt varchar(1)   default '',
87-Dados CABC Ult          pd_dabc text,
88-CodigoCEST              pd_cest varchar(7) default '',                                                                                         #Dados da curva ABC p/uso em compra
89-Prametros               pd_para text,
90-Precos p/Filial         pd_pcfl MEDIUMBLOB,
91-Filiais /nao vender     pd_nvdf MEDIUMBLOB,
92-Precos p/Filial         pd_endd varchar(10) default '',
93-Controle de nSerioe     pd_nser varchar(1) default '',
INDEX(pd_nome),
INDEX(pd_codi));

# CREATE INDEX idx_PROD_NOME ON produtos(pd_nome);
# CREATE INDEX idx_PROD_CODI ON produtos(pd_codi);
"""
84-Grava a data de alteracao do produto p/servir de paramentro de alteracao automatica entre os servidores remotos
85-Os mesmo q a data
86-Tipo de Alteracao A-Alteracao M-Produto Marcado
""" 

0 - ID-Lancamento  create table didavs (it_item varchar(3) default '',
0 - ID-Lancamento  create table idavs (it_item varchar(3) default '',

0 - ID-Lancamento  create table idavs (it_item varchar(3) default '',
1 - codigo filial  it_fili varchar(3)  default '',
2 - numero dav     it_ndav varchar(13) default '',
3 - numero comanda it_cmda varchar(13) default '',
4-codigocliente"C" it_cdcl varchar(14) default '',                                                      #-: Alterado para o novo codigo do cliente
5 - codigo produto it_codi varchar(14) default '', 
6 - codigo barras  it_barr varchar(14) default '',  
7 - nome produto   it_nome varchar(120) default '',  
8 - unidade prod   it_unid varchar(2)  default 'UN',   
9 - frabricante    it_fabr varchar(20) default '',  
10- endereco       it_ende varchar(10) default '',  
11- preco          it_prec decimal(15,3) default 0,
12- quantdade"ALT" it_quan decimal(15,4) default 0,
13- sub-total      it_subt decimal(15,2) default 0,
14- Vluntario"ALT" it_vlun decimal(15,4) default 0,                                                       #-: Verificar se tem 4 casas decimais
15- comprimento CL it_clcm decimal(6,3)  default 0,
16- largura        it_clla decimal(6,3)  default 0,
17- expessura      it_clex decimal(6,3)  default 0,
18- metros"ALT"    it_clmt decimal(15,4) default 0,
19- Comprimento CT it_ctcm decimal(6,3)  default 0,
20- largura        it_ctla decimal(6,3)  default 0,
21- expessura      it_ctex decimal(6,3)  default 0,
22- metros"ALT"    it_ctmt decimal(15,4) default 0,
23- vlr unit peca  it_unpc decimal(15,3) default 0,
24- controle UN ML it_mdct varchar(1)    default '1',
25- cortes         it_obsc text,
26- frete          it_vfre decimal(15,2) default 0,
27- acrescimo      it_vacr decimal(15,2) default 0,
28- desconto       it_vdes decimal(15,2) default 0,
29- % imcs         it_pcim decimal(6,2)  default 0,
30- % reducao icms it_pric decimal(6,2)  default 0,
31- % ipi          it_pipi decimal(6,2)  default 0,
32- % ST           it_psub decimal(6,2)  default 0,
33- % ISS          it_piss decimal(6,2)  default 0,
34- BC ICMS        it_bcim decimal(15,2) default 0,
35- BC RED.ICMS    it_bric decimal(15,2) default 0,
36- BC IPI         it_bipi decimal(15,2) default 0,
37- BC ST          it_bsub decimal(15,2) default 0,
38- BC ISS         it_biss decimal(15,2) default 0,
39- VLR ICMS       it_vcim decimal(15,2) default 0,
40- VLR RED ICMS   it_vric decimal(15,2) default 0,
41- VLR IPI        it_vipi decimal(15,2) default 0,
42- VLR ST         it_vsub decimal(15,2) default 0,
43- VLR ISS        it_viss decimal(15,2) default 0,
44- IAT Tributado  it_tiat varchar(1)    default '',
45- codigo venda   it_vdcd varchar(4)    default '',
46- nome venda     it_nmvd varchar(12)   default '',
47- nome cancela   it_usac varchar(12)   default '',
48- ID->Loja       it_inde varchar(5)    default '',
49- ID->Filial     it_idfo varchar(5)    default '',
50 -Pis %          it_pper decimal(6,2)  default 0,
51 -Confins %      it_cper decimal(6,2)  default 0,
52 -Pis Base       it_pbas decimal(15,2) default 0,
53 -Confins Base   it_cbas decimal(15,2) default 0,
54 -Pis Valor      it_pval decimal(15,2) default 0,
55 -Confins Valor  it_cval decimal(15,2) default 0,
56 -CD NCM         it_ncmc varchar(8)    default '',
57 -CD CFOP        it_cfop varchar(4)    default '',
58 -CD CST         it_cstc varchar(4)    default '',
59 -Codigo Fiscal  it_cdfi varchar(30)   default '',
60 -IBPT p         it_pibp decimal(5,2)  default 0,
61 -IBPT v         it_vibp decimal(10,2) default 0,
62 - Entregar DHU  it_entr varchar(40)   default '',
63 Entregado  DHU  it_rece varchar(40)	 default '',
64 QTEntregue"ALT" it_qent decimal(15,4) default 0,
65 ID-LancaDevoluc it_iddv varchar(3)    default '',
66 QTDevolvda"ALT" it_qtdv decimal(14,4) default 0,
67-DT Lancamento   it_lanc date default '00-00-0000',
68-HR Lancamento   it_horl time default '00:00:00',
69-QT Anterior     it_qtan decimal(15,4) default 0,
70-ImpExpedicao    it_expe varchar(100)  default '',
71-grupo           it_grup varchar(20)   default '',
72-sub-grupo 1     it_sbg1 varchar(20)   default '',
73-sub-grupo 2     it_sbg2 varchar(20)   default '',
74-EST FISICO"ALT" it_estf decimal(15,4) not null default 0,
75-Tabela          it_tabe varchar(1)    default '',
76-Retiradas       it_reti text,
77-Preco do Custo  it_cprc decimal(15,4) default 0,
78-TotalItem Custo it_ctot decimal(15,2) default 0,
79-DT Cancelamento it_dcan date default '00-00-0000',
80-HR Cancelamento it_hcan time default '00:00:00',
81-FscoAnTCan"ALT" it_aesf decimal(15,4) not null default 0,
82-Cancelad [1]    it_canc varchar(1)    default '',
83-DadosDEV id,dv  it_dado varchar(100)  default'',
84-Nome do Cliente it_clie varchar(120)  default '',
85-Emissao de DOF  it_pdof varchar(1)    default "F",
86-Enterega Futura it_futu varchar(1)    default "F",
87-Tipo de Pedido  it_tped varchar(1)    default "",
88-CD-Referencia   it_refe varchar(30)   default '',
89-Preco Manual    it_manu decimal(15,3) default 0,
90-Autorizacao R-L it_auto text,
91-Codigo KIT      it_ckit varchar(200)  default '',
92-QTKiVedido"ALT" it_qkiv decimal(15,4) default 0,
93-QTKtDvlvdo"ALT" it_qtid decimal(15,4) default 0,
94-Dados IBPT      it_dibp MEDIUMBLOB,																				 #-:Informacoes do calculo de IBPT
95-OutrasInformaca it_ouin MEDIUMBLOB,
96 QTDevolvda-UNID it_qdvu decimal(14,4) default 0,
97 InformaPartilha it_part MEDIUMBLOB,
98 NumeroSerie     it_seri MEDIUMBLOB,
99  Embalagens     it_emba varchar(100) default '',
100 Comissao       it_comi decimal(6,2) default 0,
101 Estoqeu local  it_eloc decimal(15,4) not null default 0,
INDEX (it_ndav),
INDEX (it_lanc),
INDEX (it_dcan));

# CREATE INDEX idx_IDAVS_DAVS ON didavs(it_ndav);
# CREATE INDEX idx_IDAVS_DATA ON didavs(it_lanc);
# CREATE INDEX idx_IDAVS_DCAN ON didavs(it_dcan);

#DHU - Data Hora e Usuario
0-ID          	    create table dcdavs (cr_regi int(14) not null auto_increment primary key,
0-ID          	    create table cdavs (cr_regi int(14) not null auto_increment primary key,
                    
0-ID          	    create table cdavs (cr_regi int(14) not null auto_increment primary key,
1-Filial      	    cr_fili varchar(3)  default '',
2-NoDav       	    cr_ndav varchar(13) default '',
3-CDCliente   "C"   cr_cdcl varchar(14) default '',
4-NomeCliente	    cr_nmcl varchar(50) default '',
5-Fantasia		    cr_facl varchar(20) default '',
6-CCO       	    cr_cupo varchar(6)  default '',
7-ECF-Cancelado	    cr_ccan varchar(6)  default '',
8-NotaFiscal	    cr_nota varchar(9)  default '',
9-Usuario DAV	    cr_udav varchar(20) default '',
10-Caixa		    cr_urec varchar(20) default '',
11-Emissao DAV	    cr_edav date default '00-00-0000',
12-Hora DAV		    cr_hdav time default '00:00:00',
13-Caixa DATA	    cr_erec date default '00-00-0000',
14-Caixa HORA	    cr_hrec time default '00:00:00',
15-NFE Emi		    cr_nfem varchar(60)   default '',
16-NFE CAN		    cr_nfca varchar(60)   default '',
17-ECF Emi		    cr_ecem varchar(60)   default '',
18-ECF CAN		    cr_ecca varchar(60)   default '',
19-DataCancela	    cr_ecan date default '00-00-0000',
20-HoraCancela	    cr_hcan time default '00:00:00',
21-DataEntrega	    cr_entr date default '00-00-0000',
22-HoraEntrega	    cr_hent time default '00:00:00',
23-VlFrete		    cr_vfre decimal(15,2)  default 0,
24-VlAcrescimo	    cr_vacr decimal(15,2)  default 0,
25-VlDesconto	    cr_vdes decimal(15,2)  default 0,
26-VlIcms		    cr_vcim decimal(15,2)  default 0,
27-VlRed-ICMS	    cr_vric decimal(15,2)  default 0,
28-VlIPI		    cr_vipi decimal(15,2)  default 0,
29-VlSubTrib	    cr_vsub decimal(15,2)  default 0,
30-VlISS		    cr_viss decimal(15,2)  default 0,
31-BaseCICMS	    cr_bcim decimal(15,2)  default 0,
32-BaseRedICMS	    cr_bric decimal(15,2)  default 0,
33-BaseIPI		    cr_bipi decimal(15,2)  default 0,
34-BaseSubTrib	    cr_bsub decimal(15,2)  default 0,
35-Base ISS		    cr_biss decimal(15,2)  default 0,
36-TotalProduto	    cr_tpro decimal(15,2) default 0,
37-TotalDAV		    cr_tnot decimal(15,2) default 0,
38-Referencia	    cr_refe text,
39-CPF-CNPJ		    cr_docu varchar(14)   default '',
40-FormaPGTO	    cr_paga varchar(30)   default '',
41-Tipo			    cr_tipo varchar(1)    default '',
42-RecLocal NU      cr_rloc varchar(1)    default '',
43-CodigoVenda	    cr_vdcd varchar(4)    default '',
44-NomeVenda	    cr_nmvd varchar(12)   default '',
45-UsaCancela	    cr_usac varchar(12)   default '',
46-CodigoCaixa	    cr_cxcd varchar(4)    default '',
47-Recebimento	    cr_rece varchar(30)   default '',
48-VlRecebido	    cr_vlrc decimal(15,2)  default 0,
49-VlTroco          cr_vltr decimal(15,2)  default 0,
50-ContaCor CRD     cr_ccre decimal(15,2)  default 0,
51-ContaCor DEB     cr_cdeb decimal(15,2)  default 0,
52-Filial Caixa     cr_ficx varchar(3)    default '',
53-Rateio Troco     cr_tror decimal(15,2)  default 0,
54-ID Filial DAV    cr_inde varchar(5)    default '',
55-ID Filial CLI    cr_idfc varchar(5)    default '',
56-Dinheiro	        cr_dinh decimal(15,2)  default 0,
57-Ch.Avista        cr_chav decimal(15,2)  default 0,
58-Ch.Predatado     cr_chpr decimal(15,2)  default 0,
59-CT Credito       cr_ctcr decimal(15,2)  default 0,
60-CT Debito        cr_ctde decimal(15,2)  default 0,
61-FAT Boleto       cr_fatb decimal(15,2)  default 0,
62-FAT Carteira     cr_fatc decimal(15,2)  default 0,
63-Finaceira        cr_fina decimal(15,2)  default 0,
64-Tickete          cr_tike decimal(15,2)  default 0,
65-PGTO Credito     cr_pgcr decimal(15,2)  default 0,
66-DEP. Conta       cr_depc decimal(15,2)  default 0,
67-CCF              cr_ccfe varchar(6)    default '',
68-PIS Base C       cr_pibc decimal(15,2)  default 0,
69-CONFINS Base     cr_cobc decimal(15,2)  default 0,
70-PIS Valor        cr_pivl decimal(15,2)  default 0,
71-CONFIS Valor     cr_covl decimal(15,2)  default 0,
72-pv IBPT          cr_ibpt varchar(30)   default '',
73-Cahve NFE        cr_chnf varchar(44)   default '',
74-RecEstCan 123    cr_reca varchar(1)    default '',
75-Cadastrado CL    cr_cadc varchar(1)    default '',
76-Endereco 1-2 "P" cr_ende varchar(4)    default '',
77-Motivo           cr_moti text,
78-Devolucao        cr_cdev varchar(13)   default '',
79-MoT-Devolucao    cr_dmot varchar(30)   default '',
80-MotivoCAncelamen cr_auto varchar(20)   default '',
81-Relacao AUT   NU cr_rela varchar(100)  default '',
82-Historico AUT    cr_hist text,
83-Receber Local    cr_loca varchar(30)   default '',
84-Vlr Rc.Local     cr_rcbl decimal(15,2) default 0,
85-Impressão        cr_impr text,
86-Dados Entrega    cr_dade text,
87-Bairro           cr_ebai varchar(20) default '',
88-Cidade           cr_ecid varchar(20) default '',
89-CEP              cr_ecep varchar(9)  default '',
90-Num-Romaneio     cr_roma varchar(10) default '',
91-RomaneioDADOS    cr_dado text,
92-Nº Fab.ECF       cr_ecfb varchar(20) default '',
93-Total Custo      cr_cust decimal(15,2) default 0,
94-Custo Vazio      cr_vazc varchar(1)  default 'F',
95-Pre-Recebimento  cr_prer MEDIUMBLOB,
96-Sequencial ECF   cr_ecfs varchar(3)  default '',
97-GuardaFPagamento cr_guap MEDIUMBLOB,
98-NFe Outros       cr_tfat varchar(1)    default '',
99-NFeVinculadoNFCh cr_nfev varchar(100)  default '',
100-Contigencia "D" cr_cont varchar(100)  default '',
101-Nº Serie NF     cr_seri varchar(3)    default '',
102-Comprador-Nome  cr_comp varchar(120)  default '',
103-Comprador-Codig cr_comg varchar(8)    default '',
104-1-NFe, 2-NFCe   cr_tnfs varchar(1)    default '',
105-AutorizaDevoluc cr_audv varchar(40)   default '',
106-CSTAT - NFs     cr_csta varchar(3)    default '',
107-PGTO vlrParcela cr_vpar MEDIUMBLOB,
108-NoDevolucao     cr_cavu varchar(13) default '',
109-Dados IBPT      cr_dibp MEDIUMBLOB,
110-InfoPartilhaICM cr_part MEDIUMBLOB,
111-InfoPagMistura  cr_mist MEDIUMBLOB,
112-Dav-Vinc-Em_NFe cr_vnfe varchar(13) default '',
113-Dav-Vinc-%Reduc cr_vnpr decimal(6,2) default 0,
114-StatusExpedicao cr_stat varchar(40) default '',
115-RelacaoExpedica cr_expe MEDIUMBLOB,
116-SeparandoExped  cr_exse MEDIUMBLOB,
INDEX(cr_edav),
INDEX(cr_ndav));

# CREATE INDEX idx_CDAVS_DATA ON dcdavs(cr_edav);
# CREATE INDEX idx_CDAVS_NDAV ON dcdavs(cr_ndav);
# CREATE INDEX idx_CDAVS_DREC ON dcdavs(cr_erec);
# CREATE INDEX idx_CDAVS_DCAN ON dcdavs(cr_ecan);
# CREATE INDEX idx_CDAVS_NENT ON dcdavs(cr_entr);

""" 
	100-Contigencia 1-Online 2-Offinel 3-Time out | Tipo de Nota 1-NFe 2-NFCe | Homogacao1,Homogacao2,Producao 1,2,3 
	98-1-Simples Faturamento 2-Entrega Futura de Simples Faturamento
	114-{ 1-Separando material, 2-Enviando para expedicao 3-Entregue ao cliente | data-hora | usuario q entregou }

"""

# 86 BAIRRO,CEP
# select cr_ndav,cr_nota,cr_ptnf,cr_chnf from cdavs;

#---------------------[ Cadastro de Clientes ]
00- registro         create table clientes (cl_regist int(8) not null auto_increment primary key,
01- nome             cl_nomecl varchar(50) default '',
02- fantasia         cl_fantas varchar(20) default '',
03- documento        cl_docume varchar(14) default '',
04- ie               cl_iestad varchar(15) default '',
05- fisicajuridica   cl_pessoa varchar(01) default '',
06-Aniv.Fundacao     cl_fundac date,
07- datacadastro     cl_cadast date,
08- endereco         cl_endere varchar(45)  default '',
09- bairro           cl_bairro varchar(20)  default '',
10- cidade           cl_cidade varchar(20)  default '',
11- ibge             cl_cdibge varchar(7)   default '',
12- cep1             cl_cepcli varchar(9)   default '',
13- complemento1     cl_compl1 varchar(5)   default '',
14- complemento2     cl_compl2 varchar(20)  default '',
15- uf               cl_estado varchar(02)  default '',
16- email            cl_emailc varchar(200) default '',                                                               #22-10-2016
17- telefone1        cl_telef1 varchar(13)  default '',
18- telefone2        cl_telef2 varchar(13)  default '',
19- telefine3        cl_telef3 varchar(13)  default '',
20- endentrega       cl_eender varchar(45)  default '',
21- bairroentrega    cl_ebairr varchar(20)  default '',
22- cidadeentrega    cl_ecidad varchar(20)  default '',
23- igbe             cl_ecdibg varchar(7)   default '',
24- cep              cl_ecepcl varchar(9)   default '',
25- complemento1     cl_ecomp1 varchar(5)   default '',
26- complemtneo2     cl_ecomp2 varchar(20)  default '',
27- uf               cl_eestad varchar(02)  default '',
28- idfilial         cl_indefi varchar(5)   default '',
29- im               cl_imunic varchar(15)  default '',
30- Revenda          cl_revend varchar(30)  default '',
31- Seguimento       cl_seguim varchar(30)  default '',
32- P.Referencia     cl_refere text,
33- Redes Sociais    cl_redeso text,
34- Emails           cl_emails text,
35- EmailNfeEnvio    cl_pgfutu varchar(1)  default '',
36- LimiteCredito    cl_limite decimal(15,2) default 0,
37- Ref.Comercial    cl_refeco text,
38- Codigo CL SIM    cl_cdsimm varchar(15)   default '',
39- Parceiro         cl_clmarc varchar(70)   default '',
40- RegisParceiro    cl_rgparc varchar(8)    default '',
41-DATA UltimaCMP    cl_dtcomp date          default '00-00-0000',
42-Dado UltimaCMP    cl_dadosc varchar(200)  default '',
43-PgTo Futuros      cl_pgtofu text,
44-BlqueioCredito    cl_blcred text,
45-RelCompradores    cl_compra text,
46-CodigoCliente     cl_codigo varchar(14)   default '',
47-DT-AlteraInclui   cl_dtincl date default '00-00-0000',
48-HR-AlteraInclus   cl_hrincl time default '00:00:00',
49-AlteraIncluDelete cl_incalt varchar(1)   default '',
50-Pramametros       cl_parame MEDIUMBLOB,
51-ClientesEntregas  cl_endent MEDIUMBLOB,
52-VendedorVinculado cl_vended varchar(100) default '',
53-Nome da Rede      cl_nmrede varchar(40)  default '',                             #-:31-01-2017
54-Alteracoes        cl_altera MEDIUMBLOB);


00-ID Lancamento     create table receber (rc_regist int(8) not null auto_increment primary key,                                  """ 46-Novo Codigo do cliente Composto Numero do Registro + FInclusao  """    
01-Numero documento  rc_ndocum varchar(13)  default '',
02-Origem V-R-A-P    rc_origem varchar(1)   default '',
03-No Parcela        rc_nparce varchar(2)   default '',
04-Valor Original    rc_vlorin decimal(15,2) default 0,
05-Valor Lancamento  rc_apagar decimal(15,2) default 0,
06-Forma Pagamento   rc_formap varchar(30)  default '',
07-DT Lancamento     rc_dtlanc date         default '00-00-0000',
08-Hora Lacamento    rc_hslanc time         default '00:00:00',
09-LancCodigo Caixa  rc_cdcaix varchar(4)   default '',
10-LancLogin  Caixa  rc_loginc varchar(12)  default '',
11-CodigoCliente"C"  rc_clcodi varchar(14)  default '',                                                                            #-:Alterado para suportar o novo codigo do cliente
12-Nome   Cliente    rc_clnome varchar(50)  default '',                                                                            
13-Fantasia Cliente  rc_clfant varchar(20)  default '',
14-CPF-CNPJ Cliente  rc_cpfcnp varchar(14)  default '',
15-FilialIdenClient  rc_clfili varchar(3)   default '',
16-BaixaCodigoCaixa  rc_bxcaix varchar(4)   default '',
17-BaixaLogin Caixa  rc_bxlogi varchar(12)  default '',
18-Valor Baixado     rc_vlbaix decimal(15,2) default 0,
19-DATA  Baixa       rc_dtbaix date         default '00-00-0000',
20-HORA  Baixa       rc_hsbaix time         default '00:00:00',
21-Forma Recebimnto  rc_formar varchar(40)  default '',
22-Trans Central     rc_transp varchar(55)  default '',
23-Trans DT HS       rc_trandh varchar(20)  default '',
24-IndnfcacaoFilial  rc_indefi varchar(5)   default '',
25-ID-Fil Cliente    rc_idfcli varchar(5)   default '',
26-Vencimento        rc_vencim date         default '00-00-0000',
27-Bandeira          rc_bandei varchar(40)  default '',
28-Ch Documento      rc_chdocu varchar(14)  default '',
29-Correntista       rc_chcorr varchar(100) default '',
30-NoBanco           rc_chbanc varchar(3)   default '',
31-Agencia           rc_chagen varchar(4)   default '',
32-ContaCorrente     rc_chcont varchar(20)  default '',
33-NoCheque          rc_chnume varchar(10)  default '',
34-Dados Cheque      rc_chdado text,
35-Status Comanda    rc_status varchar(1)   default '',
36-Cancela Estorno   rc_canest text,
37-1-AReceber 2-CX   rc_recebi varchar(1)   default '',
38-Bandeira Baixa    rc_banbax varchar(40)  default '',
39-Forma de Recmnto  rc_forbax varchar(30)  default '',
40-cl cadastrado SN  rc_clcada varchar(1)   default '',
41-Troco             rc_trocos decimal(15,2) default 0,
42-TansFerir CC      rc_contac decimal(15,2) default 0,
43-Sobra Rcbmento    rc_sobrar decimal(15,2) default 0,
44-DATA Cancela      rc_dtcanc date         default '00-00-0000',
45-HORA Cancela      rc_hrcanc time         default '00:00:00',
46-Cancela CodigoUS  rc_cancod varchar(4)   default '',
47-CAncela Login US  rc_canlog varchar(12)  default '',
48-Troco             rc_destro decimal(15,2) default 0,
49-TansFerir CC      rc_descon decimal(15,2) default 0,
50-Sobra Rcbmento    rc_dessob decimal(15,2) default 0,
51-DesmenbraVinculo  rc_desvin varchar(13)  default '',
52-RelacaoTitulosBX  rc_relaca text,
53-BX Liqui/Desmenb  rc_baixat varchar(1)   default '',
54-Estornado {1}     rc_estorn varchar(1)   default '',
55-modulo-processo   rc_modulo varchar(10)  default '',
56-Vendedor          rc_vended varchar(12)  default '',
57-CHQ Campo COMP    rc_chcomp varchar(3)   default '',
58-CARTAO Autoriza   rc_autori varchar(20)  default '',
59-Nota Fiscal       rc_notafi varchar(9)   default '',
60-Numero COO        rc_numcoo varchar(6)   default '',
61-Acrescimo         rc_acresc decimal(15,2) default 0,
62-Desconto          rc_dscnto decimal(15,2) default 0,
63-Observ Estorno    rc_obsest text,
64-Rel Comprovantes  rc_compro text,
65-Codigo Vendedor   rc_cdvend varchar(4)  default '',
66-HistoricoAltera   rc_histor text,
67-Numero do Boleto  rc_boleto varchar(17) default '',
68-Codigo de Barras  rc_bolbar varchar(47) default '',
69-Numero Bordero    rc_border varchar(10) default '',
70-Data Bordero      rc_databo date        default '00-00-0000',
71-Hora Bordero      rc_horabo time        default '00:00:00',
72-Usario Bordero    rc_loginu varchar(12) default '',
73-Us-Codigo Border  rc_uscodi varchar(4)  default '',
74-BancoFornece      rc_instit varchar(60) default '',
75-BancoFor REGIS    rc_rginst varchar(8)  default '',
76-CPF-CNPJ Instit   rc_docins varchar(14) default '',
77-Borde Relacao TT  rc_borrtt text,
78-Tipo 1DP 2DS 3PG  rc_tipods varchar(1)   default '',
79-BoletoNosoNumero  rc_nosson varchar(20)  default '',
80-PG-TrcerosApagar  rc_pgterc varchar(1)   default '',
81-Bco Boletos       rc_bcobol varchar(100) default'',
82-Data Boleto       rc_dtbole date         default '00-00-0000',
83-Hora Boleto       rc_hobole time         default '00:00:00',
84-FinaRemotoMarcar  rc_fimtra varchar(50)  default '',
85-EnvioRemotoServe  rc_envfil varchar(50)  default '',
86-Rel TT Apagar     rc_relapa text,
87-Dados boleto WEB  rc_blweob MEDIUMBLOB,
INDEX eceber(rc_dtlanc),
INDEX eceber(rc_dtbaix),
INDEX eceber(rc_vencim),
INDEX eceber(rc_status));

#CREATE INDEX idx_REC_DTLA ON receber(rc_dtlanc);
#CREATE INDEX idx_REC_DTBX ON receber(rc_dtbaix);
#CREATE INDEX idx_REC_DTVC ON receber(rc_vencim);

#84/85 [ T/F|FilialOrigem|FilialDestino|Data|Hora|Usuario ] { Financeiro Remoto Contigencia }


""" Campo 35-status

	Vazio - Aberto
		1 - Baixado
		2 - Liquidacao
		3 - Estornado
		4 - Cancelado para desmenbramento
		5 - Cancelado

	Campo 54 1-Aberto por estorno
	
	53 1-Baixa 2-Liquidacao 3-Desmenbramento

	78 1-Deposito 2-Desconto 3-Pagamentos 4-Contas liquidas pelo contas apagar

	86 Relacao de titulos do contas apagar, utilizando as contas do areceber para abater no contas apagar
	02-origem V-venda,  R-receber A-, P-contas apagar
	
"""

#-->[ Conta Corrente ]
00-ID Lancamento    create table conta (cc_regist int(8) not null auto_increment primary key,
01-DT Lancamento    cc_lancam date         default '00-00-0000',
02-HR Lancamento    cc_horala time         default '00:00:00',
03-CD-Usuario       cc_usuari varchar(4)   default '',
04-NM-Usuario       cc_usnome varchar(12)  default '',
05-CD-Filial        cc_cdfili varchar(3)   default '',
06-ID-Filial Lanc   cc_idfila varchar(5)   default '',
07-N.Dav Lancamento cc_davlan varchar(13)  default '',
08-CD-Clietne "C"   cc_cdclie varchar(14)  default '',                                             #-:Alterado para suportar o novo numero do cliente
09-NM-Cliente       cc_nmclie varchar(50)  default '',
10-CPF CNPJ Cliente cc_docume varchar(14)  default '',
11-ID Filia Cliente cc_idfcli varchar(5)   default '',
12-Origm Lancamento cc_origem varchar(2)   default '',
13-Historiocp       cc_histor varchar(50)  default '',
14-Credito          cc_credit decimal(15,2) default 0,
15-Debito           cc_debito decimal(15,2) default 0,
16-Saldo            cc_saldos decimal(15,2) default 0,
17-Fantasia         cc_fantas varchar(20)  default '');


#Cadastro de ocorrencias
00-registor		create table ocorren (oc_regi int(8) not null auto_increment primary key,
01-documento	oc_docu varchar(20) default '',
02-lac-usa		oc_usar varchar(60) default '',
03-ocorrencia	oc_corr text,
04-tipo		    oc_tipo varchar(20) default '',
05-ID-Filial	oc_inde varchar(5)  default '');


00-Registro	         create table tdavs (tm_regi int(14) not null auto_increment primary key,
01-Numero Item		 tm_item varchar(3)    default '',
02-ComandaControle   tm_cont varchar(14)   default '',
03-codigo produto    tm_codi varchar(14)   default '', 
04-nome produto      tm_nome varchar(120)   default '',  
05-quantidade  "ALT" tm_quan decimal(15,4) default 0,
06-unidade prod      tm_unid varchar(2)    default 'UN',   
07-preco             tm_prec decimal(15,3) default 0,
08-Valor unitario    tm_vlun decimal(15,4) default 0,
09-comprimento CL    tm_clcm decimal(6,3)  default 0,
10-largura           tm_clla decimal(6,3)  default 0,
11-expessura         tm_clex decimal(6,3)  default 0,
12-metros      "ALT" tm_clmt decimal(15,4) default 0,
13-Comprimento CT    tm_ctcm decimal(6,3)  default 0,
14-largura           tm_ctla decimal(6,3)  default 0,
15-expessura         tm_ctex decimal(6,3)  default 0,
16-metros      "ALT" tm_ctmt decimal(15,4) default 0,
17-sub-total         tm_subt decimal(15,2) default 0,
18-vlr unit peca     tm_unpc decimal(15,3) default 0,
19-controle UN ML    tm_mdct varchar(1)    default '1',
20-cortes            tm_obsc text,
21-IAT Tributado     tm_tiat varchar(1)    default '',
22-IBPT p            tm_pibp decimal(5,2)  default 0,
23-frabricante       tm_fabr varchar(20)   default '',
24-endereco          tm_ende varchar(10)   default '',  
25-codigo barras     tm_barr varchar(14)   default '',  
26-Codigo Fiscal     tm_cdfi varchar(30)   default '',
27-login usuario	 tm_logi varchar(20)   default '',
28-DT Lancamento     tm_lanc date          default '00-00-0000',
29-HR Lancamento     tm_hora time          default '00:00:00',
30-D,O DAV-ORCAMENTO tm_tipo varchar(1)    default '',
31-Codigo Cliente"C" tm_clie varchar(14)   default '',                                                         #-:Alterado para suportar o novo codigo do cliente
32-Tabela de Preco   tm_tabe varchar(1)    default '',
33-preco de custo    tm_cprc decimal(15,4) default 0,
34-custor sub-total  tm_cust decimal(15,2) default 0,
35-DadosDevolucao    tm_dado varchar(100)  default'',
36-Filial            tm_fili varchar(5)    default'',
37-ID-Produto        tm_idpd varchar(8)    default'',
38-Valor Manual      tm_manu decimal(15,3) default 0,
39-Autorizacao R-L   tm_auto text,
40-Kit-CodigoProduTo tm_kitc varchar(220)  default'',
41-QTKitVendido"ALT" tm_qkiv decimal(15,4) default 0,
42-CD Identificacao  tm_ouin MEDIUMBLOB);


""" 30 D-DAV,O-ORÇAMENTO V-DEVOLUCAO, F-SIMPLES FATURAMENTO """
#---------------------------[ Compras ]

""" Fornecedor """
00-registor		     create table fornecedor (fr_regist int(8) not null auto_increment primary key,
01-cnpj-cpf          fr_docume varchar(14) default '',
02-IE                fr_insces varchar(14) default '',
03-IM                fr_inscmu varchar(15) default '',
04-CNAE              fr_incnae varchar(7)  default '',
05-CRT               fr_inscrt varchar(1)  default '',
06-nome forncedor    fr_nomefo varchar(120) default '',
07-Fantasia          fr_fantas varchar(60) default '',
08-Endereco          fr_endere varchar(60) default '',
09-numero            fr_numero varchar(60) default '',
10-complemento       fr_comple varchar(60) default '',
11-bairro            fr_bairro varchar(60) default '',
12-cidade            fr_cidade varchar(60) default '',
13-cep               fr_cepfor varchar(8)  default '',
14-Estado            fr_estado varchar(2)  default '',
15-codigo Municipio  fr_cmunuc varchar(7)  default '',
16-Telefone1         fr_telef1 varchar(20) default '',                                      
17-Telefone2         fr_telef2 varchar(20) default '',                                      
18-Telefone3         fr_telef3 varchar(20) default '',                                      
19-Site              fr_fosite varchar(60) default '',
20-emails            fr_emails text,
21-contatos          fr_contas text,
22-DT Cadastramento  fr_dtcada date default '00-00-0000',
23-ID-Filial Lanc    fr_idfila varchar(5)   default '',
24-Tipo Fornecedor   fr_tipofi varchar(1)   default '1',
25-Numero do Banco   fr_bancof varchar(3)   default '',
26-Numero da Agencia fr_agenci varchar(6)   default '',
27-Conta Corrente    fr_contac varchar(11)  default '',
28-Boleto Convenio   fr_conven varchar(10)  default '',
29-Boleto Especie    fr_especi varchar(5)   default '',
30-Boleto Carteira   fr_cartei varchar(5)   default '',
31-Imprimi Boleto    fr_boleto varchar(1)   default 'F',
32-Instrucao Boleto  fr_insbol text,
33-Plano de Contas   fr_planoc varchar(20)  default '',
34-NomeRepresentante fr_repres varchar(120) default '',
35-Placa             fr_vplaca varchar(10)   default '',
36-Tipo Veiculo      fr_vtipov varchar(60)   default '',
37-Nome do Motorista fr_motori varchar(60)   default '',
38-Unidade manejo    fr_manejo MEDIUMBLOB,
39-Unidade padrao    fr_unpadr varchar(100) default '',
40-CargaPesoCaminhao fr_cargac decimal(15,3) default 0,
41-comprimentoCarroc fr_compri decimal(15,3) default 0,
42-Parametros        fr_parame MEDIUMBLOB);


""" Controle de Compras """
00-registor		          create table ccmp (cc_regist int(10) not null auto_increment primary key,
01-cnpj-cpf               cc_docume varchar(14) default '',
02-nome forncedor         cc_nomefo varchar(120) default '',
03-Fantasia               cc_fantas varchar(60) default '',
04-CRT                    cc_crtfor varchar(1)  default '',
05-Chave da NFE           cc_ndanfe varchar(44) default '',
06-Numero NFE             cc_numenf varchar(9)  default '',
07-DT Lancamento          cc_dtlanc date default '00-00-0000',
08-HR Lancamento          cc_hrlanc time default '00:00:00',
09-US Lancamento          cc_uslanc varchar(12)   default '',
10-NFe DT Emissao         cc_nfemis date default '00-00-0000',
11-NFe DT Saida           cc_nfdsai date default '00-00-0000',
12-NFe Hora EntraSai      cc_nfhesa time default '00:00:00',
13-Total Produtos         cc_tprodu decimal(15,2) default 0,
14-BASE  ICMS             cc_baicms decimal(15,2) default 0,
15-Valor ICMS             cc_vlicms decimal(15,2) default 0,
16-BASE  ST               cc_basest decimal(15,2) default 0,
17-Valor ST               cc_valost decimal(15,2) default 0,
18-Valor Frete            cc_vfrete decimal(15,2) default 0,
19-Valor Seguro           cc_vsegur decimal(15,2) default 0,
20-Valor Desconto         cc_vdesco decimal(15,2) default 0,
21-Valor II               cc_valoii decimal(15,2) default 0,
22-Valor IPI              cc_valipi decimal(15,2) default 0,
23-Valor PIS              cc_valpis decimal(15,2) default 0,
24-Valor COFINS           cc_vconfi decimal(15,2) default 0,
25-Outras Despesas        cc_vodesp decimal(15,2) default 0,
26-Valor Total NF         cc_vlrnfe decimal(15,2) default 0,
27-Tipo 1,2,3,4,5,6,7,8   cc_tipoes varchar(1)    default '',
28-Codigo Filial          cc_filial varchar(5)    default '',
29-Duplicatas             cc_duplic text,
30-Nº Controle            cc_contro varchar(10)   default '',
31-NºItems Pedido         cc_itemsp varchar(4)    default '',
32-Nº de Serie            cc_nserie varchar(3)    default '',
33-ST Antecipado VT       cc_stantv decimal(15,2) default 0,
34-FR Antecipado VT       cc_frantv decimal(15,2) default 0,
35-DS Antecipado VT       cc_dsantv decimal(15,2) default 0,
36-Emaisl Enviados        cc_emaile text,
37-N.Protocolo            cc_protoc varchar(60)   default '',
38-Seguro por fora        cc_fsegur decimal(15,2) default 0,
39-Desp.Acces fora        cc_fdesac decimal(15,2) default 0,
40-Total NF Fora          cc_tnffor decimal(15,2) default 0,
41-MotvoCancelamento      cc_cancel text,
42-DT Cancelamento        cc_dtcanc date default '00-00-0000',
43-HR Cancelamento        cc_hrcanc time default '00:00:00',
44-US Cancelamento        cc_uscanc varchar(12)   default '',
45-CD-US Canclamento      cc_uccanc varchar(4)    default '',
46-Cancelado {1}          cc_status varchar(1)    default '',
47-Icms Frete Fora        cc_icmfre decimal(15,2) default 0,
48-Transf Fl Orgime       cc_forige varchar(5)    default '',
49-Transf Fl Destino      cc_fdesti varchar(5)    default '',
50-FinalTransferenciaPED  cc_fimtra varchar(40)   default '',
51-DaTa de Envio a Filial cc_envfil varchar(40)   default '',
52-Nº Controle Origem     cc_corige varchar(10)   default '',
53-Nº ControleDestino     cc_cdesti varchar(10)   default '',
54-Motivo do ACerto       cc_acerto varchar(100)  default '',
55-IPI Avulso VlrTotal    cc_ipiavu decimal(15,2) default 0,
56-ST  Avulso VlrTotal    cc_stavul decimal(15,2) default 0,
57-IPI -BASE Calculo      cc_basipi decimal(15,2) default 0,
58-DadosNFe RMA           cc_infnfe text,
59-Retirado Filial Remota cc_fremot varchar(5) default '',
60-Valor total extracao   cc_manejo decimal(15,2) default 0,
61-unidade manejo roca    cc_unmane varchar(100) default '',
62-manejoRrocaExtrator_id cc_unmaid varchar(8) default '',
63-manejo nome            cc_unnome varchar(100) default '',
64-manejo fantasia        cc_unfant varchar(60) default '',                                                               # 4-07-2017
65-unidade manejo roca    cc_undocu varchar(14) default '',
66-ID-Fornecedor          cc_idforn varchar(8)  default '',
67-Gerado apagar T,F      cc_apagar varchar(1)  default '') ;


""" Campo 27
	1-Pedido de Compra
	2-Acerto de Estoque
	3-Devolucao de RMA
	4-Transferencia
	5-Orçamento
	8-Transferir para o estoque local
"""

""" Items de Compras """

00-ID Registro       create table iccmp (cc_regist int(10) not null auto_increment primary key,
01-Nº Controle       ic_contro varchar(10)   default '',
02-cnpj-cpf          ic_docume varchar(14)   default '',
03-nome forncedor    ic_nomefo varchar(120)   default '',
04-Refencia Produto  ic_refere varchar(60)   default '',	                                         #FOI ALTERADO de 20-Para-30 em 08-05-2017 de 30-60
05-Codigo - Barras   ic_cbarra varchar(14)   default '',	
06-Descricao         ic_descri varchar(120)  default '',	
07-Codigo NCM        ic_codncm varchar(8)    default '',	
08-CFOP              ic_cdcfop varchar(4)    default '',	
09-Unidad Comerc.    ic_unidad varchar(6)    default '',
10-Quantidade        ic_quanti decimal(15,4) default 0,
11-Vlr Unid Comer    ic_quncom decimal(20,10) default 0,
12-Vlr Total Produto ic_vlrpro decimal(15,2) default 0,
13-UN Tributada      ic_untrib varchar(6)    default '',
14-QT Tributada      ic_qtribu decimal(15,4) default 0,
15-Vlr UN Tributada  ic_quatri decimal(20,10) default 0,
16-Numero Pedido     ic_pedido varchar(15)   default '',
17-Cod CFI           ic_codcfi varchar(36)   default '',
18-Origem Mercadoria ic_origem varchar(1)    default '',
19-Codigo CST        ic_codcst varchar(3)    default '',
20-Codigo CSOSN      ic_ccsosn varchar(3)    default '',
21-Modalidade BC-ICM ic_modicm varchar(1)    default '',
22-Modalidade BC-CST ic_modcst varchar(1)    default '',
23-Enq legal IPI     ic_enqipi varchar(3)    default '',
24-Vlr BC ICMS       ic_bcicms decimal(15,2) default 0,
25-Pecentual ICMS    ic_pricms decimal(5,2)  default 0,
26-Vlr ICMS          ic_vlicms decimal(15,2) default 0,
27-Percentual MVA-ST ic_permva decimal(6,2)  default 0,
28-Vlr BC-ST         ic_bascst decimal(15,2) default 0,
29-Percentual ICMS   ic_prstic decimal(6,2)  default 0,
30-Vlr ICMS ST       ic_valrst decimal(15,2) default 0,
31-CST - IPI         ic_cstipi varchar(3)    default '',
32-Vlr BC IPI        ic_bscipi decimal(15,2) default 0,
33-Percentual IPI    ic_peripi decimal(6,2)  default 0,
34-Vlr IPI           ic_vlripi decimal(15,2) default 0,
35-CST PIS           ic_cstpis varchar(3)    default '',
36-Vlr BC PIS        ic_vbcpis decimal(15,2) default 0,
37-Percentual PIS    ic_perpis decimal(6,2) default 0,
38-Vlr PIS           ic_vlrpis decimal(15,2) default 0,
39-CST COFINS        ic_cstcof varchar(3)    default '',
40-BC  COFINS        ic_bccofi decimal(15,2) default 0,
41-Percentual COFINS ic_prcofi decimal(6,2) default 0,
42-Vlr COFINS        ic_vlrcof decimal(15,2) default 0,
43-DT Lancamento     ic_lancam date default '00-00-0000',
44-HR Lancamento     ic_horanl time default '00:00:00',
45-QT Anterior       ic_qtante decimal(15,4) default 0,
46-Fabricante        ic_fabric varchar(20)   default '',
47-Grupo             ic_grupos varchar(20)   default '',
48-Custo do produto  ic_vcusto decimal(15,3) default 0,
49-Quantidade UNIDAD ic_qtunid decimal(15,4) default 0,
50-Produto Vinculado ic_prdvin varchar(140)  default '',
51-ST Antecipado %   ic_stantp decimal(6,2)  default 0,
52-ST Antecipado $   ic_stantv decimal(15,2) default 0,
53-FR Antecipado %   ic_frantp decimal(6,2)  default 0,
54-FR Antecipado $   ic_frantv decimal(15,2) default 0,
55-DS Antecipado %   ic_dsantp decimal(6,2)  default 0,
56-DS Antecipado $   ic_dsantv decimal(15,2) default 0,
57-VlUnitarioFora"E" ic_vlruni decimal(15,4) default 0,                                                                   #17-02-2016
58-Nº Registro       ic_nregis varchar(8)    default '',
59-Codigo Produto    ic_cdprod varchar(14)   default '',
60-ValorToTal UNITA  ic_subuni decimal(15,2) default 0,
61-Media ST          ic_medist decimal(6,2)  default 0,
62-Seguro por fora % ic_pfsegu decimal(6,2)  default 0,
63-Seguro pof fora $ ic_vfsegu decimal(15,2) default 0,
64-Desp.Acessorias % ic_pfdsac decimal(6,2)  default 0,
65-Desp.Acessorias $ ic_vfdsac decimal(15,2) default 0,
66-EntraSaida ITEMS  ic_esitem varchar(1)    default 'E',
67-DT Cancelamento   ic_dtcanc date default '00-00-0000',
68-HR Cancelamento   ic_hocanc time default '00:00:00',
69-US cancelamento   ic_uscanc varchar(12)   default '',
70-CD Us Canclamento ic_cdusca varchar(4)    default '',
71-Status Cancel {1} ic_cancel varchar(1)    default '',
72-QT Anterior CANCE ic_qtanca decimal(15,4) default 0,
73-IMCS Frete Media% ic_icmfrm decimal(6,2)  default 0,
74-ICMS FRETE Vakir$ ic_icmfrv decimal(15,2) default 0,
75-Filial            ic_filial varchar(5)    default "",
76-Us Lancamento     ic_uslanc varchar(12)   default "",
77-CD US Lacamento   ic_cdusla varchar(4)    default "",
78-Tipo 1,2,3,4,5,7  ic_tipoen varchar(1)    default "",
79-QT FICHA ESTOQUE  ic_fichae decimal(15,4) default 0,
80-Transf Fl Orgime  ic_forige varchar(5)    default '',
81-Transf Fl Destino ic_fdesti varchar(5)    default '',
82-IPI Avulso %      ic_ipipav decimal(6,2)  default 0,                                                                  #Tambem servi pra percentual de quantidade de IPI devolvido
83-ST  Avulso %      ic_stpavu decimal(6,2)  default 0,
84-IPI Avulso $      ic_ipiavl decimal(15,4) default 0,
85-ST  Avulso $      ic_stavvl decimal(15,4) default 0,
86-CodigoFiscal RMA  ic_cfisca varchar(30)   default '',
87-Dados RMA         ic_dadrma text,
88-RetFilial Remota  ic_fremot varchar(5) default ''
89-Unidade de manejo ic_cmanej varchar(100)  default '',
90-valor manejo      ic_vmanej decimal(15,2) default 0,
91-total manejo      ic_tmanej decimal(15,2) default 0,
92-manejoExtrator_id ic_unmaid varchar(8) default '',
93-manejo nome       ic_unnome varchar(100) default '',
94-manejo fantasia   ic_unfant varchar(40) default '',
95-manejo documento  ic_undocu varchar(14) default '',
96-ID-Fornecedor     ic_idforn varchar(8)  default '',
97-InforTempoNFE     ic_inftem MEDIUMBLOB,
INDEX (ic_lancam),
INDEX (ic_dtcanc));                                                                            #informacoes temporario para emissao da nfe de rma

#CREATE INDEX idx_COMPRA_DTAL ON iccmp(ic_lancam);
#CREATE INDEX idx_COMPRA_DCAN ON iccmp(ic_dtcanc);

00-registro		     create table apagar (ap_regist int(10) not null auto_increment primary key,
01-cnpj-cpf          ap_docume varchar(14)   default '',
02-nome forncedor    ap_nomefo varchar(60)   default '',
03-Fantasia          ap_fantas varchar(60)   default '',
04-NoControleCompra  ap_ctrlcm varchar(10)   default '',
05-Numero NFE        ap_numenf varchar(9)    default '',
06-DT Lancamento     ap_dtlanc date          default '00-00-0000',
07-HR Lancamento     ap_hrlanc time          default '00:00:00',
08-Usuario Lanca     ap_usalan varchar(20)   default '',
09-DT Vencimento     ap_dtvenc date          default '00-00-0000',
10-NumeroDuplicata   ap_duplic varchar(40)   default '',
11-NumeroParcela     ap_parcel varchar(2)    default '',
12-Valor Duplicata   ap_valord decimal(15,2) default 0,
13-DT Baixa          ap_dtbaix date          default '00-00-0000',
14-HR Baixa          ap_horabx time          default '00:00:00',
15-Valor Baixado     ap_valorb decimal(15,2) default 0,
16-Usuario Baixa     ap_usabix varchar(20)   default '',
17-Filial            ap_filial varchar(5)    default '',
18-DT Cancela        ap_dtcanc date          default '00-00-0000',
19-HR Cancela        ap_hocanc time          default '00:00:00',
20-Usuario Cancela   ap_usacan varchar(20)   default '',
21-1-BX 2-CAN        ap_status varchar(1)    default '',
22 Codigo us baixa   ap_cdusbx varchar(4)    default '',
23 codigo us lanca   ap_cduslc varchar(4)    default '',
24 codigo us cance   ap_cdusca varchar(4)    default '',
25-Correntista       ap_chcorr varchar(150)  default '',                                                                           #-23-06-2017 de 50 para 150
26-NoBanco           ap_chbanc varchar(3)    default '',                                                                          
27-Agencia           ap_chagen varchar(10)   default '',
28-ContaCorrente     ap_chcont varchar(20)   default '',
29-NoCheque          ap_chnume varchar(10)   default '',
30-Juros-Multa       ap_jurosm decimal(15,2) default 0,
31-Historico         ap_histor text,
32- 1-Estorno        ap_estorn varchar(1)    default '',
33- Numero Bordero   ap_border varchar(10)   default '',
34- 1-Titulo2-Chq"F" ap_pagame varchar(2)    default '',                                                                            #-Indicacao de Pagamento 02-03-2016
35-Agrupamento       ap_agrupa varchar(10)   default '',
36-1 Cancela Agrupar ap_cangru varchar(1)    default '',
37-Lista Agrupamento ap_lisagr text,
38-Confere 1-2       ap_confer varchar(1)    default '',
39-HistoConfere      ap_hiscon text,
40-Lanca XML TIPO"F" ap_lanxml varchar(2)    default '',                                                                            #-Tipo de Documento 02-03-2016
41-Diversos {Desc}   ap_divers varchar(60)   default '',
42-Desconto          ap_descon decimal(15,2) default 0,
43-SacadoAvalista    ap_avalis varchar(120)  default '',
44-Plano de Contas   ap_contas varchar(20)   default '',
45-Baixa FPagamento  ap_fpagam text,
46-registroCADFornec ap_rgforn int(8)        default 0,
47-Bordero Receber   ap_bterce varchar(10)   default '',
48-NºCTRL Parcial    ap_pacial varchar(13)   default '',
49-Valor Original    ap_vlorig decimal(15,2) default 0,
50-Baixa Parcial     ap_bxparc varchar(1)    default'',
51-Historico usuario ap_hisusa text,
52-Unidade de Manejo ap_uniman varchar(100)  default'',
53-rel bx grupo parc ap_grparc MEDIUMBLOB,
INDEX apagar(ap_dtlanc)
INDEX apagar(ap_dtvenc)
INDEX apagar(ap_dtbaix)
INDEX apagar(ap_dtcanc));

#CREATE INDEX idx_APAGAR_DLAN ON apagar(ap_dtlanc);
#CREATE INDEX idx_APAGAR_DVEN ON apagar(ap_dtvenc);
#CREATE INDEX idx_APAGAR_DBAI ON apagar(ap_dtbaix);
#CREATE INDEX idx_APAGAR_DCAN ON apagar(ap_dtcanc);


"""
	Vazio Aberto 1-Baixa 2-Cancelados 
	40 Tipo de Lancamento da NFE para Contas Apagar
	
	ap_fpagam Lancar formas de pagamentos
	ex: 01PG:123.22|02PG:231.11 o PG a para facilitar a pesquisa por forma de pagamentos
	
"""


#-->[ Sangria-Suprimentos ]
00-ID Lancamento    create table sansu (ss_regist int(8) not null auto_increment primary key,
01-DT Lancamento    ss_lancam date          default '00-00-0000',
02-HR Lancamento    ss_horala time          default '00:00:00',
03-NM-Usuario       ss_usnome varchar(12)   default '',
04-Retiroi-Usuario  ss_usreti varchar(12)   default '',
05-ID-Filial Lanc   ss_idfila varchar(5)    default '',
06-Dinheiro         ss_dinhei decimal(15,2) default 0,
07-Ch.Avista        ss_chavis decimal(15,2) default 0,
08-Ch.Predatado     ss_chpred decimal(15,2) default 0,
09-Cartao Credito   ss_credit decimal(15,2) default 0,
10-Cartao Debito    ss_debito decimal(15,2) default 0,
11-E-S              ss_ensaid varchar(1)    default '',
12-Historico        ss_histor text);

#-->[ modulosPerfil ]
00-ID Lancamento    create table modperfil (mp_regist int(8) not null auto_increment primary key,
01-DT Lancamento    mp_lancam date         default '00-00-0000',
02-HR Lancamento    mp_horala time         default '00:00:00',
03-NM-Usuario       mp_usnome varchar(12)  default '',
04-1-Modulo 2-Prfil mp_mdperf varchar(1)   default '',
05-perfil           mp_perfil varchar(2)   default '',
06-Modulo pai       mp_modpai varchar(2)   default '',
07-Modulo filho     mp_mfilho varchar(4)   default '',
08-Descricao        mp_descri varchar(200) default '',
09-Autorizacao SN   mp_autori varchar(1)   default '');

#-->[ Autorizacao ]
00-ID Lancamento    create table auremoto (au_regist int(8) not null auto_increment primary key,
01-R-Remoto L-Local au_lancam varchar(1)   default '',
02-DT Pedido        au_dtpedi date         default '00-00-0000',
03-HR Pedido        au_hrpedi time         default '00:00:00',
04-Usuario          au_uspedi varchar(20)  default '',
05-DT Liberacao     au_dtlibi date         default '00-00-0000',
06-HR Liberacao     au_hrlibi time         default '00:00:00',
07-Usuario          au_uslibi varchar(20)  default '',
08-Historico        au_histor text,
09-US-Solicitado    au_solius varchar(20)  default '',
10-Comanda TMP      au_comand varchar(15)  default '',
11-Descartado       au_descar varchar(1)   default '',
12-HistoAnterior    au_hisant text,
13-Modulo           au_modulo varchar(2)   default '');

#-->[ Codigos do municipio ]
00-ID Lancamento create table municipio (mu_regist int(8) not null auto_increment primary key,
01-Estado        mu_estado varchar(2)   default '',
02-CD Municipio  mu_codigo varchar(7)   default '',
03-Descricao     mu_munici varchar(200) default '');

#-->[ Romaneio de Entrega ]
00-ID Lancamento     create table romaneio (rm_regist int(8) not null auto_increment primary key,
01-Numero  Romaneio  rm_roman varchar(10)   default '',
02-Abertura DATA     rm_abedt date          default '00-00-0000',
03-Abertura Hora     rm_abehr time          default '00:00:00',
04-Abertura Login    rm_abeus varchar(12)   default '',
05-Abertura CD-USA   rm_abecu varchar(4)    default '',
06-Fechamento DATA   rm_fecdt date          default '00-00-0000',
07-Fechamento Hora   rm_fechr time          default '00:00:00',
08-Fechamento Login  rm_fecus varchar(12)   default '',
09-Fechamento CD-USA rm_feccu varchar(4)    default '',
10-Cancelar DATA     rm_candt date          default '00-00-0000',
11-Cancelar Hora     rm_canhr time          default '00:00:00',
12-Cancelar Login    rm_canus varchar(12)   default '',
13-Cancelar CD-USA   rm_cancu varchar(4)    default '',
14-Quantidade DAVs   rm_qtdav int(4)        default 0,
15-Relacao DAVS      rm_relac text,
16-Historico         rm_histo text,
17-CPF-CNPJ TRANS    rm_cpfcn varchar(14)   default '',
18-Motorista         rm_motor varchar(60)   default '',
19-Placa             rm_placa varchar(10)   default '',
20-Tipo Veiculo      rm_tipov varchar(60)   default '',
21-Kilometragem      rm_kilom varchar(7)    default '',
22-DATA Entrega		 rm_dtent date          default '00-00-0000',
23-Transportadora    rm_trans varchar(60)   default '',
24-RegTransportadora rm_ident varchar(8)    default '',
25-Notificacao SMS   rm_nosms varchar(100)  default '',                 #// 14-12-2107 17:27
INDEX romaneio (rm_roman),
INDEX romaneio (rm_abedt),
INDEX romaneio (rm_fecdt),
INDEX romaneio (rm_candt)
INDEX romaneio (rm_nosms));

#CREATE INDEX idx_ROMA_NUM ON romaneio(rm_roman);
#CREATE INDEX idx_ROMA_ABE ON romaneio(rm_abedt);
#CREATE INDEX idx_ROMA_FEC ON romaneio(rm_fecdt);
#CREATE INDEX idx_ROMA_CAN ON romaneio(rm_candt);
#CREATE INDEX idx_ROMA_SMS ON romaneio(rm_nosms);
""" Status 0-Nao Atualizado 1-Atualizado no Banco Destino """

#-->[ Emissao de NFe,NFce ]
00-ID Lancamento     create table nfes (nf_regist int(10) not null auto_increment primary key,
01-1-Nfe 2-Nfce      nf_nfesce varchar(1)   default '',
02-Tipo NFes         nf_tipnfe varchar(1)   default '',
03-Tipo Lancamento   nf_tipola varchar(1)   default '',
04-Envio DATA        nf_envdat date         default '00-00-0000',
05-Envio Hora        nf_envhor time         default '00:00:00',
06-Envio Usuario     nf_envusa varchar(12)  default '',
07-Retorno DT,HORA   nf_retorn varchar(40)  default '',
08-Retorno SEFAZ     nf_rsefaz text,
09-Retorno Hora      nf_rethor time         default '00:00:00',
10-Numero DAV-Pedido nf_numdav varchar(13)  default '',
11-Origem DAV        nf_oridav varchar(1)   default '',
12-Cancela DATA      nf_candat date         default '00-00-0000',
13-Cancela Hora      nf_canhor time         default '00:00:00',
14-Cancela Usuario   nf_canusa varchar(12)  default '',
15-Can RET DT,HORA   nf_canret varchar(40)  default '',
16-CAn Retorno Hora  nf_carhor time         default '00:00:00',
17-Inutiliza DATA    nf_inndat date         default '00-00-0000',
18-Inutiliza Hora    nf_innhor time         default '00:00:00',
19-Inutiliza Usuario nf_innusa varchar(12)  default '',
20-INU RET DT,HORA   nf_innret varchar(40)  default '',
21-INU Retorno Hora  nf_inrhor time         default '00:00:00',
22-1-Producao 2-Homo nf_ambien varchar(1)   default '',
23-ID-Filial         nf_idfili varchar(5)   default '',
24-Nº Protocolo      nf_protoc varchar(60)  default '',
25-Nº Chave          nf_nchave varchar(44)  default '',
26-Nº NFe,NFCe       nf_nnotaf varchar(9)   default '',
27-CodigoClienete"C" nf_codigc varchar(14)  default '',                                                          #-:Alterado para Suportar o novo codigo do cliente
28-CPF-CNPJ          nf_cpfcnp varchar(14)  default '',
29-Fantasia          nf_fantas varchar(60)  default '',
30-NomeCliente Forn  nf_clforn varchar(120) default '',
31-CartaCorreçãoDTHR nf_retcce varchar(40)  default '',
32-URL do QRCODE     nf_urlqrc MEDIUMBLOB,
33-Nº Serie          nf_nserie varchar(3)  default '',
34-DATA-HORA do ProT nf_emprot varchar(60) default '',
35-Digest Value      nf_dgvalu varchar(60) default '',                                                           #-:Usado para guardar a data de emissao do dav
36-Contigencia  "D"  nf_contig varchar(100) default '',
37-Nº Contigncia     nf_nconti varchar(1)  default '',
38-RtornoContigencia nf_rconti varchar(160) default '',                                                          #-:CsTa|Novo Numero da Chave { Recuperacao do XML } - Tratar Duplicidade de NFe
39-cStat             nf_ncstat varchar(3)  default '',
40-XMLProtocoloCance nf_prtcan MEDIUMBLOB,
41-TotalDAV		     nf_vlnota decimal(15,2) default 0,
INDEX nfes(nf_envdat));
#CREATE INDEX idx_NFES_DATA ON nfes(nf_envdat);

""" nf_tipnfe 1-Venda,2-Devolucao de Vendas,3-Comras{Entrada de Mercadorias},4-Devolucao Compras-RMA,5-Transferencia,6-Simples Faturamento
	nf_tipola 1-Emissao 2-Inutilizar 3-Cancelamento 4-Inutilizadas 5-Nota Denegada
	nf_oridav 1-Venda   2-Compras

	nf_rconti =	cnpj,seri,noTa,proT,chav,siTu, data, hora, usuario
	nf_nconti = 1-em contigencia 2-contigencia resolvida
	
"""

#-->[ Emissao de NFe,NFce ]
00-ID Lancamento     create table sefazxml (sf_regist int(10) not null auto_increment primary key,
01-Numero DAV-Pedido sf_numdav varchar(13) default '',
02-Numero NFE        sf_notnaf varchar(9)  default '',
03-Conteudo do XML   sf_xmlarq text,
04-Conteudo PDF{CCE} sf_pdfarq MEDIUMBLOB,                      
05-Chave da NFce     sf_nchave varchar(44) default '',
06-Tipo 1-NFe 2-NFce sf_tiponf varchar(1)  default '',
07-Codigo da Filial  sf_filial varchar(5)  default '',
08-NF-Serie-Filial   sf_codigo varchar(20) default '',
09-Conteudo XML      sf_arqxml MEDIUMBLOB,
INDEX(sf_nchave));
# CREATE INDEX idx_XML_CHAV ON sefazxml(sf_nchave);

#-->[ Plano de Contas ]
00-ID Lancamento        create table plcontas (pl_regist int(10) not null auto_increment primary key,
01-NumeroContaCompleta  pl_nconta varchar(20) default '',
02-DescricaoSubConta 2  pl_dconta varchar(60) default '',
03-DescricaoSubConta 3  pl_dcont3 varchar(60) default '',
04-DescricaoSubConta 4  pl_dcont4 varchar(60) default '');

#-->[ Temporario para Emissao Relatorio de Compras Quantitativa de Clientes ]
00-ID Lancamento        create table tmpclientes (tc_regist int(10) not null auto_increment primary key,
01-Informacoes Gerais   tc_inform MEDIUMBLOB,
02-Usuario              tc_usuari varchar(20) default '',
03-Quantidade           tc_quanti int(10) default 0,
04-Valor                tc_vlrpro decimal(15,2) default 0,
05-Quantidade   "ALT"   tc_quantf decimal(15,4) default 0,
06-codigo venda         tc_vdcd varchar(4) default '',
07-nome venda           tc_nmvd varchar(12) default '',
08-codigo caixa         tc_vdcc varchar(4) default '',
09-nome caixa           tc_nmvc varchar(12) default '',
10-DATA                 tc_inndat date default '00-00-0000',
11-frabricante          tc_fabr varchar(20) default '',  
12-endereco             tc_ende varchar(10) default '',  
13-grupo                tc_grup varchar(20) default '',
14-sub-grupo 1          tc_sbg1 varchar(20) default '',
15-sub-grupo 2          tc_sbg2 varchar(20) default '',
16-codigo produto       tc_codi varchar(14) default '', 
17-codigo barras        tc_barr varchar(14) default '',  
18-nome produto         tc_nome varchar(120) default '',  
19-unidade prod         tc_unid varchar(2) default 'UN',
20-Quantidade  "ALT"    tc_quantd decimal(15,4) default 0,
21-Valor                tc_valor  decimal(15,2) default 0,
22-Nome do Relatorio    tc_relat  varchar(5)    default '',
23-Informacoes Gerais2  tc_infor2 MEDIUMBLOB,
24-Informacoes Gerais3  tc_infor3 MEDIUMBLOB,
25-Quantidade  "ALT"    tc_quant1 decimal(15,4) default 0,
26-Quantidade  "ALT"    tc_quant2 decimal(15,4) default 0,
27-Quantidade  "ALT"    tc_quant3 decimal(15,4) default 0,
28-Hoario               tc_hora   time default '00:00:00',
29-Filial               tc_filial varchar(5) default "",
30-Valor1               tc_valor1 decimal(15,3) default 0,
31-Valor2               tc_valor2 decimal(15,2) default 0,
32-Valor3               tc_valor3 decimal(15,3) default 0,
33-OBservacoes          tc_obser1 varchar(100)  default '',
34-Controle-DAV         tc_davctr varchar(14)   default '',
35-Var 1                tc_varia1 varchar(20)   default '',
36-Cliente Forncedor    tc_clifor varchar(120)  default '');


#-->[ Estoque ]
00-ID Lancamento        create table estoque (ef_regist int(10) not null auto_increment primary key,
01-ID-Filial            ef_idfili varchar(5) default '',
02-Codigo do Produto    ef_codigo varchar(14) default '',
03-ID-Produto           ef_idprod varchar(8) default '',
04-Estoque Fisico "ALT" ef_fisico decimal(15,4)  not null default 0,
05-Estoque Virtual"ALT" ef_virtua decimal(15,4)  not null default 0,
06-Estoque RMA    "ALT" ef_trocas decimal(15,4)  not null default 0,
07-Estoque loja         ef_esloja decimal(15,4)  not null default 0,                                            #01-02-2018
08-Endereco no estoque  ef_endere varchar(10)  default '',                                                       #15-05-2018
INDEX (ef_codigo));

#CREATE INDEX idx_ESTF_CODI ON estoque(ef_codigo);

#-->[ Cadastro de Fretes ]
00-ID Lancamento   create table fretes (ft_regist int(10) not null auto_increment primary key,
01-Estado          ft_estado varchar(2) default '',
02-Municipio       ft_munici varchar(60) default '',
03-Bairro          ft_bairro varchar(60) default '',
04-Valor           ft_valorf decimal(15,2)  not null default 0,
05-CadastroAltera  ft_ajuste text);


#-->[ Cadastro de entregas entre filiais ]
00-ID Lancamento   create table entregas (en_regist int(10) not null auto_increment primary key,
01-Filial Origem   en_filori varchar(5)  default '',
02-Filial Entrega  en_filent varchar(5)  default '',
03-Nº DAV          en_numdav varchar(13) default '',
04-Nº CTRL-Origem  en_ctrlor varchar(10) default '',
05-Nº CTRL-Entrega en_ctrlet varchar(10) default '',
06-QT-Anterio EF   en_qtante decimal(15,4) default 0,
07-QT-Entregue     en_qtentr decimal(15,4) default 0,
08-usuario entre   en_usentr varchar(12)   default '',
09-usuario cancel  en_uscanc varchar(12)   default '',
10-Entrega DATA    en_entdat date         default '00-00-0000',
11-Entrega Hora    en_enthor time         default '00:00:00',
12-Cancela DATA    en_candat date         default '00-00-0000',
13-Cancela Hora    en_canhor stime         default '00:00:00',
14-Codigo Produto  en_cdprod varchar(14)  default '',
15-Descricao       en_dsprod varchar(120) default '',
16-Portador        en_portad varchar(120) default '');

#-->[ Notas fiscais de compras ]
00-ID Lancamento     create table comprasxml (nc_regist int(10) not null auto_increment primary key,
01-Numero DAV-Pedido nc_contro varchar(10) default '',
02-Numero NFE        nc_notnaf varchar(9)  default '',
03-Chave da NFce     nc_nchave varchar(44) default '',
04-Codigo da Filial  nc_filial varchar(5)  default '',
05-Entrada DATA      nc_entdat date        default '00-00-0000',
06-Entrada Hora      nc_enthor time        default '00:00:00',
07-Nota Emissao      nc_notdat date        default '00-00-0000',
08-Nota Hora         nc_nothor time        default '00:00:00',
09-Usuario           nc_usuari varchar(12) default '',
10-Nome fantasia     nc_nomefa varchar(100) default '',
11-Nomer fornecedor  nc_nomefc varchar(200) default '',
12-CPF-CNPJ  		 nc_docfor varchar(14)  default '',
13-Valor da nota     nc_valorn decimal(15,4) default 0,
14-Conteudo XML      nc_arqxml MEDIUMBLOB,
15-Cancelamento PD   nc_cancel varchar(50)  default '',
INDEX(nc_notnaf,
INDEX(nc_nchave,
INDEX(nc_filial,
INDEX(nc_entdat));

#-->[ Notas fiscais de compras ]
00-ID Lancamento     create table relacionamento (rl_regist int(10) not null auto_increment primary key,
01-Filial 			 rl_filial varchar(5) default '',
02-LoginDataHora     rl_envios varchar(50)  default '',
03-RetornoEnvio      rl_status varchar(200) default '',
04-MensagemEnviada   rl_mensag MEDIUMBLOB,
05-DataEnvio         rl_envdat date        default '00-00-0000',
06-HoraEnvio         rl_envhor time        default '00:00:00',
07-ID-Envio          rl_idenvi varchar(20) default '',
08-NomeCampanh       rl_campan varchar(100) default '',
09-MidiaSMS-Whatsapp rl_midias varchar(50) default '',
10-Usuario           rl_usuari varchar(12) default '',
11-Nome do cliente   rl_nomecl varchar(120) default '',
12-Telefone envio    rl_telefo varchar(20) default '',
13-codigocliente     rl_codigo varchar(14) default '',
14-Ref FANTA-CLIE    rl_refere varchar(50) default '',
INDEX(rl_filial),
INDEX(rl_envdat),
INDEX(rl_midias),
INDEX(rl_usuari));




#-->[ Controle pelo numero de serie ]
00-ID Lancamento        create table nseries (il_regist int(10) not null auto_increment primary key,                     
01-ID-Filial            il_idfili varchar(5)   default '',
02-ControleCompra       il_contro varchar(10)  default '',
03-ChaveNFCompra        il_nchave varchar(44)  default '',
04-CPNJ-Fornecedor      il_cnpjfo varchar(14)  default '',
05-CNPJ-Filial          il_cnpjfl varchar(14)  default '',
06-Codigo Produto       il_codigo varchar(14)  default '',
07-ID-Produto           il_idprod varchar(10)  default '',
08-NumeroSerie          il_nserie varchar(120) default '',
09-QuemComprou          il_compra varchar(120) default '',
10-QuemVendeu           il_vendeu varchar(120) default '',
11-QuemCancelou         il_cancel varchar(120) default '',
12-QuemDevolveu         il_devolv varchar(120) default '',
13-DAV-Venda            il_davend varchar(14)  default '',
14-DAV-Devolucao        il_davdev varchar(14)  default '',
15-Status"1Venda-2Canc" il_status varchar(1)  default '',
16-QuemComprouCancel    il_cancom varchar(120) default '',
17-QuemReservou         il_reserv varchar(120) default '',
18-PdOriginalDevolucao  il_pdordv varchar(120) default '',
19-DavOriginouDevolucao il_dvodev varchar(14)  default '',
20-Gravar o item        il_itemdv varchar(3)  default '',
INDEX (il_codigo),
INDEX (il_contro),
INDEX (il_nchave),
INDEX (il_cnpjfo),
INDEX (il_cnpjfl),
INDEX (il_nserie));

#-->[ Controle do conta corrente banco ]
00-ID Lancamento        create table bancoconta (bc_regist int(14) not null auto_increment primary key,
01-NumeroDocumento      bc_docume varchar(50)  default '',
02-Data-Lancamento      bc_dlanca date         default '00-00-0000',
03-Hora-Lancamento      bc_hlanca time         default '00:00:00',
04-ID-BancoCadastroForn bc_idcada varchar(8)  default '',
05-Plano de contas      bc_planoc varchar(20)  default '',
06-ValorLancamentoAnte  bc_valora decimal(15,2) default 0,
07-ValorLancamentoCred  bc_valorc decimal(15,2) default 0,
08-ValorLancamentoDebi  bc_valord decimal(15,2) default 0,
09-ValorLancamentoSaldo bc_valors decimal(15,2) default 0,
10-historico de lanca   bc_histor MEDIUMBLOB,
11-historico curto      bc_hiscur varchar(100)  default '',
12-ID-Filial lancamento bc_filial varchar(5)  default '',
13-Usuario do lancament bc_usuari varchar(20)  default '',
14-Origem Lacamento     bc_origem varchar(100)  default '',
15-Tipo de Lacamento    bc_tipola varchar(2)  default '',
INDEX (bc_dlanca),
INDEX (bc_idcada),
INDEX (bc_planoc));





# ef_idfili='"+str(  )+"' and ef_codigo='"+str(  )+"' and ef_idprod='"+str(  )+"'
#-----------------------------------------------------------------#
REMOVER ESPACOS EM BRANCO STRING:

""" ID DO EVENTO PAI """
event.GetEventObject().GetId()


""" Usuario ativo no linux no momento """
print wx.GetUserId()
	
import clr
clr.AddReference('System')
import System
System.String.IsNullOrEmpty('') # returns True
System.String.IsNullOrEmpty(None) # returns True
System.String.IsNullOrEmpty('something') # returns False


sentence = ' hello  apple'
sentence.strip()
>>> 'hello  apple'
If you want to remove all spaces, you can use str.replace()

sentence = ' hello  apple'
sentence.replace(" ", "")
>>> 'helloapple'
If you want to remove duplicated spaces, use the str.split()

sentence = ' hello  apple'
" ".join(sentence.split())
>>> 'hello apple'

sentence = ' hello  apple'
sentence.trim()

#		_mensagem = wx.StaticText(self, -1, "{ Aguarde, pesquisando }",pos=(310,430),size=(400,40))
#		_mensagem.SetForegroundColour('#285428')
#		_mensagem.SetFont(wx.Font(20, wx.ROMAN, wx.NORMAL,  wx.BOLD))

		#wx.SafeYield()
		#wx.Yield()
		#wx.YieldIfNeeded()

"""
	# Marcro Substituicao CLIPPER & python eval() '''
	nconta = 'self.c'+str(_nc)+'_'+str(_s1)+'_'+str(_s2)
	self.tree.AppendItem(eval(nconta),str(i[1])+' - '+str(i[0]).zfill(10)+":"+str(i[2]))
	self.tree.AppendItem(eval(nconta),str(i[1])+' - '+str(i[2]))

"""

""" Exemplo de Plano de Contas """

		#aTivoCi   = self.tree.AppendItem(aTivo,   u'1.1 - Ativo Circulante')
		#aTivonC   = self.tree.AppendItem(aTivo,   u'1.2 - Ativo não Circulante') 
		
		#passivoCi = self.tree.AppendItem(passivo, u'2.1 - Passivo Circulante')
		#passivonC = self.tree.AppendItem(passivo, u'2.2 - Passivo não Circulante') 
		
		#recope = self.tree.AppendItem(receitas, u'3.1 - Receitas Operacionais')
		#self.c3_1_1 = self.tree.AppendItem(recope,"3.1.1 - Vendas")
		#self.c3_1_2 = self.tree.AppendItem(recope,"3.1.2 - Financeiras")
		#self.c3_1_3 = self.tree.AppendItem(recope,"3.1.3 - Outras Receitas")

		#desope = self.tree.AppendItem(despesas, u'4.1 - Despesas Operacionais')
		#self.c4_1_1 = self.tree.AppendItem(desope,"4.1.1 - Despesas Administrativas")
		#self.c4_1_2 = self.tree.AppendItem(desope,"4.1.2 - Despesas com Vendas")
		#self.c4_1_3 = self.tree.AppendItem(desope,"4.1.3 - Despesas Financeiras")
		#self.c4_1_4 = self.tree.AppendItem(desope,"4.1.4 - Outras Despesas")

Mysql
Backup
mysqldump sei -u root -p > banco.sql

Restore
mysql sei -u root -p < banco.sql

exportar para csv
select * from clientes into outfile "/tmp/lobo.csv" FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n';

registros duplicados [ Mostar apenas os o primeiro registro e o primeiro count mostar o total de registro contido o where se for pesquisa apens um se nao nao tem necessidade ]
SELECT DISTINCT it_ndav,it_nome,count(*) FROM idavs where it_ndav='0000000010731' GROUP BY it_ndav HAVING count(*) order by it_ndav;

""" porta USB Permanente no linux """
na pasta etc/udev/rules.d
criar arquivo 70-persistent_usb.rules

adiciona a linha

SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE=="0777"
:ps 0403 6001 e o id do fabricante da ECF

-para reler 
udevadm control --reload-rules
-desligar e ligar

Amarrando a posta USB0 para impressora daruma
-Adicona mais duas linhas { Vc pode colocar a impressora em quanquer port usb ele identifica para a porta USB0 }
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE=="0777"
SUBSYSTEMS=="usb", ATTRS{Manufacturer}=="URMET DARUMA", SYMLINK+="ttyUSB0"

-para reler 
udevadm control --reload-rules
-desligar e ligar

""" Testando a PORTA USB """
echo -9 "\0033\0317" > /dev/ttyUSB0 #Ejecta Linha
echo -e "\0033\0317" > /dev/ttyUSB0 #Leitura X

""" Mudando a Velocidade da Porta """
stty -F /dev/ttyUSB0 speed -> Mostrar a velocidade
stty -F /dev/ttyUSB0 speed 115200 -> muda a velocidade

""" Configuracao para ICEWM toolbar e menu """
prog Lykos seip xterm -n Lykos-SEI -iconic -e seip



""" Webservices para NFE,NFse e NFCe """
http://www.webenefix.com.br/nfc-e/f-a-q/



""" Projetos de NFE """
https://github.com/odoobrasil-fiscal/nfe
https://github.com/aricaldeira/PySPED
https://github.com/JuniorPolegato/pole/tree/master/fontes/pole

#------------[ Novo 14-10-2017 Codigo bem limpo ]

https://github.com/thiagopena/PySIGNFe

#-------------------------------------:

https://github.com/marcydoty/Recursos-NFE-em-Python
https://github.com/leonardoRC/PyNFe
https://github.com/odoo-brazil/PySPED
http://pynfe.readthedocs.org/pt/latest/
https://focusnfe.com.br/
https://github.com/kmee
https://github.com/kmee/PySPED/tree/odoo/pysped/nfe  { o desenvolvedor e o caldeira }
https://github.com/Trust-Code/PySPED
https://github.com/leotada/PyNFe #-: Tem NFCe QRCODE

https://recordnotfound.com/PyNFe-leotada-62708
https://github.com/leotada/PyNFe

https://groups.google.com/forum/#!forum/pynfe

https://github.com/danimaribeiro/PyTrustNFe #NOVO NFCE

https://github.com/thiagopena/PySIGNFe #Novo baseado na macydot e caldeira


"""   CALCULO DO ICMS-ST   """
Entra ipi+pis+cofins
http://socontabilidadeblog.blogspot.com.br/2013/04/como-calcular-o-icms-st.html

https://www.youtube.com/user/partnersbematech/videos


ver versao do linux
cat /etc/*-release
#### Vincular COO NFE3.10
http://www.flexdocs.com.br/guiaNFe/gerarNFe.ref.refECF.html

## Adidicnar FAtura pysped-mastar

#n.infNFe.cobr.fat.nFat.valor  = "22342"
#n.infNFe.cobr.fat.vOrig.valor = "32.20"
#n.infNFe.cobr.fat.vLiq.valor  = "32.20"

" xds da nfe verificar as posicoes e valore das tags"
https://searchcode.com/codesearch/view/73305206/


rsync -aHvz vendas@monfardini.dyndns.info:/mnt/simm/paf/simm /home/vendas/lobo



#--: Zerando do senha do root no mysql e redefinindo senha nova
http://www.susebr.org/forum/index.php?topic=3334.0


SETAR a PORTA SERIAL DO ECF

Crie um arquivo /etc/udev/rules.d/60-serial.rules  ou 
Crie um arquivo /etc/udev/rules.d/70-serial.rules :

KERNEL == "ttyS0", MODE = "0777"


HISTORY -CW APAGAR O HISTORICO
http://www.newssystems.eti.br/site/ nfce


bematech
http://blog.rafaelsdm.com/2013/08/configurando-impressora-bematech-mp.html







############## SIMULA #############################################
simula.invoicy.com.br
joselobinho@gmail.com
senha: 151407jml

############## Daruma Migrate Homogação ###########################

Link: https://homolog.invoicy.com.br/
Usuário: romulott@gmail.com
Troque o usuario: joselobinho@gmail.com
Senha: 151407jml
Senha: 721266

Chave de Parceiro: ovPlwhWieWokTjC8a27iLQ==
Código de Parceiro:  16057

Produção
Link: https://app.invoicy.com.br/
Usuário: romulott@gmail.com

Troque o usuario: joselobinho@gmail.com
Senha: 151407jml
Senha: 898583

Chave do Parceiro: ovPlwhWieWokTjC8a27iLQ==
Código de Parceiro:  16057

############# Dados da JPF para NFCE #############################
#-: chave do cliente no invoyce
Homologacao: 9OcC70TSTgOthqHVr6Z8ixeWZNQlqjSt
Producao...: 9OcC70TSTgOthqHVr6Z8i6uJShN+Q0lC

#-: Tocken SEFAZ
ID-Homologacao....: 000001
Tocken Homologacao: 8010637EC32B86C9F38262CD6D5976516ZPB

ID-Producao....: 000003
Tocken Producao: 3691F2E6D996DC9D805C5137F7D85FE1HZA2

############ Site Consulta Rio de Janeiro #######################
#-: Homologacao-Producao pela CHAVE
http://nfce.fazenda.rj.gov.br/consulta

#-: Homologacao-Producao pelo QRCODE
http://www4.fazenda.rj.gov.br/consultaNFCe/QRCode



Pessoal do desenvolvimento,

Vocês sabem dizer se os Status e retornos de eventos abaixo já estão sendo tratados no ACBrNFe ?

150 - Autorizado o uso da NF-e, autorização concedida fora de prazo.

151 - Cancelamento de NF-e homologado fora de prazo.

155 - Cancelamento homologado fora de prazo.

Dando uma olhada nos fontes, não encontrei referência a estes códigos.


http://software.opensuse.org/package/kiwi-ltsp

######### TSLIB para calibrar o touch screen
vi no br linux http://www.dobitaobyte.com.br/geral/raspberry-pi-com-monitor-tft-de-3-2-polegadas

tecno speed
https://ciranda.me/tsdn/blog-da-consultoria-tecnica-tecnospeed/post/como-realizar-um-post-com-basic-auth-em-python


### MASKED ###### ValueError: "      0.00" will not fit into the control "masked.num"
Resolvi em nfe2.py linha 1803,1804 -> Transformando em STR, str( valor )

e esse:  nao dar SetValue(xx) antes de message,ou uma parada
por que da erro de : ValueError: "     37.50" will not fit into the control "masked.num"

	- FUNCIONOU BEM # as veses dava erro depois q fiz direto sem variavel parou de dar problema
wx.MessageDialog(self.painel,"Confirme para eliminar produto selecionado!!\n"+(" "*120),"Compras: Apagar produtos selecionado",wx.YES_NO).ShowModal() ==  wx.ID_YES:




######### Alta Disponibilidade com MYSQL
http://www.mysqlbox.ml/alta-disponibilidade-com-mysql-parte-1/


para esse novo funcionamento, não precisa alterar nada.
[14h16min30s] Suporte Desenvolvedor Daruma -> Luís Carlos: ah, desculpe
[14h16min45s] Suporte Desenvolvedor Daruma -> Luís Carlos: achei que já era a lib da nova NT...  (facepalm)
[14h16min59s] Suporte Desenvolvedor Daruma -> Luís Carlos: para conversar com o servidor AM, você precisará mudar as configurações em 2 locais
[14h17min03s] Suporte Desenvolvedor Daruma -> Luís Carlos: um deles é no painel do Invoicy
[14h17min16s] Suporte Desenvolvedor Daruma -> Luís Carlos: colocando lá o cadastro da sua empresa como UF = AM e Cidade = MANAUS
[14h17min57s] Suporte Desenvolvedor Daruma -> Luís Carlos: aí lá no GNE_FrameWork.xml, precisa alterar as seguintes tags:

cUF = 13
cMun = 1302603
cMunFG = 1302603
UF = AM
[14h18min33s] Suporte Desenvolvedor Daruma -> Luís Carlos: com essas configurações já conseguirá falar com o servidor do AM



ACBR - CEST 06-12
Postado 23 novembro
Amigos em relação à partilha do ICMS pelo que compreendi, sim a SEFAZ passará a validá-la a partir de 01/01/2016.

E em relação ao CEST, estou fazendo da seguinte forma no meu programa:

if (tpAmbiente = tpHomologacao) or (Now >= DataHoraInicial(StrToDate('01/01/16'))) then
begin
  Prod.CEST   := FieldByName('Produto_CEST').AsString;
  if (TemSTSemPartilha) and (Vazio(Prod.CEST)) then
    Prod.CEST := '0000000';
end;
Primeiramente testo se está em homologação senão apenas entra ali se a data for maior que 01/01/2016 às 0:00:01. Aí preenche o campo CEST de acordo com o cadastro do produto independentemente da tributação do mesmo, porém logo em seguida verifico se o produto tem ST e se o mesmo não tem partilha de ICMS, e caso o campo CEST esteja vazio eu o preencho com '0000000' para evitar o erro da falta do mesmo já que a princípio não será validado porém será exigido segundo o meu entender.

Onde a função TemSTSemPartilha verifica se o produto está no CST 10, 30, 60, 70 ou 90 (este último desde que a TAG vICMSST esteja preenchida) e não pode estar preenchida o campo ICMSPart ou no CSOSN 201, 202, 203 ou 900 (este último novamente deve estar com a TAG vICMSST preenchida) e o campo ICMSPart também não pode estar preenchido.

Att.

Rômulo Mayworm

"""    Geracao de Precos MARKUP  """
https://endeavor.org.br/markup

a - custo do produto: 10,00
b - despesas fixas..: 20%
c - margem de lucro.: 15%

d = 100-20-15 -> 65
e = 100/65 ----> 1,5384613846

pv = 10,00 * 1,5384613846 -> 15,38

#############################  GMAIL CONFIGURACAO PARA ENVIAR EMAIL PELO SISTEMA
-configuracao

1 Encaminhamento e POP/IMAP
2 Ativar IMAP
3 Salvar Alteracoes
4 - Encaminhamento e POP/IMAP
5 - Acesso IMAP:
(acesse o Gmail a partir de outros clientes usando IMAP)
Saiba mais
6 - Eu quero ativar o Acesso IMAP
7 - Outro
8 - O nome de usuário e a senha não estão funcionando? Alguns aplicativos exigem que você também ative o acesso para aplicativos menos seguros antes de configurar as conexões por Acesso IMAP/POP.
9 - Ativar




######################## para nao esquecer
encode('cp1252') 
######################################

#  SERGIL
#  PROBLEMAS COM SSH : site https://bbs.archlinux.org/viewtopic.php?id=165382
#  Por que nao foi gerada a chave antes
#  Foi Resolvido com o comando: ssh-keygen -A


sshd.service - OpenSSH Daemon
   Loaded: loaded (/usr/lib/systemd/system/sshd.service; enabled)
   Active: failed (Result: start-limit) since Thu 2016-04-07 10:34:24 BRT; 1s ago
  Process: 20742 ExecStart=/usr/sbin/sshd -D $SSHD_OPTS (code=exited, status=1/FAILURE)
  Process: 20739 ExecStartPre=/usr/sbin/sshd-gen-keys-start (code=exited, status=0/SUCCESS)
 Main PID: 20742 (code=exited, status=1/FAILURE)

Apr 07 10:34:23 linux-uzvo systemd[1]: sshd.service: main process exited, code=exited, status=1/FAILURE
Apr 07 10:34:23 linux-uzvo systemd[1]: Unit sshd.service entered failed state.
Apr 07 10:34:24 linux-uzvo systemd[1]: sshd.service holdoff time over, scheduling restart.
Apr 07 10:34:24 linux-uzvo systemd[1]: Stopping OpenSSH Daemon...
Apr 07 10:34:24 linux-uzvo systemd[1]: Starting OpenSSH Daemon...
Apr 07 10:34:24 linux-uzvo systemd[1]: sshd.service start request repeated too quickly, refusing to start.
Apr 07 10:34:24 linux-uzvo systemd[1]: Failed to start OpenSSH Daemon.
Apr 07 10:34:24 linux-uzvo systemd[1]: Unit sshd.service entered failed state.

#




export LANGUAGE=pt_BR.UTF-8
export LANG=pt_BR.UTF-8

	
Eu opto por usar Win 1252 em alguns dos meus softwares, sem ter nenhum problema de acentuação, inclusive em alguns que interagem com UTF-8 e 16. Economizo uma série de problemas evitando normalização desnecessária, e sei exatamente quanto preciso de armazenamento para as strings. Só vejo encoding dar problema quando o programador não entende do assunto. UTF-8 não é 100% livre de problemas também, isso é lenda. O mesmo caractere pode ser representado de forma combinante e não combinante, e quem não sabe o que está fazendo, volta e meia também se complica com UTF-8 puro. – Bacco 9/08/14 às 






######################################
#  S O C K E T E PYTHON e PYTHON WEB #
######################################
https://www.youtube.com/watch?v=SFERo-OjfdE
https://osantana.me/curso-de-python-e-django/#

#Python avancado
https://www.youtube.com/watch?v=sC6mqcLSkZo&index=2&list=PLfCKf0-awunOu2WyLe2pSD2fXUo795xRe

#Tutorial python3
http://www.tutorialspoint.com/python3/python_database_access.htm
wxpython phenix
pip install -U --pre -f http://wxpython.org/Phoenix/snapshot-builds/ wxPython_Phoenix

NFCe UF vazio erro, resolicao ATOBA 09-09-2016 Eliardo { o cadastro do emitente numero e comprlemento estava vazio }






################### Alterando a senha do mysql
Quem nunca Esqueceu a senha do root? QUANDO começei a trabalhar Há com MySql cheguei Ao Ponto de removedor o Serviço e Instalar Novamente pois havia esquecido a Senha do root.

Há Uma Maneira Mais Fácil parágrafo Change uma Senha de QUALQUÉR Usuário cadastrado no MySql. Basta Seguir Alguns Passos Rodando o MySql em modo de segurança .

1. Pare o Servidor MySQL

Primeiro TEMOS Que Parar o Servidor MySql. Para quem utiliza linux o Comando geralmente E:

01
sudo /etc/init.d/mysql stop
2. Iniciando Servidor MySQL em modo de segurança :

Como raiz do Sistema executar o Comando

01
mysqld_safe --skip-grant-tables
3. Logando Como raiz não MySql sem utilizar Senha:

01
mysql --user=root mysql
4. Alterando a Senha do root:

01
02
03
update user set Password=PASSWORD('nova-senha') where user='root';
flush privileges;
exit;
5.Finalizando:

Agora companheiro O Processo 'mysqld' ou pare o Serviço e inicie Novamente da forma normal.

01
02
sudo /etc/init.d/mysql stop 
sudo /etc/init.d/mysql start
Tente NÃO Esquecer SUA nova Senha.

Gostou? Compartilhe!

## MARKED

parece q quando coloco strip funciona e nao da erro, exemplo: str(valor).strip() referencia: conectar.py linha 712 em diante

senha modem internet dlink 500b TMAR#DLKT20060205 usuario DLKT20060205 senha

cor do texto
wx.SetItemTextColour (0, wx.RED)





 Realizei as seguintes configurações e passou a funcionar normalmente:

1º - Vá até o Painel de Controle do Microsoft Windows:  Menu Iniciar -> Painel de Controle;

2º - Escolha a Opção: Opções da Internet;

3º - Vá até a aba “Avançadas” e, na caixa “Configurações”, vá até as últimas opções (role a barra de rolagem até o final) e:
      a.)   Marque a opção: Usar SSL 2.0;
      b.)   Desmarque a opção: Usar SSL 3.0;
      c.)   Verifique se a opção “Usar TLS 1.0” está marcada. Caso não esteja, marque esta opção;
      d.)   Certifique-se de que as opções de TLS 1.1 e 1.2 estejam desmarcadas;
      e.)   Aplique as configurações e reinicie a aplicação. 

boleto cloud
token: api-key_eNw4KWIJHz-z31RKq837waQj6ph7I8uLkGdRUhxCrWM=
usuario: joselobinho@gmail.com
senha: 15j14m07l



lykos@linux:~/.ssh> ssh vendas@monfardini.dyndns.info "sudo cat /etc/sysconfig/network/ifcfg-p3p1"
Password: 
BOOTPROTO='static'
BROADCAST=''
ETHTOOL_OPTIONS=''
IPADDR='192.168.0.252/24'
MTU='1500'
NAME=''
NETMASK=''
NETWORK=''
REMOTE_IPADDR=''
STARTMODE='auto'
DHCLIENT_SET_DEFAULT_ROUTE='yes'
lykos@linux:~/.ssh> 

# Para utilizar sistema sem senha atraves do sudo
from subprocess import Popen, PIPE

sudo_password = 'mypass'
command = 'mount -t vboxsf myfolder /home/myuser/myfolder'.split()

p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE,  universal_newlines=True)
sudo_prompt = p.communicate(sudo_password + '\n')[1]


MariaDB [sei]> select ef_codigo,ef_fisico from estoque where ef_fisico<0;
+----------------+-----------+
| ef_codigo      | ef_fisico |
+----------------+-----------+
| 7890100000153  |   -1.0000 |
| 7890100000290  |  -60.0000 |
| 7890100000610  |   -2.0000 |
| 7890100000627  |   -9.0000 |
| 7890100000894  |   -1.0000 |
| 7890100002355  |   -2.0000 |
| 00000000000178 |   -0.0001 |
| 00000000000183 |   -1.0000 |
| 00000000000192 |   -1.0000 |
| 00000000000207 |   -1.0000 |
+----------------+-----------+


"""  10 cosisa para fazer depois de instalar o open suse """
https://elias.praciano.com/2016/05/10-coisas-para-fazer-depois-de-instalar-o-opensuse-leap-42-1/

carregar o whatsaap google-chrome --profile-directory=Default --app-id=infelompnbbancffeibkenmdbbmpoged
BACKUP
URL/HOST/IP: drive.caxiashost.com.br 
Usuário: joselobinho
Senha: 151407jml

corte cloud dados do carlos
carlosatacadaodemadeiras@gmail.com Senha: 78380662

def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')
TOKEN IBPT: fTj2S4YrzTmqNI87qEwT--c8fFkfOHOIHnNuJoSXak4a9NsCCY5JGpjRWwRHD8bY

TELA MAGNETICA
https://produto.mercadolivre.com.br/MLB-760653266-tela-mosquiteira-magnetica-para-janela-de-aco-100-x-120-m-_JM





PYNFe

git init
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/joselobinho/PyNFe2.7.git
git push -u origin master
…or push an existing repository from the command line
git remote add origin https://github.com/joselobinho/PyNFe2.7.git
git push -u origin master
…or import code from another repository
You can initialize this repository with code from a Subversion, Mercurial, or TFS project.

DIRETO

…or create a new repository on the command line
echo "# direto" >> README.md
git init
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/joselobinho/direto.git
git push -u origin master
…or push an existing repository from the command line
git remote add origin https://github.com/joselobinho/direto.git
git push -u origin master
