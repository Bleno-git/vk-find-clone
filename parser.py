from ezsql import SQL
from PIL import Image
import numpy as np
import traceback
import requests
import random
import os

from config import *

from deepface import DeepFace

try:
	os.mkdir('faces')
except:
	pass

def one_query(*args, **kwargs):
	sql = SQL(mysql_host, mysql_login, mysql_pwd, mysql_db)
	try:
		r = sql.run(*args, **kwargs)
	except:
		sql.close()
		raise

	sql.close()
	return r

class Vk:
	def __init__(self):
		print('Vk initiated')
		self.tokens = vk_tokens
		self.vk_api_vers = '5.103'
	def api(self, method, **kwargs):
		return requests.post('https://api.vk.com/method/{}?v={}&access_token={}&lang=1'.format(method, self.vk_api_vers, random.choice(self.tokens)), data=kwargs, timeout=10).json()

Vk = Vk()


def get_encodings_from_link(profile_id, link, sex=None):
	try:
		content = requests.get(link, stream=True, timeout=10).raw

		img = Image.open(content)
		img = img.convert('RGB')

		img.save(f'faces/{sex}_{profile_id}.jpg')

		try:
			face = DeepFace.represent(img_path = f'faces/{sex}_{profile_id}.jpg', model_name = "Facenet512")

			one_query("INSERT INTO faces(vk_id, face, sex_from_vk) VALUES(%s, %s, %s)", profile_id, json.dumps(face), sex)
		except KeyboardInterrupt:
			exit()
		except:
			pass


		os.remove(f'faces/{sex}_{profile_id}.jpg')
			
	except KeyboardInterrupt:
		exit()
	except:
		raise

def get_range(i, m=1000):
	return ','.join(map(str, range(i,i+m)))


def parse_profile(link, profile_id, sex=None):
	try:
		try:
			encodings = get_encodings_from_link(profile_id, link, sex)
		except KeyboardInterrupt:
			exit()
		except:
			traceback.print_exc()
	except KeyboardInterrupt:
		exit()
	except:
		traceback.print_exc()

if __name__ == '__main__':
	max_id = one_query("SELECT ifnull(max(vk_id), 1) FROM faces")[0][0]
	for i in range(max_id, max_id+1000000000, 1000):

		users = Vk.api('users.get', user_ids=get_range(i), fields='photo_max_orig,sex')
		links = list([[item['photo_max_orig'], item['id'], item.get('sex', -1)] for item in users['response'] if 'photo_max_orig' in item and 'deactivated' not in item['photo_max_orig'] and 'camera_' not in item['photo_max_orig'] and item['first_name'] != 'DELETED'])

		for link, profile_id, sex in links:
			parse_profile(link, profile_id, sex)
			


