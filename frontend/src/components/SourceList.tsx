import type { Source } from "../api/client";

type SourceListProps = {
  sources: Source[];
  contexts: string[];
};

export function SourceList({ sources, contexts }: SourceListProps) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <details className="sources-panel">
      <summary>Sources used · {sources.length}</summary>
      <div className="source-grid">
        {sources.map((source, index) => (
          <article className="source-card" key={source.chunk_id}>
            <div className="source-heading">
              <span>{source.filename}</span>
              <small>distance {source.distance.toFixed(3)}</small>
            </div>
            <p>{contexts[index]}</p>
          </article>
        ))}
      </div>
    </details>
  );
}
