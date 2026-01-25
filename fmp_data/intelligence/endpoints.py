from fmp_data.intelligence.models import (
    CrowdfundingOffering,
    CrowdfundingOfferingSearchItem,
    CryptoNewsArticle,
    DividendEvent,
    EarningConfirmed,
    EarningEvent,
    EarningSurprise,
    EquityOffering,
    EquityOfferingSearchItem,
    ESGBenchmark,
    ESGData,
    ESGRating,
    FMPArticle,
    ForexNewsArticle,
    GeneralNewsArticle,
    HistoricalRating,
    HistoricalSocialSentiment,
    HistoricalStockGrade,
    HouseDisclosure,
    IPOEvent,
    PressRelease,
    PressReleaseBySymbol,
    PriceTargetNews,
    RatingsSnapshot,
    SenateTrade,
    SocialSentimentChanges,
    StockGrade,
    StockGradeNews,
    StockGradesConsensus,
    StockNewsArticle,
    StockNewsSentiment,
    StockSplitEvent,
    TrendingSocialSentiment,
)
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    ParamLocation,
    ParamType,
    URLType,
)

EARNINGS_CALENDAR: Endpoint = Endpoint(
    name="earnings_calendar",
    path="earnings-calendar",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get earnings calendar",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="End date",
            alias="to",
        ),
    ],
    response_model=EarningEvent,
)

EARNINGS_CONFIRMED: Endpoint = Endpoint(
    name="earnings_confirmed",
    path="earning-calendar-confirmed",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get confirmed earnings dates",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="End date",
            alias="to",
        ),
    ],
    response_model=EarningConfirmed,
)

EARNINGS_SURPRISES: Endpoint = Endpoint(
    name="earnings_surprises",
    path="earnings-surprises",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get earnings surprises",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=EarningSurprise,
)

HISTORICAL_EARNINGS: Endpoint = Endpoint(
    name="historical_earnings",
    path="historical/earning-calendar",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get historical earnings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=EarningEvent,
)

DIVIDENDS_CALENDAR: Endpoint = Endpoint(
    name="dividends_calendar",
    path="dividends-calendar",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get dividends calendar",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="End date",
            alias="to",
        ),
    ],
    response_model=DividendEvent,
)

STOCK_SPLITS_CALENDAR: Endpoint = Endpoint(
    name="stock_splits_calendar",
    path="splits-calendar",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get stock splits calendar",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="End date",
            alias="to",
        ),
    ],
    response_model=StockSplitEvent,
)

IPO_CALENDAR: Endpoint = Endpoint(
    name="ipo_calendar",
    path="ipos-calendar",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get IPO calendar",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
    ],
    response_model=IPOEvent,
)

FMP_ARTICLES_ENDPOINT: Endpoint = Endpoint(
    name="fmp_articles",
    path="fmp-articles",
    version=APIVersion.STABLE,
    description="Get a list of the latest FMP articles",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of articles per page",
            default=20,
        ),
    ],
    response_model=FMPArticle,
)

GENERAL_NEWS_ENDPOINT: Endpoint = Endpoint(
    name="general_news",
    path="news/general-latest",
    version=APIVersion.STABLE,
    description="Get a list of the latest general news articles",
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=GeneralNewsArticle,
)

STOCK_NEWS_ENDPOINT: Endpoint = Endpoint(
    name="stock_news",
    path="news/stock-latest",
    version=APIVersion.STABLE,
    description="Get a list of the latest stock news articles",
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=StockNewsArticle,
)

STOCK_SYMBOL_NEWS_ENDPOINT: Endpoint = Endpoint(
    name="stock_news_symbol",
    path="news/stock",
    version=APIVersion.STABLE,
    description="Get a list of the latest news for a specific stock",
    optional_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Symbol of the stock to get news for.",
            alias="symbols",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=StockNewsArticle,
)

STOCK_NEWS_SENTIMENTS_ENDPOINT: Endpoint = Endpoint(
    name="stock_news_sentiments",
    path="stock-news-sentiments-rss-feed",
    version=APIVersion.V4,
    description="[DEPRECATED] This endpoint is no longer available on the FMP API",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Page number",
        ),
    ],
    optional_params=[],
    response_model=StockNewsSentiment,
)

FOREX_NEWS_ENDPOINT: Endpoint = Endpoint(
    name="forex_news",
    path="news/forex-latest",
    version=APIVersion.STABLE,
    description="Get a list of the latest forex news articles",
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=ForexNewsArticle,
)

CRYPTO_NEWS_ENDPOINT: Endpoint = Endpoint(
    name="crypto_news",
    path="news/crypto-latest",
    version=APIVersion.STABLE,
    description="Get a list of the latest crypto news articles",
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=CryptoNewsArticle,
)

FOREX_SYMBOL_NEWS_ENDPOINT: Endpoint = Endpoint(
    name="forex_news_symbol",
    path="news/forex",
    version=APIVersion.STABLE,
    description="Search forex news articles by currency pair",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Forex symbol",
            alias="symbols",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    response_model=ForexNewsArticle,
)

