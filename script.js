// Configuration de l'API
const API_URL = "http://localhost:5000/api";

// État du jeu
let gameState = null;
let updateInterval = null;

// ============================================================================
// INITIALISATION
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  console.log("Initialisation du jeu...");

  // Charger l'état initial
  loadGameState();

  // Mise à jour périodique depuis le serveur (toutes les 500ms)
  updateInterval = setInterval(loadGameState, 500);

  // Event listeners
  document.getElementById("saveBtn").addEventListener("click", saveGame);
  document.getElementById("loadBtn").addEventListener("click", loadGame);
});

// ============================================================================
// API CALLS
// ============================================================================

async function loadGameState() {
  try {
    const response = await fetch(`${API_URL}/game`);
    const data = await response.json();
    gameState = data;
    updateUI();
  } catch (error) {
    console.error("Erreur chargement état:", error);
  }
}

async function clickCible(cibleId) {
  try {
    const response = await fetch(`${API_URL}/clic/${cibleId}`, {
      method: "POST",
    });
    const data = await response.json();

    if (data.success) {
      // Animation visuelle
      animateCibleClick(cibleId);

      // Mise à jour optimiste (on attend pas le serveur)
      if (gameState && gameState.cibles[cibleId]) {
        gameState.points = data.points_total;
        gameState.total_clics += 1;
        gameState.cibles[cibleId].total_clics += 1;
        gameState.cibles[cibleId].points_gagnes += data.points_gagnes;
        updateScoreOnly();
        updateCibleCard(cibleId);
      }
    }
  } catch (error) {
    console.error("Erreur clic:", error);
  }
}

async function selectCible(cibleId) {
  try {
    const response = await fetch(`${API_URL}/select/${cibleId}`, {
      method: "POST",
    });
    const data = await response.json();

    if (data.success) {
      const oldSelected = gameState.cible_selectionnee;
      gameState.cible_selectionnee = cibleId;
      gameState.ameliorations = data.ameliorations;

      // Mettre à jour l'UI
      updateSelectedCibleInfo();
      updateAllSelectButtons();

      // Reconstruire les améliorations seulement si on change de cible
      if (oldSelected !== cibleId) {
        const container = document.getElementById("ameliorationsContainer");
        container.innerHTML = "";
        gameState.ameliorations.forEach((amelio) => {
          container.appendChild(createAmeliorationCard(amelio));
        });
      }
    }
  } catch (error) {
    console.error("Erreur sélection:", error);
  }
}

async function buyAmelioration(type, cibleId = null) {
  try {
    const response = await fetch(`${API_URL}/amelioration/acheter`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type, cible_id: cibleId }),
    });
    const data = await response.json();

    if (data.success) {
      showToast("Amélioration achetée !", "success");

      // Remplacer complètement l'état par celui du serveur
      gameState = data.game_state;

      // Mise à jour complète de l'UI
      updateUI();

      // Animation du bouton
      const btn = document.querySelector(`[data-type="${type}"]`);
      if (btn) {
        btn.classList.add("success");
        setTimeout(() => btn.classList.remove("success"), 400);
      }
    } else {
      showToast("Pas assez de points !", "error");

      const btn = document.querySelector(`[data-type="${type}"]`);
      if (btn) {
        btn.classList.add("error");
        setTimeout(() => btn.classList.remove("error"), 400);
      }
    }
  } catch (error) {
    console.error("Erreur achat:", error);
    showToast("Erreur lors de l'achat", "error");
  }
}

async function saveGame() {
  try {
    const response = await fetch(`${API_URL}/save`, { method: "POST" });
    const data = await response.json();

    if (data.success) {
      showToast("Partie sauvegardée !", "success");
    }
  } catch (error) {
    console.error("Erreur sauvegarde:", error);
    showToast("Erreur sauvegarde", "error");
  }
}

async function loadGame() {
  try {
    const response = await fetch(`${API_URL}/load`, { method: "POST" });
    const data = await response.json();

    if (data.success) {
      showToast("Partie chargée !", "success");
      gameState = data.game_state;
      updateUI();
    } else {
      showToast("Aucune sauvegarde", "error");
    }
  } catch (error) {
    console.error("Erreur chargement:", error);
    showToast("Erreur chargement", "error");
  }
}

