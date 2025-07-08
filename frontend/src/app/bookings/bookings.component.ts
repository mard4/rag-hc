import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common'; 
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';

import { BookingService } from '../services/booking.service';
import { BookingOut, BookingIn } from '../models/booking.model'; 
import { DoctorOut } from '../models/doctor.model'; 

@Component({
  selector: 'app-bookings',
  standalone: true,
  imports: [CommonModule, FormsModule, DatePipe], 
  templateUrl: './bookings.component.html',
  styleUrls: ['./bookings.component.scss'],
  providers: [DatePipe] 
})
export class BookingsComponent implements OnInit {
  doctors: DoctorOut[] = []; 
  allBookings: BookingOut[] = []; 
  filteredBookings: BookingOut[] = []; 

  selectedDoctorId: number | 'all' = 'all'; 
  selectedDate: string = ''; // 'YYYY-MM-DD' for input type="date"

  loading: boolean = false;
  
  // Properties for the booking form (TO DO)
  showBookingForm: boolean = false;
  bookingToEdit: BookingOut | null = null; 

  constructor(private bookingService: BookingService, private datePipe: DatePipe) {} 

  ngOnInit(): void {
    this.loadDoctors();
    this.loadBookings();
  }

  loadDoctors(): void {
    this.bookingService.getDoctors().subscribe({
      next: (doctors: DoctorOut[]) => {
        this.doctors = doctors;
      },
      error: (err: HttpErrorResponse) => {
        console.error('Error fetching doctors:', err);
        // Optionally, show an error message to the user
      }
    });
  }

  loadBookings(): void {
    this.loading = true;
    this.bookingService.getPatientBookings().subscribe({
      next: (bookings: BookingOut[]) => {
        this.allBookings = bookings;
        this.applyFilters(); 
        this.loading = false;
      },
      error: (err: HttpErrorResponse) => {
        console.error('Error fetching patient bookings:', err);
        this.loading = false;
        // Optionally, show an error message to the user
      }
    });
  }

  applyFilters(): void {
    let tempBookings: BookingOut[] = [...this.allBookings]; // Start with all bookings

    // Filter by doctor
    if (this.selectedDoctorId !== 'all') {
      tempBookings = tempBookings.filter(b => b.doctor_id === this.selectedDoctorId);
    }

    // Filter by date
    if (this.selectedDate) {
      const filterDate = new Date(this.selectedDate);
      tempBookings = tempBookings.filter(b => {
        const bookingDate = new Date(b.appointment_date); // Convert booking date string to Date object
        return bookingDate.getFullYear() === filterDate.getFullYear() &&
               bookingDate.getMonth() === filterDate.getMonth() &&
               bookingDate.getDate() === filterDate.getDate();
      });
    }

    // Sort by appointment date
    this.filteredBookings = tempBookings.sort((a, b) => 
      new Date(a.appointment_date).getTime() - new Date(b.appointment_date).getTime()
    );
  }

  // Helper to format date for display in the template
  formatSlotDate(dateString: string): string {
    return this.datePipe.transform(dateString, 'mediumDate') + ' alle ' + this.datePipe.transform(dateString, 'shortTime');
  }

  // --- CRUD Actions  ---
  onAddBooking(): void {
    this.bookingToEdit = null;
    this.showBookingForm = true;
    console.log('TODO Open form to add new booking');
    // Implement logic to open a modal/form for adding a new booking
  }

  onEditBooking(booking: BookingOut): void { 
    this.bookingToEdit = { ...booking }; 
    this.showBookingForm = true;
    console.log('TODO Open form to edit booking:', booking);
    // Implement logic to open a modal/form pre-filled with booking data
  }

  onDeleteBooking(bookingId: number): void { // Use number for ID
    if (confirm('Sei sicuro di voler eliminare questo appuntamento?')) {
      console.log('Deleting booking with ID:', bookingId);
      this.allBookings = this.allBookings.filter(b => b.id !== bookingId);
      this.applyFilters();
    }
  }

  getStatusClass(status: string): string {
    switch (status.toLowerCase()) { 
      case 'scheduled': return 'status-scheduled'; 
      case 'pending': return 'status-pending';
      case 'cancelled': return 'status-cancelled';
      case 'completed': return 'status-completed';
      default: return '';
    }
  }
}