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

let deleteMode = false;

binButton.addEventListener("click", () => {
  deleteMode = !deleteMode;
  document.body.classList.toggle("delete-mode", deleteMode);
});

function parsePrice(text) {
  return parseFloat(text.replace(/[^\d.]/g, "")) || 0;
}

document.querySelectorAll(".card").forEach((card) => {
  card.addEventListener("click", async () => {
    if (!deleteMode) return;

    const cardId = card.dataset.id;
    const type = card.dataset.type;

    const myPrice = parsePrice(card.querySelector(".my-price")?.textContent);

    const res = await fetch(`/delete_card/${type}/${cardId}`, {
      method: "DELETE",
    });

    if (res.ok) {
      card.remove();
      const totalEl = document.getElementById("my-total");
      if (totalEl)
        totalEl.textContent = `£${(
          parsePrice(totalEl.textContent) - myPrice
        ).toFixed(2)}`;
    }
  });
});
