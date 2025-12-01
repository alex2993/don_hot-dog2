let dat
document.addEventListener('DOMContentLoaded', () => {
    dat = JSON.parse(localStorage.values_button)
    for (let key in dat) {
        let el = dat[key]
        document.getElementById('main').insertAdjacentHTML('beforeend', `  <article class="card" id="${key}">
    <img src=${el.src} class="card_img">
    <article class = "mains">
    <p id="name" class="card_title">${el.str}</p>
    <p id = "ves">${el.Text}</p>
    </article>
    <article class="kolvo">
    <input type="button" class="button_Plus" value="+">
    <p class = "value">${el.value}</p>
    <input type="button" class="button_Minus" value="-">
    </article>
    <p id="price" class="card_prise">${el.cost * el.value}</p>
    <button class="del">X</button>
    </article>`)
        let plus = document.getElementById(key).children[2].children[0]
        let value = document.getElementById(key).children[2].children[1].textContent
        let minus = document.getElementById(key).children[2].children[2]
        plus.addEventListener('click', (ev) => {
            value++
            dat[key].value = value
            ev.srcElement.parentElement.parentElement.children[3].textContent = el.cost * el.value
            localStorage.setItem('values_button', JSON.stringify(dat))
            document.getElementById(key).children[2].children[1].textContent = value
        })

        minus.addEventListener('click', (ev) => {
            if (value < 2) {
                ev.srcElement.parentElement.parentElement.remove()
                delete dat[key]
                localStorage.setItem('values_button', JSON.stringify(dat))
            }
            console.log()
            value--
            dat[key].value = value
            ev.srcElement.parentElement.parentElement.children[3].textContent = el.cost * value
            localStorage.setItem('values_button', JSON.stringify(dat))
            document.getElementById(key).children[2].children[1].textContent = value
        })
    }
    del();
})

function del() {
    let delButtons = document.getElementsByClassName('del');
    for (let i = 0; i < delButtons.length; i++) {
        delButtons[i].addEventListener('click', (ev) => {
            let currentCard = ev.srcElement.parentElement
            let cardId = currentCard.id
            for (let el in dat) {
                if (cardId === el) { delete dat[el] }
            }
            localStorage.setItem('values_button', JSON.stringify(dat))
            currentCard.remove()
        })
    }
}






let tryba = document.getElementById('tryba')
tryba.addEventListener('click', () => {
    alert('Контактный номер: +7 (911) 629-47-40 ')
})

let tryba_2 = document.getElementById('tryba_2')
tryba_2.addEventListener('click', () => {
    alert('Контактный номер: +7 (911) 629-47-40 ')
})