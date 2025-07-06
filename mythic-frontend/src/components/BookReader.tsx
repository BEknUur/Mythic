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
import { Filter } from 'bad-words';

interface BookReaderProps {
  bookId?: string;
  runId?: string;
  onBack: () => void;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  suggestions?: string[];
  originalFragment?: string;
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
  const [selectedRange, setSelectedRange] = useState<Range | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [variantIndex, setVariantIndex] = useState(0);
  
  const bookContentRef = useRef<HTMLDivElement>(null);
  const selectionRangeRef = useRef<Range | null>(null);
  const selectedChapterRef = useRef<number>(0);
  const { getToken } = useAuth();
  const { toast } = useToast();

  // Инициализируем фильтр нецензурной лексики один раз
  const filter = new Filter();

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

  // Обработчик выделения текста мышкой
  const handleMouseUp = () => {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return;
    
    const range = sel.getRangeAt(0);
    const selectedText = range.toString().trim();
    
    // Проверяем, что выделение внутри нашего контейнера и не пустое
    if (
      !range.collapsed &&
      selectedText.length > 2 &&
      bookContentRef.current?.contains(range.commonAncestorContainer)
    ) {
      setSelectedRange(range.cloneRange());
      
      // Автоматически запрашиваем предложения
      fetchSuggestions(selectedText);
      
      // Убираем визуальное выделение
      sel.removeAllRanges();
    }
  };

