// Spinner de carga en formularios
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function() {
            let spinner = document.createElement('div');
            spinner.className = 'spinner position-fixed top-50 start-50 translate-middle';
            spinner.style.zIndex = 2000;
            document.body.appendChild(spinner);
        });
    });

    // Mensajes motivadores en la home
    if (window.location.pathname === '/' || window.location.pathname.includes('home')) {
        const mensajes = [
            '¡Estás haciendo un gran trabajo! 🛠️',
            '¡Gracias por confiar en Ferreemas!',
            'Recuerda: cada proyecto empieza con una buena herramienta.',
            '¡Hoy es un buen día para construir algo nuevo!',
            '¿Sabías que tu carrito te espera con sorpresas?'
        ];
        const idx = Math.floor(Math.random() * mensajes.length);
        const div = document.createElement('div');
        div.className = 'mensaje-motivador text-center';
        div.innerText = mensajes[idx];
        const main = document.querySelector('main');
        if (main) main.prepend(div);
    }
}); 