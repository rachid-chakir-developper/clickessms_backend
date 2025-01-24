import re
from datetime import datetime
from dateutil.rrule import rrulestr

def parse_recurrence_rule(recurrence_rule, starting_date_time):
    """
    Parse the recurrence rule and return the frequency, days, end date, and count.
    """
    # Default values
    recurrence_frequency = None
    recurrence_days = None
    recurrence_end_date = None
    count = None

    if not recurrence_rule:
        return recurrence_frequency, recurrence_days, recurrence_end_date, count

    # Extract frequency
    freq_match = re.search(r'FREQ=([A-Z]+)', recurrence_rule)
    if freq_match:
        recurrence_frequency = freq_match.group(1)

    # Extract days
    days_match = re.search(r'BYDAY=([A-Z,]+)', recurrence_rule)
    if days_match:
        days_str = days_match.group(1)
        days_abbr = {'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4, 'SA': 5, 'SU': 6}
        recurrence_days_array = [days_abbr[day] for day in days_str.split(',')]
        recurrence_days = ",".join(str(day) for day in recurrence_days_array)

    # Extract UNTIL date
    end_date_match = re.search(r'UNTIL=([0-9T]+)', recurrence_rule)
    if end_date_match:
        end_date_str = end_date_match.group(1)
        try:
            recurrence_end_date = datetime.strptime(end_date_str, '%Y%m%dT%H%M%S')
        except ValueError:
            pass

    # Extract COUNT
    count_match = re.search(r'COUNT=(\d+)', recurrence_rule)
    if count_match:
        count = int(count_match.group(1))

    # Generate RRULE string
    rule = f"FREQ={recurrence_frequency}"
    if count:
        rule += f";COUNT={count}"

    # Use starting_date_time as the DTSTART if needed
    rrule = rrulestr(rule, dtstart=starting_date_time)

    # Calculate end date if COUNT is specified
    if count:
        occurrences = list(rrule)
        recurrence_end_date = occurrences[-1] if occurrences else None

    return recurrence_frequency, recurrence_days, recurrence_end_date, count


def get_week_days_in_range(starting_date_time, ending_date_time):

    # Calculer les jours de la semaine entre le jour de starting_date_time et la fin de la semaine
    starting_weekday = starting_date_time.weekday()  # Lundi=0, Dimanche=6
    ending_weekday = ending_date_time.weekday()  # Lundi=0, Dimanche=6

    # Générer une liste des jours de la semaine depuis starting_date_time jusqu'à la fin de la semaine
    days_from_starting = [(starting_weekday + i) % 7 for i in range(7 - starting_weekday)]  # De starting_date_time à la fin de la semaine

    # Générer une liste des jours de la semaine du début de la semaine jusqu'à ending_date_time
    days_from_ending = [(i) % 7 for i in range(ending_weekday + 1)]  # Du début de la semaine (lundi) à ending_date_time

    # Fusionner les jours et supprimer les doublons
    all_days = list(set(days_from_starting + days_from_ending))

    return all_days
