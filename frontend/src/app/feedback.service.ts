import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export interface FeedbackAnalysisResponse {
  summary: string;
  sentiment: 'HAPPY' | 'UNHAPPY' | 'NEUTRAL';
  reason: string;
}

@Injectable({
  providedIn: 'root'
})
export class FeedbackService {
  private readonly apiUrl = `${environment.apiBaseUrl}/feedback/analyze`;

  constructor(private readonly http: HttpClient) {}

  analyzeFeedback(text: string): Observable<FeedbackAnalysisResponse> {
    return this.http.post<FeedbackAnalysisResponse>(this.apiUrl, { text });
  }
}

