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
    SenateNetWorthAggregated,
    SenateNetWorthItem,
    SenatePosition,
    SenateProfile,
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

EARNINGS_CALENDAR: Endpoint[EarningEvent] = Endpoint(
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
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="include_report_times",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            description=(
                "Include report time, fiscal period and confirmation fields "
                "in the response"
            ),
            alias="includeReportTimes",
        ),
    ],
    response_model=EarningEvent,
)

EARNINGS_CONFIRMED: Endpoint[EarningConfirmed] = Endpoint(
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
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
    ],
    response_model=EarningConfirmed,
)

EARNINGS_SURPRISES: Endpoint[EarningSurprise] = Endpoint(
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
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=EarningSurprise,
)

HISTORICAL_EARNINGS: Endpoint[EarningEvent] = Endpoint(
    name="historical_earnings",
    path="earnings",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get historical and upcoming earnings reports for a symbol",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of reports to return",
        ),
        EndpointParam(
            name="include_report_times",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            description=(
                "Include report time, fiscal period and confirmation fields "
                "in the response"
            ),
            alias="includeReportTimes",
        ),
    ],
    response_model=EarningEvent,
)

DIVIDENDS_CALENDAR: Endpoint[DividendEvent] = Endpoint(
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
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
    ],
    response_model=DividendEvent,
)

STOCK_SPLITS_CALENDAR: Endpoint[StockSplitEvent] = Endpoint(
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
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
    ],
    response_model=StockSplitEvent,
)

IPO_CALENDAR: Endpoint[IPOEvent] = Endpoint(
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
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
    ],
    response_model=IPOEvent,
)

FMP_ARTICLES_ENDPOINT: Endpoint[FMPArticle] = Endpoint(
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
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of articles per page",
            default=20,
        ),
    ],
    response_model=FMPArticle,
)

GENERAL_NEWS_ENDPOINT: Endpoint[GeneralNewsArticle] = Endpoint(
    name="general_news",
    path="news/general-latest",
    version=APIVersion.STABLE,
    description="Get a list of the latest general news articles",
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=GeneralNewsArticle,
)

STOCK_NEWS_ENDPOINT: Endpoint[StockNewsArticle] = Endpoint(
    name="stock_news",
    path="news/stock-latest",
    version=APIVersion.STABLE,
    description="Get a list of the latest stock news articles",
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=StockNewsArticle,
)

STOCK_SYMBOL_NEWS_ENDPOINT: Endpoint[StockNewsArticle] = Endpoint(
    name="stock_news_symbol",
    path="news/stock",
    version=APIVersion.STABLE,
    description="Get a list of the latest news for a specific stock",
    optional_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Symbol of the stock to get news for.",
            alias="symbols",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=StockNewsArticle,
)

STOCK_NEWS_SENTIMENTS_ENDPOINT: Endpoint[StockNewsSentiment] = Endpoint(
    name="stock_news_sentiments",
    path="stock-news-sentiments-rss-feed",
    version=APIVersion.V4,
    description="[DEPRECATED] This endpoint is no longer available on the FMP API",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
        ),
    ],
    optional_params=[],
    response_model=StockNewsSentiment,
)

FOREX_NEWS_ENDPOINT: Endpoint[ForexNewsArticle] = Endpoint(
    name="forex_news",
    path="news/forex-latest",
    version=APIVersion.STABLE,
    description="Get a list of the latest forex news articles",
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=ForexNewsArticle,
)

CRYPTO_NEWS_ENDPOINT: Endpoint[CryptoNewsArticle] = Endpoint(
    name="crypto_news",
    path="news/crypto-latest",
    version=APIVersion.STABLE,
    description="Get a list of the latest crypto news articles",
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=CryptoNewsArticle,
)

FOREX_SYMBOL_NEWS_ENDPOINT: Endpoint[ForexNewsArticle] = Endpoint(
    name="forex_news_symbol",
    path="news/forex",
    version=APIVersion.STABLE,
    description="Search forex news articles by currency pair",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Forex symbol",
            alias="symbols",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    response_model=ForexNewsArticle,
)

