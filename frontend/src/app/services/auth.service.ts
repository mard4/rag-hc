import { Injectable, PLATFORM_ID, Inject } from '@angular/core'; // <--- Import PLATFORM_ID, Inject
import { isPlatformBrowser } from '@angular/common'; // <--- Import isPlatformBrowser
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { User } from '../models/user.model';
import { Router } from '@angular/router';
import { map, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/auth';

  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser: Observable<User | null>;

  // Inject PLATFORM_ID in the constructor
  constructor(
    private http: HttpClient,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object 
  ) {
    let storedUser: User | null = null;
    // Check if the code is running in a browser environment before accessing localStorage
    if (isPlatformBrowser(this.platformId)) {
      const userString = localStorage.getItem('currentUser');
      if (userString) {
        try {
          storedUser = JSON.parse(userString);
        } catch (e) {
          console.error("Error parsing stored user from localStorage", e);
          localStorage.removeItem('currentUser'); // Clear invalid data
        }
      }
    }
    if (isPlatformBrowser(this.platformId) && localStorage.getItem('jwtToken')) {
      this.fetchProfile().subscribe();
    }
    this.currentUserSubject = new BehaviorSubject<User | null>(storedUser);
    this.currentUser = this.currentUserSubject.asObservable();
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  register(userData: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/register`, userData).pipe(
      tap((response: any) => {
        console.log('Registrazione avvenuta con successo!', response);
      }),
      catchError(error => {
        console.error('Errore durante la registrazione:', error);
        throw error;
      })
    );
  }

  login(credentials: any): Observable<User> {
    return this.http.post<{ access_token: string, user: User }>(
      `${this.apiUrl}/login`,
      credentials
    ).pipe(
      tap(response => {
        // salva token e utente raw in localStorage
        if (isPlatformBrowser(this.platformId)) {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('currentUser', JSON.stringify(response.user));
        }
        // pushiamo subito il valore iniziale
        this.currentUserSubject.next(response.user);
      }),
      // poi richiamiamo fetchProfile per avere i dati aggiornati
      tap(() => this.fetchProfile().subscribe()),
      // alla fine “mappiamo” il flusso su User, non su {…}
      // in questo modo chi si iscrive a login() riceve direttamente User
      map(response => response.user),
      catchError(error => {
        console.error('Errore durante il login:', error);
        return throwError(() => error);
      })
    );
  }

  logout(): void {
    // Conditionally remove from localStorage only in browser
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('currentUser');
      localStorage.removeItem('access_token');
    }

    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  isAuthenticated(): boolean {
    return this.currentUserSubject.value !== null;
  }

  // 1) Metodo per andare a prendere il profilo dal backend
  private fetchProfile(): Observable<User> {
    return this.http
      .get<User>(`${this.apiUrl}/patients/me`)
      .pipe(
        tap(user => {
          // salva anche l’utente aggiornato in localStorage
          if (isPlatformBrowser(this.platformId)) {
            localStorage.setItem('currentUser', JSON.stringify(user));
          }
          this.currentUserSubject.next(user);
        })
      );
  }

}

export { User } from '../models/user.model';


