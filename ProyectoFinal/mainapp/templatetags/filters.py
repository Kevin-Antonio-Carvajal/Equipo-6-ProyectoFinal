from django import template
from django.utils.timezone import localtime, now

register = template.Library()

@register.filter(name='formato_fecha')
def formato_fecha(fecha):
    """
    Formatea la fecha de un mensaje:
    - Si fue enviado hoy: muestra la hora (HH:MM).
    - Si no: muestra "X d", donde X es la diferencia en días.
    """
    fecha_local = localtime(fecha)
    fecha_actual = localtime(now())
    diferencia_dias = (fecha_actual.date() - fecha_local.date()).days

    if diferencia_dias == 0:
        return fecha_local.strftime('%H:%M')  # Muestra la hora si fue enviado hoy
    return f"{diferencia_dias} d"  # Muestra la diferencia en días