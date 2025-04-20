import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  Exchange,
  ExchangesService,
} from '../../core/services/exchanges.service';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { AsyncPipe, NgFor, KeyValuePipe } from '@angular/common';

@Component({
  selector: 'app-market-overview',
  imports: [
    CommonModule,
    KeyValuePipe,
    NgFor,
    AsyncPipe,
    MatExpansionModule,
    MatCardModule,
    MatDividerModule,
  ],
  templateUrl: './market-overview.component.html',
  styleUrl: './market-overview.component.scss',
})
export class MarketOverviewComponent implements OnInit {
  exchangesByCountry: Record<string, Exchange[]> = {};

  constructor(private exchangesService: ExchangesService) {}

  ngOnInit(): void {
    this.exchangesService.getExchangesByCountry().subscribe({
      next: (data) => (this.exchangesByCountry = data),
      error: (err) => console.error('Error fetching exchanges', err),
    });
  }
}