CRYPTO_SYMBOL_NEWS_ENDPOINT: Endpoint[CryptoNewsArticle] = Endpoint(
    name="crypto_news_symbol",
    path="news/crypto",
    version=APIVersion.STABLE,
    description="Search crypto news articles by trading pair",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Crypto symbol",
            alias="symbols",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of articles to return",
            default=20,
        ),
    ],
    response_model=CryptoNewsArticle,
)

PRESS_RELEASES_ENDPOINT: Endpoint[PressRelease] = Endpoint(
    name="press_releases",
    path="news/press-releases-latest",
    version=APIVersion.STABLE,
    description="Get a list of the latest press releases",
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of releases to return",
            default=20,
        ),
    ],
    mandatory_params=[],
    response_model=PressRelease,
)

PRESS_RELEASES_BY_SYMBOL_ENDPOINT: Endpoint[PressReleaseBySymbol] = Endpoint(
    name="press_releases_by_symbol",
    path="news/press-releases",
    version=APIVersion.STABLE,
    description="Get a list of the latest press releases for a specific company",
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            default=0,
            description="Page number",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of releases to return",
            default=20,
        ),
    ],
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Company symbol",
            alias="symbols",
        )
    ],
    response_model=PressReleaseBySymbol,
)

HISTORICAL_SOCIAL_SENTIMENT_ENDPOINT: Endpoint[HistoricalSocialSentiment] = Endpoint(
    name="historical_social_sentiment",
    path="historical/social-sentiment",
    version=APIVersion.STABLE,
    description="Get historical social sentiment data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
        ),
    ],
    response_model=HistoricalSocialSentiment,
)

TRENDING_SOCIAL_SENTIMENT_ENDPOINT: Endpoint[TrendingSocialSentiment] = Endpoint(
    name="trending_social_sentiment",
    path="social-sentiments/trending",
    version=APIVersion.STABLE,
    description="Get trending social sentiment data",
    mandatory_params=[
        EndpointParam(
            name="type",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Sentiment type (bullish, bearish)",
        ),
        EndpointParam(
            name="source",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Sentiment source (stocktwits)",
        ),
    ],
    optional_params=[],
    response_model=TrendingSocialSentiment,
)

SOCIAL_SENTIMENT_CHANGES_ENDPOINT: Endpoint[SocialSentimentChanges] = Endpoint(
    name="social_sentiment_changes",
    path="social-sentiments/change",
    version=APIVersion.STABLE,
    description="Get changes in social sentiment data",
    mandatory_params=[
        EndpointParam(
            name="type",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Sentiment type (bullish, bearish)",
        ),
        EndpointParam(
            name="source",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
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
            description="Company symbol",
        )
    ],
    optional_params=[],
    response_model=ESGRating,
)

ESG_BENCHMARK: Endpoint[ESGBenchmark] = Endpoint(
    name="esg_benchmark",
    path="esg-benchmark",
    version=APIVersion.STABLE,
    description="Get ESG benchmark data",
    mandatory_params=[],
    optional_params=[],
    response_model=ESGBenchmark,
)

# Government Trading Endpoints
SENATE_LATEST: Endpoint[SenateTrade] = Endpoint(
    name="senate_latest",
    path="senate-latest",
    version=APIVersion.STABLE,
    description="Get latest Senate financial disclosures",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results",
            default=100,
        ),
    ],
    optional_params=[],
    response_model=SenateTrade,
)

SENATE_TRADING: Endpoint[SenateTrade] = Endpoint(
    name="senate_trading",
    path="senate-trades",
    version=APIVersion.STABLE,
    description="Get Senate trading data by symbol",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=SenateTrade,
)

SENATE_TRADES_BY_NAME: Endpoint[SenateTrade] = Endpoint(
    name="senate_trades_by_name",
    path="senate-trades-by-name",
    version=APIVersion.STABLE,
    description="Get Senate trading data by name",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Senator first or last name",
        )
    ],
    optional_params=[],
    response_model=SenateTrade,
)

SENATE_TRADES_BY_ID: Endpoint[SenateTrade] = Endpoint(
    name="senate_trades_by_id",
    path="senate-trades-by-id",
    version=APIVersion.STABLE,
    description="Get Senate trading data by member id",
    mandatory_params=[
        EndpointParam(
            name="senate_id",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="FMP senate member id (wire key senateID)",
            alias="senateID",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results (max 250)",
            default=100,
        ),
    ],
    response_model=SenateTrade,
)

