function toggleMenu() {
  const navList = document.getElementById('nav-list');
  navList.classList.toggle('show');
}

// Variables globales para calificación y compra
let currentProductId = null;
let selectedRating = 0;
let currentProductPrice = 0;

document.addEventListener("DOMContentLoaded", () => {
  // Referencias a elementos
  const showFormBtn = document.getElementById("showFormBtn");
  const productForm = document.getElementById("productForm");
  const productsContainer = document.getElementById("productsContainer");
  const loginLink = document.getElementById("loginLink");
  const loginModal = document.getElementById("loginModal");
  const loginForm = document.getElementById("loginForm");
  const registerLink = document.getElementById("registerLink");
  const registerModal = document.getElementById("registerModal");
  const registerForm = document.getElementById("registerForm");
  const ratingModal = document.getElementById("ratingModal");
  const ratingForm = document.getElementById("ratingForm");
  const purchaseModal = document.getElementById("purchaseModal");
  const purchaseForm = document.getElementById("purchaseForm");
  const transactionsLink = document.getElementById("transactionsLink");
  const transactionsModal = document.getElementById("transactionsModal");
  const contactLink = document.getElementById("contactLink");
  const contactoFooter = document.getElementById("contacto");

  // Nuevas referencias para el formulario avanzado
  const categorySelect = document.getElementById("categorySelect");
  const newCategoryFields = document.getElementById("newCategoryFields");
  const advancedOptionsBtn = document.getElementById("advancedOptionsBtn");
  const advancedFields = document.getElementById("advancedFields");

  // Mostrar / ocultar formulario de producto
  if (showFormBtn) {
    showFormBtn.addEventListener("click", () => {
      productForm.style.display = productForm.style.display === "none" ? "block" : "none";
    });
  }

  // Manejar selector de categoría
  if (categorySelect) {
    categorySelect.addEventListener("change", () => {
      const selectedValue = categorySelect.value;
      if (selectedValue === "new") {
        newCategoryFields.style.display = "block";
        // Hacer requeridos los campos de nueva categoría
        const newCategoryInputs = newCategoryFields.querySelectorAll("input");
        newCategoryInputs.forEach(input => {
          if (input.name === "new_category_name") {
            input.required = true;
          }
        });
      } else {
        newCategoryFields.style.display = "none";
        // Quitar requerido de los campos de nueva categoría
        const newCategoryInputs = newCategoryFields.querySelectorAll("input");
        newCategoryInputs.forEach(input => {
          input.required = false;
        });
      }
    });
  }

  // Manejar opciones avanzadas
  if (advancedOptionsBtn) {
    advancedOptionsBtn.addEventListener("click", () => {
      const isVisible = advancedFields.style.display === "block";
      advancedFields.style.display = isVisible ? "none" : "block";
      advancedOptionsBtn.textContent = isVisible ? "⚙️ Opciones Avanzadas" : "⬆️ Ocultar Opciones";
      advancedOptionsBtn.style.backgroundColor = isVisible ? "#666" : "#444";
    });
  }

  // Mostrar modal de login
  if (loginLink) {
    loginLink.addEventListener("click", (e) => {
      e.preventDefault();
      loginModal.style.display = "flex";
    });
  }

  // Mostrar modal de registro
  if (registerLink) {
    registerLink.addEventListener("click", (e) => {
      e.preventDefault();
      registerModal.style.display = "flex";
    });
  }

  // Mostrar modal de transacciones
  if (transactionsLink) {
    transactionsLink.addEventListener("click", (e) => {
      e.preventDefault();
      loadTransactions();
      transactionsModal.style.display = "flex";
    });
  }

  // Cerrar modales haciendo clic fuera
  window.addEventListener("click", (e) => {
    if (e.target === loginModal) {
      loginModal.style.display = "none";
    }
    if (e.target === registerModal) {
      registerModal.style.display = "none";
    }
    if (e.target === ratingModal) {
      ratingModal.style.display = "none";
    }
    if (e.target === purchaseModal) {
      purchaseModal.style.display = "none";
    }
    if (e.target === transactionsModal) {
      transactionsModal.style.display = "none";
    }
  });

  // Sistema de calificaciones en productos
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("star-rating")) {
      const productId = e.target.dataset.productId;
      const rating = parseInt(e.target.dataset.rating);
      
      // Mostrar modal de calificación
      currentProductId = productId;
      selectedRating = rating;
      showRatingModal(rating);
    }
  });

  // Enviar formulario de login
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const username = document.getElementById("username").value.trim();
      const password = document.getElementById("password").value;

      if (!username || !password) {
        alert("Por favor completa todos los campos.");
        return;
      }

      try {
        const response = await fetch('/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });

        const data = await response.json();
        
        if (data.success) {
          alert("¡Inicio de sesión exitoso!");
          window.location.reload(); // Recargar para mostrar el estado de sesión
        } else {
          alert("Usuario o contraseña incorrectos.");
        }
      } catch (error) {
        console.error('Error:', error);
        alert("Error al conectar con el servidor.");
      }

      loginModal.style.display = "none";
      loginForm.reset();
    });
  }

  // Enviar formulario de registro
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const username = document.getElementById("regUsername").value.trim();
      const password = document.getElementById("regPassword").value;
      const confirmPassword = document.getElementById("regConfirmPassword").value;

      if (!username || !password || !confirmPassword) {
        alert("Por favor completa todos los campos.");
        return;
      }

      if (password !== confirmPassword) {
        alert("Las contraseñas no coinciden.");
        return;
      }

      if (password.length < 6) {
        alert("La contraseña debe tener al menos 6 caracteres.");
        return;
      }

      try {
        const response = await fetch('/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });

        const data = await response.json();
        
        if (data.success) {
          alert("¡Usuario registrado exitosamente! Ahora puedes iniciar sesión.");
          registerModal.style.display = "none";
          registerForm.reset();
          // Mostrar el modal de login
          loginModal.style.display = "flex";
        } else {
          alert(data.message || "Error al registrar usuario.");
        }
      } catch (error) {
        console.error('Error:', error);
        alert("Error al conectar con el servidor.");
      }
    });
  }

  // Enviar formulario de calificación
  if (ratingForm) {
    ratingForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      if (!currentProductId || selectedRating === 0) {
        alert("Por favor selecciona una calificación.");
        return;
      }

      const comment = document.getElementById("ratingComment").value;

      try {
        const formData = new FormData();
        formData.append('rating', selectedRating);
        formData.append('comment', comment);

        const response = await fetch(`/rate_product/${currentProductId}`, {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        
        if (data.success) {
          alert("¡Calificación enviada correctamente!");
          closeRatingModal();
          // Recargar la página para actualizar las calificaciones
          window.location.reload();
        } else {
          alert(data.message || "Error al enviar calificación.");
        }
      } catch (error) {
        console.error('Error:', error);
        alert("Error al conectar con el servidor.");
      }
    });
  }

  // Enviar formulario de compra
  if (purchaseForm) {
    purchaseForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const productId = document.getElementById("purchaseProductId").value;
      const quantity = document.getElementById("purchaseQuantity").value;
      const cardNumber = document.getElementById("cardNumber").value;
      const cardHolder = document.getElementById("cardHolder").value;
      const expiryMonth = document.getElementById("expiryMonth").value;
      const expiryYear = document.getElementById("expiryYear").value;
      const cvv = document.getElementById("cvv").value;

      // Validaciones básicas
      if (!productId || !quantity || !cardNumber || !cardHolder || !expiryMonth || !expiryYear || !cvv) {
        alert("Por favor completa todos los campos.");
        return;
      }

      if (cardNumber.length < 13 || cardNumber.length > 19) {
        alert("Número de tarjeta inválido.");
        return;
      }

      if (cvv.length < 3 || cvv.length > 4) {
        alert("CVV inválido.");
        return;
      }

      try {
        const formData = new FormData();
        formData.append('product_id', productId);
        formData.append('quantity', quantity);
        formData.append('card_number', cardNumber);
        formData.append('card_holder', cardHolder);
        formData.append('expiry_month', expiryMonth);
        formData.append('expiry_year', expiryYear);
        formData.append('cvv', cvv);

        const response = await fetch('/process_purchase', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        
        if (data.success) {
          alert("¡Compra realizada exitosamente!");
          closePurchaseModal();
          
          // Actualizar el stock del producto en la interfaz
          if (data.transaction && data.transaction.new_stock !== undefined) {
            updateProductStock(productId, data.transaction.new_stock);
          }
          
          // Recargar la página para actualizar los datos
          window.location.reload();
        } else {
          alert(data.message || "Error al procesar la compra.");
        }
      } catch (error) {
        console.error('Error:', error);
        alert("Error al conectar con el servidor.");
      }
    });
  }

  // Actualizar total de compra cuando cambie la cantidad
  const purchaseQuantity = document.getElementById("purchaseQuantity");
  if (purchaseQuantity) {
    purchaseQuantity.addEventListener("input", updatePurchaseTotal);
  }

  // Enviar formulario de producto (ya está configurado para enviar al backend)
  if (productForm) {
    productForm.addEventListener("submit", (e) => {
      // El formulario ya está configurado para enviar al backend
      // No necesitamos prevenir el envío por defecto
      console.log("Enviando producto al servidor...");
    });
  }

  // Manejo del formulario de agregar producto
  const addProductForm = document.getElementById('addProductForm');
  const cancelFormBtn = document.getElementById('cancelFormBtn');
  
  // Mostrar formulario
  if (showFormBtn) {
    showFormBtn.addEventListener('click', function() {
      addProductForm.style.display = 'block';
      showFormBtn.style.display = 'none';
    });
  }
  
  // Ocultar formulario
  if (cancelFormBtn) {
    cancelFormBtn.addEventListener('click', function() {
      addProductForm.style.display = 'none';
      showFormBtn.style.display = 'block';
      addProductForm.reset();
    });
  }
  
  // Manejo del envío del formulario
  if (addProductForm) {
    addProductForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      
      fetch('/add_product', {
        method: 'POST',
        body: formData
      })
      .then(response => {
        if (response.ok) {
          // Recargar la página para mostrar el nuevo producto
          window.location.reload();
        } else {
          handleFormError(response);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        showErrorModal('Error de conexión. Por favor, inténtalo de nuevo.');
      });
    });
  }

  if (contactLink && contactoFooter) {
    contactLink.addEventListener("click", (e) => {
      e.preventDefault();
      contactoFooter.scrollIntoView({ behavior: "smooth" });
    });
  }

  // ================= BÚSQUEDA INSTANTÁNEA =================
  const searchInput = document.getElementById("searchInput");
  const searchForm = document.getElementById("searchForm");
  const mainContent = document.querySelector("main.main");

  let searchTimeout = null;
  if (searchInput && mainContent) {
    searchInput.addEventListener("input", function(e) {
      clearTimeout(searchTimeout);
      const query = searchInput.value.trim();
      searchTimeout = setTimeout(() => {
        fetch(`/buscar?q=${encodeURIComponent(query)}`)
          .then(res => res.text())
          .then(html => {
            mainContent.innerHTML = html;
          });
      }, 250);
    });
    // Evitar submit normal
    if (searchForm) {
      searchForm.addEventListener("submit", function(e) {
        e.preventDefault();
      });
    }
  }
});

