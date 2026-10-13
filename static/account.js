// One session client shared by the planner and campus pages.
export const account = { user: null, csrf: null };
const escape = (v) =>
  String(v).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const ready = fetch("/api/v1/me")
  .then((r) => r.json())
  .then(applyAccount)
  .catch(() => {});
function applyAccount(data) {
  account.user = data.user;
  account.csrf = data.csrf_token;
  document.querySelectorAll("[data-account-button]").forEach((button) => {
    button.textContent = account.user ? account.user.display_name : "Sign in";
  });
  document.dispatchEvent(
    new CustomEvent("fcs-account", { detail: account.user }),
  );
  return data;
}
export async function api(path, { method = "GET", data, raw = false } = {}) {
  await ready;
  const multipart = data instanceof FormData;
  const response = await fetch(`/api/v1${path}`, {
    method,
    headers: {
      ...(data && !multipart ? { "Content-Type": "application/json" } : {}),
      ...(["POST", "PUT", "PATCH", "DELETE"].includes(method)
        ? { "X-CSRF-Token": account.csrf }
        : {}),
    },
    ...(data ? { body: multipart ? data : JSON.stringify(data) } : {}),
  });
  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ error: `Request failed (${response.status})` }));
    if (response.status === 403) {
      await fetch("/api/v1/me")
        .then((r) => r.json())
        .then(applyAccount)
        .catch(() => {});
    }
    throw new Error(error.error || "Request failed");
  }
  return raw ? response : response.json();
}
export async function signedIn() {
  await ready;
  if (account.user) return true;
  openAccount();
  return false;
}
export function openAccount() {
  document.getElementById("account-dialog").showModal();
  renderAccount();
}
function renderAccount(mode = "login") {
  const root = document.getElementById("account-body");
  if (account.user) {
    root.innerHTML = `<p class="eyebrow">YOUR CAMPUS ACCOUNT</p><h2>${escape(account.user.display_name)}</h2><p class="muted">@${escape(account.user.username)} · ${escape(account.user.role)}</p><p class="muted small">Your saved schedules and seat watches stay with this account. Community identity and enrollment are not verified.</p><a class="primary-button button-link" href="/campus#schedules">My saved schedules ↗</a><button class="text-button account-signout" data-signout>Sign out</button>`;
    return;
  }
  root.innerHTML = `<p class="eyebrow">KEEP YOUR SEMESTER TOGETHER</p><h2>${mode === "login" ? "Welcome back." : "Your campus starts here."}</h2><p class="muted">Save schedules, watch seats, and join course conversations.</p><div class="account-tabs"><button type="button" data-auth-mode="login" class="${mode === "login" ? "active" : ""}">Sign in</button><button type="button" data-auth-mode="register" class="${mode === "register" ? "active" : ""}">Create account</button></div><form id="account-form" data-mode="${mode}">${mode === "register" ? '<label>Display name<input name="display_name" autocomplete="nickname" minlength="2" maxlength="60" required></label>' : ""}<label>Username<input name="username" autocomplete="username" minlength="3" maxlength="24" pattern="[A-Za-z0-9_]+" required></label><label>Password<input name="password" type="password" autocomplete="${mode === "login" ? "current-password" : "new-password"}" ${mode === "register" ? 'minlength="10"' : ""} maxlength="256" required></label><p class="form-error" id="account-error" role="status"></p><button class="primary-button" type="submit">${mode === "login" ? "Sign in" : "Create account"} ↗</button></form><p class="muted small">An FCS account does not verify university identity or enrollment.</p>`;
}
const dialog = document.createElement("dialog");
dialog.id = "account-dialog";
dialog.className = "account-dialog";
dialog.innerHTML =
  '<button class="dialog-close" data-close-account aria-label="Close account dialog">×</button><div id="account-body"></div>';
document.body.append(dialog);
document.addEventListener("click", async (event) => {
  if (event.target.closest("[data-account-button],[data-login]")) openAccount();
  if (event.target.closest("[data-close-account]")) dialog.close();
  const mode = event.target.closest("[data-auth-mode]");
  if (mode) renderAccount(mode.dataset.authMode);
  if (event.target.closest("[data-signout]")) {
    try {
      applyAccount(await api("/accounts/logout", { method: "POST" }));
      renderAccount();
    } catch (error) {
      alert(error.message);
    }
  }
});
dialog.addEventListener("submit", async (event) => {
  if (event.target.id !== "account-form") return;
  event.preventDefault();
  const form = event.target,
    button = form.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    applyAccount(
      await api(`/accounts/${form.dataset.mode}`, {
        method: "POST",
        data: Object.fromEntries(new FormData(form)),
      }),
    );
    dialog.close();
  } catch (error) {
    document.getElementById("account-error").textContent = error.message;
  } finally {
    button.disabled = false;
  }
});