SENATE_TRADING_RSS: Endpoint[SenateTrade] = Endpoint(
    name="senate_trading_rss",
    path="senate-trading-rss-feed",
    version=APIVersion.STABLE,
    description=(
        "DEPRECATED and non-functional: senate-trading-rss-feed 404s. Do not "
        "select it. The live senate-latest endpoint is already exposed as "
        "intelligence.get_senate_latest and returns the same rows."
    ),
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        )
    ],
    optional_params=[],
    response_model=SenateTrade,
)

HOUSE_LATEST: Endpoint[HouseDisclosure] = Endpoint(
    name="house_latest",
    path="house-latest",
    version=APIVersion.STABLE,
    description="Get latest House financial disclosures",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results",
            default=100,
        ),
    ],
    optional_params=[],
    response_model=HouseDisclosure,
)

HOUSE_DISCLOSURE: Endpoint[HouseDisclosure] = Endpoint(
    name="house_disclosure",
    path="house-trades",
    version=APIVersion.STABLE,
    description="Get House trading data by symbol",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=HouseDisclosure,
)

HOUSE_TRADES_BY_NAME: Endpoint[HouseDisclosure] = Endpoint(
    name="house_trades_by_name",
    path="house-trades-by-name",
    version=APIVersion.STABLE,
    description="Get House trading data by name",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Representative first or last name",
        )
    ],
    optional_params=[],
    response_model=HouseDisclosure,
)

SENATE_PROFILE: Endpoint[SenateProfile] = Endpoint(
    name="senate_profile",
    path="senate-profile",
    version=APIVersion.STABLE,
    description="Get Congress member profiles (path is senate-profile; includes House)",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="senate_id",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="FMP member id (wire key senateID)",
            alias="senateID",
        ),
        EndpointParam(
            name="active",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            description="Filter to currently active members",
        ),
        EndpointParam(
            name="latest_party",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Filter by latest party",
            alias="latestParty",
        ),
        EndpointParam(
            name="latest_position",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Filter by latest position",
            alias="latestPosition",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number (max 20)",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results (max 500)",
            default=500,
        ),
    ],
    response_model=SenateProfile,
)

SENATE_POSITIONS: Endpoint[SenatePosition] = Endpoint(
    name="senate_positions",
    path="senate-positions",
    version=APIVersion.STABLE,
    description="Get Congress member term history",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="senate_id",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="FMP member id (wire key senateID)",
            alias="senateID",
        ),
        EndpointParam(
            name="party",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Filter by party",
        ),
        EndpointParam(
            name="position",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Filter by position",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number (max 50)",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results (max 300)",
            default=300,
        ),
    ],
    response_model=SenatePosition,
)

SENATE_NET_WORTH: Endpoint[SenateNetWorthItem] = Endpoint(
    name="senate_net_worth",
    path="senate-net-worth",
    version=APIVersion.STABLE,
    description="Get itemized Senate/House net-worth disclosures by member id",
    mandatory_params=[
        EndpointParam(
            name="senate_id",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="FMP member id (wire key senateID)",
            alias="senateID",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number (max 100)",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results (max 250)",
            default=250,
        ),
    ],
    response_model=SenateNetWorthItem,
)

SENATE_NET_WORTH_AGGREGATED: Endpoint[SenateNetWorthAggregated] = Endpoint(
    name="senate_net_worth_aggregated",
    path="senate-net-worth-aggregated",
    version=APIVersion.STABLE,
    description="Get yearly aggregated Senate/House net-worth totals by member id",
    mandatory_params=[
        EndpointParam(
            name="senate_id",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="FMP member id (wire key senateID)",
            alias="senateID",
        )
    ],
    optional_params=[
        EndpointParam(
            name="totals_col",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description=(
                "Optional totals column. Docs mark totalsCol required but "
                "give no example; live /stable/senate-net-worth-aggregated "
                "returns 200 without it (probed 2026-08-15)."
            ),
            alias="totalsCol",
        )
    ],
    response_model=SenateNetWorthAggregated,
)

