import { Component } from '@angular/core';
import { ChatService, QueryResponse } from '../services/chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatComponent } from '../chat/chat.component';
import { AuthService, User } from '../services/auth.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ChatComponent,
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {
  userInput = '';
  chatHistory: { role: 'user' | 'assistant'; text: string }[] = [];
  loading = false;

  // Observable del profilo utente
  user$: Observable<User | null>;

  // Ora iniettiamo anche AuthService
  constructor(
    private chatService: ChatService,
    private authService: AuthService
  ) {
    // e inizializziamo user$
    this.user$ = this.authService.currentUser;
  }
}
