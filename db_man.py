import psycopg2
import sys

class PG_Connection(object):
	def __init__(self, host='', port='', dbname='', user='', password=''):
		self.host = self.checkDefault(host, 'localhost')
		self.port = self.checkDefault(port, '5432')
		self.dbname = dbname
		self.user = self.checkDefault(user, 'postgres')
		self.password = password
		self.conn = None	#connection object
		self.cursor = None	#cursor object
		
	def __del__(self):
		print 'destroying'
		self.close()
			
	def checkDefault(self, atrib, default):
		if atrib == '':
			return default
		else:
			return atrib
	
	def open(self):
		try:
			self.conn = psycopg2.connect(host=self.host, port=self.port, dbname=self.dbname, user=self.user, password=self.password)
			self.cursor = self.conn.cursor()
			success = True
		except Exception as e:
			print e
			success = False
		finally:
			if success:
				print 'CONECTADO'
			else:
				print 'NO CONECTADO'
			return success
		
	def close(self):
		if self.conn.closed == 0:
			self.conn.close()
			
	def getSelect(self, selectQuery, getOne=False):
		print self.cursor.mogrify(selectQuery)
		self.cursor.execute(selectQuery)
		if getOne:
			return self.cursor.fetchone()
		else:
			return self.cursor.fetchall()
			
			
#test
if __name__ == '__main__':
	if 'psycopg2' in sys.modules:

		db = PG_Connection(dbname='INDIGO', password='1')
		db.open()
		print db.getSelect('select id from biframewebentity')
	else:
		print 'module psycopg2 not found'