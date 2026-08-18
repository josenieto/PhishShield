import { describe, expect, it } from "vitest";

import { getDroppedFile } from "../src/fileSelection";


describe("getDroppedFile", () => {
  it("returns the first dropped file", () => {
    const firstFile = new File(["From: analyst@example.com"], "message.eml", {
      type: "message/rfc822",
    });
    const secondFile = new File(["ignored"], "other.eml", {
      type: "message/rfc822",
    });

    expect(getDroppedFile({ files: [firstFile, secondFile] as unknown as FileList })).toBe(firstFile);
  });

  it("returns null when no file was dropped", () => {
    expect(getDroppedFile({ files: [] as unknown as FileList })).toBeNull();
  });
});
