import re
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

class FormRegistro(forms.Form):

    nombre = forms.CharField(
        label="Nombre completo",
        max_length=255,
        min_length=2,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'  # Placeholder
        })
    )

    username = forms.CharField(
        label="Nombre de usuario",
        max_length=64,
        min_length=3,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'  # Placeholder
        })
    )

    correo = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'  # Placeholder
        })
    )    

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'id': 'password',
            'class': 'form-control',
            'placeholder': 'Contraseña'  # Placeholder
        }),
        required=True
    )

    # Nuevo campo: Selección del rol
    ROLES_CHOICES = [
        (2, 'Comprador'),
        (3, 'Vendedor'),        
    ]

    rol = forms.ChoiceField(
        label="Rol",
        choices=ROLES_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Selecciona tu rol'
        })
    )

    # Validación personalizada del nombre
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) > 30:
            raise ValidationError('El nombre no debe tener más de 30 caracteres.')
        # Validar que no contenga dígitos (números)
        if any(char.isdigit() for char in nombre):
            raise ValidationError('El nombre completo no puede contener dígitos.')            
        if nombre.isdigit():
            raise ValidationError('El nombre completo no puede contener solo números.')
        return nombre

    # Validación personalizada del nombre de usuario
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) > 30:
            raise ValidationError('El nombre de usuario no debe tener más de 30 caracteres.')
        if username.isdigit():
            raise ValidationError('El nombre de usuario no puede contener solo números.')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError('El nombre de usuario solo puede contener letras, números y guiones bajos.')
        return username

    # Validación personalizada de la contraseña
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('La contraseña debe tener al menos una letra mayúscula.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('La contraseña debe tener al menos una letra minúscula.')
        if not re.search(r'\d', password):
            raise ValidationError('La contraseña debe tener al menos un número.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('La contraseña debe tener al menos un carácter especial.')
        return password
    
class FormLogin(forms.Form):
    
    correo = forms.EmailField(
        label="Correo electronico",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )    

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                'id': 'password',
                'class': 'form-control',
                'placeholder': 'Contraseña',
                'autocomplete': 'off'
            }
        ),
        required=True,
    )