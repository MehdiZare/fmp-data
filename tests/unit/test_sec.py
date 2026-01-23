# tests/unit/test_sec.py
"""Tests for the SEC module endpoints"""

from datetime import date
from unittest.mock import patch

import pytest

from fmp_data.sec.models import (
    IndustryClassification,
    SECCompanySearchResult,
    SECFiling8K,
    SECFilingSearchResult,
    SECFinancialFiling,
    SECProfile,
    SICCode,
)


@pytest.fixture
def industry_classification_data():
    """Mock industry classification data"""
    return {
        "symbol": "AAPL",
        "name": "APPLE INC.",
        "cik": "0000320193",
        "sicCode": "3571",
        "industryTitle": "ELECTRONIC COMPUTERS",
        "businessAddress": "['ONE APPLE PARK WAY', 'CUPERTINO CA 95014']",
        "phoneNumber": "(408) 996-1010",
    }


class TestSECModels:
    """Tests for SEC model validation"""

    @pytest.fixture
    def filing_8k_data(self):
        """Mock SEC 8-K filing data"""
        return {
            "symbol": "AAPL",
            "cik": "0000320193",
            "formType": "8-K",
            "acceptedDate": "2024-01-15T08:30:00.000+0000",
            "filingDate": "2024-01-15",
            "finalLink": "https://www.sec.gov/Archives/...",
            "linkToTxt": "https://www.sec.gov/Archives/...txt",
            "linkToHtml": "https://www.sec.gov/Archives/...html",
            "linkToFilingDetails": "https://www.sec.gov/cgi-bin/...",
        }

    @pytest.fixture
    def financial_filing_data(self):
        """Mock SEC financial filing data"""
        return {
            "symbol": "AAPL",
            "cik": "0000320193",
            "formType": "10-K",
            "acceptedDate": "2024-01-15T08:30:00.000+0000",
            "filingDate": "2024-01-15",
            "finalLink": "https://www.sec.gov/Archives/...",
            "linkToXbrl": "https://www.sec.gov/Archives/...xbrl",
        }

    @pytest.fixture
    def company_search_data(self):
        """Mock SEC company search result"""
        return {
            "symbol": "AAPL",
            "cik": "0000320193",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "sicCode": "3571",
            "sicDescription": "Electronic Computers",
            "state": "CA",
            "fiscalYearEnd": "09",
        }

    @pytest.fixture
    def sec_profile_data(self):
        """Mock SEC profile data"""
        return {
            "symbol": "AAPL",
            "cik": "0000320193",
            "companyName": "Apple Inc.",
            "exchange": "NASDAQ",
            "sicCode": "3571",
            "sicDescription": "Electronic Computers",
            "stateLocation": "CA",
            "stateOfIncorporation": "CA",
            "fiscalYearEnd": "09",
            "businessAddress": "One Apple Park Way, Cupertino CA",
            "businessPhone": "4089961010",
        }

    @pytest.fixture
    def sic_code_data(self):
        """Mock SIC code data"""
        return {
            "sicCode": "3571",
            "industryTitle": "Electronic Computers",
            "office": "Office of Technology",
        }

    @pytest.fixture
    def industry_classification_data(self):
        """Mock industry classification data"""
        return {
            "symbol": "AAPL",
            "name": "APPLE INC.",
            "cik": "0000320193",
            "sicCode": "3571",
            "industryTitle": "ELECTRONIC COMPUTERS",
            "businessAddress": "['ONE APPLE PARK WAY', 'CUPERTINO CA 95014']",
            "phoneNumber": "(408) 996-1010",
        }

    def test_sec_filing_8k_model(self, filing_8k_data):
        """Test SECFiling8K model validation"""
        filing = SECFiling8K.model_validate(filing_8k_data)
        assert filing.symbol == "AAPL"
        assert filing.cik == "0000320193"
        assert filing.form_type == "8-K"
        assert filing.final_link is not None

    def test_sec_financial_filing_model(self, financial_filing_data):
        """Test SECFinancialFiling model validation"""
        filing = SECFinancialFiling.model_validate(financial_filing_data)
        assert filing.symbol == "AAPL"
        assert filing.form_type == "10-K"
        assert filing.link_to_xbrl is not None

    def test_sec_filing_search_result_model(self):
        """Test SECFilingSearchResult model validation"""
        data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "companyName": "Apple Inc.",
            "formType": "10-K",
            "acceptedDate": "2024-01-15T08:30:00.000+0000",
        }
        result = SECFilingSearchResult.model_validate(data)
        assert result.symbol == "AAPL"
        assert result.company_name == "Apple Inc."
        assert result.form_type == "10-K"

    def test_sec_company_search_result_model(self, company_search_data):
        """Test SECCompanySearchResult model validation"""
        result = SECCompanySearchResult.model_validate(company_search_data)
        assert result.symbol == "AAPL"
        assert result.company_name == "Apple Inc."
        assert result.sic_code == "3571"
        assert result.sic_description == "Electronic Computers"

    def test_sec_profile_model(self, sec_profile_data):
        """Test SECProfile model validation"""
        profile = SECProfile.model_validate(sec_profile_data)
        assert profile.symbol == "AAPL"
        assert profile.company_name == "Apple Inc."
        assert profile.state_location == "CA"
        assert profile.business_phone == "4089961010"

    def test_sic_code_model(self, sic_code_data):
        """Test SICCode model validation"""
        sic = SICCode.model_validate(sic_code_data)
        assert sic.sic_code == "3571"
        assert sic.industry == "Electronic Computers"
        assert sic.office == "Office of Technology"

    def test_industry_classification_model(self, industry_classification_data):
        """Test IndustryClassification model validation"""
        entry = IndustryClassification.model_validate(industry_classification_data)
        assert entry.symbol == "AAPL"
        assert entry.name == "APPLE INC."
        assert entry.sic_code == "3571"
        assert entry.industry_title == "ELECTRONIC COMPUTERS"


