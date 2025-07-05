import { Component } from '@angular/core';
import { ChatService, QueryResponse } from '../services/chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent {
  userInput = '';
  chatHistory: { role: 'user' | 'assistant'; text: string }[] = [];
  loading = false;

  constructor(private chatService: ChatService) {}

  sendMessage() {
    const question = this.userInput.trim();
    if (!question) return;

    this.chatHistory.push({ role: 'user', text: question });
    this.userInput = '';
    this.loading = true;

    this.chatService.sendQuestion(question).subscribe({
      next: (res: QueryResponse) => {
        this.chatHistory.push({ role: 'assistant', text: res.answer });
        this.loading = false;
      },
      error: (err) => {
        this.chatHistory.push({ role: 'assistant', text: '❌ Errore nella risposta dal server.' });
        console.error(err);
        this.loading = false;
      }
    });
  }
}
