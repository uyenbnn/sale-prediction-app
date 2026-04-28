import { Component, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { finalize, timeout } from 'rxjs';
import { Chart, type ChartConfiguration, type ScatterDataPoint } from 'chart.js/auto';

type PredictRequest = {
  product: string;
  date: string;
  recent_average_sales?: number;
};

type PredictResponse = {
  product: string;
  date: string;
  predicted_sales: number;
  suggestion: 'Increase stock' | 'Maintain stock' | 'Reduce inventory';
  selected_model?: string | null;
};

type ForecastDayRow = {
  date: string;
  predicted_sales: number;
  suggestion: string;
};

type ForecastSummary = {
  total_days: number;
  avg_predicted_sales: number;
  increase_stock_count: number;
  reduce_inventory_count: number;
  maintain_stock_count: number;
};

type ForecastRangeResponse = {
  daily_rows: ForecastDayRow[];
  summary: ForecastSummary;
  selected_model?: string | null;
};

type EvaluationRow = {
  date: string;
  product: string;
  actual_sales: number;
  predicted_sales: number;
  absolute_error: number;
  error_percentage: number;
};

type AccuracyTrendPoint = {
  period: string;
  mae: number;
  rmse: number;
  mape: number;
};

type EvaluationSummary = {
  total_samples: number;
  overall_mae: number;
  overall_rmse: number;
  overall_mape: number;
  best_product: string;
  worst_product: string;
};

type EvaluationResponse = {
  evaluation_rows: EvaluationRow[];
  summary: EvaluationSummary;
  accuracy_trend: AccuracyTrendPoint[];
};

type ProductComparisonMetric = {
  product: string;
  total_days: number;
  avg_predicted_sales: number;
  sum_predicted_sales: number;
  increase_stock_count: number;
  reduce_inventory_count: number;
  maintain_stock_count: number;
};

type ProductComparisonResponse = {
  comparison_metrics: ProductComparisonMetric[];
  highest_demand_product: string;
  highest_demand_average_sales: number;
  selected_model?: string | null;
};

@Component({
  selector: 'app-root',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  @ViewChild('lineChartCanvas') lineChartCanvas?: ElementRef<HTMLCanvasElement>;
  @ViewChild('barChartCanvas') barChartCanvas?: ElementRef<HTMLCanvasElement>;
  @ViewChild('evaluationChartCanvas') evaluationChartCanvas?: ElementRef<HTMLCanvasElement>;
  @ViewChild('comparisonChartCanvas') comparisonChartCanvas?: ElementRef<HTMLCanvasElement>;

  protected activeTab = 'forecast';
  protected loadingForecast = false;
  protected loadingEvaluation = false;
  protected loadingComparison = false;
  protected errorMessage = '';
  protected successMessage = '';
  
  protected result: PredictResponse | null = null;
  protected forecastData: ForecastRangeResponse | null = null;
  protected evaluationData: EvaluationResponse | null = null;
  protected comparisonData: ProductComparisonResponse | null = null;
  
  protected readonly forecastForm;
  protected readonly comparisonForm;
  protected readonly products = ['Beauty', 'Food', 'Electronics', 'Clothing', 'Home'];
  
  private readonly apiUrl = 'http://127.0.0.1:8000/api';
  private lineChartInstance?: Chart;
  private barChartInstance?: Chart;
  private evaluationChartInstance?: Chart<'scatter', ScatterDataPoint[]>;
  private comparisonChartInstance?: Chart;

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.forecastForm = this.fb.nonNullable.group({
      product: ['Beauty', [Validators.required, Validators.maxLength(200)]],
      start_date: [this.getTodayIsoDate(), [Validators.required]],
      end_date: [this.getDate7DaysFromNow(), [Validators.required]],
      recent_average_sales: [null as number | null]
    });

    this.comparisonForm = this.fb.nonNullable.group({
      selected_products: [['Beauty', 'Food', 'Electronics'], [Validators.required]]
    });
  }

  protected setActiveTab(tab: string): void {
    this.activeTab = tab;
    this.errorMessage = '';
    this.successMessage = '';
    setTimeout(() => {
      if (tab === 'forecast' && this.lineChartCanvas) {
        this.renderForecastCharts();
      } else if (tab === 'evaluation' && this.evaluationChartCanvas) {
        this.renderEvaluationChart();
      } else if (tab === 'comparison' && this.comparisonChartCanvas) {
        this.renderComparisonChart();
      }
    }, 100);
  }

  protected submitForecast(): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.forecastData = null;
    this.lineChartInstance?.destroy();
    this.barChartInstance?.destroy();

    if (this.forecastForm.invalid) {
      this.errorMessage = 'Please provide valid product and date range.';
      return;
    }

    const rawValue = this.forecastForm.getRawValue();
    const payload = {
      product: rawValue.product.trim(),
      start_date: rawValue.start_date,
      end_date: rawValue.end_date,
      recent_average_sales: rawValue.recent_average_sales ? Number(rawValue.recent_average_sales) : undefined
    };

    this.loadingForecast = true;
    this.http
      .post<ForecastRangeResponse>(`${this.apiUrl}/forecast-range`, payload)
      .pipe(
        timeout(15000),
        finalize(() => (this.loadingForecast = false))
      )
      .subscribe({
        next: (response) => {
          this.forecastData = response;
          this.successMessage = `Forecast generated for ${response.summary.total_days} days`;
          setTimeout(() => this.renderForecastCharts(), 200);
        },
        error: (err: unknown) => {
          const detail = (err as { error?: { detail?: string } })?.error?.detail;
          this.errorMessage = detail || 'Failed to generate forecast. Please check inputs and try again.';
        }
      });
  }

  protected submitEvaluation(): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.evaluationData = null;
    this.evaluationChartInstance?.destroy();

    this.loadingEvaluation = true;
    this.http
      .get<EvaluationResponse>(`${this.apiUrl}/model-evaluation`)
      .pipe(
        timeout(15000),
        finalize(() => (this.loadingEvaluation = false))
      )
      .subscribe({
        next: (response) => {
          this.evaluationData = response;
          this.successMessage = `Evaluated ${response.summary.total_samples} samples`;
          setTimeout(() => this.renderEvaluationChart(), 200);
        },
        error: (err: unknown) => {
          const detail = (err as { error?: { detail?: string } })?.error?.detail;
          this.errorMessage = detail || 'Failed to load evaluation. Please try again.';
        }
      });
  }

  protected submitComparison(): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.comparisonData = null;
    this.comparisonChartInstance?.destroy();

    if (this.comparisonForm.invalid) {
      this.errorMessage = 'Please select at least one product.';
      return;
    }

    const rawValue = this.comparisonForm.getRawValue();
    const products = rawValue.selected_products || this.products;

    this.loadingComparison = true;
    this.http
      .post<ProductComparisonResponse>(`${this.apiUrl}/compare-products`, products)
      .pipe(
        timeout(15000),
        finalize(() => (this.loadingComparison = false))
      )
      .subscribe({
        next: (response) => {
          this.comparisonData = response;
          this.successMessage = `Compared ${response.comparison_metrics.length} products`;
          setTimeout(() => this.renderComparisonChart(), 200);
        },
        error: (err: unknown) => {
          const detail = (err as { error?: { detail?: string } })?.error?.detail;
          this.errorMessage = detail || 'Failed to compare products. Please try again.';
        }
      });
  }

  private renderForecastCharts(): void {
    if (!this.forecastData?.daily_rows) return;

    const dates = this.forecastData.daily_rows.map(r => r.date);
    const sales = this.forecastData.daily_rows.map(r => r.predicted_sales);

    this.renderLineChart(dates, sales);
    this.renderSuggestionBar();
  }

  private renderLineChart(dates: string[], sales: number[]): void {
    if (!this.lineChartCanvas) return;

    this.lineChartInstance?.destroy();
    const ctx = this.lineChartCanvas.nativeElement.getContext('2d');
    if (!ctx) return;

    const config: ChartConfiguration<'line', number[], string> = {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: 'Predicted Sales',
          data: sales,
          borderColor: 'rgb(42, 157, 143)',
          backgroundColor: 'rgba(42, 157, 143, 0.1)',
          tension: 0.3,
          fill: true,
          pointRadius: 4,
          pointBackgroundColor: 'rgb(42, 157, 143)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: true, position: 'top' }
        },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Sales ($)' } }
        }
      }
    };

    this.lineChartInstance = new Chart(ctx, config);
  }

  private renderSuggestionBar(): void {
    if (!this.barChartCanvas || !this.forecastData?.summary) return;

    this.barChartInstance?.destroy();
    const ctx = this.barChartCanvas.nativeElement.getContext('2d');
    if (!ctx) return;
    const summary = this.forecastData.summary;

    const config: ChartConfiguration<'bar', number[], string> = {
      type: 'bar',
      data: {
        labels: ['Increase Stock', 'Maintain Stock', 'Reduce Inventory'],
        datasets: [{
          label: 'Count',
          data: [summary.increase_stock_count, summary.maintain_stock_count, summary.reduce_inventory_count],
          backgroundColor: ['rgba(42, 157, 143, 0.8)', 'rgba(65, 90, 119, 0.8)', 'rgba(255, 122, 89, 0.8)']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: true }
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    };

    this.barChartInstance = new Chart(ctx, config);
  }

  private renderEvaluationChart(): void {
    if (!this.evaluationChartCanvas || !this.evaluationData?.evaluation_rows) return;

    this.evaluationChartInstance?.destroy();
    const rows = this.evaluationData.evaluation_rows.slice(0, 20);
    const ctx = this.evaluationChartCanvas.nativeElement.getContext('2d');
    if (!ctx) return;

    const config: ChartConfiguration<'scatter', ScatterDataPoint[]> = {
      type: 'scatter',
      data: {
        datasets: [{
          label: 'Actual Sales',
          data: rows.map((r, i) => ({ x: i, y: r.actual_sales })),
          borderColor: 'rgb(0, 123, 255)',
          backgroundColor: 'rgba(0, 123, 255, 0.5)',
          pointRadius: 5
        }, {
          label: 'Predicted Sales',
          data: rows.map((r, i) => ({ x: i, y: r.predicted_sales })),
          borderColor: 'rgb(40, 167, 69)',
          backgroundColor: 'rgba(40, 167, 69, 0.5)',
          pointRadius: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: true }
        },
        scales: {
          x: { title: { display: true, text: 'Sample Index' } },
          y: { title: { display: true, text: 'Sales ($)' } }
        }
      }
    };

    this.evaluationChartInstance = new Chart<'scatter', ScatterDataPoint[]>(ctx, config);
  }

  private renderComparisonChart(): void {
    if (!this.comparisonChartCanvas || !this.comparisonData?.comparison_metrics) return;

    this.comparisonChartInstance?.destroy();
    const metrics = this.comparisonData.comparison_metrics;
    const ctx = this.comparisonChartCanvas.nativeElement.getContext('2d');
    if (!ctx) return;

    const config: ChartConfiguration<'bar', number[], string> = {
      type: 'bar',
      data: {
        labels: metrics.map(m => m.product),
        datasets: [{
          label: 'Average Predicted Sales',
          data: metrics.map(m => m.avg_predicted_sales),
          backgroundColor: 'rgba(42, 157, 143, 0.7)',
          borderColor: 'rgb(42, 157, 143)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: true }
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    };

    this.comparisonChartInstance = new Chart(ctx, config);
  }

  protected toggleProductSelection(product: string): void {
    const currentProducts = this.comparisonForm.get('selected_products')?.value || [];
    if (currentProducts.includes(product)) {
      this.comparisonForm.patchValue({
        selected_products: currentProducts.filter((p: string) => p !== product)
      });
    } else {
      this.comparisonForm.patchValue({
        selected_products: [...currentProducts, product]
      });
    }
  }

  protected isProductSelected(product: string): boolean {
    const currentProducts = this.comparisonForm.get('selected_products')?.value || [];
    return currentProducts.includes(product);
  }

  private getTodayIsoDate(): string {
    const now = new Date();
    const month = `${now.getMonth() + 1}`.padStart(2, '0');
    const day = `${now.getDate()}`.padStart(2, '0');
    return `${now.getFullYear()}-${month}-${day}`;
  }

  private getDate7DaysFromNow(): string {
    const date = new Date();
    date.setDate(date.getDate() + 7);
    const month = `${date.getMonth() + 1}`.padStart(2, '0');
    const day = `${date.getDate()}`.padStart(2, '0');
    return `${date.getFullYear()}-${month}-${day}`;
  }

  protected getSuggestionClass(suggestion: string): string {
    if (suggestion === 'Increase stock') return 'suggestion-increase';
    if (suggestion === 'Reduce inventory') return 'suggestion-reduce';
    return 'suggestion-maintain';
  }
}