HOUSE_TRADES_BY_ID: Endpoint[HouseDisclosure] = Endpoint(
    name="house_trades_by_id",
    path="house-trades-by-id",
    version=APIVersion.STABLE,
    description="Get House trading data by member id",
    mandatory_params=[
        EndpointParam(
            name="senate_id",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description=(
                "FMP member id. House rows use the wire key senateID "
                "(e.g. Pelosi is P000197)"
            ),
            alias="senateID",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results (max 250)",
            default=100,
        ),
    ],
    response_model=HouseDisclosure,
)

# Fundraising Endpoints
CROWDFUNDING_RSS: Endpoint[CrowdfundingOffering] = Endpoint(
    name="crowdfunding_rss",
    path="crowdfunding-offerings-latest",
    version=APIVersion.STABLE,
    description="Get latest crowdfunding offerings",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results",
            default=100,
        ),
    ],
    optional_params=[],
    response_model=CrowdfundingOffering,
)

CROWDFUNDING_SEARCH: Endpoint[CrowdfundingOfferingSearchItem] = Endpoint(
    name="crowdfunding_search",
    path="crowdfunding-offerings-search",
    version=APIVersion.STABLE,
    description="Search crowdfunding offerings",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Company or offering name",
        )
    ],
    optional_params=[],
    response_model=CrowdfundingOfferingSearchItem,
)

CROWDFUNDING_BY_CIK: Endpoint[CrowdfundingOffering] = Endpoint(
    name="crowdfunding_by_cik",
    path="crowdfunding-offerings",
    version=APIVersion.STABLE,
    description="Get crowdfunding offerings by CIK",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.CIK,
            description="Company CIK number",
        )
    ],
    optional_params=[],
    response_model=CrowdfundingOffering,
)

EQUITY_OFFERING_RSS: Endpoint[EquityOffering] = Endpoint(
    name="equity_offering_rss",
    path="fundraising-latest",
    version=APIVersion.STABLE,
    description="Get latest equity offerings",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results",
            default=10,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.CIK,
            description="Company CIK number",
        ),
    ],
    response_model=EquityOffering,
)

EQUITY_OFFERING_SEARCH: Endpoint[EquityOfferingSearchItem] = Endpoint(
    name="equity_offering_search",
    path="fundraising-search",
    version=APIVersion.STABLE,
    description="Search equity offerings",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Company or offering name",
        )
    ],
    optional_params=[],
    response_model=EquityOfferingSearchItem,
)

EQUITY_OFFERING_BY_CIK: Endpoint[EquityOffering] = Endpoint(
    name="equity_offering_by_cik",
    path="fundraising",
    version=APIVersion.STABLE,
    description="Get equity offerings by CIK",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.CIK,
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
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=RatingsSnapshot,
)

RATINGS_HISTORICAL: Endpoint[HistoricalRating] = Endpoint(
    name="ratings_historical",
    path="ratings-historical",
    version=APIVersion.STABLE,
    description="Get historical analyst ratings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results",
            default=100,
        )
    ],
    response_model=HistoricalRating,
)

PRICE_TARGET_NEWS: Endpoint[PriceTargetNews] = Endpoint(
    name="price_target_news",
    path="price-target-news",
    version=APIVersion.STABLE,
    description="Get price target news",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        )
    ],
    response_model=PriceTargetNews,
)

PRICE_TARGET_LATEST_NEWS: Endpoint[PriceTargetNews] = Endpoint(
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
            description="Page number",
            default=0,
        )
    ],
    response_model=PriceTargetNews,
)

GRADES: Endpoint[StockGrade] = Endpoint(
    name="grades",
    path="grades",
    version=APIVersion.STABLE,
    description="Get stock grades from analysts",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        )
    ],
    response_model=StockGrade,
)

GRADES_HISTORICAL: Endpoint[HistoricalStockGrade] = Endpoint(
    name="grades_historical",
    path="grades-historical",
    version=APIVersion.STABLE,
    description="Get historical stock grades",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
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
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=StockGradesConsensus,
)

GRADES_NEWS: Endpoint[StockGradeNews] = Endpoint(
    name="grades_news",
    path="grades-news",
    version=APIVersion.STABLE,
    description="Get stock grade news",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        )
    ],
    response_model=StockGradeNews,
)

GRADES_LATEST_NEWS: Endpoint[StockGradeNews] = Endpoint(
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
            description="Page number",
            default=0,
        )
    ],
    response_model=StockGradeNews,
)
