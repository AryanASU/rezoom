from django import forms
from .models import Job, JobAssignee
from companies.models import Company, Employee

BENEFIT_CHOICES = [
    ("healthcare","Healthcare"),("dental","Dental"),("vision","Vision"),
    ("pto","Paid time off"),("parental","Parental leave"),("retirement","401k/retirement"),
    ("remote_stipend","Remote stipend"),("equipment","Equipment budget"),
    ("learning","Learning budget"),("bonus","Annual bonus"),
]

PAY_PERIOD_CHOICES = [("year","Per year"),("month","Per month"),("hour","Per hour")]

class JobForm(forms.ModelForm):
    # Friendly inputs for JSON fields
    req_quals_text   = forms.CharField(required=False, help_text="Comma-separated", label="Required qualifications")
    pref_quals_text  = forms.CharField(required=False, help_text="Comma-separated", label="Preferred qualifications")
    perf_metrics_text= forms.CharField(required=False, help_text="Comma-separated", label="Performance metrics")
    tools_text       = forms.CharField(required=False, help_text="Comma-separated", label="Tools/tech stack")
    benefits_choice  = forms.MultipleChoiceField(
        required=False, choices=BENEFIT_CHOICES, widget=forms.CheckboxSelectMultiple
    )
    pay_period = forms.ChoiceField(choices=PAY_PERIOD_CHOICES, required=False)

    # Select employees (assignees)
    assignees = forms.MultipleChoiceField(
        required=False, widget=forms.SelectMultiple(attrs={"size": 6}),
        label="Assign employees (review/interview)"
    )

    deadline = forms.DateField(required=False, widget=forms.DateInput(attrs={"type":"date"}))

    class Meta:
        model = Job
        fields = [
            "company","title","department","manager","manager_name","emp_type",
            "location_mode","location_text","deadline",
            "role_purpose","description_md","responsibilities_md",
            "salary_min","salary_max","currency","pay_period",
            "visa_sponsorship","background_check_required","security_clearance","eeo_text",
        ]
        widgets = {
            "role_purpose": forms.Textarea(attrs={"rows":3}),
            "description_md": forms.Textarea(attrs={"rows":6}),
            "responsibilities_md": forms.Textarea(attrs={"rows":6}),
            "eeo_text": forms.Textarea(attrs={"rows":3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # HR can only post for companies they created
        self.fields["company"].queryset = Company.objects.filter(created_by=user)
        # Start with empty assignees; we’ll populate in view via company or AJAX
        self.fields["assignees"].choices = []

        # Prefill “text” helpers from instance JSON (edit flow)
        if self.instance and self.instance.pk:
            self.fields["req_quals_text"].initial    = ", ".join(self.instance.req_quals or [])
            self.fields["pref_quals_text"].initial   = ", ".join(self.instance.pref_quals or [])
            self.fields["perf_metrics_text"].initial = ", ".join(self.instance.perf_metrics or [])
            self.fields["tools_text"].initial        = ", ".join(self.instance.tools or [])
            self.fields["benefits_choice"].initial   = self.instance.benefits or []
            self.fields["pay_period"].initial        = self.instance.pay_period or "year"

    @staticmethod
    def _csv(text): return [t.strip() for t in (text or "").split(",") if t.strip()]

    def save(self, commit=True):
        job = super().save(commit=False)
        cd = self.cleaned_data
        # Map helpers to JSON fields
        job.req_quals     = self._csv(cd.get("req_quals_text"))
        job.pref_quals    = self._csv(cd.get("pref_quals_text"))
        job.perf_metrics  = self._csv(cd.get("perf_metrics_text"))
        job.tools         = self._csv(cd.get("tools_text"))
        job.benefits      = cd.get("benefits_choice") or []
        job.pay_period    = cd.get("pay_period") or "year"
        if commit: job.save()
        self._assignees_ids = cd.get("assignees") or []  # stash for view to create JobAssignee rows
        return job
