
let check = document.getElementById('check')
let titulo = document.getElementById('titulo-form')

check.addEventListener('change',()=>{
    let card = document.getElementById('card')
    if (check.checked){
        card.classList.toggle('flipped')
       
    } else{
        card.classList.remove('flipped')
        
    }
})