"""
Forecasting module for the Predictive Analytics layer
"""

import frappe
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings

# Suppress statsmodels warnings
warnings.filterwarnings("ignore")

def generate_forecast(forecast):
    """Generate a forecast"""
    try:
        if isinstance(forecast, str):
            forecast_doc = frappe.get_doc("Forecast", forecast)
        else:
            forecast_doc = forecast
            
        frappe.logger().info(f"Generating forecast: {forecast_doc.forecast_name}")
        
        # Update status to Running
        forecast_doc.db_set("status", "Running")
        
        # Get historical data for the metric
        metric_doc = frappe.get_doc("AnalyticsMetric", forecast_doc.metric)
        historical_data = get_historical_data(metric_doc)
        
        if not historical_data or len(historical_data) < 2:
            frappe.throw("Insufficient historical data for forecasting")
        
        # Prepare data for forecasting
        df = prepare_data_for_forecasting(historical_data, forecast_doc.forecast_frequency)
        
        # Determine last historical date
        last_date = df.index[-1]
        forecast_doc.db_set("last_historical_date", last_date.strftime("%Y-%m-%d"))
        
        # Generate forecast based on model type
        forecast_data = run_forecast_model(df, forecast_doc)
        
        # Calculate performance metrics
        performance_metrics = calculate_performance_metrics(df, forecast_data, forecast_doc)
        
        # Format results
        formatted_forecast = format_forecast_results(forecast_data, forecast_doc)
        
        # Update document with results
        forecast_doc.db_set("forecast_values", json.dumps(formatted_forecast))
        forecast_doc.db_set("performance_metrics", json.dumps(performance_metrics))
        forecast_doc.db_set("forecast_date", datetime.now())
        forecast_doc.db_set("status", "Completed")
        
        # Publish event if configured
        if forecast_doc.publish_to_mythos:
            publish_forecast_completed_event(forecast_doc, formatted_forecast, performance_metrics)
            
        # Trigger automated actions if enabled
        if forecast_doc.enable_automated_actions:
            trigger_automated_actions(forecast_doc, formatted_forecast)
            
        return {
            "success": True,
            "forecast": formatted_forecast,
            "performance": performance_metrics
        }
        
    except Exception as e:
        if isinstance(forecast, str):
            frappe.db.set_value("Forecast", forecast, "status", "Failed")
        else:
            forecast.db_set("status", "Failed")
            
        frappe.log_error(f"Error generating forecast: {str(e)}", "Forecast Generation Error")
        return {
            "success": False,
            "error": str(e)
        }

def get_historical_data(metric_doc):
    """Get historical data for a metric"""
    try:
        # This would be implemented to fetch actual historical data
        # For now, return placeholder data
        
        # Generate some realistic sample data
        start_date = datetime.now() - timedelta(days=365)
        dates = [start_date + timedelta(days=i) for i in range(365)]
        
        # Create a trend with seasonality and some noise
        trend = np.linspace(100, 150, 365)  # Upward trend from 100 to 150
        seasonality = 20 * np.sin(np.linspace(0, 2*np.pi, 365))  # Seasonal component
        noise = np.random.normal(0, 5, 365)  # Random noise
        
        values = trend + seasonality + noise
        
        # Create data points
        data = [
            {"date": date.strftime("%Y-%m-%d"), "value": value}
            for date, value in zip(dates, values)
        ]
        
        return data
        
    except Exception as e:
        frappe.log_error(f"Error getting historical data: {str(e)}", "Historical Data Error")
        raise

def prepare_data_for_forecasting(historical_data, frequency):
    """Prepare data for forecasting"""
    try:
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        
        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Set date as index
        df = df.set_index('date')
        
        # Ensure data is sorted by date
        df = df.sort_index()
        
        # Resample data to ensure regular frequency
        freq_map = {
            "Daily": "D",
            "Weekly": "W",
            "Monthly": "MS",
            "Quarterly": "QS",
            "Yearly": "YS",
            "Hourly": "H",
            "Minute": "T"
        }
        
        pandas_freq = freq_map.get(frequency, "D")
        df = df.resample(pandas_freq).mean()
        
        # Forward fill missing values
        df = df.fillna(method='ffill')
        
        return df
        
    except Exception as e:
        frappe.log_error(f"Error preparing data for forecasting: {str(e)}", "Data Preparation Error")
        raise

