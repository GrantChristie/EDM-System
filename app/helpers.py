from flask import redirect, url_for, flash


def admincheck(user):
    if user != 'admin':
        flash("You do not have permission to view this page")
        redirect(url_for('home'))


def gradebandcheck(grade):
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