# fmp_data/intelligence/mapping.py

from fmp_data.intelligence.endpoints import (
    CROWDFUNDING_BY_CIK,
    CROWDFUNDING_RSS,
    CROWDFUNDING_SEARCH,
    CRYPTO_NEWS_ENDPOINT,
    DIVIDENDS_CALENDAR,
    EARNINGS_CALENDAR,
    EARNINGS_CONFIRMED,
    EARNINGS_SURPRISES,
    EQUITY_OFFERING_BY_CIK,
    EQUITY_OFFERING_RSS,
    EQUITY_OFFERING_SEARCH,
    ESG_BENCHMARK,
    ESG_DATA,
    ESG_RATINGS,
    FMP_ARTICLES_ENDPOINT,
    FOREX_NEWS_ENDPOINT,
    GENERAL_NEWS_ENDPOINT,
    HISTORICAL_EARNINGS,
    HISTORICAL_SOCIAL_SENTIMENT_ENDPOINT,
    HOUSE_DISCLOSURE,
    HOUSE_DISCLOSURE_RSS,
    IPO_CALENDAR,
    PRESS_RELEASES_BY_SYMBOL_ENDPOINT,
    PRESS_RELEASES_ENDPOINT,
    SENATE_TRADING,
    SENATE_TRADING_RSS,
    SOCIAL_SENTIMENT_CHANGES_ENDPOINT,
    STOCK_NEWS_ENDPOINT,
    STOCK_NEWS_SENTIMENTS_ENDPOINT,
    STOCK_SPLITS_CALENDAR,
    TRENDING_SOCIAL_SENTIMENT_ENDPOINT,
)
from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)

# Endpoint to method mapping
INTELLIGENCE_ENDPOINT_MAP = {
    # Calendar endpoints
    "get_earnings_calendar": EARNINGS_CALENDAR,
    "get_earnings_confirmed": EARNINGS_CONFIRMED,
    "get_earnings_surprises": EARNINGS_SURPRISES,
    "get_historical_earnings": HISTORICAL_EARNINGS,
    "get_dividends_calendar": DIVIDENDS_CALENDAR,
    "get_stock_splits_calendar": STOCK_SPLITS_CALENDAR,
    "get_ipo_calendar": IPO_CALENDAR,
    # ESG endpoints
    "get_esg_data": ESG_DATA,
    "get_esg_ratings": ESG_RATINGS,
    "get_esg_benchmark": ESG_BENCHMARK,
    # Government Trading endpoints
    "get_senate_trading": SENATE_TRADING,
    "get_senate_trading_rss": SENATE_TRADING_RSS,
    "get_house_disclosure": HOUSE_DISCLOSURE,
    "get_house_disclosure_rss": HOUSE_DISCLOSURE_RSS,
    # Fundraising endpoints
    "get_crowdfunding_rss": CROWDFUNDING_RSS,
    "get_crowdfunding_search": CROWDFUNDING_SEARCH,
    "get_crowdfunding_by_cik": CROWDFUNDING_BY_CIK,
    "get_equity_offering_rss": EQUITY_OFFERING_RSS,
    "get_equity_offering_search": EQUITY_OFFERING_SEARCH,
    "get_equity_offering_by_cik": EQUITY_OFFERING_BY_CIK,
    # News endpoints
    "get_fmp_articles": FMP_ARTICLES_ENDPOINT,
    "get_general_news": GENERAL_NEWS_ENDPOINT,
    "get_stock_news": STOCK_NEWS_ENDPOINT,
    "get_stock_news_sentiments": STOCK_NEWS_SENTIMENTS_ENDPOINT,
    "get_forex_news": FOREX_NEWS_ENDPOINT,
    "get_crypto_news": CRYPTO_NEWS_ENDPOINT,
    "get_press_releases": PRESS_RELEASES_ENDPOINT,
    "get_press_releases_by_symbol": PRESS_RELEASES_BY_SYMBOL_ENDPOINT,
    # Social Sentiment endpoints
    "get_historical_social_sentiment": HISTORICAL_SOCIAL_SENTIMENT_ENDPOINT,
    "get_trending_social_sentiment": TRENDING_SOCIAL_SENTIMENT_ENDPOINT,
    "get_social_sentiment_changes": SOCIAL_SENTIMENT_CHANGES_ENDPOINT,
}

# Common parameter hints
SYMBOL_HINT = ParameterHint(
    natural_names=["stock", "ticker", "company", "symbol"],
    extraction_patterns=[
        r"(?i)for\s+([A-Z]{1,5})",
        r"(?i)([A-Z]{1,5})(?:'s|'|\s+)",
        r"(?i)symbol[:\s]+([A-Z]{1,5})",
    ],
    examples=["AAPL", "MSFT", "GOOGL"],
    context_clues=["company", "stock", "ticker", "symbol"],
)

DATE_HINTS = {
    "start_date": ParameterHint(
        natural_names=["start date", "from date", "beginning", "since", "from"],
        extraction_patterns=[
            r"(\d{4}-\d{2}-\d{2})",
            r"(?:from|since|after)\s+(\d{4}-\d{2}-\d{2})",
        ],
        examples=["2023-01-01", "2022-12-31"],
        context_clues=["from", "since", "starting", "after"],
    ),
    "end_date": ParameterHint(
        natural_names=["end date", "to date", "until", "through", "to"],
        extraction_patterns=[
            r"(?:to|until|through)\s+(\d{4}-\d{2}-\d{2})",
            r"(\d{4}-\d{2}-\d{2})",
        ],
        examples=["2024-01-01", "2023-12-31"],
        context_clues=["to", "until", "through", "ending"],
    ),
}

