from django.contrib import admin

from event.models import Events, FormOption, FormOption2, FormQuestion, FormQuestion2

# Register your models here.
admin.site.register(Events)
admin.site.register(FormQuestion)
admin.site.register(FormQuestion2)
admin.site.register(FormOption)
admin.site.register(FormOption2)