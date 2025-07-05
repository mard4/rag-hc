import { Routes } from "@angular/router";
import { HomeComponent } from "./home/home.component";
import { ChatComponent } from "./chat/chat.component";
import { BookingsComponent } from "./bookings/bookings.component";
import { AuthGuard } from './guards/auth.guards';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from "./register/register.component";

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: '', component: HomeComponent, canActivate: [AuthGuard] },
  { path: 'home', component: HomeComponent, canActivate: [AuthGuard] },
  { path: "chat", component: ChatComponent, canActivate: [AuthGuard] },
  //{ path: "bookings", component: BookingsComponent, canActivate: [AuthGuard] },
];
// <a [routerLink]="['/products', productID]">View Product</a>



