import Chat from './components/Chat/Chat';
import FileUploader from './components/FileUpload/Upload';
import SectionSwitchBar from './components/Section/Section';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  return (
    <div>
      <div className="row">
        <div className="col-4">
          <div className="uploader">
            <FileUploader />
            <SectionSwitchBar />
          </div>
        </div>

        <div className="col-8">
          <div className="bg-1">
            <h1 className="text-center text-logo"> Chat Document</h1>
            <Chat />
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
