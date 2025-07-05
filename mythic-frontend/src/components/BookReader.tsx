import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@clerk/clerk-react';
import { api } from '@/lib/api';
import { 
  ArrowLeft, 
  Send, 
  Check, 
  X, 
  Loader2,
  MessageSquare,
  Copy,
  Sparkles,
  RefreshCw
} from 'lucide-react';
import { ChapterBlock } from './ChapterBlock';

interface BookReaderProps {
  bookId?: string;
  runId?: string;
  onBack: () => void;
}

interface AISuggestion {
  id: string;
  selectedText: string;
  originalContext: string;
  suggestion: string;
  status: 'pending' | 'accepted' | 'rejected';
  timestamp: Date;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  suggestion?: AISuggestion;
}

export function BookReader({ bookId, runId, onBack }: BookReaderProps) {
  const [chapters, setChapters] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedText, setSelectedText] = useState<string>('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentSuggestion, setCurrentSuggestion] = useState<AISuggestion | null>(null);
  
  const bookContentRef = useRef<HTMLDivElement>(null);
  const chatScrollRef = useRef<HTMLDivElement>(null);
  const selectionRangeRef = useRef<Range | null>(null);
  const { getToken } = useAuth();
  const { toast } = useToast();
  const selectedChapterRef = useRef<number>(0);

  // Загрузка содержимого книги
  useEffect(() => {
    loadBookContent();
  }, [bookId, runId]);

  const loadBookContent = async () => {
    try {
      setLoading(true);
      const token = await getToken();
      
      let rawHtml: string;
      if (runId) {
        rawHtml = await api.getBookContent(runId, token || undefined);
      } else if (bookId) {
        // Загрузка сохраненной книги
        const response = await fetch(api.getSavedBookViewUrl(bookId, token || undefined));
        rawHtml = await response.text();
      } else {
        throw new Error('Нужен bookId или runId');
      }
      
      // Берём только контент внутри <body> и вырезаем <style> блоки
      const bodyMatch = rawHtml.match(/<body[^>]*>([\s\S]*)<\/body>/i);
      let bodyContent = bodyMatch ? bodyMatch[1] : rawHtml;
      bodyContent = bodyContent.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');

      // Парсим на главы
      const temp = document.createElement('div');
      temp.innerHTML = bodyContent;
      const chapterEls = temp.querySelectorAll('.chapter');
      if (chapterEls.length) {
        const arr: string[] = [];
        chapterEls.forEach(ch => arr.push(ch.innerHTML));
        setChapters(arr);
      } else {
        setChapters([bodyContent]);
      }
    } catch (error) {
      console.error('Ошибка загрузки книги:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить книгу',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTextSelectedFromChapter = (idx: number, range: Range, text: string) => {
    selectionRangeRef.current = range;
    selectedChapterRef.current = idx;
    setSelectedText(text);
    handleSendToAI(text);
  };

  // Отправка текста в AI
  const handleSendToAI = async (text: string) => {
    if (!text.trim() || isProcessing) return;

    setIsProcessing(true);
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: `Выделен текст: "${text}"`
    };
    
    setChatMessages(prev => [...prev, userMessage]);

    try {
      const token = await getToken();
      const response = await api.getAISuggestion(text, chapters.join(''), token || undefined);
      
      const suggestion: AISuggestion = {
        id: Date.now().toString(),
        selectedText: text,
        originalContext: getContextAroundSelection(text),
        suggestion: response.suggestion,
        status: 'pending',
        timestamp: new Date()
      };

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: response.suggestion,
        suggestion
      };

      setChatMessages(prev => [...prev, aiMessage]);
      setCurrentSuggestion(suggestion);
      
      // Прокрутка к последнему сообщению
      setTimeout(() => {
        chatScrollRef.current?.scrollTo({
          top: chatScrollRef.current.scrollHeight,
          behavior: 'smooth'
        });
      }, 100);
      
    } catch (error) {
      console.error('Ошибка AI:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось получить предложение от AI',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // Получение контекста вокруг выделенного текста
  const getContextAroundSelection = (selectedText: string): string => {
    const contentDiv = bookContentRef.current;
    if (!contentDiv) return selectedText;

    const fullText = contentDiv.innerText;
    const index = fullText.indexOf(selectedText);
    if (index === -1) return selectedText;

    const contextBefore = fullText.substring(Math.max(0, index - 100), index);
    const contextAfter = fullText.substring(index + selectedText.length, index + selectedText.length + 100);
    
    return `...${contextBefore}[${selectedText}]${contextAfter}...`;
  };

  // Принятие предложения AI
  const handleAccept = async (suggestion: AISuggestion) => {
    try {
      const token = await getToken();
      
      let updatedContent = chapters.join('');

      if (selectionRangeRef.current !== null) {
        const chapterIdx = selectedChapterRef.current;
        const chapterContainer = document.querySelector(`[data-chapter-idx="${chapterIdx}"]`) as HTMLElement | null;
        if (chapterContainer && (chapterContainer as any).__applySuggestion) {
          (chapterContainer as any).__applySuggestion(suggestion.suggestion, suggestion.selectedText);
          updatedContent = chapters.map((c, i) => (i === chapterIdx ? chapterContainer.innerHTML : c)).join('');
          setChapters(prev => prev.map((c,i)=> i===chapterIdx ? chapterContainer.innerHTML : c));
        }
      } else {
        updatedContent = chapters.join('');
      }
      
      await api.updateBookContent(
        bookId || runId || '',
        updatedContent,
        token || undefined
      );

      // Обновляем локальное содержимое
      setChapters(prev => prev.map(c => updatedContent.includes(c) ? c : updatedContent));
      
      // Обновляем статус предложения
      setChatMessages(prev =>
        prev.map(msg =>
          msg.suggestion?.id === suggestion.id
            ? { ...msg, suggestion: { ...msg.suggestion, status: 'accepted' } }
            : msg
        )
      );

      toast({
        title: 'Изменения применены',
        description: 'Книга успешно обновлена',
      });
      
      // Сброс селекции, чтобы пользователь видел чистую страницу
      const sel = window.getSelection();
      if (sel) sel.removeAllRanges();
      
    } catch (error) {
      console.error('Ошибка применения изменений:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось применить изменения',
        variant: 'destructive',
      });
    }
  };

  // Отклонение предложения AI и запрос нового
  const handleDeny = async (suggestion: AISuggestion) => {
    // Обновляем статус предложения
    setChatMessages(prev =>
      prev.map(msg =>
        msg.suggestion?.id === suggestion.id
          ? { ...msg, suggestion: { ...msg.suggestion, status: 'rejected' } }
          : msg
      )
    );

    // Запрашиваем новое предложение
    handleSendToAI(suggestion.selectedText);
  };

  // Копирование текста
  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: 'Скопировано',
      description: 'Текст скопирован в буфер обмена',
    });
  };

  const insertSuggestionIntoRange = (range: Range, text: string, selected: string) => {
    // Пытаемся обновить ближайший блочный элемент (h1, p, li, etс.)
    let target: HTMLElement | null = null;

    if (range.startContainer.nodeType === Node.TEXT_NODE) {
      target = range.startContainer.parentElement;
    } else if (range.startContainer instanceof HTMLElement) {
      target = range.startContainer;
    }

    if (target && target.tagName !== 'STYLE') {
      const regex = new RegExp(selected.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
      target.textContent = (target.textContent || '').replace(regex, text);
    } else if (target) {
      // Если попали в <style>, ищем родителя выше, не STYLE и не HEAD
      let p = target.parentElement;
      while (p && (p.tagName === 'STYLE' || p.tagName === 'HEAD')) {
        p = p.parentElement;
      }
      if (p) {
        const regex = new RegExp(selected.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
        p.textContent = (p.textContent || '').replace(regex, text);
        return;
      }
    } else {
      // Fallback – удаляем диапазон и вставляем как текст
      range.deleteContents();
      range.insertNode(document.createTextNode(text));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-600" />
          <p className="text-gray-600">Загружаем вашу книгу...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Левая часть - Книга */}
      <div className="flex-1 bg-white overflow-y-auto">
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={onBack}
              className="text-gray-700 hover:text-black"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Назад
            </Button>
            <div className="text-sm text-gray-500">
              Выделите текст для получения AI предложений
            </div>
          </div>
        </div>
        
        <div className="p-8 max-w-4xl mx-auto book-content overflow-y-auto">
          {chapters.map((html, idx)=>(
            <ChapterBlock
              key={idx}
              idx={idx}
              html={html}
              onUpdate={(i,newHtml)=> setChapters(prev=> prev.map((c,j)=> j===i? newHtml: c))}
              onTextSelected={handleTextSelectedFromChapter}
            />
          ))}
        </div>
      </div>

      {/* Правая часть - AI Чат */}
      <div className="w-96 bg-white border-l border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-violet-600" />
            <h2 className="font-semibold text-lg">AI Помощник</h2>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Выделите текст в книге для получения предложений
          </p>
        </div>

        <ScrollArea className="flex-1 p-4" ref={chatScrollRef}>
          {chatMessages.length === 0 ? (
            <div className="text-center py-8">
              <Sparkles className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-sm">
                Выделите любой текст в книге,<br />
                и я предложу улучшения
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {chatMessages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.type === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg p-3 ${
                      message.type === 'user'
                        ? 'bg-violet-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    
                    {message.suggestion && message.suggestion.status === 'pending' && (
                      <div className="mt-3 pt-3 border-t border-gray-200 flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleAccept(message.suggestion!)}
                          className="bg-green-600 hover:bg-green-700 text-white"
                        >
                          <Check className="h-4 w-4 mr-1" />
                          Accept
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeny(message.suggestion!)}
                          className="border-red-600 text-red-600 hover:bg-red-50"
                        >
                          <X className="h-4 w-4 mr-1" />
                          Deny
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleCopy(message.suggestion!.suggestion)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                    
                    {message.suggestion && message.suggestion.status === 'accepted' && (
                      <div className="mt-2 text-xs text-green-200">
                        ✓ Применено
                      </div>
                    )}
                    
                    {message.suggestion && message.suggestion.status === 'rejected' && (
                      <div className="mt-2 text-xs text-red-200">
                        ✗ Отклонено
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                  </div>
                </div>
              )}
            </div>
          )}
        </ScrollArea>
      </div>
    </div>
  );
} 