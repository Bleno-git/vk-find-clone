import pymysql
import time

from decimal import Decimal

class SQL:
	def __init__(self, host, login, password, db_name, get_pid=False):
		self.pid = None
		self.connect(host, login, password, db_name, get_pid)
	def connect(self, host, login, password, db_name, get_pid=False):
		self.connection = (host, login, password, db_name, get_pid)

		self.conn = pymysql.connect(**{'host' : host, 'user' : login, 'password' : password, 'db' : db_name})

		self.cursor = self.conn.cursor()
		if get_pid:
			self.pid = self.run("SELECT connection_id();")[0][0]
		self.created = time.time()
	def kill_me(self):
		if self.pid:
			self.run("KILL %S" % self.pid)
		self.close()
	def run(self, query, *params):
		stime = time.time()
		try:
			self.cursor.execute(query, [*params])
			res = []
			for row in self.cursor:
				#Decimal переводим в float
				row = list(row)
				for i in range(len(row)):
					if type(row[i]) == Decimal:
						row[i] = float(row[i])
				#
				res.append(row)

			speed = time.time() - stime
			try:
				self.conn.commit()
			except:
				pass

			return res
		except Exception as e:
			try:
				self.conn.commit()
			except:
				pass
			raise e

		return res
	def c(self):
		self.conn.commit()
	def json(self, query, *params):
		try:
			self.cursor.execute(query, [*params])
			try:
				names = [x[0] for x in self.cursor.description]
			except:
				names = []

			res = []
			for row in self.cursor:
				row = list(row)
				for i in range(len(row)):
					if type(row[i]) == Decimal:
						row[i] = float(row[i])
				res.append(row)

			self.c()


			return list([dict(zip(names, item)) for item in res])
		except Exception as e:
			self.c()
			raise e
	def insert(self, table_name, keys, values, ignore=False):
		# 
		params = []
		for item in values:
			params += item
		if ignore:
			return self.run("INSERT IGNORE INTO {}({}) VALUES {}".format(table_name, ','.join(keys), ','.join([f"({','.join(['%s']*len(keys))})"]*len(values)) ), *params)
		else:
			return self.run("INSERT INTO {}({}) VALUES {}".format(table_name, ','.join(keys), ','.join([f"({','.join(['%s']*len(keys))})"]*len(values)) ), *params)
	
	def reset(self):
		self.cursor.close()
		self.cursor = self.conn.cursor(buffered=True)
	def close(self):
		self.cursor.close()
		self.conn.close()
