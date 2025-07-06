import { Link } from 'react-router-dom';
import { Instagram, Twitter, Linkedin, Heart, AtSign, MessageSquare } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-white dark:bg-gray-950 border-t border-gray-100 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and About */}
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <img src="/logo.png" alt="Mythic AI Logo" className="h-8 w-8" />
              <span className="text-xl font-bold text-gray-900 dark:text-gray-50">Mythic AI</span>
            </Link>
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              Превращаем ваши цифровые воспоминания в вечные истории.
            </p>
          </div>

          {/* Navigation Links */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-50 mb-4">Навигация</h3>
            <ul className="space-y-3">
              <li><Link to="/" className="text-gray-500 dark:text-gray-400 hover:text-purple-600 transition-colors">Главная</Link></li>
              <li><Link to="/generate" className="text-gray-500 dark:text-gray-400 hover:text-purple-600 transition-colors">Создать книгу</Link></li>
              <li><Link to="/library" className="text-gray-500 dark:text-gray-400 hover:text-purple-600 transition-colors">Мои книги</Link></li>
            </ul>
          </div>

          {/* Help Links */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-50 mb-4">Помощь</h3>
            <ul className="space-y-3">
              <li><Link to="/help" className="text-gray-500 dark:text-gray-400 hover:text-purple-600 transition-colors">FAQ</Link></li>
              <li><a href="mailto:support@mythicai.com" className="text-gray-500 dark:text-gray-400 hover:text-purple-600 transition-colors">Поддержка</a></li>
            </ul>
          </div>
          
          {/* Social Links */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-50 mb-4">Следите за нами</h3>
            <div className="flex space-x-4">
              <a href="https://t.me/beknur_10" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                <MessageSquare className="h-6 w-6" />
              </a>
              <a href="https://x.com/ualihanuly60606?s=21" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                <Twitter className="h-6 w-6" />
              </a>
              <a href="https://www.instagram.com/mythic_aii/" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                <Instagram className="h-6 w-6" />
              </a>
              <a href="https://www.threads.com/@ualikhaanuly" className="text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                <AtSign className="h-6 w-6" />
              </a>
              <a href="https://www.linkedin.com/in/beknur-ualikhanuly-039704245/" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                <Linkedin className="h-6 w-6" />
              </a>
            </div>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-100 dark:border-gray-800 text-center">
          <div className="flex justify-center items-center gap-2 mb-4 text-sm text-gray-500 dark:text-gray-400">
            <span>Brought to you with</span>
            <Heart className="h-4 w-4 text-red-500" fill="currentColor" />
            <span>by</span>
            <a href="https://github.com/BEknUur/" target="_blank" rel="noopener noreferrer" className="font-semibold text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
             Beknur4ka
            </a>
          </div>
          
          <div className="flex justify-center mt-8">
            <a href="https://nfactorial.school" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors">
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