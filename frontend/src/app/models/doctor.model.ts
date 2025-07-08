export interface Doctor {
    id: string;
    name: string;
    specialty: string;
  }

  export interface DoctorOut { 
    id: number;
    name: string;
    surname: string;
    sex: string;
    birth_date: string; 
    phone_number: string;
    email: string;
    experience_years: number;
    specialization: string;
    rating: number;
    created_at: string; 
  }

  export interface AvailabilitySlot { 
    doctor_id: number;
    available_slots: string[]; // gestire la conversione
}