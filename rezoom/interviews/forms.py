from django import forms
from .models import EmployeeAvailability
from companies.models import OfficeLocation

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = EmployeeAvailability
        fields = ["start", "end", "is_bookable"]
        widgets = {
            "start": forms.DateTimeInput(attrs={"type":"datetime-local"}),
            "end": forms.DateTimeInput(attrs={"type":"datetime-local"}),
        }


class CandidateScheduleForm(forms.Form):
    slot = forms.ChoiceField(choices=[], widget=forms.RadioSelect)
    mode = forms.ChoiceField(choices=[("online","Online"), ("inperson","In person")])
    location = forms.ModelChoiceField(queryset=OfficeLocation.objects.none(), required=False)
    location_text = forms.CharField(required=False)

    def set_slot_choices(self, slots):
        # slots = queryset of EmployeeAvailability with select_related("employee__user")
        choices = []
        for s in slots:
            who = s.employee.user.get_full_name() or s.employee.user.username
            label = f"{who} — {s.start:%b %d, %Y %I:%M %p} → {s.end:%I:%M %p}"
            choices.append((str(s.id), label))
        self.fields["slot"].choices = choices

    def set_location_qs(self, qs):
        self.fields["location"].queryset = qs