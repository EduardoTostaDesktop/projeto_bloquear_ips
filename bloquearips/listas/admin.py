from django.contrib import admin
from .models import Lista

@admin.register(Lista)
class ListaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'data_desbloqueio_padrao', 'criado_por', 'criado_em')
    search_fields = ('nome', 'descricao')
    list_filter = ('criado_em',)