// ============================================================================
// UI UPDATE
// ============================================================================

function updateUI() {
  if (!gameState) return;

  updateScoreOnly();
  updateCibles();
  updateSelectedCibleInfo();
  updateAmeliorations();
}

function updateScoreOnly() {
  if (!gameState) return;

  document.getElementById("points").textContent = formatNumber(
    gameState.points,
  );
  document.getElementById("totalClics").textContent =
    `${formatNumber(gameState.total_clics)} clics`;
  document.getElementById("autoClicDelay").textContent =
    `${gameState.delai_auto_clic.toFixed(1)}s auto`;
  document.getElementById("totalCibles").textContent =
    `${Object.keys(gameState.cibles).length} cible${Object.keys(gameState.cibles).length > 1 ? "s" : ""}`;
}

function updateSelectedCibleInfo() {
  if (!gameState || !gameState.cible_selectionnee) return;

  const cible = gameState.cibles[gameState.cible_selectionnee];
  if (cible) {
    const elem = document.getElementById("selectedCible");
    elem.textContent = `Améliorations pour CIBLE ${cible.numero}`;
    elem.style.color = cible.couleur;
  }
}

function updateCibles() {
  const container = document.getElementById("ciblesContainer");
  const existingIds = new Set(
    Array.from(container.children).map((c) => parseInt(c.dataset.cibleId)),
  );
  const currentIds = new Set(Object.keys(gameState.cibles).map(Number));

  // Ajouter nouvelles cibles
  for (const id of currentIds) {
    if (!existingIds.has(id)) {
      container.appendChild(createCibleCard(gameState.cibles[id]));
    } else {
      updateCibleCard(id);
    }
  }

  // Supprimer cibles obsolètes
  for (const id of existingIds) {
    if (!currentIds.has(id)) {
      const card = container.querySelector(`[data-cible-id="${id}"]`);
      if (card) card.remove();
    }
  }
}

function createCibleCard(cible) {
  const card = document.createElement("div");
  card.className = "cible-card";
  card.dataset.cibleId = cible.numero;
  card.style.setProperty("--cible-color", cible.couleur);

  card.innerHTML = `
    <div class="cible-title">CIBLE ${cible.numero}</div>
    <div class="cible-stats">
      <div class="cible-stat-line">
        <span>Points/clic:</span>
        <span class="stat-value-ppc">${formatNumber(cible.points_par_clic)}</span>
      </div>
      <div class="cible-stat-line">
        <span>Auto:</span>
        <span class="stat-value-auto">${cible.auto_clics_par_tick}</span>
      </div>
      <div class="cible-stat-line">
        <span>Clics:</span>
        <span class="stat-value-clics">${formatNumber(cible.total_clics)}</span>
      </div>
      <div class="cible-stat-line">
        <span>Total:</span>
        <span class="stat-value-total">${formatNumber(cible.points_gagnes)}</span>
      </div>
    </div>
    <button class="cible-btn" onclick="clickCible(${cible.numero})">
      CLIC !
    </button>
    <button class="cible-select-btn ${gameState.cible_selectionnee === cible.numero ? "selected" : ""}" 
            onclick="selectCible(${cible.numero})">
      ${gameState.cible_selectionnee === cible.numero ? "SÉLECTIONNÉ" : "Voir améliorations"}
    </button>
  `;

  return card;
}

function updateCibleCard(cibleId) {
  const cible = gameState.cibles[cibleId];
  const card = document.querySelector(`[data-cible-id="${cibleId}"]`);
  if (!card || !cible) return;

  card.querySelector(".stat-value-ppc").textContent = formatNumber(
    cible.points_par_clic,
  );
  card.querySelector(".stat-value-auto").textContent =
    cible.auto_clics_par_tick;
  card.querySelector(".stat-value-clics").textContent = formatNumber(
    cible.total_clics,
  );
  card.querySelector(".stat-value-total").textContent = formatNumber(
    cible.points_gagnes,
  );

  const selectBtn = card.querySelector(".cible-select-btn");
  if (gameState.cible_selectionnee === cibleId) {
    selectBtn.classList.add("selected");
    selectBtn.textContent = "SÉLECTIONNÉ";
  } else {
    selectBtn.classList.remove("selected");
    selectBtn.textContent = "Voir améliorations";
  }
}

