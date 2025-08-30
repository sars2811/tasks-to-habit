from django import forms


class TaskListTrackingForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
        label="Task List Name",
    )
    to_track = forms.BooleanField(required=False, label="Track this list?")
    id = forms.CharField(widget=forms.HiddenInput())
