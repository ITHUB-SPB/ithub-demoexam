from django.contrib import admin
from django.db import models


class Payment(models.TextChoices):
    CASH = "Наличные", "Наличные"
    PHONE = "Перевод по номеру", "Перевод по номеру"


class Status(models.TextChoices):
    NEW = "Новая", "Новая"
    PROGRESS = "Идёт обучение", "Идёт обучение"
    COMPLETED = "Завершён", "Завершён"


class User(models.Model):
    login = models.CharField()
    password = models.CharField()
    email = models.CharField()
    fio = models.CharField()
    phone = models.CharField()

    class Meta:
        app_label = "admin"
        db_table = "user"


class Record(models.Model):
    course = models.CharField()
    date = models.DateField()
    payment = models.CharField(choices=Payment)
    status = models.CharField(choices=Status, default=Status.NEW)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        app_label = "admin"
        db_table = "record"


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ["course", "date", "user__fio", "user__phone", "status"]
    list_filter = ["course", "status", "date"]
    search_fields = ["user__email"]


admin.site.site_title  = "Админпанель"
admin.site.site_header  = "Корки.Есть. Админпанель"
admin.site.index_title  = "Корки.Есть"