// src/components/Spinner.tsx
export default function Spinner() {
    return (
      <div className="flex justify-center items-center space-x-2">
        <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <span className="text-sm text-gray-600">Loading...</span>
      </div>
    );
  }
  