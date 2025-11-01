const addCardModal = document.getElementById("add-card-modal");
const cameraModal = document.getElementById("camera-modal");
const addWishlistModal = document.getElementById("add-wishlist-modal");
const plusButton = document.querySelector(".plus-button");
const cameraButton = document.querySelector(".camera-button");
const binButton = document.querySelector(".bin-button");
const closeButtons = document.querySelectorAll(".close-button");
const addWishlistOpen = document.getElementById("add-wishlist-open");

plusButton.addEventListener("click", () => {
  addCardModal.style.display = "flex";
});

cameraButton.addEventListener("click", () => {
  cameraModal.style.display = "flex";
});

if (addWishlistOpen) {
  addWishlistOpen.addEventListener("click", () => {
    addWishlistModal.style.display = "flex";
  });
}

closeButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    btn.closest(".modal").style.display = "none";
  });
});

window.addEventListener("click", (e) => {
  if (e.target === addCardModal) addCardModal.style.display = "none";
  if (e.target === cameraModal) cameraModal.style.display = "none";
  if (e.target === addWishlistModal) addWishlistModal.style.display = "none";
});
