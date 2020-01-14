import json
import sqlite3
import datetime
from datetime import date,timedelta
import time

# SQLite DB Name ------ ALTERAR CAMINHO ABSOLUTO DO BD UTILIZADO
DB_Name =  "C:\\Users\\leticia-mota\\Desktop\\access-control\\source\\codigo-web2py\\web2py\\applications\\controledeacesso\\databases\\storage.sqlite"

#===============================================================
# Database Manager Class

class DatabaseManager():
	def __init__(self):
		self.conn = sqlite3.connect(DB_Name)
		self.conn.execute('pragma foreign_keys = on')
		self.conn.commit()
		self.cur = self.conn.cursor()
		
	def add_del_update_db_record(self, sql_query, args=()):
		self.cur.execute(sql_query, args)
		self.conn.commit()
		return
		 
	def select_record(self,sql_query, args=()):
		self.cur.execute(sql_query,args)
		registro = self.cur.fetchone()[0]
		return registro
		
	def select_agendamento(self,sql_query,args=()):
		self.cur.execute(sql_query,args)
		usuario,email,sala,dtagendamento,hrentrada,hrsaida = self.cur.fetchone()
		return usuario,email,sala,dtagendamento,hrentrada,hrsaida
		 
	def update_tag_user(self,sql_query, args=()):
		self.cur.execute(sql_query,args)
		self.conn.commit()
		if(self.cur.rowcount==1):
			status = True
		else:
			status = False
		return status
	
	def __del__(self):
		self.cur.close()
		self.conn.close()

#===============================================================
#	RECEBE ID DA TAG - BUSCA AGENDAMENTO EM SALA/DATA/HORA NO BD
def validar_agendamento(Topic, jsonData):
	dbObj = DatabaseManager()
	
	#Separação de infos contidas em tópico
	infoTopico = Topic.split('/')
	
	#Configura a mensagem json recebida
	mensagemPython = json.loads(jsonData)
	
	#Variaveis para consulta
	sala = infoTopico[1]
	data_ag = date.today()
	tag = mensagemPython['Tag']
	hrchegada = datetime.datetime.now().strftime("%H:%M:00")
	
	admin_tag=dbObj.select_record("select tag from auth_user where is_admin == 'T'")

	if(admin_tag == tag):
		#intervalo de acesso para administrador (hora_atual + 10 minutos)
		horaadm = (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime("%H:%M:00")
		usuario = 'Admin'
		hrsaida = horaadm

	else:
		#chama a funcao de busca do bd
		try:
			usuario,email,sala,dtagendamento,hrentrada,hrsaida = dbObj.select_agendamento("select u.first_name, a.funcionario, a.sala, a.dtagendamento, a.hrentrada, a.hrsaida from agendamentos as a join auth_user as u on a.funcionario = u.email where a.sala = (?) and a.dtagendamento = (?) and u.tag = (?) and ((?) between a.hrentrada and a.hrsaida)",[sala,data_ag,tag,hrchegada])			
			try:
				tolerancia=(datetime.datetime.strptime(hrentrada,'%H:%M:%S') + datetime.timedelta(minutes=15)).strftime("%H:%M:00")
				
				if(hrchegada > tolerancia):
					pontualidade = 'F'
				else:
					pontualidade = 'T'

				print(usuario,email,sala,dtagendamento,hrentrada,hrsaida, hrchegada, pontualidade)

				dbObj.add_del_update_db_record("update pontualidade set comparecimento = 'T', hrchegada = (?), pontualidade = (?) where pfuncionario = (?) and psala = (?) and pdtagendamento = (?) and phrentrada = (?)",[hrchegada,pontualidade,email,sala,dtagendamento,hrentrada])

				#dbObj.add_del_update_db_record("insert into pontualidade ('pfuncionario','psala','pdtagendamento','phrentrada','phrsaida','comparecimento','hrchegada','pontualidade') values ((?),(?),(?),(?),(?),'T',(?),(?))",[email,sala,dtagendamento,hrentrada,hrsaida,hrchegada,pontualidade])
				

			except TypeError:
				print("Erro ao inserir dados de pontualidade.")

		except TypeError:
			print("Nenhum agendamento encontrado ---- Validar Agendamento DAL")
			return None,None

		
	del dbObj
	return usuario,hrsaida
	
#===============================================================
#	ASSOCIAR TAG USUARIO
def associar_tag(Topic, jsonData):
	dbObj = DatabaseManager()
	#configura a mensagem json recebida
	mensagemPython = json.loads(jsonData)
	tag = mensagemPython['Tag']
	email = mensagemPython['Email']
	
	number = dbObj.select_record("select count(*) from auth_user where tag = (?)",[tag])

	if(number >= 1):
		print("Tag já associada.")
		status=False
	else:
		#chama a funcao de update do bd
		try:
			status = dbObj.update_tag_user("update auth_user set tag = (?) where Email = (?)",[tag,email])
		except TypeError:
			print("ERROR - Associar Tag DAL")
			status = False
	
	del dbObj
	return status