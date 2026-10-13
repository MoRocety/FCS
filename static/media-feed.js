import { api, account, signedIn } from "./account.js";
import { validateMediaSelection } from "./media-draft.js";
const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const categories = {
  campus: "Campus",
  study: "Study",
  events: "Events",
  clubs: "Clubs",
};
const when = (value) =>
  new Date(value).toLocaleDateString("en-PK", {
    month: "short",
    day: "numeric",
    timeZone: "Asia/Karachi",
  });
let root,
  courses = [],
  epoch = 0,
  before = null,
  category = "",
  course = "",
  drafts = [];
const posts = new Map();
const composer = document.createElement("dialog");
composer.className = "media-composer";
composer.setAttribute("aria-labelledby", "media-compose-title");
document.body.append(composer);
function clearDrafts() {
  drafts.forEach((d) => URL.revokeObjectURL(d.url));
  drafts = [];
}
composer.addEventListener("close", clearDrafts);
let publishing = false;
composer.addEventListener("cancel", (event) => {
  if (publishing) event.preventDefault();
});
export function leaveFeed() {
  epoch++;
  root = null;
  if (composer.open) composer.close();
}
function message(text, error = false) {
  const output = root?.querySelector("#feed-status");
  if (output) {
    output.textContent = text;
    output.classList.toggle("error", error);
  }
}
export async function renderFeed(container, catalogCourses) {
  root = container;
  courses = catalogCourses;
  const token = ++epoch;
  posts.clear();
  root.innerHTML = `<div class="feed-layout"><div class="feed-main"><div class="feed-heading"><div><p class="eyebrow">THE MOMENTS BETWEEN CLASSES</p><h2>Your campus, in the picture.</h2><p>Projects, everyday discoveries, and a little life around the timetable.</p></div><button class="primary-button" data-feed-compose>Share a moment +</button></div><div class="feed-filters" aria-label="Filter campus feed"><div class="feed-categories">${Object.entries(
    { "": "Everything", ...categories },
  )
    .map(
      ([key, label]) =>
        `<button data-feed-category="${key}" aria-pressed="${key === category}">${label}</button>`,
    )
    .join(
      "",
    )}</div><label class="feed-course-label">Course<select id="feed-course"><option value="">All courses</option>${courses.map((c) => `<option value="${esc(c.key)}" ${c.key === course ? "selected" : ""}>${esc(c.code)} · ${esc(c.name)}</option>`).join("")}</select></label><button class="text-button" data-feed-refresh>Refresh ↻</button></div><p id="feed-status" class="form-error" role="status" aria-live="polite"></p><div id="feed-posts" class="feed-posts" aria-busy="true"></div><button class="feed-more text-button" data-feed-more hidden>Older moments ↓</button></div><aside class="feed-aside"><span class="feed-orbit" aria-hidden="true">✳</span><p class="eyebrow">A WINDOW INTO CAMPUS</p><h3>More than a schedule.</h3><p>Share a project you’re proud of. Find a club. Catch a glimpse of the week beyond your classes.</p><div class="feed-aside-note"><strong>Made for moments</strong><p>Up to four photos or one clip, with a caption and descriptions for everyone.</p></div><div class="feed-aside-note"><strong>A shared space</strong><p>Posts are public. Share media you have permission to post; keep private student information out. Report content that needs attention.</p></div><a href="/" class="text-button">Back to your week ↗</a></aside></div>`;
  await fetchPosts(false, token);
}
function mediaMarkup(asset) {
  return asset.kind === "image"
    ? `<a class="feed-photo-link" href="${esc(asset.url)}" target="_blank" rel="noopener" aria-label="Open photo: ${esc(asset.description)}"><img src="${esc(asset.url)}" alt="${esc(asset.description)}" loading="lazy" width="${asset.width || 800}" height="${asset.height || 600}"></a>`
    : `<div class="feed-video"><video src="${esc(asset.url)}" controls playsinline preload="metadata" aria-label="${esc(asset.description)}"></video><p>${esc(asset.description)} · ${Math.round(asset.duration)}s clip</p></div>`;
}
function postMarkup(post) {
  return `<article class="feed-post" data-feed-post="${post.id}"><header class="feed-post-header"><span class="feed-avatar" aria-hidden="true">${esc(post.display_name.slice(0, 1).toUpperCase())}</span><div><strong>${esc(post.display_name)}</strong><span>@${esc(post.username)} · <time datetime="${esc(post.created_at)}">${when(post.created_at)}</time></span></div><span class="feed-category-tag">${categories[post.category]}</span></header><div class="feed-media feed-media-${post.assets.length}">${post.assets.map(mediaMarkup).join("")}</div><div class="feed-post-body">${post.course_key ? `<a href="/campus?kind=course&subject=${encodeURIComponent(post.course_key)}#explore" class="feed-course-tag">${esc(post.course_key.replace(":", " "))} · ${esc(post.course_name)} ↗</a>` : ""}<p class="entry-body">${esc(post.body)}</p><div class="feed-actions"><button class="feed-like" data-feed-like="${post.id}" aria-pressed="${post.liked}" aria-label="${post.liked ? "Unlike" : "Like"} this post">${post.liked ? "♥" : "♡"} <span>${post.like_count}</span></button><span class="muted small">${post.comment_count} comment${post.comment_count === 1 ? "" : "s"}</span><span class="feed-action-spacer"></span>${account.user?.id === post.owner_id ? `<button class="text-button action-danger" data-feed-remove="${post.id}">Remove</button>` : ""}<button class="text-button" data-report="${post.id}" data-type="media_post">Report</button></div><details class="feed-comments" data-feed-comments="${post.id}"><summary>Join the conversation</summary><div class="feed-comment-list"></div><button class="text-button" data-feed-more-comments="${post.id}" hidden>More comments ↓</button>${account.user ? `<form class="feed-comment-form" data-feed-comment-form="${post.id}"><label class="sr-only" for="feed-comment-${post.id}">Comment</label><textarea id="feed-comment-${post.id}" name="body" rows="2" minlength="2" maxlength="2000" placeholder="Add something to the conversation…" required></textarea><button class="text-button" type="submit">Post comment ↗</button><p class="form-error" role="status"></p></form>` : '<p class="small muted"><button class="text-button" data-login>Sign in</button> to comment.</p>'}</details></div></article>`;
}
async function fetchPosts(append, token = epoch) {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  if (course) params.set("course", course);
  if (append && before) params.set("before", before);
  const more = root?.querySelector("[data-feed-more]");
  if (more) more.disabled = true;
  try {
    const data = await api(`/media/posts?${params}`);
    if (token !== epoch || !root) return;
    const list = root.querySelector("#feed-posts");
    if (!append) {
      list.innerHTML = "";
      posts.clear();
    }
    for (const post of data.posts) {
      posts.set(post.id, post);
      list.insertAdjacentHTML("beforeend", postMarkup(post));
    }
    if (!posts.size)
      list.innerHTML = `<div class="feed-empty"><span aria-hidden="true">✳</span><p class="eyebrow">${category || course ? "A QUIET CORNER, FOR NOW" : "EVERY FEED STARTS WITH A MOMENT"}</p><h3>${category || course ? "Nothing here yet." : "Be the first to share."}</h3><p>${category || course ? "Try another category or share something here." : "A study setup, a campus view, or the project you just finished. Make this space yours."}</p><button class="primary-button" data-feed-compose>Share a moment +</button></div>`;
    before = data.next_before;
    root.querySelector("[data-feed-more]").hidden = !before;
    list.setAttribute("aria-busy", "false");
    list.querySelectorAll("details").forEach((detail) => {
      if (detail.dataset.bound) return;
      detail.dataset.bound = "true";
      detail.addEventListener("toggle", () => {
        if (detail.open && !detail.dataset.loaded) loadComments(detail);
      });
    });
  } catch (error) {
    if (token === epoch) message(error.message, true);
  } finally {
    if (token === epoch && more) more.disabled = false;
  }
}
async function loadComments(detail, append = false) {
  const token = epoch,
    identity = detail.dataset.feedComments;
  const list = detail.querySelector(".feed-comment-list");
  try {
    const data = await api(
      `/media/posts/${identity}/comments${append ? `?after=${detail.dataset.after}` : ""}`,
    );
    if (token !== epoch || !detail.isConnected) return;
    if (!append) list.innerHTML = "";
    data.comments.forEach((comment) =>
      list.insertAdjacentHTML(
        "beforeend",
        `<div class="feed-comment"><strong>${esc(comment.display_name)}</strong><span class="muted small"> · ${when(comment.created_at)}</span><p class="entry-body">${esc(comment.body)}</p><div>${account.user?.id === comment.owner_id ? `<button class="text-button action-danger" data-feed-remove-comment="${comment.id}" data-post="${identity}">Remove</button>` : ""}<button class="text-button" data-report="${comment.id}" data-type="media_comment">Report</button></div></div>`,
      ),
    );
    if (!list.children.length)
      list.innerHTML = '<p class="muted small">Start the conversation.</p>';
    detail.dataset.loaded = "true";
    detail.dataset.after = data.next_after || "";
    detail.querySelector("[data-feed-more-comments]").hidden = !data.next_after;
  } catch (error) {
    message(error.message, true);
  }
}
function showComposer() {
  clearDrafts();
  composer.innerHTML = `<button class="dialog-close" data-feed-close aria-label="Close upload">×</button><p class="eyebrow">A LITTLE LIFE AROUND CAMPUS</p><h2 id="media-compose-title">Share a moment.</h2><p class="muted">Public on FCS, under your display name.</p><form class="platform-form" id="media-compose-form"><label class="media-drop">Photos or a short clip<input type="file" id="media-files" accept="image/jpeg,image/png,image/webp,video/mp4,video/webm" multiple><span>Up to 4 photos (8 MB each), or 1 clip (20 MB, 60 seconds).</span></label><div id="media-previews"></div><label>Caption<textarea name="body" rows="3" placeholder="What’s the story?" minlength="2" maxlength="2000" required></textarea></label><div class="media-form-row"><label>Category<select name="category" aria-label="Category">${Object.entries(
    categories,
  )
    .map(
      ([key, label]) =>
        `<option value="${key}" ${key === category ? "selected" : ""}>${label}</option>`,
    )
    .join(
      "",
    )}</select></label><label>Link a course (optional)<input id="media-course-search" aria-label="Link a course (optional)" list="media-courses" placeholder="Type a course code…" autocomplete="off"><datalist id="media-courses">${courses.map((c) => `<option value="${esc(c.code)}">${esc(c.name)}</option>`).join("")}</datalist></label></div><p class="muted small">Photo metadata is removed. Clips are converted for playback. Add a description for each upload, and include any spoken context in your caption.</p><p class="form-error" id="media-compose-error" role="status" aria-live="polite"></p><div class="media-form-actions"><button class="text-button" data-feed-close type="button">Cancel</button><button class="primary-button" type="submit">Publish moment ↗</button></div></form>`;
  if (course)
    composer.querySelector("#media-course-search").value =
      courses.find((c) => c.key === course)?.code || "";
  composer.showModal();
}
function previews() {
  composer.querySelector("#media-previews").innerHTML = drafts
    .map(
      (draft, index) =>
        `<div class="media-preview">${draft.file.type.startsWith("image/") ? `<img src="${draft.url}" alt="Upload preview">` : `<video src="${draft.url}" controls preload="metadata" playsinline></video>`}<div><p>${esc(draft.file.name)}</p><label>Describe ${draft.file.type.startsWith("image/") ? "the photo" : "the clip"}<input data-media-description="${index}" value="${esc(draft.description)}" maxlength="240" minlength="2" placeholder="What can someone see here?" required></label><button class="text-button action-danger" data-media-remove="${index}" type="button">Remove file</button></div></div>`,
    )
    .join("");
}
composer.addEventListener("change", (event) => {
  if (event.target.id !== "media-files") return;
  const files = Array.from(event.target.files),
    error = validateMediaSelection(files);
  composer.querySelector("#media-compose-error").textContent = error || "";
  if (error) {
    event.target.value = "";
    return;
  }
  clearDrafts();
  drafts = files.map((file) => ({
    file,
    url: URL.createObjectURL(file),
    description: "",
  }));
  previews();
  event.target.value = "";
});
composer.addEventListener("input", (event) => {
  if (event.target.matches("[data-media-description]"))
    drafts[Number(event.target.dataset.mediaDescription)].description =
      event.target.value;
});
composer.addEventListener("click", (event) => {
  if (event.target.closest("[data-feed-close]") && !publishing)
    composer.close();
  const remove = event.target.closest("[data-media-remove]");
  if (remove) {
    URL.revokeObjectURL(drafts[Number(remove.dataset.mediaRemove)].url);
    drafts.splice(Number(remove.dataset.mediaRemove), 1);
    previews();
  }
});
composer.addEventListener("submit", async (event) => {
  if (event.target.id !== "media-compose-form") return;
  event.preventDefault();
  const form = event.target,
    button = form.querySelector("button[type=submit]"),
    error = composer.querySelector("#media-compose-error");
  const invalid = validateMediaSelection(drafts.map((d) => d.file));
  if (invalid) {
    error.textContent = invalid;
    return;
  }
  const courseCode = form
      .querySelector("#media-course-search")
      .value.trim()
      .toUpperCase(),
    linked = courses.find((c) => c.code.toUpperCase() === courseCode);
  if (courseCode && !linked) {
    error.textContent =
      "Choose an exact course code from the suggestions, or leave it blank.";
    return;
  }
  const data = new FormData(form);
  if (linked) data.set("course_key", linked.key);
  data.set("descriptions", JSON.stringify(drafts.map((d) => d.description)));
  drafts.forEach((d) => data.append("media", d.file));
  const token = epoch;
  publishing = true;
  composer
    .querySelectorAll("input,select,textarea,button")
    .forEach((control) => (control.disabled = true));
  button.textContent = "Processing & publishing…";
  error.textContent = "";
  try {
    await api("/media/posts", { method: "POST", data });
    if (token !== epoch) return;
    composer.close();
    category = "";
    course = "";
    await renderFeed(root, courses);
    message("Your moment is published.");
  } catch (e) {
    if (composer.open) error.textContent = e.message;
  } finally {
    publishing = false;
    composer
      .querySelectorAll("input,select,textarea,button")
      .forEach((control) => (control.disabled = false));
    button.disabled = false;
    button.textContent = "Publish moment ↗";
  }
});
document.addEventListener("change", async (event) => {
  if (event.target.id === "feed-course" && root) {
    course = event.target.value;
    await renderFeed(root, courses);
  }
});
document.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button || !root) return;
  try {
    if (button.hasAttribute("data-feed-compose")) {
      if (await signedIn()) showComposer();
    }
    if (button.hasAttribute("data-feed-category")) {
      category = button.dataset.feedCategory;
      await renderFeed(root, courses);
    }
    if (button.hasAttribute("data-feed-refresh"))
      await renderFeed(root, courses);
    if (button.hasAttribute("data-feed-more")) await fetchPosts(true);
    if (button.hasAttribute("data-feed-more-comments"))
      await loadComments(button.closest("details"), true);
    if (button.hasAttribute("data-feed-like")) {
      if (!(await signedIn())) return;
      const post = posts.get(Number(button.dataset.feedLike));
      button.disabled = true;
      const data = await api(`/media/posts/${post.id}/like`, {
        method: post.liked ? "DELETE" : "PUT",
      });
      post.liked = data.liked;
      post.like_count = data.like_count;
      button.setAttribute("aria-pressed", String(data.liked));
      button.setAttribute(
        "aria-label",
        `${data.liked ? "Unlike" : "Like"} this post`,
      );
      button.innerHTML = `${data.liked ? "♥" : "♡"} <span>${data.like_count}</span>`;
    }
    if (
      button.hasAttribute("data-feed-remove") &&
      confirm("Remove your post from the feed?")
    ) {
      await api(`/media/posts/${button.dataset.feedRemove}`, {
        method: "DELETE",
      });
      await renderFeed(root, courses);
      message("Post removed.");
    }
    if (
      button.hasAttribute("data-feed-remove-comment") &&
      confirm("Remove your comment?")
    ) {
      await api(`/media/comments/${button.dataset.feedRemoveComment}`, {
        method: "DELETE",
      });
      await renderFeed(root, courses);
      message("Comment removed.");
    }
  } catch (error) {
    message(error.message, true);
  } finally {
    button.disabled = false;
  }
});
document.addEventListener("submit", async (event) => {
  const form = event.target;
  if (!form.matches("[data-feed-comment-form]") || !root) return;
  event.preventDefault();
  const button = form.querySelector("button"),
    token = epoch;
  button.disabled = true;
  try {
    const identity = Number(form.dataset.feedCommentForm);
    await api(`/media/posts/${identity}/comments`, {
      method: "POST",
      data: { body: form.elements.body.value },
    });
    if (token !== epoch) return;
    form.reset();
    await loadComments(form.closest("details"));
    const post = posts.get(identity);
    post.comment_count++;
    form
      .closest("article")
      .querySelector(".feed-actions > .muted").textContent =
      `${post.comment_count} comment${post.comment_count === 1 ? "" : "s"}`;
  } catch (error) {
    form.querySelector(".form-error").textContent = error.message;
  } finally {
    button.disabled = false;
  }
});
