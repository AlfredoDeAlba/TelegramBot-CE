PRODUCTOS_MENU = [
    {
        "id": "1",
        "nombre": "Cajeta Tradicional",
        "precio": 25.00,
        "imagen": "cajeta.jpg",
        "descripcion": "Deliciosa cajeta artesanal elaborada con leche de cabra"
    },
    {
        "id": "2",
        "nombre": "Cocada Fresca",
        "precio": 15.00,
        "imagen": "Cocada.jpg",
        "descripcion": "Cocada tradicional elaborada con coco natural fresco"
    },
    {
        "id": "3",
        "nombre": "Glorias Especiales",
        "precio": 35.00,
        "imagen": "Glorias.jpg",
        "descripcion": "Nuestras famosas glorias, dulce típico que conquista paladares"
    },
    {
        "id": "4",
        "nombre": "Obleas Artesanales",
        "precio": 20.00,
        "imagen": "Obleas.jpg",
        "descripcion": "Obleas crujientes rellenas de cajeta, una delicia tradicional"
    },
    {
        "id": "5",
        "nombre": "Palanquetas Caseras",
        "precio": 18.00,
        "imagen": "palanquetas.jpg",
        "descripcion": "Palanquetas de cacahuate, el snack perfecto con sabor tradicional"
    }
]

# Función auxiliar para obtener producto por ID
def obtener_producto(producto_id):
    """Obtiene un producto específico por su ID"""
    for producto in PRODUCTOS_MENU:
        if producto["id"] == producto_id:
            return producto
    return None