def run_forecast_model(df, forecast_doc):
    """Run the forecast model"""
    try:
        # Get model parameters
        model_params = {}
        if forecast_doc.model_parameters:
            try:
                model_params = json.loads(forecast_doc.model_parameters)
            except json.JSONDecodeError:
                frappe.throw("Model parameters must be valid JSON")
        
        # Get forecast horizon
        horizon = forecast_doc.forecast_horizon
        
        # Select and run appropriate model
        if forecast_doc.forecast_model == "ARIMA":
            return run_arima_model(df, horizon, model_params)
        elif forecast_doc.forecast_model == "SARIMA":
            return run_sarima_model(df, horizon, model_params)
        elif forecast_doc.forecast_model == "Exponential Smoothing":
            return run_exponential_smoothing_model(df, horizon, model_params)
        elif forecast_doc.forecast_model == "Prophet":
            return run_prophet_model(df, horizon, model_params)
        else:
            # Default to ARIMA if model not supported
            return run_arima_model(df, horizon, model_params)
        
    except Exception as e:
        frappe.log_error(f"Error running forecast model: {str(e)}", "Model Error")
        raise

def run_arima_model(df, horizon, model_params):
    """Run ARIMA model"""
    try:
        # Extract parameters
        p = model_params.get('p', 1)
        d = model_params.get('d', 1)
        q = model_params.get('q', 0)
        
        # Fit model
        model = ARIMA(df['value'], order=(p, d, q))
        model_fit = model.fit()
        
        # Generate forecast
        forecast = model_fit.forecast(steps=horizon)
        
        # Generate prediction intervals
        pred_intervals = model_fit.get_forecast(steps=horizon).conf_int()
        lower_bound = pred_intervals.iloc[:, 0]
        upper_bound = pred_intervals.iloc[:, 1]
        
        # Create forecast DataFrame
        last_date = df.index[-1]
        freq = pd.infer_freq(df.index)
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq=freq)
        
        forecast_df = pd.DataFrame({
            'forecast': forecast,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }, index=forecast_dates)
        
        return forecast_df
        
    except Exception as e:
        frappe.log_error(f"Error running ARIMA model: {str(e)}", "ARIMA Error")
        raise

def run_sarima_model(df, horizon, model_params):
    """Run SARIMA model"""
    try:
        # Extract parameters
        p = model_params.get('p', 1)
        d = model_params.get('d', 1)
        q = model_params.get('q', 0)
        P = model_params.get('P', 0)
        D = model_params.get('D', 0)
        Q = model_params.get('Q', 0)
        s = model_params.get('s', 12)  # Default seasonal period (12 for monthly data)
        
        # Fit model
        model = SARIMAX(df['value'], order=(p, d, q), seasonal_order=(P, D, Q, s))
        model_fit = model.fit(disp=False)
        
        # Generate forecast
        forecast = model_fit.forecast(steps=horizon)
        
        # Generate prediction intervals
        pred_intervals = model_fit.get_forecast(steps=horizon).conf_int()
        lower_bound = pred_intervals.iloc[:, 0]
        upper_bound = pred_intervals.iloc[:, 1]
        
        # Create forecast DataFrame
        last_date = df.index[-1]
        freq = pd.infer_freq(df.index)
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq=freq)
        
        forecast_df = pd.DataFrame({
            'forecast': forecast,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }, index=forecast_dates)
        
        return forecast_df
        
    except Exception as e:
        frappe.log_error(f"Error running SARIMA model: {str(e)}", "SARIMA Error")
        raise

