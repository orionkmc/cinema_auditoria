# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# import md5
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import date as _date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import mark_safe
from tinymce.models import HTMLField
# from .coupons import redeem_coupon
from datetime import timedelta

TARGET_CHOICES = [
    ('_self', 'Misma página'),
    ('_blank', 'Nueva pestaña')
]

ADS_POSITIONS = [
    ('home_426x400', 'Home - Lateral 426x400'),
    ('single_426x400', 'Pelicula - Lateral 426x400'),
    ('single_980x120', 'Pelicula - Horizontal 980x120'),
    ('home_800x200', 'Home - Centro 800x200 Tablet/Mobile'),
    ('home_400x200', 'Home - Lateral 400x200'),
    ('home_600x300', 'Home - Lateral 600x300'),
    ('home_200x500', 'Home - Lateral 200x500')
]

GENRE_USER = (
    ('M', 'Masculino'),
    ('F', 'Femenino'),
)

COUPONS = (
    ('arnet', 'ARNET'),
    ('clarin_365', 'CLARIN 365'),
    ('movieclub', 'MOVIECLUB'),
    ('personal', 'PERSONAL'),
    ('ypf', 'YPF'),
    ('movistr', 'MOVISTAR'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    genre = models.CharField(
        max_length=1, choices=GENRE_USER, verbose_name='Sexo')
    date_of_birth = models.DateField(verbose_name='Fecha de Nacimiento')
    mobile_phone = models.CharField(max_length=20, verbose_name='Celular')
    fb_id = models.CharField(
        max_length=100, null=True, verbose_name='Facebook ID')

    class Meta:
        verbose_name = 'Perfíl'
        verbose_name_plural = 'Perfiles'

    def __unicode__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)


class PopupHome(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.CharField(max_length=250, verbose_name='Imagen', blank=True)
    link = models.CharField(
        max_length=150, null=True, blank=True, verbose_name='Vínculo')

    class Meta:
        verbose_name = "pupup home"
        verbose_name_plural = "Popups"

    def admin_thumbnail(self):
        return u'<img src="%s" width="640" height="480" />' % self.image
    admin_thumbnail.short_description = 'Thumbnail'
    admin_thumbnail.allow_tags = True


class Ads(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.CharField(max_length=250, verbose_name='Imagen')
    position = models.CharField(
        max_length=25, choices=ADS_POSITIONS, verbose_name='Posición')
    title = models.CharField(max_length=100, verbose_name='Título')
    link = models.CharField(
        max_length=150, null=True, blank=True, verbose_name='Vínculo')
    target = models.CharField(
        choices=TARGET_CHOICES, max_length=20, blank=True,
        verbose_name='Abrir en')

    class Meta:
        verbose_name = "publicidad"
        verbose_name_plural = "Publicidades"

    def admin_thumbnail(self):
        return u'<img src="%s"  />' % self.image
    admin_thumbnail.short_description = 'Thumbnail'
    admin_thumbnail.allow_tags = True


class HomeSlide(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.CharField(max_length=250, verbose_name='Imagen')
    title = models.CharField(max_length=150, verbose_name='Título')
    link = models.CharField(
        max_length=150, null=True, blank=True, verbose_name='Vínculo')
    target = models.CharField(
        choices=TARGET_CHOICES, max_length=20, blank=True,
        verbose_name='Abrir en')
    order = models.IntegerField(verbose_name='Orden', default=0)

    def __unicode__(self):
        return self.title

    def admin_thumbnail(self):
        return u'<img src="%s" width="%s" height="%s" />' \
            % (self.image, 500, 200)
    admin_thumbnail.short_description = 'Thumbnail'
    admin_thumbnail.allow_tags = True

    class Meta:
        verbose_name = "slide"
        verbose_name_plural = "Home - Slider"


class Sell(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, verbose_name='Usuario', on_delete=models.CASCADE)
    film_title = models.CharField(max_length=150, verbose_name='Película')
    cinema_id = models.CharField(max_length=20, verbose_name='Cine')
    session_id = models.CharField(max_length=20, verbose_name='Sesión')
    showtime = models.DateTimeField(
        auto_now=False, auto_now_add=False, verbose_name='Función')
    total = models.FloatField()
    vista_booking_id = models.CharField(
        max_length=50, blank=True, verbose_name='Código de Kiosko')
    external_reference = models.CharField(
        max_length=50, verbose_name='Código Mercadopago')
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de Venta')
    user_session_id = models.CharField(
        max_length=50, blank=True)
    vista_trans_id = models.CharField(
        max_length=50, blank=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    def admin_success(self):
        try:
            pago = self.pago.all()[0]
            if pago.status == 'approved':
                return 'Pago'
            else:
                return 'No Pago'
        except:
            return 'No pago'
    admin_success.short_description = 'Estado'

    def admin_payment_date(self):
        try:
            pago = self.pago.all()[0]
            return pago.date_approved
        except:
            return ''
    admin_payment_date.short_description = 'Fecha de pago'

    def admin_description(self):
        return '#%s %s - %s' % \
            (self.id, self.film_title, _date(
                self.showtime - timedelta(hours=3), 'l d \d\e F H:i'))
    admin_success.short_description = 'Venta'

    def __unicode__(self):
        return '#%s %s - %s' % \
            (self.id, self.film_title, _date(
                self.showtime - timedelta(hours=3), 'l d \d\e F H:i'))


class SellTicket(models.Model):
    id = models.AutoField(primary_key=True)
    sell = models.ForeignKey(
        Sell, related_name='tickets', on_delete=models.CASCADE)
    price = models.FloatField(verbose_name='Precio')
    seat_data = models.CharField(max_length=20, verbose_name='Butaca')
    ticket_code = models.CharField(
        max_length=20, verbose_name='Código de Ticket')
    description = models.CharField(
        max_length=50, verbose_name='Tipo de entrada')

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"

    def __unicode__(self):
        return self.seat_data


class SellCoupon(models.Model):
    id = models.AutoField(primary_key=True)
    sell = models.ForeignKey(Sell, on_delete=models.CASCADE)
    coupon = models.CharField(max_length=50, choices=COUPONS)
    code = models.CharField(max_length=50, verbose_name='Código')
    redeem = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Cupon"
        verbose_name_plural = "Cupones"

    def __unicode__(self):
        return '%s (%s)' % (self.code, self.coupon)


class MercadoPago(models.Model):
    id = models.AutoField(primary_key=True)
    sell = models.ForeignKey(
        Sell, related_name='pago', on_delete=models.CASCADE)
    status = models.CharField(max_length=80)
    collection_id = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    date_approved = models.DateTimeField(auto_now_add=False, null=True)

    def __unicode__(self):
        return 'Venta #%d - %s' % (self.sell.id, self.status)


class Price(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Tipo')
    price_2d = models.FloatField(
        blank=True, null=True, verbose_name='Precio 2D')
    price_3d = models.FloatField(
        blank=True, null=True, verbose_name='Precio 3D')
    ref = models.CharField(
        max_length=50, verbose_name='Aclaraciones', null=True)

    class Meta:
        verbose_name = "Precio"
        verbose_name_plural = "Precios"

    def __unicode__(self):
        return self.name


class Promotion(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Nombre')
    image = models.CharField(max_length=250, verbose_name='Imagen')
    description = HTMLField(verbose_name='Descripción')
    legal = HTMLField()
    due_date = models.DateField(verbose_name='Valido hasta')

    class Meta:
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'

    def __unicode__(self):
        return mark_safe('%s %s' % (self.name, self.description))

    def admin_description(self):
        return self.description
    admin_description.short_description = 'Descripción'
    admin_description.allow_tags = True

    def admin_thumbnail(self):
        return u'<img src="%s" width="%s" height="%s" />' \
            % (self.image, 100, 100)
    admin_thumbnail.short_description = 'Imagen'
    admin_thumbnail.allow_tags = True


# @receiver(post_save, sender=Sell)
# def create_external_reference(sender, instance, created, **kwargs):
#     if created:
#         instance.external_reference = md5.new(str(instance.id)).hexdigest()
#         instance.save()


# @receiver(post_save, sender=SellCoupon)
# def save_redeem_coupon(sender, instance, created, **kwargs):
#     if created:
#         redeem_coupon(instance.coupon, instance.code)
