import { Form } from './Form';
import { Footer } from './Footer';

interface GeneratePageProps {
  onStartScrape: (id: string) => void;
}

export function GeneratePage({ onStartScrape }: GeneratePageProps) {
  return (
    <>
      <div className="container mx-auto px-4 py-8">
        <Form onStartScrape={onStartScrape} />
      </div>
      <Footer />
    </>
  );
} 