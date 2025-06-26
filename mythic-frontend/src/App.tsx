import { useState } from 'react'
import { ClerkProvider } from '@clerk/clerk-react'
import { MainLayout } from './components/MainLayout'
import { ProgressTracker } from './components/ProgressTracker'
import { Toaster } from './components/ui/toaster'
import './App.css'

// Получаем ключ Clerk из переменных окружения
const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!clerkPubKey) {
  throw new Error("Missing Publishable Key")
}

function App() {
  const [runId, setRunId] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isComplete, setIsComplete] = useState(false);

  const handleStartScrape = (id: string) => {
    setRunId(id)
    setIsProcessing(true)
    setIsComplete(false);
  }

  const handleComplete = () => {
    setIsComplete(true);
  }

  const handleReset = () => {
    setRunId(null)
    setIsProcessing(false)
    setIsComplete(false);
  }

  if (runId && (isProcessing || isComplete)) {
    return (
      <ClerkProvider publishableKey={clerkPubKey}>
        <ProgressTracker 
          runId={runId} 
          onComplete={handleComplete} 
          onReset={handleReset} 
        />
        <Toaster />
      </ClerkProvider>
    )
  }

  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <MainLayout onStartScrape={handleStartScrape} />
      <Toaster />
    </ClerkProvider>
  )
}

export default App
