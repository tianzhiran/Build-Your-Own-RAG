type DocumentUploaderProps = {
  isUploading: boolean;
  onUpload: (file: File) => void;
};

export function DocumentUploader({ isUploading, onUpload }: DocumentUploaderProps) {
  return (
    <label className="upload-card">
      <input
        type="file"
        accept=".md,.markdown,.txt,.pdf"
        disabled={isUploading}
        onChange={(event) => {
          const file = event.target.files?.[0];

          if (file) {
            onUpload(file);
            event.target.value = "";
          }
        }}
      />
      <span className="eyebrow">Knowledge Library</span>
      <strong>{isUploading ? "Uploading…" : "Drop in a note, paper, or manual"}</strong>
      <small>Supports Markdown, TXT, and text-based PDF files.</small>
    </label>
  );
}
