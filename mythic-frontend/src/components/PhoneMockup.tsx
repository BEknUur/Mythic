import React from 'react';

const previewUrl =
  'https://images.unsplash.com/photo-1519445771041-7394c6ae61bc?auto=format&fit=crop&w=440&q=80';

export function PhoneMockup() {
  return (
    <div className="relative w-[220px] h-[440px] rounded-[28px] bg-white dark:bg-gray-900 shadow-2xl ring-1 ring-gray-200 dark:ring-gray-800 flex justify-center items-center overflow-hidden">
      {/* Screen */}
      <img src={previewUrl} alt="Book preview" className="w-full h-full object-cover" />
     
      <div className="absolute bottom-4 w-24 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full" />
    </div>
  );
} 