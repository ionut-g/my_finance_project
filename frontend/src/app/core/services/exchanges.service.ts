import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Exchange {
  code: string;
  mic: string;
  name: string;
  country: string;
  city: string;
}

@Injectable({
  providedIn: 'root',
})
export class ExchangesService {
  private readonly baseUrl = '/exchanges'; // Folosește proxy-ul Angular

  constructor(private http: HttpClient) {}

  getExchangesByCountry(): Observable<Record<string, Exchange[]>> {
    return this.http.get<Record<string, Exchange[]>>(
      `${this.baseUrl}/by-country`
    );
  }
}
