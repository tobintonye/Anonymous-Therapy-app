document.addEventListener('DOMContentLoaded', function() {
    // Animation for elements on page load
    const elements = [
        document.querySelector('.profile-name'),
        document.querySelector('.profile-username'),
        document.querySelector('.profile-bio'),
        ...document.querySelectorAll('.profile-section'),
        document.querySelector('.profile-meta'),
        document.querySelector('.contact-button')
    ];
    
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = `opacity 0.5s ease ${0.2 + index * 0.1}s, transform 0.5s ease ${0.2 + index * 0.1}s`;
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100);
    });
    
    // Image modal functionality
    const profileImage = document.getElementById('profileImage');
    const imageModal = document.getElementById('imageModal');
    const fullImage = document.getElementById('fullImage');
    const closeModal = document.getElementById('closeModal');
    
    // Open modal when profile image is clicked
    profileImage.addEventListener('click', function() {
        fullImage.src = this.src;
        imageModal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling when modal is open
    });
    
    // Close modal when close button is clicked
    closeModal.addEventListener('click', function() {
        imageModal.classList.remove('active');
        setTimeout(() => {
            document.body.style.overflow = ''; // Re-enable scrolling
        }, 300);
    });
    
    // Close modal when clicking outside the image
    imageModal.addEventListener('click', function(e) {
        if (e.target === imageModal) {
            imageModal.classList.remove('active');
            setTimeout(() => {
                document.body.style.overflow = '';
            }, 300);
        }
    });
    
    // Close modal when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && imageModal.classList.contains('active')) {
            imageModal.classList.remove('active');
            setTimeout(() => {
                document.body.style.overflow = '';
            }, 300);
        }
    });
    
    // Basic image zoom functionality
    let scale = 1;
    const MAX_SCALE = 3;
    const MIN_SCALE = 1;
    
    fullImage.addEventListener('wheel', function(e) {
        e.preventDefault();
        
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale + delta));
        
        fullImage.style.transform = `scale(${scale})`;
    });
    
    // Reset scale when modal is closed
    closeModal.addEventListener('click', function() {
        scale = 1;
        fullImage.style.transform = '';
    });
});