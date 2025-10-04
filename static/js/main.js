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