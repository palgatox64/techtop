document.addEventListener('DOMContentLoaded', function() {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
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
    const dropdownItems = document.querySelectorAll('.nav-item-dropdown');
    const pageOverlay = document.getElementById('page-overlay'); 

    dropdownItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        
        link.addEventListener('click', function(event) {
            if (window.innerWidth <= 768) {
                event.preventDefault(); 
                const wasActive = item.classList.contains('active');
                dropdownItems.forEach(openItem => {
                    if (openItem !== item) {
                        openItem.classList.remove('active');
                    }
                });
                if (wasActive) {
                    item.classList.remove('active'); 
                    if (pageOverlay) pageOverlay.classList.remove('is-active'); 
                } else {
                    item.classList.add('active'); 
                    if (pageOverlay) pageOverlay.classList.add('is-active'); 
                }
            }
        });
    });

    document.addEventListener('click', function(event) {
        if (!event.target.closest('.user-menu')) {
            if (userMenuDropdown) userMenuDropdown.classList.remove('show');
            if (userMenuDropdownLoggedIn) userMenuDropdownLoggedIn.classList.remove('show');
        }
        if (window.innerWidth <= 768) {
            const clickedInsideNavbar = event.target.closest('.navbar');
            if (!clickedInsideNavbar) {
                dropdownItems.forEach(item => {
                    item.classList.remove('active');
                });
                if (pageOverlay) pageOverlay.classList.remove('is-active'); 
            }
        }
    });

    if (pageOverlay && dropdownItems.length > 0) {
        dropdownItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                if (window.innerWidth > 768) {
                    pageOverlay.classList.add('is-active');
                }
            });
            item.addEventListener('mouseleave', function() {
                if (window.innerWidth > 768) {
                    pageOverlay.classList.remove('is-active');
                }
            });
        });
    }
    const openBtn = document.getElementById('open-filters-btn');
    const closeBtn = document.getElementById('close-filters-btn');
    const filterSidebar = document.getElementById('filter-sidebar');
    const backdrop = document.getElementById('filter-backdrop');

    if (openBtn) {
        openBtn.addEventListener('click', function() {
            filterSidebar.classList.add('is-open');
            backdrop.classList.add('is-active');
        });
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            filterSidebar.classList.remove('is-open');
            backdrop.classList.remove('is-active');
        });
    }
    if (backdrop) {
        backdrop.addEventListener('click', function() {
            filterSidebar.classList.remove('is-open');
            backdrop.classList.remove('is-active');
        });
    }
    const cartIconButton = document.getElementById('cart-icon-button');
    const cartOffcanvas = document.getElementById('cart-offcanvas');
    const cartBackdrop = document.getElementById('cart-backdrop');
    const closeCartBtn = document.getElementById('close-cart-btn');

    function openCartPanel() {
        if(cartBackdrop) cartBackdrop.classList.add('is-active');
        if(cartOffcanvas) cartOffcanvas.classList.add('is-open');
    }

    function closeCartPanel() {
        if(cartBackdrop) cartBackdrop.classList.remove('is-active');
        if(cartOffcanvas) cartOffcanvas.classList.remove('is-open');
    }

    if(cartIconButton) cartIconButton.addEventListener('click', (e) => { e.preventDefault(); loadInitialCart(); openCartPanel(); });
    if(closeCartBtn) closeCartBtn.addEventListener('click', closeCartPanel);
    if(cartBackdrop) cartBackdrop.addEventListener('click', closeCartPanel);
    function updateCartUI(data) {
        const cartCountSpan = document.getElementById('cart-item-count');
        const cartBody = document.getElementById('cart-offcanvas-body');
        const cartSubtotal = document.getElementById('cart-subtotal');
        
        if (!cartCountSpan || !cartBody || !cartSubtotal) {
            console.error("Elementos del carrito no encontrados en el DOM.");
            return;
        }

        cartCountSpan.textContent = data.cart_item_count;
        cartCountSpan.style.display = data.cart_item_count > 0 ? 'block' : 'none';
        cartBody.innerHTML = '';
        if (data.items && data.items.length > 0) {
            data.items.forEach(item => {
                const formattedPrice = parseFloat(item.price).toLocaleString('es-CL');
                const cartItemHTML = `
                    <div class="cart-offcanvas-item">
                        <img src="${item.image_url}" alt="${item.name}" class="item-image">
                        <div class="item-details">
                            <p class="item-name">${item.name}</p>
                            <p class="item-price">Cantidad: ${item.quantity} x $${formattedPrice}</p>
                        </div>
                        <button class="cart-item-remove" data-item-id="${item.id}" title="Eliminar" style="background:none; border:none; font-size: 1.5rem; color:#900; cursor:pointer; padding: 5px;">&times;</button>
                    </div>
                `;
                cartBody.insertAdjacentHTML('beforeend', cartItemHTML);
            });
            cartSubtotal.textContent = '$' + parseFloat(data.subtotal).toLocaleString('es-CL');
        } else {
            cartBody.innerHTML = '<p>Tu carrito está vacío.</p>';
            cartSubtotal.textContent = '$0';
        }
    }
    document.body.addEventListener('submit', function(event) {
        if (event.target.matches('form[action*="/agregar/"]')) {
            
            const form = event.target;
            const formData = new FormData(form);
            const redirectNext = formData.get('next'); 
            if (redirectNext === 'checkout') {
                return; 
            }
            event.preventDefault();
            const url = form.action;
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken') 
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartUI(data); 
                    Swal.fire({
                        icon: 'success', title: '¡Producto Agregado!', toast: true,
                        position: 'top-end', showConfirmButton: false, timer: 2000, timerProgressBar: true
                    });
                    openCartPanel(); 
                } else {
                    Swal.fire({ icon: 'error', title: 'Oops...', text: data.message || 'Ocurrió un error.' });
                }
            })
            .catch(error => console.error('Error en AJAX al agregar:', error));
        }
    });

    function loadInitialCart() {
        fetch('/api/get-cart/') 
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartUI(data);
                }
            })
            .catch(error => console.error('Error al cargar el carrito inicial:', error));
    }

    loadInitialCart();
    const clearCartBtn = document.getElementById('clear-cart-btn');
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', function() {
            const cartItemCountSpan = document.getElementById('cart-item-count');
            const itemCount = parseInt(cartItemCountSpan?.textContent) || 0;

            if (itemCount === 0) {
                Swal.fire({
                    title: 'Carrito Vacío',
                    text: 'No hay productos para vaciar.',
                    icon: 'info',
                    confirmButtonText: 'Entendido'
                });
                return;
            }

            Swal.fire({
                title: '¿Estás seguro?',
                text: "Se eliminarán todos los productos de tu carrito.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sí, vaciar carrito',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch('/limpiar-carro/', { 
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            loadInitialCart(); 
                            Swal.fire(
                                '¡Vaciado!',
                                'Tu carrito ha sido vaciado.',
                                'success'
                            );

                            closeCartPanel(); 
                        }
                    })
                    .catch(error => console.error('Error al vaciar el carrito:', error));
                }
            });
        });
    }

    if (cartBody) {
        cartBody.addEventListener('click', function(e) {
            if (e.target.classList.contains('cart-item-remove')) {
                e.preventDefault();
                const product_id = e.target.dataset.itemId;
                const url = `/eliminar-del-carro/${product_id}/`; 

                fetch(url, {
                    method: 'POST', 
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateCartUI(data); 
                        closeCartPanel();
                    } else {
                        alert(data.message || 'Error al eliminar el producto.');
                    }
                })
                .catch(error => console.error('Error al eliminar ítem:', error));
            }
        });
    }

}); 