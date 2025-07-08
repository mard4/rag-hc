import { Component } from '@angular/core';
import { ChatService, ExtendedQueryResponse, Suggestion } from '../services/chat.service'; 
import { DoctorOut, AvailabilitySlot } from '../models/doctor.model';
import { BookingIn, BookingOut } from '../models/booking.model';
import { CommonModule, DatePipe } from '@angular/common'; 
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, DatePipe], 
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent {
  userInput = '';
  chatHistory: { role: 'user' | 'assistant'; text: string }[] = [];
  loading = false;
  suggestions: Suggestion[] = [];
  
  // Variables for doctor recommendation and booking 
  showDoctorRecommendation = false;
  recommendedProblemType: string | null = null;
  availableDoctors: DoctorOut[] = [];
  selectedDoctor: DoctorOut | null = null;
  doctorAvailability: AvailabilitySlot | null = null;
  showAvailability = false;
  reasonForVisit: string = ''; 
  
  constructor(private chatService: ChatService) {}

  sendMessage() {
    const question = this.userInput.trim();
    if (!question) return;

    this.chatHistory.push({ role: 'user', text: question });
    this.userInput = '';
    this.loading = true;
    this.suggestions = [];
    this.resetDoctorRecommendation(); // Resets doctor recommendation UI

    this.chatService.sendQuestion(question, true).subscribe({
      next: (res: ExtendedQueryResponse) => {
        this.chatHistory.push({ role: 'assistant', text: res.answer });
        this.loading = false;
        if (res.suggestions && res.suggestions.length > 0) {
          this.suggestions = res.suggestions;
        } else {
          this.suggestions = [];
        }
      },
      error: (err: HttpErrorResponse) => {
        this.chatHistory.push({ role: 'assistant', text: '❌ Errore' });
        console.error(err);
        this.loading = false;
        this.suggestions = [];
      }
    });
  }

  sendSuggestedQuestion(suggestionValue: string) {
    this.userInput = suggestionValue;
    this.sendMessage();
  }

  handleDoctorRecommendation(data?: { [key: string]: any }) {
    this.showDoctorRecommendation = true;
    this.recommendedProblemType = data && data['problem_type'] ? data['problem_type'] : null;
    this.loading = true;
    this.suggestions = [];

    this.chatService.getDoctors().subscribe({
      next: (doctors: DoctorOut[]) => {
        if (this.recommendedProblemType) {
          const lowerCaseProblem = this.recommendedProblemType.toLowerCase();
          this.availableDoctors = doctors.filter(doc => 
            doc.specialization.toLowerCase().includes(lowerCaseProblem) || 
            lowerCaseProblem.includes('generale')
          );
          if (this.availableDoctors.length === 0) {
            this.availableDoctors = doctors;
            this.chatHistory.push({ role: 'assistant', text: `Non ho trovato specialisti per '${this.recommendedProblemType}'. Ecco tutti i medici disponibili. Oppure considera un medico generico.` });
          }
        } else {
          this.availableDoctors = doctors;
        }
        this.loading = false;
      },
      error: (err: HttpErrorResponse) => {
        console.error('Error fetching doctors:', err);
        this.loading = false;
        this.chatHistory.push({ role: 'assistant', text: '❌ Errore nel recuperare la lista dei medici.' });
      }
    });
  }

  selectDoctor(doctor: DoctorOut) {
    console.log('Selected doctor:', doctor);
    this.selectedDoctor = doctor;
    this.showAvailability = true;
    this.loading = true;
    this.doctorAvailability = null;

    this.chatService.getDoctorAvailability(doctor.id).subscribe({
      next: (availability: AvailabilitySlot) => {
        this.doctorAvailability = availability;
        this.loading = false;
      },
      error: (err: HttpErrorResponse) => {
        console.error('Error fetching doctor availability:', err);
        this.loading = false;
        this.chatHistory.push({ role: 'assistant', text: `❌ Errore nel recuperare la disponibilità per ${doctor.name} ${doctor.surname}.` });
      }
    });
  }

  bookSelectedSlot(slotString: string) {
    if (this.selectedDoctor && slotString) {
      this.loading = true;
      const bookingData: BookingIn = {
        doctor_id: this.selectedDoctor.id,
        appointment_date: slotString,
        reason_for_visit: this.reasonForVisit || `Visita per ${this.recommendedProblemType || 'motivo generico'}`
      };

      this.chatService.bookAppointment(bookingData).subscribe({
        next: (response: BookingOut) => {
          this.chatHistory.push({ role: 'assistant', text: `✅ Appuntamento con il Dr. ${this.selectedDoctor?.surname} il ${this.formatSlotDate(response.appointment_date)} prenotato con successo! ID Prenotazione: ${response.id}` });
          this.loading = false;
          this.resetDoctorRecommendation();
        },
        error: (err: HttpErrorResponse) => {
          console.error('Error booking appointment:', err);
          this.chatHistory.push({ role: 'assistant', text: `❌ Errore durante la prenotazione dell'appuntamento.` });
          this.loading = false;
        }
      });
    }
  }

  formatSlotDate(slotString: string): string {
    const date = new Date(slotString);
    return new DatePipe('en-US').transform(date, 'mediumDate') + ' alle ' + new DatePipe('en-US').transform(date, 'shortTime');
  }

  resetDoctorRecommendation() {
    this.showDoctorRecommendation = false;
    this.recommendedProblemType = null;
    this.availableDoctors = [];
    this.selectedDoctor = null;
    this.doctorAvailability = null;
    this.showAvailability = false;
    this.reasonForVisit = ''; // Reset reason for visit
  } 
}