class TestSECClient:
    """Tests for SECClient methods"""

    @pytest.fixture
    def filing_8k_data(self):
        """Mock 8-K data"""
        return {
            "symbol": "AAPL",
            "cik": "0000320193",
            "formType": "8-K",
        }

    @patch("httpx.Client.request")
    def test_get_latest_8k(
        self, mock_request, fmp_client, mock_response, filing_8k_data
    ):
        """Test fetching latest 8-K filings"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[filing_8k_data]
        )
        result = fmp_client.sec.get_latest_8k(
            page=0,
            limit=10,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 2, 1),
        )
        assert len(result) == 1
        assert isinstance(result[0], SECFiling8K)
        assert result[0].form_type == "8-K"

    @patch("httpx.Client.request")
    def test_get_latest_financials(self, mock_request, fmp_client, mock_response):
        """Test fetching latest financial filings"""
        financial_data = {"symbol": "AAPL", "formType": "10-K"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[financial_data]
        )
        result = fmp_client.sec.get_latest_financials(
            page=0,
            limit=10,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 2, 1),
        )
        assert len(result) == 1
        assert isinstance(result[0], SECFinancialFiling)

    @patch("httpx.Client.request")
    def test_search_by_form_type(self, mock_request, fmp_client, mock_response):
        """Test searching filings by form type"""
        search_data = {"symbol": "AAPL", "formType": "10-K", "companyName": "Apple"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[search_data]
        )
        result = fmp_client.sec.search_by_form_type("10-K", page=0, limit=10)
        assert len(result) == 1
        assert isinstance(result[0], SECFilingSearchResult)
        assert result[0].form_type == "10-K"

    @patch("httpx.Client.request")
    def test_search_by_symbol(self, mock_request, fmp_client, mock_response):
        """Test searching filings by symbol"""
        search_data = {"symbol": "AAPL", "formType": "10-K"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[search_data]
        )
        result = fmp_client.sec.search_by_symbol("AAPL", page=0, limit=10)
        assert len(result) == 1
        assert isinstance(result[0], SECFilingSearchResult)

    @patch("httpx.Client.request")
    def test_search_by_cik(self, mock_request, fmp_client, mock_response):
        """Test searching filings by CIK"""
        search_data = {"cik": "0000320193", "formType": "10-K"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[search_data]
        )
        result = fmp_client.sec.search_by_cik("0000320193", page=0, limit=10)
        assert len(result) == 1
        assert isinstance(result[0], SECFilingSearchResult)

    @patch("httpx.Client.request")
    def test_search_company_by_name(self, mock_request, fmp_client, mock_response):
        """Test searching companies by name"""
        company_data = {"symbol": "AAPL", "companyName": "Apple Inc."}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_data]
        )
        result = fmp_client.sec.search_company_by_name("Apple", page=0, limit=10)
        assert len(result) == 1
        assert isinstance(result[0], SECCompanySearchResult)

    @patch("httpx.Client.request")
    def test_search_company_by_symbol(self, mock_request, fmp_client, mock_response):
        """Test searching companies by symbol"""
        company_data = {"symbol": "AAPL", "companyName": "Apple Inc."}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_data]
        )
        result = fmp_client.sec.search_company_by_symbol("AAPL")
        assert len(result) == 1
        assert isinstance(result[0], SECCompanySearchResult)

    @patch("httpx.Client.request")
    def test_get_profile(self, mock_request, fmp_client, mock_response):
        """Test fetching SEC profile"""
        profile_data = {"symbol": "AAPL", "companyName": "Apple Inc.", "cik": "320193"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[profile_data]
        )
        result = fmp_client.sec.get_profile("AAPL")
        assert isinstance(result, SECProfile)
        assert result.symbol == "AAPL"

    @patch("httpx.Client.request")
    def test_get_profile_empty(self, mock_request, fmp_client, mock_response):
        """Test fetching SEC profile with no results"""
        mock_request.return_value = mock_response(status_code=200, json_data=[])

        result = fmp_client.sec.get_profile("AAPL")
        assert result is None

    @patch("httpx.Client.request")
    def test_get_sic_codes(self, mock_request, fmp_client, mock_response):
        """Test fetching SIC codes"""
        sic_data = {"sicCode": "3571", "industry": "Electronic Computers"}
        sic_data2 = {"sicCode": "3572", "industry": "Data"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[sic_data, sic_data2]
        )
        result = fmp_client.sec.get_sic_codes()
        assert len(result) == 2
        assert isinstance(result[0], SICCode)
        assert result[0].sic_code == "3571"

    @patch("httpx.Client.request")
    def test_search_industry_classification(
        self, mock_request, fmp_client, mock_response, industry_classification_data
    ):
        """Test searching industry classification data"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[industry_classification_data]
        )
        result = fmp_client.sec.search_industry_classification(symbol="AAPL")
        assert len(result) == 1
        assert result[0].sic_code == "3571"

    @patch("httpx.Client.request")
    def test_get_all_industry_classification(
        self, mock_request, fmp_client, mock_response, industry_classification_data
    ):
        """Test fetching all industry classification records"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[industry_classification_data]
        )
        result = fmp_client.sec.get_all_industry_classification(page=0, limit=10)
        assert len(result) == 1
        assert result[0].symbol == "AAPL"
