from django.contrib import admin
from therapy.models import Topic, SubTopic, Specialization, TherapistProfile

# Inline for SubTopics within Topics
class SubTopicInline(admin.TabularInline):
    model = SubTopic
    extra = 3  

# Admin for Topic, including SubTopics
class TopicAdmin(admin.ModelAdmin):
    inlines = [SubTopicInline]  # Allow managing SubTopics from the Topic admin page
    list_display = ('name',)  
    search_fields = ('name',) 


# Admin for Specialization
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Show the name field in the admin list view
    filter_horizontal = ('topics', 'subtopics')  
    search_fields = ('name',) 


# Admin for TherapistProfile (if needed)
class TherapistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization')  # Replace with actual fields in TherapistProfile
    search_fields = ('user__username', 'specialization__name')  

# Registering the models with the admin
admin.site.register(Topic, TopicAdmin)
admin.site.register(Specialization, SpecializationAdmin)
admin.site.register(TherapistProfile)
