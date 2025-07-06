import { Lock } from 'lucide-react';

interface ComingSoonPageProps {
  title: string;
  description: string;
}

export function ComingSoonPage({ title, description }: ComingSoonPageProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] text-center p-8">
      <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-6">
        <Lock className="h-8 w-8 text-gray-400 dark:text-gray-500" />
      </div>
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-50 mb-3">{title}</h1>
      <p className="text-lg text-gray-500 dark:text-gray-400 max-w-md">
        {description}
      </p>
    </div>
  );
} 