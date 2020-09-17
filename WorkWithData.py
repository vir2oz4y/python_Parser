def GetLesBegin(time):  # получает начало пары
    time = time.replace(' ', '')
    begin = time.split('-')
    return begin[0]


def GetLesEnd(time):  # получает конец пары
    begin = time.split('-')
    return begin[1]


def GetNumLessons(lesbegin, lesbeginarr):
    LessonsBegin = lesbeginarr
    intervalNumber = -1
    for i in range(len(LessonsBegin)):
        if LessonsBegin[i] == lesbegin:
            intervalNumber=i+1
            return intervalNumber
    return None



def GetLesBegin(time):  # получает начало пары
    time = time.replace(' ', '')
    begin = time.split('-')
    return begin[0]


def GetLesEnd(time):  # получает конец пары
    time = time.replace(' ', '')
    begin = time.split('-')
    return begin[1]


def GetDayOf(day, level):   # перевод дня недели в число
    DayOfWeek = [['Понедельник', 'Пн'], ['Вторник', 'Вт'], ['Среда', 'Ср'], [
        'Четверг', 'Чт'], ['Пятница', 'Пт'], ['Суббота', 'Сб']]

    if level == 'low':
        for i in range(len(DayOfWeek)):
            if DayOfWeek[i][1] == day:
                return i+1
    elif level == 'full':
        for i in range(len(DayOfWeek)):
            if DayOfWeek[i][0] == day:
                return i+1
