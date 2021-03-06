from datetime import datetime
from django.db.models import Q
from django.contrib import admin
from django.template.response import TemplateResponse
from website.models import Ads, HomeSlide, Promotion
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from website.models import UserProfile, Sell, SellTicket, MercadoPago, Price, \
    SellCoupon, PopupHome
from django_object_actions import DjangoObjectActions


class PopupHomeAdmin(admin.ModelAdmin):
    list_display = ('admin_thumbnail', )

    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    inline_classes = ('grp-collapse grp-open',)


class SellInline(admin.StackedInline):
    model = Sell
    can_delete = False
    max_num = 0
    verbose_name_plural = 'Ventas'
    inline_classes = ('grp-collapse grp-open',)
    fields = ('vista_booking_id', )
    readonly_fields = ('vista_booking_id', )


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, SellInline)
    fieldsets = (
        (None, {
            'fields': ('email', 'password', 'first_name', 'last_name')}),
        ('permissions', {
            'classes': ('grp-collapse grp-closed',),
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions')
        }),

    )


class SellTicketInline(admin.TabularInline):
    model = SellTicket
    can_delete = False
    verbose_name_plural = 'Perfil'
    readonly_fields = ('ticket_code', 'description', 'price', 'seat_data')


class SellCouponInline(admin.TabularInline):
    model = SellCoupon
    can_delete = False
    verbose_name_plural = 'Cupones'
    readonly_fields = ('coupon', 'code', 'redeem')
    extra = 0


class PaymentListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Pago'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'payment'

    def lookups(self, request, model_admin):
        return (
            # ('Si', 'Si'),
            ('No', 'No'),
            ('err', 'Error'),
            ('err2', 'Error No Pago'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Si':
            ids = MercadoPago.objects.filter(status='approved')\
                .values_list('sell__id', flat=True)
            return queryset.filter(id__in=ids)
        if self.value() == 'No':
            ids = MercadoPago.objects.filter(status='approved')\
                .values_list('sell_id', flat=True)
            return queryset.exclude(id__in=ids)
        if self.value() == 'err2':
            ids = MercadoPago.objects.filter(status='approved')\
                .values_list('sell_id', flat=True)
            return queryset.exclude(id__in=ids).exclude(vista_booking_id='')
        if self.value() == 'err':
            ids = MercadoPago.objects.filter(status='approved')\
                .values_list('sell_id', flat=True)
            return queryset.filter(id__in=ids, vista_booking_id='')


class AuditoriaFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Auditoria'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'auditoria'

    def lookups(self, request, model_admin):
        return (
            ('VOUCHER', 'VOUCHER'),
            ('MOVIECLUB PASE', 'MOVIECLUB PASE'),
            ('m/v', 'MOVIECLUB PASE/VOUCHER'),
            ('m/v/er', 'MOVIECLUB PASE/VOUCHER/ENTRADA REGULAR'),
            ('er', 'ENTRADA REGULAR'),
        )

    def queryset(self, request, queryset):
        fecha = '01/12/2019'
        d_fecha = datetime.strptime(fecha, '%d/%m/%Y')
        a = ['VOUCHER WEB', 'MOVIECLUB PASE']
        b = [
            'MARATON WEB', 'GENERAL WEB', 'GENERAL 3D WEB', 'MATINEE WEB',
            'LUNES/MARTES WEB', 'LUNES/MART 3D WEB', 'MIERCOLES WEB',
            'MIERCOLES 3D WEB', 'MENOR WEB', 'JUBILADO WEB',
            'A MIERCOLES WEB', 'A MENOR-JUBILADO 3D WEB', 'MATINEE 3D WEB',
            'A MIERCOLES 3D WEB', 'A MENOR-JUBILADO WEB',
            'A DESCUENTO 3D WEB', 'ANTICIPADA DESCUENTO WEB',
            'ANTICIPADA 3D WEB,' 'MENOR 3D WEB', 'JUBILADO 3D WEB',
            'ANTICIPADA WEB'
        ]

        if self.value() == 'VOUCHER':
            return queryset.filter(
                ~Q(vista_booking_id=''),
                Q(created__gte=d_fecha),
                Q(sellcoupon__isnull=True),
                ~Q(pago__status='approved'),
                tickets__description='VOUCHER WEB',
            )
        if self.value() == 'MOVIECLUB PASE':
            return queryset.filter(
                ~Q(vista_booking_id=''),
                Q(created__gte=d_fecha),
                Q(sellcoupon__isnull=True),
                ~Q(pago__status='approved'),
                tickets__description='MOVIECLUB PASE',
            )

        if (self.value() == 'm/v'):
            return queryset.filter(
                ~Q(vista_booking_id=''),
                Q(created__gte=d_fecha),
                Q(sellcoupon__isnull=True),
                ~Q(pago__status='approved'),
                Q(tickets__description__in=a),
            )
        if (self.value() == 'm/v/er'):
            return queryset.filter(
                ~Q(vista_booking_id=''),
                Q(created__gte=d_fecha),
                Q(sellcoupon__isnull=True),
                ~Q(pago__status='approved'),
                Q(tickets__description__in=a + b),
            )

        if (self.value() == 'er'):
            return queryset.filter(
                ~Q(vista_booking_id=''),
                Q(created__gte=d_fecha),
                Q(sellcoupon__isnull=True),
                ~Q(pago__status='approved'),
                Q(tickets__description__in=b),
            )


class SellAdmin(DjangoObjectActions, admin.ModelAdmin):
    inlines = (SellTicketInline, SellCouponInline)
    list_display = (
        '__unicode__', 'user', 'admin_success', 'created',
        'admin_payment_date'
    )
    list_filter = (PaymentListFilter, AuditoriaFilter, 'created', )
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'id', 'film_title')
    raw_id_fields = ('user', )

    def get_queryset(self, request):
        qs = super(SellAdmin, self).get_queryset(request)
        return qs.prefetch_related('pago')

    def auditotia(self, request, queryset):
        context = {
            'results': [1, 2, 3]
        }
        return TemplateResponse(request, "admin/audit.html", context)

    auditotia.label = "Auditar Entradas"
    auditotia.short_description = "Auditar Entradas"
    changelist_actions = ('auditotia', )


class SellCouponAdmin(admin.ModelAdmin):
    list_display = ('sell', '__unicode__', 'redeem')
    raw_id_fields = ('sell', )


class HomeSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'admin_thumbnail')
    exclude = ('movie_title', )


class AdsAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'admin_thumbnail')


class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin_thumbnail', 'admin_description')


class MercadoPagoAdmin(admin.ModelAdmin):
    list_display = ('sell', 'status', 'collection_id', 'created')
    raw_id_fields = ('sell', )


class SellTicketAdmin(admin.ModelAdmin):
    raw_id_fields = ('sell', )

# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(HomeSlide, HomeSlideAdmin)
admin.site.register(Ads, AdsAdmin)
admin.site.register(Sell, SellAdmin)
admin.site.register(SellCoupon, SellCouponAdmin)
admin.site.register(MercadoPago, MercadoPagoAdmin)
admin.site.register(Price)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(PopupHome, PopupHomeAdmin)
