// Test Component to verify Tailwind is working
import React from 'react';

const TestStyles: React.FC = () => {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold text-blue-600 mb-8">Tailwind CSS Test</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Test Colors */}
        <div className="bg-red-500 text-white p-4 rounded-lg">
          <h3 className="font-bold">Red Background</h3>
          <p>This should be red with white text</p>
        </div>

        <div className="bg-blue-500 text-white p-4 rounded-lg">
          <h3 className="font-bold">Blue Background</h3>
          <p>This should be blue with white text</p>
        </div>

        <div className="bg-green-500 text-white p-4 rounded-lg">
          <h3 className="font-bold">Green Background</h3>
          <p>This should be green with white text</p>
        </div>

        {/* Test Spacing */}
        <div className="bg-yellow-100 p-6 border-2 border-yellow-300 rounded-lg">
          <h3 className="font-bold text-yellow-800">Spacing Test</h3>
          <p className="text-yellow-700">Padding 6, border 2, rounded corners</p>
        </div>

        {/* Test Flexbox */}
        <div className="bg-purple-100 p-4 rounded-lg">
          <h3 className="font-bold text-purple-800 mb-2">Flexbox Test</h3>
          <div className="flex space-x-2">
            <div className="bg-purple-500 text-white px-3 py-1 rounded">Item 1</div>
            <div className="bg-purple-600 text-white px-3 py-1 rounded">Item 2</div>
            <div className="bg-purple-700 text-white px-3 py-1 rounded">Item 3</div>
          </div>
        </div>

        {/* Test Typography */}
        <div className="bg-indigo-100 p-4 rounded-lg">
          <h3 className="font-bold text-indigo-800">Typography Test</h3>
          <p className="text-indigo-600 mb-2">Normal text with indigo color</p>
          <p className="text-sm text-indigo-500">Small text</p>
          <p className="text-lg font-semibold text-indigo-700">Large semibold text</p>
        </div>
      </div>

      {/* Test Buttons */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Button Tests</h2>
        <div className="flex flex-wrap gap-4">
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Primary Button
          </button>
          <button className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
            Secondary Button
          </button>
          <button className="bg-transparent hover:bg-gray-100 text-gray-700 font-bold py-2 px-4 border border-gray-300 rounded">
            Outline Button
          </button>
        </div>
      </div>

      {/* Test Grid */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Grid Test</h2>
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-200 p-4 text-center">1</div>
          <div className="bg-gray-300 p-4 text-center">2</div>
          <div className="bg-gray-400 p-4 text-center">3</div>
          <div className="bg-gray-500 p-4 text-center">4</div>
        </div>
      </div>
    </div>
  );
};

export default TestStyles;