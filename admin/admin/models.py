from django.contrib import admin
from django.db import models


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
    payment = models.CharField()
    status = models.CharField()
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