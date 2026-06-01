from django import forms

from .models import Perfume


class PerfumeForm(forms.ModelForm):
    class Meta:
        model = Perfume
        fields = [
            "name",
            "brand",
            "year",
            "gender",
            "longevity",
            "description",
            "image",
            "families",
            "notes",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "brand": forms.Select(attrs={"class": "form-select"}),
            "year": forms.NumberInput(attrs={"class": "form-control", "min": 1800, "max": 2100}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "longevity": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "families": forms.CheckboxSelectMultiple,
            "notes": forms.CheckboxSelectMultiple,
        }

    def clean_year(self):
        year = self.cleaned_data.get("year")
        if year is not None and year < 1900:
            raise forms.ValidationError("Год выпуска должен быть не раньше 1900.")
        return year
