from sklearn import preprocessing
from ezsql import SQL
from PIL import Image
import numpy as np
import traceback
import threading
import random
import pickle
import glob
import json
import time
import os

from config import *

from sklearn.cluster import KMeans
import numpy as np

from deepface import DeepFace

print("Модули подгрузили...")

def one_query(*args, **kwargs):
	sql = SQL(mysql_host, mysql_login, mysql_pwd, mysql_db)
	try:
		r = sql.run(*args, **kwargs)
	except:
		sql.close()
		raise

	sql.close()
	return r

def dist(a,b):
	return np.sum(np.power([a]-b, 2), axis=1)[0]

def create_test(fn='durov.jpg'):
	test_face = DeepFace.represent(img_path = fn, model_name = "Facenet512")
	test_face = preprocessing.normalize([test_face])[0]
	with open('test.pickle', 'wb') as file:
		pickle.dump(test_face, file)
	return test_face
def load_test():
	with open('test.pickle', 'rb') as file:
		test_face = pickle.load(file)
	return test_face

def load_model():
	with open('model.pickle', 'rb') as file:
		clf = pickle.load(file)
	return clf


if __name__ == '__main__':
	test_face = create_test(input("Введите путь до картинки с тестом: "))
	test_face = load_test()
	clf = load_model()
	cluster_id = clf.predict([test_face])[0]
	print(f"Данное лицо относится к {cluster_id} кластеру.")

	# Загружаем все фото из бд и проводим кластеризацию
	faces = [[vk_id, preprocessing.normalize([json.loads(face)])[0]] for vk_id, face in one_query("SELECT vk_id, face FROM faces WHERE cluster_id=%s", cluster_id)]
	print("Загрузили лица из базы и нормализовали")


	res = {}

	stime = time.time()
	for vk_id, face in faces:
		d = dist(np.array(face), np.array(test_face))
		res[vk_id] = d
	for ID, similarity in sorted(res.items(), key=lambda x: x[1], reverse=False)[:10]:
		print(f"Профиль https://vk.com/id{ID} похож на данный профиль на {round((1-similarity)*100)}%")

	print(f"Поиск занял {time.time()-stime} с.")