// Función para cerrar el modal de login desde la X
function closeLoginModal() {
  document.getElementById("loginModal").style.display = "none";
}

// Función para cerrar el modal de registro desde la X
function closeRegisterModal() {
  document.getElementById("registerModal").style.display = "none";
}

// Función para cerrar el modal de calificación desde la X
function closeRatingModal() {
  document.getElementById("ratingModal").style.display = "none";
}

// Función para cerrar el modal de compra desde la X
function closePurchaseModal() {
  document.getElementById("purchaseModal").style.display = "none";
}

// Función para cerrar el modal de transacciones desde la X
function closeTransactionsModal() {
  document.getElementById("transactionsModal").style.display = "none";
}

// Función para mostrar el modal de calificación
function showRatingModal(rating) {
  const ratingModal = document.getElementById("ratingModal");
  const stars = ratingModal.querySelectorAll(".rating-stars i");
  
  // Limpiar estrellas anteriores
  stars.forEach(star => star.classList.remove("active"));
  
  // Activar estrellas hasta la calificación seleccionada
  for (let i = 0; i < rating; i++) {
    stars[i].classList.add("active");
  }
  
  // Agregar eventos a las estrellas del modal
  stars.forEach((star, index) => {
    star.onclick = () => {
      selectedRating = index + 1;
      stars.forEach((s, i) => {
        s.classList.toggle("active", i < selectedRating);
      });
    };
  });
  
  ratingModal.style.display = "flex";
}

