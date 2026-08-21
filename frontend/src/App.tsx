import { useState } from "react";

const API_URL = "http://127.0.0.1:8001";

type Source = {
  filename: string;
  page_start: number;
  page_end: number;
  similarity: number;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  async function uploadPdf() {
    if (!file) return;

    setUploading(true);
    setUploadStatus("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      setUploadStatus(
        `${data.filename} uploaded — ${data.pages} pages, ${data.chunks} chunks`
      );

      setFile(null);
    } catch (error) {
      setUploadStatus("Upload failed. Make sure the backend is running.");
    } finally {
      setUploading(false);
    }
  }

  async function sendMessage() {
    if (!question.trim() || loading) return;

    const currentQuestion = question.trim();

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: currentQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/chat?question=${encodeURIComponent(currentQuestion)}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Something went wrong. Make sure the FastAPI backend is running on port 8001.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Modular RAG Chat</h1>
          <p>Chat with your PDF knowledge base</p>
        </div>
      </header>

      <main className="layout">
        <aside className="sidebar">
          <h2>Documents</h2>

          <div className="upload-box">
            <input
              type="file"
              accept=".pdf"
              onChange={(event) =>
                setFile(event.target.files?.[0] ?? null)
              }
            />

            <button
              onClick={uploadPdf}
              disabled={!file || uploading}
            >
              {uploading ? "Uploading..." : "Upload PDF"}
            </button>
          </div>

          {file && (
            <div className="selected-file">
              Selected:
              <strong>{file.name}</strong>
            </div>
          )}

          {uploadStatus && (
            <div className="upload-status">
              {uploadStatus}
            </div>
          )}
        </aside>

        <section className="chat">
          <div className="messages">
            {messages.length === 0 && (
              <div className="empty-state">
                <h2>Ask your PDFs anything</h2>
                <p>
                  Upload a PDF and ask a question about its contents.
                </p>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                className={`message ${message.role}`}
                key={index}
              >
                <div className="message-role">
                  {message.role === "user" ? "You" : "AI"}
                </div>

                <div className="message-content">
                  {message.content}
                </div>

                {message.sources &&
                  message.sources.length > 0 && (
                    <div className="sources">
                      <strong>Sources</strong>

                      {message.sources.map((source, sourceIndex) => (
                        <div
                          className="source"
                          key={sourceIndex}
                        >
                          <span>{source.filename}</span>
                          <span>
                            Page{" "}
                            {source.page_start === source.page_end
                              ? source.page_start
                              : `${source.page_start}-${source.page_end}`}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
              </div>
            ))}

            {loading && (
              <div className="message assistant">
                <div className="message-role">AI</div>
                <div className="message-content">
                  Searching your PDFs...
                </div>
              </div>
            )}
          </div>

          <div className="input-area">
            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask something about your PDFs..."
              rows={2}
            />

            <button
              onClick={sendMessage}
              disabled={!question.trim() || loading}
            >
              Send
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;