PAGE_HINT = ParameterHint(
    natural_names=["page", "page number", "result page"],
    extraction_patterns=[
        r"page\s*(\d+)",
        r"(\d+)(?:st|nd|rd|th)\s+page",
    ],
    examples=["0", "1", "2"],
    context_clues=["page", "next", "previous", "results"],
)

LIMIT_HINT = ParameterHint(
    natural_names=["limit", "count", "number of results"],
    extraction_patterns=[
        r"limit\s*(\d+)",
        r"(\d+)\s*results",
    ],
    examples=["50", "100", "200"],
    context_clues=["limit", "maximum", "results", "entries"],
)
# Additional utility mappings
SENTIMENT_SOURCES = {
    "stocktwits": {
        "terms": ["stocktwits", "st", "stock tweets"],
        "patterns": [r"(?i)stocktwits?", r"(?i)st"],
    },
    "twitter": {
        "terms": ["twitter", "tweets", "x platform"],
        "patterns": [r"(?i)twitter", r"(?i)tweet"],
    },
}

NEWS_CATEGORIES = {
    "market": ["market news", "trading updates", "financial news"],
    "company": ["corporate news", "business updates", "company announcements"],
    "economic": ["economic news", "macro updates", "economy news"],
    "industry": ["sector news", "industry updates", "segment news"],
}

