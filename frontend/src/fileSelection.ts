export function getDroppedFile(dataTransfer: Pick<DataTransfer, "files">): File | null {
  return dataTransfer.files.length > 0 ? dataTransfer.files[0] : null;
}
