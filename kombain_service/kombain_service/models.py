import datetime

from django.db import models
from django.contrib.auth.models import User

import tabula


class CallReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    call_report_created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='pdf')

    def pdf_to_db(self, pdf_path, user):
        # pdf converter is so bad, because pfd is image, not table
        data_frame = tabula.read_pdf(pdf_path, output_format="dataframe", pages='all')
        count_str = data_frame[0].shape[0]
        result = []
        report = CallReport.objects.create(user=user, file=pdf_path)
        for i in range(count_str):
            try:

                raw_str = data_frame[0].iloc[i]
                try:
                    date_time = datetime.datetime.strptime(f"{raw_str['Дата']} {raw_str['Время']}", '%d.%m.%Y %H:%M:%S')
                except ValueError:
                    continue

                if str(raw_str['Номер']).startswith('<--'):
                    income = True
                    raw_str['Номер'] = raw_str['Номер'].replace('<--', '')
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
                result.append(CallReportTraffic(
                    call_report_id=report,
                    date_time=date_time,
                    traffic_place=number,
                    traffic_name=traffic_name,
                    traffic_int_volume=internet,
                    traffic_sec_volume=calls,
                    traffic_other_volume=other,
                    traffic_income=income
                ))
            except:
                pass

        CallReportTraffic.objects.bulk_create(result)


class CallReportTraffic(models.Model):
    call_report_id = models.ForeignKey(CallReport, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    traffic_place = models.CharField(max_length=64)
    traffic_income = models.BooleanField(default=False)
    traffic_name = models.CharField(max_length=32)
    traffic_int_volume = models.IntegerField(null=True)
    traffic_sec_volume = models.IntegerField(null=True)
    traffic_other_volume = models.IntegerField(null=True)

