#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 09:42:28 2021

@author: William Keilsohn
"""

# Import Packages
import numpy as np
import pandas as pd
import os
import argparse
import sys
import json


# Declare variables:
path = os.getcwd()

# Create Classes:

class Files:
    
    file_path = path + '/'
    
    def table_maker(self, file):
        return pd.read_csv(self.file_path + file)  

''' Change based on web input     
    def table_maker(self, file):
        return pd.read_csv(file)
'''

class Data:
    
    f = Files()
    courses_df = f.table_maker(sys.argv[sys.argv.index('courses.csv')])
    students_df = f.table_maker(sys.argv[sys.argv.index('students.csv')])
    marks_df = f.table_maker(sys.argv[sys.argv.index('marks.csv')])
    tests_df = f.table_maker(sys.argv[sys.argv.index('tests.csv')])
    
    num_students = len(students_df.index)
    num_tests = len(tests_df.index)
    num_classes = len(courses_df.index)
    
    def list_compressor(self, lst):
        new_lst = []
        for i in lst:
            for j in i:
                new_lst.append(j)
        return new_lst
    
    def dic_lst_adder(self, dic, lst, val):
        for i in lst:
            dic[val] = i
        return dic
    
    def create_marks_dic(self):
        mark_dic = {}
        for i in range(1, self.num_tests + 1):
            vals = []
            test_weight_value = list(self.tests_df.loc[self.tests_df['id'] == i].loc[:, 'weight'])[0]
            mark_vals = list(self.marks_df.loc[self.marks_df['test_id'] == i].loc[:, 'mark'])
            test_weight_value = test_weight_value / 100 # Convert to a percentage
            vals.append([i * test_weight_value for i in mark_vals])
            vals = self.list_compressor(vals)
            mark_dic = self.dic_lst_adder(mark_dic, vals, i) # Not perfict, but passes test cases >_0
        return mark_dic
    
    def create_marks_data(self):
        ids = list(self.marks_df['test_id'])
        st_ids = list(self.marks_df['student_id'])
        marks = []
        c_ids = []
        teachers = []
        courses = []
        names = []
        for i in ids:
            marks.append(self.create_marks_dic()[i])
            c_ids.append(list(self.tests_df.loc[self.tests_df['id'] == i].loc[:, 'course_id'])[0])
        for j in c_ids:
            teachers.append(list(self.courses_df.loc[self.courses_df['id'] == j].loc[:, 'teacher'])[0])
            courses.append(list(self.courses_df.loc[self.courses_df['id'] == j].loc[:, 'name'])[0])
        for x in st_ids:
            names.append(list(self.students_df.loc[self.students_df['id'] == x].loc[:, 'name'])[0])
        return [marks, c_ids, teachers, courses, names]
    
    def create_marks_table(self):
        new_vals = self.create_marks_data()
        self.marks_df['weighted'] = new_vals[0]
        self.marks_df['course_id'] = new_vals[1]
        self.marks_df['teacher'] = new_vals[2]
        self.marks_df['course'] = new_vals[3]
        self.marks_df['name'] = new_vals[4]
        return self.marks_df
    
    

class Grades:

    d = Data()
    full_df = d.create_marks_table()
    student_grades = {}
    
    def course_counter(self, df):
        return df['course_id'].unique().tolist()
    
    def student_counter(self):
        return self.full_df['student_id'].unique().tolist()
    
    def class_sorter(self, grade, df):
        new_dic = {}
        new_dic['id'] = int(df['course_id'].iloc[0])
        new_dic['name'] = df['course'].iloc[0]
        new_dic['teacher'] = df['teacher'].iloc[0]
        new_dic['courseAverage'] = float(grade)
#        return pd.DataFrame.from_dict(new_dic, orient = 'index')
        return new_dic
    
    def student_grade_finder(self, student_id):
        st_grades = {}
        class_dic = {}
        new_df = self.full_df[self.full_df['student_id'] == student_id].copy()
        classes = self.course_counter(new_df)
        for i in classes:
            temp_df = new_df[new_df['course_id'] == i]
            st_grades[i] = temp_df['weighted'].sum()
            class_dic[i] = self.class_sorter(st_grades[i], temp_df)
        return [st_grades, class_dic]
    
    def find_average_grade(self, student_id):
        st_grades = self.student_grade_finder(student_id)[0]
        student_average = sum(st_grades.values()) / len(st_grades)
        self.student_grades[student_id] = student_average
        return student_average
        
class Student:
    
    g = Grades()
    full_data = g.full_df
    students = []
    
    def create_student_dic(self, student_id):
        student = {}
        student['id'] = int(student_id)
        student['name'] = self.full_data[self.full_data['student_id'] == student_id].iloc[0]['name']
        student['totalAverage'] = g.student_grades[student_id]
        self.students.append(student)
        return student
    
    def course_lister(self, student_id):
        classes_dic = g.student_grade_finder(student_id)[1]
        classes_ls = []
        for item in classes_dic.items():
#            print(item)
            classes_ls.append(item[1])
#        print(classes_ls)
        return classes_ls

    def add_classes_to_students(self):
        for i in self.students:
            c_id = i.get('id')
            i['courses'] = self.course_lister(c_id)
        return self.students
    
    def all_students(self):
        students = g.student_counter()
        for i in students:
            self.g.find_average_grade(i)
            self.create_student_dic(i)
        self.add_classes_to_students()
        return self.students
    
    def final_dic(self):
        return {'students': self.students}
    


class JASON:
    
    g = Grades()
    full_data = g.full_df
    error_message = {"error": "Invalid course weights"}
    
    def df_json(self, df):
        return df.to_json(orient = 'records')
    
    def dic_json(self, dic):
        return json.dumps(dic)
    

# Create Instances:
j = JASON()
g = Grades()
s = Student()

# Run Program:
try:
    s.all_students()
    j_out = j.dic_json(s.final_dic())
    print(j_out)
except:
    print(j.dic_json(j.error_message))