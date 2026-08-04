document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("contact-form");
    if (!form) {
        return;
    }

    const emailField = document.getElementById("id_email");
    const phoneField = document.getElementById("id_phone");

    const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const PHONE_ALLOWED_CHARS = /^[0-9+\-\s()]+$/;
    const PHONE_MIN_DIGITS = 7;
    const PHONE_MAX_DIGITS = 15;

    function showError(field, message) {
        const errorEl = form.querySelector('[data-error-for="' + field.name + '"]');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.remove("hidden");
        }
        field.classList.add("border-red-500");
    }

    function clearError(field) {
        const errorEl = form.querySelector('[data-error-for="' + field.name + '"]');
        if (errorEl) {
            errorEl.textContent = "";
            errorEl.classList.add("hidden");
        }
        field.classList.remove("border-red-500");
    }

    function validateEmail() {
        if (!EMAIL_PATTERN.test(emailField.value.trim())) {
            showError(emailField, "Enter a valid email address (e.g. name@example.com).");
            return false;
        }
        clearError(emailField);
        return true;
    }

    function validatePhone() {
        const value = phoneField.value.trim();
        const digitCount = value.replace(/\D/g, "").length;
        const hasOnlyAllowedChars = PHONE_ALLOWED_CHARS.test(value);
        const hasValidLength = digitCount >= PHONE_MIN_DIGITS && digitCount <= PHONE_MAX_DIGITS;

        if (!hasOnlyAllowedChars || !hasValidLength) {
            showError(
                phoneField,
                "Enter a valid phone number (" + PHONE_MIN_DIGITS + "-" + PHONE_MAX_DIGITS +
                " digits; spaces, +, - and () are allowed)."
            );
            return false;
        }
        clearError(phoneField);
        return true;
    }

    emailField.addEventListener("blur", validateEmail);
    phoneField.addEventListener("blur", validatePhone);

    form.addEventListener("submit", function (event) {
        const isEmailValid = validateEmail();
        const isPhoneValid = validatePhone();

        if (!isEmailValid || !isPhoneValid) {
            event.preventDefault();
        }
    });
});