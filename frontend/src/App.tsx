import { useEffect, useState } from "react";
import {
  askQuestion,
  deleteDocument,
  listDocuments,
  uploadDocument,
  type AskResponse,
  type DocumentRecord
} from "./api/client";
import { ChatPanel } from "./components/ChatPanel";
import { DocumentList } from "./components/DocumentList";
import { DocumentUploader } from "./components/DocumentUploader";

export default function App() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AskResponse | null>(null);
  const [notice, setNotice] = useState("Ready to study smarter.");
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);

  async function refreshDocuments() {
    setIsLoadingDocuments(true);

    try {
      setDocuments(await listDocuments());
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Failed to load documents.");
    } finally {
      setIsLoadingDocuments(false);
    }
  }

  async function handleUpload(file: File) {
    setIsUploading(true);
    setNotice(`Uploading ${file.name}…`);

    try {
      await uploadDocument(file);
      setNotice(`${file.name} is now in your knowledge base.`);
      await refreshDocuments();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleDelete(documentId: string) {
    setNotice("Removing document…");

    try {
      await deleteDocument(documentId);
      setNotice("Document removed.");
      await refreshDocuments();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Delete failed.");
    }
  }

  async function handleAsk() {
    setIsAsking(true);
    setNotice("Retrieving context…");

    try {
      setAnswer(await askQuestion(question));
      setNotice("Answer generated with retrieved sources.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Question failed.");
    } finally {
      setIsAsking(false);
    }
  }

  useEffect(() => {
    refreshDocuments();
  }, []);

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <span className="eyebrow">RAG Study Assistant</span>
          <h1>Your personal knowledge studio for notes, papers, and manuals.</h1>
          <p>
            A calm, Linear-inspired workspace for uploading documents and asking grounded
            questions against your FastAPI RAG backend.
          </p>
        </div>
        <div className="hero-card">
          <span>Backend</span>
          <strong>FastAPI · FAISS · SQLite</strong>
          <small>API docs remain available at http://127.0.0.1:8000/docs</small>
        </div>
      </section>

      <div className="notice-bar">{notice}</div>

      <section className="workspace-grid">
        <section className="panel library-panel">
          <div className="panel-header">
            <span className="eyebrow">Library</span>
            <h2>Knowledge uploads</h2>
          </div>
          <DocumentUploader isUploading={isUploading} onUpload={handleUpload} />
          {isLoadingDocuments ? (
            <div className="empty-state">Loading documents…</div>
          ) : (
            <DocumentList documents={documents} onDelete={handleDelete} />
          )}
        </section>

        <ChatPanel
          question={question}
          response={answer}
          isAsking={isAsking}
          onQuestionChange={setQuestion}
          onAsk={handleAsk}
        />
      </section>
    </main>
  );
}
