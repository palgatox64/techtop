from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from store.models import Pedido

class Command(BaseCommand):
    help = 'Cancela pedidos pendientes que tienen más de 1 hora de antigüedad'

    def handle(self, *args, **kwargs):
        # 1. Calculamos el límite (Hace 1 hora)
        tiempo_limite = timezone.now() - timedelta(hours=1)

        # 2. Buscamos pedidos pendientes creados ANTES de ese límite
        # IMPORTANTE: Usamos 'fecha_pedido' que es el campo real de tu base de datos
        pedidos_vencidos = Pedido.objects.filter(
            estado='pendiente',  # Ojo: minúscula, coincide con tus choices
            fecha_pedido__lt=tiempo_limite
        )

        count = pedidos_vencidos.count()

        if count > 0:
            for pedido in pedidos_vencidos:
                # Restaurar stock si es necesario (opcional)
                # for detalle in pedido.detalles.all():
                #     detalle.producto.stock += detalle.cantidad
                #     detalle.producto.save()

                pedido.estado = 'cancelado'
                pedido.save()
                self.stdout.write(self.style.SUCCESS(f'Pedido #{pedido.id} cancelado por inactividad.'))
            
            self.stdout.write(self.style.SUCCESS(f'Se cancelaron {count} pedidos vencidos.'))
        else:
            self.stdout.write(self.style.SUCCESS('No hay pedidos vencidos para cancelar.'))