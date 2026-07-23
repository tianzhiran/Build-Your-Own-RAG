const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export type DocumentRecord = {
  document_id: string;
  filename: string;
  file_type: string;
  upload_time: string;
  status: string;
};

export type Source = {
  document_id: string;
  chunk_id: string;
  filename: string;
  distance: number;
};

export type AskResponse = {
  answer: string;
  contexts: string[];
  sources: Source[];
};

function extractErrorMessage(payload: string) {
  if (!payload) {
    return "Request failed.";
  }

  try {
    const parsed = JSON.parse(payload) as { detail?: string };

    return parsed.detail ?? payload;
  } catch {
    return payload;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const payload = await response.text();

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload) || `Request failed with ${response.status}`);
  }

  if (!payload) {
    return undefined as T;
  }

  return JSON.parse(payload) as T;
}

export function listDocuments() {
  return request<DocumentRecord[]>("/documents");
}

export function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  return request("/documents/upload", {
    method: "POST",
    body: formData
  });
}

export function deleteDocument(documentId: string) {
  return request(`/documents/${documentId}`, {
    method: "DELETE"
  });
}

export function askQuestion(question: string) {
  return request<AskResponse>("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ question })
  });
}
