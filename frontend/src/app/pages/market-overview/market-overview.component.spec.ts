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
import { FilterSidebarComponent } from '../../components/filter-sidebar/filter-sidebar.component';

@Component({
  selector: 'app-market-overview',
  standalone: true,
  imports: [
    CommonModule,
    KeyValuePipe,
    NgFor,
    AsyncPipe,
    MatExpansionModule,
    MatCardModule,
    MatDividerModule,
    FilterSidebarComponent,
  ],
  templateUrl: './market-overview.component.html',
  styleUrls: ['./market-overview.component.scss'],
})
export class MarketOverviewComponent implements OnInit {
  exchangesByCountry: Record<string, Exchange[]> = {};
  allExchangesByCountry: Record<string, Exchange[]> = {};

  constructor(private exchangesService: ExchangesService) {}

  ngOnInit(): void {
    this.exchangesService.getExchangesByCountry().subscribe({
      next: (data) => {
        const normalized = Object.entries(data).reduce(
          (acc, [country, exchanges]) => {
            acc[country.toUpperCase()] = exchanges;
            return acc;
          },
          {} as Record<string, Exchange[]>
        );

        this.allExchangesByCountry = normalized;
        this.exchangesByCountry = normalized;
      },
      error: (err) => console.error('❌ Eroare la încărcare exchanges:', err),
    });
  }

  applyFilters(filters: any): void {
    const countries: string[] = (filters.country || []).map((c: string) =>
      c.toUpperCase()
    );
    const exchanges: string[] = (filters.exchange || []).map((e: string) =>
      e.toUpperCase().trim()
    );

    let filtered: Record<string, Exchange[]> = {};

    for (const country of countries) {
      const countryData = this.allExchangesByCountry[country];
      if (countryData) {
        filtered[country] = exchanges.length
          ? countryData.filter((ex) =>
              exchanges.includes(ex.mic?.toUpperCase().trim())
            )
          : countryData;
      }
    }

    this.exchangesByCountry = filtered;
  }
}
