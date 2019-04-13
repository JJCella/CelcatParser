from icalendar import Calendar, Event
import datetime
import requests
import re
import os


ics_file = 'ics_etu.ics'

def parse_course(component):


    description_patterns = {
        'matiere': {'r': '(?i)Matière :', 'p': '(?i)Matière *: *(allemand|anglais|espagnol|.+)', 'default' : ['?'], 'post' : str.capitalize},
        'professeur': {'r': '(?i)Personnel *:', 'p': '(?i)Personnel *: *(.*)', 'default' : ['?'], 'post' : lambda str: str},
        'remarques': {'r': '(?i)Remarques *:', 'p': '(?i)Remarques *: *([^\n]*)', 'default' : ['?'], 'post' : lambda str: str},
        'groupe' : {'r' : '(?i)Groupe *:', 'p': '(?i)(TP|TD)? *G((?:A|E)?\d)', 'default' : ['all'], 'post' : lambda str: str}

    }

    summary_patterns = {
        "type": "(?i)(Contrôle continu|TP|TD|CM|projet)"
    }

    course = {}

    description = component.get("description").replace(",", " ").replace("  ", " ").split('\n')
    summary = component.get("summary").replace(",", " ")

    '''Evenement sans location = evenement annulé'''

    if component.get("location"):
        course["salle"] = component.get("location")
        course["debut"] = component.get("dtstart").dt + datetime.timedelta(hours=1)
        course["fin"] = component.get("dtend").dt + datetime.timedelta(hours=1)

        '''Traitement du summary'''

        for field_name, field_parsing in summary_patterns.items():
            field_data = re.search(field_parsing, summary)
            if field_data:
                field_data = list(field_data.groups())
                course[field_name] = ''.join(filter(None, field_data))

        '''Traitement de la description'''

        for field in description:
            for field_name, field_parsing in description_patterns.items():
                if re.search(field_parsing['r'], field):
                    field_data = re.findall(field_parsing['p'], field)
                    if field_data:
                        for index, data in enumerate(field_data):
                            if isinstance(data, tuple):
                                field_data[index] = ''.join(data)
                            field_data[index] = field_parsing['post'](field_data[index])

                        course[field_name] = field_data

        '''Valeur par defaut si champs non trouvé'''

        for field, field_parsing in description_patterns.items():
            if field not in course:
                course[field] = field_parsing["default"]

        '''TD **** ou les groupes sont non renseignés => TDs spécifiques genre CeLFE'''
        '''TODO système defaults pour les summary_patterns'''
        if 'type' not in course:
            return
        if course['type'] == 'TD' and course['groupe'] == ['all']:
            return

        return course


def get_courses(calendar, date, groups):

    courses = []

    for component in calendar.walk():
        if component.name == "VEVENT":
            if component.get("dtstart").dt.date() == date.date():
                course = parse_course(component)
                if course:
                    if set(course["groupe"]) & set(groups + ['all']):
                            courses.append(course)
    return courses


def get_icalendar():
    if os.path.exists(ics_file):
        created_time = datetime.datetime.fromtimestamp(os.path.getmtime('ics_etu.ics'))
    else:
        created_time = datetime.datetime.fromtimestamp(0)

    if created_time + datetime.timedelta(hours=1) < datetime.datetime.now():
            r = requests.get("http://celcat.univ-angers.fr/ics_etu.php?url=publi/etu/g467129.ics")
            open('ics_etu.ics', 'wb').write(r.content)

    return Calendar.from_ical(open('ics_etu.ics', 'rb').read())


def format_courses(courses):

    formatted_courses = []

    if courses:
        for course in courses:
            f = "{:%Hh%M}->{:%Hh%M} : [{}] {} en {} avec {} ({})".format(course["debut"], course["fin"],
                                                                             course["type"], " ".join(course["matiere"]),
                                                                             course["salle"], " ".join(course["professeur"]),
                                                                       " & ".join(course["groupe"]))
            if " ".join(course["remarques"]) != "?":
                f += " Remarques : {}".format(" ".join(course["remarques"]))

            formatted_courses.append(f)

        return formatted_courses
    else:
        return None


def process(date, groups):

    calendar = get_icalendar()

    dt = datetime.datetime.strptime(date, '%d-%m-%Y')

    courses = get_courses(calendar, dt, groups)

    if courses:
        formatted_courses = format_courses(courses)
    else:
        formatted_courses = ["Pas de cours trouvé à cette date"]


    return '\n'.join(formatted_courses)

