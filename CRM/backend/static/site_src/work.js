document.addEventListener('DOMContentLoaded', (ev) => {
    if (localStorage.getItem('curr-user')) {
        let currentUser = JSON.parse(localStorage.getItem('curr-user'))
        document.forms.formWork.name.value = currentUser.name
        document.forms.formWork.number.value = currentUser.contactInfo.phone
    }
})


let tryba = document.getElementById('tryba')
tryba.addEventListener('click', () => {
    alert('Контактный номер: +7 (911) 629-47-40 ')
})

let tryba_2 = document.getElementById('tryba_2')
tryba_2.addEventListener('click', () => {
    alert('Контактный номер: +7 (911) 629-47-40 ')
})

document.getElementById('send').addEventListener('click', (ev) => {
    ev.preventDefault()

    
    

    const form = document.forms.formWork
    let name = form.name.value
    let number = form.number.value
    let adres = form.city.value
    let mail = form.email.value
    let professia = form.professia.value
    
    let work = {
        name: `${name}`,
        number: number,
        adres: `${adres}`,
        mail: `${mail}`,
        proffessia: `${professia}`
    }

    console.log(work)

    addWork(work)
})

async function  addWork(workB) {
    let response = await fetch('http://localhost:8080/addWork', {    
        method: 'POST',
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: JSON.stringify(workB)
      })
alert('Work added')
}