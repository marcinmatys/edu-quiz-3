import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// API Configuration
// To use real API:
// 1. Set USE_MOCK_API to false
// 2. Set API_BASE_URL in src/lib/api.ts to your real API URL if needed
const USE_MOCK_API = false; // Set to false to use real API

// Initialize MSW in development environment
async function enableMocking() {
  if (process.env.NODE_ENV !== 'development' || !USE_MOCK_API) {
    console.log(`API Mode: ${USE_MOCK_API ? 'Mock API' : 'Real API'}`);
    return
  }

  const { worker } = await import('./mocks/browser')
  console.log('Mock Service Worker enabled');
  return worker.start({ onUnhandledRequest: 'bypass' })
}

// Start the app after enabling mocking
enableMocking().then(() => {
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
})
