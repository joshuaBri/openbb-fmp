"""FMP Historical Rating Model."""

import asyncio
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import to_snake_case

from openbb_fmp_extension.standard_models.historical_rating import (
    HistoricalRatingData,
    HistoricalRatingQueryParams,
)
from openbb_fmp_extension.utils.helpers import create_url, get_jsonparsed_data


class FMPHistoricalRatingQueryParams(HistoricalRatingQueryParams):
    """Historical Rating Query Parameters.

    Source: https://fmp.a.pinggy.link/api/v3/historical-rating/AAPL
    """


class FMPHistoricalRatingData(HistoricalRatingData):
    """Historical Rating Data Model."""

    __alias_dict__ = {"symbol": "ticker"}


class FMPHistoricalRatingFetcher(
    Fetcher[
        HistoricalRatingQueryParams,
        List[HistoricalRatingData],
    ]
):
    """Fetches and transforms data from the House Disclosure endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> HistoricalRatingQueryParams:
        """Transform the query params."""
        return HistoricalRatingQueryParams(**params)

    @staticmethod
    async def aextract_data(
            query: FMPHistoricalRatingQueryParams,
            credentials: Optional[Dict[str, str]] = None,
            **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the House Disclosure endpoint."""
        symbols = query.symbol.split(",")
        results: List[Dict] = []

        async def get_one(symbol):
            """Get data for the given symbol."""
            url = create_url(
                3, f"historical-rating/{symbol}"
            )
            result = get_jsonparsed_data(url)
            if not result or len(result) == 0:
                warn(f"Symbol Error: No data found for symbol {symbol}")
            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data returned for the given symbol.")
        results = [{to_snake_case(key): value for key, value in d.items()} for d in results]

        return results

    @staticmethod
    def transform_data(
            query: FMPHistoricalRatingQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[HistoricalRatingData]:
        """Return the transformed data."""
        return [FMPHistoricalRatingData(**d) for d in data]
