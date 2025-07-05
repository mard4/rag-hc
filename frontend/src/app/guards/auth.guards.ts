import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { map, take } from 'rxjs/operators'; // Utile se AuthService usa Observable per lo stato

export const AuthGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true; // Utente autenticato, permetti l'accesso
  } else {
    // Utente non autenticato, reindirizza alla pagina di login
    router.navigate(['/login']);
    return false;
  }
};