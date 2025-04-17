from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import TherapistProfile

# signal to delete specializations when a therapist is deleted 
@receiver(pre_delete, sender=TherapistProfile)
def deleterelated_specializations(sender, instance, **kwargs):
      for specialization in instance.specializations.all():
        # if the specialization has no other therapists associated, delete it
        if specialization.therapists.count() == 1: # only current therapists associated with it
            specialization.delete()