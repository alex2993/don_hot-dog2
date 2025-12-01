let numbers = {}
let btnValueLocal = {}


let buttonAddFirst = document.getElementsByClassName('txt_btn')
let button_Number = document.getElementsByClassName('button_Number')
let buttonPlus = document.getElementsByClassName('button_Plus')
let buttonMinus = document.getElementsByClassName('button_Minus')
let allSec = document.getElementsByClassName('kolvo')


document.addEventListener('DOMContentLoaded', (event) => {

  if (localStorage.getItem('numbers')) {
    numbers = JSON.parse(localStorage.getItem('numbers'))
  }

  if (localStorage.getItem('values_button')) {
    btnValueLocal = JSON.parse(localStorage.getItem('values_button'))
    let arrayNames = []
    for (let key in btnValueLocal) {
      arrayNames.push(key)
    }

    arrayNames.forEach((el) => {
      let allSecTarget = document.getElementById(el).children[4].children[1]
      let buttonAddFirstTarget = document.getElementById(el).children[4].children[0]
      let btnValueTarget = document.getElementById(el).children[4].children[1].children[2]

      if (btnValueLocal[el].value <= 0) {
        allSecTarget.style.display = 'none'
        console.log(allSecTarget)
      } else {

        allSecTarget.style.display = 'block'
        buttonAddFirstTarget.style.display = 'none'
        btnValueTarget.textContent = btnValueLocal[el].value
      }
    })

  }
})



for (let i = 0; i < buttonAddFirst.length; i++) {
  buttonAddFirst[i].addEventListener('click', (event) => {
    console.log(event.srcElement.parentElement.parentElement.children[2].textContent)

    
    
    let idEl = event.srcElement.parentElement.parentElement.id;
    let currentValue = event.srcElement.parentElement.children[1].childNodes[5].textContent;
    currentValue = 1
    btnValueLocal[idEl] = {
      id: event.srcElement.parentElement.parentElement.id,
      value: Number(currentValue),
      cost: Number(event.srcElement.parentElement.parentElement.children[1].textContent.split('₽').join('')),
      src: event.srcElement.parentElement.parentElement.children[0].src,
      str: event.srcElement.parentElement.parentElement.children[2].textContent,
      Text: event.srcElement.parentElement.parentElement.children[3].textContent
    }

    localStorage.setItem('values_button', JSON.stringify(btnValueLocal))
      button_Number[i].textContent = btnValueLocal[idEl].value
      allSec[i].style.display = 'block'
      buttonAddFirst[i].style.display = 'none'

  })

  buttonPlus[i].addEventListener('click', (event) => {
    let idEl = event.srcElement.parentElement.parentElement.parentElement.id
    let currentValue = event.srcElement.parentElement.childNodes[5];
    btnValueLocal[idEl].value++
    currentValue.textContent = btnValueLocal[idEl].value
    localStorage.setItem('values_button', JSON.stringify(btnValueLocal))
  })

  buttonMinus[i].addEventListener('click', (event) => {

    let idEl = event.srcElement.parentElement.parentElement.parentElement.id
    let currentValue = event.srcElement.parentElement.childNodes[5];
    btnValueLocal[idEl].value--
    
    currentValue.textContent = btnValueLocal[idEl].value
    if (btnValueLocal[idEl].value < 1) {
      allSec[i].style.display = 'none'
      buttonAddFirst[i].style.display = 'block'
      delete btnValueLocal[idEl]
    }

    localStorage.setItem('values_button', JSON.stringify(btnValueLocal))

  })

}


const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        document.querySelectorAll('.link').forEach((link) => {
          let id = link.getAttribute('href').replace('#', '');
          if (id === entry.target.id) {
            link.classList.add('link--active');
          } else {
            link.classList.remove('link--active');
          }
        });
      }
    });
  }, {
    threshold: 0.5
  });
  
  document.querySelectorAll('.nm').forEach(el => { observer.observe(el) });
  
  
  let tryba = document.getElementById('tryba')
  tryba.addEventListener('click', () => {
    alert('Контактный номер: +7 (911) 629-47-40 ')
  })
  
  let tryba_2 = document.getElementById('tryba_2')
  tryba_2.addEventListener('click', () => {
    alert('Контактный номер: +7 (911) 629-47-40 ')
  })