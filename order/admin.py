import csv
import datetime
from django.contrib import admin
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import Order, OrderItem



def export_to_csv(modeladmin, request, queryset):
  opts = modeladmin.model._meta
  content_disposition = f'attatchment; filename={opts.verbose_name}.csv'
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = content_disposition
  writer = csv.writer(response)
  fields = [field for field in opts.get_fields() if not \
            field.many_to_many and not field.one_to_many]
  # write header information
  writer.writerow([field.verbose_name for field in fields])
  # write data 
  for obj in queryset:
    data_row = []
    for field in fields:
      value = getattr(obj, field.name)
      if isinstance(value, datetime.datetime):
        value = value.strftime('%d/%m/%Y')
      data_row.append(value)
    writer.writerow(data_row)
  
  return response

export_to_csv.short_description = 'Export to CSV'

def order_detail(obj):
  url = reverse('order:admin_order_detail', args=[obj.id])
  return mark_safe(f"<a href='{url}'>View</a>")

def order_pdf(obj):
  url = reverse('order:admin_order_pdf', args=[obj.id])
  return mark_safe(f"<a href='{url}'>PDF</a>")
order_pdf.short_description = 'Invoice'
class OrderItemInline(admin.TabularInline):
  model = OrderItem
  raw_id_fields = ['product']

class OrderAdmin(admin.ModelAdmin):
  list_display = ['id', 'first_name', 'last_name', 'email',
                  'address', 'zipcode', 'city', 'paid',
                  'status', 'created_at', order_detail,
                  order_pdf]
  list_filter = ['paid', 'status', 'created_at']
  search_fields = ['first_name', 'address']
  inlines = [OrderItemInline]
  actions = [export_to_csv]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
