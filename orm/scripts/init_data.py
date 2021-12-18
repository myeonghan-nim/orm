import csv
import os

from orm.models import User


def run():
    with open(f'{os.getcwd()}/sample.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            _, created = User.objects.get_or_create(
                **row
            )
