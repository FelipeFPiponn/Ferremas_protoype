import os
import django
import random
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config_sys.settings')
django.setup()

from django.utils import timezone
from productos.models import Producto, Categoria

def crear_productos():
    # Asegúrate de que las categorías existan
    categoria_herramientas, _ = Categoria.objects.get_or_create(
        nombre="Herramientas Manuales",
        defaults={"descripcion": "Herramientas manuales para todo tipo de trabajos"}
    )
    
    categoria_electricas, _ = Categoria.objects.get_or_create(
        nombre="Herramientas Eléctricas",
        defaults={"descripcion": "Herramientas eléctricas para trabajos profesionales"}
    )
    
    categoria_materiales, _ = Categoria.objects.get_or_create(
        nombre="Materiales de Construcción",
        defaults={"descripcion": "Materiales para construcción y remodelación"}
    )
    
    # Productos de Herramientas Manuales - Martillos
    martillos = [
        {
            "nombre": "Martillo de Carpintero Stanley",
            "descripcion": "Martillo de carpintero con mango ergonómico y cabeza de acero forjado. Ideal para trabajos de carpintería y construcción general.",
            "precio": 15.99,
            "stock": 50,
            "destacado": True,
            "subcategoria": "Martillos"
        },
        {
            "nombre": "Martillo de Bola Truper",
            "descripcion": "Martillo de bola con mango de fibra de vidrio y cabeza de acero. Perfecto para trabajos de mecánica y metalurgia.",
            "precio": 18.50,
            "stock": 35,
            "destacado": False,
            "subcategoria": "Martillos"
        },
        {
            "nombre": "Martillo de Goma Pretul",
            "descripcion": "Martillo de goma para trabajos que requieren impacto sin dañar la superficie. Ideal para colocación de baldosas y trabajos de acabado.",
            "precio": 8.75,
            "stock": 60,
            "destacado": False,
            "subcategoria": "Martillos"
        },
        {
            "nombre": "Combo 4 Libras Tramontina",
            "descripcion": "Martillo tipo combo de 4 libras con mango de madera. Perfecto para demolición y trabajos pesados.",
            "precio": 22.99,
            "stock": 25,
            "destacado": True,
            "subcategoria": "Martillos"
        }
    ]
    
    # Productos de Herramientas Manuales - Destornilladores
    destornilladores = [
        {
            "nombre": "Juego de Destornilladores Stanley 10 piezas",
            "descripcion": "Set de 10 destornilladores con diferentes puntas y tamaños. Incluye destornilladores Phillips y planos.",
            "precio": 29.99,
            "stock": 40,
            "destacado": True,
            "subcategoria": "Destornilladores"
        },
        {
            "nombre": "Destornillador Eléctrico Inalámbrico Black & Decker",
            "descripcion": "Destornillador eléctrico recargable con batería de litio. Incluye 10 puntas intercambiables.",
            "precio": 45.50,
            "stock": 30,
            "destacado": True,
            "subcategoria": "Destornilladores"
        },
        {
            "nombre": "Destornillador de Precisión Truper",
            "descripcion": "Set de destornilladores de precisión para electrónica y trabajos finos. Incluye 6 piezas con estuche.",
            "precio": 12.75,
            "stock": 55,
            "destacado": False,
            "subcategoria": "Destornilladores"
        },
        {
            "nombre": "Destornillador Magnético Phillips #2",
            "descripcion": "Destornillador con punta magnética Phillips #2. Mango ergonómico y punta endurecida.",
            "precio": 7.99,
            "stock": 70,
            "destacado": False,
            "subcategoria": "Destornilladores"
        }
    ]
    
    # Productos de Herramientas Manuales - Llaves
    llaves = [
        {
            "nombre": "Juego de Llaves Combinadas Stanley 12 piezas",
            "descripcion": "Set de 12 llaves combinadas en medidas métricas. Fabricadas en acero cromo-vanadio.",
            "precio": 42.99,
            "stock": 35,
            "destacado": True,
            "subcategoria": "Llaves"
        },
        {
            "nombre": "Llave Ajustable 12\" Truper",
            "descripcion": "Llave ajustable de 12 pulgadas con acabado cromado. Apertura máxima de 1-1/2\".",
            "precio": 15.75,
            "stock": 45,
            "destacado": False,
            "subcategoria": "Llaves"
        },
        {
            "nombre": "Juego de Llaves Allen Métricas",
            "descripcion": "Set de 9 llaves Allen en medidas métricas con soporte organizador. Fabricadas en acero templado.",
            "precio": 18.50,
            "stock": 50,
            "destacado": False,
            "subcategoria": "Llaves"
        },
        {
            "nombre": "Llave de Tubo 14\" Urrea",
            "descripcion": "Llave de tubo profesional de 14 pulgadas. Ideal para plomería y trabajos con tuberías.",
            "precio": 28.99,
            "stock": 30,
            "destacado": True,
            "subcategoria": "Llaves"
        }
    ]
    
    # Productos de Herramientas Eléctricas - Taladros
    taladros = [
        {
            "nombre": "Taladro Percutor DeWalt 1/2\"",
            "descripcion": "Taladro percutor de 1/2 pulgada con 700W de potencia. Velocidad variable y reversible.",
            "precio": 129.99,
            "stock": 25,
            "destacado": True,
            "subcategoria": "Taladros"
        },
        {
            "nombre": "Taladro Inalámbrico Bosch 12V",
            "descripcion": "Taladro inalámbrico de 12V con 2 baterías de litio y cargador. Incluye maletín y accesorios.",
            "precio": 149.50,
            "stock": 20,
            "destacado": True,
            "subcategoria": "Taladros"
        },
        {
            "nombre": "Taladro de Banco Skil 10\"",
            "descripcion": "Taladro de banco con mesa inclinable y láser de precisión. Motor de 3.2 Amp.",
            "precio": 199.99,
            "stock": 15,
            "destacado": False,
            "subcategoria": "Taladros"
        },
        {
            "nombre": "Mini Taladro Dremel 3000",
            "descripcion": "Mini taladro multiusos con 130W de potencia. Incluye 25 accesorios y estuche.",
            "precio": 89.75,
            "stock": 30,
            "destacado": False,
            "subcategoria": "Taladros"
        }
    ]
    
    # Productos de Herramientas Eléctricas - Sierras
    sierras = [
        {
            "nombre": "Sierra Circular DeWalt 7-1/4\"",
            "descripcion": "Sierra circular con disco de 7-1/4 pulgadas y motor de 1800W. Cortes precisos a 90° y 45°.",
            "precio": 159.99,
            "stock": 20,
            "destacado": True,
            "subcategoria": "Sierras"
        },
        {
            "nombre": "Sierra Caladora Bosch GST 650",
            "descripcion": "Sierra caladora con 450W de potencia y sistema de cambio rápido de hoja. Cortes precisos en madera, metal y plástico.",
            "precio": 119.50,
            "stock": 25,
            "destacado": False,
            "subcategoria": "Sierras"
        },
        {
            "nombre": "Sierra de Mesa Skil 10\"",
            "descripcion": "Sierra de mesa con disco de 10 pulgadas y extensiones laterales. Motor de 15 Amp para cortes profesionales.",
            "precio": 299.99,
            "stock": 10,
            "destacado": True,
            "subcategoria": "Sierras"
        },
        {
            "nombre": "Sierra de Inglete Makita 10\"",
            "descripcion": "Sierra de inglete compuesta con disco de 10 pulgadas. Ideal para carpintería y trabajos de precisión.",
            "precio": 249.75,
            "stock": 15,
            "destacado": False,
            "subcategoria": "Sierras"
        }
    ]
    
    # Productos de Herramientas Eléctricas - Lijadoras
    lijadoras = [
        {
            "nombre": "Lijadora Orbital DeWalt 1/4\"",
            "descripcion": "Lijadora orbital con base de 1/4 de hoja. Motor de 200W y sistema de recolección de polvo.",
            "precio": 79.99,
            "stock": 30,
            "destacado": False,
            "subcategoria": "Lijadoras"
        },
        {
            "nombre": "Lijadora de Banda Bosch GBS 75 AE",
            "descripcion": "Lijadora de banda profesional con 750W de potencia. Ideal para trabajos de acabado en madera.",
            "precio": 189.50,
            "stock": 20,
            "destacado": True,
            "subcategoria": "Lijadoras"
        },
        {
            "nombre": "Lijadora Roto-orbital Makita BO5041",
            "descripcion": "Lijadora roto-orbital con órbita de 3mm y velocidad variable. Perfecta para acabados finos.",
            "precio": 129.99,
            "stock": 25,
            "destacado": False,
            "subcategoria": "Lijadoras"
        },
        {
            "nombre": "Mini Lijadora Mouse Black & Decker",
            "descripcion": "Mini lijadora tipo mouse para espacios reducidos y detalles. Incluye accesorios y bolsa recolectora.",
            "precio": 49.75,
            "stock": 35,
            "destacado": True,
            "subcategoria": "Lijadoras"
        }
    ]
    
    # Productos de Materiales de Construcción
    materiales = [
        {
            "nombre": "Cemento Portland 50kg",
            "descripcion": "Saco de cemento Portland de 50kg. Ideal para construcciones generales y trabajos de albañilería.",
            "precio": 12.99,
            "stock": 100,
            "destacado": True,
            "subcategoria": "Cemento"
        },
        {
            "nombre": "Arena Fina 40kg",
            "descripcion": "Saco de arena fina de 40kg. Perfecta para mezclas de concreto y trabajos de acabado.",
            "precio": 8.50,
            "stock": 150,
            "destacado": False,
            "subcategoria": "Arena"
        },
        {
            "nombre": "Ladrillos Cerámicos 6 Huecos (Pack 100)",
            "descripcion": "Pack de 100 ladrillos cerámicos de 6 huecos. Medidas estándar para construcción de muros.",
            "precio": 89.99,
            "stock": 50,
            "destacado": True,
            "subcategoria": "Ladrillos"
        },
        {
            "nombre": "Pintura Látex Interior 20L",
            "descripcion": "Pintura látex para interiores de 20 litros. Disponible en varios colores. Alta cobertura y rendimiento.",
            "precio": 59.75,
            "stock": 40,
            "destacado": True,
            "subcategoria": "Pinturas"
        },
        {
            "nombre": "Barniz Poliuretano 4L",
            "descripcion": "Barniz de poliuretano para madera de 4 litros. Acabado brillante y alta resistencia.",
            "precio": 45.99,
            "stock": 35,
            "destacado": False,
            "subcategoria": "Barnices"
        },
        {
            "nombre": "Cerámica para Piso 45x45cm (Caja 2m²)",
            "descripcion": "Caja de cerámica para piso de 45x45cm. Cubre aproximadamente 2m². Resistente al desgaste.",
            "precio": 32.50,
            "stock": 60,
            "destacado": True,
            "subcategoria": "Cerámicos"
        }
    ]


