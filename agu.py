import requests
from Entity import Entity
from Lesson import Lesson
from bs4 import BeautifulSoup as Bs
from datetime import date, timedelta
import datetime
from Interval import Interval
from Papser import Parser

main_url = "https://www.asu.ru/timetable"


class Agu(Parser):
    def __init__(self, university, username, password):
        super().__init__(university, username, password)

    def get_timetable(self, faculties):
        objectLessons = []
        for faculty in faculties:
            # Пока есть факультеты - получаем группы факультета
            groups = self.get_groups(faculty)
            for group in groups:
                # Получаем именование группы
                name = [faculty, group]

                # Метод получения информации о парах
                entity = Entity(name, None, 'group', None)

                objectLessons.append(entity)

        return objectLessons

    def get_lessons(self, thisgroup):
        # получаем все теги с парами
        global number_week
        massSchedule = []
        # Получаем html
        url = main_url + "/students/" + thisgroup.name[0] + thisgroup.name[1] + "?date=" + str(get_two_week())
        soup = pars(url)

        thisgroup.name = self.get_name(soup)
        thisgroup.url = url
        table = self.get_table(soup)

        if table != None:
            for td in table.find_all("tr"):
                # Если тэг блоком информации о дате и дне -> получаем, если нет, то это тэг с парами
                try:
                    number_week = get_number_week(td)
                    day = self.get_day(td)
                    continue
                except Exception:
                    pass
                extra = self.get_extra(td)
                subject = self.get_subject(td)
                if subject == "":
                    subject = None
                try:
                    number = int(self.get_number(td).strip())
                except ValueError:
                    pass

                auditory = self.get_auditory(td)
                start_time = self.get_start_time(td)
                end_time = self.get_end_time(td)

                if start_time != "" and start_time != None and end_time != "" and end_time != None:
                    interval = Interval(number, start_time, end_time)

                    typ = self.get_type(td)
                    lesson = Lesson(number_week, day, interval, subject, auditory, extra, typ)
                    if lesson.subject != None:
                        self.addLessonToSchedule(massSchedule, lesson)
        return massSchedule

    def get_day(self, tr):
        try:
            day = tr.find("span", class_="t_bold t_brown").text
        except AttributeError:
            day = tr.find("span", class_="t_bold t_blue").text

        if day == "Понедельник":
            return 1
        elif day == "Вторник":
            return 2
        elif day == "Среда":
            return 3
        elif day == "Четверг":
            return 4
        elif day == "Пятница":
            return 5
        elif day == "Суббота":
            return 6

    def get_type(self, tr):
        typ = tr.find_all("td")[2].text.strip().split(" ")[0]
        if typ == "пр.з." or typ == "биох.":
            return "Практика"
        elif typ == "лек." or typ == "физ.":
            return "Лекция"
        elif typ == "бот." or typ.strip() == "зоол.":
            return "Лабораторная"
        else:
            return None

    def get_number(self, tr):
        return tr.find_all("td")[0].text.strip()

    def get_end_time(self, tr):
        try:
            return tr.find_all("td")[1].text.strip().split(" - ")[1]
        except IndexError:
            pass

    def get_start_time(self, tr):
        return tr.find_all("td")[1].text.strip().split(" - ")[0]

    def get_extra(self, tr):
        prefixes = ["проф. ", "ст.пр ", "ст.п. ", "зав.каф. ", "преп. ", "зав. ", "пр ", "асс. ",
                    "ст.пр. ", "декан ", "доц. ", "с)", "доц." "асс.", "преп. ", "доц. ", "ст.пр. ", "проф. ", "доц."]
        extra = tr.find_all("td")[3].text.strip()
        for prefix in prefixes:
            extra = extra.replace(prefix, "")
            if extra == "":
                return None
        return extra

    def get_subject(self, tr):
        prefixes = ["пр.з. ", "лек. ", "биох. ", "физ. ", "бот. ", "зоол.", "нем. ", "лаб. ", "\n", " " * 23,
                    "биот. ", "экол. ", "обэк ", "агро ", "англ. ", "анг. ", "ГиТ ", "МО ", "англ.1 ",
                    "англ.2 ", "зач.", "экз. ", "яз. ", "обэк ", "агро ",
                    "экол. ", "анг. ", "англ.1 ", "декан ", "ст.пр."]
        subject = tr.find_all("td")[2].text.strip()
        for prefix in prefixes:
            subject = subject.replace(prefix, "")
        return subject

    def get_auditory(self, tr):
        auditory = tr.find_all("td")[4].text.strip()
        if auditory == "":
            return ' '
        return auditory

    def get_name(self, soup):
        try:
            name = soup.find("h1").text.split("группы ")[1].split("(")[0].strip()
            return name
        except IndexError:
            return '1100 пр'

    def get_groups(self, faculty):
        groups = []
        soup = pars(main_url + "/students/" + faculty)
        divs = soup.find_all("div", class_="link_ptr_left margin_bottom")
        for div in divs:
            groups.append(div.find("a").get("href").strip())
        return groups

    def get_faculties(self):
        faculties = []
        soup = pars(main_url + "/students/")
        all_tag_a = soup.find("div", class_="padding_left_x").find_all("a")
        for a in all_tag_a:
            faculties.append(a.get("href"))
        return faculties

    def check_freeday(self, table):
        try:
            table.find_all("td")
            return True
        except AttributeError:
            return False

    def get_table(self, soup):
        return soup.find("table", class_="align_top schedule")


