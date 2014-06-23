from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms


SEX_CHOICES = (('N', 'Not Indicated'),
              ('M', 'Male'), ('F', 'Female'))

EXPERIENCE_CHOICES = (('A', 'Agree'), ('U', 'Unsure'), ('D', 'Disagree'))


class UKDemographicsSurvey(models.Model):
    user = models.ForeignKey(User)
    age = models.IntegerField(default=0, help_text="Please provide your age (in years).")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, help_text="Please indicate your sex.")
    education_undergrad = models.CharField(max_length=1, default="N")
    education_undergrad_major = models.CharField(max_length=100, default="")
    education_undergrad_year = models.CharField(max_length=1, default="")

    def __unicode__(self):
        return self.user.username


# information about the user's experience of the AB Search App, will be obtained from final questionnaire
class Experience(models.Model):
    user = models.OneToOneField(User)  # link to user profile

    # level of ease of use of AB Search App
    ease = models.CharField(max_length=1, default="")

    # level of boredom experienced by user when using AB Search App
    boredom = models.CharField(max_length=1, default="")

    # level of rage experienced by user when using AB Search App
    rage = models.CharField(max_length=1, default="")

    # level of frustration experienced by user when using AB Search App
    frustration = models.CharField(max_length=1, default="")

    # level of excitement experienced by user when using AB Search App
    excitement = models.CharField(max_length=1, default="")

    # level of indifference experienced by user when using AB Search App
    indifference = models.CharField(max_length=1, default="")

   # level of confusion experienced by user when using AB Search App
    confusion = models.CharField(max_length=1, default="")

    # level of anxiety experienced by user when using AB Search App
    anxiety = models.CharField(max_length=1, default="")

    # any additional comments the user wishes to add about their experience of the AB Search App
    comment = models.CharField(max_length=200, default="")

    def __unicode__(self):
        return self.user.username



