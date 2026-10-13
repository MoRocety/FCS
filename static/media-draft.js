// Early feedback only; the server always decodes and validates the actual bytes.
export function validateMediaSelection(files) {
  if (!files.length || files.length > 4)
    return "Choose one clip or up to four photos.";
  const imageTypes = ["image/jpeg", "image/png", "image/webp"];
  const videoTypes = ["video/mp4", "video/webm"];
  if (files.some((file) => ![...imageTypes, ...videoTypes].includes(file.type)))
    return "Use JPEG, PNG, WebP, MP4, or WebM files.";
  if (
    files.some((file) => videoTypes.includes(file.type)) &&
    files.length !== 1
  )
    return "Post one clip or up to four photos, rather than a mix.";
  if (
    files.some(
      (file) =>
        !file.size ||
        file.size > (imageTypes.includes(file.type) ? 8 : 20) * 1024 * 1024,
    )
  )
    return "Photos can be up to 8 MB each; clips can be up to 20 MB.";
  return null;
}
