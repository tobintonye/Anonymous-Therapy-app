document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const mainNav = document.getElementById('main-nav');
   
    function isMobile() {
        return window.innerWidth <= 768;
    }
    
    // Function to handle the close button visibility
    function handleCloseButtonVisibility() {
        // Use a MutationObserver to detect when the dropdown menu is added to the DOM
        const dropdownContainer = document.getElementById('dropdown-menu-container');
        if (!dropdownContainer) return;
        
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check if a dropdown menu was added
                    const closeButton = dropdownContainer.querySelector('.dropdown-close');
                    if (closeButton && isMobile()) {
                        // Remove close button on mobile
                        closeButton.remove();
                    }
                }
            });
        });
        
        // Start observing the dropdown container
        observer.observe(dropdownContainer, { childList: true });
    }
    
    // Call the function to set up the observer
    handleCloseButtonVisibility();
    
    // Also handle window resize events
    window.addEventListener('resize', function() {
        const closeButton = document.querySelector('.dropdown-close');
        if (closeButton) {
            closeButton.style.display = isMobile() ? 'none' : 'flex';
        }
    });
    
    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', function(event) {
            // Prevent this event from bubbling up
            event.stopPropagation();
            
            mainNav.classList.toggle('active');
            this.classList.toggle('active');
            const icon = mobileNavToggle.querySelector('i');
            if (mainNav.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-xmark');
            } else {
                icon.classList.remove('fa-xmark');
                icon.classList.add('fa-bars');
            }
        });
    }

    // Avatar dropdown toggle
    const avatarButton = document.querySelector('.avatar-button');
    if (avatarButton) {
        avatarButton.addEventListener('click', function(event) {
            // Prevent this event from bubbling up
            event.stopPropagation();
            
            // Make sure this doesn't also toggle the mobile nav
            if (mobileNavToggle && event.target !== mobileNavToggle) {
                // Do nothing - the HTMX will handle this
            }
        });
    }

    // Set active navigation link based on current URL
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Add animation to cards on scroll
    const cards = document.querySelectorAll('.therapist-card');
    
    function checkVisibility() {
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const isVisible = (rect.top <= window.innerHeight * 0.8 && rect.bottom >= 0);
            
            if (isVisible) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }
        });
    }
    
    // Initialize cards
    if (cards.length > 0) {
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            // Stagger the animation timing
            card.style.transition = `opacity 0.5s ease ${index * 0.1}s, transform 0.5s ease ${index * 0.1}s`;
        });
        
        // Check visibility on load and scroll
        checkVisibility();
        window.addEventListener('scroll', checkVisibility);
    }
    
    // Handle clicks outside the dropdown to close it
    document.addEventListener('click', function(event) {
        const dropdownContainer = document.getElementById('dropdown-menu-container');
        
        
        if (dropdownContainer && 
            dropdownContainer.children.length > 0 && 
            !dropdownContainer.contains(event.target) && 
            !avatarButton.contains(event.target)) {
            // Clear the dropdown content when clicking outside
            dropdownContainer.innerHTML = '';
        }
    });
});