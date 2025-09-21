from django import forms
from .models import User, UserProfile
import json

class ProfileForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=150, required=False)
    last_name  = forms.CharField(max_length=150, required=False)

    # Friendly inputs (we’ll convert to JSON lists)
    skills_text       = forms.CharField(required=False, help_text="Comma-separated (e.g., Django, GSAP, Lenis)")
    interests_text    = forms.CharField(required=False, help_text="Comma-separated")
    languages_text    = forms.CharField(required=False, help_text="Comma-separated")
    education_text    = forms.CharField(widget=forms.Textarea, required=False,
                                        help_text="One per line (e.g., B.Tech @ IIT, 2025)")
    experience_text   = forms.CharField(widget=forms.Textarea, required=False,
                                        help_text="One per line (e.g., Backend Intern @ FooCo, 6 months)")
    # Projects are built with small rows in the UI; we’ll serialize into this hidden field
    projects_json     = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = UserProfile
        fields = [
            "profile_photo", "birthdate", "gender", "address",
            "contract_type", "visa_status", "github_url", "resume",
            # the text helpers above + hidden projects_json handle JSON fields
        ]
        widgets = {
            "birthdate": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user: User = None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        prof: UserProfile = self.instance

        # Prefill helper fields from existing JSON where possible
        self.fields["first_name"].initial = user.first_name if user else ""
        self.fields["last_name"].initial  = user.last_name if user else ""

        self.fields["skills_text"].initial     = ", ".join(prof.skills or [])
        self.fields["interests_text"].initial  = ", ".join(prof.interests or [])
        self.fields["languages_text"].initial  = ", ".join(prof.languages or [])
        self.fields["education_text"].initial  = "\n".join(prof.education or [])
        self.fields["experience_text"].initial = "\n".join(prof.experience or [])
        self.fields["projects_json"].initial   = json.dumps(prof.projects or [])

    @staticmethod
    def _csv_to_list(text: str):
        return [x.strip() for x in text.split(",") if x.strip()] if text else []

    @staticmethod
    def _lines_to_list(text: str):
        return [x.strip() for x in text.splitlines() if x.strip()] if text else []

    def clean_projects_json(self):
        raw = self.cleaned_data.get("projects_json") or "[]"
        try:
            data = json.loads(raw)
            if not isinstance(data, list):
                raise ValueError("projects_json must be a list")
            # normalize keys
            norm = []
            for p in data:
                if not isinstance(p, dict):  # allow basic strings if user hacks it
                    norm.append({"title": str(p), "technologies": [], "github": ""})
                    continue
                norm.append({
                    "title": p.get("title","").strip(),
                    "technologies": [t.strip() for t in (p.get("technologies") or []) if t.strip()],
                    "github": (p.get("github") or "").strip(),
                })
            return norm
        except Exception:
            raise forms.ValidationError("Projects data is invalid. Please re-add your projects.")

    def save(self, commit=True):
        prof: UserProfile = super().save(commit=False)
        cd = self.cleaned_data

        # user core fields
        if self.user:
            self.user.first_name = cd.get("first_name", "") or ""
            self.user.last_name  = cd.get("last_name", "") or ""
            if commit:
                self.user.save()

        # map helpers → JSON fields
        prof.skills     = self._csv_to_list(cd.get("skills_text",""))
        prof.interests  = self._csv_to_list(cd.get("interests_text",""))
        prof.languages  = self._csv_to_list(cd.get("languages_text",""))
        prof.education  = self._lines_to_list(cd.get("education_text",""))
        prof.experience = self._lines_to_list(cd.get("experience_text",""))
        prof.projects   = cd.get("projects_json") or []

        if commit:
            prof.save()
        return prof
