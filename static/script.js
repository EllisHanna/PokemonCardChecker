const modal = document.getElementById("add-card-modal");
const plusButton = document.querySelector(".plus-button");
const closeButton = document.querySelector(".close-button");
const cardsGrid = document.getElementById("my-cards-grid");
const binButton = document.querySelector(".bin-button");

plusButton.addEventListener("click", () => {
  modal.style.display = "flex";
});

closeButton.addEventListener("click", () => {
  modal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target === modal) modal.style.display = "none";
});
