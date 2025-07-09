import { FlipBook } from './FlipBook';

export function FlipBookPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">Демо книги с эффектом перелистывания</h1>
      <FlipBook />
    </div>
  );
} 