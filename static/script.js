const modal = document.getElementById("add-card-modal");
const plusButton = document.querySelector(".plus-button");
const closeButton = document.querySelector(".close-button");
const cardsGrid = document.getElementById("my-cards-grid");
const binButton = document.querySelector(".bin-button");
const cameraModal = document.getElementById("camera-modal");
const cameraButton = document.querySelector(".camera-button");
const closeButtons = document.querySelectorAll(".close-button");

plusButton.addEventListener("click", () => {
  modal.style.display = "flex";
});

closeButton.addEventListener("click", () => {
  modal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target === modal) modal.style.display = "none";
});

cameraButton.addEventListener("click", () => {
  cameraModal.style.display = "flex";
});

closeButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    btn.closest(".modal").style.display = "none";
  });
});

window.addEventListener("click", (e) => {
  if (e.target === cameraModal) cameraModal.style.display = "none";
});