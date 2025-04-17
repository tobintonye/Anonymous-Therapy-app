from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

# Topic Model
class Topic(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    
    def __str__(self):
        return self.name
    
# SubTopic Model
class SubTopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subtopics') # 1:N relationship
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# a model for specializations and connected to topic model so therapists can be categorized more precisely.
class Specialization(models.Model):
    topics = models.ManyToManyField(Topic, related_name='specializations')  # Link to multiple topics
    subtopics = models.ManyToManyField(SubTopic, related_name='specializations', blank=True)  # Linking to subtopics for detailed categorization
    name = models.CharField(
        max_length=70,
        unique=True,
        choices=[
            ("Mental Health", "Mental Health"),
            ("Relationships", "Relationships"),
            ("Trauma & Abuse", "Trauma & Abuse"),
            ("Self-Esteem & Self-Worth", "Self-Esteem & Self-Worth"),
            ("Spirituality", "Spirituality"),
            ("Addiction & Recovery", "Addiction & Recovery"),
        ],
    )

    def __str__(self):
        return self.name
    
# Therapist Model - therapists can have multiple specializations, and each specialization can be related to one or more topics.
class TherapistProfile(models.Model):
    specializations = models.ManyToManyField(Specialization, related_name='therapists')
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    profile_image = models.ImageField(upload_to='therapist/profile/', blank=False, null=False)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    date_of_birth = models.DateField(blank=False, null=False)
    years_of_experience = models.PositiveIntegerField(blank=False, null=False)
    languages_spoken = models.CharField(max_length=60, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='therapist')
    created_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField()
    country = models.CharField(max_length=60, blank=False, null=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


'''
#  Populate Subtopics Automatically for Specializations
@receiver(m2m_changed, sender=Specialization.topics.through)
def auto_assign_subtopics_to_specialization(instance, action, **kwargs):
    if action in ['post_add', 'post_remove']:
        # Automatically link all subtopics under the associated topics to the specialization
        subtopics_to_add = SubTopic.objects.filter(topic__in=instance.topics.all())
        instance.subtopics.set(subtopics_to_add)  # Assign all related subtopics

@receiver(m2m_changed, sender=TherapistProfile.specializations.through)
def auto_assign_specialization_subtopics_to_therapist(instance, action, **kwargs):
    if action in ['post_add', 'post_remove']:
        # Automatically inherit subtopics from selected specializations
        subtopics_to_add = SubTopic.objects.filter(specializations__in=instance.specializations.all())
        instance.subtopics.set(subtopics_to_add)  # Add all related subtopics from selected specializations
'''