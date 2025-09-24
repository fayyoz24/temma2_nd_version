from django.contrib import admin

from .models import (Question, 
                    Answer,
                    Category, Sector,
                    MessageRoom, 
                    Messages,
                    MentorMatchScholier, MentorForStudent,
                    MentorMatchStudent, MentorForScholier,
                    University, Study, JobTitle)


admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Category)
admin.site.register(MessageRoom)
admin.site.register(Messages)

class JobTitleAdmin(admin.ModelAdmin):
    list_display=['job_title', 'sector']
    search_fields = ['job_title']
    ordering = ['job_title']
    @admin.display(description='sector')
    def sector(self, object):
        return object.sector.sector
admin.site.register(JobTitle, JobTitleAdmin)

class SectorAdmin(admin.ModelAdmin):
    list_display=['sector']
    search_fields = ['sector']
    ordering = ['sector']

admin.site.register(Sector, SectorAdmin)

class StudyAdmin(admin.ModelAdmin):
    list_display=['name', 'degree', 'university']
    search_fields = ['name']
    ordering = ['name']

    @admin.display(description='university')
    def university(self, object):
        return object.university.name
admin.site.register(Study, StudyAdmin)

class UniversityAdmin(admin.ModelAdmin):
    list_display=['name', 'degree', 'logo']
    search_fields = ['name']
    ordering = ['name']
admin.site.register(University, UniversityAdmin)

class MentorForScholierAdmin(admin.ModelAdmin):
    list_display=['study', 'university', 'email', 'name', 'linkedin_link', 'created_at']
    search_fields = ['name', 'email']
    @admin.display(description='university')
    def university(self, object):
        return object.university.name
    
    @admin.display(description='study')
    def study(self, object):
        return object.study.name
    
admin.site.register(MentorForScholier, MentorForScholierAdmin)

class MentorMatchScholierAdmin(admin.ModelAdmin):
    list_display=['is_replied', 'study', 'university', 'created_at']
    search_fields = ['email']
    @admin.display(description='university')
    def university(self, object):
        return object.university.name
    
    @admin.display(description='study')
    def study(self, object):
        return object.study.name
    
admin.site.register(MentorMatchScholier, MentorMatchScholierAdmin)


class MentorMatchStudentAdmin(admin.ModelAdmin):
    list_display=['is_replied', 'job_title', 'user', 'created_at']

    @admin.display(description='job_title')
    def job_title(self, object):
        return object.job_title.job_title
    
    @admin.display(description='user')
    def user(self, object):
        return object.user.username
    
admin.site.register(MentorMatchStudent, MentorMatchStudentAdmin)

class MentorForStudentAdmin(admin.ModelAdmin):
    list_display=['name','email', 'job_title', 'user', 'created_at']

    @admin.display(description='job_title')
    def job_title(self, object):
        return object.job_title.job_title
    
    @admin.display(description='user')
    def user(self, object):
        return object.user.username
    
admin.site.register(MentorForStudent, MentorForStudentAdmin)
