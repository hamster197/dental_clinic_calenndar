from apps.guides.models import MKB10Classes, MKB10Quide


def csv_reader(file_obj):
    import csv
    reader = csv.DictReader(file_obj, delimiter=',')
    new_count = update_count = 0
    print('Started')
    for line in reader:
        if len(line['code']) != 0:
            obj = MKB10Quide.objects.filter(title=line["title"], code=line['code'] )
            if obj.exists():
                obj.update(dental=True)

    print(new_count, update_count)



if __name__ != "__main__":
    csv_path = "shell/new_mkb/mkb.csv"
    with open(csv_path, "r") as f_obj:
        csv_reader(f_obj)