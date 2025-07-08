import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';

import { ChatComponent } from '../chat/chat.component'; 
import { BookingsComponent } from '../bookings/bookings.component'; 
import { AuthService, User } from '../services/auth.service';
import { ChatService, ChatMessage } from '../services/chat.service'; 
import { BookingService } from '../services/booking.service'; 
import { BookingOut } from '../models/booking.model'; 

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    DatePipe, 
    ChatComponent, 
    BookingsComponent, 
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  providers: [DatePipe] 
})
export class HomeComponent implements OnInit {
  // User data from AuthService
  user$: Observable<User | null>;

  patientChatHistory: ChatMessage[] = [];
  showHistory = false;

  patientBookings: BookingOut[] = [];
  showBookings = false;

  loading: boolean = false; 

  constructor(
    private authService: AuthService,
    private chatService: ChatService, 
    private bookingService: BookingService, 
    private datePipe: DatePipe 
  ) {
    this.user$ = this.authService.currentUser;
  }

  ngOnInit(): void {
    // INITIAL setup
  }

  // Method to toggle chat history visibility and fetch data
  toggleChatHistory() {
    this.showHistory = !this.showHistory;
    this.showBookings = false; // Hide bookings when showing chat history
    if (this.showHistory && this.patientChatHistory.length === 0) {
      this.loading = true;
      this.chatService.getChatHistory().subscribe({
        next: (history: ChatMessage[]) => {
          this.patientChatHistory = history;
          this.loading = false;
        },
        error: (err: HttpErrorResponse) => {
          console.error('Error fetching chat history:', err);
          this.loading = false;
        }
      });
    }
  }

  // Method to toggle bookings visibility and fetch data
  toggleBookings() {
    this.showBookings = !this.showBookings;
    this.showHistory = false; // Hide chat history when showing bookings
    if (this.showBookings && this.patientBookings.length === 0) {
      this.loading = true;
      this.bookingService.getPatientBookings().subscribe({
        next: (bookings: BookingOut[]) => {
          this.patientBookings = bookings;
          this.loading = false;
        },
        error: (err: HttpErrorResponse) => {
          console.error('Error fetching patient bookings:', err);
          this.loading = false;
        }
      });
    }
  }

  // Helper to format date for display in the template (for history/bookings)
  formatDateForDisplay(dateString: string): string {
    const date = new Date(dateString);
    return this.datePipe.transform(date, 'mediumDate') + ' alle ' + this.datePipe.transform(date, 'shortTime');
  }
}