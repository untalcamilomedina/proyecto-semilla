import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Rutas públicas que no requieren autenticación
const publicPaths = ['/login', '/register', '/', '/api/health'];

// Rutas que requieren autenticación
const protectedPaths = ['/dashboard'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Obtener el token de las cookies
  const token = request.cookies.get('access_token')?.value;
  
  // Verificar si la ruta actual es pública
  const isPublicPath = publicPaths.some(path => pathname === path || pathname.startsWith(`${path}/`));
  
  // Verificar si la ruta actual es protegida
  const isProtectedPath = protectedPaths.some(path => pathname === path || pathname.startsWith(`${path}/`));
  
  // Si es una ruta protegida y no hay token, redirigir al login
  if (isProtectedPath && !token) {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    url.searchParams.set('from', pathname);
    return NextResponse.redirect(url);
  }
  
  // Si el usuario está autenticado y trata de acceder al login o register, redirigir al dashboard
  if (token && (pathname === '/login' || pathname === '/register')) {
    const url = request.nextUrl.clone();
    url.pathname = '/dashboard';
    return NextResponse.redirect(url);
  }
  
  // Continuar con la solicitud
  return NextResponse.next();
}

// Configurar las rutas donde se aplicará el middleware
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api/health (health check endpoints)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public|.*\\..*|api/health).*)',
  ],
};