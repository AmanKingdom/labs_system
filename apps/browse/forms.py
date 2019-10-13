from django.forms import Form, fields


class LoginForm(Form):
    account = fields.CharField()
    password = fields.CharField()
