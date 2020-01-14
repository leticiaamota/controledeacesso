import applications.controledeacesso.controllers.publisher_web2py as pub
import datetime
import json

dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
step = datetime.timedelta(days=1)

def validar_agendamento(formAgendamento):
    data_inicial = formAgendamento.vars.dinicio
    data_final = formAgendamento.vars.dfim
    #Validação de data
    if formAgendamento.vars.dinicio > formAgendamento.vars.dfim:
        formAgendamento.errors.dinicio = 'Data inicial maior que Data final.'

    #Validação de hora
    if formAgendamento.vars.hrentrada > formAgendamento.vars.hrsaida:
        formAgendamento.errors.hrentrada = 'Horário de entrada maior que Horário saída.'

    #Validação de agendamentos previamente cadastrados
    while data_inicial <= data_final:
        if dias[data_inicial.weekday()] in formAgendamento.vars.periodicidade:
            #print (formAgendamento.vars.dinicio, dias[formAgendamento.vars.dinicio.weekday()])
            validation = db((db.agendamentos.sala == formAgendamento.vars.sala) & (db.agendamentos.dtagendamento == data_inicial) & (db.agendamentos.hrentrada == formAgendamento.vars.hrentrada)).count()
            if(validation>0):
                formAgendamento.errors.dtagendamento = 'Não é possível cadastrar novo agendamento para a sala %s na Data: %s (%s)/Horário: %s' %(formAgendamento.vars.sala,data_inicial,dias[data_inicial.weekday()],formAgendamento.vars.hrentrada)
            else:
                pass          
        data_inicial += step 

@auth.requires_login()
def cadastrar_agendamento():
    if session.auth.user.is_admin == True:
        pass
    else:
        redirect(URL('default','home'))

    formAgendamento = SQLFORM.factory(Field('funcionario', 'string', label='Funcionário', requires=IS_IN_DB(db(db.auth_user.is_admin == False), 'auth_user.email')),
    Field('sala', 'string', label='Sala', requires=IS_IN_DB(db, 'salas.codigo')),
    Field('dinicio', type='date', label='Data inicial', requires = IS_DATE(format=('%d-%m-%Y'))),
    Field('dfim', type='date', label='Data final', requires = IS_DATE(format=('%d-%m-%Y'))),
    Field('periodicidade', type='string', requires=IS_IN_SET(['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'],multiple=True),widget=SQLFORM.widgets.checkboxes.widget),
    Field('hrentrada', type='time', label='Horário de entrada', requires = IS_TIME()),
    Field('hrsaida', type='time', label='Horário de saída', requires = IS_TIME()))
    if formAgendamento.process(onvalidation=validar_agendamento).accepted:
        #Persistência de dados
        while formAgendamento.vars.dinicio <= formAgendamento.vars.dfim:
            if dias[formAgendamento.vars.dinicio.weekday()] in formAgendamento.vars.periodicidade:
                db.agendamentos.insert(funcionario=formAgendamento.vars.funcionario,sala=formAgendamento.vars.sala,dtagendamento=formAgendamento.vars.dinicio,hrentrada=formAgendamento.vars.hrentrada,hrsaida=formAgendamento.vars.hrsaida) 
                db.pontualidade.insert(pfuncionario=formAgendamento.vars.funcionario,psala=formAgendamento.vars.sala,pdtagendamento=formAgendamento.vars.dinicio,phrentrada=formAgendamento.vars.hrentrada,phrsaida=formAgendamento.vars.hrsaida,comparecimento=False,hrchegada=None,pontualidade=False)         
            formAgendamento.vars.dinicio += step

        session.flash = 'Novo agendamento cadastrado com sucesso.' 
        redirect(URL('registros','registro_de_agendamentos')) 
    elif formAgendamento.errors:
        response.flash = 'Erros no formulário!'
    else:
        response.flash = 'Preencha o formulário!'
    return dict(formAgendamento=formAgendamento)

