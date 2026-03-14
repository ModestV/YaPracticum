from django import forms


class ComposeMessageForm(forms.Form):
    recipient_email = forms.EmailField(
        required=False,
        label="Кому",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "friend@example.com",
            }
        ),
    )
    subject = forms.CharField(
        max_length=255,
        label="Тема",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Очень важная тема письма",
            }
        ),
    )
    body = forms.CharField(
        label="Текст письма",
        widget=forms.Textarea(
            attrs={
                "rows": 12,
                "placeholder": "Напишите что-нибудь. Можно даже немного неловкое письмо.",
            }
        ),
    )
