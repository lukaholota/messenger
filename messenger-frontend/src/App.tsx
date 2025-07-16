import React, { useState } from 'react';
import { Login } from './components/Login';
import './css/index.css';
import ChatApp from "./ChatApp";

const App: React.FC = () => {
  const [accessToken, setAccessToken] = useState<string | null>(localStorage.getItem('access_token'));

  if (!accessToken) {
    return <Login setAccessToken={setAccessToken} />;
  }

  return <ChatApp accessToken={accessToken} />;
};


export default App;