function updateAllSelectButtons() {
  const allCards = document.querySelectorAll(".cible-card");
  allCards.forEach((card) => {
    const cibleId = parseInt(card.dataset.cibleId);
    const selectBtn = card.querySelector(".cible-select-btn");

    if (gameState.cible_selectionnee === cibleId) {
      selectBtn.classList.add("selected");
      selectBtn.textContent = "SÉLECTIONNÉ";
    } else {
      selectBtn.classList.remove("selected");
      selectBtn.textContent = "Voir améliorations";
    }
  });
}

function updateAmeliorations() {
  const container = document.getElementById("ameliorationsContainer");

  if (!gameState.ameliorations) return;

  // Vérifier si on doit reconstruire (changement de cible sélectionnée)
  const existingTypes = new Set(
    Array.from(container.children).map((card) => card.dataset.type),
  );
  const currentTypes = new Set(gameState.ameliorations.map((a) => a.type));

  // Si les types ne correspondent pas, on reconstruit tout
  const needsRebuild =
    existingTypes.size !== currentTypes.size ||
    ![...existingTypes].every((t) => currentTypes.has(t));

  if (needsRebuild) {
    container.innerHTML = "";
    gameState.ameliorations.forEach((amelio) => {
      container.appendChild(createAmeliorationCard(amelio));
    });
  } else {
    // Sinon, on met juste à jour les valeurs
    gameState.ameliorations.forEach((amelio) => {
      const card = container.querySelector(`[data-type="${amelio.type}"]`);
      if (card) {
        updateAmeliorationCard(card, amelio);
      }
    });
  }
}

function updateAmeliorationCard(card, amelio) {
  // Mettre à jour le niveau
  const niveauElem = card.querySelector(".amelioration-niveau");
  if (niveauElem) {
    niveauElem.textContent = `Niveau: ${amelio.niveau}`;
  }

  // Mettre à jour le bouton
  const btn = card.querySelector(".amelioration-btn");
  if (btn) {
    btn.textContent = `${formatNumber(amelio.prix)}`;
    btn.disabled = gameState.points < amelio.prix;

    // Mettre à jour le onclick
    const cibleId = amelio.pour_cible ? gameState.cible_selectionnee : null;
    btn.onclick = () => buyAmelioration(amelio.type, cibleId);
  }
}

function createAmeliorationCard(amelio) {
  const card = document.createElement("div");
  card.className = "amelioration-card";
  card.dataset.type = amelio.type;

  const cibleId = amelio.pour_cible ? gameState.cible_selectionnee : null;
  const canAfford = gameState.points >= amelio.prix;

  card.innerHTML = `
    <div class="amelioration-name">${amelio.nom}</div>
    <div class="amelioration-description">${amelio.description}</div>
    <div class="amelioration-niveau">Niveau: ${amelio.niveau}</div>
    <button class="amelioration-btn" 
            data-type="${amelio.type}"
            ${!canAfford ? "disabled" : ""}>
      ${formatNumber(amelio.prix)}
    </button>
  `;

  const btn = card.querySelector(".amelioration-btn");
  btn.onclick = () => buyAmelioration(amelio.type, cibleId);

  return card;
}

// ============================================================================
// ANIMATIONS
// ============================================================================

function animateCibleClick(cibleId) {
  const card = document.querySelector(`[data-cible-id="${cibleId}"]`);
  if (!card) return;

  const btn = card.querySelector(".cible-btn");
  btn.style.transform = "scale(0.95)";
  setTimeout(() => {
    btn.style.transform = "";
  }, 100);
}

function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast ${type} show`;

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// ============================================================================
// UTILS
// ============================================================================

function formatNumber(num) {
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(2) + "B";
  }
  if (num >= 1000000) {
    return (num / 1000000).toFixed(2) + "M";
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(2) + "K";
  }
  return num.toLocaleString("fr-FR");
}

// ============================================================================
// CLEANUP
// ============================================================================

window.addEventListener("beforeunload", () => {
  if (updateInterval) {
    clearInterval(updateInterval);
  }
});
