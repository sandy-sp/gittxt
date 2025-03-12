from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Optional, URL

class ScanForm(FlaskForm):
    repo_url = StringField('Repository URL or Path', validators=[DataRequired()])
    output_format = SelectMultipleField(
        'Output Format',
        choices=[('txt', 'Text'), ('json', 'JSON'), ('md', 'Markdown')],
        default=['txt']
    )
    include_patterns = StringField('Include Patterns (comma-separated)', validators=[Optional()])
    exclude_patterns = StringField('Exclude Patterns (comma-separated)', validators=[Optional()])
    size_limit = IntegerField('Size Limit (bytes)', validators=[Optional()])
    docs_only = BooleanField('Documentation Files Only')
    auto_filter = BooleanField('Auto-filter Common Unwanted Files')
