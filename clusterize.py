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

print("Подгрузили модули...")

def one_query(*args, **kwargs):
	sql = SQL(mysql_host, mysql_login, mysql_pwd, mysql_db)
	try:
		r = sql.run(*args, **kwargs)
	except:
		sql.close()
		raise

	sql.close()
	return r

# Загружаем все фото из бд и проводим кластеризацию

def create_test(name="durov.jpg"):
	test_face = DeepFace.represent(img_path = name, model_name = "Facenet512")
	test_face = preprocessing.normalize([test_face])[0]
	with open('test.pickle', 'wb') as file:
		pickle.dump(test_face, file)
	return test_face
def load_test():
	with open('test.pickle', 'rb') as file:
		test_face = pickle.load(file)
	return test_face

def create_model(faces):
	clf = KMeans(n_clusters=8)
	clf.fit(faces)

	with open('model.pickle', 'wb') as file:
		pickle.dump(clf, file)

	return clf

def load_model():
	with open('model.pickle', 'rb') as file:
		clf = pickle.load(file)
	return clf


faces = [[vk_id, preprocessing.normalize([json.loads(face)])[0]] for vk_id, face in one_query("SELECT vk_id, face FROM faces")]

create_model([item[1] for item in faces])

clf = load_model()

for vk_id, face in faces:
	cluster_id = clf.predict([face])[0]
	one_query("UPDATE faces SET cluster_id=%s WHERE vk_id=%s", cluster_id, vk_id)

