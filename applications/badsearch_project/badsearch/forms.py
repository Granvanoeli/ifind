from django import forms
from badsearch.models import UserProfile, Demographics, Experience
from django.contrib.auth.models import User

GENDER_CHOICES = (('Not Indicated', 'Not Indicated'),
                  ('Male', 'Male'), ('Female', 'Female'))

YES_CHOICES = (('Not Indicated', 'Not Indicated'),
               ('Yes', 'Yes'), ('No', 'No'))

YEAR_CHOICES = (('Not Indicated', 'Not Indicated'),
                ('First Year', 'First Year'), ('Second Year', 'Second Year'), ('Third Year', 'Third Year'),
                ('Fourth Year', 'Fourth Year'), ('Fifth Year', 'Fifth Year'), ('Completed', 'Completed'))


EXPERIENCE_CHOICES = (('A', 'Agree'), ('U', 'Unsure'), ('D', 'Disagree'))


class UserForm(forms.ModelForm):
    username = forms.CharField(label="Username")
    email = forms.CharField(label="Email")
    password = forms.CharField(label="Password",widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput(),label='Repeat Password')

    def clean(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password != password2:
            raise forms.ValidationError("Your passwords do not match")
        #return password2

        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(pk=self.instance.pk).get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u'Username "%s" is already in use.' % username)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        for fieldname in ['username']:
            self.fields[fieldname].help_text = None


    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture',)


class DemographicsForm(forms.ModelForm):
    age = forms.IntegerField(label="Please provide your age (in years)", max_value=100, required=False)
    sex = forms.CharField(max_length=20, widget=forms.Select(choices=GENDER_CHOICES), label="Please indicate your sex",
                          required=False)
    education_undergrad = forms.CharField(widget=forms.Select(choices=YES_CHOICES),
                                          label="Are you undertaking, or have you obtained, an undergraduate degree?",
                                          required=False)
    education_undergrad_major = forms.CharField(widget=forms.TextInput(attrs={'size': '60', 'class': 'inputText'}),
                                                label="If yes, what is/was your subject area?", required=False)
    education_undergrad_year = forms.CharField(widget=forms.Select(choices=YEAR_CHOICES),
                                               label="What year are you in?", required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get("age"):
            cleaned_data["age"] = 0
            print "clean age"
        return cleaned_data

   # def clean(self):
      #  user_age = self.cleaned_data['age']
      #  if user_age < 18:
       #     raise forms.ValidationError('You must be at least 18 years old to register')
        #return self.cleaned_data

    class Meta:
        model = Demographics
        exclude = ('user',)


class ValidationForm(forms.Form):
    terms = forms.BooleanField(required=True, initial=False,
                               label="I have read and agree to the above Study Information and I have had the opportunity to ask any questions",
                               error_messages={'required': 'You must accept the terms and conditions'}, )
    questions = forms.BooleanField(required=True, initial=False,
                               label="I understand that I am able to ask questions about this study at any time",
                               error_messages={'required': 'You must accept the terms and conditions'}, )
    name = forms.BooleanField(required=True, initial=False,
                               label="I understand that my name will not appear in any published document relating to research conducted as part of this study",
                               error_messages={'required': 'You must accept the terms and conditions'}, )
    info = forms.BooleanField(required=True, initial=False,
                               label="I am willing for anonymous data from my search sessions and questionnaires that I have submitted may be quoted in papers, journal articles and books that may be written by the researchers",
                               error_messages={'required': 'You must accept the terms and conditions'}, )
    agree = forms.BooleanField(required=True, initial=False,
                               label="I agree to take part in this study",
                               error_messages={'required': 'You must accept the terms and conditions'}, )
    age = forms.BooleanField(required=True, initial=False, label="I certify that I am aged 18 or over",
                             error_messages={'required': 'You must be 18 or over to participate in the experiment'},)
    notify = forms.BooleanField(required=False, initial=False,
                               label="I would like to be notified by email of the outcome of this experiment",
                               error_messages={'required': 'You must accept the terms and conditions'}, )

class FinalQuestionnaireForm(forms.ModelForm):
    ease = forms.ChoiceField(widget=forms.RadioSelect(), choices=EXPERIENCE_CHOICES, label='The search engine was '
                                                                                           'easy to use:')
    boredom = forms.ChoiceField(widget=forms.RadioSelect(), choices=EXPERIENCE_CHOICES, label='I quickly became bored '
                                                                                              'while using the search '
                                                                                              'engine:')
    rage = forms.ChoiceField(widget=forms.RadioSelect(), choices=EXPERIENCE_CHOICES, label='I was enraged by the search'
                                                                                           ' engine:')
    frustration = forms.ChoiceField(widget=forms.RadioSelect(), choices=EXPERIENCE_CHOICES, label='I was frustrated by '
                                                                                                  'the search engine:')
    excitement = forms.ChoiceField(widget=forms.RadioSelect(), choices=EXPERIENCE_CHOICES, label='I was excited while'
                                                                                                 ' using the search'
                                                                                                 ' engine:')
    indifference = forms.ChoiceField(widget=forms.RadioSelect(), choices=EXPERIENCE_CHOICES, label='I was indifferent '
                                                                                                   'to the search '
                                                                                                   'engine:')
    confusion = forms.ChoiceField(widget=forms.RadioSelect(), choices=EXPERIENCE_CHOICES, label='I was confused by the'
                                                                                                ' search engine:')
    anxiety = forms.ChoiceField(widget=forms.RadioSelect(), choices=EXPERIENCE_CHOICES, label='I was anxious when '
                                                                                              'using the search '
                                                                                              'engine:')
    comment = forms.CharField(widget=forms.Textarea, label='Please add any other comments you may have about '
                                                           'Slowsearch:')

    class Meta:
        model = Experience
        exclude= ('user',)