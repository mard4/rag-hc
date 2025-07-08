import { Injectable } from '@angular/core';
import { HttpClient,HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DoctorOut,AvailabilitySlot } from '../models/doctor.model';
import { BookingIn, BookingOut } from '../models/booking.model';


const API_URL =
  (typeof window !== 'undefined' && (window as any).env?.API_URL) ||
  'http://localhost:8000';   

@Injectable({ providedIn: 'root' })
export class BookingService {
  private baseUrl = API_URL;
  private doctorsUrl = `${this.baseUrl}/doctors`;
  private bookingsUrl = `${this.baseUrl}/bookings`;
  constructor(private http: HttpClient) {}

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
      return this.http.get<BookingOut[]>(`${this.bookingsUrl}/me`); 
    }
}
