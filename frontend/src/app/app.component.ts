import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

import { HomeComponent } from './home/home.component';
import { ChatComponent } from './chat/chat.component';
// import { BookingsComponent } from './bookings/bookings.component';

import { AuthService, User } from './services/auth.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    HomeComponent,
    ChatComponent,
    // BookingsComponent
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']  // not styleUrl
})
export class AppComponent {
  title = 'frontend';

  // Observable del profilo utente
  user$: Observable<User | null>;

  constructor(private authService: AuthService) {
    // Iniettiamo il servizio e sottoscriviamo currentUser$
    this.user$ = this.authService.currentUser;
  }

  logout() {
    this.authService.logout();
  }
}
