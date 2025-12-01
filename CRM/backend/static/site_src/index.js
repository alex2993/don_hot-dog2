let slides = document.querySelectorAll('.slide');
let currentSlide = 0;
let slideInterval = setInterval(nextSlide, 5000);

function nextSlide() {
  slides[currentSlide].className = 'slide';
  currentSlide = (currentSlide + 1) % slides.length;
  slides[currentSlide].className = 'slide showing';
}


let card = document.getElementById('card')
let cardText = document.getElementById('cardText')
card.addEventListener('mouseover', () => {
  cardText.style.color = "#E2B802"
})
card.addEventListener('mouseout', () => {
  cardText.style.color = 'black'
})

let card_2 = document.getElementById('card_2')
let cardText_2 = document.getElementById('cardText_2')
card_2.addEventListener('mouseover', () => {
  cardText_2.style.color = "#E2B802"
})
card_2.addEventListener('mouseout', () => {
  cardText_2.style.color = 'black'
})

let card_3 = document.getElementById('card_3')
let cardText_3 = document.getElementById('cardText_3')
card_3.addEventListener('mouseover', () => {
  cardText_3.style.color = "#E2B802"
})
card_3.addEventListener('mouseout', () => {
  cardText_3.style.color = 'black'
})

let card_4 = document.getElementById('card_4')
let cardText_4 = document.getElementById('cardText_4')
card_4.addEventListener('mouseover', () => {
  cardText_4.style.color = "#E2B802"
})
card_4.addEventListener('mouseout', () => {
  cardText_4.style.color = 'black'
})

let card_5 = document.getElementById('card_5')
let cardText_5 = document.getElementById('cardText_5')
card_5.addEventListener('mouseover', () => {
  cardText_5.style.color = "#E2B802"
})
card_5.addEventListener('mouseout', () => {
  cardText_5.style.color = 'black'
})

let tryba = document.getElementById('tryba')
tryba.addEventListener('click', () => {
  alert('Контактный номер: +7 (911) 629-47-40 ')
})

let tryba_2 = document.getElementById('tryba_2')
tryba_2.addEventListener('click', () => {
  alert('Контактный номер: +7 (911) 629-47-40 ')
})