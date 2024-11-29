document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modal-oferta");
    const modalForm = document.getElementById("modal-form");
    const closeModal = document.querySelector(".close");
    const offerButtons = document.querySelectorAll(".oferta-form button");

    offerButtons.forEach(button => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            const comicId = button.closest(".comic").dataset.comicId;
            modalForm.action = `/hacer_oferta/${comicId}/`; 
            modal.style.display = "block";
        });
    });

    closeModal.addEventListener("click", () => {
        modal.style.display = "none";
    });

    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});