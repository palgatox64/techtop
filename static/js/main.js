document.addEventListener('DOMContentLoaded', function() {


    console.log("Intentando inicializar Swiper...");

    const swiper = new Swiper('.swiper', {
        direction: 'horizontal',
        loop: true,
      
        pagination: {
          el: '.swiper-pagination',
          clickable: true,
        },
      
        navigation: {
          nextEl: '.swiper-button-next',
          prevEl: '.swiper-button-prev',
        },

        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
    });
});


document.addEventListener('DOMContentLoaded', function() {
    
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenuDropdown = document.getElementById('user-menu-dropdown');
    
    const userMenuButtonLoggedIn = document.getElementById('user-menu-button-loggedin');
    const userMenuDropdownLoggedIn = document.getElementById('user-menu-dropdown-loggedin');

    if (userMenuButton) {
        userMenuButton.addEventListener('click', function(event) {
            event.stopPropagation(); 
            userMenuDropdown.classList.toggle('show');
        });
    }

    if (userMenuButtonLoggedIn) {
        userMenuButtonLoggedIn.addEventListener('click', function(event) {
            event.stopPropagation(); 
            userMenuDropdownLoggedIn.classList.toggle('show');
        });
    }

    window.addEventListener('click', function(event) {
        if (userMenuDropdown && userMenuDropdown.classList.contains('show')) {
            userMenuDropdown.classList.remove('show');
        }
        if (userMenuDropdownLoggedIn && userMenuDropdownLoggedIn.classList.contains('show')) {
            userMenuDropdownLoggedIn.classList.remove('show');
        }
    });
});