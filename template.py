import math


def template_circle(template_len, template_range, template_ratio) :
    template = []
    radius = template_range
    radius_square = radius * radius
    template_range = template_range * math.sin(template_ratio * math.pi / 2)
    interval = template_range * 2 / template_len

    for i in range (template_len) :
        x = i * interval - template_range + interval / 2
        template.append([i, radius - math.sqrt(radius_square - x * x)])
    return template


def template_gen(template_type, template_len, template_range, template_ratio) :
    if "circle" == template_type :
        return template_circle(template_len, template_range, template_ratio)




