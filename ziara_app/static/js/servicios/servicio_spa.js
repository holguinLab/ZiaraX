
// 567021 Masaje Relajante 
// 3184610 Masaje con piedras volcanicas 
// 5132408 Masaje deportivo


let apiKey='47561401-91c03c27e9e8b50ee0ce43764'
let ids=[567021,3184610,5132408]

let infoimagen = {
    567021: {
        titulo: 'Masaje Relajante ',
        precio: '42.000',
    },
    3184610: {
        titulo: 'Masaje con piedras volcanicas',
        precio: '50.000',
        descripcion: ''
    },
    5132408: {
        titulo: ' Masaje deportivo',
        precio: '60.000',
    },
}




function getIdImagen(id_parametro){
    fetch(`https://pixabay.com/api/?key=${apiKey}&id=${id_parametro}&image_type=photo`)
        .then(respuesta => respuesta.json())
        .then(datos => {
            
            /* Servicio tiene el primer objeto extraido de la array  */
            let objetoArray = datos.hits[0] /* HITS . o donde estan guardados los arrays */

            if (objetoArray){ /* Esto lo hago para que cuando la api no encuentre el id pues generamos un error */
                
                /* Esto es una comparacion si se encuentra el id del objeto del array en la lista que contiene la informacion de las imagenes en este caso estamos comparando por el id   */
                let id_servicio = infoimagen[objetoArray.id]

                /* Creacion de elementos dinamicos en el DOM */
                let contenedor = document.getElementById("container-card")
                let card = document.createElement("div")
                let img = document.createElement("img")
                let cardBody =document.createElement("div")
                let titulo = document.createElement("p")
                let precio = document.createElement("p")

                /* Agregando valores a los elementos  */    
                img.src=objetoArray.webformatURL
                titulo.innerText=id_servicio.titulo
                precio.innerText=id_servicio.precio


                /* Agregando clases a los elementos Dinamicos  */
                card.classList.add('card')
                img.classList.add('img-top')
                cardBody.classList.add('card-body')

                /* Agregando appendchild*/
                contenedor.appendChild(card)
                card.appendChild(img)
                card.appendChild(cardBody)
                cardBody.appendChild(titulo)
                cardBody.appendChild(precio)

                /* Agregando estilos */
                img.style.width='100%'
                img.style.height='100%'
                img.style.objectFit='cover'

                contenedor.style.display='flex'
                contenedor.style.flexWrap='wrap'
                contenedor.style.justifyContent='center'
                contenedor.style.gap='30px'

                card.style.width='300px'
                card.style.height='400px'
                card.style.border='none'

                }
        })
}

ids.forEach(id => {
    getIdImagen(id)
});