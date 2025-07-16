import React from 'react'
import ReactDom from 'react-dom/client'
import './css/index.css'
import App from './App.tsx'

ReactDom.createRoot(document.getElementById('root')!).render(
  // <React.StrictMode>
    <App />
  // </React.StrictMode>,
);