  // Запрос предложений к AI
  const fetchSuggestions = async (fragment: string) => {
    try {
      setIsAiResponding(true);
      const token = await getToken();
      
      const systemPrompt = `Вы — AI-Редактор книги. Ваш единственный навык — предлагать улучшения текста.

Правила:
1. Работайте ТОЛЬКО с редактированием текста книги
2. Никакого оффтопа (спорт, погода, политика)
3. Запрещена нецензурная лексика
4. Возвращайте JSON: {"suggestions": ["вариант1", "вариант2", "вариант3"]}
5. Всегда 3 варианта улучшения
6. Сохраняйте исходный смысл

Фрагмент для улучшения: "${fragment}"`;

      const response = await fetch(api.getEditChatUrl(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: `Улучшите этот фрагмент: "${fragment}"` }
          ]
        })
      });

      if (!response.body) throw new Error("No response body");
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantResponse = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        assistantResponse += decoder.decode(value, { stream: true });
      }

      // Парсим JSON ответ
      try {
        const jsonMatch = assistantResponse.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          if (parsed.suggestions && Array.isArray(parsed.suggestions)) {
            setSuggestions(parsed.suggestions);
            setVariantIndex(0);
            
            // Добавляем в историю чата
            const suggestionMessage: ChatMessage = {
              id: Date.now().toString(),
              role: 'assistant',
              content: `✨ Предлагаю ${parsed.suggestions.length} варианта улучшения:`,
              suggestions: parsed.suggestions,
              originalFragment: fragment
            };
            setChatHistory(prev => [...prev, suggestionMessage]);
          }
        }
      } catch (e) {
        console.error('Ошибка парсинга JSON:', e);
        toast({ title: 'Ошибка', description: 'Не удалось обработать ответ AI', variant: 'destructive' });
      }
    } catch (error) {
      console.error('Ошибка запроса предложений:', error);
      toast({ title: 'Ошибка AI', description: 'Не удалось получить предложения', variant: 'destructive' });
    } finally {
      setIsAiResponding(false);
    }
  };

 
  const handleTextSelectedFromChapter = (idx: number, range: Range, text: string) => {
    if (text.trim().length < 2) return; 
    selectionRangeRef.current = range;
    selectedChapterRef.current = idx;
    
  
  };

 
  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }
    
    if (!chatInput.trim()) return;
    
    setIsAiResponding(true);
    
    
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
    const apiMessages = currentHistory.map(({ id, suggestions, error, ...msg }) => msg);

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
                          content: `✨ Вариант ${variantNumber} готов:`,
                          suggestions: [text], // Массив с одним вариантом
                          originalFragment: original
                      };
                  }
              }
          }
          return msg;
      });
  };

  // Принятие предложения AI через Range API
  const handleAcceptSuggestion = async (messageId: string, suggestionIndex: number) => {
    const message = chatHistory.find(m => m.id === messageId);
    if (!message || !message.suggestions || !selectedRange) return;
    
    const suggestion = message.suggestions[suggestionIndex];
    
    try {
      // Удаляем выделенный контент
      selectedRange.deleteContents();
      
      // Вставляем новый текстовый узел
      const textNode = document.createTextNode(suggestion);
      selectedRange.insertNode(textNode);
      
      // Обновляем состояние chapters из DOM
      if (bookContentRef.current) {
        const chapterElements = bookContentRef.current.querySelectorAll('.chapter');
        const updatedChapters: string[] = [];
        chapterElements.forEach(el => {
          updatedChapters.push(el.innerHTML);
        });
        
        if (updatedChapters.length > 0) {
          setChapters(updatedChapters);
        } else {
          // Если нет отдельных глав, обновляем весь контент
          setChapters([bookContentRef.current.innerHTML]);
        }
      }
      
      // Убираем предложения из чата (закрываем карточку)
      setChatHistory(prev => prev.map(msg => 
        msg.id === messageId ? { ...msg, suggestions: undefined } : msg
      ));
      
      // Сбрасываем состояние
      setSelectedRange(null);
      setSuggestions([]);
      setVariantIndex(0);
      
      toast({ 
        title: "✅ Изменение применено", 
        description: `Текст успешно заменен на: "${suggestion.substring(0, 50)}${suggestion.length > 50 ? '...' : ''}"` 
      });

      // Сохраняем на сервере
      try {
        const token = await getToken();
        const fullHtml = bookContentRef.current?.innerHTML || '';
        await api.updateBookContent(bookId || runId || '', fullHtml, token || undefined);
      } catch (error) {
        console.error('Ошибка сохранения книги:', error);
        toast({ title: 'Ошибка сохранения', variant: 'destructive' });
      }
    } catch (error) {
      console.error('Ошибка применения предложения:', error);
      toast({
        variant: "destructive",
        title: "❌ Ошибка применения",
        description: "Не удалось применить изменение. Попробуйте выделить текст заново.",
      });
    }
  };

  // Отклонение предложения AI - показываем следующий вариант
  const handleDenySuggestion = async (messageId: string) => {
    const message = chatHistory.find(m => m.id === messageId);
    if (!message || !message.suggestions) return;

    const currentIndex = variantIndex;
    const nextIndex = currentIndex + 1;
    
    if (nextIndex < message.suggestions.length) {
      // Показываем следующий вариант
      setVariantIndex(nextIndex);
      
      // Обновляем сообщение в чате
      setChatHistory(prev => prev.map(msg => 
        msg.id === messageId ? { 
          ...msg, 
          content: `✨ Вариант ${nextIndex + 1} из ${message.suggestions!.length}:` 
        } : msg
      ));
    } else {
      // Больше вариантов нет - убираем карточку
      setChatHistory(prev => prev.map(msg => 
        msg.id === messageId ? { ...msg, suggestions: undefined } : msg
      ));
      
      const finalMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `❌ Больше вариантов нет (показано ${message.suggestions.length}). Попробуйте выделить другой фрагмент.`
      };
      setChatHistory(prev => [...prev, finalMessage]);
      
      // Сбрасываем состояние
      setSelectedRange(null);
      setSuggestions([]);
      setVariantIndex(0);
    }
  };

  /*
   * ВСТАВКА ТЕКСТА В DOM + СОХРАНЕНИЕ
   * Выполняет реальное изменение контента книги и сбрасывает локальный стейт
   */
  const doInsert = async (cleanText: string) => {
    if (!selectedRange) {
      toast({
        variant: "destructive",
        title: "❌ Ошибка",
        description: "Сначала выделите текст, который хотите заменить.",
      });
      return;
    }

    try {
      // 1. Обновляем DOM через Range API
      selectedRange.deleteContents();
      selectedRange.insertNode(document.createTextNode(cleanText));

      // 2. Синхронизируем React-состояние глав
      if (bookContentRef.current) {
        const chapterElements = bookContentRef.current.querySelectorAll('.chapter');
        const updatedChapters: string[] = [];
        chapterElements.forEach(el => updatedChapters.push(el.innerHTML));
        setChapters(updatedChapters.length > 0 ? updatedChapters : [bookContentRef.current.innerHTML]);
      }

      // 3. Сохраняем новое содержимое на сервер
      const token = await getToken();
      const fullHtml = bookContentRef.current?.innerHTML || '';
      await api.updateBookContent(bookId || runId || '', fullHtml, token || undefined);

      toast({ 
        title: "✅ Изменение применено", 
        description: "Текст успешно обновлен." 
      });
    } catch (error) {
      console.error('Ошибка применения или сохранения:', error);
      toast({
        variant: "destructive",
        title: "❌ Ошибка",
        description: "Не удалось применить изменение.",
      });
    } finally {
      // 4. Сброс локального состояния
      setSelectedRange(null);
      setSuggestions([]);
      setVariantIndex(0);
    }
  };

  /*
   * Проверка текста (bad-words + Moderation API) и делегирование в doInsert
   */
  const applyTextChange = async (rawText: string) => {
    const textToInsert = rawText.trim();
    if (!textToInsert) return;

    // 1. Локальный фильтр нецензурной лексики
    if (filter.isProfane(textToInsert)) {
      toast({
        variant: "destructive",
        title: "🚫 Недопустимый контент",
        description: "Текст содержит запрещённые слова. Пожалуйста, исправьте его.",
      });
      return;
    }

    // 2. Дополнительная проверка через Moderation API
    try {
      const token = await getToken();
      const moderationResult = await api.moderateText(textToInsert, token || undefined);
      if (moderationResult.flagged) {
        toast({
          variant: "destructive",
          title: "🚫 Недопустимый контент",
          description: "Этот текст не прошёл модерацию. Попробуйте другой вариант.",
        });
        return;
      }
    } catch (err) {
      // Если сервис недоступен, продолжим полагаясь только на локальный фильтр
      console.error('Ошибка запроса модерации:', err);
    }

    // 3. Вставляем текст
    await doInsert(textToInsert);
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
        
        <div className="p-8 max-w-4xl mx-auto book-content overflow-y-auto" ref={bookContentRef} onMouseUp={handleMouseUp}>
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
            🖱️ Выделите текст мышкой для получения предложений по улучшению.
          </p>
        </div>

        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {chatHistory.length === 0 && !selectedRange && (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-4">✍️</div>
                <p className="font-medium mb-2">Как работать с AI-редактором:</p>
                <div className="text-sm space-y-1 text-left max-w-sm mx-auto">
                  <p>1. Выделите фрагмент текста мышкой.</p>
                  <p>2. Появится карточка с вариантами от AI.</p>
                  <p>3. Выберите лучший или впишите свой.</p>
                  <p>4. Изменения применятся сразу в книгу.</p>
                </div>
              </div>
            )}
            
            {chatHistory.map((message) => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`p-3 rounded-lg max-w-[90%] whitespace-pre-wrap ${message.role === 'user' ? 'bg-violet-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                  {message.content}
                </div>
              </div>
            ))}

            {isAiResponding && !selectedRange && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3 flex items-center">
                  <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                  <span className="text-sm text-gray-600 ml-2">AI генерирует варианты...</span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
        
        {/* Чат инпут остаётся для общих вопросов */}
        <form onSubmit={handleSendMessage} className="p-4 border-t bg-white">
          <div className="flex items-center gap-2">
            <Textarea
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Здесь можно задать общий вопрос AI..."
              className="flex-1 resize-none"
              rows={1}
            />
            <Button type="submit" disabled={isAiResponding}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </form>
      </div>

      {/* Плавающая карточка для редактирования */}
      {selectedRange && (
        <div className="fixed bottom-5 right-5 z-50 w-96 bg-white border border-gray-300 rounded-lg shadow-2xl p-4 animate-in fade-in-5 slide-in-from-bottom-2">
          <Button 
            variant="ghost" 
            size="icon" 
            className="absolute top-2 right-2 h-7 w-7" 
            onClick={() => {
              setSelectedRange(null);
              setSuggestions([]);
            }}
          >
            <X className="h-4 w-4" />
          </Button>

          <div className="text-sm font-medium mb-3">Редактирование фрагмента</div>

          {isAiResponding ? (
            <div className="flex items-center text-sm text-gray-500">
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              Ищем лучшие варианты...
            </div>
          ) : suggestions.length > 0 ? (
            <div className="mb-3">
              <div className="text-xs text-gray-500 mb-2">Вариант {variantIndex + 1} из {suggestions.length}:</div>
              <p className="text-sm font-medium p-3 bg-blue-50 rounded border border-blue-200">
                {suggestions[variantIndex]}
              </p>
              <div className="flex gap-2 mt-2">
                <Button size="sm" onClick={() => applyTextChange(suggestions[variantIndex])} className="bg-green-600 hover:bg-green-700 text-white">
                  ✅ Применить
                </Button>
                <Button size="sm" variant="outline" onClick={() => setVariantIndex(v => (v + 1) % suggestions.length)}>
                  ➡️ Следующий
                </Button>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-500 mb-3">Нет предложений от AI.</p>
          )}
        </div>
      )}
    </div>
  );
}