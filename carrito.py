class carrito:
    def __init__(self):
        self.items = []

    def agregar_producto(self, id_producto, nombre, cantidad, precio_unitario):
        # Revisar si ya existe el producto en el carrito
        for item in self.items:
            if item["id"] == id_producto:
                item["cantidad"] += cantidad
                return
        # Si no existe, se agrega nuevo
        self.items.append({
            "id": id_producto,
            "nombre": nombre,
            "cantidad": cantidad,
            "precio": precio_unitario
        })

    def calcular_total(self):
        total = 0
        for item in self.items:
            total += item["cantidad"] * item["precio"]
        return total

    def mostrar_carrito(self):
        if not self.items:
            return "🛒 El carrito está vacío"

        mensaje = "🛒 *CARRITO:*\n\n"
        for item in self.items:
            subtotal = item["cantidad"] * item["precio"]
            mensaje += f"• {item['nombre']} x{item['cantidad']} = ${subtotal:.2f}\n"

        mensaje += f"\n💰 *Total: ${self.calcular_total():.2f}*"
        return mensaje


# Carrito global único
mi_carrito = carrito()

# Estados simples
esperando_id = False
esperando_cantidad = False
producto_seleccionado = None