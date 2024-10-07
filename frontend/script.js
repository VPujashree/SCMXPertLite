document.getElementById('switch').addEventListener('click', function() {
    document.querySelector('.card-inner').style.transform = 'rotateY(180deg)';
});

document.getElementById('switch-back').addEventListener('click', function() {
    document.querySelector('.card-inner').style.transform = 'rotateY(0deg)';
});
