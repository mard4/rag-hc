import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent {
  userInput = '';
  chatHistory: { role: 'user' | 'assistant'; text: string }[] = [];

  async sendMessage() {
    if (!this.userInput.trim()) return;

    this.chatHistory.push({ role: 'user', text: this.userInput });

    // Simulazione chiamata API (da sostituire con il backend reale)
    const response = await this.fakeRagResponse(this.userInput);

    this.chatHistory.push({ role: 'assistant', text: response });
    this.userInput = '';
  }

  // Mock temporaneo
  async fakeRagResponse(question: string): Promise<string> {
    if (question.includes('mal di testa')) {
      return `Potrebbe trattarsi di un'emicrania. Ti consiglio il Dr. Rossi (neurologo). 
Slot disponibili: domani 10:00 o giovedì 14:30. Vuoi prenotare?`;
    }
    return `Sto analizzando i dati… ti risponderò tra poco.`;
  }
}
