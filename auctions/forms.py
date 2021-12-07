from djmoney.models.fields import MoneyField
from django import forms

class newListingForm (forms.Form):
    title = forms.CharField(required = True, max_length = 128, label='Auction title:', widget= forms.TextInput (attrs={
        'class':'form-control', 'placeholder': 'title'})) 
    #title = forms.CharField(label='Title', widget=forms.TextInput(attrs={'placeholder': 'title', 'class': 'sizeform'}))
    description = forms.CharField(required = True, label='Description:', widget=forms.Textarea(attrs={
        'placeholder': 'Describe your item here...', 'class':'form-control', 'rows':'3'}))
    price = forms.DecimalField(required = True, 
        widget=forms.NumberInput(attrs={'placeholder': 'initial Price', 'class':'form-control', 'step': 0.01, 'min':1.00, 'max':100000.00}))
    image_url = forms.URLField(required = False, widget=forms.TextInput(attrs={'placeholder': 'url (optional)', 'class':'form-control'}))

class bidForm (forms.Form):
    bid = forms.DecimalField(required = True, 
        widget=forms.NumberInput(attrs={'placeholder': 'bid', 'class':'form-control', 'step': 0.01, 'min':1.00, 'max':100000.00}))

class addCommentForm (forms.Form):
    comment = forms.CharField(required = True, widget=forms.Textarea(attrs={
        'placeholder': 'Add a comment', 'class':'form-control', 'rows':'3'}))