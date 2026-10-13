import test from "node:test";
import assert from "node:assert/strict";
import { validateMediaSelection } from "../static/media-draft.js";
const photo = { type: "image/jpeg", size: 1024 };
const clip = { type: "video/mp4", size: 2048 };
test("accepts up to four photos or one clip", () => {
  assert.equal(validateMediaSelection([photo, photo, photo, photo]), null);
  assert.equal(validateMediaSelection([clip]), null);
});
test("rejects empty, too many, mixed and unsupported files", () => {
  for (const files of [
    [],
    Array(5).fill(photo),
    [clip, photo],
    [clip, clip],
    [{ type: "image/svg+xml", size: 1 }],
  ])
    assert.ok(validateMediaSelection(files));
});
test("enforces early upload byte limits", () => {
  for (const files of [
    [{ ...photo, size: 0 }],
    [{ ...photo, size: 8 * 1024 * 1024 + 1 }],
    [{ ...clip, size: 20 * 1024 * 1024 + 1 }],
  ])
    assert.ok(validateMediaSelection(files));
});
