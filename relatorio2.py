#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Inicio: 01-08-2018 16:06 Jose de almeida lobinho
import datetime

from conectar import login,dialogos,relatorios,gerenciador,formasPagamentos,truncagem,listaemails,diretorios,menssagem,numeracao
from decimal import *
from relatorio import modelo
from decimal   import Decimal

from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep,Color, black, blue, red, green, yellow, orange, magenta, violet, pink, brown,HexColor
from reportlab.lib.units import inch
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart

alertas = dialogos()
rls  = relatorios()
mdl  = modelo()
mens = menssagem()

class RelatorioControleContaCorrente:

    def relatorioContaCorrente(self, parent, id_relatorio, data_inicial, data_final, filial, dados, informacao1, informacao2 ):

        def cabccnf(_separa):

            """ Cabecalho """
            pag = str(pg).zfill(3)
            _rs = "EXTRATO CONTA"
            if id_relatorio == '90':    _rs = "SALDOS DE CONTAS"
            rls.cabecalhopadrao(cv,ImageReader,dh,pag, filial,_rs,2)
            cv.setFillColor(HexColor('0x636363'))

            """ Titulo de Cabecalho """
            cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12=''
            _rl = "DO EXTRATO DA CONTA CORRENTE"
            if id_relatorio == '90':    _rl = "SALDOS DE CONTAS"
            rel = u'Usuário: '+ login.usalogin + u"  PERÌODO: "+ data_final +" A "+ data_final +(" "*10)+ filial +u"  { RELATORIO "+ _rl +"  [ "+ informacao1[9:] +" ]  }"

            if id_relatorio == "90":

                cb1 = u"200|540||#7F7F7F"
                cb2 = u"630|540||#7F7F7F"
            else:

                cb1 = u"22|540|ORDEM  Emissão|#7F7F7F"
                cb2 = u"180|540|Histórico de lançamentos|#7F7F7F"
                cb3 = u"550|540|Saldo anterior|"
                cb4 = u"615|540|Crédito|"
                cb5 = u"680|540|Dédito|"
                cb6 = u"745|540|Saldo atual|"

            if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,2)
            else:

                if id_relatorio == "90":

                    cv.line((float(cb1.split('|')[0])-2), float(ccampo), (float(cb1.split('|')[0])-2), float(lcampo))
                    cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
                    #cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
                    #cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
                else:

                    cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
                    cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
                    cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
                    cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
                    cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
                cv.line(20,float(lcampo),820,float(lcampo))

        dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
        pg  = 1

        nomeArquivo = diretorios.usPasta+"atualizadas_"+login.usalogin.lower()+".pdf"

        cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))

        lcampo = 515
        ccampo = 525
        linhas = 1
        cabccnf(False)

        if id_relatorio == '90':    nregistro = len( dados )
        else:   nregistro = dados.GetItemCount()
        saldo_final = Decimal('0.00')

        rd1 = '22|35|110|(Relatorio:Controle de conta corrente )  [ '+ informacao2+' ]|'
        _mensagem = mens.showmsg("Relatótiro Controle de conta corrente...\n\nAguarde...")

        for r in range( nregistro ):

            if id_relatorio == '90':

                if linhas == 1:

                    cv.setFont('Helvetica-Bold', 8)
                    cv.setFillColor(HexColor('#000000'))
                    cv.drawRightString(290,  float(lcampo), u'Número do banco' )
                    cv.drawRightString(340,  float(lcampo), u'Agência' )
                    cv.drawRightString(460,  float(lcampo), u'Número conta corrente' )
                    cv.drawRightString(600,  float(lcampo), u'Saldo' )
                    linhas +=1
                    lcampo -= 10

                cv.setFont('Helvetica', 9)
                cv.drawRightString(290,  float(lcampo), dados[r].split('|')[0] )
                cv.drawRightString(340,  float(lcampo), dados[r].split('|')[1] )
                cv.drawRightString(460,  float(lcampo), dados[r].split('|')[2] )

                if Decimal( dados[r].split('|')[3].replace(',','') ) < 0:   cv.setFillColor(HexColor('#B82222'))
                elif Decimal( dados[r].split('|')[3].replace(',','') ): cv.setFillColor(HexColor('#101083'))

                cv.drawRightString(600,  float(lcampo), dados[r].split('|')[3] )
                cv.setFillColor(HexColor('#BFBFBF'))
                cv.drawString(290,  float(lcampo -2 ), ('.'*124) )
                cv.setFillColor(HexColor('#000000'))
                saldo_final += Decimal( dados[r].split('|')[3].replace(',','') )

            else:
                cv.setFont('Helvetica', 9)
                cv.drawString(22,  float(lcampo), dados.GetItem( r, 0).GetText()+'  '+dados.GetItem( r, 1).GetText() )
                if len(dados.GetItem( r, 2).GetText()) > 60:    cv.setFont('Helvetica', 6)
                cv.drawString(180, float(lcampo), dados.GetItem( r, 2).GetText())
                cv.setFont('Helvetica', 9)
                if dados.GetItem( r, 3).GetText() and Decimal( str( dados.GetItem( r, 3).GetText().replace(',','') ) ) < 0:
                    cv.setFont('Helvetica-Bold', 8)
                    cv.setFillColor(HexColor('#E90808'))
                else:   cv.setFillColor(HexColor('#0F0F71'))
                cv.drawRightString(610, float(lcampo), dados.GetItem( r, 3).GetText() )

                cv.setFont('Helvetica', 9)
                cv.setFillColor(HexColor('0x000000'))
                cv.drawRightString(675, float(lcampo), dados.GetItem( r, 4).GetText() )
                cv.drawRightString(740, float(lcampo), dados.GetItem( r, 5).GetText() )

                if dados.GetItem( r, 6).GetText() and Decimal( str( dados.GetItem( r, 6).GetText().replace(',','') ) ) < 0:
                    cv.setFont('Helvetica-Bold', 8)
                    cv.setFillColor(HexColor('#E90808'))
                else:   cv.setFillColor(HexColor('#0F0F71'))

                cv.drawRightString(817, float(lcampo), dados.GetItem( r, 6).GetText() )
                cv.line(20,( lcampo -2 ),820,( lcampo -2 ))
                cv.setFillColor(HexColor('0x000000'))

            linhas +=1
            lcampo -= 10

            if linhas >= 48:

                cabccnf(True)
                mdl.rodape(cv,rd1,'','','','','','','','',6)

                pg +=1
                cv.addPageLabel(pg)
                cv.showPage()
                linhas = 1
                lcampo = 515
                ccampo = 525

                cabccnf(False)

        if id_relatorio == '90':

            if saldo_final < 0: cv.setFillColor(HexColor('#E90808'))
            elif saldo_final: cv.setFillColor(HexColor('#101083'))

            cv.drawString(700, float(lcampo + 20 ), 'Saldo final:' )
            cv.drawRightString(817, float(lcampo + 20 ), format( saldo_final, ',' ) )
            cv.setFillColor(HexColor('0x000000'))

        cabccnf(True)
        mdl.rodape(cv,rd1,'','','','','','','','',6)
        cv.save()

        del _mensagem

        gerenciador.TIPORL = ''
        gerenciador.Anexar = nomeArquivo
        gerenciador.imprimir = True
        gerenciador.Filial   = filial

        ger_frame=gerenciador(parent=parent,id=-1)
        ger_frame.Centre()
        ger_frame.Show()