// Función para mostrar el modal de compra
function showPurchaseModal(productId, productName, price, stock) {
  currentProductId = productId;
  currentProductPrice = price;
  
  document.getElementById("purchaseProductName").textContent = productName;
  document.getElementById("purchasePrice").textContent = price;
  document.getElementById("purchaseProductId").value = productId;
  document.getElementById("purchaseQuantity").max = stock;
  document.getElementById("purchaseQuantity").value = 1;
  
  updatePurchaseTotal();
  
  purchaseModal.style.display = "flex";
}

// Función para actualizar el total de la compra
function updatePurchaseTotal() {
  const quantity = parseInt(document.getElementById("purchaseQuantity").value) || 1;
  const total = quantity * currentProductPrice;
  document.getElementById("purchaseTotal").textContent = total.toFixed(2);
}

// Función para actualizar el stock en la página
function updateProductStock(productId, newStock) {
  const productCard = document.querySelector(`[data-product-id="${productId}"]`);
  if (productCard) {
    const quantityElement = productCard.querySelector('.quantity');
    if (quantityElement) {
      quantityElement.textContent = `Stock: ${newStock} unidades`;
    }
  }
}

// Función para cargar transacciones
async function loadTransactions() {
  try {
    const response = await fetch('/transactions');
    const data = await response.json();
    
    if (data.success) {
      const transactionsList = document.getElementById("transactionsList");
      
      if (data.transactions.length === 0) {
        transactionsList.innerHTML = '<p style="text-align: center; color: #666;">No tienes compras registradas.</p>';
        return;
      }
      
      transactionsList.innerHTML = data.transactions.map(transaction => `
        <div class="transaction-item">
          <h4>${transaction.product_name}</h4>
          <div class="transaction-details">
            <div>
              <strong>Cantidad:</strong> ${transaction.quantity}<br>
              <strong>Precio unitario:</strong> $${transaction.product_price}<br>
              <strong>Tarjeta:</strong> ****${transaction.card_last_four}
            </div>
            <div>
              <div class="transaction-amount">Total: $${transaction.total_amount}</div>
              <div class="transaction-date">${transaction.transaction_date}</div>
            </div>
          </div>
        </div>
      `).join('');
    } else {
      alert(data.message || "Error al cargar transacciones.");
    }
  } catch (error) {
    console.error('Error:', error);
    alert("Error al conectar con el servidor.");
  }
}

