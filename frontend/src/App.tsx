import "./App.css";
import FileUpload from "./FileUpload";

function App() {
  return (
    <div className="App flex flex-col gap-5 justify-center items-center">
      <header className="App-header">
        <h1 className="bg-white px-3 py-1 rounded-md text-center font-bold text-2xl">
          File Uploader
        </h1>
      </header>
      <FileUpload />
    </div>
  );
}

export default App;
