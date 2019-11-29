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


# На реорганизацию кода было затрачено около 8 часов
# Дополнительно исправлен способ решения задачи advanced:
# Исключено удаление повторяющихся строк из списка, так как эта операция могла замедлять работу программы при большом
# количестве данных. Вместо этого использовался словарь, хранящий индексы повторяющихся строк. Каждая строка с первым
# индексом из словаря хранила суммированные значения и в дальнейшем записывалась в файл.


import csv
import json
import xml.etree.ElementTree as ElementTree
from os import listdir
from os.path import isfile, join, dirname
import sorting


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


# функция удаления лишних столбцов
def to_2n_columns(data, n):
    # массив хранящий индексы стобцов для удаления
    index_del = []
    # проверка числа в названии каждого заголовка
    for index, name_column in enumerate(data[0]):
        if int(name_column[1:]) > n:
            index_del.append(index)
    # сортировка индексов от большого к меньшему
    # для избежания ошибок из-за изменения индексов элементов
    # в списке обрабатываемых данных после каждого удаления
    index_del.sort(reverse=True)
    for index in index_del:
        for row in data:
            del row[index]
    return data


# функция получения списка файлов для обработки
def get_list_of_files():
    # определение директории текущего модуля
    dir_name = dirname(__file__)
    # определение пути к директории с файлами для обработки
    path_to_files = join(dir_name, 'Files\\')
    # создание списка всех файлов в указанной директории
    files = [f for f in listdir(path_to_files) if isfile(join(path_to_files, f))]
    files = [path_to_files + file for file in files]
    return files


# функция получения количества столбцов Dn
def get_count_of_d_columns(files):
    # количество столбцов D*
    n = 0
    # определение числа n по первому найденному файлу с подходящим форматом
    for file_name in files:
        file_format = file_name.split('.')[1]
        # извлечение данных исходя из формата файла
        if file_format == "csv":
            data_from_file = get_from_csv(file_name)
        elif file_format == 'json':
            data_from_file = get_from_json(file_name)
        elif file_format == 'xml':
            data_from_file = get_from_xml(file_name)
        else:
            continue
        # получение названий столбцов и определение количества столбцов D*
        columns_names = data_from_file[0]
        n = len([column_d for column_d in columns_names if "D" in column_d])
        break
    return n


# функция проверки данных на наличие ошибок
def check_errors(n, data, file_name):
    # список для хранения найденных ошибок
    errors = []
    # проверка корректности данных
    # в столбцах D не должно быть пустых строк
    # в столбцах M должны быть только числа
    for i_row, row in enumerate(data):
        for i_elem, elem in enumerate(row[:n]):
            if elem == '':
                data[i_row][i_elem] = '_'
                errors.append(u"Error in file {0}, field {1}. No data at D{2} element!".format(file_name,
                                                                                               i_row + 1,
                                                                                               i_elem + 1))
        for i_elem, elem in enumerate(row[n:]):
            if str(elem).isdigit():
                data[i_row][n + i_elem] = int(elem)
            else:
                errors.append(u"Error in file {0}, field {1}. Element M{2} is not integer!".format(file_name,
                                                                                                   i_row + 1,
                                                                                                   i_elem + 1))
                data[i_row][n + i_elem] = 0
    return errors


# функция получения 2n стобцов из файла
def get_2n_columns_from_file(file_name, n):
    # определение формата файла
    file_format = file_name.split('.')[1]
    # извлечение данных исходя из формата файла
    if file_format == "csv":
        data_from_file = get_from_csv(file_name)
    elif file_format == 'json':
        data_from_file = get_from_json(file_name)
    elif file_format == 'xml':
        data_from_file = get_from_xml(file_name)
    else:
        return None

    # запись 2n столбцов из всех данных файла
    data_with_2n_columns = to_2n_columns(data_from_file, n)

    return data_with_2n_columns


# функция добавления заголовков данных
def set_headers(data, n):
    # создание заголовков данных
    headers = []
    for i in range(n):
        header = "D{}".format(i + 1)
        headers.append(header)
    for i in range(n):
        header = "M{}".format(i + 1)
        headers.append(header)
    # запись заголовков в итоговый список
    data.insert(0, headers)


