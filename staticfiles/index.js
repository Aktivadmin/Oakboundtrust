//Mobile navigation animation

const mobileNavMenu = document.querySelector('.mobile-navigation-menu');
const hamburgerMenuIcon = document.querySelector('.ham-menu');

const firstHamBar = document.querySelector('.ham-menu .bar:first-child');
const secondHamBar = document.querySelector('.ham-menu .bar:nth-child(2)');
const thirdHamBar = document.querySelector('.ham-menu .bar:last-child');

hamburgerMenuIcon.addEventListener('mousedown', function() {
    mobileNavMenu.classList.toggle('appear');
    firstHamBar.classList.toggle('rotate-left');
    secondHamBar.classList.toggle('opaque');
    thirdHamBar.classList.toggle('rotate-right');
})