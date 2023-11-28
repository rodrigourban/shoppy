from django import forms

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("content",)
        labels = {"content": "Type a message"}
        widgets = {
            "content": forms.Textarea(
                attrs={"class": "w-full py-4 px-6 rounded-xl border"}
            )
        }
