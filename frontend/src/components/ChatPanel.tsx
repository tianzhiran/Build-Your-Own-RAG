import type { AskResponse } from "../api/client";
import { SourceList } from "./SourceList";

type ChatPanelProps = {
  question: string;
  response: AskResponse | null;
  isAsking: boolean;
  onQuestionChange: (question: string) => void;
  onAsk: () => void;
};

export function ChatPanel({
  question,
  response,
  isAsking,
  onQuestionChange,
  onAsk
}: ChatPanelProps) {
  return (
    <section className="panel chat-panel">
      <div className="panel-header">
        <span className="eyebrow">Ask your knowledge base</span>
        <h2>Study with your uploaded context</h2>
      </div>

      <textarea
        value={question}
        placeholder="Ask about your notes, lab docs, readings, or internal knowledge…"
        onChange={(event) => onQuestionChange(event.target.value)}
      />

      <button className="primary-button" disabled={!question.trim() || isAsking} onClick={onAsk}>
        {isAsking ? "Thinking…" : "Ask RAG"}
      </button>

      {response && (
        <div className="answer-card">
          <span className="eyebrow">Answer</span>
          <p>{response.answer}</p>
          <SourceList sources={response.sources} contexts={response.contexts} />
        </div>
      )}
    </section>
  );
}
