import { Component, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { FeedbackService, FeedbackAnalysisResponse } from './feedback.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html'
})
export class AppComponent {
  feedbackText = signal('');
  loading = signal(false);
  error = signal<string | null>(null);
  result = signal<FeedbackAnalysisResponse | null>(null);

  isSubmitDisabled = computed(
    () => this.loading() || this.feedbackText().trim().length === 0
  );

  constructor(private readonly feedbackService: FeedbackService) {}

  onSubmit(): void {
    const text = this.feedbackText().trim();
    if (!text || this.loading()) {
      return;
    }

    this.loading.set(true);
    this.error.set(null);
    this.result.set(null);

    this.feedbackService.analyzeFeedback(text).subscribe({
      next: (res) => {
        this.result.set(res);
        this.loading.set(false);
      },
      error: (err) => {
        console.error(err);
        this.error.set('Something went wrong while analyzing the feedback. Please try again.');
        this.loading.set(false);
      }
    });
  }

  clear(): void {
    if (this.loading()) {
      return;
    }
    this.feedbackText.set('');
    this.result.set(null);
    this.error.set(null);
  }

  getSentimentLabel(): string | null {
    const res = this.result();
    if (!res) {
      return null;
    }
    if (res.sentiment === 'HAPPY') {
      return 'Customer is happy';
    }
    if (res.sentiment === 'UNHAPPY') {
      return 'Customer is unhappy';
    }
    return 'Customer sentiment is neutral';
  }
}

