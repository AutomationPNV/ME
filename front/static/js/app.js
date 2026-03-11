// Стан додатку
let motors = [];
let motorToDelete = null;

// API URL
const API_URL = "http://localhost:8000/api";
// Ініціалізація при завантаженні
document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  loadMotors();
  initForm();
  initDeleteConfirmation();
});

// Навігація
function initNavigation() {
  const navBtns = document.querySelectorAll(".nav-btn");
  const views = document.querySelectorAll(".view");

  navBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const viewName = btn.dataset.view;

      // Оновлюємо активну кнопку
      navBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      // Показуємо відповідне представлення
      views.forEach((view) => {
        view.classList.remove("active");
        if (view.id === `${viewName}-view`) {
          view.classList.add("active");
        }
      });

      // Якщо перейшли на дашборд, оновлюємо список
      if (viewName === "dashboard") {
        loadMotors();
      }
    });
  });
}

async function loadMotors() {
  console.log("📡 Завантаження моторів...");
  console.log("🔗 API_URL:", API_URL);

  try {
    // Виконуємо запит до API
    const response = await fetch(`${API_URL}/motors`);
    console.log("📊 Статус відповіді:", response.status);

    // Перевіряємо чи запит успішний
    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ Текст помилки:", errorText);
      throw new Error(`HTTP помилка! статус: ${response.status}`);
    }

    // Парсимо JSON відповідь
    const data = await response.json();
    console.log("📦 Отримані дані з API:", data);

    // ЗБЕРІГАЄМО ДАНІ В ГЛОБАЛЬНУ ЗМІННУ
    window.motors = data; // зберігаємо в глобальний об'єкт window
    motors = data; // зберігаємо в локальну глобальну змінну

    console.log("✅ motors збережено:", motors);
    console.log("✅ window.motors:", window.motors);
    console.log("📊 Кількість моторів:", motors.length);

    if (motors.length > 0) {
      console.log("📋 Перший мотор:", motors[0]);
    }

    // Оновлюємо статистику на сторінці
    updateDashboard();
    console.log("📊 Статистика оновлена");

    // Відображаємо мотори
    renderMotors();
    console.log("🎨 Відображення оновлене");
  } catch (error) {
    console.error("❌ ПОМИЛКА завантаження:");
    console.error("   Назва:", error.name);
    console.error("   Повідомлення:", error.message);
    console.error("   Стек:", error.stack);

    // Показуємо помилку на сторінці
    const grid = document.getElementById("motorsGrid");
    if (grid) {
      grid.innerHTML = `
                <div style="
                    text-align: center; 
                    padding: 3rem; 
                    background: #ffebee; 
                    border-radius: 12px; 
                    grid-column: 1/-1;
                    border: 2px solid #f44336;
                ">
                    <i class="fas fa-exclamation-triangle" style="font-size: 4rem; color: #f44336;"></i>
                    <h3 style="color: #f44336; margin: 1rem 0;">Помилка завантаження</h3>
                    <p style="color: #666; margin-bottom: 0.5rem;">${error.message}</p>
                    <p style="color: #999; font-size: 0.9rem; margin-bottom: 1rem;">API_URL: ${API_URL}</p>
                    <button onclick="loadMotors()" style="
                        background: #f44336;
                        color: white;
                        border: none;
                        padding: 0.5rem 2rem;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 1rem;
                        transition: all 0.3s;
                    ">🔄 Спробувати знову</button>
                </div>
            `;
    }

    showToast("Помилка: " + error.message, "error");
  }
}
// Оновлення статистики на дашборді
function updateDashboard() {
  console.log("📊 Оновлення статистики...");

  // Оновлюємо тільки якщо ми на сторінці dashboard
  if (!document.getElementById("dashboard-view").classList.contains("active")) {
    console.log(
      "   ⏭️ Не на сторінці dashboard, пропускаємо оновлення статистики",
    );
    return;
  }

  const totalMotorsEl = document.getElementById("totalMotors");
  const activeMotorsEl = document.getElementById("activeMotors");
  const warningMotorsEl = document.getElementById("warningMotors");

  if (totalMotorsEl) totalMotorsEl.textContent = motors.length || 0;
  if (activeMotorsEl) activeMotorsEl.textContent = motors.length || 0;
  if (warningMotorsEl) warningMotorsEl.textContent = 0;

  console.log("📊 Статистика оновлена");
}

