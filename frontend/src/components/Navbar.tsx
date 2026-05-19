'use client';
import { LogOut, User } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { removeAuthToken } from '@/lib/auth';

export default function Navbar() {
  const router = useRouter();

  const handleLogout = () => {
    removeAuthToken();
    router.push('/login');
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <h1 className="text-lg font-semibold text-slate-800">Workspace</h1>
      <div className="flex items-center gap-4">
        <button className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors">
          <User className="w-5 h-5" />
          <span className="text-sm font-medium">Profile</span>
        </button>
        <button 
          onClick={handleLogout}
          className="flex items-center gap-2 text-red-600 hover:text-red-700 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="text-sm font-medium">Logout</span>
        </button>
      </div>
    </header>
  );
}
