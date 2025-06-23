document.addEventListener("DOMContentLoaded", function () {
    const overlay = document.getElementById("loading-overlay");
    const button = document.getElementById("submit-btn");

    if (typeof initPoint !== "undefined" && initPoint) {
        overlay.classList.remove("hidden");
        if (button) button.disabled = true;

        setTimeout(() => {
            window.location.href = initPoint;
        }, 1500);
    }
});
