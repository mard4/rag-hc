import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { Router, RouterLink } from '@angular/router'; // Per la navigazione

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink], // Aggiungi RouterLink per il link di registrazione
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit(): void {
    this.errorMessage = null;
    console.log("onSubmit called!");
    if (this.loginForm.valid) {
      const { email, password } = this.loginForm.value;
      this.authService.login({ email, password }).subscribe({
        next: (user) => {
          this.router.navigate(['/home']); 
        },
        error: (error) => {
          this.errorMessage = error.error?.message || 'Credenziali non valide. Riprova.';
        }
      });
    } else {
      this.errorMessage = 'Inserisci email e password valide.';
      this.loginForm.markAllAsTouched();
    }
  }

  // Getter per un accesso più facile ai controlli del form nel template
  get f() { return this.loginForm.controls; }
}