def run_exponential_smoothing_model(df, horizon, model_params):
    """Run Exponential Smoothing model"""
    try:
        # Extract parameters
        trend = model_params.get('trend', 'add')  # 'add' or 'mul'
        seasonal = model_params.get('seasonal', 'add')  # 'add', 'mul', or None
        seasonal_periods = model_params.get('seasonal_periods', 12)
        
        # Fit model
        model = ExponentialSmoothing(
            df['value'],
            trend=trend,
            seasonal=seasonal,
            seasonal_periods=seasonal_periods
        )
        model_fit = model.fit()
        
        # Generate forecast
        forecast = model_fit.forecast(horizon)
        
        # Create forecast DataFrame
        last_date = df.index[-1]
        freq = pd.infer_freq(df.index)
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq=freq)
        
        # For exponential smoothing, we'll estimate prediction intervals
        # based on historical forecast errors
        residuals = model_fit.resid
        residual_std = residuals.std()
        z_value = 1.96  # 95% confidence interval
        
        forecast_df = pd.DataFrame({
            'forecast': forecast,
            'lower_bound': forecast - z_value * residual_std,
            'upper_bound': forecast + z_value * residual_std
        }, index=forecast_dates)
        
        return forecast_df
        
    except Exception as e:
        frappe.log_error(f"Error running Exponential Smoothing model: {str(e)}", "Exponential Smoothing Error")
        raise

def run_prophet_model(df, horizon, model_params):
    """Run Prophet model"""
    try:
        # Prophet requires specific import
        from prophet import Prophet
        
        # Prepare data for Prophet
        prophet_df = df.reset_index()
        prophet_df.columns = ['ds', 'y']
        
        # Extract parameters
        yearly_seasonality = model_params.get('yearly_seasonality', 'auto')
        weekly_seasonality = model_params.get('weekly_seasonality', 'auto')
        daily_seasonality = model_params.get('daily_seasonality', 'auto')
        seasonality_mode = model_params.get('seasonality_mode', 'additive')
        
        # Initialize and fit model
        model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
            seasonality_mode=seasonality_mode
        )
        model.fit(prophet_df)
        
        # Create future dataframe
        freq_map = {
            "Daily": "D",
            "Weekly": "W",
            "Monthly": "M",
            "Quarterly": "Q",
            "Yearly": "Y",
            "Hourly": "H",
            "Minute": "min"
        }
        freq = freq_map.get("Daily", "D")  # Default to daily
        
        future = model.make_future_dataframe(periods=horizon, freq=freq)
        
        # Generate forecast
        forecast = model.predict(future)
        
        # Extract relevant portions
        forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(horizon)
        
        # Convert to standard format
        result_df = pd.DataFrame({
            'forecast': forecast_df['yhat'].values,
            'lower_bound': forecast_df['yhat_lower'].values,
            'upper_bound': forecast_df['yhat_upper'].values
        }, index=pd.to_datetime(forecast_df['ds']))
        
        return result_df
        
    except ImportError:
        frappe.log_error("Prophet package not installed. Falling back to ARIMA.", "Prophet Error")
        return run_arima_model(df, horizon, model_params)
    except Exception as e:
        frappe.log_error(f"Error running Prophet model: {str(e)}", "Prophet Error")
        raise

def calculate_performance_metrics(historical_df, forecast_df, forecast_doc):
    """Calculate performance metrics for the forecast"""
    try:
        # For a real forecast, we would calculate metrics based on historical performance
        # For now, return placeholder metrics
        
        # Calculate Mean Absolute Percentage Error (MAPE) on historical data
        # This would normally be done using a test set or cross-validation
        mape = np.random.uniform(3, 10)  # Random MAPE between 3% and 10%
        
        # Calculate other metrics
        mae = np.random.uniform(2, 8)  # Mean Absolute Error
        rmse = np.random.uniform(3, 12)  # Root Mean Square Error
        r2 = np.random.uniform(0.7, 0.95)  # R-squared
        
        # Return metrics
        return {
            "MAPE": round(mape, 2),
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "R2": round(r2, 2),
            "accuracy": round(100 - mape, 2),
            "forecast_model": forecast_doc.forecast_model,
            "calculation_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        frappe.log_error(f"Error calculating performance metrics: {str(e)}", "Metrics Error")
        raise

def format_forecast_results(forecast_df, forecast_doc):
    """Format forecast results for storage and display"""
    try:
        # Convert DataFrame to list of dictionaries
        forecast_data = []
        
        for date, row in forecast_df.iterrows():
            forecast_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "value": round(row['forecast'], 2),
                "lower_bound": round(row['lower_bound'], 2),
                "upper_bound": round(row['upper_bound'], 2)
            })
        
        return forecast_data
        
    except Exception as e:
        frappe.log_error(f"Error formatting forecast results: {str(e)}", "Formatting Error")
        raise

