import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom'
import { MainLayout } from './components/MainLayout'
import { HomePage } from './components/HomePage'
import { GeneratePage } from './components/GeneratePage'
import { ProgressTracker } from './components/ProgressTracker'
import { MyBooksLibrary } from './components/MyBooksLibrary'
import { BookReader } from './components/BookReader'
import { TikTokPage } from './components/TikTokPage'
import { HelpPage } from './components/HelpPage'
import { ComingSoonPage } from './components/ComingSoonPage'
import { TourProvider, TourAlertDialog, TOUR_STEP_IDS, useTour } from '@/components/ui/tour'
import { Toaster } from './components/ui/toaster'
import './App.css'

// Placeholder components
const FanficPage = () => (
  <ComingSoonPage 
    title="Написать фанфик"
    description="Этот раздел находится в активной разработке. Скоро здесь появится возможность создавать фанфики по любимым вселенным!"
  />
);
const SettingsPage = () => <div className="p-8"><h1>Настройки</h1><p>Скоро здесь можно будет настроить приложение.</p></div>;

function AppContent() {
  const navigate = useNavigate();
  const [runId, setRunId] = useState<string | null>(null);
  const [bookToRead, setBookToRead] = useState<{ bookId?: string; runId?: string } | null>(null);
  const [showTourDialog, setShowTourDialog] = useState(true);
  const { setSteps } = useTour();

  useEffect(() => {
    // Define the steps for the tour
    setSteps([
      {
        selectorId: TOUR_STEP_IDS.START_CREATING_BUTTON,
        path: "/",
        position: "bottom",
        content: (
          <div className="space-y-2">
            <h3 className="font-medium">Начните здесь!</h3>
            <p className="text-sm text-muted-foreground">
              Нажмите эту кнопку, чтобы перейти на страницу создания вашей уникальной книги.
            </p>
          </div>
        ),
      },
      {
        selectorId: TOUR_STEP_IDS.INSTAGRAM_INPUT,
        path: "/generate",
        position: "bottom",
        content: (
          <div className="space-y-2">
            <h3 className="font-medium">Вставьте ссылку</h3>
            <p className="text-sm text-muted-foreground">
              Это основное поле, куда нужно вставить ссылку на Instagram-профиль.
            </p>
          </div>
        ),
      },
      {
        selectorId: TOUR_STEP_IDS.MY_BOOKS_BUTTON,
        path: "/library",
        position: "right",
        content: (
          <div className="space-y-2">
            <h3 className="font-medium">Ваша библиотека</h3>
            <p className="text-sm text-muted-foreground">
              Готовые книги будут ждать вас здесь. Вы сможете их почитать или скачать.
            </p>
          </div>
        ),
      },
    ]);
  }, [setSteps]);

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
      <TourAlertDialog isOpen={showTourDialog} setIsOpen={setShowTourDialog} />
    </>
  );
}

function App() {
  return (
    <TourProvider>
      <AppContent />
    </TourProvider>
  );
}

export default App;
