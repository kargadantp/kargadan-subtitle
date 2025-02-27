"use client";

import { useState } from "react";
import axios from "axios";
import { Upload, Loader, CheckCircle, AlertCircle } from "lucide-react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [srtUrl, setSrtUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("لطفاً یک فایل انتخاب کنید.");
      return;
    }

    setLoading(true);
    setError(null);
    setSrtUrl(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData);
      setSrtUrl(response.data.srt_url);
    } catch (err) {
      setError("مشکلی در پردازش فایل رخ داد. لطفاً دوباره تلاش کنید.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-6">
      <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full max-w-md text-center">
        <h1 className="text-3xl font-bold mb-6 text-blue-400">زیرنویس خودکار با کرگدن</h1>
        
        <input 
          type="file" 
          onChange={handleFileChange} 
          className="mb-4 p-2 border border-gray-600 bg-gray-700 rounded-lg text-white w-full" 
        />

        <button
          onClick={handleUpload}
          className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 transition duration-300 text-white px-6 py-3 rounded-lg w-full disabled:opacity-50"
          disabled={loading}
        >
          {loading ? <Loader className="animate-spin" /> : <Upload />}
          {loading ? "در حال پردازش..." : "آپلود و پردازش"}
        </button>

        {error && (
          <p className="text-red-400 mt-3 flex items-center gap-2"><AlertCircle /> {error}</p>
        )}

        {srtUrl && (
          <div className="mt-4">
            <a 
              href={srtUrl} 
              className="text-green-400 flex items-center gap-2 hover:text-green-300 transition duration-300"
            >
              <CheckCircle /> دانلود زیرنویس
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
