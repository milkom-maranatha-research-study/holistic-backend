from datetime import timedelta
from dateutil.relativedelta import relativedelta
from rest_framework.exceptions import ValidationError


def validate_weekly_period(start_date, end_date):
    """
    Checks if that incoming `start_date` and `end_date`
    is the correct start and end date of the week.
    """

    correct_start_date = start_date - timedelta(days=start_date.weekday())
    correct_end_date = correct_start_date + timedelta(days=6)

    if start_date != correct_start_date:
        raise ValidationError({
            'start_date': f'{start_date.isoformat()} is not the start date of the week.'
        }, code='invalid')

    if end_date != correct_end_date:
        raise ValidationError({
            'end_date': f'{end_date.isoformat()} is not the end date of the week.'
        }, code='invalid')


def validate_monthly_period(start_date, end_date):
    """
    Checks if that incoming `start_date` and `end_date`
    is the correct start and end date of the month.
    """

    correct_start_date = start_date.replace(day=1)

    # We use `relativedelta` to calculate the end of month
    # So it won't blindly add 31 days to that `correct_start_date`.
    correct_end_date = correct_start_date + relativedelta(day=31)

    if start_date != correct_start_date:
        raise ValidationError({
            'start_date': f'{start_date.isoformat()} is not the start date of the month.'
        }, code='invalid')

    if end_date != correct_end_date:
        raise ValidationError({
            'end_date': f'{end_date.isoformat()} is not the end date of the month.'
        }, code='invalid')


def validate_yearly_period(start_date, end_date):
    """
    Checks if that incoming `start_date` and `end_date`
    is the correct start and end date of the year.
    """

    correct_start_date = start_date.replace(day=1, month=1)
    first_date_of_dec = correct_start_date.replace(month=12)

    # We use `relativedelta` to calculate the end of month
    # So it won't blindly add 31 days to that `first_date_of_dec`.
    correct_end_date = first_date_of_dec + relativedelta(day=31)

    if start_date != correct_start_date:
        raise ValidationError({
            'start_date': f'{start_date.isoformat()} is not the start date of the year.'
        }, code='invalid')

    if end_date != correct_end_date:
        raise ValidationError({
            'end_date': f'{end_date.isoformat()} is not the end date of the year.'
        }, code='invalid')
