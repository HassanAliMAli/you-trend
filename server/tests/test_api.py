import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Adjust the import according to your project structure
# This assumes main.py is in the parent directory of the tests directory (e.g., server/main.py)
from server.main import app  # Or: from ..main import app


@pytest.fixture(scope="module")
def client():
    # Create a TestClient instance using your FastAPI app
    with TestClient(app) as c:
        yield c

# --- Mock Data Examples (adjust as needed for your API responses) ---

@pytest.fixture
def mock_youtube_api_responses():
    """Provides mock responses for youtube_api.py functions."""
    return {
        'fetch_search_results': MagicMock(return_value=([
            {'id': 'video1', 'title': 'Test Video 1', 'views': 1000, 'channelTitle': 'Test Channel'}
        ], 'nextPageToken')),
        'fetch_video_details': MagicMock(return_value=([
            {'id': 'video1', 'statistics': {'viewCount': '1000', 'likeCount': '100', 'commentCount': '10'}, 'snippet': {'publishedAt': '2023-01-01T00:00:00Z'}}
        ])),
        'fetch_channel_details': MagicMock(return_value=([
            {'id': 'channel1', 'statistics': {'subscriberCount': '5000', 'videoCount': '50'}}
        ])),
        # Add other mocks as needed for functions in youtube_api.py
    }

# --- Test Cases for API Endpoints ---

@patch('server.utils.youtube_api.fetch_search_results')
@patch('server.utils.youtube_api.fetch_video_details') # Add more patches if trends endpoint uses more youtube_api functions
@patch('server.utils.data_processor.process_trend_data') # Assuming this function exists and is used
def test_trends_endpoint(mock_process_data, mock_fetch_video_details, mock_fetch_search_results, client, mock_youtube_api_responses):
    """Test the /api/trends endpoint."""
    # Setup mocks
    mock_fetch_search_results.return_value = mock_youtube_api_responses['fetch_search_results'].return_value
    mock_fetch_video_details.return_value = mock_youtube_api_responses['fetch_video_details'].return_value
    mock_process_data.return_value = {'top_videos': [], 'top_channels': [], 'related_topics': []} # Example processed data

    response = client.get("/api/trends?keyword=test&country=US")
    assert response.status_code == 200
    data = response.json()
    assert "top_videos" in data
    assert "top_channels" in data
    mock_fetch_search_results.assert_called_once()
    # Add more assertions based on your expected response structure and mock_process_data output


@patch('server.utils.youtube_api.fetch_search_results') # Assuming compare endpoint uses search
@patch('server.utils.data_processor.process_comparison_data') # Assuming this function exists
def test_compare_endpoint(mock_process_comparison, mock_fetch_search_results_compare, client, mock_youtube_api_responses):
    """Test the /api/compare endpoint."""
    mock_fetch_search_results_compare.return_value = mock_youtube_api_responses['fetch_search_results'].return_value
    mock_process_comparison.return_value = {'niche1_data': {}, 'niche2_data': {}} # Example

    response = client.post("/api/compare", json={"niches": ["niche1", "niche2"], "country": "US"})
    assert response.status_code == 200
    data = response.json()
    assert "niche1_data" in data
    mock_fetch_search_results_compare.assert_called()
    # Add more assertions


@patch('server.utils.report_generator.generate_text_report') # Patch the actual report generation function
def test_reports_endpoint_txt(mock_generate_report, client):
    """Test the /api/reports endpoint for TXT generation."""
    mock_generate_report.return_value = "Sample Text Report Content"

    response = client.post("/api/reports", json={
        "report_type": "txt",
        "data": {"videos": [{"title": "v1"}], "channels": []} # Example data
    })
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "Sample Text Report Content" in response.text
    mock_generate_report.assert_called_once()


@patch('server.utils.report_generator.generate_csv_report')
def test_reports_endpoint_csv(mock_generate_report, client):
    """Test the /api/reports endpoint for CSV generation."""
    mock_generate_report.return_value = "col1,col2\nval1,val2"
    
    response = client.post("/api/reports", json={
        "report_type": "csv",
        "data": {"videos": [{"title": "v1"}], "channels": []} 
    })
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "col1,col2" in response.text
    mock_generate_report.assert_called_once()

# Add similar tests for XLSX and PDF report types, mocking their respective generator functions
# e.g., test_reports_endpoint_xlsx, test_reports_endpoint_pdf

# Placeholder for a test for the /api/status endpoint
def test_status_endpoint(client):
    """Test the /api/status endpoint."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "API is running"
    assert "version" in data 
    # Add more specific checks if your status endpoint returns more info like API key validity or quota


# Example of how to run a specific test if needed, though pytest will discover them
# if __name__ == "__main__":
#     pytest.main([__file__]) 