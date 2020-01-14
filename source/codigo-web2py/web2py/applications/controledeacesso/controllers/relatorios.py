import datetime
from datetime import date

@auth.requires_login()
def relatorio_de_pontualidade():
	fields=(db.pontualidade.pfuncionario, db.pontualidade.psala, db.pontualidade.pdtagendamento, db.pontualidade.phrentrada,db.pontualidade.phrsaida,db.pontualidade.comparecimento,db.pontualidade.hrchegada,db.pontualidade.pontualidade)
	default_sort_order=[~db.pontualidade.pdtagendamento,~db.pontualidade.phrentrada]
	
	if session.auth.user.is_admin == True:
		relatorios = SQLFORM.grid(query=db(db.pontualidade.pdtagendamento <= date.today()),fields=fields,orderby=default_sort_order,details=False,create=False,editable=False,deletable=False,csv=False,paginate=25)
	else:
		relatorios = SQLFORM.grid(query=db((db.pontualidade.pfuncionario == session.auth.user.email)&(db.pontualidade.pdtagendamento <= date.today())),fields=fields,orderby=default_sort_order,details=False,searchable=False,create=False,editable=False,deletable=False,csv=False,paginate=25)
	return dict(relatorios=relatorios)

@auth.requires_login()
def estatisticas_de_pontualidade():
	
	today = date.today()
	idx = (today.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
	sun = today - datetime.timedelta(7+idx) #ULTIMO DOMINGO
	sat = today - datetime.timedelta(7+idx-6) #ULTIMO SABADO

	if session.auth.user.is_admin == False:

		total_agendamentos = db((db.pontualidade.pfuncionario==session.auth.user.email)&(db.pontualidade.pdtagendamento <= date.today())).count()
		comparecimentos = db((db.pontualidade.pfuncionario==session.auth.user.email)&(db.pontualidade.pdtagendamento <= date.today())&(db.pontualidade.comparecimento==True)&(db.pontualidade.pontualidade==True)).count()
		atrasos = db((db.pontualidade.pfuncionario==session.auth.user.email)&(db.pontualidade.pdtagendamento <= date.today())&(db.pontualidade.comparecimento==True)&(db.pontualidade.pontualidade==False)).count()
		ausencias = db((db.pontualidade.pfuncionario==session.auth.user.email)&(db.pontualidade.pdtagendamento <= date.today())&(db.pontualidade.comparecimento==False)).count()

		if(total_agendamentos == 0):
			percentual_comparecimentos = 0
			percentual_atrasos = 0
			percentual_ausencias = 0
		else:
			percentual_comparecimentos = (comparecimentos/total_agendamentos)*100
			percentual_atrasos = (atrasos/total_agendamentos)*100
			percentual_ausencias = (ausencias/total_agendamentos)*100


		total_agendamentos_semanal = db((db.pontualidade.pfuncionario==session.auth.user.email)&(db.pontualidade.pdtagendamento >= sun )&(db.pontualidade.pdtagendamento <= sat)).count()
		comparecimentos_semanal = db((db.pontualidade.pfuncionario==session.auth.user.email)&(db.pontualidade.pdtagendamento >= sun )&(db.pontualidade.pdtagendamento <= sat)&(db.pontualidade.comparecimento==True)&(db.pontualidade.pontualidade==True)).count()
		atrasos_semanal = db((db.pontualidade.pfuncionario==session.auth.user.email)&(db.pontualidade.pdtagendamento >= sun )&(db.pontualidade.pdtagendamento <= sat)&(db.pontualidade.comparecimento==True)&(db.pontualidade.pontualidade==False)).count()
		ausencias_semanal = db((db.pontualidade.pfuncionario==session.auth.user.email)&(db.pontualidade.pdtagendamento >= sun )&(db.pontualidade.pdtagendamento <= sat)&(db.pontualidade.comparecimento==False)).count()

		if(total_agendamentos_semanal == 0):
			percentual_comparecimentos_semanal = 0
			percentual_atrasos_semanal = 0
			percentual_ausencias_semanal = 0
		else:
			percentual_comparecimentos_semanal = (comparecimentos_semanal/total_agendamentos_semanal)*100
			percentual_atrasos_semanal = (atrasos_semanal/total_agendamentos_semanal)*100
			percentual_ausencias_semanal = (ausencias_semanal/total_agendamentos_semanal)*100

		ultimos_agendamentos = db((db.pontualidade.pfuncionario == session.auth.user.email)&(db.pontualidade.pdtagendamento <= date.today())).select(db.pontualidade.pdtagendamento,db.pontualidade.phrentrada,db.pontualidade.hrchegada, limitby=(0,7))

	else:
		if request.vars.funcionario:
			total_agendamentos = db((db.pontualidade.pfuncionario==request.vars.funcionario)&(db.pontualidade.pdtagendamento <= date.today())).count()
			comparecimentos = db((db.pontualidade.pfuncionario==request.vars.funcionario)&(db.pontualidade.pdtagendamento <= date.today())&(db.pontualidade.comparecimento==True)&(db.pontualidade.pontualidade==True)).count()
			atrasos = db((db.pontualidade.pfuncionario==request.vars.funcionario)&(db.pontualidade.pdtagendamento <= date.today())&(db.pontualidade.comparecimento==True)&(db.pontualidade.pontualidade==False)).count()
			ausencias = db((db.pontualidade.pfuncionario==request.vars.funcionario)&(db.pontualidade.pdtagendamento <= date.today())&(db.pontualidade.comparecimento==False)).count()

			if(total_agendamentos == 0):
				percentual_comparecimentos = 0
				percentual_atrasos = 0
				percentual_ausencias = 0
			else:
				percentual_comparecimentos = (comparecimentos/total_agendamentos)*100
				percentual_atrasos = (atrasos/total_agendamentos)*100
				percentual_ausencias = (ausencias/total_agendamentos)*100

			total_agendamentos_semanal = db((db.pontualidade.pfuncionario==request.vars.funcionario)&(db.pontualidade.pdtagendamento >= sun )&(db.pontualidade.pdtagendamento <= sat)).count()
			comparecimentos_semanal = db((db.pontualidade.pfuncionario==request.vars.funcionario)&(db.pontualidade.pdtagendamento >= sun )&(db.pontualidade.pdtagendamento <= sat)&(db.pontualidade.comparecimento==True)&(db.pontualidade.pontualidade==True)).count()
			atrasos_semanal = db((db.pontualidade.pfuncionario==request.vars.funcionario)&(db.pontualidade.pdtagendamento >= sun )&(db.pontualidade.pdtagendamento <= sat)&(db.pontualidade.comparecimento==True)&(db.pontualidade.pontualidade==False)).count()
			ausencias_semanal = db((db.pontualidade.pfuncionario==request.vars.funcionario)&(db.pontualidade.pdtagendamento >= sun )&(db.pontualidade.pdtagendamento <= sat)&(db.pontualidade.comparecimento==False)).count()


			if(total_agendamentos_semanal == 0):
				percentual_comparecimentos_semanal = 0
				percentual_atrasos_semanal = 0
				percentual_ausencias_semanal = 0
			else:
				percentual_comparecimentos_semanal = (comparecimentos_semanal/total_agendamentos_semanal)*100
				percentual_atrasos_semanal = (atrasos_semanal/total_agendamentos_semanal)*100
				percentual_ausencias_semanal = (ausencias_semanal/total_agendamentos_semanal)*100

			ultimos_agendamentos = db((db.pontualidade.pfuncionario == request.vars.funcionario)&(db.pontualidade.pdtagendamento <= date.today())).select(db.pontualidade.pdtagendamento,db.pontualidade.phrentrada,db.pontualidade.hrchegada, limitby=(0,7))
		else:
			ultimos_agendamentos = None
			total_agendamentos=None
			percentual_comparecimentos=None
			percentual_atrasos=None
			percentual_ausencias=None
			total_agendamentos_semanal=None
			percentual_comparecimentos_semanal=None
			percentual_atrasos_semanal=None
			percentual_ausencias_semanal=None

	return dict(ultimos_agendamentos=ultimos_agendamentos,total_agendamentos=total_agendamentos,percentual_comparecimentos=percentual_comparecimentos,percentual_atrasos=percentual_atrasos,percentual_ausencias=percentual_ausencias,total_agendamentos_semanal=total_agendamentos_semanal, percentual_comparecimentos_semanal=percentual_comparecimentos_semanal, percentual_atrasos_semanal=percentual_atrasos_semanal,percentual_ausencias_semanal=percentual_ausencias_semanal)