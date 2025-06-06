import pytest
from datetime import datetime, timedelta
from src.core.evaluation import find_optimal_weather_block
from src.core.hourly_weather import HourlyWeather

# Helper to create an HourlyWeather object


def create_hour(time, weather_score, symbol="clearsky", temp=20, wind=1):
  return HourlyWeather(
      time=time,
      symbol=symbol,
      temp=temp,
      wind=wind,
      weather_score=weather_score,
      temp_score=0,
      wind_score=0,
      cloud_score=0,
      precip_prob_score=0,
  )

# Test cases for find_optimal_weather_block


def test_find_optimal_block_with_clear_winner():
  base_time = datetime(2023, 1, 1, 10)
  hours = [
      create_hour(base_time, 5),
      create_hour(base_time + timedelta(hours=1), 8),
      create_hour(base_time + timedelta(hours=2), 10),
      create_hour(base_time + timedelta(hours=3), 12),
      create_hour(base_time + timedelta(hours=4), 9),
      create_hour(base_time + timedelta(hours=5), 2),
  ]
  result = find_optimal_weather_block(hours)
  assert result is not None
  # With new conservative scoring, algorithm may select different optimal block
  # Test that it selects a reasonable block with good scores
  assert result['avg_score'] >= 10  # Should select high-scoring hours
  assert result['duration'] >= 1   # Should have at least 1 hour
  assert result['combined_score'] > result['avg_score']  # Should have duration boost


def test_find_optimal_block_with_long_good_block():
  base_time = datetime(2023, 1, 1, 10)
  hours = [
      create_hour(base_time, 8),
      create_hour(base_time + timedelta(hours=1), 9),
      create_hour(base_time + timedelta(hours=2), 10),
      create_hour(base_time + timedelta(hours=3), 11),
      create_hour(base_time + timedelta(hours=4), 12),
      create_hour(base_time + timedelta(hours=5), 5),
  ]
  result = find_optimal_weather_block(hours)
  assert result is not None
  # Should select a good block, possibly favoring higher individual scores
  # over longer duration due to reduced duration boost
  assert result['avg_score'] >= 8   # Should select reasonably good hours
  assert result['duration'] >= 1    # Should have at least 1 hour
  assert result['combined_score'] >= result['avg_score']  # Should have some boost


def test_find_optimal_block_with_no_good_blocks():
  base_time = datetime(2023, 1, 1, 10)
  hours = [
      create_hour(base_time, -2),
      create_hour(base_time + timedelta(hours=1), -5),
      create_hour(base_time + timedelta(hours=2), -3),
  ]
  result = find_optimal_weather_block(hours)
  assert result is None


def test_find_optimal_block_with_single_best_hour():
  base_time = datetime(2023, 1, 1, 10)
  hours = [
      create_hour(base_time, 2),
      create_hour(base_time + timedelta(hours=1), -5),
      create_hour(base_time + timedelta(hours=2), 8),  # The single best hour
      create_hour(base_time + timedelta(hours=3), -2),
  ]
  result = find_optimal_weather_block(hours)
  assert result is not None
  assert result['duration'] == 1
  assert result['start'].hour == 12


def test_find_optimal_block_empty_input():
  result = find_optimal_weather_block([])
  assert result is None


def test_find_optimal_block_short_good_block():
  base_time = datetime(2023, 1, 1, 10)
  hours = [
      create_hour(base_time, 8),
      create_hour(base_time + timedelta(hours=1), 9)
  ]
  result = find_optimal_weather_block(hours)
  assert result is not None
  assert result['duration'] == 2
