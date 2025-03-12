// 1979440 Afeitado Normal 
// 1007886 Afeitado con vapor
// 1007897 Afeitado y corte 


// 7099180 Corte Sencillo 
// 1007897 Afeitado y corte 
// 7017230 Trenzas 


// 1584711 Masaje Relajante 
// 3184610 Masaje con piedras volcanicas 
// 7452918 Masaje deportivo

// 4481538 Tratamiento Hidratacion Profunda 
// 8307698 Tratamiento contorno de ojos
// 1007874 Tratamiento sencillo 

// 1179458 Cejas 


let apiKey='47561401-91c03c27e9e8b50ee0ce43764'
let ids=[1979440,1007886,3173419]

let serviciosPorID = {
    1979440: {
        titulo: 'Afeitado Sencillo',
        precio: '42.000',
    },
    1007886: {
        titulo: 'Afeitado Con Vapor',
        precio: '50.000',
        descripcion: ''
    },
    3173419: {
        titulo: 'Afeitado & Corte',
        precio: '60.000',
    },
}




function getIdImagen(id){
    fetch(`https://pixabay.com/api/?key=${apiKey}&id=${id}&image_type=photo`)
        .then(respuesta => respuesta.json())
        .then(datos => {
            /* Se obtiene primera posicion de la lista */
            let dato = datos.hits[0]
            if (dato){

                let id_servicio = serviciosPorID[dato.id]

                let contenedor = document.getElementById('container-card')
                let card = document.createElement('div')
                let cardBody= document.createElement('div')
                let img = document.createElement('img')
                let titulo = document.createElement('p')
                let precio = document.createElement('p')

                card.classList.add('card')
                cardBody.classList.add('card-body')
                titulo.classList.add('card-title')
                precio.classList.add('card-text')
                

                titulo.textContent=id_servicio.titulo
                img.src=dato.webformatURL
                precio.textContent=`Desde $ ${id_servicio.precio} COP`


                contenedor.appendChild(card)
                card.appendChild(img)
                card.appendChild(cardBody)
                cardBody.appendChild(titulo)
                cardBody.appendChild(precio)
            }

        })


}

ids.forEach(elemento => {
    getIdImagen(elemento)
});