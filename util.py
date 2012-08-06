import jinja2
import json
import re
import settings

from contrib.unidecode import unidecode
from google.appengine.api import users
from math import floor

from models.userprefs import UserPrefs

# Setup the Jinja2 template environment
JINJA_ENV = jinja2.Environment(**{
    'loader': jinja2.FileSystemLoader(settings.TEMPLATE_PATH)
})

# The logout url, if a user is currently logged in
LOGOUT_URL = users.create_logout_url('/')

# A mapping of award names to icon, description pairs
AWARDS = {
    'donated': ['gift', 'Donated'],
    'liked15': ['heart', 'Liked 15 brews'],
    'created10': ['book', 'Created 10 brews']
}


def render(handler, template, params=None):
    """
    Render a page through Jinja2, passing in optional parameters.
    """
    p = params and params.copy() or {}
    p.update({
        'debug': settings.DEBUG,
        'user': UserPrefs.get(),
        'is_admin': users.is_current_user_admin(),
        'logout_url': LOGOUT_URL
    })

    t = JINJA_ENV.get_template(template)
    handler.response.out.write(t.render(p))


def render_json(handler, value):
    """
    Render a Python object as JSON.
    """
    handler.response.headers['Content-Type'] = 'application/json'
    handler.response.out.write(json.dumps(value))


def slugify(value):
    """
    Return a slugified version of a string, removing strange
    unicode characters and replacing whitespace with dashes.
    """
    return re.sub(r'\W+', '-', unidecode(value).lower())

JINJA_ENV.filters['slugify'] = slugify


def render_fermentable_template(values):
    """
    Render a fermentable template list item for the buttons which add a
    new fermentable item to the recipe.
    """
    return '<li data-description="%(description)s" data-ppg="%(ppg)d" data-srm="%(srm)d" onclick="Recipe.addFermentableRow(this);"><a><span class="srm" data-srm="%(srm)d"></span> %(description)s</a></li>' % {
        'description': values[0],
        'ppg': values[1],
        'srm': values[2]
    }

JINJA_ENV.filters['render_fermentable_template'] = render_fermentable_template


def render_hops_template(values):
    """
    Render a hop or spice template list item for the buttons which add
    a new hop or spice item to the recipe.
    """
    rating = ''

    # Only show rating information for hops
    if values[1]:
        for i in range(3):
            rating += '<i class="icon-asterisk"'
            if i >= values[1] / 5.0:
                rating += 'style="opacity: 0.2"'
            rating += '></i>'

    return '<li data-description="%(description)s" data-aa="%(aa)s" onclick="Recipe.addHopRow(this);"><a>%(rating)s %(description)s</a></li>' % {
        'description': values[0],
        'aa': values[1],
        'rating': rating
    }

JINJA_ENV.filters['render_hops_template'] = render_hops_template


def render_yeast_template(values):
    """
    Render a yeast or bug template list item for the buttons which add a
    new yeast or bug item to the recipe.
    """
    return '<li data-description="%(description)s" data-type="%(type)s" data-form="%(form)s" data-attenuation="%(attenuation)s" onclick="Recipe.addYeastRow(this);"><a>%(description)s</a></li>' % {
        'description': values[0],
        'type': values[1],
        'form': values[2],
        'attenuation': values[3]
    }

JINJA_ENV.filters['render_yeast_template'] = render_yeast_template


def weight_whole(value):
    """
    Get the whole part of a weight. E.g. for a weight of 8.6, this would
    return 8.
    """
    return int(floor(value))

JINJA_ENV.filters['weight_whole'] = weight_whole


def weight_fractional(value, parts):
    """
    Get the fractional part of a weight, given a number of parts. E.g. for
    8.6 and 16 parts, this would return 10.
    """
    return int(round((value - floor(value)) * parts))

JINJA_ENV.filters['weight_fractional'] = weight_fractional


def render_awards(values):
    """
    Render a list of awards for a user, or if the user has none display the
    message 'No Awards!'.
    """
    return ' '.join(['<i class="icon-%(image)s" title="%(title)s"></i>' % {
        'image': AWARDS[item][0],
        'title': AWARDS[item][1]
    } for item in values]) or 'No Awards!'

JINJA_ENV.filters['render_awards'] = render_awards


def format_date(value, format="%d %b %Y"):
    """
    Format a date by a given strftime format string. This defaults to looking
    like:

        16 Jun 2012

    """
    return value.strftime(format)

JINJA_ENV.filters['format_date'] = format_date


def recipe_snippet(value):
    return JINJA_ENV.get_template('recipe_snippet.html').render({
        'recipe': value
    })

JINJA_ENV.filters['recipe_snippet'] = recipe_snippet