// Відображення карток моторів
function renderMotors() {
  const grid = document.getElementById("motorsGrid");

  if (motors.length === 0) {
    grid.style.display = "flex";
    grid.style.justifyContent = "center";
    grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-motorcycle"></i>
                <h3>Немає доданих двигунів</h3>
                <p>Додайте перший двигун у вкладці "Додати двигун"</p>
            </div>
        `;
    return;
  }

  grid.innerHTML = motors
    .map(
      (motor) => `
        <div class="motor-card" data-id="${motor.id}">
            <div class="motor-card-header">
                <h3>
                    <i class="fas fa-bolt"></i>
                    Двигун ${motor.name_motors || "Невідомо"}
                </h3>
            </div>
            <div class="motor-card-body">
                <div class="motor-info">
                    
                    <div class="info-row">
                        <i class="fas fa-network-wired"></i>
                        <span>Tesys: ${motor.ip_tesys || "—"}</span>
                    </div>
                    <div class="info-row">
                        <i class="fas fa-microchip"></i>
                        <span>PLC: ${motor.ip_plc || "—"}</span>
                    </div>
                    <div class="info-row">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${motor.location || "Не вказано"}</span>
                    </div>
                </div>
            </div>
            <div class="motor-card-footer">
                <button class="btn-details" onclick="showMotorDetails(${motor.id})">
                    <i class="fas fa-info-circle"></i>
                    Деталі
                </button>
                <button class="btn-details" onclick="showMotorDetails(${motor.id})">
                    <i class="fas fa-info-circle"></i>
                    Опір ізоляції
                </button>
                <button class="btn-details" onclick="showMotorDetails(${motor.id})">
                    <i class="fas fa-info-circle"></i>
                    Графіки
                </button>
                <button class="btn-delete" onclick="showDeleteModal(${motor.id}, '${motor.name_motors}')">
                    <i class="fas "></i>
                    Видалити
                </button>
                
                
            </div>
        </div>
    `,
    )
    .join("");
}

// Ініціалізація форми додавання
function initForm() {
  const form = document.getElementById("addMotorForm");
  const messageDiv = document.getElementById("formMessage");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append(
      "motor_name_text",
      document.getElementById("motorName").value,
    );
    formData.append("ip_tesys_text", document.getElementById("ipTesys").value);
    formData.append("ip_plc_text", document.getElementById("ipPlc").value);
    formData.append(
      "motor_location_text",
      document.getElementById("motorLocation").value,
    );

    try {
      const response = await fetch(`${API_URL}/add_motor`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Помилка додавання");

      const result = await response.json();

      // Показуємо успішне повідомлення
      messageDiv.innerHTML = `
                <div class="success-message">
                    <i class="fas fa-check-circle"></i>
                    ${result.message}
                </div>
            `;

      // Очищаємо форму
      form.reset();

      // Завантажуємо оновлений список моторів
      await loadMotors();

      // Через 3 секунди ховаємо повідомлення
      setTimeout(() => {
        messageDiv.innerHTML = "";
      }, 3000);

      // Показуємо toast
      showToast("Мотор успішно додано!", "success");
    } catch (error) {
      messageDiv.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    Помилка при додаванні мотора
                </div>
            `;
      showToast("Помилка при додаванні мотора", "error");
    }
  });

  // Стилі для повідомлень
  const style = document.createElement("style");
  style.textContent = `
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .empty-state {
            text-align: center;
            padding: 4rem;
            background: white;
            border-radius: 12px;
            box-shadow: var(--shadow-sm);
        }
        .empty-state i {
            font-size: 4rem;
            color: var(--gray-400);
            margin-bottom: 1rem;
        }
        .empty-state h3 {
            color: var(--gray-700);
            margin-bottom: 0.5rem;
        }
        .empty-state p {
            color: var(--gray-500);
        }
    `;
  document.head.appendChild(style);
}

// Ініціалізація модального вікна для видалення
function initDeleteConfirmation() {
  const modal = document.getElementById("deleteModal");
  const confirmBtn = document.getElementById("confirmDelete");

  if (!modal || !confirmBtn) {
    console.error("❌ Модальне вікно або кнопка не знайдені");
    return;
  }

  confirmBtn.addEventListener("click", async () => {
    if (!motorToDelete) {
      console.warn("⚠️ motorToDelete не визначений");
      return;
    }

    console.log("🗑️ Видалення мотора:", motorToDelete);

    try {
      const url = `${API_URL}/delete_motor/${motorToDelete.id}`;
      console.log("📡 DELETE запит на:", url);

      const response = await fetch(url, {
        method: "DELETE",
        headers: {
          Accept: "application/json",
        },
      });

      console.log("📊 Статус відповіді:", response.status);
      console.log("📊 Заголовки:", [...response.headers.entries()]);

      // Отримуємо текст відповіді для аналізу
      const responseText = await response.text();
      console.log("📦 Текст відповіді:", responseText);

      // Якщо статус не 2xx, кидаємо помилку
      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}: ${responseText || "Невідома помилка"}`,
        );
      }

      // Якщо відповідь не порожня, пробуємо розпарсити JSON
      let responseData = null;
      if (responseText && responseText.trim()) {
        try {
          responseData = JSON.parse(responseText);
          console.log("✅ JSON відповідь:", responseData);
        } catch (e) {
          console.log("⚠️ Відповідь не є JSON, але це не помилка");
        }
      }

      // Закриваємо модальне вікно
      closeModal();

      // Перезавантажуємо список моторів
      await loadMotors();

      // Показуємо успішне повідомлення
      const successMessage =
        responseData?.message || `Мотор "${motorToDelete.name}" видалено`;
      showToast(successMessage, "success");
      console.log("✅ Мотор успішно видалено");
    } catch (error) {
      console.error("❌ ПОМИЛКА при видаленні:");
      console.error("   Назва:", error.name);
      console.error("   Повідомлення:", error.message);

      // Показуємо помилку користувачу
      showToast(`Помилка: ${error.message}`, "error");

      // Закриваємо модальне вікно тільки після помилки
      closeModal();
    }
  });

  // Додаємо закриття по кліку поза модальним вікном
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });

  console.log("✅ initDeleteConfirmation завершено");
}

// Показати модальне вікно видалення
function showDeleteModal(id, name) {
  motorToDelete = { id, name };
  document.getElementById("deleteMotorName").textContent = name || "невідомий";
  document.getElementById("deleteModal").classList.add("active");
}

// Закрити модальне вікно
function closeModal() {
  document.getElementById("deleteModal").classList.remove("active");
  motorToDelete = null;
}

// Показати деталі мотора
function showMotorDetails(id) {
  const motor = motors.find((m) => m.id === id);
  if (!motor) return;

  // Тут можна відкрити модальне вікно з деталями
  showToast(`Деталі мотора #${id} в розробці`, "info");
}

// Показати toast повідомлення
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast show ${type}`;

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// Функція для видалення (сумісність зі старим кодом)
async function DeleteMotor(id) {
  showDeleteModal(id, "");
}