@auth.requires_login()
def associar_tag_master():
    if session.auth.user.is_admin == True:
        pass
    else:
        redirect(URL('default','home'))

    associarTagMaster = SQLFORM.factory(Field('sala_controle', 'string', label="Selecione o código da sala:", requires=IS_IN_DB(db, Salas.codigo)))
    if associarTagMaster.process().accepted:
        topicoEntrada = db((db.salas.codigo == associarTagMaster.vars.sala_controle) & (db.salas.status == True)).select(db.salas.topicoEntrada)
        admin=db(db.auth_user.is_admin == True).select(db.auth_user.email)[0]
        print(topicoEntrada[0].topicoEntrada)
        print(admin.email)
        pub.publish_associar_tag_master(str(topicoEntrada[0].topicoEntrada),str(admin.email))
    elif associarTagMaster.errors:
        response.flash = 'Erros no formulário!'
    return dict(associarTagMaster=associarTagMaster)

@auth.requires_login()
def associar_tag_usuario():
    if session.auth.user.is_admin == True:
        pass
    else:
        redirect(URL('default','home'))

    associarTagUser = SQLFORM.factory(Field('usuario_controle', 'string', label="Selecione o usuário:", requires=IS_IN_DB(db(db.auth_user.is_admin == False), db.auth_user.email)), Field('sala_controle', 'string', label="Selecione o código da sala:", requires=IS_IN_DB(db, Salas.codigo)))
    if associarTagUser.process().accepted:
        topicoEntrada = db((db.salas.codigo == associarTagUser.vars.sala_controle) & (db.salas.status == True)).select(db.salas.topicoEntrada)
        print(topicoEntrada[0].topicoEntrada)
        print(associarTagUser.vars.usuario_controle)
        pub.publish_associar_tag_user(str(topicoEntrada[0].topicoEntrada),str(associarTagUser.vars.usuario_controle))
    elif associarTagUser.errors:
        response.flash = 'Erros no formulário!'
    return dict(associarTagUser=associarTagUser)

def validar_salas(formSalas):
    codigo = formSalas.vars.bloco + str(formSalas.vars.numero)
    validation = db(db.salas.codigo == codigo).count()
    if(validation>0):
        formSalas.errors.codigo = 'Sala já cadastrada'
    else:
        pass    

@auth.requires_login()
def cadastrar_sala():
    if session.auth.user.is_admin == True:
        pass
    else:
        redirect(URL('default','home'))

    formSalas = SQLFORM(Salas)
    if formSalas.process(onvalidation=validar_salas).accepted:
        codigo = formSalas.vars.bloco + str(formSalas.vars.numero)
        topicoEntrada = "topicoEntrada/" + codigo 
        topicoSaida = "topicoSaida/" + codigo 
        db((db.salas.bloco == formSalas.vars.bloco) & (db.salas.numero == formSalas.vars.numero)).update(codigo = codigo, topicoEntrada = topicoEntrada, topicoSaida = topicoSaida)
        session.flash = 'Sala %s cadastrada com sucesso.' % codigo
        redirect(URL('registros','registro_de_salas'))    
    elif formSalas.errors:
        response.flash = 'Erros no formulário!'
    else:
        if not response.flash:
            response.flash = 'Preencha o formulário!'

    return dict(formSalas=formSalas)

@auth.requires_login()
def cadastrar_usuario():
    if session.auth.user.is_admin == True:
        pass
    else:
        redirect(URL('default','home'))
        
    formUsuarios = SQLFORM(db.auth_user)
    if formUsuarios.process().accepted:
        session.flash = 'Novo usuário cadastrado: %s' % formUsuarios.vars.nome
        redirect(URL('registros','registro_de_usuarios')) 
    elif formUsuarios.errors:
        response.flash = 'Erros no formulário!'
    else:
        response.flash = 'Preencha o formulário!'
    return dict(formUsuarios=formUsuarios)