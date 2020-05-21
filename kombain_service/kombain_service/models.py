import datetime

from django.db import models
from django.contrib.auth.models import User

import tabula
from bs4 import BeautifulSoup


class CallReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    call_report_created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='pdf')

    def file_data_to_db(self, date, time, number, val, zone=None):
        date_time = datetime.datetime.strptime(f"{date} {time}", '%d.%m.%Y %H:%M:%S')

        if str(number).startswith('<--'):
            income = True
            number = number.replace('<--', '')
        else:
            income = False

        internet = None
        calls = None
        other = None
        if val.endswith('Kb'):
            internet = int(val[:-2])
        elif val.find(':') != -1:
            calls = val.split(':')
            calls = int(calls[0]) * 60 + int(calls[1])
        else:
            other = int(val)

        return date_time, income, number, internet, calls, other, zone

    def pdf_to_db(self, pdf_path, user):
        # pdf converter is so bad, because pfd is image, not table
        data_frame = tabula.read_pdf(pdf_path, output_format="dataframe", pages='all')
        count_str = data_frame[0].shape[0]
        result = []
        report = CallReport.objects.create(user=user, file=pdf_path)
        for i in range(count_str):
            try:
                raw_str = data_frame[0].iloc[i]
                date_time, income, number, internet, calls, other, traffic_name = self.file_data_to_db(
                    raw_str['Дата'], raw_str['Время'], raw_str['Номер'],
                    raw_str['Зона направления\rвызова/номер сессии'], raw_str['Зона вызова']
                )
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

    def html_to_db(self, html_path, user):
        html = html_path.read()

        soup = BeautifulSoup(html, 'lxml')
        # num = re.findall(r'7\d{10}', html)
        rows = soup.tbody
        result = []
        report = CallReport.objects.create(user=user, file=html_path)
        for row in rows:
            res = row.contents
            date_time, income, number, internet, calls, other, traffic_name = self.file_data_to_db(
                res[1].next, res[2].next,
                res[4].next, res[9].next)
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
        CallReportTraffic.objects.bulk_create(result)


class CallReportTraffic(models.Model):
    call_report_id = models.ForeignKey(CallReport, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    traffic_place = models.CharField(max_length=64)
    traffic_income = models.BooleanField(default=False)
    traffic_name = models.CharField(max_length=32, null=True)
    traffic_int_volume = models.IntegerField(null=True)
    traffic_sec_volume = models.IntegerField(null=True)
    traffic_other_volume = models.IntegerField(null=True)

