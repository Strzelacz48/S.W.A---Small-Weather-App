document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("delete-modal");
    if (!modal) {
        return;
    }

    const nameEl = document.getElementById("delete-modal-name");
    const form = document.getElementById("delete-modal-form");
    const cancelButton = document.getElementById("delete-modal-cancel");

    function openModal(deleteUrl, contactName) {
        nameEl.textContent = contactName;
        form.action = deleteUrl;
        modal.classList.remove("hidden");
    }

    function closeModal() {
        modal.classList.add("hidden");
    }

    document.querySelectorAll(".delete-trigger").forEach(function (button) {
        button.addEventListener("click", function () {
            openModal(button.dataset.deleteUrl, button.dataset.contactName);
        });
    });

    cancelButton.addEventListener("click", closeModal);

    // Clicking the dark overlay outside the dialog also cancels.
    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !modal.classList.contains("hidden")) {
            closeModal();
        }
    });
});