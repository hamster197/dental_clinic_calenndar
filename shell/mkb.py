from apps.guides.models import MKB10Classes, MKB10Quide


def csv_reader(file_obj):
    import csv
    reader = csv.DictReader(file_obj, delimiter=',')
    new_count = update_count = 0
    print('Started')
    for line in reader:
        if len(line['ksg_code']) != 0:
            mkb_class, created = MKB10Classes.objects.get_or_create(title=line["mkb_class"], )
            values_for_update={"class_id":mkb_class, "title": line["mkb_name"]}
            mkb, created = MKB10Quide.objects.update_or_create(code=line["mkb_code"], defaults=values_for_update)
            if created:
                new_count += 1
            else:
                update_count += 1

    print(new_count, update_count)



if __name__ != "__main__":
    csv_path = "shell/mkb_all.csv"
    with open(csv_path, "r") as f_obj:
        csv_reader(f_obj)