CRYPTO_SYMBOL_NEWS_ENDPOINT: Endpoint = Endpoint(
    name="crypto_news_symbol",
    path="news/crypto",
    version=APIVersion.STABLE,
    description="Search crypto news articles by trading pair",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Crypto symbol",
            alias="symbols",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    response_model=CryptoNewsArticle,
)

PRESS_RELEASES_ENDPOINT: Endpoint = Endpoint(
    name="press_releases",
    path="news/press-releases-latest",
    version=APIVersion.STABLE,
    description="Get a list of the latest press releases",
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of releases to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=PressRelease,
)

PRESS_RELEASES_BY_SYMBOL_ENDPOINT: Endpoint = Endpoint(
    name="press_releases_by_symbol",
    path="news/press-releases",
    version=APIVersion.STABLE,
    description="Get a list of the latest press releases for a specific company",
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            default=0,
            description="Page number",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of releases to return",
            default=20,
        ),
    ],
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company symbol",
            alias="symbols",
        )
    ],
    response_model=PressReleaseBySymbol,
)

HISTORICAL_SOCIAL_SENTIMENT_ENDPOINT: Endpoint = Endpoint(
    name="historical_social_sentiment",
    path="historical/social-sentiment",
    version=APIVersion.STABLE,
    description="Get historical social sentiment data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Page number",
        ),
    ],
    response_model=HistoricalSocialSentiment,
)

TRENDING_SOCIAL_SENTIMENT_ENDPOINT: Endpoint = Endpoint(
    name="trending_social_sentiment",
    path="social-sentiments/trending",
    version=APIVersion.STABLE,
    description="Get trending social sentiment data",
    mandatory_params=[
        EndpointParam(
            name="type",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Sentiment type (bullish, bearish)",
        ),
        EndpointParam(
            name="source",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Sentiment source (stocktwits)",
        ),
    ],
    optional_params=[],
    response_model=TrendingSocialSentiment,
)

SOCIAL_SENTIMENT_CHANGES_ENDPOINT: Endpoint = Endpoint(
    name="social_sentiment_changes",
    path="social-sentiments/change",
    version=APIVersion.STABLE,
    description="Get changes in social sentiment data",
    mandatory_params=[
        EndpointParam(
            name="type",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Sentiment type (bullish, bearish)",
        ),
        EndpointParam(
            name="source",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Sentiment source (stocktwits)",
        ),
    ],
    optional_params=[],
    response_model=SocialSentimentChanges,
)

# ESG Endpoints
ESG_DATA: Endpoint[ESGData] = Endpoint(
    name="esg_data",
    path="esg-disclosures",
    version=APIVersion.STABLE,
    description="Get ESG data for a company",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company symbol",
        )
    ],
    optional_params=[],
    response_model=ESGData,
)

ESG_RATINGS: Endpoint[ESGRating] = Endpoint(
    name="esg_ratings",
    path="esg-ratings",
    version=APIVersion.STABLE,
    description="Get ESG ratings for a company",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company symbol",
        )
    ],
    optional_params=[],
    response_model=ESGRating,
)

ESG_BENCHMARK: Endpoint = Endpoint(
    name="esg_benchmark",
    path="esg-benchmark",
    version=APIVersion.STABLE,
    description="Get ESG benchmark data",
    mandatory_params=[],
    optional_params=[],
    response_model=ESGBenchmark,
)

# Government Trading Endpoints
SENATE_LATEST: Endpoint = Endpoint(
    name="senate_latest",
    path="senate-latest",
    version=APIVersion.STABLE,
    description="Get latest Senate financial disclosures",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of results",
            default=100,
        ),
    ],
    optional_params=[],
    response_model=SenateTrade,
)

SENATE_TRADING: Endpoint = Endpoint(
    name="senate_trading",
    path="senate-trades",
    version=APIVersion.STABLE,
    description="Get Senate trading data by symbol",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=SenateTrade,
)

SENATE_TRADES_BY_NAME: Endpoint = Endpoint(
    name="senate_trades_by_name",
    path="senate-trades-by-name",
    version=APIVersion.STABLE,
    description="Get Senate trading data by name",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Senator first or last name",
        )
    ],
    optional_params=[],
    response_model=SenateTrade,
)

SENATE_TRADING_RSS: Endpoint = Endpoint(
    name="senate_trading_rss",
    path="senate-trading-rss-feed",
    version=APIVersion.STABLE,
    description="Get Senate trading RSS feed",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Page number",
            default=0,
        )
    ],
    optional_params=[],
    response_model=SenateTrade,
)

HOUSE_LATEST: Endpoint = Endpoint(
    name="house_latest",
    path="house-latest",
    version=APIVersion.STABLE,
    description="Get latest House financial disclosures",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of results",
            default=100,
        ),
    ],
    optional_params=[],
    response_model=HouseDisclosure,
)