# функция записи в файл результата базового задания
def write_in_file_basic(data):
    # определение директории с файлами для записи результатов
    dir_name = dirname(__file__)
    path_to_files = join(dir_name, 'Results\\')
    with open(path_to_files + 'basic_results.tsv', "w", newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        for row in data:
            tsv_output.writerow(row)
        print("basic_results.tsv created!")


# функция записи в файл дополнительного задания
def write_in_file_advanced(data, dict_same_rows):
    dir_name = dirname(__file__)
    path_to_files = join(dir_name, 'Results\\')
    with open(path_to_files + 'advanced_results.tsv', "w", newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        for indexes_same_rows in dict_same_rows.values():
            # запись первого индекса, к которому прибавлялись элементы повторяющихся строк
            index_row_with_sum = indexes_same_rows[0]
            tsv_output.writerow(data[index_row_with_sum])
        print("advanced_results.tsv created!")


# функция получения словаря с индексами повторяющихся строк
def get_dict_of_same_rows(n, data):
    # словарь повторяющихся строк: строка D1...Dn(ключ) - её индексы в списке(значение)
    same_rows_with_indexes = {}

    for index, row in enumerate(data):
        # набор D1...Dn текущей строки - ключ словаря
        set_of_d_columns = str(row[:n])
        # получение индекса строки с данным ключом(набором D1...Dn)
        index_uniq_row = same_rows_with_indexes.get(set_of_d_columns)
        # если такого ключа не существует, то создаём его
        # и присваиваем ему индекс текущей строки списка all_data
        if index_uniq_row is None:
            same_rows_with_indexes[set_of_d_columns] = []
            same_rows_with_indexes[set_of_d_columns].append(index)
        # если строка с таким набором существует
        # то добавляем в словарь текущий индекс
        else:
            same_rows_with_indexes[set_of_d_columns].append(index)

    return same_rows_with_indexes


# функция суммирования повторяющихся строк
def sum_same_rows(n, data, same_rows):
    # каждому ключу словаря соответствует список индексов одинаковых строк
    for indexes_same_rows in same_rows.values():
        # если строка присутствует больше одного раза
        if len(indexes_same_rows) > 1:
            # записываем первый индекс
            first_index = indexes_same_rows[0]
            # прибавляем к строке с первым индексом
            # строки с последующими индексами
            for index_row in indexes_same_rows[1:]:
                # суммирование частей строк M1...Mn
                for i in range(n):
                    data[first_index][n + i] += data[index_row][n + i]
    return data


def main():
    # получение списка файлов для обработки
    files = get_list_of_files()
    # получение числа столбцов D*
    n = get_count_of_d_columns(files)

    # список для записи данных
    all_data = []
    # список для записи ошибок
    all_errors = []

    for file in files:
        # получение данных из 2n столбцов в файле
        data_from_file = get_2n_columns_from_file(file, n)
        # если данные не получены, происходит переход к следующему файлу
        if data_from_file is None:
            continue

        # упорядочивание столбцов алгоритмом быстрой сортировки по заголовку
        sorting.quick_sort_columns(data_from_file, 0, len(data_from_file[0]) - 1)

        # определение ошибок в полученных данных
        errors_in_file = check_errors(n, data_from_file[1:], file)

        # запись данных в итоговый список
        for row in data_from_file[1:]:
            all_data.append(row)
        # запись ошибок в итоговый список
        for error in errors_in_file:
            all_errors.append(error)

    # сортировка полученных данных по строкам
    # алгоритмом быстрой сортировки
    sorting.quick_sort_rows(all_data, 0, len(all_data) - 1)

    # добавление заголовков
    set_headers(all_data, n)
    # запись полученных данных после выполнения базого задания в файл
    write_in_file_basic(all_data)

    # ВЫПОЛНЕНИЕ ДОПОЛНИТЕЛЬНОГО ЗАДАНИЯ (ADVANCED)

    # получение словаря повторяющихся строк
    dict_of_same_rows = get_dict_of_same_rows(n, all_data)
    # суммирование повторяющихся строк
    data_with_sum_rows = sum_same_rows(n, all_data, dict_of_same_rows)
    # запись обработанных строк в файл
    write_in_file_advanced(data_with_sum_rows, dict_of_same_rows)

    # информирование пользователя об ошибках
    for error in all_errors:
        print(error)


if __name__ == '__main__':
    main()
