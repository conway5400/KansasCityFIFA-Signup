/**
 * Kansas City FIFA Fan Fest Signup
 * Main JavaScript functionality
 */

(function() {
    'use strict';

    // Utility functions
    const utils = {
        // Debounce function for performance
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Format phone number
        formatPhoneNumber: function(value) {
            const cleaned = value.replace(/\D/g, '');
            const match = cleaned.match(/^(\d{0,3})(\d{0,3})(\d{0,4})$/);
            if (match) {
                let formatted = '';
                if (match[1]) {
                    formatted = '(' + match[1];
                }
                if (match[2]) {
                    formatted += ') ' + match[2];
                }
                if (match[3]) {
                    formatted += '-' + match[3];
                }
                return formatted;
            }
            return value;
        },

        // Validate email
        isValidEmail: function(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        },

        // Show/hide loading state
        setLoading: function(button, isLoading) {
            const btnText = button.querySelector('.btn-text');
            const btnLoading = button.querySelector('.btn-loading');
            
            if (isLoading) {
                btnText.style.display = 'none';
                btnLoading.style.display = 'flex';
                button.disabled = true;
            } else {
                btnText.style.display = 'block';
                btnLoading.style.display = 'none';
                button.disabled = false;
            }
        }
    };

    // Form handling
    const formHandler = {
        init: function() {
            const form = document.querySelector('.signup-form');
            if (!form) return;

            this.form = form;
            this.submitBtn = form.querySelector('#submitBtn');
            this.setupValidation();
            this.setupFormatters();
            this.setupSubmission();
        },

        setupValidation: function() {
            // Real-time email validation
            const emailInput = this.form.querySelector('[name="email"]');
            if (emailInput) {
                emailInput.addEventListener('blur', utils.debounce(function() {
                    const value = emailInput.value.trim();
                    if (value && !utils.isValidEmail(value)) {
                        emailInput.setCustomValidity('Please enter a valid email address');
                    } else {
                        emailInput.setCustomValidity('');
                    }
                }, 300));
            }

            // Zip code validation
            const zipInput = this.form.querySelector('[name="zip_code"]');
            if (zipInput) {
                zipInput.addEventListener('input', function() {
                    // Only allow digits
                    this.value = this.value.replace(/\D/g, '').substring(0, 10);
                });
            }

            // Events validation
            const eventCheckboxes = this.form.querySelectorAll('[name="events_interested"]');
            if (eventCheckboxes.length > 0) {
                eventCheckboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', function() {
                        const checked = document.querySelectorAll('[name="events_interested"]:checked');
                        eventCheckboxes.forEach(cb => {
                            cb.setCustomValidity(checked.length === 0 ? 'Please select at least one event' : '');
                        });
                    });
                });
            }
        },

        setupFormatters: function() {
            // Phone number formatting
            const phoneInput = this.form.querySelector('[name="phone"]');
            if (phoneInput) {
                phoneInput.addEventListener('input', utils.debounce(function() {
                    const formatted = utils.formatPhoneNumber(this.value);
                    this.value = formatted;
                }, 100));
            }

            // Name capitalization
            const nameInput = this.form.querySelector('[name="name"]');
            if (nameInput) {
                nameInput.addEventListener('blur', function() {
                    const words = this.value.trim().split(' ');
                    const capitalized = words.map(word => {
                        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
                    }).join(' ');
                    this.value = capitalized;
                });
            }
        },

        setupSubmission: function() {
            const self = this;
            
            this.form.addEventListener('submit', function(e) {
                // Show loading state
                utils.setLoading(self.submitBtn, true);

                // Validate form
                if (!self.validateForm()) {
                    e.preventDefault();
                    utils.setLoading(self.submitBtn, false);
                    return false;
                }

                // Track submission
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'form_submit_attempt', {
                        'event_category': 'engagement',
                        'event_label': 'signup_form'
                    });
                }
            });

            // Restore button on page show (back button)
            window.addEventListener('pageshow', function(e) {
                if (e.persisted) {
                    utils.setLoading(self.submitBtn, false);
                }
            });
        },

        validateForm: function() {
            const requiredFields = ['name', 'email', 'zip_code'];
            let isValid = true;

            // Check required fields
            requiredFields.forEach(fieldName => {
                const field = this.form.querySelector(`[name="${fieldName}"]`);
                if (!field.value.trim()) {
                    field.setCustomValidity('This field is required');
                    field.reportValidity();
                    isValid = false;
                }
            });

            // Check at least one event selected
            const eventCheckboxes = this.form.querySelectorAll('[name="events_interested"]:checked');
            if (eventCheckboxes.length === 0) {
                const firstCheckbox = this.form.querySelector('[name="events_interested"]');
                if (firstCheckbox) {
                    firstCheckbox.setCustomValidity('Please select at least one event');
                    firstCheckbox.reportValidity();
                    isValid = false;
                }
            }

            return isValid;
        }
    };

    // Analytics tracking
    const analytics = {
        init: function() {
            this.trackPageView();
            this.trackEngagement();
        },

        trackPageView: function() {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'page_view', {
                    'page_title': document.title,
                    'page_location': window.location.href,
                    'page_path': window.location.pathname
                });
            }
        },

        trackEngagement: function() {
            // Track form field focus
            const formInputs = document.querySelectorAll('.signup-form input, .signup-form textarea');
            formInputs.forEach(input => {
                input.addEventListener('focus', function() {
                    if (typeof gtag !== 'undefined') {
                        gtag('event', 'form_field_focus', {
                            'event_category': 'engagement',
                            'event_label': this.name || this.id
                        });
                    }
                }, { once: true });
            });

            // Track time on page
            const startTime = Date.now();
            window.addEventListener('beforeunload', function() {
                const timeOnPage = Math.round((Date.now() - startTime) / 1000);
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'time_on_page', {
                        'event_category': 'engagement',
                        'value': timeOnPage
                    });
                }
            });
        }
    };

    // Performance monitoring
    const performanceMonitor = {
        init: function() {
            if (!window.performance || !window.performance.getEntriesByType) return;

            window.addEventListener('load', () => {
                setTimeout(() => {
                    this.reportMetrics();
                }, 0);
            });
        },

        reportMetrics: function() {
            if (!window.performance || !window.performance.getEntriesByType) return;
            const perfEntries = window.performance.getEntriesByType('navigation');
            if (!perfEntries || perfEntries.length === 0) return;
            const perfData = perfEntries[0];
            if (!perfData) return;

            const metrics = {
                loadTime: Math.round(perfData.loadEventEnd - perfData.fetchStart),
                domReady: Math.round(perfData.domContentLoadedEventEnd - perfData.fetchStart),
                firstByte: Math.round(perfData.responseStart - perfData.requestStart)
            };

            // Log to console in development
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.log('Performance Metrics:', metrics);
            }

            // Send to analytics if available
            if (typeof gtag !== 'undefined') {
                gtag('event', 'page_performance', {
                    'event_category': 'performance',
                    'page_load_time': metrics.loadTime,
                    'dom_ready_time': metrics.domReady,
                    'first_byte_time': metrics.firstByte
                });
            }
        }
    };

    // Accessibility enhancements
    const accessibility = {
        init: function() {
            this.setupKeyboardNav();
            this.setupFocusManagement();
        },

        setupKeyboardNav: function() {
            // Ensure all interactive elements are keyboard accessible
            const interactiveElements = document.querySelectorAll('a, button, input, select, textarea');
            interactiveElements.forEach(el => {
                if (!el.hasAttribute('tabindex') && el.tabIndex < 0) {
                    el.setAttribute('tabindex', '0');
                }
            });
        },

        setupFocusManagement: function() {
            // Add visible focus indicators for keyboard users
            let mouseUser = false;

            document.addEventListener('mousedown', () => {
                mouseUser = true;
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    mouseUser = false;
                }
            });

            document.addEventListener('focusin', (e) => {
                if (!mouseUser) {
                    e.target.classList.add('keyboard-focus');
                }
            });

            document.addEventListener('focusout', (e) => {
                e.target.classList.remove('keyboard-focus');
            });
        }
    };

    // Initialize everything when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        formHandler.init();
        analytics.init();
        performanceMonitor.init();
        accessibility.init();
    }

})();

