from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})




@register.filter
def abs_value(value):
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value
    

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

