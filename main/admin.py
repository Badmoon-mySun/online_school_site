from django.contrib import admin

from main.models import User, Subject, Question, Test, CourseVideo, Schedule

admin.site.register(User)
admin.site.register(Subject)
admin.site.register(Schedule)

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(CourseVideo)
