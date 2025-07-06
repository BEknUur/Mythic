import { Link } from 'react-router-dom';
import { BookOpen, Instagram, Send, Twitter } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-100">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and About */}
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <BookOpen className="h-7 w-7 text-purple-600" />
              <span className="text-xl font-bold text-gray-900">Mythic AI</span>
            </Link>
            <p className="text-gray-500 text-sm">
              Превращаем ваши цифровые воспоминания в вечные истории.
            </p>
          </div>

          {/* Navigation Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Навигация</h3>
            <ul className="space-y-3">
              <li><Link to="/" className="text-gray-500 hover:text-purple-600 transition-colors">Главная</Link></li>
              <li><Link to="/generate" className="text-gray-500 hover:text-purple-600 transition-colors">Создать книгу</Link></li>
              <li><Link to="/library" className="text-gray-500 hover:text-purple-600 transition-colors">Мои книги</Link></li>
            </ul>
          </div>

          {/* Help Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Помощь</h3>
            <ul className="space-y-3">
              <li><Link to="/help" className="text-gray-500 hover:text-purple-600 transition-colors">FAQ</Link></li>
              <li><a href="mailto:support@mythicai.com" className="text-gray-500 hover:text-purple-600 transition-colors">Поддержка</a></li>
            </ul>
          </div>
          
          {/* Social Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Следите за нами</h3>
            <div className="flex space-x-4">
              <a href="https://www.tiktok.com/@mythica.ai" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-purple-600 transition-colors">
                <Twitter className="h-6 w-6" />
              </a>
              <a href="https://www.instagram.com/mythic_aii/" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-purple-600 transition-colors">
                <Instagram className="h-6 w-6" />
              </a>
              <a href="https://www.threads.com/@mythic_aii" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-purple-600 transition-colors">
                <Send className="h-6 w-6" />
              </a>
            </div>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-100 text-center">
          <p className="text-sm text-gray-500">
            © {new Date().getFullYear()} Mythic AI. Все права защищены.
          </p>
          <div className="flex justify-center mt-4">
            <a href="https://nfactorial.school" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition-colors">
              <span>Backed by</span>
              <div className="flex items-center gap-1.5">
                <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="font-sans text-white font-bold text-xs">n<span className="inline-block -scale-y-100">!</span></span>
                </div>
                <span className="font-semibold">nFactorial</span>
              </div>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
} 