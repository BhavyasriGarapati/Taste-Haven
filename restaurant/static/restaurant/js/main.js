/**
 * Taste Haven - Client-Side Interactions & UI Logic
 * Handles navigation bar animations, mobile responsiveness, and booking validations.
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Navigation Sticky Animation
    const header = document.querySelector('.main-header');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // 2. Mobile Responsive Menu
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Close menu when clicking any link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }

    // 3. Date Validation for Reservations
    const dateInput = document.getElementById('id_date');
    if (dateInput) {
        // Restrict date input to today and future dates
        const today = new Date();
        const yyyy = today.getFullYear();
        let mm = today.getMonth() + 1; // Months start at 0
        let dd = today.getDate();

        if (mm < 10) mm = '0' + mm;
        if (dd < 10) dd = '0' + dd;

        const formattedToday = `${yyyy}-${mm}-${dd}`;
        dateInput.setAttribute('min', formattedToday);
        
        // Default to today if empty
        if (!dateInput.value) {
            dateInput.value = formattedToday;
        }

        // Live validation on date change
        dateInput.addEventListener('change', () => {
            const selectedDate = new Date(dateInput.value);
            const currentDate = new Date(formattedToday);
            
            // Set hours to 0 to compare dates only
            selectedDate.setHours(0,0,0,0);
            currentDate.setHours(0,0,0,0);

            if (selectedDate < currentDate) {
                alert("Please select a date in the future. We cannot accept bookings for past dates.");
                dateInput.value = formattedToday;
            }
        });
    }

    // 4. Form Submission Agreement Validation
    const bookingForm = document.querySelector('.main-booking-form');
    const agreementCheckbox = document.getElementById('policy-agree');

    if (bookingForm && agreementCheckbox) {
        bookingForm.addEventListener('submit', (e) => {
            if (!agreementCheckbox.checked) {
                e.preventDefault();
                alert("You must agree to the Reservation Policy to book a table.");
            }
        });
    }

    // 5. Message Banner Automatic Fadeout
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.6s ease";
            alert.style.opacity = "0";
            setTimeout(() => {
                alert.style.display = "none";
            }, 600);
        }, 5000); // Fades out after 5 seconds
    });
});
