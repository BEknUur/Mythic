import { Instagram, Send } from 'lucide-react';

const TikTokIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M12.528 8.007a2.5 2.5 0 1 1-5.001-0c0-1.803 1.156-3.372 2.854-3.837.24-.066.49-.098.747-.098v5.928Z" />
    <path d="M12.528 8.007V1.99a2.5 2.5 0 1 0-5 0v10.53a2.5 2.5 0 1 0 5 0V8.007Z" />
    <path d="M18.03 12.527a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Z" />
  </svg>
);

export function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200">
      <div className="container mx-auto px-6 py-8">
        <div className="flex flex-col items-center justify-between space-y-4 md:flex-row md:space-y-0">
          <p className="text-sm text-gray-600">
            © {new Date().getFullYear()} Mythic. Все права защищены.
          </p>
          <div className="flex space-x-4">
            <a href="https://www.instagram.com/mythic_aii/" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-gray-900">
              <Instagram className="h-6 w-6" />
            </a>
            <a href="https://www.tiktok.com/@mythicaai?_t=ZM-8xRdRje7ZIs&_r=1" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-gray-900">
              <TikTokIcon className="h-6 w-6" />
            </a>
            <a href="https://www.threads.com/@ualikhaanuly?igshid=NTc4MTIwNjQ2YQ==" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-gray-900">
              <Send className="h-6 w-6" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
} 