"use strict";

const taskForm = document.querySelector("#task-form");
const taskInput = document.querySelector("#new-task");
const taskList = document.querySelector("#task-list");
const taskCount = document.querySelector("#task-count");
const notice = document.querySelector("#notice");
const filterButtons = [...document.querySelectorAll("[data-filter]")];
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

let currentFilter = "all";
let requestVersion = 0;

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.method && options.method !== "GET" ? { "X-CSRF-Token": csrfToken } : {}),
      ...options.headers,
    },
  });

  if (response.status === 401) {
    window.location.assign("/login");
    throw new Error("Your session ended. Please log in again.");
  }

  if (response.status === 204) {
    return null;
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error?.message || "Something went wrong. Please try again.");
  }
  return payload;
}

function showNotice(message = "", isError = false) {
  notice.textContent = message;
  notice.classList.toggle("is-error", isError);
}

function setFilter(filter) {
  currentFilter = filter;
  for (const button of filterButtons) {
    const selected = button.dataset.filter === filter;
    button.classList.toggle("is-selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  }
}

function addEmptyState() {
  const item = document.createElement("li");
  const wrapper = document.createElement("div");
  const mark = document.createElement("span");
  const heading = document.createElement("strong");
  const copy = document.createElement("p");

  wrapper.className = "empty-state";
  mark.className = "empty-mark";
  mark.setAttribute("aria-hidden", "true");
  mark.textContent = currentFilter === "completed" ? "✓" : "·";
  heading.textContent = currentFilter === "completed" ? "Nothing completed yet" : "A clear little slate";
  copy.textContent = currentFilter === "active"
    ? "You’re all caught up. Enjoy the breathing room."
    : currentFilter === "completed"
      ? "Finished tasks will find their place here."
      : "Add a task above and take it one step at a time.";

  wrapper.append(mark, heading, copy);
  item.append(wrapper);
  taskList.append(item);
}

function makeIconButton(label, glyph, className = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `icon-button ${className}`.trim();
  button.setAttribute("aria-label", label);
  button.textContent = glyph;
  return button;
}

function renderTask(task) {
  const item = document.createElement("li");
  const row = document.createElement("article");
  const main = document.createElement("div");
  const checkbox = document.createElement("input");
  const title = document.createElement("span");
  const actions = document.createElement("div");
  const editButton = makeIconButton(`Edit ${task.title}`, "✎");
  const deleteButton = makeIconButton(`Delete ${task.title}`, "×", "delete-button");

  row.className = `task-row${task.completed ? " is-complete" : ""}`;
  main.className = "task-main";
  checkbox.className = "task-checkbox";
  checkbox.type = "checkbox";
  checkbox.checked = task.completed;
  checkbox.setAttribute("aria-label", `Mark ${task.title} ${task.completed ? "active" : "complete"}`);
  title.className = "task-title";
  title.textContent = task.title;
  actions.className = "task-actions";

  checkbox.addEventListener("change", async () => {
    await mutateTask(task.id, { completed: checkbox.checked }, "Task status updated.");
  });
  editButton.addEventListener("click", () => beginEdit(item, task));
  deleteButton.addEventListener("click", async () => {
    try {
      showNotice("");
      await apiRequest(`/api/tasks/${task.id}`, { method: "DELETE" });
      await refreshTasks("Task deleted.");
    } catch (error) {
      showNotice(error.message, true);
    }
  });

  main.append(checkbox, title);
  actions.append(editButton, deleteButton);
  row.append(main, actions);
  item.append(row);
  return item;
}

function beginEdit(item, task) {
  const form = document.createElement("form");
  const input = document.createElement("input");
  const saveButton = document.createElement("button");
  const cancelButton = document.createElement("button");

  form.className = "edit-form";
  input.type = "text";
  input.value = task.title;
  input.setAttribute("aria-label", `Edit task ${task.title}`);
  input.required = true;
  saveButton.className = "small-button";
  saveButton.type = "submit";
  saveButton.textContent = "Save";
  cancelButton.className = "small-button secondary";
  cancelButton.type = "button";
  cancelButton.textContent = "Cancel";
  cancelButton.addEventListener("click", () => refreshTasks());

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = input.value.trim();
    if (!title) {
      input.setCustomValidity("Enter a task title.");
      input.reportValidity();
      input.setCustomValidity("");
      return;
    }
    await mutateTask(task.id, { title }, "Task saved.");
  });

  form.append(input, saveButton, cancelButton);
  item.replaceChildren(form);
  input.focus();
  input.select();
}

async function mutateTask(taskId, fields, successMessage) {
  try {
    showNotice("");
    await apiRequest(`/api/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify(fields),
    });
    await refreshTasks(successMessage);
  } catch (error) {
    await refreshTasks();
    showNotice(error.message, true);
  }
}

async function refreshTasks(successMessage = "") {
  const version = ++requestVersion;
  taskList.setAttribute("aria-busy", "true");
  showNotice("Loading tasks…");
  try {
    const payload = await apiRequest(`/api/tasks?filter=${encodeURIComponent(currentFilter)}`);
    if (version !== requestVersion) return;
    const tasks = payload.tasks;
    taskList.replaceChildren();
    taskCount.textContent = `${tasks.length} ${tasks.length === 1 ? "task" : "tasks"}`;
    if (tasks.length === 0) {
      addEmptyState();
    } else {
      for (const task of tasks) {
        taskList.append(renderTask(task));
      }
    }
    showNotice(successMessage);
  } catch (error) {
    if (version !== requestVersion) return;
    taskList.replaceChildren();
    taskCount.textContent = "—";
    showNotice(error.message, true);
  } finally {
    if (version === requestVersion) {
      taskList.setAttribute("aria-busy", "false");
    }
  }
}

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = taskInput.value.trim();
  if (!title) {
    taskInput.setCustomValidity("Enter a task title.");
    taskInput.reportValidity();
    taskInput.setCustomValidity("");
    return;
  }

  const submitButton = taskForm.querySelector("button[type='submit']");
  submitButton.disabled = true;
  try {
    showNotice("");
    await apiRequest("/api/tasks", {
      method: "POST",
      body: JSON.stringify({ title }),
    });
    taskForm.reset();
    setFilter("all");
    await refreshTasks("Task added.");
    taskInput.focus();
  } catch (error) {
    showNotice(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

for (const button of filterButtons) {
  button.addEventListener("click", () => {
    setFilter(button.dataset.filter);
    refreshTasks();
  });
}

refreshTasks();
