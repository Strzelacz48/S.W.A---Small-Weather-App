from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def icon(name, css_class="w-4 h-4"):
    """Render an inline SVG icon by name from templates/icons/<name>.svg (Tabler icons, https://tabler.io/icons)."""
    svg = render_to_string(f"icons/{name}.svg", {"css_class": css_class})
    return mark_safe(svg)