def validation_check(subject, extra, typ):
    if subject is None and extra is None and typ is None:
        return True
    else:
        return False


def getObjectLessons(timetable, name, faculty, group, url):
    url = url + "/students/" + faculty + group + "?date=" + str(get_two_week())
    valid_table = [name, url, "group", timetable]
    return valid_table


def get_monday():
    if datetime.datetime.weekday(datetime.datetime.today()) == 0:
        return date.today()

    elif datetime.datetime.weekday(datetime.datetime.today()) == 1:
        return date.today() - timedelta(days=1)

    elif datetime.datetime.weekday(datetime.datetime.today()) == 2:
        return date.today() - timedelta(days=2)

    elif datetime.datetime.weekday(datetime.datetime.today()) == 3:
        return date.today() - timedelta(days=3)

    elif datetime.datetime.weekday(datetime.datetime.today()) == 4:
        return date.today() - timedelta(days=4)

    elif datetime.datetime.weekday(datetime.datetime.today()) == 5:
        return date.today() - timedelta(days=5)

    elif datetime.datetime.weekday(datetime.datetime.today()) == 6:
        return date.today() - timedelta(days=6)


def get_number_week(tr):
    date = tr.find("span", class_="date t_small_x t_gray_light").text
    day, month, year = tuple(date.split("."))
    number_week = datetime.date(int(year), int(month), int(day)).isocalendar()[1]
    if number_week % 2 == 0:
        return 2
    else:
        return 1


def get_two_week():
    monday_plus_monday = get_monday() + timedelta(days=12)
    year = str(get_monday()).split("-")[0]
    month = str(get_monday()).split("-")[1]
    day = str(get_monday()).split("-")[2]
    year12 = str(monday_plus_monday).split("-")[0]
    month12 = str(monday_plus_monday).split("-")[1]
    day12 = str(monday_plus_monday).split("-")[2]
    return year + month + day + "-" + year12 + month12 + day12


def indent(response):
    return 60 - len(response["entityStatus"])


def pars(url):
    r = requests.get(url)
    return Bs(r.text, "html.parser")


def runAGU():
    Parser = Agu("АГУ", "d75feac15739439af3860ede7983480b", "c685c179801840bed521437c7e78a81d")
    faculties = Parser.get_faculties()
    entity = Parser.get_timetable(faculties)
    # entity = entity[204:208:]

    for index in range(len(entity)):
        thisGroup = entity[index]
        try:
            schedule = Parser.get_lessons(thisGroup)
            thisGroup.schedule = schedule
            Parser.sendEntityToDatabase(thisGroup, index, len(entity))
        except Exception as e:
            e = "AGU "+str(e) + "\t" + " не удалось скачать расписание для группы " + thisGroup.name
            Parser.sendMessOnError(e)