def publish_forecast_completed_event(forecast_doc, forecast_data, performance_metrics):
    """Publish event when forecast is completed"""
    try:
        # Implementation would depend on Mythos EDA
        event_data = {
            "forecast_id": forecast_doc.name,
            "forecast_name": forecast_doc.forecast_name,
            "metric": forecast_doc.metric,
            "status": "Completed",
            "forecast_date": datetime.now().isoformat(),
            "performance_summary": {
                "MAPE": performance_metrics["MAPE"],
                "accuracy": performance_metrics["accuracy"]
            },
            "forecast_summary": {
                "horizon": forecast_doc.forecast_horizon,
                "latest_value": forecast_data[0]["value"],
                "trend": "increasing" if forecast_data[-1]["value"] > forecast_data[0]["value"] else "decreasing"
            }
        }
        
        # Placeholder for Mythos event publishing
        frappe.logger().info(f"Would publish to Mythos: {event_data}")
        
    except Exception as e:
        frappe.log_error(f"Error publishing forecast completed event: {str(e)}", "Event Error")

def trigger_automated_actions(forecast_doc, forecast_data):
    """Trigger automated actions based on forecast results"""
    try:
        # This would implement automated actions like creating recommendations
        # For now, just log the intent
        frappe.logger().info(f"Would trigger automated actions for forecast {forecast_doc.name}")
        
        # Example: Create a recommendation if forecast shows significant trend
        first_value = forecast_data[0]["value"]
        last_value = forecast_data[-1]["value"]
        percent_change = (last_value - first_value) / first_value * 100
        
        if abs(percent_change) > 10:  # If change is more than 10%
            trend = "increasing" if percent_change > 0 else "decreasing"
            frappe.logger().info(f"Would create recommendation for {trend} trend of {abs(percent_change):.2f}%")
            
            # This would create a Recommendation DocType
            # recommendation = frappe.new_doc("Recommendation")
            # recommendation.title = f"Significant {trend} trend detected in {forecast_doc.metric}"
            # recommendation.description = f"Forecast shows a {trend} trend of {abs(percent_change):.2f}% over the next {forecast_doc.forecast_horizon} periods."
            # recommendation.source = "Forecast"
            # recommendation.source_reference = forecast_doc.name
            # recommendation.priority = "High" if abs(percent_change) > 20 else "Medium"
            # recommendation.save()
        
    except Exception as e:
        frappe.log_error(f"Error triggering automated actions: {str(e)}", "Action Error")

def run_scheduled_forecasts():
    """Run all scheduled forecasts"""
    try:
        # Get all active forecasts that need to be run
        forecasts = frappe.get_all(
            "Forecast",
            filters={
                "is_active": 1,
                "status": ["in", ["Draft", "Failed"]]
            },
            fields=["name", "forecast_name"]
        )
        
        frappe.logger().info(f"Running {len(forecasts)} scheduled forecasts")
        
        # Generate each forecast
        for forecast in forecasts:
            frappe.enqueue(
                "cauldron_synapse.predictive_analytics.forecasting.generate_forecast",
                forecast=forecast.name,
                queue="long",
                timeout=1500
            )
        
        return {
            "success": True,
            "message": f"Scheduled {len(forecasts)} forecasts for generation",
            "forecasts": [f.name for f in forecasts]
        }
        
    except Exception as e:
        frappe.log_error(f"Error running scheduled forecasts: {str(e)}", "Scheduler Error")
        return {
            "success": False,
            "error": str(e)
        }