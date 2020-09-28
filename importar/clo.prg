use cliente
l = "clientes.txt"
set printer to (l)
set device to print
a := 0

do while !eof()

   ? cl_nome+'|'+cl_fantas+'|'+cl_docume+'|'+cl_endere+'|'+cl_bairro+'|'+cl_cidade+'|'+cl_estado+'|'+cl_cep+'|'+cl_cdibge+'|'+cl_compl1+'|'+cl_compl2+'|'+cl_email+'|'+cl_telef1+'|'+cl_telef2+'|'+cl_telef3+'|'+cl_email1+'|'+cl_email2+'|'+cl_facebo+'|'+cl_twiter+'|'+transform(cl_limite,'99999999.99')+'|'+cl_tabela+"|"+cl_codigo+"|"+cl_iestad

   a = a + 1
   skip
   
enddo

set printer to
set device to screen
//browse()