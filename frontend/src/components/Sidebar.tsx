'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, FileText, MessageSquare, ShieldAlert } from 'lucide-react';
import { syncUserRoleFromApi } from '@/lib/auth';
import { useEffect, useState } from 'react';

export default function Sidebar() {
  const pathname = usePathname();
  const [isUserAdmin, setIsUserAdmin] = useState(false);

  useEffect(() => {
    syncUserRoleFromApi().then((role) => setIsUserAdmin(role === 'admin'));
  }, []);

  const links = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/documents', label: 'Documents', icon: FileText },
    { href: '/chat', label: 'Chat Assistant', icon: MessageSquare },
  ];

  if (isUserAdmin) {
    links.push({ href: '/admin', label: 'Admin Panel', icon: ShieldAlert });
  }

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col min-h-screen">
      <div className="p-6 border-b border-slate-200">
        <h2 className="text-xl font-bold text-blue-600 flex items-center gap-2">
          <ShieldAlert className="w-6 h-6" /> DocuGuard AI
        </h2>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700 font-medium'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <Icon className="w-5 h-5" />
              {link.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
