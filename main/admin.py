from django.contrib import admin

from main.models import User, Subject, Question, Test, AnswerHistory, TestHistory, CourseVideo

admin.site.register(User)
admin.site.register(Subject)

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(TestHistory)
admin.site.register(AnswerHistory)
admin.site.register(CourseVideo)
