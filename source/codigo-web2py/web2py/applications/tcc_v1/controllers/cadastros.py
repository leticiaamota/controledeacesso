import applications.tcc_v1.controllers.publisher_web2py as pub

def cadastrar_agendamento():
    return dict()

def associar_tag_master():
    associarTagMaster = SQLFORM.factory(Field('sala_controle', 'string', label="Selecione o código da sala:", requires=IS_IN_DB(db, Salas.codigo)))
    if associarTagMaster.process().accepted:
        topicoEntrada = db((db.salas.codigo == associarTagMaster.vars.sala_controle) & (db.salas.status == True)).select(db.salas.topicoEntrada)
        print(topicoEntrada[0].topicoEntrada)
        pub.publish_associar_tag_master(str(topicoEntrada[0].topicoEntrada))
    elif associarTagMaster.errors:
        response.flash = 'Erros no formulário!'
    return dict(associarTagMaster=associarTagMaster)

def associar_tag_usuario():
    associarTagUser = SQLFORM.factory(Field('usuario_controle', 'string', label="Selecione o usuário:", requires=IS_IN_DB(db, Usuarios.email)), Field('sala_controle', 'string', label="Selecione o código da sala:", requires=IS_IN_DB(db, Salas.codigo)))
    if associarTagUser.process().accepted:
        topicoEntrada = db((db.salas.codigo == associarTagUser.vars.sala_controle) & (db.salas.status == True)).select(db.salas.topicoEntrada)
        print(topicoEntrada[0].topicoEntrada)
        print(associarTagUser.vars.usuario_controle)
        pub.publish_associar_tag_user(str(topicoEntrada[0].topicoEntrada),str(associarTagUser.vars.usuario_controle))
    elif associarTagUser.errors:
        response.flash = 'Erros no formulário!'
    return dict(associarTagUser=associarTagUser)

def cadastrar_sala():
    formSalas = SQLFORM(Salas)
    if formSalas.process().accepted:
        codigo = formSalas.vars.bloco + str(formSalas.vars.numero)
        topicoEntrada = "topicoEntrada/" + codigo 
        topicoSaida = "topicoSaida/" + codigo 
        db((db.salas.bloco == formSalas.vars.bloco) & (db.salas.numero == formSalas.vars.numero)).update(codigo = codigo, topicoEntrada = topicoEntrada, topicoSaida = topicoSaida)
        session.flash = 'Sala %s cadastrada com sucesso.' % codigo
        redirect(URL('cadastrar_sala'))    
    elif formSalas.errors:
        response.flash = 'Erros no formulário!'
    else:
        if not response.flash:
            response.flash = 'Preencha o formulário!'

    return dict(formSalas=formSalas)

def cadastrar_usuario():
    formUsuarios = SQLFORM(Usuarios)
    if formUsuarios.process().accepted:
        session.flash = 'Novo usuário cadastrado: %s' % formUsuarios.vars.nome
        redirect(URL('cadastrar_usuario'))
    elif formUsuarios.errors:
        response.flash = 'Erros no formulário!'
    else:
        response.flash = 'Preencha o formulário!'
    return dict(formUsuarios=formUsuarios)
