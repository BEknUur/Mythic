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
import { Textarea } from '@/components/ui/textarea';

interface BookReaderProps {
  bookId?: string;
  runId?: string;
  onBack: () => void;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  suggestion?: AISuggestion;
  error?: string;
}

interface AISuggestion {
  variant: number;
  original: string;
  text: string;
  status?: 'pending' | 'accepted' | 'denied';
}

interface EditSession {
  fragment: string;
  variantIndex: number;
  maxVariants: number;
}

export function BookReader({ bookId, runId, onBack }: BookReaderProps) {
  const [chapters, setChapters] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isAiResponding, setIsAiResponding] = useState(false);
  const [currentEditSession, setCurrentEditSession] = useState<EditSession | null>(null);
  
  const bookContentRef = useRef<HTMLDivElement>(null);
  const selectionRangeRef = useRef<Range | null>(null);
  const selectedChapterRef = useRef<number>(0);
  const { getToken } = useAuth();
  const { toast } = useToast();

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

  // Выделение текста в главе
  const handleTextSelectedFromChapter = (idx: number, range: Range, text: string) => {
    if (text.trim().length < 2) return; // Игнорируем короткие выделения
    selectionRangeRef.current = range;
    selectedChapterRef.current = idx;
    
    // Больше не предзаполняем поле ввода автоматически
    // Просто сохраняем информацию о выделении для использования в чате
  };

  // Отправка сообщения в чат
  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault(); // Предотвращаем перезагрузку страницы
    }
    
    if (!chatInput.trim()) return;
    
    setIsAiResponding(true);
    
    // Создаем или обновляем сессию редактирования
    let editSession = currentEditSession;
    if (selectionRangeRef.current) {
      const selectedText = selectionRangeRef.current.toString();
      if (selectedText && selectedText.trim().length > 0) {
        editSession = {
          fragment: selectedText,
          variantIndex: currentEditSession?.fragment === selectedText ? 
            (currentEditSession.variantIndex + 1) : 1,
          maxVariants: 3
        };
        setCurrentEditSession(editSession);
      }
    }
    
    // Формируем сообщение пользователя
    let messageContent = chatInput;
    if (editSession) {
      messageContent = `Фрагмент: "${editSession.fragment}"\n\nЗапрос: ${chatInput}`;
    }
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: messageContent
    };
    
    const currentHistory = [...chatHistory, userMessage];
    setChatHistory(currentHistory);
    setChatInput(""); // Очищаем поле ввода

    // Формируем контекст для AI
    const apiMessages = currentHistory.map(({ id, suggestion, error, ...msg }) => msg);

    // Добавляем системный промпт В ЗАВИСИМОСТИ ОТ КОНТЕКСТА
    let systemContent = "";
    if(selectionRangeRef.current) {
        let contextChapter = chapters[selectedChapterRef.current];
        
        // Ограничиваем размер главы, чтобы избежать превышения лимита токенов
        const maxChapterLength = 8000; // примерно 2000 токенов
        if (contextChapter.length > maxChapterLength) {
            contextChapter = contextChapter.substring(0, maxChapterLength) + "...\n[Глава обрезана для экономии токенов]";
        }
        
        systemContent = `Вы — AI-Редактор книги. Ваш единственный навык — предлагать улучшения выделенного фрагмента текста книги.

Правила:
1. Никогда не отвечайте на вопросы вне области редактирования (спорт, погода, политика, шутки и т.д.).
2. Запрещены любые нецензурные выражения.
3. При получении фрагмента текста предлагайте **только один** вариант улучшения в формате:

[SUGGESTION]
Оригинал: <точный оригинальный текст>
Вариант ${editSession?.variantIndex || 1}: <ваш вариант>

4. Всегда строго сохраняйте исходный контекст и смысл.
5. Делайте текст более выразительным, но читаемым.

Контекст книги для понимания стиля:\n\n---\n\n${contextChapter}\n\n---\n

Отвечайте только одним вариантом в указанном формате.`;
    } else {
        systemContent = `Вы — AI-Редактор книги. Ваш единственный навык — предлагать улучшения текста книги.

Правила:
1. Никогда не отвечайте на вопросы вне области редактирования (спорт, погода, политика, шутки и т.д.).
2. Запрещены любые нецензурные выражения.
3. При получении фрагмента текста предлагайте **только один** вариант улучшения в формате:

[SUGGESTION]
Оригинал: <точный оригинальный текст>
Вариант ${editSession?.variantIndex || 1}: <ваш вариант>

4. Если текст для редактуры не предоставлен, отвечайте: "Пожалуйста, скопируйте и вставьте фрагмент текста для улучшения"
5. Всегда строго сохраняйте исходный контекст и смысл.

Отвечайте только одним вариантом в указанном формате.`;
    }

    const systemPrompt = {
        role: "system",
        content: systemContent
    };

    try {
        const token = await getToken();
        const response = await fetch(api.getEditChatUrl(), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ messages: [systemPrompt, ...apiMessages] })
        });

        if (!response.body) throw new Error("No response body");
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantResponse = "";

        // Добавляем пустое сообщение ассистента для стриминга
        setChatHistory(prev => [...prev, { id: Date.now().toString(), role: 'assistant', content: '' }]);

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            assistantResponse += chunk;
            
            setChatHistory(prev => {
                const newHistory = [...prev];
                if (newHistory[newHistory.length - 1].role === 'assistant') {
                    newHistory[newHistory.length - 1].content = assistantResponse;
                } else {
                    newHistory.push({ id: Date.now().toString(), role: 'assistant', content: assistantResponse });
                }
                return newHistory;
            });
        }

        // Парсим финальный ответ на наличие предложений
        setChatHistory(prev => parseSuggestions(prev));

    } catch (error) {
        console.error('Ошибка в работе AI чата:', error);
        toast({ title: 'Ошибка AI', description: 'Не удалось связаться с ассистентом.', variant: 'destructive' });
    } finally {
        setIsAiResponding(false);
        selectionRangeRef.current = null; // Сбрасываем выделение после обработки
    }
  };
  
  const parseSuggestions = (messages: ChatMessage[]): ChatMessage[] => {
      return messages.map(msg => {
          if (msg.role === 'assistant' && msg.content) {
              // Ищем паттерн [SUGGESTION] в тексте
              const suggestionMatch = msg.content.match(/\[SUGGESTION\]([\s\S]*?)(?=\[|$)/);
              if (suggestionMatch) {
                  const suggestionText = suggestionMatch[1].trim();
                  
                  // Парсим Оригинал и Вариант
                  const originalMatch = suggestionText.match(/Оригинал:\s*(.*?)(?=\n|$)/);
                  const variantMatch = suggestionText.match(/Вариант\s+(\d+):\s*([\s\S]*?)(?=\n|$)/);
                  
                  if (originalMatch && variantMatch) {
                      const original = originalMatch[1].trim();
                      const variantNumber = parseInt(variantMatch[1]);
                      const text = variantMatch[2].trim();
                      
                      return {
                          ...msg,
                          content: msg.content.replace(/\[SUGGESTION\][\s\S]*/, "").trim() || `Вариант ${variantNumber} готов:`,
                          suggestion: {
                              variant: variantNumber,
                              original,
                              text,
                              status: 'pending' as const
                          }
                      };
                  }
              }
          }
          return msg;
      });
  };

  // Отклонение предложения AI
  const handleDenySuggestion = async (suggestion: AISuggestion) => {
    // Отмечаем текущее предложение как отклоненное
    setChatHistory(prev => prev.map(msg => ({
      ...msg,
      suggestion: msg.suggestion && msg.suggestion.variant === suggestion.variant ? 
        { ...msg.suggestion, status: 'denied' as const } : msg.suggestion
    })));

    // Проверяем, можем ли запросить следующий вариант
    if (currentEditSession && currentEditSession.variantIndex < currentEditSession.maxVariants) {
      // Автоматически запрашиваем следующий вариант
      setTimeout(() => {
        setChatInput("Предложите другой вариант");
        handleSendMessage();
      }, 500);
    } else {
      // Больше вариантов нет
      const finalMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `❌ Больше вариантов нет (показано ${currentEditSession?.maxVariants || 3}). Выберите один из предложенных или оставьте как есть.`
      };
      setChatHistory(prev => [...prev, finalMessage]);
      setCurrentEditSession(null);
    }
  };

  // Принятие предложения AI
  const handleAcceptSuggestion = async (suggestion: AISuggestion) => {
    // Нормализация текста для более точного поиска
    const normalizeText = (text: string) => text.replace(/\s+/g, ' ').trim();
    
    let success = false;
    let updatedChapters = [...chapters];
    
    // Сначала пробуем точное совпадение
    for (let i = 0; i < updatedChapters.length; i++) {
      if (updatedChapters[i].includes(suggestion.original)) {
        updatedChapters[i] = updatedChapters[i].replace(suggestion.original, suggestion.text);
        success = true;
        break;
      }
    }
    
    // Если не найдено, пробуем нормализованный поиск
    if (!success) {
      const normalizedOriginal = normalizeText(suggestion.original);
      for (let i = 0; i < updatedChapters.length; i++) {
        const normalizedChapter = normalizeText(updatedChapters[i]);
        const index = normalizedChapter.indexOf(normalizedOriginal);
        if (index !== -1) {
          // Находим позицию в оригинальном тексте
          const beforeText = updatedChapters[i].substring(0, index);
          const afterText = updatedChapters[i].substring(index + suggestion.original.length);
          updatedChapters[i] = beforeText + suggestion.text + afterText;
          success = true;
          break;
        }
      }
    }

    if (success) {
        setChapters(updatedChapters);
        
        // Обновляем статус предложения в чате
        setChatHistory(prev => prev.map(msg => ({
          ...msg,
          suggestion: msg.suggestion && msg.suggestion.variant === suggestion.variant ? 
            { ...msg.suggestion, status: 'accepted' as const } : msg.suggestion
        })));
        
        // Сбрасываем сессию редактирования
        setCurrentEditSession(null);
        
        toast({ 
          title: "✅ Изменение применено", 
          description: `Заменено: "${suggestion.original.substring(0, 50)}${suggestion.original.length > 50 ? '...' : ''}"` 
        });

        // Сохраняем на сервере
        try {
            const token = await getToken();
            const fullHtml = `<div class="chapter">${updatedChapters.join('</div><div class="chapter">')}</div>`;
            await api.updateBookContent(bookId || runId || '', fullHtml, token || undefined);
        } catch (error) {
            console.error('Ошибка сохранения книги:', error);
            toast({ title: 'Ошибка сохранения', variant: 'destructive' });
        }
    } else {
        toast({
            variant: "default",
            title: "❌ Текст не найден",
            description: "Не удалось найти оригинальный текст в книге. Попробуйте скопировать фрагмент заново.",
        });
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
        
        <div className="p-8 max-w-4xl mx-auto book-content overflow-y-auto" ref={bookContentRef}>
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
            <h2 className="font-semibold text-lg">AI Редактор</h2>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            📝 Скопируйте текст из книги, вставьте в чат и опишите, как его улучшить
          </p>
        </div>

        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {chatHistory.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-4">✍️</div>
                <p className="font-medium mb-2">Как работать с AI-редактором:</p>
                <div className="text-sm space-y-1 text-left max-w-sm mx-auto">
                  <p>1. Скопируйте фрагмент текста из книги</p>
                  <p>2. Вставьте в поле ниже</p>
                  <p>3. Опишите, как улучшить (например: "сделать более поэтично")</p>
                  <p>4. Выберите понравившийся вариант</p>
                </div>
              </div>
            )}
            
            {chatHistory.map((message) => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`p-3 rounded-lg max-w-[90%] ${message.role === 'user' ? 'bg-violet-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  {message.suggestion && (
                    <div className="mt-3">
                      <div 
                        className={`p-3 rounded-lg border ${
                          message.suggestion.status === 'accepted' ? 'bg-green-50 border-green-200' :
                          message.suggestion.status === 'denied' ? 'bg-red-50 border-red-200' :
                          'bg-white/90 border-violet-200'
                        }`}
                      >
                        <div className="text-xs text-gray-500 mb-1">Оригинал:</div>
                        <p className="text-sm text-gray-600 line-through mb-2">{message.suggestion.original}</p>
                        <div className="text-xs text-gray-500 mb-1">Вариант {message.suggestion.variant}:</div>
                        <p className="text-sm font-medium text-gray-900 mb-3">{message.suggestion.text}</p>
                        
                        {message.suggestion.status === 'pending' && (
                          <div className="flex gap-2">
                            <Button 
                              size="sm" 
                              onClick={() => handleAcceptSuggestion(message.suggestion!)}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              ✅ Применить
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              onClick={() => handleDenySuggestion(message.suggestion!)}
                            >
                              ❌ Отклонить
                            </Button>
                          </div>
                        )}
                        
                        {message.suggestion.status === 'accepted' && (
                          <div className="text-green-700 font-medium">✅ Применено</div>
                        )}
                        
                        {message.suggestion.status === 'denied' && (
                          <div className="text-red-700 font-medium">❌ Отклонено</div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isAiResponding && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                  <span className="text-sm text-gray-600 ml-2">AI анализирует текст...</span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
        
        <form onSubmit={handleSendMessage} className="p-4 border-t bg-white">
          <div className="flex items-center gap-2">
            <Textarea
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Вставьте текст и опишите, как его улучшить..."
              className="flex-1 resize-none"
              rows={2}
            />
            <Button type="submit" disabled={isAiResponding || !chatInput.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            💡 Пример: "Она была красивая → сделать более поэтично"
          </p>
        </form>
      </div>
    </div>
  );
}