HOUSE_DISCLOSURE: Endpoint = Endpoint(
    name="house_disclosure",
    path="house-trades",
    version=APIVersion.STABLE,
    description="Get House trading data by symbol",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=HouseDisclosure,
)

HOUSE_TRADES_BY_NAME: Endpoint = Endpoint(
    name="house_trades_by_name",
    path="house-trades-by-name",
    version=APIVersion.STABLE,
    description="Get House trading data by name",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Representative first or last name",
        )
    ],
    optional_params=[],
    response_model=HouseDisclosure,
)

# Fundraising Endpoints
CROWDFUNDING_RSS: Endpoint = Endpoint(
    name="crowdfunding_rss",
    path="crowdfunding-offerings-latest",
    version=APIVersion.STABLE,
    description="Get latest crowdfunding offerings",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of results",
            default=100,
        ),
    ],
    optional_params=[],
    response_model=CrowdfundingOffering,
)

CROWDFUNDING_SEARCH: Endpoint = Endpoint(
    name="crowdfunding_search",
    path="crowdfunding-offerings-search",
    version=APIVersion.STABLE,
    description="Search crowdfunding offerings",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company or offering name",
        )
    ],
    optional_params=[],
    response_model=CrowdfundingOfferingSearchItem,
)

CROWDFUNDING_BY_CIK: Endpoint = Endpoint(
    name="crowdfunding_by_cik",
    path="crowdfunding-offerings",
    version=APIVersion.STABLE,
    description="Get crowdfunding offerings by CIK",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company CIK number",
        )
    ],
    optional_params=[],
    response_model=CrowdfundingOffering,
)

EQUITY_OFFERING_RSS: Endpoint = Endpoint(
    name="equity_offering_rss",
    path="fundraising-latest",
    version=APIVersion.STABLE,
    description="Get latest equity offerings",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of results",
            default=10,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Company CIK number",
        ),
    ],
    response_model=EquityOffering,
)

EQUITY_OFFERING_SEARCH: Endpoint = Endpoint(
    name="equity_offering_search",
    path="fundraising-search",
    version=APIVersion.STABLE,
    description="Search equity offerings",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company or offering name",
        )
    ],
    optional_params=[],
    response_model=EquityOfferingSearchItem,
)

EQUITY_OFFERING_BY_CIK: Endpoint = Endpoint(
    name="equity_offering_by_cik",
    path="fundraising",
    version=APIVersion.STABLE,
    description="Get equity offerings by CIK",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company CIK number",
        )
    ],
    optional_params=[],
    response_model=EquityOffering,
)

# Analyst Ratings and Grades Endpoints
RATINGS_SNAPSHOT: Endpoint[RatingsSnapshot] = Endpoint(
    name="ratings_snapshot",
    path="ratings-snapshot",
    version=APIVersion.STABLE,
    description="Get current analyst ratings snapshot",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=RatingsSnapshot,
)

RATINGS_HISTORICAL: Endpoint = Endpoint(
    name="ratings_historical",
    path="ratings-historical",
    version=APIVersion.STABLE,
    description="Get historical analyst ratings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results",
            default=100,
        )
    ],
    response_model=HistoricalRating,
)

PRICE_TARGET_NEWS: Endpoint = Endpoint(
    name="price_target_news",
    path="price-target-news",
    version=APIVersion.STABLE,
    description="Get price target news",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        )
    ],
    response_model=PriceTargetNews,
)

PRICE_TARGET_LATEST_NEWS: Endpoint = Endpoint(
    name="price_target_latest_news",
    path="price-target-latest-news",
    version=APIVersion.STABLE,
    description="Get latest price target news",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        )
    ],
    response_model=PriceTargetNews,
)

GRADES: Endpoint = Endpoint(
    name="grades",
    path="grades",
    version=APIVersion.STABLE,
    description="Get stock grades from analysts",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        )
    ],
    response_model=StockGrade,
)

GRADES_HISTORICAL: Endpoint = Endpoint(
    name="grades_historical",
    path="grades-historical",
    version=APIVersion.STABLE,
    description="Get historical stock grades",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results",
            default=100,
        )
    ],
    response_model=HistoricalStockGrade,
)

GRADES_CONSENSUS: Endpoint[StockGradesConsensus] = Endpoint(
    name="grades_consensus",
    path="grades-consensus",
    version=APIVersion.STABLE,
    description="Get stock grades consensus summary",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=StockGradesConsensus,
)

GRADES_NEWS: Endpoint = Endpoint(
    name="grades_news",
    path="grades-news",
    version=APIVersion.STABLE,
    description="Get stock grade news",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        )
    ],
    response_model=StockGradeNews,
)

GRADES_LATEST_NEWS: Endpoint = Endpoint(
    name="grades_latest_news",
    path="grades-latest-news",
    version=APIVersion.STABLE,
    description="Get latest stock grade news",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        )
    ],
    response_model=StockGradeNews,
)
