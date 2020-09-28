use produto
l = "produto.txt"
set printer to (l)
set device to print
a := 0

do while !eof()

   ? pd_codi+';'+pd_nome+';'+pd_cara+';'+pd_refe+';'+pd_atal+';'+pd_unid+';'+pd_nmgr+';'+pd_fant+";"+transform(pd_vend,"9999999.99")+"0;"+transform(pd_estf,"999999.9999")+";"+pd_mdun+";"+transform(pd_tpr6,"999999.9999")+";"+transform(pd_coms,"99.99")+";"+transform(pd_marg,"9999.999")+";"+transform(pd_pesb,"9999.999")+";"+transform(pd_pesl,"9999.999")+";"+pd_loca+";"+pd_intc+";"+transform(pd_tpr2,"9999999.99")+"0;"+transform(pd_tpr3,"9999999.99")+"0;"+transform(pd_tpr4,"9999999.99")+"0;"+transform(pd_tpr5,"9999999.99")+"0;"+pd_cmu5+";"+pd_cmu4+";"+pd_cmu3+";"+transform(pd_mrse,"99.99")+";"+transform(pd_pcus,"9999999.99")+"0"+";"+transform(pd_pcom,"9999999.99")+"0"+";"+transform(pd_cusm,"9999999.99")+"0"+";"+pd_cupf+";"+str(pd_icms)+";"+pd_clfs+";"+pd_stfs+";"+pd_cfop+";"+pd__ncm

   a = a + 1
   skip
   
enddo

set printer to
set device to screen
//browse()
