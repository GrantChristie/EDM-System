from flask import redirect, url_for, flash
from sklearn.metrics import accuracy_score
import numpy as np


def admincheck(user):
    if user != 'admin':
        flash("You do not have permission to view this page")
        redirect(url_for('home'))


def gradebandcheck(grade):
    grade = round(grade, 1)
    if 21.5 <= grade <= 22.0:
        return 'A1'
    elif 20.5 <= grade <= 21.49:
        return 'A2'
    elif 19.5 <= grade <= 20.49:
        return 'A3'
    elif 18.5 <= grade <= 19.49:
        return 'A4'
    elif 17.5 <= grade <= 18.49:
        return 'A5'
    elif 16.5 <= grade <= 17.49:
        return 'B1'
    elif 15.5 <= grade <= 16.49:
        return 'B2'
    elif 14.5 <= grade <= 15.49:
        return 'B3'
    elif 13.5 <= grade <= 14.49:
        return 'C1'
    elif 12.5 <= grade <= 13.49:
        return 'C2'
    elif 11.5 <= grade <= 12.49:
        return 'C3'
    elif 10.5 <= grade <= 11.49:
        return 'D1'
    elif 9.5 <= grade <= 10.49:
        return 'D2'
    elif 8.5 <= grade <= 9.49:
        return 'D3'
    elif 7.5 <= grade <= 8.49:
        return 'E1'
    elif 6.5 <= grade <= 7.49:
        return 'E2'
    elif 5.5 <= grade <= 6.49:
        return 'E3'
    elif 4.5 <= grade <= 5.49:
        return 'F1'
    elif 3.5 <= grade <= 4.49:
        return 'F2'
    elif 2.5 <= grade <= 3.49:
        return 'F3'
    elif 1.5 <= grade <= 2.49:
        return 'G1'
    elif 0.5 <= grade <= 1.49:
        return 'G2'
    else:
        return 'G3'


def degreeclassification(grade):
    grade = round(grade, 1)
    if 18.0 <= grade <= 22.0:
        return 'First Class'
    elif 17.1 <= grade <= 17.9:
        return 'Borderline First / Upper Second Class'
    elif 15.0 <= grade <= 17.0:
        return 'Upper Second Class'
    elif 14.1 <= grade <= 14.9:
        return 'Borderline Upper Second / Lower Second Class'
    elif 12.0 <= grade <= 14.0:
        return 'Lower Second Class'
    elif 11.1 <= grade <= 11.9:
        return 'Borderline Lower Second / Third Class'
    elif 9.0 <= grade <= 11.0:
        return 'Third Class'
    elif 8.1 <= grade <= 8.9:
        return 'Borderline Third Class / Fail'
    else:
        return 'Fail'


def calculategpa(grade, course_credits, total_credits):
    return grade * course_credits / total_credits


def gradetocgs(grade):
    if grade == 'A1':
        return 22
    elif grade == 'A2':
        return 21
    elif grade == 'A3':
        return 20
    elif grade == 'A4':
        return 19
    elif grade == 'A5':
        return 18
    elif grade == 'B1':
        return 17
    elif grade == 'B2':
        return 16
    elif grade == 'B3':
        return 15
    elif grade == 'C1':
        return 14
    elif grade == 'C2':
        return 13
    elif grade == 'C3':
        return 12
    elif grade == 'D1':
        return 11
    elif grade == 'D2':
        return 10
    elif grade == 'D3':
        return 9
    elif grade == 'E1':
        return 8
    elif grade == 'E2':
        return 7
    elif grade == 'E3':
        return 6
    elif grade == 'F1':
        return 5
    elif grade == 'F2':
        return 4
    elif grade == 'F3':
        return 3
    elif grade == 'G1':
        return 2
    elif grade == 'G2':
        return 1
    elif grade == 'G3':
        return 0


def testbayes(all_student_level1_results, level2grades, clf):
    y_training = []
    y_test = []
    for x in level2grades[15:]:
        y_training.append(gradebandcheck(x))
    for y in level2grades[:5]:
        y_test.append(gradebandcheck(y))
    x_training = np.array(all_student_level1_results[15:])
    x_test = np.array(all_student_level1_results[:5])
    clf.fit(x_training, y_training)
    preds = clf.predict(x_test)
    # print(accuracy_score(y_test, preds))


def testlinearregression(lin, all_student_level1_results, level2grades):
    x_training = np.array(all_student_level1_results[15:])
    x_test = np.array(all_student_level1_results[:5])
    y_training = level2grades[15:]
    y_test = level2grades[:5]
    lin.fit(x_training, y_training)
    preds = lin.predict(x_test)
    preds2 = []
    for x in preds:
        x = gradebandcheck(x)
        preds2.append(x)
    y_test2 = []
    for x in y_test:
        y_test2.append(gradebandcheck(x))
    # print(accuracy_score(y_test2, preds2))
