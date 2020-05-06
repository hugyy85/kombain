import datetime

from django.db import models
from django.contrib.auth.models import User

import tabula


class CallReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    call_report_created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='pdf')
    r_date_time = models.DateTimeField()
    r_traffic_place = models.CharField(max_length=64)
    r_traffic_income = models.BooleanField(default=False)
    r_traffic_name = models.CharField(max_length=32)
    r_traffic_int_volume = models.IntegerField(null=True)
    r_traffic_sec_volume = models.IntegerField(null=True)
    r_traffic_other_volume = models.IntegerField(null=True)

    def pdf_to_db(self, pdf_path, user):
        # pdf converter is so bad, because pfd is image, not table
        data_frame = tabula.read_pdf(pdf_path, output_format="dataframe", pages='all')
        count_str = data_frame[0].shape[0]
        result = []
        for i in range(count_str):
            try:

                raw_str = data_frame[0].iloc[i]
                try:
                    date_time = datetime.datetime.strptime(f"{raw_str['Дата']} {raw_str['Время']}", '%d.%m.%Y %H:%M:%S')
                except ValueError:
                    continue

                if str(raw_str['Номер']).startswith('<--'):
                    income = True
                else:
                    income = False
                number = raw_str['Номер']
                traffic_name = raw_str['Зона вызова']
                traffic_volume = raw_str['Зона направления\rвызова/номер сессии']
                internet = None
                calls = None
                other = None
                if traffic_volume.endswith('Kb'):
                    internet = int(traffic_volume[:-2])
                elif traffic_volume.find(':') != -1:
                    calls = traffic_volume.split(':')
                    calls = int(calls[0]) * 60 + int(calls[1])
                else:
                    other = int(traffic_volume)
                result.append(CallReport(
                    user=user,
                    file=pdf_path,
                    r_date_time=date_time,
                    r_traffic_place=number,
                    r_traffic_name=traffic_name,
                    r_traffic_int_volume=internet,
                    r_traffic_sec_volume=calls,
                    r_traffic_other_volume=other,
                    r_traffic_income=income
                ))
            except:
                pass
        CallReport.objects.bulk_create(result)

