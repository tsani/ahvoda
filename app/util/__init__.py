from flask import render_template

def render_template_with_data(template, **kwargs):
    """ Render a template and give it access to the data module containing many
    useful constants and data for forms.
    """
    return render_template(template, data=data, **kwargs)

from . import mailchimp, data
