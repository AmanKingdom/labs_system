from django.forms import Form, fields


class LoginForm(Form):
    username = fields.CharField()
    password = fields.CharField()
