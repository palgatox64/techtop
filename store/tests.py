

from django.test import TestCase, Client as TestClient
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from decimal import Decimal
from .models import (
    Cliente, Empleado, Producto, Categoria, Marca, 
    Direccion, Pedido, DetallePedido, ImagenProducto
)



class ClienteManagementTests(TestCase):
    """Pruebas para la gestión de usuarios y clientes"""

    def setUp(self):
        """Configuración inicial para todas las pruebas de clientes"""
        self.cliente_data = {
            'nombre': 'Juan',
            'apellidos': 'Pérez González',
            'email': 'juan.perez@example.com',
            'pass_hash': 'hashed_password_123',
            'telefono': '912345678'
        }

    def test_TT_U01_registro_nuevo_cliente(self):
        """
        TT-U01: Registro de nuevo cliente en la BD
        Verifica que se pueda crear un nuevo cliente correctamente.
        """
        cliente = Cliente.objects.create(**self.cliente_data)
        
        self.assertEqual(cliente.nombre, 'Juan')
        self.assertEqual(cliente.apellidos, 'Pérez González')
        self.assertEqual(cliente.email, 'juan.perez@example.com')
        self.assertEqual(cliente.telefono, '912345678')
        self.assertEqual(Cliente.objects.count(), 1)
        
        print("✅ TT-U01: Registro de nuevo cliente -> EXITOSA")

    def test_TT_U02_consulta_cliente_por_email(self):
        """
        TT-U02: Consulta de cliente por email
        Verifica que se pueda buscar y recuperar un cliente por su email.
        """
        Cliente.objects.create(**self.cliente_data)
        
        cliente = Cliente.objects.get(email='juan.perez@example.com')
        
        self.assertEqual(cliente.nombre, 'Juan')
        self.assertEqual(cliente.apellidos, 'Pérez González')
        
        print("✅ TT-U02: Consulta de cliente por email -> EXITOSA")

    def test_TT_U03_actualizacion_datos_cliente(self):
        """
        TT-U03: Actualización de datos del cliente (ej. teléfono)
        Verifica que se puedan actualizar los datos de un cliente existente.
        """
        cliente = Cliente.objects.create(**self.cliente_data)
        
        
        cliente.telefono = '987654321'
        cliente.save()
        
        cliente_actualizado = Cliente.objects.get(id_cliente=cliente.id_cliente)
        self.assertEqual(cliente_actualizado.telefono, '987654321')
        
        print("✅ TT-U03: Actualización de datos del cliente -> EXITOSA")

    def test_TT_U04_eliminacion_cliente(self):
        """
        TT-U04: Eliminación de un cliente de la BD
        Verifica que se pueda eliminar un cliente de la base de datos.
        """
        cliente = Cliente.objects.create(**self.cliente_data)
        cliente_id = cliente.id_cliente
        
        cliente.delete()
        
        self.assertEqual(Cliente.objects.filter(id_cliente=cliente_id).count(), 0)
        self.assertEqual(Cliente.objects.count(), 0)
        
        print("✅ TT-U04: Eliminación de un cliente -> EXITOSA")

    def test_TT_U05_verificacion_email_duplicado(self):
        """
        TT-U05: Verificación de email duplicado al registrar
        Verifica que no se permita registrar dos clientes con el mismo email.
        """
        Cliente.objects.create(**self.cliente_data)
        
        
        with self.assertRaises(IntegrityError):
            Cliente.objects.create(
                nombre='María',
                apellidos='López Silva',
                email='juan.perez@example.com',  
                pass_hash='otro_hash',
                telefono='923456789'
            )
        
        print("✅ TT-U05: Verificación de email duplicado -> EXITOSA")




