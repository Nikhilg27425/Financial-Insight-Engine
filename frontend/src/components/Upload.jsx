import { useState } from "react";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Please select a PDF file first!");
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // 👇 Correct backend endpoint (matches Keshav’s code)
      const res = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      alert("Upload failed. Check if backend is running and CORS is configured.");
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h1>📄 Financial Document Analyzer</h1>

      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button
        onClick={handleUpload}
        disabled={loading}
        style={{ marginLeft: "1rem" }}
      >
        {loading ? "Uploading..." : "Upload PDF"}
      </button>

      {response && (
        <div style={{ marginTop: "2rem", textAlign: "left" }}>
          <h3>✅ Upload Result:</h3>
          <pre
            style={{
              background: "#f5f5f5",
              padding: "1rem",
              borderRadius: "8px",
              maxHeight: "300px",
              overflowY: "auto",
            }}
          >
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
