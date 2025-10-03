document.addEventListener('DOMContentLoaded', function() {
    const dropdownItems = document.querySelectorAll('.nav-item-dropdown');
    if (dropdownItems.length > 0) {
        dropdownItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            link.addEventListener('click', function(event) {
                event.preventDefault();
                const isActive = item.classList.contains('active');
                dropdownItems.forEach(openItem => {
                    openItem.classList.remove('active');
                });
                if (!isActive) {
                    item.classList.add('active');
                }
            });
        });
    }

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