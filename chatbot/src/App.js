import './App.css';
import "bootstrap/dist/css/bootstrap.min.css";
import Home from './components/Home';
import Chatbot from './components/Chatbot';

function App() {
  return(
    <div className='app'>
      <Home />
      <Chatbot />
    </div>
  )
}

export default App;
