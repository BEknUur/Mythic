import React from 'react';
import { HumorPage } from './HumorPage';
import { RomanticPage } from './RomanticPage';
import { FantasyPage } from './FantasyPage';

export function StyleTestPage() {
  const testData = {
    title: "Тестовая глава",
    text: "Это тестовый текст для демонстрации разных стилей страниц. Здесь может быть любой контент, который будет отображаться в соответствии с выбранным стилем.",
    image: "https://via.placeholder.com/400x300/ff6b6b/ffffff?text=Test+Image",
    caption: "Тестовое изображение"
  };

  return (
    <div className="p-8 space-y-8">
      <h1 className="text-3xl font-bold text-center mb-8">Демонстрация стилей страниц</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Юмористический стиль */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-center">Юмористический стиль</h2>
          <div className="w-full h-96 border rounded-lg overflow-hidden">
            <HumorPage
              number={1}
              title={testData.title}
              text={testData.text}
              image={testData.image}
              caption={testData.caption}
            />
          </div>
        </div>

        {/* Романтический стиль */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-center">Романтический стиль</h2>
          <div className="w-full h-96 border rounded-lg overflow-hidden">
            <RomanticPage
              number={1}
              title={testData.title}
              text={testData.text}
              image={testData.image}
              caption={testData.caption}
            />
          </div>
        </div>

        {/* Фэнтезийный стиль */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-center">Фэнтезийный стиль</h2>
          <div className="w-full h-96 border rounded-lg overflow-hidden">
            <FantasyPage
              number={1}
              title={testData.title}
              text={testData.text}
              image={testData.image}
              caption={testData.caption}
            />
          </div>
        </div>
      </div>
    </div>
  );
} 