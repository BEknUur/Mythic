import { useEffect, useState } from 'react';
import { FlipBook } from './FlipBook';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download } from 'lucide-react';
import { api } from '@/lib/api';
import { useAuth } from '@clerk/clerk-react';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

interface FlipBookReaderProps {
  bookId?: string;
  runId?: string;
  onBack: () => void;
}

// Extracts individual elements that should become pages inside flip-book.
// We look for elements with the `.page` class inside the `#book` container.
function splitHtmlIntoPages(rawHtml: string): string[] {
  const temp = document.createElement('div');
  temp.innerHTML = rawHtml;

  // The backend template wraps each page's content in a <div class="page">
  // inside a main <div id="book"> container.
  const pageElements = temp.querySelectorAll('#book .page');
  const pages: string[] = [];

  if (pageElements.length > 0) {
    pageElements.forEach(el => {
      // We push the innerHTML of the page container, which is the actual content.
      pages.push(el.innerHTML);
    });
  } else {
    // Fallback in case the new structure is not found.
    // Tries to render the whole body, which might not look perfect but is better than nothing.
    const bodyMatch = rawHtml.match(/<body[^>]*>([\s\S]*)<\/body>/i);
    if (bodyMatch && bodyMatch[1]) {
      pages.push(bodyMatch[1]);
    } else {
      pages.push(rawHtml);
    }
  }

  return pages;
}

export function FlipBookReader({ bookId, runId, onBack }: FlipBookReaderProps) {
  const [pages, setPages] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const { getToken } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const token = await getToken();
        let html: string;
        if (runId) {
          html = await api.getBookContent(runId, token || undefined);
        } else if (bookId) {
          const res = await fetch(api.getSavedBookViewUrl(bookId, token || undefined));
          html = await res.text();
        } else {
          throw new Error('Нужен bookId или runId');
        }
        setPages(splitHtmlIntoPages(html));
      } catch (err) {
        toast({ title: 'Ошибка', description: 'Не удалось загрузить книгу', variant: 'destructive' });
      } finally {
        setLoading(false);
      }
    })();
  }, [bookId, runId, getToken, toast]);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-900">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
        <p className="mt-4 text-lg">Загружаем вашу волшебную книгу...</p>
      </div>
    );
  }

  const handleDownloadPdf = async () => {
    try {
      const token = await getToken();
      if (runId) await api.downloadFile(runId, 'book.pdf', token || undefined);
      else if (bookId) await api.downloadSavedBook(bookId, 'book.pdf', token || undefined);
    } catch (error) {
      toast({ title: 'Ошибка', description: 'Не удалось скачать PDF', variant: 'destructive' });
    }
  };

  const pageComponents = pages.map((html, idx) => (
    <div key={idx} className="book-content w-full h-full overflow-auto p-6 bg-white dark:bg-gray-800" dangerouslySetInnerHTML={{ __html: html }} />
  ));

  return (
    <div key={runId || bookId} className="flex-1 flex flex-col bg-gray-100 dark:bg-gray-900">
      <header className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 border-b">
        <Button variant="ghost" onClick={onBack}><ArrowLeft className="mr-2 h-4 w-4" /> В библиотеку</Button>
        <h2 className="text-xl font-semibold">Ваша Книга</h2>
        <Button onClick={handleDownloadPdf} disabled={!runId && !bookId}><Download className="mr-2 h-4 w-4" /> Скачать PDF</Button>
      </header>
      
      {!loading && pages.length > 0 && (
        <div className="flex-1 overflow-auto flex items-center justify-center p-4">
          <FlipBook key={runId || bookId} pages={pageComponents} />
        </div>
      )}

      {!loading && pages.length === 0 && (
        <div className="flex-1 flex items-center justify-center">
          <p>Не удалось загрузить страницы книги.</p>
        </div>
      )}
    </div>
  );
} 