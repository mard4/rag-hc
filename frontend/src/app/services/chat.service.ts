import { Injectable } from '@angular/core';
import { HttpClient,HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DoctorOut,AvailabilitySlot } from '../models/doctor.model';
import { BookingIn, BookingOut } from '../models/booking.model';
export interface QueryRequest {
  query: string;
}

export interface ContextDocument {
  //id: string;
  title?: string;
  context?: string;
  question: string;
  answer?: string; 
}

export interface QueryResponse {        
  answer: string;
  context_used: ContextDocument[];
}

export interface ExtendedQueryResponse extends QueryResponse {
  //suggestions: string[];
  suggestions: Suggestion[];
}

// chathistory
export interface ChatMessage {
  id: number;
  message: string;
  answer: string;
  timestamp: string; // Or Date 
}

export interface Suggestion {
  type: string; // 'question' o 'doctor_recommendation'
  value: string; 
  data?: { [key: string]: any }; 
}


const API_URL =
  (typeof window !== 'undefined' && (window as any).env?.API_URL) ||
  'http://localhost:8000';   

@Injectable({ providedIn: 'root' })
export class ChatService {
  private apiUrl = `${API_URL}/ask`;
  private chatHistoryUrl = `${API_URL}/chat/history`;
  private doctorsUrl = `${API_URL}/doctors`;
  private bookingsUrl = `${API_URL}/bookings`;
  constructor(private http: HttpClient) {}

  sendQuestion(question: string, includeSuggestion: boolean = false): Observable<ExtendedQueryResponse> {
    let params = new HttpParams();
    if (includeSuggestion) {
      params = params.set('include_suggestions', 'true');
    } else {
      params = params.set('include_suggestions', 'false');
    }
    return this.http.post<ExtendedQueryResponse>(this.apiUrl, { query: question }, { params: params });
  }

  getChatHistory(): Observable<ChatMessage[]> {
    return this.http.get<ChatMessage[]>(this.chatHistoryUrl);
  }

  // fetch doctors
  getDoctors(): Observable<DoctorOut[]> {
    return this.http.get<DoctorOut[]>(this.doctorsUrl);
  }

  // doctor availability
  getDoctorAvailability(doctorId: number): Observable<AvailabilitySlot> {
    return this.http.get<AvailabilitySlot>(`${this.doctorsUrl}/${doctorId}/availability`);
  }
  
  bookAppointment(bookingData: BookingIn): Observable<BookingOut> {
    return this.http.post<BookingOut>(this.bookingsUrl, bookingData);
  }

  getPatientBookings(): Observable<BookingOut[]> {
      return this.http.get<BookingOut[]>(`${this.apiUrl}/bookings/me`); 
    }
}
