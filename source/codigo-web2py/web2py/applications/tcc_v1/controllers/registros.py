def registro_de_salas():
    salas = SQLFORM.grid(db(Salas))
    return dict(salas=salas)

def registro_de_usuarios():
    #usuarios = db(Usuarios).select()
    usuarios = SQLFORM.grid(db(Usuarios))
    return dict(usuarios=usuarios)

def registro_de_agendamentos():
	return dict()
