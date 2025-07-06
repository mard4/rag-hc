import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface QueryRequest {
  query: string;
}

export interface ContextDocument {
  id: string;
  content: string;
  source: string;
}

export interface QueryResponse {        
  answer: string;
  context_used: ContextDocument[];
}

export interface ExtendedQueryResponse extends QueryResponse {
  suggestions: string[];
}

const API_URL =
  (typeof window !== 'undefined' && (window as any).env?.API_URL) ||
  'http://localhost:8000';   

@Injectable({ providedIn: 'root' })
export class ChatService {
  private apiUrl = `${API_URL}/ask`;

  constructor(private http: HttpClient) {}

  sendQuestion(question: string): Observable<any> {
    return this.http.post(this.apiUrl, { query: question });
  }
}
