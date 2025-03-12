

let apiKey = '47561401-91c03c27e9e8b50ee0ce43764'
let ids = [5711575, 1007875, 3184610, 8307698]

let serviciosPorID = {
    5711575: {
        titulo: 'Corte',
        precio: '48.000',
        descripcion: 'Servicio de corte de cabello profesional adaptado a tu estilo y preferencias.'
    },
    1007875: {
        titulo: 'Barba',
        precio: '42.000',
        descripcion: 'Perfilado y cuidado de la barba con técnicas precisas para un acabado impecable.'
    },
    3184610: {
        titulo: 'Masajes & Spa',
        precio: '60.000',
        descripcion: 'Experiencia relajante con masajes profesionales para aliviar el estrés y revitalizar tu cuerpo.'
    },
    8307698: {
        titulo: 'Tratamientos',
        precio: '200.000',
        descripcion: 'Tratamientos especializados para el cuidado capilar, mejorando la salud y apariencia de tu cabello.'
    }
}

/* Los pongo afuera por si no carga la imagen o no tengo internet de igual forma se creen los elementos pero que no apareza la imagen */




function getIdImagen(id) {
    fetch(`https://pixabay.com/api/?key=${apiKey}&id=${id}&image_type=photo`)
        .then(response => response.json())
        .then(data => {
            let dato = data.hits[0] /* Primera posicion del arreglo hits que viene de la api  */

            if (dato) { /* Como es un API puede que el ID lo cambien o elimen la imagen por eso es mejor crear validaciones */

                let servicio = serviciosPorID[dato.id] /* busca dentro de la lista servicios si hay un ID que sea igual al ID de la imagen de la API dato.id es el id de la api  */

                let img = document.createElement('img')
                let contenedor = document.getElementById('container-card')
                let card = document.createElement('div')
                let frontal = document.createElement('div')
                let back = document.createElement('div')
                let infoImg = document.createElement('ul')
                let nombre = document.createElement('li')
                let precio = document.createElement('li')
                let titulo = document.createElement('p')


                card.classList.add('card')
                frontal.classList.add('frontal')
                back.classList.add('back')
                titulo.classList.add('titulo-card')


                img.src = dato.webformatURL
                nombre.textContent = servicio.descripcion
                precio.textContent = `Precio Desde : ${servicio.precio} $ `
                titulo.textContent = servicio.titulo



                contenedor.appendChild(card)
                card.appendChild(frontal)
                card.appendChild(back)


                infoImg.appendChild(nombre)
                infoImg.appendChild(precio)

                frontal.appendChild(img)
                frontal.append(titulo)
                back.appendChild(infoImg)


                card.addEventListener('click', () => {
                    card.classList.toggle('rotada')
                });

            }

        })

}

ids.forEach(elemento => { /* Recorrer la array que tiene los ids de las imagenes y por cada iteracion ejecutar la funcion de obtener id haciendo que cree una tarjeta por cada imagen */
    getIdImagen(elemento)
});












// 1179459 , 5711575 Corte cabello
// 3173419 , 1007875 Barba
// 3184610  masajes y spa
// 8307698 Mascarillas

