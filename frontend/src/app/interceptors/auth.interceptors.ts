import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('jwtToken'); // Recupera il token dal localStorage

  // Se il token esiste, clona la richiesta e aggiungi l'header Authorization
  if (token) {
    const cloned = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    return next(cloned);
  }

  // Altrimenti, passa la richiesta originale
  return next(req);
};