// Eliminar producto (solo para admin)
async function deleteProduct(productId) {
  if (!confirm("¿Estás seguro de que quieres eliminar este producto?")) {
    return;
  }

  try {
    const response = await fetch(`/delete_product/${productId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    const data = await response.json();
    
    if (data.success) {
      alert("Producto eliminado correctamente");
      // Eliminar el elemento del DOM
      const productCard = document.querySelector(`[data-product-id="${productId}"]`);
      if (productCard) {
        productCard.remove();
      }
    } else {
      alert(data.message || "Error al eliminar el producto");
    }
  } catch (error) {
    console.error('Error:', error);
    alert("Error al conectar con el servidor.");
  }
}

// Función para mostrar modal de error
function showErrorModal(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorModal').style.display = 'block';
}

// Función para cerrar modal de error
function closeErrorModal() {
    document.getElementById('errorModal').style.display = 'none';
}

// Función para manejar errores de formularios
function handleFormError(response) {
    if (response.status === 400) {
        response.text().then(text => {
            showErrorModal(text);
        });
    } else {
        showErrorModal('Error inesperado del servidor. Por favor, inténtalo de nuevo.');
    }
}

// Función para editar producto
async function editProduct(productId) {
    try {
        const response = await fetch(`/get_product/${productId}`);
        const data = await response.json();
        
        if (data.success) {
            const product = data.product;
            
            // Llenar el formulario con los datos del producto
            document.getElementById('editProductId').value = product.id;
            document.getElementById('editProductName').value = product.name;
            document.getElementById('editProductFeatures').value = product.features;
            document.getElementById('editProductPrice').value = product.price;
            document.getElementById('editProductQuantity').value = product.quantity;
            
            // Seleccionar la categoría correcta
            const categorySelect = document.getElementById('editCategorySelect');
            categorySelect.value = product.category_id;
            
            // Campos avanzados
            document.getElementById('editProductSku').value = product.sku || '';
            document.getElementById('editProductBrand').value = product.brand || '';
            document.getElementById('editProductWeight').value = product.weight || '';
            document.getElementById('editProductDimensions').value = product.dimensions || '';
            document.getElementById('editProductWarranty').value = product.warranty_months || 12;
            document.getElementById('editProductFeatured').checked = product.is_featured == 1;
            document.getElementById('editProductActive').checked = product.is_active == 1;
            
            // Mostrar el modal
            document.getElementById('editProductModal').style.display = 'flex';
            
        } else {
            alert(data.message || "Error al cargar el producto");
        }
    } catch (error) {
        console.error('Error:', error);
        alert("Error al conectar con el servidor.");
    }
}

// Función para cerrar el modal de edición
function closeEditProductModal() {
    document.getElementById('editProductModal').style.display = 'none';
    document.getElementById('editProductForm').reset();
}

// Agregar eventos para el modal de edición
document.addEventListener("DOMContentLoaded", () => {
    // Referencias para el modal de edición
    const editProductModal = document.getElementById('editProductModal');
    const editProductForm = document.getElementById('editProductForm');
    const editCategorySelect = document.getElementById('editCategorySelect');
    const editNewCategoryFields = document.getElementById('editNewCategoryFields');
    const editAdvancedOptionsBtn = document.getElementById('editAdvancedOptionsBtn');
    const editAdvancedFields = document.getElementById('editAdvancedFields');
    
    // Cerrar modal de edición haciendo clic fuera
    if (editProductModal) {
        window.addEventListener("click", (e) => {
            if (e.target === editProductModal) {
                editProductModal.style.display = "none";
            }
        });
    }
    
    // Manejar selector de categoría en edición
    if (editCategorySelect) {
        editCategorySelect.addEventListener("change", () => {
            const selectedValue = editCategorySelect.value;
            if (selectedValue === "new") {
                editNewCategoryFields.style.display = "block";
                // Hacer requeridos los campos de nueva categoría
                const newCategoryInputs = editNewCategoryFields.querySelectorAll("input");
                newCategoryInputs.forEach(input => {
                    if (input.name === "new_category_name") {
                        input.required = true;
                    }
                });
            } else {
                editNewCategoryFields.style.display = "none";
                // Quitar requerido de los campos de nueva categoría
                const newCategoryInputs = editNewCategoryFields.querySelectorAll("input");
                newCategoryInputs.forEach(input => {
                    input.required = false;
                });
            }
        });
    }
    
    // Manejar opciones avanzadas en edición
    if (editAdvancedOptionsBtn) {
        editAdvancedOptionsBtn.addEventListener("click", () => {
            const isVisible = editAdvancedFields.style.display === "block";
            editAdvancedFields.style.display = isVisible ? "none" : "block";
            editAdvancedOptionsBtn.textContent = isVisible ? "⚙️ Opciones Avanzadas" : "⬆️ Ocultar Opciones";
            editAdvancedOptionsBtn.style.backgroundColor = isVisible ? "#666" : "#444";
        });
    }
    
    // Manejar envío del formulario de edición
    if (editProductForm) {
        editProductForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const productId = document.getElementById('editProductId').value;
            const formData = new FormData(editProductForm);
            
            try {
                const response = await fetch(`/edit_product/${productId}`, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    closeEditProductModal();
                    // Recargar la página para mostrar los cambios
                    window.location.reload();
                } else {
                    alert(data.message || "Error al actualizar el producto");
                }
            } catch (error) {
                console.error('Error:', error);
                alert("Error al conectar con el servidor.");
            }
        });
    }
});