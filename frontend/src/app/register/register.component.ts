import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router'; // Per la navigazione dopo la registrazione

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  registerForm: FormGroup;
  errorMessage: string | null = null;
  successMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      name: ['', Validators.required],
      surname: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required],
      sex: ['', Validators.required], 
      birth_date: ['', Validators.required], 
      address: ['', Validators.required], 
      phone_number: ['', Validators.required] 
    }, { validator: this.passwordMatchValidator });
  }

  // Validatore personalizzato per verificare che le password corrispondano
  private passwordMatchValidator(form: FormGroup) {
    return form.get('password')?.value === form.get('confirmPassword')?.value
      ? null : { mismatch: true };
  }

  onSubmit(): void {
    this.errorMessage = null;
    this.successMessage = null;

    if (this.registerForm.valid) {
      const { name, surname, email, password, sex, birth_date, address, phone_number } = this.registerForm.value;
      this.authService.register({ name, surname, email, password, sex, birth_date, address, phone_number  }).subscribe({
        next: (response) => {
          this.successMessage = 'Registrazione avvenuta con successo! Puoi effettuare il login.';
          this.registerForm.reset(); // Resetta il form
          // Opzionale: Reindirizza alla pagina di login dopo un breve ritardo
          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 2000);
        },
        error: (error) => {
          // Gestisci errori specifici dalla tua API Flask (es. email già registrata)
          this.errorMessage = error.error?.message || 'Errore durante la registrazione. Riprova.';
        }
      });
    } else {
      this.errorMessage = 'Compila tutti i campi richiesti correttamente.';
      this.registerForm.markAllAsTouched(); // Mostra gli errori di validazione
    }
  }

  // Getter per un accesso più facile ai controlli del form nel template
  get f() { return this.registerForm.controls; }
}