class ProductoManagementTests(TestCase):
    """Pruebas para la gestión de productos (CRUD)"""

    def setUp(self):
        """Configuración inicial para todas las pruebas de productos"""
        self.categoria = Categoria.objects.create(
            nombre='Electrónica',
            descripcion='Dispositivos electrónicos'
        )
        self.marca = Marca.objects.create(nombre='TechTop Genérico')

    def test_TT_P01_publicar_nuevo_producto(self):
        """
        TT-P01: Publicar (Crear) un nuevo producto
        Verifica que se pueda crear un nuevo producto en la base de datos.
        """
        producto = Producto.objects.create(
            nombre='Teclado Mecánico RGB',
            descripcion='Un teclado gaming con iluminación RGB',
            precio=59990,
            stock=10,
            categoria=self.categoria,
            marca=self.marca
        )

        self.assertEqual(producto.nombre, 'Teclado Mecánico RGB')
        self.assertEqual(producto.precio, Decimal('59990'))
        self.assertEqual(producto.stock, 10)
        self.assertEqual(Producto.objects.count(), 1)
        
        print("✅ TT-P01: Publicar un nuevo producto -> EXITOSA")

    def test_TT_P02_editar_producto_existente(self):
        """
        TT-P02: Editar información de un producto existente
        Verifica que se puedan actualizar los datos de un producto.
        """
        producto = Producto.objects.create(
            nombre='Mouse Óptico',
            descripcion='Mouse básico',
            precio=15000,
            stock=20,
            categoria=self.categoria,
            marca=self.marca
        )

        
        producto.nombre = 'Mouse Óptico Gaming'
        producto.precio = 25000
        producto.stock = 15
        producto.save()

        producto_actualizado = Producto.objects.get(id=producto.id)
        self.assertEqual(producto_actualizado.nombre, 'Mouse Óptico Gaming')
        self.assertEqual(producto_actualizado.precio, Decimal('25000'))
        self.assertEqual(producto_actualizado.stock, 15)
        
        print("✅ TT-P02: Editar información de un producto -> EXITOSA")

    def test_TT_P03_eliminar_producto(self):
        """
        TT-P03: Eliminar un producto publicado
        Verifica que se pueda eliminar un producto de la base de datos.
        """
        producto = Producto.objects.create(
            nombre='Auriculares Bluetooth',
            precio=35000,
            stock=5,
            categoria=self.categoria,
            marca=self.marca
        )
        producto_id = producto.id

        producto.delete()

        self.assertEqual(Producto.objects.filter(id=producto_id).count(), 0)
        
        print("✅ TT-P03: Eliminar un producto publicado -> EXITOSA")

    def test_TT_P04_verificar_carga_imagen_principal(self):
        """
        TT-P04: Verificar carga y visualización de imagen principal
        Verifica que un producto pueda tener una imagen asociada.
        """
        producto = Producto.objects.create(
            nombre='Laptop Gaming',
            precio=899990,
            stock=3,
            categoria=self.categoria,
            marca=self.marca,
            imagen='productos/laptop_test.jpg'
        )

        self.assertIsNotNone(producto.imagen)
        self.assertTrue(producto.imagen.name.endswith('laptop_test.jpg'))
        
        print("✅ TT-P04: Verificar carga de imagen principal -> EXITOSA")

    def test_TT_P05_busqueda_productos_por_nombre(self):
        """
        TT-P05: Búsqueda de productos por nombre
        Verifica que se puedan buscar productos filtrando por nombre.
        """
        Producto.objects.create(
            nombre='Teclado Mecánico',
            precio=50000,
            stock=10,
            categoria=self.categoria,
            marca=self.marca
        )
        Producto.objects.create(
            nombre='Mouse Inalámbrico',
            precio=20000,
            stock=15,
            categoria=self.categoria,
            marca=self.marca
        )
        Producto.objects.create(
            nombre='Teclado Bluetooth',
            precio=30000,
            stock=8,
            categoria=self.categoria,
            marca=self.marca
        )

        
        productos_teclado = Producto.objects.filter(nombre__icontains='Teclado')
        
        self.assertEqual(productos_teclado.count(), 2)
        self.assertTrue(all('Teclado' in p.nombre for p in productos_teclado))
        
        print("✅ TT-P05: Búsqueda de productos por nombre -> EXITOSA")




