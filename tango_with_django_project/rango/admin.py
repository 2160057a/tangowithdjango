from django.contrib import admin
from rango.models import Category, Page

class PageAdmin(admin.ModelAdmin):

	list_display = ('title', 'category', 'url', 'views')

class CategoryAdmin(admin.ModelAdmin):
	prepopulated_Fields ={'slug':('name',)}

	list_display = ('name', 'views', 'likes')
	
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
