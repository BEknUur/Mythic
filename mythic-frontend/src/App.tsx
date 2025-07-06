import { useState } from 'react'
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom'
import { MainLayout } from './components/MainLayout'
import { HomePage } from './components/HomePage'
import { GeneratePage } from './components/GeneratePage'
import { ProgressTracker } from './components/ProgressTracker'
import { MyBooksLibrary } from './components/MyBooksLibrary'
import { BookReader } from './components/BookReader'
import { TikTokPage } from './components/TikTokPage'
import { HelpPage } from './components/HelpPage'
import { Toaster } from './components/ui/toaster'
import './App.css'

// Placeholder components
const FanficPage = () => <div className="p-8"><h1>Написать фанфик</h1><p>Скоро здесь появится возможность создавать фанфики!</p></div>;
const SettingsPage = () => <div className="p-8"><h1>Настройки</h1><p>Скоро здесь можно будет настроить приложение.</p></div>;

function AppContent() {
  const navigate = useNavigate();
  const [runId, setRunId] = useState<string | null>(null);
  const [bookToRead, setBookToRead] = useState<{ bookId?: string; runId?: string } | null>(null);

  const handleStartScrape = (id: string) => {
    setRunId(id);
    navigate('/progress');
  };

  const handleReset = () => {
    setRunId(null);
    navigate('/generate');
  };

  const handleShowLibrary = () => {
    navigate('/library');
  };
  
  const handleBackToMain = () => {
    navigate('/');
  };
  
  const handleOpenBookReader = (bookId?: string, runId?: string) => {
    setBookToRead({ bookId, runId });
    navigate('/reader');
  };

  const handleBackFromReader = () => {
    setBookToRead(null);
    navigate('/library');
  };

  return (
    <>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route 
            path="/generate" 
            element={<GeneratePage onStartScrape={handleStartScrape} />} 
          />
          <Route path="/tiktok" element={<TikTokPage />} />
          <Route 
            path="/library"
            element={<MyBooksLibrary onBack={handleBackToMain} onOpenBook={handleOpenBookReader} />}
          />
          <Route path="/fanfic" element={<FanficPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/help" element={<HelpPage />} />
        </Route>
        
        <Route 
          path="/progress"
          element={
            runId ? (
              <ProgressTracker runId={runId} onComplete={() => {}} onReset={handleReset} />
            ) : (
              <Navigate to="/generate" />
            )
          } 
        />
        <Route
          path="/reader"
          element={
            bookToRead ? (
              <BookReader 
                bookId={bookToRead.bookId} 
                runId={bookToRead.runId} 
                onBack={handleBackFromReader} 
              />
            ) : (
              <Navigate to="/library" />
            )
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      <Toaster />
    </>
  );
}

function App() {
  return <AppContent />;
}

export default App;
