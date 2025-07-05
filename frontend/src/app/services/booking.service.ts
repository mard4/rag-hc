import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';
import { Doctor } from '../models/doctor.model';
import { Patient } from '../models/patient.model';
import { Booking } from '../models/booking.model';

@Injectable({
  providedIn: 'root'
})
export class BookingService {
  private doctors: Doctor[] = [
    { id: 'd1', name: 'Dr. Marco Rossi', specialty: 'Cardiologia' },
    { id: 'd2', name: 'Dr. Laura Bianchi', specialty: 'Dermatologia' },
    { id: 'd3', name: 'Dr. Paolo Verdi', specialty: 'Pediatria' },
  ];

  private patients: Patient[] = [
    { id: 'p1', name: 'Anna', surname: 'Conti', phone: '3331122334',email: 'ma@gmail.com',
         sex:'f', birth_date:'1999-19-19', address:'blalbal' },
  ];

  private bookings: Booking[] = [
    {
      id: 'b1', doctorId: 'd1', patientId: 'p1',
      startTime: new Date('2025-07-10T09:00:00'), endTime: new Date('2025-07-10T09:30:00'),
      type: 'visit', status: 'confirmed'
    },
    {
      id: 'b2', doctorId: 'd2', patientId: 'p2',
      startTime: new Date('2025-07-10T10:00:00'), endTime: new Date('2025-07-10T10:45:00'),
      type: 'consultation', status: 'pending'
    },
    {
      id: 'b3', doctorId: 'd1', patientId: 'p3',
      startTime: new Date('2025-07-11T14:00:00'), endTime: new Date('2025-07-11T14:30:00'),
      type: 'visit', status: 'confirmed'
    },
  ];

  // Subject per notificare i cambiamenti ai booking
  private bookingsSubject = new BehaviorSubject<Booking[]>(this.bookings);
  bookings$ = this.bookingsSubject.asObservable(); // Observable pubblico per sottoscrizioni

  constructor() {
    this.populateBookingsWithDetails(); // Aggiungi dettagli dottore/paziente ai booking iniziali
  }

  // Metodo per popolare i booking con i dettagli di dottori e pazienti
  private populateBookingsWithDetails(): void {
    this.bookings.forEach(booking => {
      booking.doctor = this.doctors.find(d => d.id === booking.doctorId);
      booking.patient = this.patients.find(p => p.id === booking.patientId);
    });
    this.bookingsSubject.next(this.bookings);
  }

  getDoctors(): Observable<Doctor[]> {
    return of(this.doctors).pipe(delay(100));
  }

  getPatients(): Observable<Patient[]> {
    return of(this.patients).pipe(delay(100));
  }

  getBookings(): Observable<Booking[]> {
    return this.bookings$; // Ritorna l'observable per aggiornamenti reattivi
  }

  addBooking(newBooking: Omit<Booking, 'id' | 'doctor' | 'patient'>): Observable<Booking> {
    const id = `b${this.bookings.length + 1}`;
    const fullBooking: Booking = {
      ...newBooking,
      id: id,
      doctor: this.doctors.find(d => d.id === newBooking.doctorId),
      patient: this.patients.find(p => p.id === newBooking.patientId)
    };
    this.bookings.push(fullBooking);
    this.bookingsSubject.next(this.bookings); // Notifica l'aggiornamento
    return of(fullBooking).pipe(delay(200));
  }

  updateBooking(updatedBooking: Booking): Observable<Booking | undefined> {
    const index = this.bookings.findIndex(b => b.id === updatedBooking.id);
    if (index > -1) {
      // Assicurati che i dettagli di dottore/paziente siano aggiornati se necessario
      updatedBooking.doctor = this.doctors.find(d => d.id === updatedBooking.doctorId);
      updatedBooking.patient = this.patients.find(p => p.id === updatedBooking.patientId);
      this.bookings[index] = updatedBooking;
      this.bookingsSubject.next(this.bookings); // Notifica l'aggiornamento
      return of(updatedBooking).pipe(delay(200));
    }
    return of(undefined);
  }

  deleteBooking(id: string): Observable<boolean> {
    const initialLength = this.bookings.length;
    this.bookings = this.bookings.filter(b => b.id !== id);
    if (this.bookings.length < initialLength) {
      this.bookingsSubject.next(this.bookings); // Notifica l'aggiornamento
      return of(true).pipe(delay(100));
    }
    return of(false);
  }
}