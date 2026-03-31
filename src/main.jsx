import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import App from './App';
import './index.css';
import './styles/mobile.css'; // Mobile optimizations

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 3000,
          style: {
            fontSize: '17px',
            fontWeight: '700',
            maxWidth: '95vw',
            padding: '18px 24px',
            borderRadius: '14px',
            boxShadow: '0 10px 40px rgba(0,0,0,0.30)',
          },
          success: {
            duration: 3500,
            style: {
              background: '#15803d',
              color: '#ffffff',
              border: '2px solid #166534',
            },
            iconTheme: {
              primary: '#ffffff',
              secondary: '#15803d',
            },
          },
          error: {
            duration: 5000,
            style: {
              background: '#dc2626',
              color: '#ffffff',
              border: '2px solid #991b1b',
            },
            iconTheme: {
              primary: '#ffffff',
              secondary: '#dc2626',
            },
          },
          loading: {
            style: {
              background: '#1d4ed8',
              color: '#ffffff',
              border: '2px solid #1e40af',
            },
            iconTheme: {
              primary: '#ffffff',
              secondary: '#1d4ed8',
            },
          },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
);
