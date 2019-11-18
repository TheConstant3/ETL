#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# в данной программе были реализованы задачи basic и advanced
# из бонусов были выполнены два пункта: предусмотрена обработка большого количества данных (в программе использовались
# наиболее быстрые алгоритмы сортировки) и обработка некорректных данных без остановки программы с дальнейшим
# информированием пользователя об ошибках
# на выполнение программы было затрачено примерно 13 часов:
# - 3 часа на написание парсера csv, json файлов, к приведение их к одной размерности
# - 3 часа на написание алгоритма быстрой сортировки и парсера xml файлов
# - 5 часов на выполнение дополнительного задания и реализации записи ошибок
# - 2 часа рефакторинг кода
#
# программа обрабатывает все файлы формата csv, json и xml в директории Files, находящейся в директории проекта


import csv
import json
import xml.etree.ElementTree as ElementTree
from os import listdir
from os.path import isfile, join, dirname
import sorting


# определение директории с файлами для обработки
dirname = dirname(__file__)
path_to_files = join(dirname, 'Files//')
# создание списка всех файлов в указанной директории
files = [f for f in listdir(path_to_files) if isfile(join(path_to_files, f))]
files = [path_to_files + file for file in files]


# определение числа n (количество столбцов D*) по любому файлу csv
n = 0
for file_name in files:
    file_format = file_name.split('.')[1]
    if file_format == "csv":
        with open(file_name, "r") as f_obj:
            reader = csv.reader(f_obj)
            data_from_file = [row for row in reader]
            columns = data_from_file[0]
            n = len([column_d for column_d in columns if "D" in column_d])
            break


# функция получения данных из файла формата csv в виде списка
def get_from_csv(path):
    with open(path, "r") as csv_f_obj:
        csv_data = csv.reader(csv_f_obj)
        csv_data = [row for row in csv_data]
        return csv_data


# функция получения данных из файла формата json в виде списка
def get_from_json(path):
    with open(path) as json_f_obj:
        json_file = json.load(json_f_obj)['fields']
        keys = [key for key, value in json_file[0].items()]
        json_data = [keys]
        for field in json_file:
            values = [value for key, value in field.items()]
            json_data.append(values)
        return json_data


# функция получения данных из файла формата xml в виде списка
def get_from_xml(path):
    tree = ElementTree.parse(path)
    root = tree.getroot()
    # список хранящий данные из файла
    xml_data = []
    for index, group in enumerate(root.findall('objects')):
        # список хранящий заголовки
        objects_names = []
        # список хранящий соответствующие значения
        values = []
        # поиск всех объектов
        for xml_object in group.findall('object'):
            # запись имени объекта
            objects_names.append(xml_object.get('name'))
            for value in xml_object.findall('value'):
                # запись значения объекта
                values.append(value.text)
        # запись заголовков при нахождении первого тега objects
        if index == 0:
            xml_data.append(objects_names)
        xml_data.append(values)
    return xml_data


# функция обработки полученных данных
# для удаление лишних слобцов
# и упорядочивания оставшихся
def to_2n_columns(data):
    # массив хранящий индексы стобцов для удаления
    index_del = []
    # проверка числа в названии каждого заголовка
    for index, column in enumerate(data[0]):
        if int(column[1:]) > n:
            index_del.append(index)
    # сортировка индексов от большого к меньшему
    # для избежания ошибок из-за изменения индексов элементов
    # в списке обрабатываемых данных после каждого удаления
    index_del.sort(reverse=True)
    for index in index_del:
        for row in data:
            del row[index]
    # упорядочивание столбцов алгоритмом быстрой сортировки
    sorting.quick_sort_columns(data, 0, len(data[0]) - 1)
    return data[1:]


# список для хранения ошибок, возникших во время обработки
errors = []
# список для хранения всей обработанной информации
all_data = []
# обработка данных из имеющихся файлов
for file_name in files:
    # определение формата файла
    file_format = file_name.split('.')[1]
    # список для хранения данных из файла
    data_from_file = []
    # извлечение данных исходя из формата файла
    if file_format == "csv":
        data_from_file = get_from_csv(file_name)
    elif file_format == 'json':
        data_from_file = get_from_json(file_name)
    elif file_format == 'xml':
        data_from_file = get_from_xml(file_name)
    else:
        continue
    # запись обработанных данных
    normal_data = to_2n_columns(data_from_file)

    # проверка корректности данных
    # в столбцах D не должно быть пустых строк
    # в столбцах M должны быть только числа
    for i_r, row in enumerate(normal_data):
        for i, x in enumerate(row[n:]):
            if not str(x).isdigit():
                errors.append(u"Error in file {0}, field {1}. Element M{2} is not integer!".format(file_name,
                                                                                                   i_r + 1, i+1))
                normal_data[i_r][n + i] = 0
            else:
                normal_data[i_r][n + i] = int(x)
        for i, x in enumerate(row[:n]):
            if x == '':
                errors.append(u"Error in file {0}, field {1}. No data at D{2} element!".format(file_name,
                                                                                               i_r + 1, i+1))
    for row in normal_data:
        all_data.append(row)


# сортировка всех полученных данных по строкам
# алгоритмом быстрой сортировки
sorting.quick_sort_rows(all_data, 0, len(all_data) - 1)


# создание заголовков данных
headers = []
for i in range(n):
    header = "D{}".format(i+1)
    headers.append(header)
for i in range(n):
    header = "M{}".format(i+1)
    headers.append(header)
# запись заголовков в итоговый список
all_data.insert(0, headers)


# запись полученных данных после выполнения базого задания в файл
with open(path_to_files + "basic_results.tsv", "w") as f_output:
    tsv_output = csv.writer(f_output, delimiter='\t')
    for row in all_data:
        tsv_output.writerow(row)
    print("basic_results.tsv created!")


# ВЫПОЛНЕНИЕ ДОПОЛНИТЕЛЬНОГО ЗАДАНИЯ (ADVANCED)


# удаление заголовка
all_data.pop(0)
# словарь из пар: уникальный набор D1...Dn - индекс первой найденной строки с таким же набором
uniq_D = {}
# индекс анализируемой строки
index_row = 0
while index_row + 1 <= len(all_data):
    # набор D1...Dn текущей строки - ключ словаря
    key_set = str(all_data[index_row][:n])
    # получение индекса строки с данным ключом(набором D1...Dn)
    index_uniq = uniq_D.get(key_set)
    # если такого ключа не существует, то создаём его
    # и присваиваем ему индекс текущей строки списка all_data
    if index_uniq is None:
        uniq_D[key_set] = index_row
        # переход к следующей строке all_data
        index_row += 1
    # если строка с таким набором существует
    # то прибавляем к элементам M1...Mn первой найденной строки
    # соответствующие элементы текущей строки и удаляем её
    else:
        # запись строки с повторяющимся набором D1...Dn и её удаление
        non_uniq_row = all_data.pop(index_row)
        # прибавление элементов M1...Mn к уникальной строке
        for i in range(n):
            all_data[index_uniq][n + i] += non_uniq_row[n + i]


# запись заголовков в итоговый список
all_data.insert(0, headers)
# запись полученных данных после выполнения базого задания в файл
with open(path_to_files + "advanced_results.tsv", "w") as f_output:
    tsv_output = csv.writer(f_output, delimiter='\t')
    for row in all_data:
        tsv_output.writerow(row)
    print("advanced_results.tsv created!")


# информирование пользователя об ошибках
for error in errors:
    print(error)
