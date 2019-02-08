from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import StringField, PasswordField, SubmitField,\
    BooleanField, Form, FileField, IntegerField, SelectField


# it handles Category form submission errors and form cleaning
class CategoryForm(Form):
    name = StringField('Category Name', validators=[DataRequired(),
                       Length(min=2, max=20)])
    submit = SubmitField('Add')


# it handles Item form submission errors and form cleaning
class ItemForm(Form):
    name = StringField('Item Name', validators=[DataRequired(),
                       Length(min=2, max=50)])
    description = StringField('Description', validators=[DataRequired(),
                              Length(min=10, max=1000)])
    image = StringField('Image', validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired(),
                        Length(min=2, max=30)])
    price = IntegerField('Price', validators=[DataRequired()])
    category = SelectField('Category', choices=[], coerce=int)
    submit = SubmitField('Add')
