import { ChangeEvent, FormEvent, useState } from "react";
import axios from "axios";





const FileUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [fileType, setFileType] = useState<string>("pdf");
  const [query, setQuery] = useState<string>("");
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const file = e.target.files ? e.target.files[0] : null;
    if (!file) return;
    setFile(file);
  };

  const handleFileTypeChange = (e: ChangeEvent<HTMLSelectElement>): void => {
    setFileType(e.target.value);
  };

  const handleQueryChange = (e: ChangeEvent<HTMLInputElement>):void => {
    setQuery(e.target.value);
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file as File);
      formData.append("query", query);

      let endpoint = "";
      if (fileType === "pdf") {
        endpoint = "predict_pdf";
      } else if (fileType === "txt") {
        endpoint = "predict_txt";
      } else if (fileType === "csv") {
        endpoint = "analyze_csv";
      }

      const response = await axios.post(
        `http://localhost:8000/${endpoint}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data.result);
      setLoading(false);
    } catch (error) {
      console.error("Error:", error);
      setLoading(false);
    }
  };

  return (
    <div className="min-w-[1020px] h-[500px] gap-2 flex flex-wrap justify-center items-center">
      <div className="w-[500px] h-full bg-white flex flex-col justify-center items-center gap-2 p-3 rounded-md">
        <h2 className="text-center font-bold text-lg w-full border-b-2">Upload a file</h2>
        <div className="flex gap-2">
          <label>Select file type:</label>
          <select
            className="bg-gray-100 px-4 py-1 rounded-md"
            value={fileType}
            onChange={handleFileTypeChange}
          >
            <option value="">Select file type</option>
            <option value="pdf">PDF</option>
            <option value="txt">TXT</option>
            <option value="csv">CSV</option>
          </select>
        </div>
        <div className="flex transition-all hover:bg-gray-200 border-2 border-dotted justify-center items-center bg-gray-100 w-full h-full relative rounded-md">
          <label className="absolute pointer-events-none w-1/2 break-all  overflow-hidden">
            {
              file ? "Selected File: " + file.name : "Select or Drop a File"
            }
          </label>
          <input
            className="w-full h-full opacity-0 cursor-pointer"
            type="file"
            accept={`.${fileType}`}
            onChange={handleFileChange}
          />
        </div>
        <form className="w-full flex gap-2" onSubmit={handleSubmit}>
          <input
            className="w-full bg-gray-100 px-4 py-1 rounded-md"
            type="text"
            required
            placeholder="Enter query"
            value={query}
            disabled={!fileType || !file}
            onChange={handleQueryChange}
          />
          <button
            className={`${file ? "bg-blue-500" : "bg-blue-300 cursor-not-allowed"} text-white px-4 py-1 rounded-md`}
            type="submit"
            disabled={!fileType || !file}
          >
            {
              loading ? "Loading..." : "Submit"
            }
          </button>
        </form>
      </div>
      <div className="w-[500px] h-full bg-white flex flex-col justify-center items-center gap-5 p-3 rounded-md">
        <h1 className="text-center font-bold text-lg w-full border-b-2">Result</h1>
        {result ? <p
          className="w-full h-full overflow-y-auto bg-gray-100 p-3 rounded-md"
        >{result}</p>
        : <p className="w-full h-full flex justify-center items-center  bg-gray-100 font-bold p-3 rounded-md">NO Result</p>
      } 
      </div>
    </div>
  );
}

export default FileUpload;

