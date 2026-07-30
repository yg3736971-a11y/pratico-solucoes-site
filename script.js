const WHATSAPP_NUMBER = "5511965267558";

const assistant = document.querySelector("#assistant");
const body = document.querySelector("#assistant-body");
const actions = document.querySelector("#assistant-actions");
const progress = document.querySelector("#assistant-progress");
const menuToggle = document.querySelector(".menu-toggle");
const nav = document.querySelector(".nav");

const initialState = () => ({
  step: 0,
  property: "",
  service: "",
  urgency: "",
  location: "",
  description: "",
  name: "",
});

let state = initialState();
let lastFocusedElement = null;

const steps = [
  {
    key: "property",
    question: "Olá! Vou organizar seu pedido para a equipe. Primeiro: onde será o serviço?",
    options: ["Residência ou apartamento", "Condomínio", "Empresa ou comércio"],
  },
  {
    key: "service",
    question: "Qual serviço mais se aproxima do que você precisa?",
    options: [
      "Serralheria",
      "Elétrica",
      "Marido de aluguel",
      "Manutenção predial",
      "Reparos",
      "Outro serviço",
    ],
  },
  {
    key: "urgency",
    question: "Como está a urgência do pedido?",
    options: ["Pode ser agendado", "Preciso resolver em breve", "Existe risco ou emergência"],
  },
  {
    key: "location",
    question: "Em qual bairro ou região de São Paulo será o atendimento?",
    input: "text",
    placeholder: "Ex.: Bela Vista, Liberdade, Sé...",
  },
  {
    key: "description",
    question: "Descreva brevemente o que precisa ser feito.",
    input: "textarea",
    placeholder: "Conte o problema, quantidade de itens ou resultado esperado...",
  },
  {
    key: "name",
    question: "Para finalizar, qual é o seu nome?",
    input: "text",
    placeholder: "Digite seu nome",
  },
];

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderMessage(text) {
  body.innerHTML = `<p class="assistant__message">${escapeHtml(text)}</p>`;
}

function renderStep() {
  const current = steps[state.step];
  const percentage = ((state.step + 1) / (steps.length + 1)) * 100;
  progress.style.width = `${percentage}%`;
  renderMessage(current.question);
  actions.innerHTML = "";

  if (current.options) {
    current.options.forEach((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "assistant__option";
      button.textContent = option;
      button.addEventListener("click", () => submitAnswer(option));
      actions.append(button);
    });
    actions.querySelector("button")?.focus();
    return;
  }

  const form = document.createElement("form");
  form.className = "assistant__form";
  const field =
    current.input === "textarea" ? document.createElement("textarea") : document.createElement("input");
  field.placeholder = current.placeholder;
  field.maxLength = current.input === "textarea" ? 500 : 100;
  field.required = true;
  field.setAttribute("aria-label", current.question);

  const submit = document.createElement("button");
  submit.type = "submit";
  submit.className = "assistant__submit";
  submit.setAttribute("aria-label", "Continuar");
  submit.innerHTML =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';

  form.append(field, submit);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const value = field.value.trim();
    if (value) submitAnswer(value);
  });
  actions.append(form);
  field.focus();
}

function submitAnswer(value) {
  const current = steps[state.step];
  state[current.key] = value;
  state.step += 1;
  if (state.step === 1 && state.service) {
    state.step += 1;
  }
  if (state.step >= steps.length) {
    renderSummary();
  } else {
    renderStep();
  }
}

function buildMessage() {
  return [
    "Olá, Prático Soluções! Organizei meu pedido pelo site:",
    "",
    `Nome: ${state.name}`,
    `Local: ${state.property}`,
    `Serviço: ${state.service}`,
    `Urgência: ${state.urgency}`,
    `Bairro/região: ${state.location}`,
    `Descrição: ${state.description}`,
    "",
    "Gostaria de confirmar se vocês atendem e receber uma avaliação.",
  ].join("\n");
}

function renderSummary() {
  progress.style.width = "100%";
  body.innerHTML = `
    <p class="assistant__message"><strong>Pronto, ${escapeHtml(state.name)}!</strong><br>
    Revise o resumo e abra o WhatsApp para enviar à equipe.</p>
    <div class="assistant__summary">
      <div><span>Local</span><strong>${escapeHtml(state.property)}</strong></div>
      <div><span>Serviço</span><strong>${escapeHtml(state.service)}</strong></div>
      <div><span>Urgência</span><strong>${escapeHtml(state.urgency)}</strong></div>
      <div><span>Região</span><strong>${escapeHtml(state.location)}</strong></div>
    </div>
  `;
  const url = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(buildMessage())}`;
  actions.innerHTML = `
    <a class="assistant__whatsapp" href="${url}" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.6 9.6 0 0 1-4-.9L3 21l1.7-4.3A8.3 8.3 0 0 1 3.5 12 8.5 8.5 0 0 1 12 3.5a8.5 8.5 0 0 1 9 8Z"/>
      </svg>
      Abrir conversa no WhatsApp
    </a>
    <button class="assistant__reset" type="button">Refazer pedido</button>
  `;
  actions.querySelector(".assistant__reset").addEventListener("click", resetAssistant);
  actions.querySelector(".assistant__whatsapp")?.focus();
}

function openAssistant(event) {
  lastFocusedElement = event?.currentTarget || document.activeElement;
  const preset = event?.currentTarget?.dataset.service;
  state = initialState();
  if (preset) {
    state.service = preset;
  }
  assistant.hidden = false;
  document.body.classList.add("assistant-open");

  if (preset) {
    state.step = 0;
  }
  renderStep();
}

function closeAssistant() {
  assistant.hidden = true;
  document.body.classList.remove("assistant-open");
  lastFocusedElement?.focus();
}

function resetAssistant() {
  state = initialState();
  renderStep();
}

document.querySelectorAll("[data-open-assistant]").forEach((button) => {
  button.addEventListener("click", openAssistant);
});

document.querySelectorAll("[data-close-assistant]").forEach((button) => {
  button.addEventListener("click", closeAssistant);
});

document.querySelectorAll("[data-whatsapp]").forEach((link) => {
  const message = "Olá, Prático Soluções! Vim pelo site e gostaria de solicitar uma avaliação.";
  link.href = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`;
  link.target = "_blank";
  link.rel = "noopener";
});

menuToggle?.addEventListener("click", () => {
  const open = !nav.classList.contains("is-open");
  nav.classList.toggle("is-open", open);
  menuToggle.setAttribute("aria-expanded", String(open));
});

nav?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    nav.classList.remove("is-open");
    menuToggle?.setAttribute("aria-expanded", "false");
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !assistant.hidden) closeAssistant();
});

document.querySelector("#current-year").textContent = new Date().getFullYear();
