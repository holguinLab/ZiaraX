

let apiKey = '47561401-91c03c27e9e8b50ee0ce43764'

/* Los pongo afuera por si no carga la imagen o no tengo internet de igual forma se creen los elementos pero que no apareza la imagen */



// objeto que tiene los codigos unicos de las imagenes , y se asociana un id que vienes desde la api de pixaby
const imagenes = {
    1 : 1007875 ,// Afeiado clasico
    2 : 5711575 ,//Corte Clásico
    3 : 6818718,//Corte Infantil
    4 : 9201143, // Limpieza Facial  
    5 : 7304948 ,//AROMATERAPIA
    6 : 4800866 , // MASAJES
}


function asignarImg(){
    fetch('/obtener_servicios/')
    .then(response => response.json())
    .then(servicios => {
        servicios.forEach(servicio => {
            // como es un objeto se deben buscar sus elementos key con llaves []n
            let img_selected = imagenes[servicio.id] // el id del servicio que viene desde la consulta a la BD que esta dentro de la api de nuestra aplicacio django (url) 
            

            // Consulta a la api de Pixaby 
            fetch(`https://pixabay.com/api/?key=${apiKey}&id=${img_selected}&image_type=photo`)
            .then(response => response.json())
            .then(data => {
                let dato = data.hits[0] /* Primera posicion del arreglo hits que viene de la api  */
                
                if (dato) { /* Como es un API puede que el ID lo cambien o elimen la imagen por eso es mejor crear validaciones */
                    let img = document.getElementById(`img_${servicio.id}`)
                    img.src = dato.webformatURL
                    img.style.objectFit = 'cover'; 
                    img.style.height='200px'
                }
            })
        });
    })
}

asignarImg()

// 1179459 , 5711575 Corte cabello
// 3173419 , 1007875 Barba
// 3184610  masajes y spa
// 8307698 Mascarillas

