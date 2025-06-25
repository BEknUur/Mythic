import { useState } from 'react'
import { ClerkProvider } from '@clerk/clerk-react'
import { Hero } from './components/Hero'
import { Steps } from './components/Steps'
import { Form } from './components/Form'
import { Footer } from './components/Footer'
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
      <div className="min-h-screen bg-white">
        <Hero />
        <Steps />
        <Form onStartScrape={handleStartScrape} />
        <Footer />
        <Toaster />
      </div>
    </ClerkProvider>
  )
}

export default App
