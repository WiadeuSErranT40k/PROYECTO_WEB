function toggleMenu() {
  const navList = document.getElementById('nav-list');
  navList.classList.toggle('show');
}

const isAdmin = true;

document.addEventListener("DOMContentLoaded", () => {
  // Referencias a elementos
  const showFormBtn = document.getElementById("showFormBtn");
  const productForm = document.getElementById("productForm");
  const productsContainer = document.getElementById("productsContainer");
  const loginLink = document.getElementById("loginLink");
  const loginModal = document.getElementById("loginModal");
  const loginForm = document.getElementById("loginForm");

  // Ocultar opciones de admin si no es admin
  if (!isAdmin) {
    showFormBtn.style.display = "none";
    productForm.style.display = "none";
  }

  // Mostrar / ocultar formulario de producto
  showFormBtn.addEventListener("click", () => {
    productForm.style.display = productForm.style.display === "none" ? "block" : "none";
  });

  // Enviar formulario de producto
  productForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const name = document.getElementById("productName").value.trim();
    const category = document.getElementById("productCategory").value.trim();
    const features = document.getElementById("productFeatures").value.trim();
    const price = document.getElementById("productPrice").value.trim();
    const imageFile = document.getElementById("productImageFile").files[0];

    if (!imageFile) {
      alert("Por favor, selecciona una imagen.");
      return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
      const imageUrl = e.target.result;

      const newCard = document.createElement("div");
      newCard.className = "product-card";

      newCard.innerHTML = `
        <div class="image" style="background-image: url('${imageUrl}');"></div>
        <div class="details">
          <div class="title">${name}</div>
          <div class="subtitle">Categoría: ${category} | ${features} | $${price}</div>
        </div>
        <button class="delete-btn" onclick="deleteProduct(this)">🗑 Eliminar</button>
      `;

      productsContainer.appendChild(newCard);

      productForm.reset();
      productForm.style.display = "none";
    };

    reader.readAsDataURL(imageFile);
  });

  // Mostrar modal de login
  loginLink.addEventListener("click", (e) => {
    e.preventDefault();
    loginModal.style.display = "flex";
  });

  // Cerrar modal haciendo clic fuera
  window.addEventListener("click", (e) => {
    if (e.target === loginModal) {
      loginModal.style.display = "none";
    }
  });

  // Enviar formulario de login
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
      alert("Por favor completa todos los campos.");
      return;
    }

    // Aquí podrías hacer un fetch() a tu backend para autenticar
    alert(`¡Bienvenido, ${username}!`);

    loginModal.style.display = "none";
    loginForm.reset();
  });
});

// Función para cerrar el modal desde la X
function closeLoginModal() {
  document.getElementById("loginModal").style.display = "none";
}

// Eliminar producto
function deleteProduct(button) {
  const card = button.closest(".product-card");
  card.remove();
}
