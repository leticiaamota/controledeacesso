@auth.requires_login()
def registro_de_salas():
	fields=(db.salas.codigo, db.salas.descricao, db.salas.topicoEntrada, db.salas.topicoSaida)
	default_sort_order=[db.salas.codigo,db.salas.status]
	if session.auth.user.is_admin == True:
		salas = SQLFORM.grid(query=db(db.salas.status == True),fields=fields,orderby=default_sort_order,searchable=False,details=False,deletable=False,paginate=25,csv=False)
	else:
		redirect(URL('default','home')) 
	return dict(salas=salas)

@auth.requires_login()
def registro_de_usuarios():
	fields=(db.auth_user.first_name, db.auth_user.last_name, db.auth_user.email, db.auth_user.password, db.auth_user.telefone, db.auth_user.funcao, db.auth_user.tag)
	default_sort_order=[db.auth_user.first_name]
	if session.auth.user.is_admin == True:
		usuarios = SQLFORM.grid(query=db(db.auth_user.is_admin == False,db.auth_user.status == True),fields=fields,orderby=default_sort_order,searchable=False,deletable=False,details=False,paginate=25,csv=False)
	else:
		redirect(URL('default','home')) 
	return dict(usuarios=usuarios)

@auth.requires_login()
def registro_de_agendamentos():
	fields=(db.agendamentos.funcionario, db.agendamentos.sala, db.agendamentos.dtagendamento, db.agendamentos.hrentrada, db.agendamentos.hrsaida)
	default_sort_order=[~db.agendamentos.dtagendamento]
	
	if session.auth.user.is_admin == True:
		agendamentos = SQLFORM.grid(query=db.agendamentos,fields=fields,orderby=default_sort_order,searchable=False,details=False,paginate=25,csv=False)
	else:
		agendamentos = SQLFORM.grid(query=db(db.agendamentos.funcionario == session.auth.user.email),fields=fields,orderby=default_sort_order,searchable=False,details=False,paginate=25,csv=False,deletable=False,editable=False,create=False)
	return dict(agendamentos=agendamentos)