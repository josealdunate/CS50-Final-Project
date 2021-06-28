import csv
from cs50 import SQL


db = SQL("sqlite:///renection.db")

with open('static/OT_Chile.csv') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else: 
            db.execute("INSERT INTO ubicacion (region, provincia, comuna) VALUES (:region, :provincia, :comuna)",
                        region=row[0], provincia=row[1], comuna=row[2])
            line_count += 1