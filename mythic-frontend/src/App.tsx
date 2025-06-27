import { useState } from 'react'
import { ClerkProvider } from '@clerk/clerk-react'
import { MainLayout } from './components/MainLayout'
import { ProgressTracker } from './components/ProgressTracker'
import { MyBooksLibrary } from './components/MyBooksLibrary'
import { Toaster } from './components/ui/toaster'
import './App.css'

// Получаем ключ Clerk из переменных окружения
const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!clerkPubKey) {
  throw new Error("Missing Publishable Key")
}

type AppView = 'main' | 'library' | 'progress';

function App() {
  const [runId, setRunId] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isComplete, setIsComplete] = useState(false);
  const [currentView, setCurrentView] = useState<AppView>('main');

  const handleStartScrape = (id: string) => {
    setRunId(id)
    setIsProcessing(true)
    setIsComplete(false);
    setCurrentView('progress');
  }

  const handleComplete = () => {
    setIsComplete(true);
  }

  const handleReset = () => {
    setRunId(null)
    setIsProcessing(false)
    setIsComplete(false);
    setCurrentView('main');
  }

  const handleShowLibrary = () => {
    setCurrentView('library');
  }

  const handleBackToMain = () => {
    setCurrentView('main');
  }

  if (currentView === 'progress' && runId && (isProcessing || isComplete)) {
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

  if (currentView === 'library') {
    return (
      <ClerkProvider publishableKey={clerkPubKey}>
        <MyBooksLibrary onBack={handleBackToMain} />
        <Toaster />
      </ClerkProvider>
    )
  }

  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <MainLayout 
        onStartScrape={handleStartScrape} 
        onShowLibrary={handleShowLibrary}
      />
      <Toaster />
    </ClerkProvider>
  )
}

export default App
