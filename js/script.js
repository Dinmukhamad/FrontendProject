// ============================================
// PRESTIGE MOTORS - INTERACTIVE FEATURES
// Modern JavaScript Implementation
// ============================================

(function() {
    'use strict';

    // DOM Content Loaded Event
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    function initializeApp() {
        // Initialize all features
        initScrollEffects();
        initNavigationEffects();
        initCarCardInteractions();
        initContactForm();
        initImageLazyLoading();
        initTypewriterEffect();
        initSmoothScrolling();
        initMobileNavigation();
    }

    // ============================================
    // SCROLL EFFECTS & ANIMATIONS
    // ============================================
    function initScrollEffects() {
        // Header background opacity on scroll
        let lastScrollTop = 0;
        const header = document.querySelector('header');
        
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Header background effect
            if (scrollTop > 50) {
                header.style.backgroundColor = 'rgba(11, 11, 11, 0.98)';
                header.style.backdropFilter = 'blur(20px)';
            } else {
                header.style.backgroundColor = 'rgba(11, 11, 11, 0.95)';
                header.style.backdropFilter = 'blur(10px)';
            }

            // Scroll direction detection for future enhancements
            const isScrollingDown = scrollTop > lastScrollTop;
            lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
        });

        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, observerOptions);

        // Observe elements for animations
        const animateElements = document.querySelectorAll('.car-card, .contact-item, .intro, .section-title');
        animateElements.forEach(element => {
            observer.observe(element);
        });
    }

    // ============================================
    // NAVIGATION ENHANCEMENTS
    // ============================================
    function initNavigationEffects() {
        const navLinks = document.querySelectorAll('.nav-links a');
        
        navLinks.forEach(link => {
            link.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
            });
            
            link.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });

        // Active page highlighting
        const currentPage = window.location.pathname.split('/').pop();
        navLinks.forEach(link => {
            const linkPage = link.getAttribute('href');
            if (linkPage === currentPage || (currentPage === '' && linkPage === 'index.html')) {
                link.classList.add('active');
            }
        });
    }

    // ============================================
    // CAR CARD INTERACTIONS
    // ============================================
    function initCarCardInteractions() {
        const carCards = document.querySelectorAll('.car-card');
        
        carCards.forEach(card => {
            const img = card.querySelector('.car-image');
            const content = card.querySelector('.car-content');
            
            // Hover effects
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-10px) scale(1.02)';
                this.style.boxShadow = '0 20px 40px rgba(201, 162, 77, 0.2)';
                
                if (img) {
                    img.style.transform = 'scale(1.1)';
                }
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = 'none';
                
                if (img) {
                    img.style.transform = 'scale(1)';
                }
            });

            // Click interaction for "View Details" buttons
            const detailBtn = card.querySelector('.btn');
            if (detailBtn) {
                detailBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    const carName = card.querySelector('h3').textContent;
                    showCarDetails(carName);
                });
            }
        });
    }

    function showCarDetails(carName) {
        // Create modal for car details
        const modal = createModal(
            `${carName} Details`,
            `
                <div class="car-details">
                    <h3>${carName}</h3>
                    <p>Thank you for your interest in the ${carName}. Our luxury vehicle specialists will be happy to provide you with detailed information, arrange a private viewing, or schedule a test drive.</p>
                    <div class="detail-actions">
                        <button class="btn btn-primary" onclick="window.location.href='contact.html'">Contact Us</button>
                        <button class="btn" onclick="closeModal()">Close</button>
                    </div>
                </div>
            `
        );
        document.body.appendChild(modal);
        
        // Add close functionality
        window.closeModal = function() {
            document.body.removeChild(modal);
        };
    }

    // ============================================
    // CONTACT FORM ENHANCEMENTS
    // ============================================
    function initContactForm() {
        const contactForm = document.querySelector('.contact-form');
        if (!contactForm) return;
        
        const inputs = contactForm.querySelectorAll('input, textarea');
        
        // Input focus effects
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                if (!this.value.trim()) {
                    this.parentElement.classList.remove('focused');
                }
            });
            
            // Real-time validation
            input.addEventListener('input', function() {
                validateField(this);
            });
        });
        
        // Form submission
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (validateForm(this)) {
                submitForm(this);
            }
        });
    }

    function validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        let isValid = true;
        
        // Remove previous error styling
        field.classList.remove('error');
        
        // Validation rules
        switch(fieldType) {
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                isValid = emailRegex.test(value);
                break;
            case 'tel':
                const phoneRegex = /^[\+]?[1-9][\d\s\-\(\)]{7,}$/;
                isValid = !value || phoneRegex.test(value); // Phone is optional
                break;
            case 'text':
            case 'textarea':
                if (field.hasAttribute('required')) {
                    isValid = value.length >= 2;
                }
                break;
        }
        
        if (!isValid) {
            field.classList.add('error');
        }
        
        return isValid;
    }

    function validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isFormValid = true;
        
        requiredFields.forEach(field => {
            if (!validateField(field)) {
                isFormValid = false;
            }
        });
        
        return isFormValid;
    }

    function submitForm(form) {
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Sending...';
        submitBtn.disabled = true;
        
        // Simulate form submission (replace with actual endpoint)
        setTimeout(() => {
            showNotification('Message sent successfully! We will contact you shortly.', 'success');
            form.reset();
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }, 2000);
    }

    // ============================================
    // IMAGE LAZY LOADING
    // ============================================
    function initImageLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }

    // ============================================
    // TYPEWRITER EFFECT FOR HERO SECTION
    // ============================================
    function initTypewriterEffect() {
        const heroTitle = document.querySelector('.hero h1');
        if (!heroTitle) return;
        
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        heroTitle.style.borderRight = '2px solid #c9a24d';
        
        let i = 0;
        function typeWriter() {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            } else {
                // Remove cursor after typing is complete
                setTimeout(() => {
                    heroTitle.style.borderRight = 'none';
                }, 1000);
            }
        }
        
        // Start typewriter effect after a delay
        setTimeout(typeWriter, 1000);
    }

    // ============================================
    // SMOOTH SCROLLING
    // ============================================
    function initSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // ============================================
    // MOBILE NAVIGATION
    // ============================================
    function initMobileNavigation() {
        // Create mobile menu button if it doesn't exist
        const nav = document.querySelector('nav');
        const navLinks = document.querySelector('.nav-links');
        
        if (window.innerWidth <= 768) {
            let mobileMenuBtn = document.querySelector('.mobile-menu-btn');
            if (!mobileMenuBtn) {
                mobileMenuBtn = document.createElement('button');
                mobileMenuBtn.className = 'mobile-menu-btn';
                mobileMenuBtn.innerHTML = '☰';
                mobileMenuBtn.setAttribute('aria-label', 'Toggle mobile menu');
                nav.appendChild(mobileMenuBtn);
                
                mobileMenuBtn.addEventListener('click', function() {
                    navLinks.classList.toggle('mobile-open');
                    this.textContent = navLinks.classList.contains('mobile-open') ? '✕' : '☰';
                });
            }
        }
    }

    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    function createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <span class="close" onclick="closeModal()">&times;</span>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        // Close modal when clicking outside
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
        
        return modal;
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Remove notification after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 5000);
    }

    // ============================================
    // PERFORMANCE MONITORING
    // ============================================
    function logPerformance() {
        if (window.performance && window.performance.timing) {
            const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
            console.log(`Page loaded in ${loadTime}ms`);
        }
    }

    // Log performance after page load
    window.addEventListener('load', logPerformance);

    // ============================================
    // ADDITIONAL CSS STYLES VIA JAVASCRIPT
    // ============================================
    function addDynamicStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Fade-in animation */
            .fade-in {
                animation: fadeInUp 0.8s ease forwards;
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Form styling enhancements */
            .form-group.focused label {
                color: #c9a24d;
                transform: translateY(-5px);
                font-size: 0.9em;
            }
            
            .form-group input.error,
            .form-group textarea.error {
                border-color: #ff6b6b;
                box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
            }
            
            /* Modal styles */
            .modal {
                display: flex;
                position: fixed;
                z-index: 2000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.8);
                align-items: center;
                justify-content: center;
            }
            
            .modal-content {
                background-color: #1a1a1a;
                margin: auto;
                padding: 0;
                border: 1px solid #c9a24d;
                width: 90%;
                max-width: 500px;
                border-radius: 8px;
                color: #f5f5f5;
            }
            
            .modal-header {
                padding: 20px;
                border-bottom: 1px solid #2a2a2a;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-body {
                padding: 20px;
            }
            
            .close {
                color: #aaa;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }
            
            .close:hover {
                color: #c9a24d;
            }
            
            /* Notification styles */
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 5px;
                color: white;
                font-weight: 500;
                z-index: 3000;
                transform: translateX(400px);
                transition: transform 0.3s ease;
            }
            
            .notification.show {
                transform: translateX(0);
            }
            
            .notification.success {
                background-color: #4CAF50;
            }
            
            .notification.error {
                background-color: #f44336;
            }
            
            /* Mobile menu styles */
            @media (max-width: 768px) {
                .mobile-menu-btn {
                    display: block;
                    background: none;
                    border: none;
                    color: #c9a24d;
                    font-size: 1.5rem;
                    cursor: pointer;
                }
                
                .nav-links {
                    position: absolute;
                    top: 100%;
                    left: 0;
                    width: 100%;
                    background-color: rgba(11, 11, 11, 0.98);
                    flex-direction: column;
                    padding: 20px 0;
                    transform: translateY(-100%);
                    opacity: 0;
                    visibility: hidden;
                    transition: all 0.3s ease;
                }
                
                .nav-links.mobile-open {
                    transform: translateY(0);
                    opacity: 1;
                    visibility: visible;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Add dynamic styles when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addDynamicStyles);
    } else {
        addDynamicStyles();
    }

})();
