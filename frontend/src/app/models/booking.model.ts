export interface BookingIn {
    doctor_id: number;
    appointment_date: string; 
    reason_for_visit?: string;
  }
  
  export interface BookingOut {
    id: number;
    patient_id: number;
    doctor_id: number;
    doctor_name: string;
    doctor_surname: string;
    appointment_date: string; 
    reason_for_visit?: string;
    status: string;
    created_at: string;
  }