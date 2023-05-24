# importing csv module
import csv

# csv file name
filename = "grades.csv"

# initializing the titles and rows list
fields = []
rows = []

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting field names through first row
    fields = next(csvreader)

    # extracting each data row one by one
    for row in csvreader:
        rows.append(row)

# printing the field names
# print('Field names are:' + ', '.join(field for field in fields))
grades = {}
# printing first 5 rows
for row in rows:
    if row[2].isnumeric():
        num = [int(x) if x.isnumeric() else 0 for x in row[4:14]]
        grades[row[2]] = [row[1].strip().lower()] + [row[3]] + num
    # print(grades[row[2]])
    # print('\n')

print(grades)
