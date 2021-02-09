from django import forms

class kayitform(forms.Form):
    kullanici_adi = forms.CharField(max_length=16, required=True, help_text='Benzersiz bir kullanıcı adını seçin. (1-16 Karakter)')
    gercek_isim = forms.CharField(max_length=16, required=False, help_text='Zorunlu değil')
    email = forms.EmailField(max_length=254, required=True, help_text='Ulaşabildiğiniz bir email adresi girin')
    dogum_yili = forms.CharField(max_length=4, required=True, help_text='Zorunlu')
