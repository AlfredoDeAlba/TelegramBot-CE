import os
import logging
from dotenv import load_dotenv

import DB.Repuestas
from DB import Repuestas
from DB.productos import *
from carrito import esperando_id, mi_carrito

# Importaciones de telegram - versión compatible
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

    print("✅ Importaciones de telegram exitosas")
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Ejecuta: pip install --upgrade python-telegram-bot")
    exit(1)

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Estados del ConversationHandler
ESPERANDO_ID, ESPERANDO_CANTIDAD = range(2)


# Función para el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía un mensaje cuando el comando /start es ejecutado."""
    user = update.effective_user
    await update.message.reply_html(
        f"¡Hola {user.mention_html()}! 👋\n"
        f"Somos las Sevillanas.\n"
        f"Por favor mande el comando que se adecua mejor a su situacion.\n\n"
        f"Comandos disponibles:\n\n" +
        DB.Repuestas.COMANDOS

    )


# Función para el comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía un mensaje de ayuda cuando el comando /help es ejecutado."""
    await update.message.reply_text(Repuestas.AYUDA, parse_mode='Markdown')


# Función para el comando /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la historia de la sevillana."""
    await update.message.reply_text(Repuestas.HISTORIA, parse_mode='Markdown')


# Función para manejar errores
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los errores que ocurran en el bot."""
    logger.warning(f'Update {update} caused error {context.error}')


async def exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía un mensaje de despedida /exit es ejecutado."""
    exit_text = (
        "QUE TENGAS UN EXCELENTE DIA"
    )
    await update.message.reply_text(exit_text, parse_mode='Markdown')


