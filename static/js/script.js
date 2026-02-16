// ============================================
// PRESTIGE MOTORS - INTERACTIVE FEATURES
// Single Page Application (SPA) Version
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
        initSinglePageNavigation();
        initCarCardInteractions();
        initContactForm();
        initImageLazyLoading();
        initTypewriterEffect();
        initMobileNavigation();
    }

    // ============================================
    // SINGLE PAGE NAVIGATION
    // ============================================
    function initSinglePageNavigation() {
        const navLinks = document.querySelectorAll('.nav-links a, a[href^="#"]');
        const header = document.querySelector('header');
        const headerHeight = header ? header.offsetHeight : 0;

        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                
                // Only handle hash links
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    
                    const targetId = href.substring(1);
                    const targetElement = document.getElementById(targetId);
                    
                    if (targetElement) {
                        // Calculate position with offset for fixed header
                        const targetPosition = targetElement.offsetTop - headerHeight;
                        
                        // Smooth scroll to target
                        window.scrollTo({
                            top: targetPosition,
                            behavior: 'smooth'
                        });
                        
                        // Update active navigation state
                        updateActiveNavLink(targetId);
                        
                        // Close mobile menu if open
                        const navLinksContainer = document.querySelector('.nav-links');
                        if (navLinksContainer && navLinksContainer.classList.contains('mobile-open')) {
                            navLinksContainer.classList.remove('mobile-open');
                            const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
                            if (mobileMenuBtn) {
                                mobileMenuBtn.textContent = '☰';
                            }
                        }
                    }
                }
            });
        });

        // Update active link on scroll
        let ticking = false;
        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(function() {
                    updateActiveNavOnScroll();
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    function updateActiveNavLink(activeId) {
        const navLinks = document.querySelectorAll('.nav-links a');
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === `#${activeId}`) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    function updateActiveNavOnScroll() {
        const sections = document.querySelectorAll('section[id]');
        const scrollPosition = window.scrollY + 150;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                updateActiveNavLink(sectionId);
            }
        });
    }

    // ============================================
    // SCROLL EFFECTS & ANIMATIONS
    // ============================================
    function initScrollEffects() {
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
    }

    // ============================================
    // CAR CARD INTERACTIONS
    // ============================================
    function initCarCardInteractions() {
        const carCards = document.querySelectorAll('.car-card');
        
        carCards.forEach(card => {
            const img = card.querySelector('.car-image');
            
            // Hover effects only - no click interception
            card.addEventListener('mouseenter', function() {
                this.style.boxShadow = '0 20px 40px rgba(201, 162, 77, 0.2)';
                
                if (img) {
                    img.style.transform = 'scale(1.1)';
                }
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.boxShadow = 'none';
                
                if (img) {
                    img.style.transform = 'scale(1)';
                }
            });
        });
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
                isValid = !value || phoneRegex.test(value);
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
        
        // Simulate form submission
        setTimeout(() => {
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
                setTimeout(() => {
                    heroTitle.style.borderRight = 'none';
                }, 1000);
            }
        }
        
        setTimeout(typeWriter, 1000);
    }

    // ============================================
    // MOBILE NAVIGATION
    // ============================================
    function initMobileNavigation() {
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

        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                navLinks.classList.remove('mobile-open');
                const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
                if (mobileMenuBtn) {
                    mobileMenuBtn.textContent = '☰';
                }
            }
        });
    }

    // ============================================
    // UTILITY FUNCTIONS
    // ============================================

    // ============================================
    // PERFORMANCE MONITORING
    // ============================================
    function logPerformance() {
        if (window.performance && window.performance.timing) {
            const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
            console.log(`Page loaded in ${loadTime}ms`);
        }
    }

    window.addEventListener('load', logPerformance);

    // ============================================
    // DYNAMIC STYLES
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
            
            /* Smooth scroll behavior */
            html {
                scroll-behavior: smooth;
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
            
            /* Mobile menu styles */
            @media (max-width: 768px) {
                .mobile-menu-btn {
                    display: block;
                    background: none;
                    border: none;
                    color: #c9a24d;
                    font-size: 1.5rem;
                    cursor: pointer;
                    padding: 0.5rem;
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
                
                .nav-links li {
                    width: 100%;
                    text-align: center;
                }
            }
        `;
        document.head.appendChild(style);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addDynamicStyles);
    } else {
        addDynamicStyles();
    }

})();
