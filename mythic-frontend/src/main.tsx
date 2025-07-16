import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ClerkProvider } from '@clerk/clerk-react'
import { ruRU } from "@clerk/localizations"
import { ThemeProvider } from "@/components/theme-provider"
import './index.css'
import App from './App.tsx'

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!clerkPubKey) {
  throw new Error("Missing Publishable Key")
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
   <ClerkProvider
  publishableKey={clerkPubKey}
  localization={ruRU}
  signInForceRedirectUrl="/generate"
  signUpForceRedirectUrl="/generate"
>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <BrowserRouter>
    <App />
        </BrowserRouter>
      </ThemeProvider>
    </ClerkProvider>
  </StrictMode>,
)