async def preguntasF(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """resolver preguntas frecuentes de las sevllanas dulceria"""
    await update.message.reply_text(Repuestas.FRECUENTES, parse_mode='Markdown')


async def apoyo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """resolver te contacta con una persona real"""
    await update.message.reply_text(Repuestas.APOYO)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """resolver te contacta con una persona real"""
    i = 0
    exit_text = (
        "PERFECTO VAMOS A VER NUESTRAS OPCIONES JUNTO SU ID\n\n"
    )

    await update.message.reply_text(exit_text)
    for i in range(1, 6):
        productos = obtener_producto(str(i))
        imagen_path = f"fotos/{productos['imagen']}"
        texto = "id:" + productos["id"] + "\n" + "producto:" + productos["nombre"] + "\nPrecion X unidad:" + str(
            productos["precio"]) + "$\nDescripcion:" + productos["descripcion"]
        with open(imagen_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=texto)


async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """resolver te contacta con una persona real"""
    await update.message.reply_text("estas promociones solo son validas en sucursales")
    imagen_path = f"fotos/promo1.png"
    with open(imagen_path, 'rb') as photo:
        await update.message.reply_photo(photo=photo)


# ==================== SISTEMA DE PEDIDOS CON CONVERSATION HANDLER ====================

async def iniciar_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso de pedido - ENTRY POINT"""
    await update.message.reply_text(
        "🛍️ **NUEVO PEDIDO**\n\n"
        "Para realizar tu pedido, primero necesito que veas nuestros productos.\n"
        "Usa /menu para ver todos los productos disponibles con sus IDs.\n\n"
        "Una vez que hayas visto el menú, escribe el **ID del producto** que deseas:"
    )

    # Limpiar datos previos
    context.user_data.clear()

    return ESPERANDO_ID


async def procesar_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el ID del producto ingresado"""
    id_producto = update.message.text.strip()

    try:
        # Verificar si el ID existe usando tu función
        producto = obtener_producto(id_producto)

        if not producto:
            await update.message.reply_text(
                f"❌ El ID `{id_producto}` no existe.\n\n"
                f"Por favor, usa /menu para ver los productos disponibles y sus IDs.\n"
                f"Luego escribe un ID válido:"
            )
            return ESPERANDO_ID

        # Guardar el producto seleccionado
        context.user_data['id_producto'] = id_producto
        context.user_data['producto'] = producto

        # Mostrar el producto seleccionado con imagen
        imagen_path = f"fotos/{producto['imagen']}"
        texto_confirmacion = (
            f"✅ **Producto seleccionado:**\n\n"
            f"🆔 ID: {producto['id']}\n"
            f"📦 Producto: {producto['nombre']}\n"
            f"💰 Precio por unidad: ${producto['precio']}\n"
            f"📝 Descripción: {producto['descripcion']}\n\n"
            f"Ahora ingresa la **cantidad** que deseas:"
        )

        try:
            with open(imagen_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=texto_confirmacion)
        except FileNotFoundError:
            # Si no se encuentra la imagen, enviar solo texto
            await update.message.reply_text(texto_confirmacion)

        return ESPERANDO_CANTIDAD

    except Exception as e:
        logger.error(f"Error al obtener producto {id_producto}: {e}")
        await update.message.reply_text(
            f"❌ Error al buscar el producto con ID `{id_producto}`.\n"
            f"Por favor, verifica el ID y inténtalo de nuevo:"
        )
        return ESPERANDO_ID


async def procesar_cantidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la cantidad y completa el pedido"""
    try:
        cantidad = int(update.message.text.strip())

        if cantidad <= 0:
            await update.message.reply_text(
                "❌ La cantidad debe ser mayor a 0.\n"
                "Por favor, ingresa una cantidad válida:"
            )
            return ESPERANDO_CANTIDAD

        # Obtener datos guardados
        id_producto = context.user_data['id_producto']
        producto = context.user_data['producto']

        # Calcular totales
        precio_unitario = float(producto['precio'])
        total = precio_unitario * cantidad

        # Agregar al carrito (usando tu sistema de carrito existente)
        # Aquí puedes llamar a tu función del carrito
        # mi_carrito.agregar_producto(id_producto, cantidad)

        # Mensaje de confirmación
        mensaje_pedido = f"""
🎉 **¡PRODUCTO AGREGADO AL CARRITO!**

📋 **Detalles:**
🆔 ID: {id_producto}
📦 Producto: {producto['nombre']}
💰 Precio unitario: ${precio_unitario}
🔢 Cantidad: {cantidad}
💵 **Subtotal: ${total:.2f}**

✅ El producto ha sido agregado a tu carrito.
📱 Usa /carrito para ver todos tus productos.
🛍️ Usa /pedido para agregar más productos.

¡Gracias por tu compra! 🍭
        """

        await update.message.reply_text(mensaje_pedido)

        # Limpiar datos del usuario
        context.user_data.clear()

        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text(
            "❌ Por favor ingresa un número válido para la cantidad.\n"
            "Ejemplo: 1, 2, 5, 10, etc.\n\n"
            "Ingresa la cantidad:"
        )
        return ESPERANDO_CANTIDAD
    except Exception as e:
        logger.error(f"Error procesando cantidad: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error procesando tu pedido.\n"
            "Por favor, inténtalo de nuevo con /pedido"
        )
        context.user_data.clear()
        return ConversationHandler.END


async def cancelar_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el pedido actual"""
    await update.message.reply_text(
        "❌ Pedido cancelado.\n"
        "Usa /pedido cuando quieras realizar un nuevo pedido."
    )
    context.user_data.clear()
    return ConversationHandler.END


# ==================== FIN SISTEMA DE PEDIDOS ====================

async def ver_carrito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el carrito"""
    await update.message.reply_text(mi_carrito.mostrar_carrito(), parse_mode='Markdown')


def main():
    """Función principal para ejecutar el bot."""
    # Verificar que el token existe
    if not BOT_TOKEN:
        print("❌ Error: No se encontró el token del bot.")
        print("Asegúrate de que tu archivo .env contenga: BOT_TOKEN=tu_token_aqui")
        return

    print(f"🔑 Token encontrado: {BOT_TOKEN[:10]}...")

    # Crear la aplicación
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        print("✅ Aplicación creada correctamente")
    except Exception as e:
        print(f"❌ Error creando la aplicación: {e}")
        return

    # ==================== CREAR EL CONVERSATION HANDLER ====================
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('pedido', iniciar_pedido)],
        states={
            ESPERANDO_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_id)
            ],
            ESPERANDO_CANTIDAD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_cantidad)
            ],
        },
        fallbacks=[CommandHandler('cancelar', cancelar_pedido)],
        per_chat=True,
        per_user=True,
        conversation_timeout=300,  # 5 minutos
    )

    # Agregar el conversation handler PRIMERO
    application.add_handler(conversation_handler)

    # Luego agregar los demás comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pregFrecuentes", preguntasF))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("apoyo", apoyo))
    application.add_handler(CommandHandler("carrito", ver_carrito))
    application.add_handler(CommandHandler("exit", exit))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("promo", promo))

    # Añadir manejador de errores
    application.add_error_handler(error_handler)

    # Iniciar el bot con polling
    try:
        print("🤖 Bot iniciado correctamente...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"❌ Error ejecutando el bot: {e}")


if __name__ == '__main__':
    main()