# Additional response field mappings for specialized endpoints
SPECIALIZED_RESPONSE_FIELDS = {
    "sentiment": {
        "score_ranges": {
            "very_positive": (0.8, 1.0),
            "positive": (0.3, 0.8),
            "neutral": (-0.3, 0.3),
            "negative": (-0.8, -0.3),
            "very_negative": (-1.0, -0.8),
        },
    },
    "fundraising": {
        "offering_types": ["equity", "debt", "convertible", "hybrid"],
        "security_types": ["common", "preferred", "notes", "warrants"],
    },
}
# Semantic definitions
INTELLIGENCE_ENDPOINTS_SEMANTICS = {
    "earnings_calendar": EndpointSemantics(
        client_name="intelligence",
        method_name="get_earnings_calendar",
        natural_description=(
            "Access comprehensive earnings "
            "calendar showing upcoming earnings releases, "
            "estimated and actual results, "
            "and historical earnings data"
        ),
        example_queries=[
            "Show earnings calendar",
            "When is AAPL's next earnings?",
            "Get upcoming earnings dates",
            "Show earnings releases for next week",
        ],
        related_terms=[
            "earnings release",
            "earnings report",
            "quarterly results",
            "financial results",
            "earnings announcement",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Corporate Events",
        parameter_hints={
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Earnings announcement date",
                examples=["2024-01-25", "2024-02-01"],
                related_terms=["announcement date", "release date"],
            ),
            "eps": ResponseFieldInfo(
                description="Earnings per share",
                examples=["1.25", "2.50"],
                related_terms=["earnings", "EPS", "profit"],
            ),
        },
        use_cases=[
            "Earnings tracking",
            "Event planning",
            "Trading strategy",
            "Market research",
        ],
    ),
    "esg_data": EndpointSemantics(
        client_name="intelligence",
        method_name="get_esg_data",
        natural_description=(
            "Retrieve detailed ESG (Environmental, Social, Governance) metrics and "
            "scores for companies including component breakdowns and benchmarks"
        ),
        example_queries=[
            "Get ESG data for AAPL",
            "Show environmental scores for MSFT",
            "What's the ESG rating for TSLA?",
            "Get sustainability metrics",
        ],
        related_terms=[
            "sustainability",
            "environmental",
            "social responsibility",
            "governance",
            "ESG score",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="ESG",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "environmental_score": ResponseFieldInfo(
                description="Environmental component score",
                examples=["85.5", "72.3"],
                related_terms=["environmental rating", "eco score"],
            ),
            "social_score": ResponseFieldInfo(
                description="Social component score",
                examples=["78.9", "66.4"],
                related_terms=["social rating", "community score"],
            ),
        },
        use_cases=[
            "ESG investing",
            "Sustainability analysis",
            "Risk assessment",
            "Corporate responsibility",
        ],
    ),
    "equity_offering_rss": EndpointSemantics(
        client_name="intelligence",
        method_name="get_equity_offering_rss",
        natural_description=(
            "Get real-time RSS feed of "
            "equity offerings including new issues, follow-on "
            "offerings, and capital raising events"
        ),
        example_queries=[
            "Show latest equity offerings",
            "Get new stock offerings",
            "Recent capital raises",
            "New equity issuances",
        ],
        related_terms=[
            "stock offering",
            "equity issuance",
            "capital raise",
            "share offering",
            "new issues",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Fundraising",
        parameter_hints={"page": PAGE_HINT},
        response_hints={
            "offering_type": ResponseFieldInfo(
                description="Type of equity offering",
                examples=["IPO", "Follow-on", "Secondary"],
                related_terms=["offering type", "issuance type"],
            ),
            "amount": ResponseFieldInfo(
                description="Offering amount",
                examples=["100000000", "50000000"],
                related_terms=["size", "value", "raise amount"],
            ),
        },
        use_cases=[
            "New issue monitoring",
            "Capital markets tracking",
            "Offering analysis",
            "Market activity",
        ],
    ),
    "equity_offering_by_cik": EndpointSemantics(
        client_name="intelligence",
        method_name="get_equity_offering_by_cik",
        natural_description=(
            "Retrieve equity offerings for a specific company using CIK number "
            "including historical and current offerings"
        ),
        example_queries=[
            "Get equity offerings by CIK",
            "Show company stock offerings",
            "Find offerings by CIK",
            "Historical equity raises",
        ],
        related_terms=[
            "stock issuance",
            "company offerings",
            "equity raises",
            "share sales",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Fundraising",
        parameter_hints={
            "cik": ParameterHint(
                natural_names=["CIK", "company identifier", "SEC number"],
                extraction_patterns=[r"\d{10}"],
                examples=["0000320193", "0001018724"],
                context_clues=["CIK", "identifier", "SEC ID"],
            ),
        },
        response_hints={
            "form_type": ResponseFieldInfo(
                description="SEC form type",
                examples=["S-1", "424B4"],
                related_terms=["filing type", "registration"],
            ),
            "offering_amount": ResponseFieldInfo(
                description="Size of offering",
                examples=["100000000", "50000000"],
                related_terms=["amount", "size", "value"],
            ),
        },
        use_cases=[
            "Company research",
            "Capital raising history",
            "Offering analysis",
            "Due diligence",
        ],
    ),
    "fmp_articles": EndpointSemantics(
        client_name="intelligence",
        method_name="get_fmp_articles",
        natural_description=(
            "Access Financial Modeling Prep articles including market analysis, "
            "company research, and financial insights"
        ),
        example_queries=[
            "Get FMP articles",
            "Show latest analysis",
            "Recent research articles",
            "Market insights",
        ],
        related_terms=[
            "research articles",
            "market analysis",
            "financial research",
            "investment insights",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="News & Research",
        parameter_hints={
            "page": PAGE_HINT,
            "size": LIMIT_HINT,
        },
        response_hints={
            "title": ResponseFieldInfo(
                description="Article title",
                examples=["Market Analysis: Q1 2024", "Stock Deep Dive"],
                related_terms=["headline", "article name"],
            ),
            "content": ResponseFieldInfo(
                description="Article content",
                examples=["Full analysis...", "Detailed research..."],
                related_terms=["text", "body", "analysis"],
            ),
        },
        use_cases=[
            "Market research",
            "Investment analysis",
            "Company insights",
            "Industry trends",
        ],
    ),
    "general_news": EndpointSemantics(
        client_name="intelligence",
        method_name="get_general_news",
        natural_description=(
            "Retrieve general financial news and "
            "market updates from various sources "
            "covering markets, economy, and business"
        ),
        example_queries=[
            "Show general market news",
            "Get latest financial news",
            "Recent market updates",
            "Business headlines",
        ],
        related_terms=[
            "market news",
            "financial updates",
            "business news",
            "market coverage",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="News & Media",
        parameter_hints={"page": PAGE_HINT},
        response_hints={
            "site": ResponseFieldInfo(
                description="News source",
                examples=["Reuters", "Bloomberg"],
                related_terms=["source", "publisher"],
            ),
            "text": ResponseFieldInfo(
                description="Article text",
                examples=["Market news...", "Business updates..."],
                related_terms=["content", "story", "article"],
            ),
        },
        use_cases=[
            "Market monitoring",
            "News tracking",
            "Business updates",
            "Research",
        ],
    ),
    "stock_news": EndpointSemantics(
        client_name="intelligence",
        method_name="get_stock_news",
        natural_description=(
            "Access stock-specific news and updates including company events, "
            "market moves, and corporate developments"
        ),
        example_queries=[
            "Get stock news for AAPL",
            "Show company updates",
            "Latest stock headlines",
            "Company news feed",
        ],
        related_terms=[
            "company news",
            "stock updates",
            "corporate news",
            "market news",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="News & Media",
        parameter_hints={
            "tickers": ParameterHint(
                natural_names=["symbols", "stocks", "tickers"],
                extraction_patterns=[r"[A-Z,\s]+"],
                examples=["AAPL", "AAPL,MSFT,GOOGL"],
                context_clues=["stocks", "symbols", "companies"],
            ),
            "page": PAGE_HINT,
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
            "limit": LIMIT_HINT,
        },
        response_hints={
            "title": ResponseFieldInfo(
                description="News headline",
                examples=["Earnings Beat Estimates", "New Product Launch"],
                related_terms=["headline", "title"],
            ),
            "text": ResponseFieldInfo(
                description="News content",
                examples=["Company announced...", "Market reaction..."],
                related_terms=["content", "story", "article"],
            ),
        },
        use_cases=[
            "Stock monitoring",
            "Company research",
            "Market analysis",
            "Event tracking",
        ],
    ),
    "stock_news_sentiments": EndpointSemantics(
        client_name="intelligence",
        method_name="get_stock_news_sentiments",
        natural_description=(
            "Get stock news with sentiment analysis "
            "including positive/negative sentiment "
            "scores and market impact assessment"
        ),
        example_queries=[
            "Show news sentiment analysis",
            "Get stock news with sentiment",
            "News sentiment scores",
            "Market sentiment data",
        ],
        related_terms=[
            "sentiment analysis",
            "news sentiment",
            "market mood",
            "news impact",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="News & Media",
        parameter_hints={"page": PAGE_HINT},
        response_hints={
            "sentiment": ResponseFieldInfo(
                description="News sentiment score",
                examples=["0.85", "-0.32"],
                related_terms=["sentiment score", "mood"],
            ),
            "sentimentScore": ResponseFieldInfo(
                description="Numerical sentiment value",
                examples=["0.75", "-0.45"],
                related_terms=["score", "sentiment value"],
            ),
        },
        use_cases=[
            "Sentiment analysis",
            "Market psychology",
            "Trading signals",
            "Risk assessment",
        ],
    ),
    "press_releases_by_symbol": EndpointSemantics(
        client_name="intelligence",
        method_name="get_press_releases_by_symbol",
        natural_description=(
            "Retrieve company-specific press releases and official announcements "
            "including corporate events and updates"
        ),
        example_queries=[
            "Get press releases for AAPL",
            "Show company announcements",
            "Find official releases",
            "Corporate updates feed",
        ],
        related_terms=[
            "company releases",
            "announcements",
            "corporate news",
            "official updates",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="News & Media",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "page": PAGE_HINT,
        },
        response_hints={
            "title": ResponseFieldInfo(
                description="Press release title",
                examples=["Q4 Results", "Product Launch"],
                related_terms=["headline", "announcement"],
            ),
            "text": ResponseFieldInfo(
                description="Release content",
                examples=["Company announces...", "Today we released..."],
                related_terms=["content", "announcement", "text"],
            ),
        },
        use_cases=[
            "Corporate monitoring",
            "Event tracking",
            "News analysis",
            "Research",
        ],
    ),
    "earnings_confirmed": EndpointSemantics(
        client_name="intelligence",
        method_name="get_earnings_confirmed",
        natural_description=(
            "Access confirmed earnings dates and times for companies including "
            "timing details and publication information"
        ),
        example_queries=[
            "Show confirmed earnings dates",
            "When are the next confirmed earnings?",
            "Get scheduled earnings releases",
            "Confirmed earnings calendar",
        ],
        related_terms=[
            "earnings schedule",
            "release date",
            "earnings timing",
            "announcement date",
            "confirmed release",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Corporate Events",
        parameter_hints={
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "event_date": ResponseFieldInfo(
                description="Confirmed earnings date",
                examples=["2024-01-25", "2024-02-01"],
                related_terms=["announcement date", "release date"],
            ),
            "time": ResponseFieldInfo(
                description="Time of earnings release",
                examples=["16:30", "09:00"],
                related_terms=["release time", "announcement time"],
            ),
        },
        use_cases=[
            "Event planning",
            "Trading preparation",
            "Calendar management",
            "Research scheduling",
        ],
    ),
    "historical_social_sentiment": EndpointSemantics(
        client_name="intelligence",
        method_name="get_historical_social_sentiment",
        natural_description=(
            "Retrieve historical social media "
            "sentiment data including sentiment scores, "
            "engagement metrics, and trend analysis"
        ),
        example_queries=[
            "Get social sentiment history for AAPL",
            "Show historical sentiment trends",
            "Social media sentiment analysis",
            "Past sentiment data",
        ],
        related_terms=[
            "social media sentiment",
            "market sentiment",
            "social analysis",
            "sentiment history",
            "sentiment trends",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Sentiment Analysis",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "page": PAGE_HINT,
        },
        response_hints={
            "sentiment": ResponseFieldInfo(
                description="Sentiment score",
                examples=["0.85", "-0.32"],
                related_terms=["sentiment score", "sentiment rating"],
            ),
            "posts": ResponseFieldInfo(
                description="Number of social media posts",
                examples=["1250", "750"],
                related_terms=["post count", "mentions", "activity"],
            ),
        },
        use_cases=[
            "Sentiment analysis",
            "Social monitoring",
            "Trend analysis",
            "Market psychology",
        ],
    ),
    "trending_social_sentiment": EndpointSemantics(
        client_name="intelligence",
        method_name="get_trending_social_sentiment",
        natural_description=(
            "Get current trending social "
            "media sentiment data including "
            "most discussed "
            "stocks and sentiment rankings"
        ),
        example_queries=[
            "Show trending sentiment",
            "What stocks are trending on social media?",
            "Get popular stock sentiment",
            "Social media trends",
        ],
        related_terms=[
            "trending stocks",
            "popular sentiment",
            "social trends",
            "market buzz",
            "social momentum",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Sentiment Analysis",
        parameter_hints={
            "type": ParameterHint(
                natural_names=["sentiment type", "trend type"],
                extraction_patterns=[
                    r"(?i)(bullish|bearish)",
                ],
                examples=["bullish", "bearish"],
                context_clues=["positive", "negative", "optimistic", "pessimistic"],
            ),
            "source": ParameterHint(
                natural_names=["data source", "platform"],
                extraction_patterns=[
                    r"(?i)(stocktwits|twitter)",
                ],
                examples=["stocktwits", "twitter"],
                context_clues=["social media", "platform", "source"],
            ),
        },
        response_hints={
            "rank": ResponseFieldInfo(
                description="Trending rank",
                examples=["1", "5", "10"],
                related_terms=["position", "ranking", "trend rank"],
            ),
            "sentiment": ResponseFieldInfo(
                description="Current sentiment score",
                examples=["0.75", "-0.45"],
                related_terms=["sentiment value", "sentiment level"],
            ),
        },
        use_cases=[
            "Trend spotting",
            "Momentum analysis",
            "Social monitoring",
            "Market sentiment",
        ],
    ),
    "house_disclosure": EndpointSemantics(
        client_name="intelligence",
        method_name="get_house_disclosure",
        natural_description=(
            "Access House of Representatives "
            "trading disclosures including transaction "
            "details, filing information, "
            "and trade specifics"
        ),
        example_queries=[
            "Show House trading for AAPL",
            "Get Congress stock trades",
            "House member disclosures",
            "Congressional trading activity",
        ],
        related_terms=[
            "congress trading",
            "house trades",
            "political trading",
            "congressional disclosure",
            "representative trading",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Government Trading",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "representative": ResponseFieldInfo(
                description="Name of representative",
                examples=["John Smith", "Jane Doe"],
                related_terms=["congress member", "representative name"],
            ),
            "transaction_date": ResponseFieldInfo(
                description="Date of trade",
                examples=["2024-01-15", "2023-12-20"],
                related_terms=["trade date", "transaction time"],
            ),
        },
        use_cases=[
            "Political trading analysis",
            "Insider activity monitoring",
            "Regulatory compliance",
            "Government oversight",
        ],
    ),
    "press_releases": EndpointSemantics(
        client_name="intelligence",
        method_name="get_press_releases",
        natural_description=(
            "Retrieve corporate press releases and official company announcements "
            "with detailed content and publication information"
        ),
        example_queries=[
            "Show recent press releases",
            "Get company announcements",
            "Latest press releases",
            "Corporate news releases",
        ],
        related_terms=[
            "company announcement",
            "press release",
            "corporate news",
            "official statement",
            "company release",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="News & Media",
        parameter_hints={"page": PAGE_HINT},
        response_hints={
            "title": ResponseFieldInfo(
                description="Press release title",
                examples=[
                    "Company Announces Q4 Results",
                    "New Product Launch",
                ],
                related_terms=["headline", "announcement title"],
            ),
            "text": ResponseFieldInfo(
                description="Press release content",
                examples=["Full text of announcement...", "Detailed release..."],
                related_terms=["content", "announcement text"],
            ),
        },
        use_cases=[
            "News monitoring",
            "Corporate updates",
            "Market research",
            "Event tracking",
        ],
    ),
    "forex_news": EndpointSemantics(
        client_name="intelligence",
        method_name="get_forex_news",
        natural_description=(
            "Retrieve forex market news "
            "including currency pair updates, "
            "exchange rate "
            "movements, and international "
            "market developments"
        ),
        example_queries=[
            "Get forex news for EURUSD",
            "Show currency market updates",
            "Latest FX news",
            "Foreign exchange headlines",
        ],
        related_terms=[
            "currency news",
            "forex market",
            "exchange rates",
            "currency trading",
            "fx updates",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="News & Media",
        parameter_hints={
            "symbol": ParameterHint(
                natural_names=["currency pair", "forex pair", "exchange rate"],
                extraction_patterns=[r"^[A-Z]{6}$"],
                examples=["EURUSD", "GBPUSD", "USDJPY"],
                context_clues=["forex", "currency", "exchange"],
            ),
            "page": PAGE_HINT,
            "limit": LIMIT_HINT,
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "title": ResponseFieldInfo(
                description="News article headline",
                examples=["EUR/USD Breaks Resistance", "GBP Falls After Data"],
                related_terms=["headline", "story", "forex news"],
            ),
            "text": ResponseFieldInfo(
                description="Article content",
                examples=["Currency analysis...", "Market movement details..."],
                related_terms=["content", "article text", "details"],
            ),
        },
        use_cases=[
            "Currency market monitoring",
            "Exchange rate tracking",
            "Forex trading research",
            "International markets",
        ],
    ),
    "crowdfunding_rss": EndpointSemantics(
        client_name="intelligence",
        method_name="get_crowdfunding_rss",
        natural_description=(
            "Access latest crowdfunding "
            "offerings and campaigns "
            "including funding details, "
            "company information, and offering terms"
        ),
        example_queries=[
            "Show crowdfunding offerings",
            "Get latest fundraising campaigns",
            "New crowdfunding opportunities",
            "Recent funding rounds",
        ],
        related_terms=[
            "crowdfunding",
            "fundraising",
            "startup funding",
            "investment offerings",
            "capital raise",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Fundraising",
        parameter_hints={"page": PAGE_HINT},
        response_hints={
            "company_name": ResponseFieldInfo(
                description="Name of company raising funds",
                examples=["Tech Startup Inc", "Green Energy Co"],
                related_terms=["company", "issuer", "business"],
            ),
            "offering_amount": ResponseFieldInfo(
                description="Amount being raised",
                examples=["1000000", "500000"],
                related_terms=["raise amount", "funding goal", "target"],
            ),
        },
        use_cases=[
            "Investment opportunities",
            "Startup monitoring",
            "Market research",
            "Due diligence",
        ],
    ),
    "equity_offering_search": EndpointSemantics(
        client_name="intelligence",
        method_name="get_equity_offering_search",
        natural_description=(
            "Search for equity offerings including public and private placements, "
            "with detailed offering terms and company information"
        ),
        example_queries=[
            "Search equity offerings",
            "Find stock offerings",
            "Look up company offerings",
            "Search share issuance",
        ],
        related_terms=[
            "stock offering",
            "equity issuance",
            "share offering",
            "capital raise",
            "public offering",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Fundraising",
        parameter_hints={
            "name": ParameterHint(
                natural_names=["company name", "business name", "issuer"],
                extraction_patterns=[r"[\w\s]+"],
                examples=["Tech Corp", "Energy Solutions"],
                context_clues=["company", "business", "corporation"],
            ),
        },
        response_hints={
            "offering_type": ResponseFieldInfo(
                description="Type of equity offering",
                examples=["IPO", "Secondary", "PIPE"],
                related_terms=["offering", "issuance type", "deal type"],
            ),
            "amount": ResponseFieldInfo(
                description="Offering amount",
                examples=["100000000", "50000000"],
                related_terms=["size", "deal value", "raise amount"],
            ),
        },
        use_cases=[
            "Deal sourcing",
            "Investment research",
            "Market monitoring",
            "Competitive analysis",
        ],
    ),
    "social_sentiment_changes": EndpointSemantics(
        client_name="intelligence",
        method_name="get_social_sentiment_changes",
        natural_description=(
            "Track changes in social media sentiment including sentiment shifts, "
            "momentum changes, and trend developments"
        ),
        example_queries=[
            "Show sentiment changes",
            "Get social sentiment shifts",
            "Track sentiment movement",
            "Monitor sentiment trends",
        ],
        related_terms=[
            "sentiment change",
            "sentiment shift",
            "trend change",
            "momentum shift",
            "sentiment movement",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Sentiment Analysis",
        parameter_hints={
            "type": ParameterHint(
                natural_names=["sentiment type", "trend type"],
                extraction_patterns=[r"(bullish|bearish)"],
                examples=["bullish", "bearish"],
                context_clues=["positive", "negative", "direction"],
            ),
            "source": ParameterHint(
                natural_names=["data source", "platform"],
                extraction_patterns=[r"(stocktwits|twitter)"],
                examples=["stocktwits", "twitter"],
                context_clues=["social media", "platform"],
            ),
        },
        response_hints={
            "sentiment_change": ResponseFieldInfo(
                description="Change in sentiment score",
                examples=["+0.25", "-0.15"],
                related_terms=["change", "shift", "movement"],
            ),
            "rank": ResponseFieldInfo(
                description="Current sentiment rank",
                examples=["1", "5", "10"],
                related_terms=["position", "ranking", "standing"],
            ),
        },
        use_cases=[
            "Sentiment tracking",
            "Momentum analysis",
            "Trend spotting",
            "Market psychology",
        ],
    ),
    "crypto_news": EndpointSemantics(
        client_name="intelligence",
        method_name="get_crypto_news",
        natural_description=(
            "Access cryptocurrency news articles including market updates, "
            "trading information, and digital asset developments"
        ),
        example_queries=[
            "Get crypto news for BTC",
            "Show Bitcoin headlines",
            "Latest cryptocurrency news",
            "Crypto market updates",
        ],
        related_terms=[
            "crypto news",
            "digital assets",
            "cryptocurrency",
            "blockchain news",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="News & Media",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "page": PAGE_HINT,
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
            "limit": LIMIT_HINT,  # Added missing limit parameter
        },
        response_hints={
            "title": ResponseFieldInfo(
                description="News article headline",
                examples=["Bitcoin Reaches New High", "ETH 2.0 Launch"],
                related_terms=["headline", "title", "news"],
            ),
        },
        use_cases=[
            "Crypto market monitoring",
            "Trading research",
            "Market analysis",
            "News tracking",
        ],
    ),
    "earnings_surprises": EndpointSemantics(
        client_name="intelligence",
        method_name="get_earnings_surprises",
        natural_description=(
            "Retrieve historical earnings "
            "surprises including actual vs "
            "estimated earnings, "
            "surprise percentages, and earnings dates"
        ),
        example_queries=[
            "Get earnings surprises for AAPL",
            "Show earnings beats and misses for MSFT",
            "Historical earnings surprises for GOOGL",
            "Earnings performance vs estimates",
        ],
        related_terms=[
            "earnings beat",
            "earnings miss",
            "surprise factor",
            "earnings estimates",
            "actual results",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Calendar Events",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "actual_earning_result": ResponseFieldInfo(
                description="Actual reported earnings",
                examples=["2.58", "1.45"],
                related_terms=["actual earnings", "reported EPS"],
            ),
            "estimated_earning": ResponseFieldInfo(
                description="Estimated earnings",
                examples=["2.25", "1.38"],
                related_terms=["expected earnings", "estimated EPS"],
            ),
        },
        use_cases=[
            "Earnings analysis",
            "Performance tracking",
            "Estimate accuracy",
            "Historical comparison",
        ],
    ),
    "historical_earnings": EndpointSemantics(
        client_name="intelligence",
        method_name="get_historical_earnings",
        natural_description=(
            "Access historical earnings "
            "reports including revenue, "
            "EPS, and dates for "
            "past quarters and fiscal years"
        ),
        example_queries=[
            "Show historical earnings for AAPL",
            "Get past earnings reports for MSFT",
            "Previous earnings history for GOOGL",
            "Company earnings track record",
        ],
        related_terms=[
            "past earnings",
            "earnings history",
            "historical results",
            "previous reports",
            "past performance",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Calendar Events",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "date": ResponseFieldInfo(
                description="Earnings report date",
                examples=["2023-07-25", "2023-10-24"],
                related_terms=["report date", "earnings date"],
            ),
            "eps": ResponseFieldInfo(
                description="Reported earnings per share",
                examples=["2.58", "1.45"],
                related_terms=["earnings", "EPS", "result"],
            ),
        },
        use_cases=[
            "Performance tracking",
            "Historical analysis",
            "Trend identification",
            "Seasonal patterns",
        ],
    ),
    "dividends_calendar": EndpointSemantics(
        client_name="intelligence",
        method_name="get_dividends_calendar",
        natural_description=(
            "Get upcoming and historical "
            "dividend events including "
            "ex-dividend dates, "
            "payment dates, and dividend amounts"
        ),
        example_queries=[
            "Show dividend calendar",
            "Get upcoming dividends",
            "Next dividend dates",
            "Dividend payment schedule",
        ],
        related_terms=[
            "dividend dates",
            "ex-dividend",
            "payment dates",
            "dividend schedule",
            "dividend events",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Calendar Events",
        parameter_hints={
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Ex-dividend date",
                examples=["2024-01-15", "2024-02-01"],
                related_terms=["ex-date", "record date"],
            ),
            "dividend": ResponseFieldInfo(
                description="Dividend amount",
                examples=["0.85", "1.25"],
                related_terms=["payment", "distribution", "amount"],
            ),
        },
        use_cases=[
            "Dividend tracking",
            "Income planning",
            "Portfolio management",
            "Payment scheduling",
        ],
    ),
    "stock_splits_calendar": EndpointSemantics(
        client_name="intelligence",
        method_name="get_stock_splits_calendar",
        natural_description=(
            "Access upcoming and historical "
            "stock split events including "
            "split ratios, "
            "dates, and affected securities"
        ),
        example_queries=[
            "Show stock split calendar",
            "Get upcoming splits",
            "Stock split schedule",
            "Next split dates",
        ],
        related_terms=[
            "stock splits",
            "share splits",
            "split ratio",
            "split events",
            "corporate actions",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Calendar Events",
        parameter_hints={
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Split date",
                examples=["2024-01-15", "2024-02-01"],
                related_terms=["effective date", "split date"],
            ),
            "numerator": ResponseFieldInfo(
                description="Split ratio numerator",
                examples=["4", "3"],
                related_terms=["ratio", "multiplier"],
            ),
        },
        use_cases=[
            "Corporate action tracking",
            "Portfolio adjustment",
            "Event monitoring",
            "Position management",
        ],
    ),
    "ipo_calendar": EndpointSemantics(
        client_name="intelligence",
        method_name="get_ipo_calendar",
        natural_description=(
            "Retrieve upcoming and recent IPO events including pricing details, "
            "offering sizes, and listing dates"
        ),
        example_queries=[
            "Show IPO calendar",
            "Get upcoming IPOs",
            "New listings schedule",
            "Public offering dates",
        ],
        related_terms=[
            "initial public offering",
            "new listings",
            "IPO events",
            "public offerings",
            "market debuts",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Calendar Events",
        parameter_hints={
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "company": ResponseFieldInfo(
                description="Company name",
                examples=["Tech Corp", "New Co Inc"],
                related_terms=["issuer", "company name"],
            ),
            "shares": ResponseFieldInfo(
                description="Number of shares offered",
                examples=["10000000", "5000000"],
                related_terms=["offering size", "share count"],
            ),
        },
        use_cases=[
            "IPO tracking",
            "New listing research",
            "Market monitoring",
            "Investment opportunities",
        ],
    ),
    "esg_ratings": EndpointSemantics(
        client_name="intelligence",
        method_name="get_esg_ratings",
        natural_description=(
            "Access company ESG ratings "
            "and scores including environmental, social, "
            "and governance performance metrics "
            "and industry rankings"
        ),
        example_queries=[
            "Get ESG ratings for AAPL",
            "Show company sustainability scores",
            "ESG performance metrics",
            "Company ESG rankings",
        ],
        related_terms=[
            "ESG scores",
            "sustainability ratings",
            "environmental rating",
            "social score",
            "governance rating",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="ESG",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "esg_risk_rating": ResponseFieldInfo(
                description="Overall ESG risk rating",
                examples=["Low Risk", "Medium Risk"],
                related_terms=["risk level", "ESG grade"],
            ),
            "industry_rank": ResponseFieldInfo(
                description="Company's ESG rank within industry",
                examples=["1 of 50", "5 of 100"],
                related_terms=["sector rank", "peer comparison"],
            ),
        },
        use_cases=[
            "ESG analysis",
            "Sustainable investing",
            "Risk assessment",
            "Industry comparison",
        ],
    ),
    "esg_benchmark": EndpointSemantics(
        client_name="intelligence",
        method_name="get_esg_benchmark",
        natural_description=(
            "Retrieve industry ESG benchmarks "
            "and sector averages for environmental, "
            "social, and governance metrics"
        ),
        example_queries=[
            "Get ESG industry benchmarks",
            "Show sector ESG averages",
            "ESG performance standards",
            "Industry ESG metrics",
        ],
        related_terms=[
            "industry standards",
            "sector benchmarks",
            "ESG averages",
            "peer metrics",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="ESG",
        parameter_hints={
            "year": ParameterHint(
                natural_names=["year", "annual", "period"],
                extraction_patterns=[r"20\d{2}"],
                examples=["2023", "2024"],
                context_clues=["year", "annual", "yearly"],
            ),
        },
        response_hints={
            "sector": ResponseFieldInfo(
                description="Industry sector name",
                examples=["Technology", "Healthcare"],
                related_terms=["industry", "sector name"],
            ),
            "esg_score": ResponseFieldInfo(
                description="Sector ESG score",
                examples=["85.5", "76.3"],
                related_terms=["benchmark score", "industry average"],
            ),
        },
        use_cases=[
            "Peer comparison",
            "Industry analysis",
            "Performance benchmarking",
            "Sector research",
        ],
    ),
    "senate_trading": EndpointSemantics(
        client_name="intelligence",
        method_name="get_senate_trading",
        natural_description=(
            "Access Senate trading activity "
            "and disclosures including stock trades, "
            "transaction details, and filing information"
        ),
        example_queries=[
            "Get Senate trades for AAPL",
            "Show Senator stock transactions",
            "Political trading activity",
            "Senate trading history",
        ],
        related_terms=[
            "senator trades",
            "political trading",
            "congress trades",
            "senate disclosures",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Government Trading",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "transaction_date": ResponseFieldInfo(
                description="Date of the trade",
                examples=["2024-01-15", "2023-12-20"],
                related_terms=["trade date", "transaction time"],
            ),
            "amount": ResponseFieldInfo(
                description="Trade amount range",
                examples=["$15,000-$50,000", "$50,001-$100,000"],
                related_terms=["value", "transaction size"],
            ),
        },
        use_cases=[
            "Political trading tracking",
            "Insider activity",
            "Regulatory compliance",
            "Market research",
        ],
    ),
    "senate_trading_rss": EndpointSemantics(
        client_name="intelligence",
        method_name="get_senate_trading_rss",
        natural_description=(
            "Get real-time RSS feed of Senate trading disclosures including new "
            "filings and transaction updates"
        ),
        example_queries=[
            "Show latest Senate trades",
            "Recent Senate disclosures",
            "New political trading activity",
            "Senate trading feed",
        ],
        related_terms=[
            "senate updates",
            "trading feed",
            "disclosure alerts",
            "political trades",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Government Trading",
        parameter_hints={"page": PAGE_HINT},
        response_hints={
            "date_received": ResponseFieldInfo(
                description="Filing receipt date",
                examples=["2024-01-15", "2023-12-20"],
                related_terms=["filing date", "disclosure date"],
            ),
            "transaction_date": ResponseFieldInfo(
                description="Actual trade date",
                examples=["2024-01-10", "2023-12-15"],
                related_terms=["trade date", "execution date"],
            ),
        },
        use_cases=[
            "Real-time monitoring",
            "Trade tracking",
            "Compliance updates",
            "Market analysis",
        ],
    ),
    "house_disclosure_rss": EndpointSemantics(
        client_name="intelligence",
        method_name="get_house_disclosure_rss",
        natural_description=(
            "Access real-time RSS feed of House Representative trading disclosures "
            "including new filings and updates"
        ),
        example_queries=[
            "Show House trading disclosures",
            "Recent Representative trades",
            "House disclosure feed",
            "Political trading updates",
        ],
        related_terms=[
            "house trades",
            "congress disclosures",
            "representative trading",
            "political updates",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Government Trading",
        parameter_hints={"page": PAGE_HINT},
        response_hints={
            "disclosure_date": ResponseFieldInfo(
                description="Disclosure filing date",
                examples=["2024-01-15", "2023-12-20"],
                related_terms=["filing date", "report date"],
            ),
            "transaction_date": ResponseFieldInfo(
                description="Trade execution date",
                examples=["2024-01-10", "2023-12-15"],
                related_terms=["trade date", "execution date"],
            ),
        },
        use_cases=[
            "Disclosure monitoring",
            "Political trading analysis",
            "Regulatory tracking",
            "Market research",
        ],
    ),
    "institutional_holders": EndpointSemantics(
        client_name="intelligence",
        method_name="get_institutional_holders",
        natural_description=(
            "Retrieve institutional ownership data including holder details, "
            "position sizes, and ownership changes"
        ),
        example_queries=[
            "Show institutional holders for AAPL",
            "Get institutional ownership data",
            "Who owns this stock?",
            "Major shareholders list",
        ],
        related_terms=[
            "institutional ownership",
            "major holders",
            "shareholders",
            "ownership stakes",
            "institutional investors",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Ownership",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "holder_name": ResponseFieldInfo(
                description="Institution name",
                examples=["BlackRock", "Vanguard"],
                related_terms=["institution", "shareholder", "investor"],
            ),
            "shares": ResponseFieldInfo(
                description="Number of shares held",
                examples=["10000000", "5000000"],
                related_terms=["position size", "holdings", "stake"],
            ),
        },
        use_cases=[
            "Ownership analysis",
            "Investment research",
            "Institutional tracking",
            "Market structure",
        ],
    ),
    "crowdfunding_search": EndpointSemantics(
        client_name="intelligence",
        method_name="get_crowdfunding_search",
        natural_description=(
            "Search crowdfunding offerings and campaigns by company name with "
            "detailed offering information"
        ),
        example_queries=[
            "Search crowdfunding offerings",
            "Find company fundraising",
            "Look up crowdfunding campaigns",
            "Search startup funding",
        ],
        related_terms=[
            "crowdfunding",
            "fundraising",
            "startup funding",
            "capital raise",
            "offering search",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Fundraising",
        parameter_hints={
            "name": ParameterHint(
                natural_names=["company name", "business name", "search term"],
                extraction_patterns=[r"[\w\s]+"],
                examples=["Tech Corp", "Green Energy"],
                context_clues=["company", "business", "name"],
            ),
        },
        response_hints={
            "offering_amount": ResponseFieldInfo(
                description="Fundraising amount",
                examples=["1000000", "500000"],
                related_terms=["raise amount", "target", "goal"],
            ),
            "security_type": ResponseFieldInfo(
                description="Type of security offered",
                examples=["Common Stock", "SAFE"],
                related_terms=["instrument", "security", "investment type"],
            ),
        },
        use_cases=[
            "Startup research",
            "Investment opportunities",
            "Market research",
            "Due diligence",
        ],
    ),
    "crowdfunding_by_cik": EndpointSemantics(
        client_name="intelligence",
        method_name="get_crowdfunding_by_cik",
        natural_description=(
            "Retrieve crowdfunding offerings for a specific company using CIK "
            "with complete offering details"
        ),
        example_queries=[
            "Get crowdfunding by CIK",
            "Show company offerings",
            "Find fundraising by CIK",
            "Company funding rounds",
        ],
        related_terms=[
            "CIK lookup",
            "company offerings",
            "fundraising rounds",
            "startup funding",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Fundraising",
        parameter_hints={
            "cik": ParameterHint(
                natural_names=["CIK", "company identifier", "SEC number"],
                extraction_patterns=[r"\d{10}"],
                examples=["0000320193", "0001018724"],
                context_clues=["CIK", "identifier", "SEC ID"],
            ),
        },
        response_hints={
            "offering_details": ResponseFieldInfo(
                description="Offering information",
                examples=["Series A", "Seed Round"],
                related_terms=["round details", "funding info"],
            ),
        },
        use_cases=[
            "Company research",
            "Funding analysis",
            "Investment tracking",
            "Due diligence",
        ],
    ),
    "financial_reports_dates": EndpointSemantics(
        client_name="intelligence",
        method_name="get_financial_reports_dates",
        natural_description=(
            "Retrieve available financial report dates and filing deadlines"
        ),
        example_queries=[
            "When are financial reports due?",
            "Get report filing dates",
            "Show financial reporting calendar",
            "Next earnings report dates",
        ],
        related_terms=[
            "filing dates",
            "report deadlines",
            "financial calendar",
            "reporting schedule",
        ],
        category=SemanticCategory.INTELLIGENCE,
        sub_category="Calendar Events",
        parameter_hints={},  # Add any parameters if needed
        response_hints={
            "date": ResponseFieldInfo(
                description="Report filing date",
                examples=["2024-01-15", "2024-02-01"],
                related_terms=["filing date", "report date"],
            ),
        },
        use_cases=[
            "Filing deadline tracking",
            "Report scheduling",
            "Compliance planning",
            "Calendar management",
        ],
    ),
}
