use contarec
l = "recebers.txt"
set printer to (l)
set device to print
a := 0

do while !eof()

    if rc_cancela #4 .and. rc_control#"1"
    
       ? rc_docnume+'|'+transform(rc_notafis,"999999")+'|'+transform(rc_valordc,"999999999.99")+'|'+transform(rc_saldodc,"999999999.99")+'|'+rc_usalanc+'|'+dtoc(rc_datalan)+'|'+dtoc(rc_dataven)+'|'+rc_codicli+'|'+rc_nomclie+'|'+rc_tipolan+'|'+rc_formalc+'|'+rc_cpfclie+'|'+rc_cnpjcli

    endif
   a = a + 1
   skip
   
enddo

set printer to
set device to screen
//browse()