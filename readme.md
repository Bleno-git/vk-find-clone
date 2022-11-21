Задача данного проекта: собрать лица пользователей из соц. сети ВК, найти точки лица с помощью Facenet и добиться поиска по базе с несколькими десятками миллионов лиц за срок не более одной секунды.

Примерная скорость нахождения дистанции между двумя векторами с 512-ью координатами: 47000 в секунду. То есть, если в нашей базе находится, например, 94000 лиц, то поиск по такой базе займёт около двух секунд, чего недостаточно для выполнения условий задачи.

Для оптимизации поиска воспользуемся идеей работы множеств: разобьём всю базу лиц на блоки (кластеры) и во время поиска будем искать не по всей базе, а только по кластеру.
Для того, чтобы разбивать базу на кластеры и определять кластер, к которому принадлежит данное лицо, воспользуемся машинным обучением, а именно кластеризацией в модуле SKLearn.

При поиске нам будет достаточно определить кластер лица, а потом обычным "перебором" найти евклидовы расстояния между входным лицом и каждым лицом из кластера, вернуть 10 лиц с минимальной дистанцией.

Поиск будет работать по следующему алгоритму:
1) Определяем кластер, к которому принадлежит лицо.
2) Достаём из базы все лица этого кластера.
3) Ищем все расстояния между входным лицом и лицами в кластере.
4) Возвращаем 10 лиц с минимальным расстоянием до данного.

При такой конфигурации можно добиться поиска с временем ожидания не более одной секунды и с масштабируемостью до базы данных в десятки миллионов лиц.

Подготовка выглядит так:
1) Парсим и обрабатываем фото профилей из вк
2) Определяем кластер лица по уже обученной модели и добавляем лицо в базу вместе с ссылкой на кластер.
3) Когда в одном из кластеров становится более 47000 лиц (то есть поиск по этому кластеру будет длиться более 1 секунды), переобучаем модель и перераспределяем все лица на новые кластеры (не забывая увеличить кол-во кластеров).

Для парсинга запускаем скрипт search.py:
python search.py

Для кластеризации и сохранения в базе запускаем скрипт clusterize.py:
python clusterize.py

Для поиска запускаем скрипт search.py:
python search.py

== Установка и настройка

# Устанавливаем модули
pip install -r .\requirements.txt

# Импортируем структуру базы данных (предварительно создав на сервере пустую базу данных с именем vk_db)
mysql -uroot -p vk_db < dump.sql

# В файле config.py указываем логин, пароль, адрес, название базы данных для MySQL
# В файле config.py в переменную vk_tokens добавляем несколько токенов вк, у которых есть доступ к получению информации о пользователях. Можно взять из приложений, которые можно создать здесь: https://vk.com/apps?act=manage

Альтернативно можно установить Tensorflow с поддержкой GPU (для ускорения процесса обработки фото):
https://www.tensorflow.org/install/gpu

