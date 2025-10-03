document.addEventListener('DOMContentLoaded', function() {
const cartIcon = document.querySelector('#open-cart-btn'); 
    const closeCartBtn = document.querySelector('.close-cart-btn');
    const cartOverlay = document.querySelector('.cart-overlay');
    
    if (cartIcon) {
        cartIcon.addEventListener('click', (e) => {
            e.preventDefault();
            document.body.classList.add('cart-open');
        });
    }
    if (closeCartBtn) {
        closeCartBtn.addEventListener('click', () => document.body.classList.remove('cart-open'));
    }
    if (cartOverlay) {
        cartOverlay.addEventListener('click', () => document.body.classList.remove('cart-open'));
    }
});