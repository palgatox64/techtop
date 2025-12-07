from django.contrib import admin
from django.urls import path
from store import views
import os
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), 
    path('contacto/', views.contacto, name='contacto'), 
    path('quienes-somos/', views.about, name='about'),
    path('seguimiento-compra/', views.seguimiento_compra, name='seguimiento_compra'),
    path('centro-ayuda/', views.centro_ayuda, name='centro_ayuda'),
    path('garantias/', views.garantias, name='garantias'),
    path('politicas-privacidad/', views.politicas_privacidad, name='politicas_privacidad'),
    path('terminos-condiciones/', views.terminos_condiciones, name='terminos_condiciones'),
    path('tienda/', views.product_catalog, name='product_catalog'),
    path('tienda/marca/<str:brand_name>/', views.product_catalog, name='product_catalog_by_brand'),
    path('radios/', views.radios_catalog, name='radios_catalog'),
    path('electronica/', views.electronica_catalog, name='electronica_catalog'),
    path('api/get-cart/', views.get_cart_data, name='get_cart_data'),
    path('accesorios/', views.accesorios_catalog, name='accesorios_catalog'),
    path('otros/', views.otros_catalog, name='otros_catalog'),
    path('categoria/<str:categoria_nombre>/', views.category_catalog, name='category_catalog'),
    path('producto/<int:product_id>/', views.product_detail, name='product_detail'),
    path('carro/', views.view_cart, name='view_cart'),
    path('agregar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('actualizar-carro/<int:product_id>/', views.update_cart, name='update_cart'),
    path('eliminar-del-carro/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'), 
    path('buscar/', views.search_results_view, name='search'),
    path('test-seo/', views.test_seo, name='test_seo'),  # Vista de prueba de SEO
    path('gestion/comentarios/', views.listar_comentarios_view, name='listar_comentarios'),
    path('gestion/comentarios/aprobar/<int:comentario_id>/', views.aprobar_comentario_view, name='aprobar_comentario'),
    path('gestion/comentarios/rechazar/<int:comentario_id>/', views.rechazar_comentario_view, name='rechazar_comentario'),
    path('limpiar-carro/', views.clear_cart, name='clear_cart'), 
    path('chatbot/', views.chatbot_view, name='chatbot'),  
    path('gestion/', views.panel_gestion_view, name='panel_gestion'),
    path('gestion/productos/', views.listar_productos_view, name='listar_productos'),
    path('gestion/productos/crear/', views.crear_producto_view, name='crear_producto'),
    path('gestion/productos/editar/<int:pk>/', views.editar_producto_view, name='editar_producto'),
    path('gestion/productos/eliminar/<int:pk>/', views.eliminar_producto_view, name='eliminar_producto'),
    path('gestion/productos/exportar-csv/', views.exportar_productos_csv, name='exportar_productos_csv'), 
    path('gestion/categorias/', views.listar_categorias_view, name='listar_categorias'),
    path('gestion/categorias/crear/', views.crear_categoria_view, name='crear_categoria'),
    path('gestion/categorias/editar/<int:pk>/', views.editar_categoria_view, name='editar_categoria'),
    path('gestion/categorias/eliminar/<int:pk>/', views.eliminar_categoria_view, name='eliminar_categoria'),
    path('gestion/categorias/exportar-csv/', views.exportar_categorias_csv, name='exportar_categorias_csv'),
    # URLs para Gestión de Marcas
    path('gestion/marcas/', views.listar_marcas_view, name='listar_marcas'),
    path('gestion/marcas/crear/', views.crear_marca_view, name='crear_marca'),
    path('gestion/marcas/editar/<int:pk>/', views.editar_marca_view, name='editar_marca'),
    path('gestion/marcas/eliminar/<int:pk>/', views.eliminar_marca_view, name='eliminar_marca'),
    path('gestion/marcas/exportar-csv/', views.exportar_marcas_csv, name='exportar_marcas_csv'),

    # URLs para Gestión de Tags
    path('gestion/tags/', views.listar_tags_view, name='listar_tags'),
    path('gestion/tags/crear/', views.crear_tag_view, name='crear_tag'),
    path('gestion/tags/editar/<int:pk>/', views.editar_tag_view, name='editar_tag'),
    path('gestion/tags/eliminar/<int:pk>/', views.eliminar_tag_view, name='eliminar_tag'),

    # URLs para Gestión de Empleados (Superadmin)
    path('gestion/empleados/', views.gestion_empleados, name='gestion_empleados'),
    path('gestion/empleados/crear/', views.crear_empleado, name='crear_empleado'),
    path('gestion/empleados/editar/<int:pk>/', views.editar_empleado, name='editar_empleado'),
    path('gestion/empleados/eliminar/<int:pk>/', views.eliminar_empleado, name='eliminar_empleado'),

    path('checkout/', views.checkout_view, name='checkout'),
    path('procesar-pedido/', views.procesar_pedido_view, name='procesar_pedido'),
    path('pedido/recibo/<int:pedido_id>/', views.generar_recibo_pdf, name='generar_recibo_pdf'),
    path('gestion/metricas/', views.ver_metricas, name='ver_metricas'),
    path('pago/transferencia/<int:pedido_id>/', views.subir_comprobante, name='subir_comprobante'),
    path('gestion/transferencias/', views.listar_transferencias_view, name='listar_transferencias'),
    path('gestion/transferencias/<int:pago_id>/', views.gestionar_transferencia_view, name='gestionar_transferencia'),
    path('pago/cancelar/<int:pedido_id>/', views.cancelar_pedido_transferencia, name='cancelar_pedido_transferencia'),
    # Rutas para Webpay Plus (Transbank)
    path('webpay/iniciar/', views.iniciar_pago_webpay, name='iniciar_pago_webpay'),
    path('webpay/retorno/', views.retorno_webpay, name='retorno_webpay'),
    path('webpay/anular/<int:transaccion_id>/', views.anular_transaccion_webpay, name='anular_transaccion_webpay'),
    
    # Rutas para Mercado Pago
    path('mercadopago/iniciar/', views.iniciar_pago_mercadopago, name='iniciar_pago_mercadopago'),
    path('mercadopago/success/', views.retorno_mercadopago_success, name='retorno_mercadopago_success'),
    path('mercadopago/failure/', views.retorno_mercadopago_failure, name='retorno_mercadopago_failure'),
    path('mercadopago/pending/', views.retorno_mercadopago_pending, name='retorno_mercadopago_pending'),
    
    path('mi-cuenta/', views.perfil_usuario_view, name='perfil_usuario'),
    path('mi-cuenta/editar/', views.editar_perfil_view, name='editar_perfil'),
    path('mi-cuenta/compras/', views.historial_compras_view, name='historial_compras'),
    path('mi-cuenta/compras/<int:pedido_id>/', views.detalle_compra_view, name='detalle_compra'),
    
    path('gestion/pedidos/', views.listar_pedidos_view, name='listar_pedidos'),
    path('gestion/pedidos/<int:pedido_id>/', views.gestionar_pedido_view, name='gestionar_pedido'),
    path('mi-cuenta/notificaciones/', views.mis_notificaciones_view, name='mis_notificaciones'), 
    
    # Recuperación de contraseña
    path('recuperar-contrasena/', views.password_reset_request, name='password_reset_request'),
    path('restablecer-contrasena/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG or not settings.PRODUCTION:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))
