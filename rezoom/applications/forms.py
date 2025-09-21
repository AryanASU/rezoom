from django import forms

class ApplyForm(forms.Form):
    resume_file = forms.FileField(required=False, help_text="Optional: upload a different resume for this job.")

class ReviewDecisionForm(forms.Form):
    decision = forms.ChoiceField(choices=[("approve","Approve"),("reject","Reject")])
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":3}))
