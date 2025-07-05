import { Doctor } from './doctor.model';
import { Patient } from './patient.model';

export interface Booking {
  id: string;
  doctorId: string; // ID del dottore prenotato
  patientId: string; // ID del paziente che prenota
  doctor?: Doctor; // Popolato per visualizzazione, non sempre persistito
  patient?: Patient; // Popolato per visualizzazione, non sempre persistito
  startTime: Date; // Ora e data di inizio del booking
  endTime: Date;   // Ora e data di fine del booking
  type: 'visit' | 'consultation' | 'procedure'; // Tipo di appuntamento
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed'; // Stato del booking
  notes?: string;
}
