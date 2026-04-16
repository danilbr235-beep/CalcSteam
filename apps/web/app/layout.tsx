import { PageHeader } from '@/components/PageHeader';
import { Providers } from '@/components/Providers';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-100 text-slate-900">
        <Providers>
          <div className="min-h-screen">
            <PageHeader />
            {children}
          </div>
        </Providers>
      </body>
    </html>
  );
}
