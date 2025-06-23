import { useState } from 'react'
import { Hero } from './components/Hero'
import { Steps } from './components/Steps'
import { Form } from './components/Form'
import { Footer } from './components/Footer'
import { ProgressTracker } from './components/ProgressTracker'
import { Toaster } from './components/ui/toaster'
import './App.css'

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
      <>
        <ProgressTracker 
          runId={runId} 
          onComplete={handleComplete} 
          onReset={handleReset} 
        />
        <Toaster />
      </>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <Hero />
      <Steps />
      <Form onStartScrape={handleStartScrape} />
      <Footer />
      <Toaster />
    </div>
  )
}

export default App
