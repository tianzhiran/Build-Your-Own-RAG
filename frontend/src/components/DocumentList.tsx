import type { DocumentRecord } from "../api/client";

type DocumentListProps = {
  documents: DocumentRecord[];
  onDelete: (documentId: string) => void;
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

export function DocumentList({ documents, onDelete }: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="empty-state">
        <span>✦</span>
        <p>No documents yet. Upload class notes, readings, or internal manuals to begin.</p>
      </div>
    );
  }

  return (
    <div className="document-list">
      {documents.map((document) => (
        <article className="document-row" key={document.document_id}>
          <div>
            <div className="document-title">{document.filename}</div>
            <div className="document-meta">
              {document.file_type} · {formatDate(document.upload_time)}
            </div>
          </div>
          <div className="document-actions">
            <span className={`status-pill status-${document.status}`}>{document.status}</span>
            <button onClick={() => onDelete(document.document_id)}>Delete</button>
          </div>
        </article>
      ))}
    </div>
  );
}
