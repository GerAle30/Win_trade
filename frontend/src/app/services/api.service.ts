import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  // Traders endpoints
  getTraders(filters?: any): Observable<any> {
    let params = new HttpParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          params = params.set(key, filters[key]);
        }
      });
    }
    return this.http.get(`${this.apiUrl}/traders/`, { params });
  }

  getTrader(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/traders/${id}/`);
  }

  getTraderStats(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/traders/${id}/stats/`);
  }

  getTraderTrades(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/traders/${id}/trades/`);
  }

  getTraderFollowers(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/traders/${id}/followers_list/`);
  }

  // Trades endpoints
  getTrades(filters?: any): Observable<any> {
    let params = new HttpParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          params = params.set(key, filters[key]);
        }
      });
    }
    return this.http.get(`${this.apiUrl}/trades/`, { params });
  }

  getTrade(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/trades/${id}/`);
  }

  createTrade(tradeData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/trades/`, tradeData);
  }

  updateTrade(id: number, tradeData: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/trades/${id}/`, tradeData);
  }

  closeTrade(id: number, exitPrice: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/trades/${id}/close_trade/`, { exit_price: exitPrice });
  }

  getTradesByStatus(status: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/trades/by_status/`, { params: { status } });
  }

  getTopPerformers(limit: number = 10): Observable<any> {
    return this.http.get(`${this.apiUrl}/trades/top_performers/`, { params: { limit } });
  }

  // Followers endpoints
  getFollowers(filters?: any): Observable<any> {
    let params = new HttpParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          params = params.set(key, filters[key]);
        }
      });
    }
    return this.http.get(`${this.apiUrl}/followers/`, { params });
  }

  followTrader(traderId: number, autoyCopy: boolean = true, copyPercentage: number = 100, initialInvestment: number = 0): Observable<any> {
    const data = {
      trader_id: traderId,
      auto_copy_trades: autoyCopy,
      copy_percentage: copyPercentage,
      initial_investment: initialInvestment
    };
    return this.http.post(`${this.apiUrl}/followers/follow_trader/`, data);
  }

  unfollowTrader(traderId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/followers/unfollow_trader/`, { trader_id: traderId });
  }

  getFollowerPerformance(followerId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/followers/${followerId}/performance/`);
  }

  // Auth endpoints
  login(username: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/token/`, { username, password });
  }

  refreshToken(refresh: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/token/refresh/`, { refresh });
  }
}
