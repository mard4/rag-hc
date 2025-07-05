// src/app/bookings/bookings.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { BookingService } from '../services/booking.service';
import { Booking } from '../models/booking.model';
import { Doctor } from '../models/doctor.model';
// import { Patient } from '../models/patient.model'; // You might not need to import Patient here if only used in service

@Component({
  selector: 'app-bookings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './bookings.component.html',
  styleUrls: ['./bookings.component.scss']
})
export class BookingsComponent implements OnInit {
  bookings: Booking[] = [];
  doctors: Doctor[] = [];
  filteredBookings: Booking[] = [];

  selectedDoctorId: string = 'all';
  selectedDate: string = '';

  showBookingForm: boolean = false;
  bookingToEdit: Booking | null = null;

  constructor(private bookingService: BookingService) { }

  ngOnInit(): void {
    // FIX: Add explicit type for 'doctors' parameter
    this.bookingService.getDoctors().subscribe((doctors: Doctor[]) => {
      this.doctors = doctors;
    });

    // FIX: Add explicit type for 'bookings' parameter
    this.bookingService.getBookings().subscribe((bookings: Booking[]) => {
      this.bookings = bookings;
      this.applyFilters();
    });
  }

  applyFilters(): void {
    let tempBookings = [...this.bookings];

    if (this.selectedDoctorId !== 'all') {
      // Ensure type consistency if doctorId is 'string' in your models
      tempBookings = tempBookings.filter(b => b.doctorId === this.selectedDoctorId);
    }

    if (this.selectedDate) {
      const filterDate = new Date(this.selectedDate);
      tempBookings = tempBookings.filter(b =>
        b.startTime.getFullYear() === filterDate.getFullYear() &&
        b.startTime.getMonth() === filterDate.getMonth() &&
        b.startTime.getDate() === filterDate.getDate()
      );
    }

    this.filteredBookings = tempBookings.sort((a, b) => a.startTime.getTime() - b.startTime.getTime());
  }

  onAddBooking(): void {
    this.bookingToEdit = null;
    this.showBookingForm = true;
    console.log('Aggiungi nuovo booking');
  }

  onEditBooking(booking: Booking): void {
    this.bookingToEdit = { ...booking };
    this.showBookingForm = true;
    console.log('Modifica booking:', booking);
  }

  onDeleteBooking(id: string): void {
    if (confirm('Sei sicuro di voler eliminare questo booking?')) {
      // FIX: Add explicit type for 'success' parameter
      this.bookingService.deleteBooking(id).subscribe((success: boolean) => { // Assuming deleteBooking returns Observable<boolean>
        if (success) {
          console.log('Booking eliminato con successo!');
          // Re-fetch bookings after deletion
          // FIX: Add explicit type for 'bookings' parameter
          this.bookingService.getBookings().subscribe((bookings: Booking[]) => {
            this.bookings = bookings;
            this.applyFilters();
          });
        } else {
          console.error('Errore nell\'eliminazione del booking.');
        }
      }, (error: any) => { // Good to explicitly type error too
        console.error('Errore durante la chiamata di eliminazione:', error);
      });
    }
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'confirmed': return 'status-confirmed';
      case 'pending': return 'status-pending';
      case 'cancelled': return 'status-cancelled';
      case 'completed': return 'status-completed';
      default: return '';
    }
  }
}