class ProcesoCompraTests(TestCase):
    """Pruebas para el proceso de compra y carrito"""

    def setUp(self):
        """Configuración inicial para todas las pruebas de compra"""
        self.client = TestClient()
        
        
        self.categoria = Categoria.objects.create(nombre='Electrónica')
        self.marca = Marca.objects.create(nombre='TechTop')
        
        
        self.producto1 = Producto.objects.create(
            nombre='Teclado RGB',
            precio=50000,
            stock=10,
            categoria=self.categoria,
            marca=self.marca
        )
        self.producto2 = Producto.objects.create(
            nombre='Mouse Gaming',
            precio=30000,
            stock=15,
            categoria=self.categoria,
            marca=self.marca
        )
        
        
        self.cliente = Cliente.objects.create(
            nombre='Ana',
            apellidos='Silva Rojas',
            email='ana.silva@example.com',
            pass_hash='hashed_pass',
            telefono='956789012'
        )
        
        
        self.direccion = Direccion.objects.create(
            cliente=self.cliente,
            calle='Av. Principal 123',
            ciudad='Santiago',
            region='Metropolitana',
            codigo_postal='8320000'
        )

    def test_TT_C01_añadir_producto_al_carrito(self):
        """
        TT-C01: Añadir producto al carrito de compras
        Verifica que se pueda añadir un producto al carrito de sesión.
        """
        
        response = self.client.post(
            f'/agregar/{self.producto1.id}/',
            {'quantity': 1}
        )
        
        
        cart = self.client.session.get('cart', {})
        
        self.assertIn(str(self.producto1.id), cart)
        self.assertEqual(cart[str(self.producto1.id)]['quantity'], 1)
        
        print("✅ TT-C01: Añadir producto al carrito -> EXITOSA")

    def test_TT_C02_actualizar_cantidad_en_carrito(self):
        """
        TT-C02: Actualizar cantidad de producto en el carrito
        Verifica que se pueda modificar la cantidad de un producto en el carrito.
        """
        
        self.client.post(
            f'/agregar/{self.producto1.id}/',
            {'quantity': 1}
        )

        
        self.client.post(
            f'/actualizar-carro/{self.producto1.id}/',
            {'action': 'increase'}
        )
        self.client.post(
            f'/actualizar-carro/{self.producto1.id}/',
            {'action': 'increase'}
        )

        cart = self.client.session.get('cart', {})
        
        self.assertEqual(cart[str(self.producto1.id)]['quantity'], 3)
        
        print("✅ TT-C02: Actualizar cantidad en el carrito -> EXITOSA")

    def test_TT_C03_eliminar_producto_del_carrito(self):
        """
        TT-C03: Eliminar producto del carrito
        Verifica que se pueda eliminar un producto del carrito.
        """
        
        self.client.post(
            f'/agregar/{self.producto1.id}/',
            {'quantity': 2}
        )
        self.client.post(
            f'/agregar/{self.producto2.id}/',
            {'quantity': 1}
        )

        
        self.client.post(f'/eliminar-del-carro/{self.producto1.id}/')

        cart = self.client.session.get('cart', {})
        
        self.assertNotIn(str(self.producto1.id), cart)
        self.assertIn(str(self.producto2.id), cart)
        
        print("✅ TT-C03: Eliminar producto del carrito -> EXITOSA")

    def test_TT_C04_proceso_checkout_simulado(self):
        """
        TT-C04: Proceso de Checkout (simulado)
        Verifica que el carrito tenga los datos necesarios para checkout.
        """
        
        self.client.post(
            f'/agregar/{self.producto1.id}/',
            {'quantity': 2}
        )
        self.client.post(
            f'/agregar/{self.producto2.id}/',
            {'quantity': 1}
        )

        
        cart = self.client.session.get('cart', {})

        
        total_calculado = Decimal('0')
        for product_id_str, item in cart.items():
            producto = Producto.objects.get(id=int(product_id_str))
            total_calculado += producto.precio * item['quantity']

        total_esperado = (self.producto1.precio * 2) + (self.producto2.precio * 1)

        self.assertEqual(total_calculado, total_esperado)
        self.assertEqual(len(cart), 2)
        
        print("✅ TT-C04: Proceso de Checkout (simulado) -> EXITOSA")

    def test_TT_C05_creacion_pedido_y_detalle(self):
        """
        TT-C05: Creación de Pedido y DetallePedido en la BD
        Verifica que se pueda crear un pedido con sus detalles correctamente.
        """
        
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            direccion_envio=self.direccion,
            total=0,
            estado='pendiente'
        )

        
        detalle1 = DetallePedido.objects.create(
            pedido=pedido,
            producto=self.producto1,
            cantidad=2,
            precio_unitario=self.producto1.precio
        )
        detalle2 = DetallePedido.objects.create(
            pedido=pedido,
            producto=self.producto2,
            cantidad=1,
            precio_unitario=self.producto2.precio
        )

        
        total = (detalle1.cantidad * detalle1.precio_unitario) + \
                (detalle2.cantidad * detalle2.precio_unitario)
        pedido.total = total
        pedido.save()

        
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(pedido.detalles.count(), 2)
        self.assertEqual(pedido.total, Decimal('130000'))
        self.assertEqual(pedido.estado, 'pendiente')
        
        
        self.assertEqual(pedido.cliente.email, 'ana.silva@example.com')
        self.assertEqual(pedido.direccion_envio.ciudad, 'Santiago')
        
        print("✅ TT-C05: Creación de Pedido y DetallePedido -> EXITOSA")



def print_test_summary():
    """Imprime un resumen de las pruebas disponibles"""
    print("\n" + "="*70)
    print("SUITE DE PRUEBAS TECHTOP - RESUMEN")
    print("="*70)
    print("\n📋 GESTIÓN DE USUARIOS Y CLIENTES (5 pruebas)")
    print("   TT-U01: Registro de nuevo cliente")
    print("   TT-U02: Consulta de cliente por email")
    print("   TT-U03: Actualización de datos del cliente")
    print("   TT-U04: Eliminación de un cliente")
    print("   TT-U05: Verificación de email duplicado")
    print("\n🛍️  GESTIÓN DE PRODUCTOS (5 pruebas)")
    print("   TT-P01: Publicar un nuevo producto")
    print("   TT-P02: Editar información de un producto")
    print("   TT-P03: Eliminar un producto")
    print("   TT-P04: Verificar carga de imagen principal")
    print("   TT-P05: Búsqueda de productos por nombre")
    print("\n🛒 PROCESO DE COMPRA (5 pruebas)")
    print("   TT-C01: Añadir producto al carrito")
    print("   TT-C02: Actualizar cantidad en el carrito")
    print("   TT-C03: Eliminar producto del carrito")
    print("   TT-C04: Proceso de Checkout (simulado)")
    print("   TT-C05: Creación de Pedido y DetallePedido")
    print("\n" + "="*70)
    print("TOTAL: 15 casos de prueba")
    print("="*70 + "\n")
