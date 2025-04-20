import { Component, EventEmitter, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient } from '@angular/common/http';
import { Exchange } from '../../core/services/exchanges.service';

@Component({
  selector: 'app-filter-sidebar',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    MatChipsModule,
    MatIconModule,
  ],
  templateUrl: './filter-sidebar.component.html',
  styleUrls: ['./filter-sidebar.component.scss'],
})
export class FilterSidebarComponent implements OnInit {
  @Output() filtersChanged = new EventEmitter<any>();

  form: FormGroup;

  countries: string[] = [];
  exchanges: string[] = [];

  // GICS placeholders
  sectors: string[] = [];
  industryGroups: string[] = [];
  industries: string[] = [];
  subIndustries: string[] = [];

  exchangesRaw: Exchange[] = [];

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.form = this.fb.group({
      country: [[]],
      exchange: [[]],
      sector: [null],
      industryGroup: [null],
      industry: [null],
      subIndustry: [null],
      interval: ['1d'],
    });
  }

  ngOnInit(): void {
    this.http.get<Exchange[]>('/assets/data/exchanges.json').subscribe({
      next: (data) => {
        this.exchangesRaw = data || [];
        this.countries = Array.from(
          new Set(this.exchangesRaw.map((e) => e.country?.toUpperCase()))
        ).sort();

        // Populate exchanges initially if country is pre-filled
        this.updateExchanges(this.form.value.country);

        this.form
          .get('country')
          ?.valueChanges.subscribe((selectedCountries: string[]) => {
            this.updateExchanges(selectedCountries);

            // reset the exchange selection safely
            this.form.patchValue({ exchange: [] }, { emitEvent: false });
            this.form.get('exchange')?.markAsTouched();
            this.form.get('exchange')?.markAsDirty();

            this.onFilterChange(); // trigger filter after exchange reset
          });

        this.form
          .get('exchange')
          ?.valueChanges.subscribe(() => this.onFilterChange());
        this.form
          .get('interval')
          ?.valueChanges.subscribe(() => this.onFilterChange());
        this.form
          .get('sector')
          ?.valueChanges.subscribe(() => this.onFilterChange());
        this.form
          .get('industryGroup')
          ?.valueChanges.subscribe(() => this.onFilterChange());
        this.form
          .get('industry')
          ?.valueChanges.subscribe(() => this.onFilterChange());
        this.form
          .get('subIndustry')
          ?.valueChanges.subscribe(() => this.onFilterChange());
      },
      error: (err) => {
        console.error('❌ Eroare la încărcarea exchanges.json:', err);
      },
    });
  }

  updateExchanges(selectedCountries: string[]) {
    const normalized = (selectedCountries || []).map((c) => c.toUpperCase());

    this.exchanges = this.exchangesRaw
      .filter((e) => normalized.includes(e.country?.toUpperCase()))
      .map((e) => e.mic?.toUpperCase().trim())
      .filter((value, index, self) => value && self.indexOf(value) === index)
      .sort();
  }

  removeCountry(country: string): void {
    const updated = this.form.value.country.filter(
      (c: string) => c !== country
    );
    this.form.patchValue({ country: updated });
    this.updateExchanges(updated);
    this.onFilterChange();
  }

  removeExchange(exchange: string): void {
    const updated = this.form.value.exchange.filter(
      (e: string) => e !== exchange
    );
    this.form.patchValue({ exchange: updated });
    this.onFilterChange();
  }

  onFilterChange(): void {
    this.filtersChanged.emit(this.form.value);
  }
}
