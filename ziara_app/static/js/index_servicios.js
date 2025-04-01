// Hacemos una solicitud a la API de Django para obtener la lista de servicios
fetch('/obtener_servicios/')  
.then(response => response.json())  // Convertimos la respuesta en formato JSON
.then(servicios => {  
    // Recorremos la lista de servicios obtenidos desde la API
    servicios.forEach(servicio => {  
        // Buscamos en el documento HTML el elemento <img> correspondiente al servicio actual
        let img = document.getElementById(`img_${servicio.id}`);  
        
        // Verificamos que la imagen exista en el HTML y que el servicio tenga una URL de imagen válida
        if (img && servicio.img_url) {  
            img.src = servicio.img_url;  // Asignamos la URL de la imagen al atributo 'src' de la etiqueta <img>
            img.style.objectFit = 'cover';  // Ajustamos la imagen para que cubra el área sin distorsionarse
            img.style.height = '200px';  // Definimos una altura fija de 200px para todas las imágenes
        }
    });
})
